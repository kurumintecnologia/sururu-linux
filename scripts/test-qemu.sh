#!/bin/sh
# Teste de boot: abre a ISO no QEMU. Uso: ./scripts/test-qemu.sh [arquivo.iso]
#   MEM=8192 ./scripts/test-qemu.sh   -> mais memória (o cluster precisa de 8 GB no live)
#   UEFI=1   ./scripts/test-qemu.sh   -> boot UEFI (menu do GRUB) em vez de BIOS (isolinux)
#   HEADLESS=1 (CI): espera o login aparecer na serial
set -e
ISO="${1:-$(ls -1 sururu-isaac-*.hybrid.iso 2>/dev/null | head -1)}"
[ -f "$ISO" ] || { echo "ISO não encontrada"; exit 1; }
MEM="${MEM:-6144}"

ACCEL=""
if [ -w /dev/kvm ]; then
  ACCEL="-enable-kvm -cpu host"
else
  echo "AVISO: sem aceleração KVM. Vai ficar MUITO lento (e o cluster trava)."
  echo "       Para ligar: sudo usermod -aG kvm \$USER  e entre de novo na sessão."
fi

FIRMWARE=""
if [ "${UEFI:-0}" = "1" ]; then
  for f in /usr/share/OVMF/OVMF_CODE_4M.fd /usr/share/OVMF/OVMF_CODE.fd /usr/share/ovmf/OVMF.fd; do
    [ -f "$f" ] && FIRMWARE="-bios $f" && break
  done
  [ -n "$FIRMWARE" ] || echo "AVISO: instale o pacote ovmf para testar UEFI."
fi

if [ "${HEADLESS:-0}" = "1" ]; then
  # shellcheck disable=SC2086
  timeout 600 qemu-system-x86_64 $ACCEL $FIRMWARE -m 3072 -smp 2 -cdrom "$ISO" \
    -boot d -nographic -serial mon:stdio 2>/dev/null \
    | tee boot.log | grep -m1 -q "login:" && echo "BOOT OK" || { echo "BOOT FALHOU"; exit 1; }
else
  # shellcheck disable=SC2086
  qemu-system-x86_64 $ACCEL $FIRMWARE -m "$MEM" -smp 2 -cdrom "$ISO" -boot d -vga virtio
fi
