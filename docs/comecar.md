# Baixar e gravar no pendrive

## O que você precisa

- Um pendrive de **8 GB ou mais** (o conteúdo dele será apagado).
- Um computador 64 bits com **4 GB de RAM** no mínimo. Para o cluster com
  workers, **8 GB** deixam tudo confortável.

## 1. Baixe a ISO

Pegue a versão mais recente na página de
[releases do GitHub](https://github.com/kurumintecnologia/sururu-linux/releases).
Baixe também o arquivo `SHA256SUMS`.

Confira se o download veio inteiro:

```bash
sha256sum -c SHA256SUMS --ignore-missing
```

Tem que aparecer `OK`. Se aparecer `FALHOU`, baixe de novo.

??? info "Conferir a assinatura (opcional, para quem gosta de segurança)"
    Cada versão é assinada com Sigstore, sem chave para você guardar:
    ```bash
    cosign verify-blob SHA256SUMS --bundle SHA256SUMS.sigstore.json \
      --certificate-identity-regexp 'github.com/kurumintecnologia/sururu-linux' \
      --certificate-oidc-issuer https://token.actions.githubusercontent.com
    ```

## 2. Grave no pendrive

=== "Windows"
    Use o [Rufus](https://rufus.ie) ou o [balenaEtcher](https://etcher.balena.io):
    escolha a ISO, escolha o pendrive e clique em Iniciar. No Rufus, se
    perguntar o modo, escolha **DD**.

=== "Linux"
    Descubra o nome do pendrive com `lsblk` (ex.: `/dev/sdb`) e grave:
    ```bash
    sudo dd if=sururu-isaac-amd64.hybrid.iso of=/dev/sdX bs=4M status=progress conv=fsync
    ```
    Troque `sdX` pelo seu pendrive. **Errar aqui apaga o disco errado.**

=== "Ventoy"
    Se você já usa o [Ventoy](https://www.ventoy.net), é só copiar a ISO para
    dentro do pendrive.

## 3. Dê boot

Reinicie o computador com o pendrive conectado e escolha ele no menu de boot
(geralmente F12, F11, F9 ou Esc, depende do fabricante). O Sururu funciona com
**Secure Boot ligado**.

Em menos de um minuto você está na área de trabalho, e a Central Sururu abre
sozinha para dar as boas-vindas.

!!! warning "Modo live"
    Rodando direto do pendrive, o que você fizer some ao desligar. Para
    guardar seu progresso, use o ícone **Instalar** na área de trabalho e
    instale no disco (dá para instalar ao lado do Windows).

Próximo passo: [seu primeiro cluster](primeiro-cluster.md).
