# Identidade visual do Sururu Linux

A paleta vem da lagoa, do mangue e do filé alagoano, o bordado de rede de
Pontal da Barra. A trama do filé aparece no céu dos papéis de parede e vira a
malha de nós de um cluster: Alagoas e Kubernetes no mesmo desenho.

| Nome           | Hex       | Uso                                         |
|----------------|-----------|---------------------------------------------|
| Lagoa funda    | `#0F3B40` | cor principal escura, painel, títulos       |
| Mangue         | `#2F7A63` | cor principal, botões, links                |
| Água rasa      | `#E7F1EF` | fundo claro                                 |
| Nácar          | `#A9C9D0` | bordas, detalhes, texto suave no escuro     |
| Sol de Alagoas | `#F2B134` | destaque único (a pérola do logo, sucesso)  |
| Concha         | `#2B2747` | sombra do logo, modo noite                  |

## Tipografia
- **IBM Plex Sans**: interface e títulos (pacote `fonts-ibm-plex`)
- **JetBrains Mono**: comandos e terminal (pacote `fonts-jetbrains-mono`)

## Arquivos
- `sururu-simbolo.svg`: a concha sozinha (ícone, menu, favicon)
- `sururu-logo.svg`: concha + nome
- `wallpaper/sururu-lagoa-dia.svg` e `wallpaper/sururu-lagoa-noite.svg`:
  gerados por `gerar-wallpapers.py`. Edite o script, não o SVG.

## O símbolo
Uma concha de sururu. As linhas de crescimento da concha ligam três nós (o
cluster), e a pérola amarela na ponta é o sol de Alagoas.

## Arte de boot
- `boot/splash-16x9.png` (GRUB) e `boot/splash-4x3.png` (isolinux): fundo do menu de boot
- `boot/plymouth-*.png`: peças da tela de carregamento (concha, nome e nós)
- Gerados por `gerar-boot.py` (SVG) e `scripts/renderizar-arte.py` (PNG), com `make pngs`
- `scripts/tema-boot.sh` aplica tudo sobre os modelos oficiais do live-build
