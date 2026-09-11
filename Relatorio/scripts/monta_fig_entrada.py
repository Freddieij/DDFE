from PIL import Image, ImageDraw, ImageFont
import os

from pathlib import Path
BASE = Path(__file__).resolve().parents[2] / "Figuras"

def load_font(size, bold=False):
    for name in (("seguisb.ttf", "segoeui.ttf") if bold else ("segoeui.ttf",)):
        p = os.path.join(r"C:\Windows\Fonts", name)
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()

a = Image.open(os.path.join(BASE, "Figura2a.png")).convert("RGB")
b = Image.open(os.path.join(BASE, "Figura2b.png")).convert("RGB")

# Marca as tres linhas do PROETA1 no painel (b), antes de qualquer escala.
# 16 linhas de dados distribuidas na altura da imagem.
d = ImageDraw.Draw(b)
n_rows = 16
row_h = b.height / n_rows
top = 1
bottom = row_h * 3 - 1
d.rectangle([1, top, b.width - 2, bottom], outline=(200, 16, 46), width=3)

# Normaliza as duas capturas para a mesma altura.
H = max(a.height, b.height)
def scale_to_h(im, h):
    w = round(im.width * h / im.height)
    return im.resize((w, h), Image.LANCZOS)
a = scale_to_h(a, H)
b = scale_to_h(b, H)

GAP, PAD, LABEL_H = 34, 10, 40
f_lab = load_font(21, bold=True)
f_sub = load_font(19)

W = PAD + a.width + GAP + b.width + PAD
out = Image.new("RGB", (W, LABEL_H + H + PAD), "white")
dr = ImageDraw.Draw(out)

ax, bx = PAD, PAD + a.width + GAP
dr.text((ax, 8), "(a) aba Fuels", font=f_lab, fill=(17, 17, 17))
w_a = dr.textlength("(a) aba Fuels", font=f_lab)
dr.text((ax + w_a + 10, 10), "— fuel, stage, color", font=f_sub, fill=(85, 85, 85))
dr.text((bx, 8), "(b) aba Techs", font=f_lab, fill=(17, 17, 17))
w_b = dr.textlength("(b) aba Techs", font=f_lab)
dr.text((bx + w_b + 10, 10), "— tech, fuel_in, fuel_out", font=f_sub, fill=(85, 85, 85))

out.paste(a, (ax, LABEL_H))
out.paste(b, (bx, LABEL_H))
dr.rectangle([ax, LABEL_H, ax + a.width - 1, LABEL_H + H - 1], outline=(185, 192, 203))
dr.rectangle([bx, LABEL_H, bx + b.width - 1, LABEL_H + H - 1], outline=(185, 192, 203))

dest = os.path.join(BASE, "fig-entrada-excel.png")
out.save(dest, optimize=True)
print(f"{dest}  {out.size[0]}x{out.size[1]}  ratio={out.size[0]/out.size[1]:.2f}")
