#!/bin/sh
# Smoke test: boota a ISO no QEMU. Uso: ./scripts/test-qemu.sh [arquivo.iso]
# Em modo headless (CI), passe HEADLESS=1: espera o login aparecer na serial.
set -e
ISO="${1:-$(ls -1 sururu-isaac-*.hybrid.iso 2>/dev/null | head -1)}"
[ -f "$ISO" ] || { echo "ISO não encontrada"; exit 1; }

ACCEL=""
[ -w /dev/kvm ] && ACCEL="-enable-kvm -cpu host"

if [ "${HEADLESS:-0}" = "1" ]; then
  timeout 600 qemu-system-x86_64 $ACCEL -m 3072 -smp 2 -cdrom "$ISO" \
    -boot d -nographic -serial mon:stdio 2>/dev/null \
    | tee boot.log | grep -m1 -q "login:" && echo "BOOT OK" || { echo "BOOT FALHOU"; exit 1; }
else
  qemu-system-x86_64 $ACCEL -m 4096 -smp 2 -cdrom "$ISO" -boot d -vga virtio
fi
