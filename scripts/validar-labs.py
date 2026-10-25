#!/usr/bin/env python3
"""Confere se todos os laboratórios em central/labs têm os campos obrigatórios."""
import json
import sys
from pathlib import Path

OBRIGATORIOS = ["id", "trilha", "ordem", "titulo", "nivel", "tempo", "precisa",
                "prova", "resumo", "historia", "passos", "verificacoes", "solucao", "limpeza"]
TRILHAS = {"linux", "containers", "kubernetes"}
PRECISA = {"docker", "cluster"}

erros = []
ids = set()
labs = sorted(Path(__file__).resolve().parent.parent.joinpath("central/labs").glob("*.json"))
for arq in labs:
    try:
        lab = json.loads(arq.read_text(encoding="utf-8"))
    except ValueError as e:
        erros.append(f"{arq.name}: JSON inválido ({e})")
        continue
    faltando = [c for c in OBRIGATORIOS if c not in lab]
    if faltando:
        erros.append(f"{arq.name}: faltam os campos {', '.join(faltando)}")
        continue
    if lab["id"] + ".json" != arq.name:
        erros.append(f"{arq.name}: o id deve ser igual ao nome do arquivo")
    if lab["id"] in ids:
        erros.append(f"{arq.name}: id repetido")
    ids.add(lab["id"])
    if lab["trilha"] not in TRILHAS:
        erros.append(f"{arq.name}: trilha deve ser uma de {sorted(TRILHAS)}")
    if not set(lab["precisa"]) <= PRECISA:
        erros.append(f"{arq.name}: 'precisa' aceita só {sorted(PRECISA)}")
    if not lab["verificacoes"]:
        erros.append(f"{arq.name}: precisa de pelo menos uma verificação")
    for v in lab["verificacoes"]:
        if not {"texto", "comando", "dica"} <= v.keys():
            erros.append(f"{arq.name}: cada verificação precisa de texto, comando e dica")

if erros:
    print("\n".join(erros))
    sys.exit(1)
print(f"{len(labs)} laboratórios ok")
