#!/usr/bin/env python3
"""Gera o Pix "copia e cola" (BR Code estático, padrão do Banco Central) e o QR Code.

Sem valor fixo: quem doa escolhe quanto quer mandar.
Uso: python3 scripts/gerar-pix.py
Saída: pagina/img/pix.svg, docs/img/pix.svg e pagina/pix.txt (copia e cola)
"""
from pathlib import Path

import qrcode
import qrcode.image.svg

CHAVE = "engineer@tacio.cloud"
NOME = "TACIO SOUZA DE OLIVEIRA"   # até 25 caracteres, sem acento
CIDADE = "ARACAJU"                 # até 15 caracteres, sem acento
IDENTIFICADOR = "SURURU"           # aparece no extrato de quem recebe

RAIZ = Path(__file__).resolve().parent.parent


def campo(id_: str, valor: str) -> str:
    return f"{id_}{len(valor):02d}{valor}"


def crc16(dados: str) -> str:
    """CRC16-CCITT (polinômio 0x1021, valor inicial 0xFFFF), exigido pelo BR Code."""
    crc = 0xFFFF
    for byte in dados.encode("utf-8"):
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else (crc << 1)
            crc &= 0xFFFF
    return f"{crc:04X}"


def payload() -> str:
    conta = campo("00", "br.gov.bcb.pix") + campo("01", CHAVE)
    corpo = (
        campo("00", "01")              # versão do payload
        + campo("26", conta)           # dados da conta Pix
        + campo("52", "0000")          # categoria
        + campo("53", "986")           # moeda: real
        + campo("58", "BR")
        + campo("59", NOME)
        + campo("60", CIDADE)
        + campo("62", campo("05", IDENTIFICADOR))
        + "6304"                       # CRC vem a seguir
    )
    return corpo + crc16(corpo)


if __name__ == "__main__":
    codigo = payload()
    img = qrcode.make(codigo, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=2)
    for destino in (RAIZ / "pagina/img/pix.svg", RAIZ / "docs/img/pix.svg"):
        destino.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(destino))
    (RAIZ / "pagina/pix.txt").write_text(codigo + "\n", encoding="utf-8")
    print(codigo)
