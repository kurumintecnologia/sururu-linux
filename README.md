# Sururu Linux 2027 — codinome "Isaac"

*Nome inspirado no sururu, o marisco das lagoas de Alagoas.*

Distribuição baseada no **Debian 13 (trixie)**, feita pela Kurumin Tecnologia,
para quem estuda e trabalha com **Linux, containers e Kubernetes**.
Dá boot do pendrive com um lab de Kubernetes pronto: `kind create cluster` e pronto.

> O Sururu é derivado do Debian, mas não é um produto oficial do Projeto Debian.

## O que vem nela
- Desktop XFCE leve, em português, teclado ABNT2, fuso de São Paulo
- Instalador gráfico Calamares
- kubectl, helm, k9s, kind, podman, buildah, skopeo, containerd
- Kernel, GRUB e shim **assinados do Debian** (Secure Boot funciona)

## Gerar a ISO (no seu Debian)
```bash
make deps
make build     # ~20-40 min, gera sururu-isaac-amd64.hybrid.iso
make test      # boota no QEMU
```

## Estrutura
```
auto/config                       opções do live-build (base, idioma, nome da ISO)
config/package-lists/*.list.chroot  pacotes do Debian
config/hooks/live/*.hook.chroot     scripts que rodam dentro do sistema (branding, k8s)
config/includes.chroot/           arquivos copiados como estão para o sistema
scripts/test-qemu.sh              teste de boot
.github/workflows/build-iso.yml   CI: build, teste, SBOM, Trivy, assinatura, release
```

## Roadmap
- [ ] v0.1 — ISO live boota com XFCE e ferramentas k8s
- [ ] v0.2 — Calamares instala no disco com branding próprio
- [ ] v0.3 — tema, wallpaper, logo e plymouth
- [ ] v0.4 — "Central Sururu": painel com labs da Escola Kurumin
- [ ] v0.5 — repositório APT próprio (aptly) só para pacotes Sururu
- [ ] 2027.1 — lançamento

## Licença
Scripts e configurações: GPL-3.0. Cada pacote mantém a licença original.
