#!/usr/bin/env python3
"""Gera os papéis de parede do Sururu Linux (dia e noite) em SVG.

Cena: entardecer numa lagoa de Alagoas. Coqueiros à direita, raízes de
mangue à esquerda e, no céu, a trama do filé alagoano, que também é a malha
de nós de um cluster. Rode: python3 artwork/gerar-wallpapers.py
"""
import math
import random
from pathlib import Path

W, H = 1920, 1080
HORIZONTE = 700
OUT = Path(__file__).parent / "wallpaper"

TEMAS = {
    "dia": {
        "ceu": ["#0F3B40", "#2F7A63", "#E9C27A", "#F2B134"],
        "ceu_pos": [0, 0.38, 0.82, 1],
        "agua": ["#1F5E5C", "#0F3B40"],
        "astro": "#F2B134", "astro_r": 118, "astro_y": HORIZONTE - 40,
        "reflexo": "#F2B134",
        "silhueta": "#0B2A2E", "margem": "#123F3F",
        "file": "#E7F1EF", "file_op": 0.16, "no": "#F2B134",
        "marca": "#E7F1EF",
    },
    "noite": {
        "ceu": ["#14122A", "#1D2C4A", "#1D4C57", "#2F7A63"],
        "ceu_pos": [0, 0.45, 0.85, 1],
        "agua": ["#12343B", "#0B1A26"],
        "astro": "#E7F1EF", "astro_r": 54, "astro_y": 250,
        "reflexo": "#A9C9D0",
        "silhueta": "#070F17", "margem": "#0C2128",
        "file": "#A9C9D0", "file_op": 0.14, "no": "#F2B134",
        "marca": "#A9C9D0",
    },
}


def gradiente(gid, cores, pos, vertical=True):
    paradas = "".join(
        f'<stop offset="{p}" stop-color="{c}"/>' for c, p in zip(cores, pos)
    )
    eixo = 'x1="0" y1="0" x2="0" y2="1"' if vertical else 'x1="0" y1="0" x2="1" y2="0"'
    return f'<linearGradient id="{gid}" {eixo}>{paradas}</linearGradient>'


def file_alagoano(t):
    """Trama de filé: malha quadrada girada 45°, com nós acesos ligados."""
    passo = 46
    linhas = []
    for i in range(-30, 60):
        x0 = i * passo
        linhas.append(f"M{x0} 0 L{x0 + 620} 620")
        linhas.append(f"M{x0} 0 L{x0 - 620} 620")
    malha = (
        f'<path d="{" ".join(linhas)}" stroke="{t["file"]}" stroke-width="1.2" '
        f'fill="none" opacity="{t["file_op"]}" mask="url(#fadeFile)"/>'
    )
    # motivo de filé (estrela de quadradinhos cheios) no canto superior esquerdo
    motivo = []
    cx, cy = 360, 210
    for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0), (-2, 0),
                   (0, 2), (0, -2), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
        x = cx + (dx - dy) * passo / 2
        y = cy + (dx + dy) * passo / 2
        s = passo * 0.34
        motivo.append(
            f'<rect x="{x - s/2:.1f}" y="{y - s/2:.1f}" width="{s:.1f}" height="{s:.1f}" '
            f'transform="rotate(45 {x:.1f} {y:.1f})" fill="{t["file"]}" opacity="{t["file_op"] * 1.9:.2f}"/>'
        )
    # nós do cluster: alguns cruzamentos acesos, ligados por fios
    random.seed(27)
    nos = [(cx, cy), (cx + 3 * passo, cy + 2 * passo), (cx + 7 * passo, cy - 1 * passo),
           (cx + 11 * passo, cy + 3 * passo), (cx - 4 * passo, cy + 4 * passo)]
    fios = " ".join(f"M{a[0]} {a[1]} L{b[0]} {b[1]}" for a, b in zip(nos, nos[1:]))
    pontos = "".join(
        f'<circle cx="{x}" cy="{y}" r="{6 if i == 0 else 4}" fill="{t["no"]}" opacity="{0.9 if i == 0 else 0.6}"/>'
        for i, (x, y) in enumerate(nos)
    )
    return (
        malha + "".join(motivo)
        + f'<path d="{fios}" stroke="{t["no"]}" stroke-width="1.5" opacity="0.35" fill="none"/>'
        + pontos
    )


