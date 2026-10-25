#!/usr/bin/env python3
"""Transforma os SVGs de boot em PNG (GRUB, isolinux e Plymouth só leem PNG).

Uso (só quem mexe na arte precisa): pip install playwright && playwright install chromium
    python3 scripts/renderizar-arte.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

ARTE = Path(__file__).resolve().parent.parent / "artwork"
BOOT = ARTE / "boot"
ALVOS = [
    ("../wallpaper/sururu-lagoa-dia.svg", "../wallpaper/sururu-lagoa-dia.png", 3840, 2160, False),
    ("../wallpaper/sururu-lagoa-noite.svg", "../wallpaper/sururu-lagoa-noite.png", 3840, 2160, False),
    ("splash-16x9.svg", "splash-16x9.png", 1920, 1080, False),
    ("splash-4x3.svg", "splash-4x3.png", 640, 480, False),
    ("splash-isolinux.svg", "splash-isolinux.png", 1024, 768, False),
    ("plymouth-logo.svg", "plymouth-logo.png", 360, 360, True),
    ("plymouth-nome.svg", "plymouth-nome.png", 520, 110, True),
    ("plymouth-no.svg", "plymouth-no.png", 24, 24, True),
    ("plymouth-no-ativo.svg", "plymouth-no-ativo.png", 24, 24, True),
]

with sync_playwright() as p:
    nav = p.chromium.launch()
    for svg, png, w, h, transparente in ALVOS:
        pg = nav.new_page(viewport={"width": w, "height": h})
        corpo = (BOOT / svg).read_text(encoding="utf-8")
        corpo = corpo.replace("<svg ", f'<svg style="width:{w}px;height:{h}px;display:block" ', 1)
        pg.set_content(f"<html><body style='margin:0;background:transparent'>{corpo}</body></html>")
        pg.screenshot(path=str(BOOT / png), omit_background=transparente,
                      clip={"x": 0, "y": 0, "width": w, "height": h})
        print("ok:", png)
    nav.close()
