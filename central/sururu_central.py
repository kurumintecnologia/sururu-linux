#!/usr/bin/env python3
"""Central Sururu: painel local para estudar Linux, containers e Kubernetes.

Roda só em 127.0.0.1, sem dependências além do Python 3. Abre no navegador.
Segurança:
  * escuta apenas em 127.0.0.1;
  * toda chamada à API exige um token aleatório criado a cada execução
    (protege contra sites que tentem mandar requisições para o localhost);
  * confere o cabeçalho Host (protege contra DNS rebinding);
  * só executa comandos fixos, deste arquivo ou dos labs instalados em
    /usr/share/sururu/labs. Nada vindo do navegador vira comando.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import pwd
import secrets
import shutil
import subprocess
import threading
import time
import uuid
import webbrowser
from concurrent.futures import ThreadPoolExecutor
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

VERSAO = "2027.1"
AQUI = Path(__file__).resolve().parent
WEB = Path(os.environ.get("SURURU_WEB", AQUI / "web"))
LABS = Path(os.environ.get("SURURU_LABS", AQUI / "labs"))
DADOS = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "sururu"
PROGRESSO = DADOS / "progresso.json"
CLUSTER = "sururu"
TOKEN = secrets.token_urlsafe(24)
PORTA = 8787
# Espaço que o kind precisa para baixar e descompactar a imagem do Kubernetes
MINIMO_CLUSTER_GB = float(os.environ.get("SURURU_MINIMO_GB", "3"))

JOBS: dict[str, dict] = {}
JOBS_LOCK = threading.Lock()


# ---------------------------------------------------------------- utilidades
def rodar(cmd: list[str] | str, timeout: int = 20) -> tuple[int, str]:
    """Executa um comando fixo e devolve (código, saída combinada)."""
    shell = isinstance(cmd, str)
    try:
        r = subprocess.run(
            ["bash", "-c", cmd] if shell else cmd,
            capture_output=True, text=True, timeout=timeout,
            env={**os.environ, "LANG": "C.UTF-8"},
        )
        return r.returncode, (r.stdout + r.stderr).strip()
    except FileNotFoundError:
        return 127, "comando não encontrado"
    except OSError as erro:
        return 126, str(erro)
    except subprocess.TimeoutExpired:
        return 124, "tempo esgotado"


def versao(ferramenta: str, args: list[str]) -> str | None:
    if not shutil.which(ferramenta):
        return None
    cod, saida = rodar([ferramenta, *args], timeout=5)
    linha = saida.splitlines()[0] if saida else ""
    return linha[:80] if cod == 0 else "instalado"


def ler_progresso() -> dict:
    try:
        return json.loads(PROGRESSO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def salvar_progresso(dados: dict) -> None:
    DADOS.mkdir(parents=True, exist_ok=True)
    tmp = PROGRESSO.with_suffix(".tmp")
    tmp.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(PROGRESSO)


def carregar_labs() -> list[dict]:
    labs = []
    for arq in sorted(LABS.glob("*.json")):
        try:
            labs.append(json.loads(arq.read_text(encoding="utf-8")))
        except ValueError:
            continue
    return labs


def lab_por_id(lab_id: str) -> dict | None:
    return next((l for l in carregar_labs() if l.get("id") == lab_id), None)


# ------------------------------------------------------------------- estado
def nome_usuario() -> str:
    """Primeiro nome do usuário (campo GECOS), ou o login."""
    try:
        info = pwd.getpwuid(os.getuid())
        nome = info.pw_gecos.split(",")[0].strip()
        return (nome.split()[0] if nome else info.pw_name).capitalize()
    except (KeyError, IndexError):
        return os.environ.get("USER", "estudante")


def espaco_para_containers() -> float:
    """Espaço livre onde o Docker guarda as imagens (GB). No modo live isso é RAM."""
    for caminho in ("/var/lib/docker", "/var/lib", "/"):
        if Path(caminho).exists():
            return round(shutil.disk_usage(caminho).free / 1e9, 1)
    return 0.0


def info_sistema() -> dict:
    nome = "Sururu Linux"
    try:
        for linha in Path("/etc/os-release").read_text().splitlines():
            if linha.startswith("PRETTY_NAME="):
                nome = linha.split("=", 1)[1].strip('"')
    except OSError:
        pass
    mem_total = mem_livre = 0
    try:
        for linha in Path("/proc/meminfo").read_text().splitlines():
            if linha.startswith("MemTotal:"):
                mem_total = int(linha.split()[1]) // 1024
            elif linha.startswith("MemAvailable:"):
                mem_livre = int(linha.split()[1]) // 1024
    except OSError:
        pass
    disco = shutil.disk_usage(Path.home())
    try:
        carga = os.getloadavg()[0]
    except OSError:
        carga = 0.0
    return {
        "nome": nome,
        "kernel": platform.release(),
        "usuario": nome_usuario(),
        "cpus": os.cpu_count() or 1,
        "carga": round(carga, 2),
        "mem_total_mb": mem_total,
        "mem_livre_mb": mem_livre,
        "disco_total_gb": round(disco.total / 1e9, 1),
        "disco_livre_gb": round(disco.free / 1e9, 1),
        "live": Path("/run/live/medium").exists(),
        "containers_livre_gb": espaco_para_containers(),
    }


def info_ferramentas() -> list[dict]:
    lista = [
        ("docker", ["--version"], "Roda containers. O kind usa o Docker para criar os nós."),
        ("podman", ["--version"], "Alternativa ao Docker, sem daemon."),
        ("kubectl", ["version", "--client"], "Conversa com o cluster Kubernetes."),
        ("kind", ["version"], "Cria clusters Kubernetes dentro de containers."),
        ("helm", ["version", "--short"], "Instala aplicações prontas no cluster."),
        ("k9s", ["version", "--short"], "Painel do cluster dentro do terminal."),
    ]
    with ThreadPoolExecutor(max_workers=len(lista)) as pool:
        versoes = list(pool.map(lambda item: versao(item[0], item[1]), lista))
    return [{"nome": n, "versao": v, "para_que": d} for (n, _, d), v in zip(lista, versoes)]


def docker_ok() -> dict:
    if not shutil.which("docker"):
        return {"ok": False, "motivo": "sem_docker"}
    # O Docker do Debian liga por socket: a primeira chamada acorda o serviço,
    # o que pode levar alguns segundos. Por isso o tempo maior.
    cod, saida = rodar(["docker", "info", "--format", "{{.ServerVersion}}"], timeout=30)
    if cod == 0:
        return {"ok": True}
    if "permission denied" in saida.lower():
        return {"ok": False, "motivo": "sem_permissao"}
    return {"ok": False, "motivo": "parado"}


def info_cluster() -> dict:
    if not shutil.which("kind") or not shutil.which("kubectl"):
        return {"existe": False, "motivo": "sem_ferramentas"}
    cod, saida = rodar(["kind", "get", "clusters"], timeout=15)
    if cod != 0 or CLUSTER not in saida.split():
        return {"existe": False}
    cod, saida = rodar(
        ["kubectl", "--context", f"kind-{CLUSTER}", "get", "nodes", "-o", "json"], timeout=15
    )
    nos = []
    if cod == 0:
        for item in json.loads(saida).get("items", []):
            pronto = any(
                c["type"] == "Ready" and c["status"] == "True"
                for c in item["status"].get("conditions", [])
            )
            papel = "control-plane" if any(
                "control-plane" in k for k in item["metadata"].get("labels", {})
            ) else "worker"
            nos.append({
                "nome": item["metadata"]["name"],
                "papel": papel,
                "pronto": pronto,
                "versao": item["status"]["nodeInfo"]["kubeletVersion"],
            })
    cod, saida = rodar(
        ["kubectl", "--context", f"kind-{CLUSTER}", "get", "pods", "-A", "-o", "json"], timeout=15
    )
    pods = []
    if cod == 0:
        for item in json.loads(saida).get("items", []):
            pods.append({
                "ns": item["metadata"]["namespace"],
                "nome": item["metadata"]["name"],
                "fase": item["status"].get("phase", "?"),
            })
    return {"existe": True, "nos": nos, "pods": pods}


# --------------------------------------------------------------------- jobs
def novo_job(titulo: str, passos: list[list[str]]) -> str:
    job_id = uuid.uuid4().hex[:10]
    with JOBS_LOCK:
        JOBS[job_id] = {"id": job_id, "titulo": titulo, "estado": "rodando",
                        "log": [], "inicio": time.time()}

    def trabalhar():
        for cmd in passos:
            with JOBS_LOCK:
                JOBS[job_id]["log"].append("$ " + " ".join(cmd))
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    text=True, env={**os.environ, "LANG": "C.UTF-8"})
            assert proc.stdout
            for linha in proc.stdout:
                with JOBS_LOCK:
                    JOBS[job_id]["log"].append(linha.rstrip())
                    JOBS[job_id]["log"] = JOBS[job_id]["log"][-300:]
            if proc.wait() != 0:
                with JOBS_LOCK:
                    JOBS[job_id]["estado"] = "falhou"
                return
        with JOBS_LOCK:
            JOBS[job_id]["estado"] = "pronto"

    threading.Thread(target=trabalhar, daemon=True).start()
    return job_id


def config_kind(workers: int) -> Path:
    DADOS.mkdir(parents=True, exist_ok=True)
    arq = DADOS / "kind-sururu.yaml"
    nos = "  - role: control-plane\n" + "  - role: worker\n" * workers
    arq.write_text(
        "kind: Cluster\napiVersion: kind.x-k8s.io/v1alpha4\nname: sururu\nnodes:\n" + nos,
        encoding="utf-8",
    )
    return arq


# --------------------------------------------------------------------- labs
def verificar_lab(lab: dict) -> dict:
    resultados = []
    for chk in lab.get("verificacoes", []):
        cod, saida = rodar(chk["comando"], timeout=chk.get("timeout", 20))
        resultados.append({"texto": chk["texto"], "ok": cod == 0,
                           "dica": None if cod == 0 else chk.get("dica")})
    tudo_ok = bool(resultados) and all(r["ok"] for r in resultados)
    prog = ler_progresso()
    reg = prog.get(lab["id"], {})
    reg["tentativas"] = reg.get("tentativas", 0) + 1
    if tudo_ok and not reg.get("concluido"):
        reg["concluido"] = time.strftime("%Y-%m-%d %H:%M")
    prog[lab["id"]] = reg
    salvar_progresso(prog)
    return {"ok": tudo_ok, "resultados": resultados}


# --------------------------------------------------------------------- HTTP
class Central(SimpleHTTPRequestHandler):
    server_version = "CentralSururu/" + VERSAO

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(WEB), **kw)

    def log_message(self, fmt, *args):  # silencioso
        pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'")
        super().end_headers()

    # ---- segurança
    def _host_ok(self) -> bool:
        host = self.headers.get("Host", "")
        return host in (f"127.0.0.1:{PORTA}", f"localhost:{PORTA}")

    def _api_ok(self) -> bool:
        return self._host_ok() and secrets.compare_digest(
            self.headers.get("X-Sururu-Token", ""), TOKEN)

    def _json(self, dados, status=HTTPStatus.OK):
        corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def _corpo(self) -> dict:
        tam = int(self.headers.get("Content-Length") or 0)
        if tam > 10_000:
            return {}
        try:
            return json.loads(self.rfile.read(tam) or b"{}")
        except ValueError:
            return {}

    # ---- rotas
    def do_GET(self):
        if not self._host_ok():
            return self.send_error(HTTPStatus.FORBIDDEN)
        if not self.path.startswith("/api/"):
            return super().do_GET()
        if not self._api_ok():
            return self._json({"erro": "token inválido"}, HTTPStatus.FORBIDDEN)

        if self.path == "/api/estado":
            with ThreadPoolExecutor(max_workers=2) as pool:
                ferr = pool.submit(info_ferramentas)
                dock = pool.submit(docker_ok)
                return self._json({"versao": VERSAO, "sistema": info_sistema(),
                                   "ferramentas": ferr.result(), "docker": dock.result(),
                                   "minimo_cluster_gb": MINIMO_CLUSTER_GB})
        if self.path == "/api/cluster":
            return self._json(info_cluster())
        if self.path == "/api/labs":
            prog = ler_progresso()
            labs = []
            for l in carregar_labs():
                pub = {k: v for k, v in l.items() if k != "verificacoes"}
                pub["verificacoes"] = [v["texto"] for v in l.get("verificacoes", [])]
                pub["progresso"] = prog.get(l["id"], {})
                labs.append(pub)
            return self._json(labs)
        if self.path.startswith("/api/jobs/"):
            job_id = self.path.rsplit("/", 1)[-1]
            with JOBS_LOCK:
                job = JOBS.get(job_id)
                return self._json(dict(job) if job else {"erro": "não encontrado"},
                                  HTTPStatus.OK if job else HTTPStatus.NOT_FOUND)
        return self._json({"erro": "rota desconhecida"}, HTTPStatus.NOT_FOUND)

    def do_POST(self):
        if not self._api_ok():
            return self._json({"erro": "token inválido"}, HTTPStatus.FORBIDDEN)
        corpo = self._corpo()

        if self.path == "/api/cluster/criar":
            workers = max(0, min(int(corpo.get("workers", 1)), 2))
            arq = config_kind(workers)
            job = novo_job("Criando o cluster", [
                ["kind", "create", "cluster", "--config", str(arq), "--wait", "120s"],
                ["kubectl", "config", "use-context", f"kind-{CLUSTER}"],
            ])
            return self._json({"job": job})
        if self.path == "/api/cluster/apagar":
            return self._json({"job": novo_job("Apagando o cluster",
                                               [["kind", "delete", "cluster", "--name", CLUSTER]])})
        if self.path.startswith("/api/labs/") and self.path.endswith("/verificar"):
            lab = lab_por_id(self.path.split("/")[3])
            if not lab:
                return self._json({"erro": "lab não encontrado"}, HTTPStatus.NOT_FOUND)
            return self._json(verificar_lab(lab))
        if self.path.startswith("/api/labs/") and self.path.endswith("/recomecar"):
            lab = lab_por_id(self.path.split("/")[3])
            if not lab:
                return self._json({"erro": "lab não encontrado"}, HTTPStatus.NOT_FOUND)
            for cmd in lab.get("limpeza", []):
                rodar(cmd, timeout=60)
            prog = ler_progresso()
            prog.pop(lab["id"], None)
            salvar_progresso(prog)
            return self._json({"ok": True})
        return self._json({"erro": "rota desconhecida"}, HTTPStatus.NOT_FOUND)


def main():
    global PORTA
    ap = argparse.ArgumentParser(description="Central Sururu")
    ap.add_argument("--porta", type=int, default=PORTA)
    ap.add_argument("--sem-navegador", action="store_true")
    ap.add_argument("--pagina", default="", help="abrir direto numa seção (ex.: labs)")
    args = ap.parse_args()
    PORTA = args.porta
    sessao = DADOS / "sessao"
    extra = f"&p={args.pagina}" if args.pagina else ""
    try:
        srv = ThreadingHTTPServer(("127.0.0.1", PORTA), Central)
    except OSError:
        # já está aberta: reaproveita a sessão em vez de falhar
        try:
            url = sessao.read_text().strip() + extra
            print(f"Central Sururu já está aberta: {url}")
            if not args.sem_navegador:
                webbrowser.open(url)
            return
        except OSError:
            raise SystemExit(f"A porta {PORTA} está ocupada por outro programa.")
    url = f"http://127.0.0.1:{PORTA}/#t={TOKEN}"
    DADOS.mkdir(parents=True, exist_ok=True)
    sessao.touch(mode=0o600)
    sessao.write_text(url)
    url += extra
    print(f"Central Sururu {VERSAO} em {url}")
    if not args.sem_navegador:
        threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
