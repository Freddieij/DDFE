"""Confere se a Lista de Figuras/Tabelas aponta a pagina real de cada legenda."""
import re, sys, pypdf

from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]
pdf = RAIZ / "Relatorio" / "Relatorio_Final_PIBITI_2025-2026.pdf"
r = pypdf.PdfReader(pdf)
pages = [(p.extract_text() or "").replace("\u00a0", " ") for p in r.pages]

offset = None
for i, t in enumerate(pages):
    if "1.1" in t and "Ferramentas de modelagem" in t:
        offset = i
        break
if offset is None:
    sys.exit("nao achei o inicio do corpo")

# Paginas reais de cada legenda "Figura N —" / "Tabela N —"
real = {}
for i, t in enumerate(pages):
    for kind, num in re.findall(r"\b(Figura|Tabela)\s+(\d+)\s*\u2014", t):
        real.setdefault(f"{kind} {num}", i - offset + 1)

# O que as listas declaram (pontos-guia sao ". . . ." no texto extraido)
LEADER = re.compile(r"(?:\.[ \t]){3,}\.?")
ENTRY = re.compile(r"\b(Figura|Tabela)[ \t]+(\d+)[ \t]+(.{0,400}?)@@\s*(\d+)", re.S)
declarado = {}
for t in pages[:offset]:
    norm = LEADER.sub("@@", t)
    for m in ENTRY.finditer(norm):
        declarado[f"{m.group(1)} {m.group(2)}"] = int(m.group(4))

print(f"paginas no PDF: {len(pages)}   corpo comeca no indice {offset}\n")
ok = True
for key in sorted(real, key=lambda k: (k.split()[0], int(k.split()[1]))):
    d, v = declarado.get(key), real[key]
    if d != v:
        ok = False
    print(f"  {'OK  ' if d == v else 'ERRO'}  {key:10s} lista: p.{d}   real: p.{v}")

falta = set(declarado) - set(real)
if falta:
    ok = False
    print("\n  declaradas mas nao localizadas:", sorted(falta))

print("\nRESULTADO:", "todas as paginas conferem" if ok else ">>> HA DIVERGENCIA <<<")
sys.exit(0 if ok else 1)
