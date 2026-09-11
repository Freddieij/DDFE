"""Mede o vao branco no pe de cada pagina, em cm."""
import glob, os, sys
from PIL import Image

from pathlib import Path
import sys
RAIZ = Path(__file__).resolve().parents[2]
# Renderize antes:  typst compile --root . --format png --ppi 72 \
#   Relatorio/relatorio.typ "Relatorio/_previa/p{0p}.png"
D = sys.argv[1] if len(sys.argv) > 1 else str(RAIZ / "Relatorio" / "_previa")
PPI = 72.0
A4_H_CM = 29.7
BOTTOM_MARGIN_CM = 2.0
# o numero de pagina fica no rodape; ignora a faixa inferior ao procurar conteudo
FOOTER_BAND_CM = 1.6

files = sorted(glob.glob(os.path.join(D, "p[0-9]*.png")))
print(f"{'pag':>4}  {'vao no pe (cm)':>15}")
print("-" * 24)
alerta = []
for f in files:
    im = Image.open(f).convert("L")
    w, h = im.size
    px_per_cm = h / A4_H_CM
    footer_px = int(FOOTER_BAND_CM * px_per_cm)
    limite = h - footer_px
    px = im.load()
    ultima = None
    for y in range(limite - 1, -1, -1):
        linha_tem_tinta = False
        for x in range(0, w, 2):
            if px[x, y] < 235:
                linha_tem_tinta = True
                break
        if linha_tem_tinta:
            ultima = y
            break
    if ultima is None:
        vao = A4_H_CM - BOTTOM_MARGIN_CM
    else:
        vao = (limite - ultima) / px_per_cm
    n = int(os.path.basename(f)[1:].split(".")[0])
    marca = ""
    if vao > 4.0:
        marca = "  <<< VAO GRANDE"
        alerta.append((n, round(vao, 1)))
    print(f"{n:>4}  {vao:>15.1f}{marca}")

print("\npaginas com vao > 4 cm:", alerta if alerta else "nenhuma")
sys.exit(1 if alerta else 0)
