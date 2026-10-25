#!/usr/bin/env python3
"""Gera a arte de boot do Sururu Linux em SVG.

- boot/splash-16x9.svg  fundo do menu do GRUB (1920x1080)
- boot/splash-4x3.svg   fundo do menu do isolinux (640x480)
- boot/plymouth-*.svg   peças da tela de carregamento

Os PNGs usados na ISO ficam em artwork/boot/*.png e são gerados por
scripts/renderizar-arte.py (precisa do Playwright). Assim quem só gera a ISO
não precisa de nenhuma ferramenta gráfica.
"""
from pathlib import Path

OUT = Path(__file__).parent / "boot"

CONCHA = '''
<g>
  <path d="M24 106 C14 86 20 52 44 30 C62 14 88 10 104 20 C118 30 116 52 102 70 C86 92 58 108 34 110 C29 110 26 109 24 106 Z" fill="url(#casca)"/>
  <path d="M46 34 C62 20 86 16 100 25 C110 32 110 47 100 61" fill="none" stroke="url(#nacar)" stroke-width="5" stroke-linecap="round" opacity="0.9"/>
  <path d="M30 100 C44 80 62 60 92 40" fill="none" stroke="#A9C9D0" stroke-width="3" stroke-linecap="round" opacity="0.6"/>
  <path d="M34 104 C54 94 74 80 98 58" fill="none" stroke="#A9C9D0" stroke-width="3" stroke-linecap="round" opacity="0.4"/>
  <circle cx="92" cy="40" r="5" fill="#E7F1EF"/>
  <circle cx="98" cy="58" r="4" fill="#E7F1EF" opacity="0.85"/>
  <circle cx="62" cy="66" r="4" fill="#E7F1EF" opacity="0.85"/>
  <circle cx="29" cy="103" r="7" fill="#F2B134"/>
</g>'''

DEFS = '''
<linearGradient id="casca" x1="0.15" y1="0.9" x2="0.85" y2="0.1">
  <stop offset="0" stop-color="#3A3463"/><stop offset="0.55" stop-color="#1F5A66"/><stop offset="1" stop-color="#3B9A7C"/>
</linearGradient>
<linearGradient id="nacar" x1="0" y1="0" x2="1" y2="1">
  <stop offset="0" stop-color="#E7F1EF"/><stop offset="1" stop-color="#A9C9D0"/>
</linearGradient>
<linearGradient id="fundo" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#14122A"/><stop offset="0.55" stop-color="#0F2B36"/><stop offset="1" stop-color="#0C3A3E"/>
</linearGradient>
<radialGradient id="halo" cx="0.5" cy="0.5" r="0.5">
  <stop offset="0" stop-color="#2F7A63" stop-opacity="0.45"/><stop offset="1" stop-color="#2F7A63" stop-opacity="0"/>
</radialGradient>
'''

FONTE = "IBM Plex Sans, Inter Display, Inter, DejaVu Sans, sans-serif"


