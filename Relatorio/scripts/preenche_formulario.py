# -*- coding: utf-8 -*-
"""Preenche o formulario oficial da AGIR preservando header, logos e layout."""
import pymupdf, os

from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]

# Formulario em branco da AGIR. Baixe de agir.uff.br/bolsas e ajuste o caminho,
# ou passe como primeiro argumento na linha de comando.
import sys
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else (
    Path.home() / "Downloads" /
    "Relatório Final 2020-2021 - Daniel Henrique Nogueira Dias.pdf")
DST = RAIZ / "Relatorio" / "Formulario_Relatorio_Final_PIBITI_2025-2026.pdf"

from textos_formulario import TITULO, RESUMO, DIAGNOSTICO, SOLUCOES, RESULTADOS, REFERENCIAS

TEXTOS = {
    "Campo num#C3#A9rico 1":   "25",
    "Campo num#C3#A9rico 1_2": "26",
    "Caixa de texto 1":   TITULO,
    "Caixa de texto 2":   "Tiago Abud",
    "Caixa de texto 2_2": "Frederico José Poli Antunes",
    "Caixa de texto 3":   RESUMO,
    "Caixa de texto 4":   DIAGNOSTICO,
    "Caixa de texto 5":   SOLUCOES,
    "Caixa de texto 4_2": RESULTADOS,
    "Caixa de texto 5_2": REFERENCIAS,
    "Caixa de texto 1_2": "",   # justificativa de nao comparecimento
    "Caixa de texto 7":   "",   # cidade (fora de sede)
}

# Sim/Não  ->  comparece: Sim | sigilo: Não | fora de sede: Não | transporte: nenhum
MARCAS = {
    "Caixa de sele#C3#A7#C3#A3o 2":   True,   "Caixa de sele#C3#A7#C3#A3o 1":   False,
    "Caixa de sele#C3#A7#C3#A3o 2_2": False,  "Caixa de sele#C3#A7#C3#A3o 2_3": True,
    "Caixa de sele#C3#A7#C3#A3o 2_4": False,  "Caixa de sele#C3#A7#C3#A3o 2_5": True,
    "Caixa de sele#C3#A7#C3#A3o 2_6": False,  "Caixa de sele#C3#A7#C3#A3o 2_7": False,
    "Caixa de sele#C3#A7#C3#A3o 2_8": False,  "Caixa de sele#C3#A7#C3#A3o 2_9": True,
}

doc = pymupdf.open(SRC)
vistos = set()
for pg in doc:
    for w in pg.widgets():
        nome = w.field_name
        vistos.add(nome)
        if nome in TEXTOS:
            w.field_value = TEXTOS[nome]
            w.update()
        elif nome in MARCAS:
            w.field_value = bool(MARCAS[nome])
            w.update()

faltou = (set(TEXTOS) | set(MARCAS)) - vistos
assert not faltou, f"campos nao encontrados: {faltou}"

os.makedirs(os.path.dirname(DST), exist_ok=True)
doc.save(DST, deflate=True, garbage=3)
print("gravado:", DST)

v = pymupdf.open(DST)
for pg in v:
    for w in pg.widgets():
        val = w.field_value
        mostra = (val if isinstance(val, bool) else f"{len(val or '')} car.")
        print(f"   {w.field_name:34s} {mostra}")
