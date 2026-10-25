/* Central Sururu — interface. Sem dependências, sem internet. */
"use strict";

const params = new URLSearchParams(location.hash.slice(1));
const TOKEN = params.get("t") || sessionStorage.getItem("sururu-token") || "";
if (params.get("t")) {
  sessionStorage.setItem("sururu-token", TOKEN);
  history.replaceState(null, "", "#" + (params.get("p") || "inicio"));
}

const TRILHAS = {
  linux: { nome: "Linux", texto: "Terminal, arquivos, permissões e scripts. A base de tudo." },
  containers: { nome: "Containers", texto: "Empacote e rode aplicações com Docker, em segundos." },
  kubernetes: { nome: "Kubernetes", texto: "Orquestre containers num cluster de verdade, como na CKA." },
};

let LABS = [];
let ESTADO = null;

/* ---------- utilidades */
function h(tag, attrs = {}, ...filhos) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const f of filhos.flat()) {
    if (f === null || f === undefined || f === false) continue;
    el.append(f instanceof Node ? f : document.createTextNode(String(f)));
  }
  return el;
}
const $ = (s) => document.querySelector(s);

async function api(caminho, opcoes = {}) {
  const r = await fetch("/api/" + caminho, {
    method: opcoes.method || "GET",
    headers: { "X-Sururu-Token": TOKEN, "Content-Type": "application/json" },
    body: opcoes.body ? JSON.stringify(opcoes.body) : undefined,
  });
  if (r.status === 403) throw new Error("sessao");
  return r.json();
}

let toastTimer;
function avisar(texto) {
  const t = $("#toast");
  t.textContent = texto;
  t.hidden = false;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => (t.hidden = true), 2600);
}

function copiar(texto) {
  navigator.clipboard.writeText(texto).then(
    () => avisar("Comando copiado. Cole no terminal com Ctrl+Shift+V."),
    () => avisar("Não deu para copiar. Selecione o texto e use Ctrl+C."),
  );
}

function blocoComando(cmd) {
  return h("div", { class: "comando" },
    h("pre", {}, h("code", {}, cmd)),
    h("button", { class: "botao pequeno", type: "button", onclick: () => copiar(cmd) }, "Copiar"));
}

function saudacao() {
  const hora = new Date().getHours();
  if (hora < 12) return "Bom dia";
  if (hora < 18) return "Boa tarde";
  return "Boa noite";
}

function mb(v) { return v >= 1024 ? (v / 1024).toFixed(1) + " GB" : v + " MB"; }