def coqueiro(base_x, altura, curva, cor, escala=1.0):
    """Coqueiro: tronco curvo afinando e folhas em arco que caem para os lados."""
    topo_x = base_x + curva
    topo_y = HORIZONTE + 40 - altura
    meio_x = base_x + curva * 0.15
    meio_y = topo_y + altura * 0.55
    tronco = (
        f'<path d="M{base_x - 16 * escala:.1f} {H} Q{meio_x - 6 * escala:.1f} {meio_y:.1f} '
        f'{topo_x - 5 * escala:.1f} {topo_y:.1f} L{topo_x + 5 * escala:.1f} {topo_y + 3:.1f} '
        f'Q{meio_x + 10 * escala:.1f} {meio_y:.1f} {base_x + 16 * escala:.1f} {H} Z" fill="{cor}"/>'
    )
    folhas = []
    # (direção horizontal, alcance, altura do arco, queda na ponta)
    for dirx, alc, arco, queda in [(-1, 1.00, 70, 120), (-1, 0.80, 95, 40), (-0.45, 0.55, 110, -10),
                                   (0.45, 0.55, 110, -10), (1, 0.80, 95, 40), (1, 1.00, 70, 120),
                                   (-0.15, 0.35, 90, 60), (0.7, 0.6, 30, 160)]:
        comp = 230 * escala * alc
        fx = topo_x + dirx * comp
        fy = topo_y + queda * escala
        cxq = topo_x + dirx * comp * 0.45
        cyq = topo_y - arco * escala
        folhas.append(
            f'<path d="M{topo_x:.1f} {topo_y:.1f} Q{cxq:.1f} {cyq:.1f} {fx:.1f} {fy:.1f}" '
            f'stroke="{cor}" stroke-width="{6 * escala:.1f}" fill="none" stroke-linecap="round"/>'
        )
        n = 14
        for k in range(2, n):
            u = k / n
            px = (1 - u) ** 2 * topo_x + 2 * (1 - u) * u * cxq + u ** 2 * fx
            py = (1 - u) ** 2 * topo_y + 2 * (1 - u) * u * cyq + u ** 2 * fy
            tam = (46 - 30 * u) * escala
            lado = 1 if dirx >= 0 else -1
            folhas.append(
                f'<path d="M{px:.1f} {py:.1f} q{lado * tam * 0.25:.1f} {tam * 0.5:.1f} {lado * tam * 0.15:.1f} {tam:.1f} '
                f'M{px:.1f} {py:.1f} q{-lado * tam * 0.35:.1f} {tam * 0.45:.1f} {-lado * tam * 0.45:.1f} {tam * 0.9:.1f}" '
                f'stroke="{cor}" stroke-width="{2.6 * escala:.1f}" fill="none" stroke-linecap="round"/>'
            )
    cocos = "".join(
        f'<circle cx="{topo_x + dx * escala:.1f}" cy="{topo_y + 12 * escala:.1f}" r="{8 * escala:.1f}" fill="{cor}"/>'
        for dx in (-9, 4, 14)
    )
    return tronco + "".join(folhas) + cocos


def mangue(cor):
    """Mangue: copa irregular sobre raízes-escora em arco que entram na água."""
    partes = []
    random.seed(7)
    # raízes
    for i in range(16):
        x = -20 + i * 30
        topo = 830 + (i % 4) * 12
        abre = 40 + (i * 13) % 50
        partes.append(
            f'<path d="M{x + 20} {topo} Q{x - abre * 0.2} {topo + 90} {x - abre} {H + 10}" '
            f'stroke="{cor}" stroke-width="{5 + i % 3}" fill="none" stroke-linecap="round"/>'
        )
        partes.append(
            f'<path d="M{x + 20} {topo} Q{x + abre * 0.6} {topo + 110} {x + abre * 0.9} {H + 10}" '
            f'stroke="{cor}" stroke-width="{4 + i % 2}" fill="none" stroke-linecap="round"/>'
        )
    # copa: soma de círculos
    for cx, cy, r in [(0, 780, 120), (90, 740, 95), (190, 770, 90), (290, 800, 80),
                      (370, 830, 60), (140, 820, 90), (40, 840, 90), (250, 845, 60)]:
        partes.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{cor}"/>')
    return "".join(partes)


