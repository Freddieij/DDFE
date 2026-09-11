# -*- coding: utf-8 -*-
"""Quantas linhas cada caixa comporta e quantas o texto ocupa."""
import pymupdf, importlib.util, sys

import os
_aqui = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "p", os.path.join(_aqui, "preenche_formulario.py"))
P = importlib.util.module_from_spec(spec)
sys.modules["p"] = P
try:
    spec.loader.exec_module(P)
except SystemExit:
    pass

FONT, SIZE = "helv", 11.0
LINE = SIZE * 1.16

def quebra(texto, largura):
    linhas = 0
    for par in texto.split("\n"):
        if not par.strip():
            linhas += 1
            continue
        atual = ""
        for palavra in par.split(" "):
            teste = (atual + " " + palavra).strip()
            if pymupdf.get_text_length(teste, FONT, SIZE) <= largura:
                atual = teste
            else:
                linhas += 1
                atual = palavra
        linhas += 1
    return linhas

doc = pymupdf.open(P.SRC)
for pg in doc:
    for w in pg.widgets():
        nome = w.field_name
        if nome not in P.TEXTOS:
            continue
        txt = P.TEXTOS[nome]
        if len(txt) < 60:
            continue
        larg = w.rect.width - 8
        cabem = int((w.rect.height - 4) // LINE)
        usa = quebra(txt, larg)
        st = "OK  " if usa <= cabem else "ESTOURA"
        print(f"{st} {nome:20s} cabem={cabem:3d} linhas  usa={usa:3d}  "
              f"(sobra {cabem-usa:+d})  {len(txt)} car.")
