#!/bin/sh
# Aplica o tema do Sururu nos menus de boot da ISO (GRUB e isolinux).
# Parte dos modelos oficiais do live-build instalados na máquina e troca só a
# arte, as cores e os nomes. Assim acompanhamos as atualizações do live-build.
set -e
ORIGEM="${LB_BOOTLOADERS:-/usr/share/live/build/bootloaders}"
DESTINO=config/bootloaders
ARTE=artwork/boot

if [ ! -d "$ORIGEM" ]; then
  echo "AVISO: $ORIGEM não existe (live-build não instalado?). Menu de boot fica padrão."
  exit 0
fi

rm -rf "$DESTINO"
cp -rL "$ORIGEM" "$DESTINO"

# 1. Fundo: troca o splash SVG (com o capacete) pelo nosso PNG
find "$DESTINO" \( -name 'splash.svg' -o -name 'splash.svg.in' \) -delete
find "$DESTINO" -mindepth 1 -type d | while read -r dir; do
  case "$dir" in
    *isolinux*|*syslinux*|*extlinux*|*pxelinux*) cp "$ARTE/splash-4x3.png" "$dir/splash.png" ;;
    *grub*) cp "$ARTE/splash-16x9.png" "$dir/splash.png" ;;
  esac
done

# 2. Cores do tema do GRUB (nácar, sol de Alagoas e lagoa)
find "$DESTINO" -name 'theme.txt' | while read -r t; do
  sed -i -E \
    -e 's/(^|[[:space:]])(item_color[[:space:]]*=[[:space:]]*)"[^"]*"/\1\2"#A9C9D0"/' \
    -e 's/(selected_item_color[[:space:]]*=[[:space:]]*)"[^"]*"/\1"#F2B134"/' \
    -e 's/(title-color[[:space:]]*:[[:space:]]*)"[^"]*"/\1"#E7F1EF"/' \
    -e 's/(message-color[[:space:]]*:[[:space:]]*)"[^"]*"/\1"#A9C9D0"/' \
    -e 's/(fg_color[[:space:]]*=[[:space:]]*)"[^"]*"/\1"#F2B134"/' \
    -e 's/(bg_color[[:space:]]*=[[:space:]]*)"[^"]*"/\1"#0F3B40"/' \
    -e 's/(title-text[[:space:]]*:[[:space:]]*)"[^"]*"/\1""/' \
    "$t"
done

# 3. Cores do menu do isolinux
find "$DESTINO" -name 'stdmenu.cfg' | while read -r m; do
  sed -i -E \
    -e 's/^(menu color sel[[:space:]]+).*/\1* #ff0f3b40 #fff2b134 none/' \
    -e 's/^(menu color unsel[[:space:]]+).*/\1* #ffe7f1ef #00000000 none/' \
    -e 's/^(menu color title[[:space:]]+).*/\1* #ffe7f1ef #00000000 none/' \
    -e 's/^(menu color hotsel[[:space:]]+).*/\1* #ff0f3b40 #fff2b134 none/' \
    -e 's/^(menu color tabmsg[[:space:]]+).*/\1* #ffa9c9d0 #00000000 none/' \
    "$m"
done

# 4. Nomes em português no menu
find "$DESTINO" -name '*.cfg' | while read -r c; do
  sed -i -E \
    -e 's/Live system \(([^)]*) fail-safe mode\)/Sururu Linux em modo de segurança (\1)/g' \
    -e 's/Live system \(fail-safe mode\)/Sururu Linux em modo de segurança/g' \
    -e 's/Live system/Experimentar o Sururu Linux/g' \
    -e 's/Debian GNU\/Linux/Sururu Linux/g' \
    -e 's/Utilities/Utilitários/g' \
    -e 's/Advanced options/Opções avançadas/g' \
    -e 's/UEFI Firmware Settings/Configurações do firmware (UEFI)/g' \
    "$c"
done

echo "Tema de boot aplicado em $DESTINO"