/* ---------- navegação */
const SECOES = ["inicio", "cluster", "labs", "lab", "prova", "ajuda"];
function rota() {
  const [pag, arg] = (location.hash.slice(1) || "inicio").split("/");
  const atual = SECOES.includes(pag) ? pag : "inicio";
  document.querySelectorAll("[data-secao]").forEach((s) => (s.hidden = s.dataset.secao !== atual));
  document.querySelectorAll("[data-pag]").forEach((a) => {
    const ativo = a.dataset.pag === atual || (atual === "lab" && a.dataset.pag === "labs");
    if (ativo) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  });
  if (atual === "inicio") desenharInicio();
  if (atual === "cluster") atualizarCluster();
  if (atual === "labs") desenharListaLabs();
  if (atual === "lab") desenharLab(arg);
  if (atual === "prova") desenharProva();
  $("#conteudo").focus({ preventScroll: true });
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", rota);

/* ---------- início */
function desenharInicio() {
  if (!ESTADO) return;
  const s = ESTADO.sistema;
  $("#ola").textContent = `${saudacao()}, ${s.usuario}!`;
  $("#versao").textContent = s.nome;

  const caminho = $("#caminho");
  caminho.replaceChildren();
  Object.entries(TRILHAS).forEach(([id, t], i) => {
    const labs = LABS.filter((l) => l.trilha === id);
    const feitos = labs.filter((l) => l.progresso.concluido).length;
    const barra = h("span");
    const li = h("li", { class: "etapa" + (labs.length && feitos === labs.length ? " feito" : "") },
      h("div", { class: "no", "aria-hidden": "true" }, i + 1),
      h("h2", {}, t.nome),
      h("p", {}, t.texto),
      h("div", { class: "barra", "aria-hidden": "true" }, barra),
      h("small", {}, `${feitos} de ${labs.length} laboratórios`),
      h("br"),
      h("a", { class: "ir", href: "#labs", onclick: () => (filtroTrilha = id) },
        feitos === 0 ? "Começar" : feitos === labs.length ? "Revisar" : "Continuar"));
    caminho.append(li);
    requestAnimationFrame(() => (barra.style.width = labs.length ? (100 * feitos / labs.length) + "%" : "0"));
  });

  const usoMem = s.mem_total_mb ? Math.round(100 * (1 - s.mem_livre_mb / s.mem_total_mb)) : 0;
  const usoDisco = s.disco_total_gb ? Math.round(100 * (1 - s.disco_livre_gb / s.disco_total_gb)) : 0;
  const medidor = (p) => { const sp = h("span"); sp.style.width = p + "%"; return h("div", { class: "medidor" }, sp); };
  $("#medidas").replaceChildren(
    h("dt", {}, "Memória"), h("dd", {}, `${mb(s.mem_livre_mb)} livres de ${mb(s.mem_total_mb)}`, medidor(usoMem)),
    h("dt", {}, "Disco"), h("dd", {}, `${s.disco_livre_gb} GB livres de ${s.disco_total_gb} GB`, medidor(usoDisco)),
    h("dt", {}, "Processadores"), h("dd", {}, `${s.cpus} núcleos, carga ${s.carga}`),
    h("dt", {}, "Kernel"), h("dd", {}, s.kernel),
  );
  $("#aviso-live").hidden = !s.live;
  if (s.mem_total_mb && s.mem_total_mb < 6000) {
    $("#medidas").append(h("dt", {}, "Dica"), h("dd", {}, "Com menos de 6 GB de RAM, prefira o cluster só com o control-plane."));
  }

  $("#ferramentas").replaceChildren(...ESTADO.ferramentas.map((f) =>
    h("li", {},
      h("span", { class: f.versao ? "ok" : "falta", "aria-label": f.versao ? "instalado" : "não instalado" }, f.versao ? "✓" : "–"),
      h("span", {}, h("b", {}, f.nome), " ", h("span", {}, f.versao ? "" : "não instalado")),
      h("small", {}, f.para_que))));
}

/* ---------- cluster */
let jobAtual = null;
async function atualizarCluster() {
  const alerta = $("#docker-alerta");
  const d = ESTADO && ESTADO.docker;
  alerta.hidden = !d || d.ok;
  if (d && !d.ok) {
    const textos = {
      sem_docker: ["O Docker não está instalado. O kind precisa dele para criar os nós do cluster.", "sudo apt install docker.io"],
      sem_permissao: ["Seu usuário ainda não pode usar o Docker. Rode o comando abaixo, saia da sessão e entre de novo.", "sudo usermod -aG docker $USER"],
      parado: ["O Docker está parado. Ligue o serviço com:", "sudo systemctl start docker"],
    }[d.motivo];
    alerta.replaceChildren(h("strong", {}, "Falta um passo. "), textos[0], blocoComando(textos[1]));
  }
  const c = await api("cluster");
  const palco = $("#cluster-palco");
  palco.replaceChildren();
  $("#apagar").hidden = !c.existe;
  $("#criar").hidden = c.existe;
  $("#tamanho").hidden = c.existe;
  $("#pods-bloco").hidden = !c.existe;
  if (!c.existe) {
    palco.append(h("div", { class: "vazio" },
      h("h2", {}, "Você ainda não tem um cluster"),
      h("p", {}, "Escolha o tamanho e clique em \"Criar meu cluster\". Leva uns 2 minutos na primeira vez, porque baixa a imagem do Kubernetes.")));
    avisoEspaco();
    return;
  }
  $("#espaco-alerta")?.remove();
  c.nos.forEach((n) => palco.append(
    h("div", { class: "node" + (n.papel === "control-plane" ? " cp" : "") },
      h("div", { class: "papel" }, n.papel === "control-plane" ? "Control-plane" : "Worker"),
      h("div", { class: "nome" }, n.nome),
      h("span", { class: "estado" + (n.pronto ? " pronto" : "") }, n.pronto ? "Pronto" : "Subindo"),
      h("div", { class: "papel" }, n.versao))));
  $("#pods").replaceChildren(...c.pods.map((p) =>
    h("tr", {}, h("td", {}, p.ns), h("td", {}, p.nome), h("td", {}, p.fase))));
}

/* No modo live o "disco" é a memória RAM. Sem espaço, o kind trava no meio. */
let forcarCriacao = false;
function avisoEspaco() {
  $("#espaco-alerta")?.remove();
  const s = ESTADO.sistema;
  const minimo = ESTADO.minimo_cluster_gb || 3;
  const pouco = s.containers_livre_gb < minimo;
  $("#criar").disabled = pouco && !forcarCriacao;
  if (!pouco) return;
  const alerta = h("div", { class: "alerta", id: "espaco-alerta" },
    h("strong", {}, `Falta espaço para o cluster. `),
    `O Kubernetes precisa de uns ${minimo} GB livres e aqui há só ${s.containers_livre_gb} GB. `,
    s.live
      ? "No modo live, o \"disco\" é a memória RAM, por isso acaba rápido. "
      : "Libere espaço no disco antes de criar. ",
    s.live ? h("ul", {},
      h("li", {}, "Instale o Sururu no disco pelo ícone \"Instalar o Sururu Linux\" na área de trabalho (recomendado)."),
      h("li", {}, "Ou use um pendrive com persistência (o Ventoy faz isso), para ter espaço de verdade."),
      h("li", {}, "Numa máquina virtual, dê pelo menos 8 GB de memória.")) : null,
    h("button", { class: "botao pequeno", type: "button", onclick: () => {
      forcarCriacao = true; $("#criar").disabled = false; avisar("Tudo bem, pode tentar. Se travar, é falta de espaço.");
    } }, "Tentar mesmo assim"));
  $("#cluster-acoes").before(alerta);
}

async function acompanhar(jobId, botao) {
  const log = $("#job-log");
  log.hidden = false;
  botao.disabled = true;
  const textoOriginal = botao.textContent;
  botao.textContent = "Trabalhando...";
  for (;;) {
    const j = await api("jobs/" + jobId);
    log.textContent = j.log.join("\n");
    log.scrollTop = log.scrollHeight;
    if (j.estado !== "rodando") {
      botao.disabled = false;
      botao.textContent = textoOriginal;
      avisar(j.estado === "pronto" ? `${j.titulo}: pronto!` : `${j.titulo}: deu erro. Veja o log abaixo.`);
      break;
    }
    await new Promise((r) => setTimeout(r, 1500));
  }
  atualizarCluster();
}

$("#criar").addEventListener("click", async (e) => {
  const workers = Number(document.querySelector("input[name=workers]:checked").value);
  const r = await api("cluster/criar", { method: "POST", body: { workers } });
  acompanhar(r.job, e.currentTarget);
});
$("#apagar").addEventListener("click", async (e) => {
  if (!confirm("Apagar o cluster sururu? Tudo que está nele será perdido.")) return;
  const r = await api("cluster/apagar", { method: "POST" });
  acompanhar(r.job, e.currentTarget);
});

/* ---------- labs */
let filtroTrilha = "";
document.querySelectorAll("#abas-trilha button").forEach((b) =>
  b.addEventListener("click", () => { filtroTrilha = b.dataset.trilha; desenharListaLabs(); }));

function precisaTexto(l) {
  if (l.precisa.includes("cluster")) return "Precisa do cluster";
  if (l.precisa.includes("docker")) return "Precisa do Docker";
  return "Só o terminal";
}

function desenharListaLabs() {
  document.querySelectorAll("#abas-trilha button").forEach((b) =>
    b.setAttribute("aria-selected", String(b.dataset.trilha === filtroTrilha)));
  const lista = LABS.filter((l) => !filtroTrilha || l.trilha === filtroTrilha)
    .sort((a, b) => Object.keys(TRILHAS).indexOf(a.trilha) - Object.keys(TRILHAS).indexOf(b.trilha) || a.ordem - b.ordem);
  $("#lista-labs").replaceChildren(...lista.map((l) =>
    h("li", {}, h("a", { href: "#lab/" + l.id },
      h("h3", {}, l.titulo),
      h("p", {}, l.resumo),
      h("div", { class: "meta" },
        l.progresso.concluido ? h("span", { class: "selo concluido" }, "Concluído") : h("span", { class: "selo trilha" }, TRILHAS[l.trilha].nome),
        h("div", {}, `${l.tempo} min, ${l.nivel}`),
        h("div", {}, precisaTexto(l)))))));
}

function desenharLab(id) {
  const l = LABS.find((x) => x.id === id);
  const art = $("#lab");
  if (!l) { art.replaceChildren(h("p", {}, "Laboratório não encontrado.")); return; }
  const resultado = h("div", { class: "verificacao", "aria-live": "polite" });
  const botaoVerificar = h("button", { class: "botao principal", type: "button" }, "Verificar");
  botaoVerificar.addEventListener("click", async () => {
    botaoVerificar.disabled = true;
    botaoVerificar.textContent = "Verificando...";
    const r = await api(`labs/${l.id}/verificar`, { method: "POST" });
    botaoVerificar.disabled = false;
    botaoVerificar.textContent = "Verificar de novo";
    resultado.replaceChildren(
      h("ul", { class: "checklist" }, ...r.resultados.map((x) =>
        h("li", {}, h("span", { class: x.ok ? "ok" : "falta" }, x.ok ? "✓" : "✕"), h("span", {}, x.texto),
          x.dica ? h("span", { class: "dica" }, x.dica) : null))),
      r.ok ? h("div", { class: "parabens" }, "Mandou bem! Laboratório concluído. Seu progresso ficou salvo.") : null);
    await carregarLabs();
  });
  const botaoRecomecar = h("button", { class: "botao", type: "button" }, "Recomeçar do zero");
  botaoRecomecar.addEventListener("click", async () => {
    if (!confirm("Apagar o que você fez neste laboratório e começar de novo?")) return;
    await api(`labs/${l.id}/recomecar`, { method: "POST" });
    resultado.replaceChildren();
    avisar("Pronto. Pode começar de novo.");
    await carregarLabs();
  });

  const aviso = l.precisa.includes("cluster")
    ? h("p", { class: "aviso" }, "Este laboratório usa o cluster. Se ainda não criou, vá em ", h("a", { href: "#cluster" }, "Meu cluster"), " antes.")
    : null;

  art.replaceChildren(
    h("span", { class: "selo trilha" }, TRILHAS[l.trilha].nome),
    h("h1", {}, l.titulo),
    h("p", { class: "historia" }, l.historia),
    aviso,
    h("h2", {}, "Passo a passo"),
    h("ol", { class: "passos" }, ...l.passos.map((p) =>
      h("li", {}, h("div", {}, p.texto), p.comando ? blocoComando(p.comando) : null))),
    h("h2", {}, "Quando terminar"),
    h("p", {}, "A Central confere estes pontos no seu sistema:"),
    h("ul", {}, ...l.verificacoes.map((v) => h("li", {}, v))),
    h("div", { class: "linha-acoes" }, botaoVerificar, botaoRecomecar),
    resultado,
    h("details", { class: "solucao" },
      h("summary", {}, "Ver a solução (tente antes!)"),
      ...l.solucao.map(blocoComando)));
}

/* ---------- modo prova */
let prova = null;
function desenharProva() {
  const area = $("#prova");
  const tarefas = LABS.filter((l) => l.prova).sort((a, b) => a.ordem - b.ordem);
  if (!prova) {
    area.replaceChildren(
      h("section", { class: "bloco" },
        h("h2", {}, "Antes de começar"),
        h("ul", {},
          h("li", {}, "Crie o cluster em Meu cluster. As tarefas dependem dele."),
          h("li", {}, "As tarefas vêm sem os comandos. Use o que aprendeu e a documentação."),
          h("li", {}, "No fim, a Central corrige tudo de uma vez e mostra sua nota.")),
        h("button", { class: "botao principal", type: "button", onclick: comecarProva }, "Começar a prova")));
    return;
  }
  const lista = h("ol", { class: "tarefas" }, ...tarefas.map((l) =>
    h("li", { id: "tarefa-" + l.id, class: prova.resultado ? (prova.resultado[l.id] ? "certa" : "errada") : "" },
      h("h3", {}, l.titulo), h("div", {}, l.resumo),
      h("ul", {}, ...l.verificacoes.map((v) => h("li", {}, v))))));
  const relogio = h("div", { class: "relogio", id: "relogio" });
  const corrigir = h("button", { class: "botao principal", type: "button", onclick: corrigirProva }, "Corrigir prova");
  const encerrar = h("button", { class: "botao", type: "button", onclick: () => { prova = null; clearInterval(tique); desenharProva(); } }, "Sair da prova");
  const nota = prova.resultado
    ? h("p", { class: "nota" }, `Nota: ${prova.nota} de ${tarefas.length}. ${prova.nota === tarefas.length ? "Gabaritou!" : "Revise as tarefas em vermelho nos laboratórios."}`)
    : "";
  area.replaceChildren(relogio, lista, h("div", { class: "linha-acoes" }, corrigir, encerrar), nota);
  pintarRelogio();
}
let tique;
function comecarProva() {
  prova = { fim: Date.now() + 30 * 60 * 1000, resultado: null };
  clearInterval(tique);
  tique = setInterval(pintarRelogio, 1000);
  desenharProva();
}
function pintarRelogio() {
  const el = $("#relogio");
  if (!el || !prova) return;
  const resta = Math.max(0, prova.fim - Date.now());
  const m = String(Math.floor(resta / 60000)).padStart(2, "0");
  const s = String(Math.floor((resta % 60000) / 1000)).padStart(2, "0");
  el.textContent = `${m}:${s}`;
  el.classList.toggle("fim", resta === 0);
  if (resta === 0 && !prova.resultado) { clearInterval(tique); corrigirProva(); }
}
async function corrigirProva() {
  const tarefas = LABS.filter((l) => l.prova);
  const resultado = {};
  for (const l of tarefas) resultado[l.id] = (await api(`labs/${l.id}/verificar`, { method: "POST" })).ok;
  prova.resultado = resultado;
  prova.nota = Object.values(resultado).filter(Boolean).length;
  clearInterval(tique);
  await carregarLabs();
  desenharProva();
}

/* ---------- partida */
async function carregarLabs() { LABS = await api("labs"); }

async function iniciar() {
  $("#ola").textContent = `${saudacao()}!`;
  $("#medidas").replaceChildren(h("dt", {}, "Lendo..."), h("dd", {}, "Conferindo memória, disco e processador"));
  $("#ferramentas").replaceChildren(h("li", {}, h("span", { class: "falta" }, "…"), h("span", {}, "Conferindo as ferramentas instaladas")));
  try {
    [ESTADO] = await Promise.all([api("estado"), carregarLabs()]);
  } catch (e) {
    $("#conteudo").replaceChildren(h("section", { class: "bloco" },
      h("h1", {}, "Abra a Central pelo menu"),
      h("p", {}, "Esta página precisa ser aberta pelo ícone Central Sururu no menu (ou pelo comando sururu-central no terminal), que cria uma chave de acesso nova a cada vez.")));
    return;
  }
  rota();
}
iniciar();
