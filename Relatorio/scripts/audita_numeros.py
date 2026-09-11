import json, openpyxl, os
from collections import Counter, defaultdict

from pathlib import Path
RAIZ = Path(__file__).resolve().parents[2]
wb = openpyxl.load_workbook(os.path.join(RAIZ, "RES_Dados_Siglas.xlsx"))

fuels = [r for r in list(wb["Fuels"].iter_rows(values_only=True))[1:] if r[0]]
techrows = [r for r in list(wb["Techs"].iter_rows(values_only=True))[1:] if any(r[:3])]

stage = {str(r[0]).strip(): int(r[1]) for r in fuels}
cor = {str(r[0]).strip(): str(r[2]).strip() for r in fuels}

print("=== DADOS ===")
print("combustiveis:", len(fuels), "| estagios:", sorted(set(stage.values())))
print("por estagio:", dict(sorted(Counter(stage.values()).items())))
print("linhas na aba Techs:", len(techrows))

porTech = defaultdict(list)
for r in techrows:
    porTech[str(r[0]).strip() if r[0] else None].append(
        ((str(r[1]).strip() if r[1] else None), (str(r[2]).strip() if r[2] else None)))
print("tecnologias distintas:", len(porTech))

fonte = [t for t, rs in porTech.items() if all(i is None for i, o in rs) and any(o for i, o in rs)]
print("tecnologias-fonte (NENHUMA entrada em nenhuma linha):", len(fonte))
print("  [contagem por LINHA, como estava antes:",
      sum(1 for r in techrows if r[0] and not r[1] and r[2]), "]")

multi_out = [t for t, rs in porTech.items() if len({o for i, o in rs if o}) > 1]
multi_in = [t for t, rs in porTech.items() if len({i for i, o in rs if i}) > 1]
print("tecnologias com multiplas SAIDAS:", len(multi_out), multi_out)
print("tecnologias com multiplas ENTRADAS:", len(multi_in), multi_in)
print("tecnologias com mais de uma linha:",
      len([t for t, rs in porTech.items() if len(rs) > 1]))

bf = [(t, i, o) for t, rs in porTech.items() for i, o in rs
      if i in stage and o in stage and stage[i] >= stage[o]]
print("fluxos reversos:", len(bf), [b[0] for b in bf])

print("cores distintas no cadastro:", len(set(cor.values())))
print("cores dos primarios:", {f: c for f, c in cor.items() if stage[f] == 1})
print("fuels stage 5 (demanda):", sum(1 for f in stage if stage[f] == 5))
print("nos totais:", len(fuels), "+", len(porTech), "=", len(fuels) + len(porTech))

print("\n=== VEGA ===")
spec = json.load(open(os.path.join(RAIZ, "Deneb", "RES_FlowDiagram.json"), encoding="utf-8"))
data = spec.get("data", [])
derivados = [d for d in data if d.get("source")]
print("entradas em data:", len(data), "| derivadas de outra:", len(derivados))
print("  raiz:", [d["name"] for d in data if not d.get("source")])

def marcas(ms):
    out = []
    for m in ms:
        out.append(m.get("name"))
        out += marcas(m.get("marks", []))
    return out
todas = marcas(spec.get("marks", []))
print("marcas:", len(todas))

sinais = spec.get("signals", [])
reativos = [s["name"] for s in sinais if s.get("on")]
print("sinais totais:", len(sinais), "| reativos (com 'on'):", len(reativos))

import re
txt = json.dumps(spec)
print("strokeWidth 45 (hitbox):", txt.count('"strokeWidth": 45'), "ocorrencias")
print("strokeOpacity 0.001:", txt.count('"strokeOpacity": 0.001'))
print("strokeWidth encontrados:", sorted(set(re.findall(r'"strokeWidth":\s*([0-9.]+)', txt)), key=float))

print("\n=== CODIGO ===")
import glob
pq = glob.glob(os.path.join(RAIZ, "PowerQuery", "*.pq"))
tot = sum(sum(1 for _ in open(f, encoding="utf-8")) for f in pq)
print("arquivos .pq:", len(pq), "| linhas M:", tot)
vg = sum(1 for _ in open(os.path.join(RAIZ, "Deneb", "RES_FlowDiagram.json"), encoding="utf-8"))
print("linhas do JSON Vega:", vg)