def cena(nome, t):
    defs = [
        gradiente("ceu", t["ceu"], t["ceu_pos"]),
        gradiente("agua", t["agua"], [0, 1]),
        '<linearGradient id="fadeGrad" x1="0" y1="0" x2="0.9" y2="0.9">'
        '<stop offset="0" stop-color="#fff"/><stop offset="0.6" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        f'<mask id="fadeFile"><rect width="{W}" height="{HORIZONTE}" fill="url(#fadeGrad)"/></mask>',
        f'<radialGradient id="brilho"><stop offset="0" stop-color="{t["astro"]}" stop-opacity="0.55"/>'
        f'<stop offset="1" stop-color="{t["astro"]}" stop-opacity="0"/></radialGradient>',
        f'<clipPath id="acimaAgua"><rect width="{W}" height="{HORIZONTE}"/></clipPath>',
    ]
    ax, ay, ar = 1330, t["astro_y"], t["astro_r"]
    reflexo = []
    for i in range(14):
        y = HORIZONTE + 14 + i * 22
        meia = (ar * 1.1) * (1 - i / 18) + 10
        reflexo.append(
            f'<rect x="{ax - meia:.0f}" y="{y}" width="{2 * meia:.0f}" height="{4 + i % 3}" rx="3" '
            f'fill="{t["reflexo"]}" opacity="{0.55 - i * 0.035:.2f}"/>'
        )
    ondas = "".join(
        f'<path d="M{x} {HORIZONTE + 40 + (x * 7) % 300} h{60 + x % 90}" stroke="{t["file"]}" '
        f'stroke-width="2" opacity="0.10" stroke-linecap="round"/>'
        for x in range(80, W, 137)
    )
    margem = (
        f'<path d="M0 {HORIZONTE} L0 {HORIZONTE - 18} Q200 {HORIZONTE - 34} 420 {HORIZONTE - 20} '
        f'Q700 {HORIZONTE - 4} 980 {HORIZONTE - 16} Q1250 {HORIZONTE - 30} 1500 {HORIZONTE - 12} '
        f'Q1720 {HORIZONTE - 2} {W} {HORIZONTE - 14} L{W} {HORIZONTE} Z" fill="{t["margem"]}"/>'
    )
    marca = (
        f'<text x="64" y="{H - 52}" font-family="IBM Plex Sans, Inter, sans-serif" font-size="26" '
        f'fill="{t["marca"]}" opacity="0.55"><tspan font-weight="600">sururu</tspan>'
        f'<tspan font-weight="300"> linux 2027</tspan></text>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<title>Sururu Linux — lagoa ({nome})</title>
<defs>{"".join(defs)}</defs>
<rect width="{W}" height="{HORIZONTE}" fill="url(#ceu)"/>
{file_alagoano(t)}
<circle cx="{ax}" cy="{ay}" r="{ar * 3}" fill="url(#brilho)"/>
<g clip-path="url(#acimaAgua)"><circle cx="{ax}" cy="{ay}" r="{ar}" fill="{t["astro"]}"/></g>
<rect y="{HORIZONTE}" width="{W}" height="{H - HORIZONTE}" fill="url(#agua)"/>
{margem}
{"".join(reflexo)}
{ondas}
{mangue(t["silhueta"])}
{coqueiro(1560, 320, 30, t["silhueta"], 0.75)}
{coqueiro(1690, 520, -60, t["silhueta"], 1.1)}
{coqueiro(1850, 420, 50, t["silhueta"], 0.9)}
{marca}
</svg>
'''


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for nome, tema in TEMAS.items():
        (OUT / f"sururu-lagoa-{nome}.svg").write_text(cena(nome, tema), encoding="utf-8")
        print(f"ok: wallpaper/sururu-lagoa-{nome}.svg")
