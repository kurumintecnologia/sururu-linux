#!/bin/sh
# Aplica o tema do Sururu nos menus de boot da ISO (GRUB e isolinux).
# Parte dos modelos oficiais do live-build instalados na máquina e troca só a
# arte, as cores e os nomes. Assim acompanhamos as atualizações do live-build.
#
# Atenção: o isolinux (boot por BIOS) NÃO entende acentos. Nos arquivos dele
# os textos ficam sem acento ("Utilitarios"). O GRUB (UEFI) entende UTF-8.
set -e
ORIGEM="${LB_BOOTLOADERS:-/usr/share/live/build/bootloaders}"
DESTINO=config/bootloaders
ARTE=artwork/boot

if [ ! -d "$ORIGEM" ]; then
  echo "AVISO: $ORIGEM não existe (live-build não instalado?). Menu de boot fica padrão."
  exit 0
fi

rm -rf "$DESTINO"
# -a preserva os atalhos (ex.: isolinux.bin -> /usr/lib/ISOLINUX/...). O
# live-build resolve esses atalhos sozinho durante o build.
cp -a "$ORIGEM" "$DESTINO"

# Atalhos de pasta que apontam para o modelo original passam a apontar para a
# nossa cópia (assim o tema vale também para o grub-efi, por exemplo)
find "$DESTINO" -type l | while read -r link; do
  alvo=$(readlink "$link")
  case "$alvo" in
    "$ORIGEM"/*)
      novo="$(pwd)/$DESTINO/${alvo#"$ORIGEM"/}"
      [ -d "$novo" ] && ln -sfn "$(realpath --relative-to="$(dirname "$link")" "$novo")" "$link"
      ;;
  esac
done

eh_syslinux() {
  case "$1" in *isolinux*|*syslinux*|*extlinux*|*pxelinux*) return 0 ;; esac
  return 1
}

# 1. Fundo: troca o splash SVG (com o capacete) pelo nosso PNG
find "$DESTINO" -type f \( -name 'splash.svg' -o -name 'splash.svg.in' \) -delete
find "$DESTINO" -mindepth 1 -type d | while read -r dir; do
  if eh_syslinux "$dir"; then
    cp "$ARTE/splash-isolinux.png" "$dir/splash.png"
  else
    case "$dir" in *grub*) cp "$ARTE/splash-16x9.png" "$dir/splash.png" ;; esac
  fi
done

# 2. Cores do tema do GRUB (nácar, sol de Alagoas e lagoa)
find "$DESTINO" -type f -name 'theme.txt' | while read -r t; do
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

# 3. Menu do isolinux: 1024x768, cores e posição casando com o splash
#    (grade de 8x16 px: 128 colunas x 48 linhas; menu na linha 21)
find "$DESTINO" -type f -name 'stdmenu.cfg' | while read -r m; do
  sed -i -E '/^[[:space:]]*menu (resolution|width|margin|rows|vshift|hshift|tabmsgrow|cmdlinerow|timeoutrow|helpmsgrow|helpmsgendrow|tabmsg|color)[[:space:]]/Id' "$m"
  cat >> "$m" <<'CFG'

# --- tema Sururu ---
menu resolution 1024 768
menu width 74
menu margin 4
menu rows 9
menu vshift 21
menu hshift 27
menu tabmsgrow 43
menu cmdlinerow 43
menu timeoutrow 44
menu helpmsgrow 40
menu helpmsgendrow 41
menu tabmsg Pressione ENTER para iniciar ou TAB para editar a linha de boot
menu color screen  * #00000000 #00000000 none
menu color border  * #00000000 #00000000 none
menu color title   * #ffe7f1ef #00000000 none
menu color sel     * #ff0f3b40 #fff2b134 none
menu color hotsel  * #ff0f3b40 #fff2b134 none
menu color unsel   * #ffe7f1ef #00000000 none
menu color hotkey  * #fff2b134 #00000000 none
menu color tabmsg  * #ffa9c9d0 #00000000 none
menu color cmdmark * #fff2b134 #00000000 none
menu color cmdline * #ffe7f1ef #00000000 none
menu color timeout_msg * #ffa9c9d0 #00000000 none
menu color timeout * #fff2b134 #00000000 none
menu color help    * #ffa9c9d0 #00000000 none
menu color disabled * #ff5b7a78 #00000000 none
CFG
done

# 4. Nomes em português
find "$DESTINO" -type f \( -name '*.cfg' -o -name '*.cfg.in' \) | while read -r c; do
  if eh_syslinux "$c"; then
    # isolinux: sem acentos
    sed -i -E \
      -e 's/Live system \(([^)]*) fail-safe mode\)/Sururu Linux - modo de seguranca (\1)/g' \
      -e 's/Live system \(fail-safe mode\)/Sururu Linux - modo de seguranca/g' \
      -e 's/Live system/Experimentar o Sururu Linux/g' \
      -e 's/Debian GNU\/Linux/Sururu Linux/g' \
      -e 's/^([[:space:]]*menu title[[:space:]]+)Boot menu/\1Escolha como iniciar/I' \
      -e 's/Utilities/Utilitarios/g' \
      -e 's/Utilitários/Utilitarios/g' \
      -e 's/Hardware Detection Tool \(HDT\)/Detectar hardware (HDT)/g' \
      -e 's/Memory Diagnostic Tool \(memtest86\+\)/Testar memoria (memtest86+)/g' \
      -e 's/Return to main menu/Voltar ao menu principal/g' \
      -e 's/^([[:space:]]*menu label[[:space:]]+)\^?Back/\1Voltar/I' \
      "$c"
  else
    sed -i -E \
      -e 's/Live system \(([^)]*) fail-safe mode\)/Sururu Linux em modo de segurança (\1)/g' \
      -e 's/Live system \(fail-safe mode\)/Sururu Linux em modo de segurança/g' \
      -e 's/Live system/Experimentar o Sururu Linux/g' \
      -e 's/Debian GNU\/Linux/Sururu Linux/g' \
      -e 's/Utilities/Utilitários/g' \
      -e 's/Advanced options/Opções avançadas/g' \
      -e 's/UEFI Firmware Settings/Configurações do firmware (UEFI)/g' \
      -e 's/Memory Diagnostic Tool/Testar a memória/g' \
      "$c"
  fi
done

echo "Tema de boot aplicado em $DESTINO"
