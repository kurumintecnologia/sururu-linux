# Atualizações e versões

## De onde vêm as atualizações?

**Quase tudo vem direto do Debian.** O kernel, o Firefox, o desktop e as
bibliotecas são os pacotes oficiais do Debian 13, e as correções de segurança
chegam pelo mesmo caminho que chegam para qualquer Debian, normalmente no mesmo
dia em que são publicadas.

Para atualizar, como em qualquer Debian:

```bash
sudo apt update && sudo apt upgrade
```

ou pelo atualizador gráfico, que avisa sozinho.

## E o que é do Sururu?

Só o que é nosso de verdade: a Central, os laboratórios, a arte e as
configurações. Isso é pouco código, fica neste repositório e vai para as
próximas versões da ISO. No futuro, vai virar pacotes `sururu-*` num
repositório APT próprio, assinado, para atualizar junto com o resto.

As ferramentas de Kubernetes (`kubectl`, `helm`, `kind`, `k9s`) vêm dos
binários oficiais de cada projeto, com versão fixa e checksum conferido no
build. Um robô (Renovate) abre um pedido de atualização sempre que sai versão
nova.

## Calendário de versões

| Versão | Quando | Base |
|---|---|---|
| **2027.x "Isaac"** | Nova ISO a cada atualização pontual do Debian 13 (mais ou menos a cada 2 ou 3 meses) | Debian 13 "trixie" |
| **Próxima versão grande** | Alguns meses depois do lançamento do Debian 14 | Debian 14 "forky" |

O Debian 13 tem suporte de segurança até 2028 e suporte estendido (LTS) até
2030. Quem instalar o Sururu 2027 está coberto por esse período.

## Preciso baixar a ISO de novo a cada versão?

Não. Quem instalou no disco só roda `apt upgrade`. A ISO nova é para quem vai
instalar pela primeira vez ou usa o pendrive no modo live.

## Isso dá muito trabalho para manter?

Bem menos do que parece, e foi pensado para isso:

- **Segurança e pacotes**: o Debian faz. É o trabalho mais pesado e não é
  nosso.
- **Gerar a ISO**: o GitHub Actions monta, testa o boot, gera SBOM, varre
  vulnerabilidades e assina, sozinho, a cada versão marcada.
- **Ferramentas Kubernetes**: o Renovate abre o pedido; a gente revisa e
  aceita.
- **O que sobra para pessoas**: manter os laboratórios funcionando a cada
  versão nova do Kubernetes (são três por ano), revisar contribuições e
  responder dúvidas.