def trama(w, h, passo, opacidade):
    linhas = []
    for i in range(-(h // passo) - 2, (w // passo) + 3):
        x = i * passo
        linhas.append(f"M{x} 0 L{x + h} {h}")
        linhas.append(f"M{x + h} 0 L{x} {h}")
    return (f'<path d="{" ".join(linhas)}" stroke="#A9C9D0" stroke-width="1" '
            f'fill="none" opacity="{opacidade}"/>')


def lagoa(w, h, y0):
    """Faixa da lagoa no rodapé, com a margem e reflexos."""
    ondas = "".join(
        f'<rect x="{x}" y="{h * 0.975 + (x * 7) % max(4, int(h * 0.018)):.0f}" width="{40 + x % 70}" height="2" rx="1" fill="#A9C9D0" opacity="0.10"/>'
        for x in range(30, w, max(60, w // 22))
    )
    return (
        f'<rect y="{y0}" width="{w}" height="{h - y0}" fill="#0B2A2E"/>'
        f'<path d="M0 {y0} Q{w * 0.25} {y0 - h * 0.018} {w * 0.5} {y0 - h * 0.006} '
        f'Q{w * 0.78} {y0 + h * 0.004} {w} {y0 - h * 0.014} L{w} {y0} Z" fill="#0B2A2E"/>'
        + ondas
    )


def splash(w, h):
    """Fundo do menu de boot: marca no terço de cima, área livre embaixo para o menu."""
    s = h / 1080
    cx = w / 2
    tam = 150 * s
    y_logo = h * 0.14
    texto_y = y_logo + tam + 92 * s
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<defs>{DEFS}</defs>
<rect width="{w}" height="{h}" fill="url(#fundo)"/>
{trama(w, h, max(18, int(46 * s)), 0.07)}
<ellipse cx="{cx}" cy="{y_logo + tam / 2}" rx="{tam * 1.9}" ry="{tam * 1.5}" fill="url(#halo)"/>
<g transform="translate({cx - tam / 2} {y_logo}) scale({tam / 128})">{CONCHA}</g>
<text x="{cx}" y="{texto_y}" text-anchor="middle" font-family="{FONTE}" font-size="{86 * s}" letter-spacing="{-2 * s}" fill="#E7F1EF"><tspan font-weight="600">sururu</tspan><tspan font-weight="300" fill="#7CC4A8"> linux</tspan></text>
<text x="{cx}" y="{texto_y + 48 * s}" text-anchor="middle" font-family="{FONTE}" font-size="{26 * s}" fill="#A9C9D0" letter-spacing="{3 * s}">2027  ISAAC</text>
{lagoa(w, h, h * 0.9)}
<text x="{cx}" y="{h * 0.955}" text-anchor="middle" font-family="{FONTE}" font-size="{22 * s}" fill="#A9C9D0" opacity="0.8">Linux, containers e Kubernetes sem bicho de sete cabeças</text>
</svg>
'''


def splash_isolinux():
    """Menu do isolinux (BIOS) em 1024x768. O menu do syslinux usa uma grade de
    8x16 pixels: 128 colunas e 48 linhas. A marca ocupa as linhas 1 a 18, o menu
    começa na linha 21 e a ajuda fica na linha 43 (ver scripts/tema-boot.sh)."""
    w, h = 1024, 768
    cx = w / 2
    tam = 112
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">
<defs>{DEFS}</defs>
<rect width="{w}" height="{h}" fill="url(#fundo)"/>
{trama(w, h, 28, 0.07)}
<ellipse cx="{cx}" cy="{36 + tam / 2}" rx="{tam * 1.9}" ry="{tam * 1.4}" fill="url(#halo)"/>
<g transform="translate({cx - tam / 2} 36) scale({tam / 128})">{CONCHA}</g>
<text x="{cx}" y="222" text-anchor="middle" font-family="{FONTE}" font-size="62" letter-spacing="-1.5" fill="#E7F1EF"><tspan font-weight="600">sururu</tspan><tspan font-weight="300" fill="#7CC4A8"> linux</tspan></text>
<text x="{cx}" y="258" text-anchor="middle" font-family="{FONTE}" font-size="19" fill="#A9C9D0" letter-spacing="3">2027  ISAAC</text>
<rect x="208" y="322" width="608" height="180" rx="10" fill="#0B2A2E" opacity="0.55"/>
{lagoa(w, h, h * 0.93)}
<text x="{cx}" y="{h - 22}" text-anchor="middle" font-family="{FONTE}" font-size="17" fill="#A9C9D0" opacity="0.85">Linux, containers e Kubernetes sem bicho de sete cabeças</text>
</svg>
'''


def plymouth_logo():
    """Concha com halo, para o centro da tela de carregamento (fundo transparente)."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 360" width="360" height="360">
<defs>{DEFS}</defs>
<ellipse cx="180" cy="180" rx="175" ry="150" fill="url(#halo)"/>
<g transform="translate(80 80) scale(1.5625)">{CONCHA}</g>
</svg>
'''


def plymouth_nome():
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 110" width="520" height="110">
<text x="260" y="72" text-anchor="middle" font-family="{FONTE}" font-size="72" letter-spacing="-2" fill="#E7F1EF"><tspan font-weight="600">sururu</tspan><tspan font-weight="300" fill="#7CC4A8"> linux</tspan></text>
</svg>
'''


def plymouth_ponto(cor, nome):
    return nome, f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
<circle cx="12" cy="12" r="7" fill="{cor}"/>
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    arquivos = {
        "splash-16x9.svg": splash(1920, 1080),
        "splash-4x3.svg": splash(640, 480),
        "splash-isolinux.svg": splash_isolinux(),
        "plymouth-logo.svg": plymouth_logo(),
        "plymouth-nome.svg": plymouth_nome(),
    }
    for nome, svg in [plymouth_ponto("#2F7A63", "plymouth-no.svg"),
                      plymouth_ponto("#F2B134", "plymouth-no-ativo.svg")]:
        arquivos[nome] = svg
    for nome, svg in arquivos.items():
        (OUT / nome).write_text(svg, encoding="utf-8")
        print("ok:", f"boot/{nome}")
