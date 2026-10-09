"""Gera a apresentação do XVI Seminário de Iniciação à Inovação (PIBITI 2025-2026).

Parte do template oficial da AGIR (Template_XVI_Seminario.pptx), preserva capa, cores,
fontes e layouts, e acrescenta os slides de conteúdo com as figuras do repositório.

Uso:  python Apresentacao/gera_apresentacao.py
Saída: Apresentacao/Apresentacao_XVI_Seminario_PIBITI.pptx
"""
import copy
from pathlib import Path

from PIL import Image, ImageDraw
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.dml import MSO_LINE
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Inches, Pt

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
FIG = RAIZ / "Figuras"
TMP = AQUI / "_assets"
TEMPLATE = AQUI / "Template_XVI_Seminario.pptx"
SAIDA = AQUI / "Apresentacao_XVI_Seminario_PIBITI.pptx"

TITULO_PROJETO = ("Computação Paralela Aplicada à Simulação Estocástica de Redes "
                  "Elétricas com Recursos Energéticos Distribuídos")
BOLSISTA = "Frederico José Poli Antunes"
ORIENTADOR = "Prof. Tiago Pires Abud"
REPO = "github.com/Freddieij/Power_BI_Borba"

# Paleta derivada do template: o azul da capa domina; cinza-claro é o lt2 do tema.
AZUL = RGBColor(0x0B, 0x53, 0x94)
AZUL_CLARO = RGBColor(0xCF, 0xE2, 0xF3)
TINTA = RGBColor(0xEA, 0xF1, 0xF8)
CINZA_FUNDO = RGBColor(0xF3, 0xF3, 0xF3)
CINZA_TXT = RGBColor(0x59, 0x59, 0x59)
ESCURO = RGBColor(0x1F, 0x1F, 0x1F)
BRANCO = RGBColor(0xFF, 0xFF, 0xFF)
MOLDURA = RGBColor(0xD9, 0xD9, 0xD9)
SETA = RGBColor(0x9D, 0xB4, 0xD3)
OK = RGBColor(0x2E, 0x7D, 0x32)
OK_CLARO = RGBColor(0xA5, 0xD6, 0xA7)
NAO = RGBColor(0xB0, 0x3A, 0x2E)
# Cores do esquema dos nós fantasmas (as mesmas da figura do relatório)
RAIA_FUNDO = RGBColor(0xEA, 0xF2, 0xFB)
RAIA_BORDA = RGBColor(0xB9, 0xD2, 0xEC)
RAIA_TXT = RGBColor(0x3A, 0x6E, 0xA5)
CAIXA_TXT = RGBColor(0x1D, 0x3F, 0x5E)
LARANJA_FUNDO = RGBColor(0xFC, 0xED, 0xE4)
LARANJA_BORDA = RGBColor(0xF0, 0xC8, 0xAE)
LARANJA = RGBColor(0xB5, 0x54, 0x1E)
VERMELHO = RGBColor(0xC8, 0x10, 0x2E)
VERDE = RGBColor(0x1F, 0x7A, 0x3A)
FANTASMA_FUNDO = RGBColor(0xF2, 0xF2, 0xF2)
FANTASMA_BORDA = RGBColor(0x8C, 0x8C, 0x8C)
# Cores dos combustíveis no diagrama (planilha RES_Dados_Siglas.xlsx)
COR_GAS = RGBColor(0xD9, 0x5F, 0x02)
COR_ELETRICIDADE = RGBColor(0x75, 0x70, 0xB3)

FONTE = "Calibri"  # fonte dos layouts de conteúdo do template
X0, LARG = 1.0, 11.33  # coluna de conteúdo alinhada ao texto do título


# ----------------------------------------------------------------------------- imagens
# Recorte da Figura 4: a linha de retorno atravessa a figura inteira, e o trecho do meio
# só tem linhas horizontais. Suprimi-lo (com marca de corte) deixa o texto ~3x maior.
F4_ESQ, F4_DIR, F4_Y = (0, 440), (1025, 1176), (318, 425)
F4_VAO = 14
F4_X_TERMICAS, F4_X_ELETRICIDADE, F4_X_GAS = 152, 359, 1047
F4_ESCALA = 3


def _x_fig4(x_original):
    """Posição horizontal, na imagem montada, de uma coluna da Figura 4 original."""
    if x_original <= F4_ESQ[1]:
        return x_original - F4_ESQ[0]
    return (F4_ESQ[1] - F4_ESQ[0]) + F4_VAO + (x_original - F4_DIR[0])


def prepara_imagens():
    TMP.mkdir(exist_ok=True)
    # cadeias.png tem margens brancas largas: recorta ao conteúdo.
    img = Image.open(RAIZ / "cadeias.png").convert("RGB")
    cinza = img.convert("L").point(lambda v: 255 if v < 245 else 0)
    x0, y0, x1, y1 = cinza.getbbox()
    pad = 12
    img.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)).save(TMP / "cadeias_recorte.png")

    f4 = Image.open(FIG / "Figura4.png").convert("RGB")
    esq = f4.crop((F4_ESQ[0], F4_Y[0], F4_ESQ[1], F4_Y[1]))
    dir_ = f4.crop((F4_DIR[0], F4_Y[0], F4_DIR[1], F4_Y[1]))
    alt = F4_Y[1] - F4_Y[0]
    montada = Image.new("RGB", (esq.width + F4_VAO + dir_.width, alt), "white")
    montada.paste(esq, (0, 0))
    montada.paste(dir_, (esq.width + F4_VAO, 0))
    montada = montada.resize((montada.width * F4_ESCALA, alt * F4_ESCALA), Image.LANCZOS)
    # marca de corte "//" no vão, desenhada já na escala final para sair nítida
    d = ImageDraw.Draw(montada)
    x_vao = esq.width * F4_ESCALA
    alt_f = alt * F4_ESCALA
    for dx in (8, 24):
        d.line([(x_vao + dx - 6, alt_f - 40), (x_vao + dx + 10, 40)], fill=(140, 140, 140), width=5)
    montada.save(TMP / "retorno_zoom.png")

    # Figura 7: detalhe com nomes legíveis (combustíveis primários e primeiras tecnologias).
    f7 = Image.open(FIG / "Figura7.png").convert("RGB")
    f7 = f7.crop((0, 20, 560, 470))
    f7.resize((f7.width * 2, f7.height * 2), Image.LANCZOS).save(TMP / "panorama_zoom.png")


def proporcao(caminho):
    w, h = Image.open(caminho).size
    return w / h


# ----------------------------------------------------------------------------- texto
def _run(par, texto, tam, cor, negrito=False, italico=False, link=None):
    r = par.add_run()
    r.text = texto
    f = r.font
    f.name, f.size, f.bold, f.italic = FONTE, Pt(tam), negrito, italico
    f.color.rgb = cor
    if link:
        r.hyperlink.address = link
    return r


def _marcador(par, char="•", cor=AZUL, recuo=0.22):
    pPr = par._p.get_or_add_pPr()
    pPr.set("marL", str(int(Inches(recuo))))
    pPr.set("indent", str(-int(Inches(recuo))))
    for tag in ("a:buClr", "a:buFont", "a:buChar", "a:buNone"):
        for e in pPr.findall(qn(tag)):
            pPr.remove(e)
    buClr = pPr.makeelement(qn("a:buClr"), {})
    clr = buClr.makeelement(qn("a:srgbClr"), {"val": str(cor)})
    buClr.append(clr)
    pPr.append(buClr)
    # Arial não tem ✓/✗; em marcador o PowerPoint não faz substituição de fonte.
    fonte_marca = "Arial" if char == "•" else "Segoe UI Symbol"
    pPr.append(pPr.makeelement(qn("a:buFont"), {"typeface": fonte_marca}))
    pPr.append(pPr.makeelement(qn("a:buChar"), {"char": char}))


def texto(slide, x, y, w, h, paragrafos, tam=16, cor=ESCURO, alinhar=PP_ALIGN.LEFT,
          ancora=MSO_ANCHOR.TOP, margem=0.0, nome=None):
    """paragrafos: lista de parágrafos; cada um é str, lista de runs, ou dict com
    runs/tam/cor/negrito/italico/alinhar/antes/depois/marcador. Run = str ou (str, dict),
    e o dict do run aceita também "link"."""
    caixa = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    if nome:
        caixa.name = nome
    preenche(caixa.text_frame, paragrafos, tam, cor, alinhar, ancora, margem)
    return caixa


def preenche(tf, paragrafos, tam=16, cor=ESCURO, alinhar=PP_ALIGN.LEFT,
             ancora=MSO_ANCHOR.TOP, margem=0.0):
    tf.word_wrap = True
    tf.vertical_anchor = ancora
    m = Inches(margem)
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = m
    for i, p in enumerate(paragrafos):
        if not isinstance(p, dict):
            p = {"runs": p}
        runs = p["runs"] if isinstance(p["runs"], list) else [p["runs"]]
        par = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        par.alignment = p.get("alinhar", alinhar)
        par.space_before = Pt(p.get("antes", 0))
        par.space_after = Pt(p.get("depois", 0))
        par.line_spacing = p.get("entrelinha", 1.0)
        if p.get("marcador"):
            _marcador(par, **({} if p["marcador"] is True else p["marcador"]))
        for run in runs:
            t, o = (run, {}) if isinstance(run, str) else run
            _run(par, t, o.get("tam", p.get("tam", tam)), o.get("cor", p.get("cor", cor)),
                 o.get("negrito", p.get("negrito", False)),
                 o.get("italico", p.get("italico", False)), o.get("link"))


def _sem_estilo(shape):
    # Sem <p:style>: o estilo padrão herda a sombra do tema, que o Google Slides e o
    # LibreOffice desenham mesmo com <a:effectLst/> vazio.
    estilo = shape._element.find(qn("p:style"))
    if estilo is not None:
        shape._element.remove(estilo)


def caixa(slide, x, y, w, h, fundo=None, borda=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE,
          raio=0.06, nome=None, espessura=0.75, tracejado=False):
    s = slide.shapes.add_shape(forma, Inches(x), Inches(y), Inches(w), Inches(h))
    if forma == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = raio
    if fundo is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fundo
    if borda is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = borda
        s.line.width = Pt(espessura)
        if tracejado:
            s.line.dash_style = MSO_LINE.DASH
    _sem_estilo(s)
    if nome:
        s.name = nome
    return s


def linha(slide, x1, y1, x2, y2, cor, espessura=2.5, seta_fim=False):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1),
                                   Inches(x2), Inches(y2))
    c.line.color.rgb = cor
    c.line.width = Pt(espessura)
    if seta_fim:
        ln = c.line._get_or_add_ln()
        ln.append(ln.makeelement(qn("a:tailEnd"), {"type": "triangle", "w": "med", "len": "med"}))
    _sem_estilo(c)
    return c


def figura(slide, caminho, x, y, w=None, h=None, moldura=True, nome=None):
    r = proporcao(caminho)
    if w is None:
        w = h * r
    if h is None:
        h = w / r
    pic = slide.shapes.add_picture(str(caminho), Inches(x), Inches(y), Inches(w), Inches(h))
    if moldura:
        pic.line.color.rgb = MOLDURA
        pic.line.width = Pt(0.75)
    if nome:
        pic.name = nome
    return pic, w, h


def numero_slide(slide):
    """Copia para o slide o campo de número de página que o layout do template já define."""
    for ph in slide.slide_layout.placeholders:
        if ph.placeholder_format.type is not None and "SLIDE_NUMBER" in str(ph.placeholder_format.type):
            slide.shapes._spTree.append(copy.deepcopy(ph._element))
            return
    raise RuntimeError("Layout sem campo de número de slide")


def novo_slide(prs, secao, titulo, notas):
    s = prs.slides.add_slide(prs.slide_layouts[5])  # TITLE_ONLY
    t = s.shapes.title
    t.text_frame.text = titulo
    for r in t.text_frame.paragraphs[0].runs:
        r.font.size = Pt(32)
        r.font.bold = True
        r.font.color.rgb = AZUL
    tag = texto(s, X0, 0.42, 6, 0.3, [[(secao.upper(), {"negrito": True})]], tam=12,
                cor=CINZA_TXT, nome="Secao")
    tag.text_frame.paragraphs[0].runs[0]._r.get_or_add_rPr().set("spc", "200")
    numero_slide(s)
    s.notes_slide.notes_text_frame.text = notas
    return s


def seta(slide, x, y, w, h, cor=SETA):
    return caixa(slide, x, y, w, h, fundo=cor, forma=MSO_SHAPE.RIGHT_ARROW)


# ----------------------------------------------------------------------------- slides
def capa(prs):
    s = prs.slides[0]
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        runs = [r for p in sh.text_frame.paragraphs for r in p.runs]
        txt = sh.text_frame.text
        if txt.startswith("Nome do projeto"):
            runs[0].text = TITULO_PROJETO
            runs[0].font.size = Pt(32)
            runs[0].font.bold = True
            # remove o parágrafo vazio que sobra do template
            ps = sh.text_frame.paragraphs
            for p in ps[1:]:
                p._p.getparent().remove(p._p)
        elif txt.startswith("Bolsista"):
            runs[0].text = f"Bolsista: {BOLSISTA}"
            runs[1].text = f"Orientador: {ORIENTADOR}"
    s.notes_slide.notes_text_frame.text = (
        "[~20 s] Bom dia. Sou o Frederico, bolsista PIBITI sob orientação do Prof. Tiago Abud. "
        "O título é o da proposta original; vou explicar em seguida por que o enfoque mudou.")


def contexto(prs):
    s = novo_slide(prs, "Introdução", "Contexto: da proposta original ao P&D", (
        "[~50 s] A proposta submetida era aplicar computação paralela à simulação estocástica de "
        "redes elétricas com recursos energéticos distribuídos, usando OpenDSS e Python. "
        "Ao longo do ano houve a necessidade de mudar o enfoque: atuei em apoio ao Prof. Bruno "
        "Borba no projeto de Pesquisa e Desenvolvimento 'Impactos do Crescimento da Frota de "
        "Veículos Elétricos no Sistema Eletro-Energético e Avaliação do Ciclo de Vida em "
        "Comparação com Veículos à Combustão', por causa da alta demanda de trabalho desse "
        "projeto. O tema continua ligado à proposta: planejamento energético do sistema "
        "elétrico. No P&D, o planejamento é feito com o OSeMOSYS, uma ferramenta de "
        "planejamento energético, e foi dali que surgiu o problema que este trabalho resolve."))
    y, h = 2.05, 3.5
    c1 = caixa(s, X0, y, 4.55, h, fundo=CINZA_FUNDO, nome="Proposta")
    preenche(c1.text_frame, [
        {"runs": "PROPOSTA SUBMETIDA (PIBITI)", "tam": 12, "negrito": True, "cor": CINZA_TXT},
        {"runs": "Computação paralela aplicada à simulação estocástica de redes elétricas "
                 "com recursos energéticos distribuídos", "tam": 20, "antes": 10},
        {"runs": "OpenDSS + Python, para reduzir o tempo de simulação", "tam": 14,
         "cor": CINZA_TXT, "antes": 12},
    ], margem=0.3, ancora=MSO_ANCHOR.MIDDLE)
    seta(s, 5.8, y + h / 2 - 0.35, 1.1, 0.7)
    texto(s, 5.55, y + h / 2 + 0.45, 1.6, 0.6, ["mudança de enfoque"], tam=12, cor=CINZA_TXT,
          alinhar=PP_ALIGN.CENTER)
    c2 = caixa(s, 7.1, y, X0 + LARG - 7.1, h, fundo=AZUL, nome="PeD")
    preenche(c2.text_frame, [
        {"runs": "PROJETO DE PESQUISA E DESENVOLVIMENTO (P&D)", "tam": 12, "negrito": True,
         "cor": AZUL_CLARO},
        {"runs": "“Impactos do Crescimento da Frota de Veículos Elétricos no Sistema "
                 "Eletro-Energético e Avaliação do Ciclo de Vida em Comparação com Veículos "
                 "à Combustão”", "tam": 16, "italico": True, "cor": BRANCO, "antes": 10},
        {"runs": "Planejamento energético com a ferramenta OSeMOSYS. Atuação junto ao "
                 "Prof. Bruno Borba.", "tam": 14, "cor": AZUL_CLARO, "antes": 12},
    ], margem=0.3, ancora=MSO_ANCHOR.MIDDLE)
    b = caixa(s, X0, 5.85, LARG, 0.95, fundo=TINTA, nome="Motivo")
    preenche(b.text_frame, [[("Por quê: ", {"negrito": True, "cor": AZUL}),
                             "alta demanda de trabalho do P&D, em tema ligado à proposta "
                             "original. Este trabalho automatiza um instrumento do planejamento "
                             "energético: o diagrama de fluxo de energia."]],
             tam=16, margem=0.25, ancora=MSO_ANCHOR.MIDDLE)


def res(prs):
    s = novo_slide(prs, "Introdução", "Diagrama de Fluxo de Energia de Referência", (
        "[~50 s] No OSeMOSYS, o sistema energético é descrito como uma rede: combustíveis, "
        "organizados por estágio da cadeia energética, ligados por tecnologias de extração, "
        "conversão, transporte e uso final. O desenho dessa rede é o Diagrama de Fluxo de "
        "Energia de Referência, a especificação visual do modelo. À esquerda está o diagrama "
        "de referência do projeto, desenhado à mão. Um diagrama realista tem cerca de 170 nós e "
        "mais de 100 arestas e leva dias para desenhar. O problema maior é a manutenção: "
        "qualquer alteração no modelo invalida o desenho, que congela numa versão antiga e "
        "deixa de documentar o modelo."))
    pic, w, h = figura(s, TMP / "cadeias_recorte.png", X0, 1.95, h=4.6, nome="Diagrama manual")
    texto(s, X0, 1.95 + h + 0.06, w, 0.3, ["Diagrama de referência do projeto, desenhado à mão"],
          tam=11, cor=CINZA_TXT, alinhar=PP_ALIGN.CENTER)
    xd = X0 + w + 0.5
    wd = X0 + LARG - xd
    texto(s, xd, 1.95, wd, 1.9, [
        {"runs": "Grafo dirigido que é a especificação visual de um modelo OSeMOSYS",
         "tam": 18, "negrito": True, "depois": 8},
        {"runs": "Combustíveis (linhas verticais), ordenados por estágio: do recurso primário "
                 "à demanda", "tam": 15, "marcador": True, "depois": 4},
        {"runs": "Tecnologias (caixas) consomem e produzem combustíveis", "tam": 15,
         "marcador": True},
    ])
    stats = [("~170", "nós"), ("100+", "arestas"), ("dias", "de desenho à mão")]
    ws = (wd - 0.4) / 3
    for i, (n, rot) in enumerate(stats):
        c = caixa(s, xd + i * (ws + 0.2), 4.0, ws, 1.25, fundo=CINZA_FUNDO, nome=f"Stat {rot}")
        preenche(c.text_frame, [{"runs": n, "tam": 32, "negrito": True, "cor": AZUL},
                                {"runs": rot, "tam": 13, "cor": CINZA_TXT}],
                 alinhar=PP_ALIGN.CENTER, ancora=MSO_ANCHOR.MIDDLE, margem=0.05)
    p = caixa(s, xd, 5.5, wd, 1.05, fundo=TINTA, nome="Problema")
    preenche(p.text_frame, [[("Problema: ", {"negrito": True, "cor": NAO}),
                             "cada alteração no modelo invalida o desenho, e o diagrama "
                             "deixa de corresponder ao modelo."]],
             tam=15, margem=0.2, ancora=MSO_ANCHOR.MIDDLE)


def lacuna(prs):
    s = novo_slide(prs, "Introdução", "Estado da arte e lacuna", (
        "[~50 s] Gerar o diagrama automaticamente não é novidade. O otoole, ferramenta oficial do "
        "OSeMOSYS, faz isso com o Graphviz, mas a coluna de cada nó é inferida pela topologia, "
        "e não pelo estágio que o modelador declarou; os combustíveis viram pontos sem rótulo; "
        "e a saída é uma imagem estática. Os diagramas de Sankey do Power BI codificam volume, "
        "derivam o eixo do grafo e não tratam as conexões de retorno. A lacuna é gerar um "
        "diagrama que respeite o estágio declarado, com combustíveis rotulados, conexões de "
        "retorno desenhadas e interatividade, dentro do Power BI. Na revisão feita, não "
        "encontramos implementação equivalente."))
    cartoes = [
        ("otoole viz res", "ferramenta oficial do OSeMOSYS", False, [
            (True, "Gera o diagrama automaticamente"),
            (False, "Coluna inferida pela topologia, não pelo estágio"),
            (False, "Combustíveis viram pontos sem rótulo"),
            (False, "Saída é imagem estática")]),
        ("Sankey e visuais de rede", "ferramentas como o Power BI", False, [
            (True, "Já dentro do Power BI"),
            (False, "Eixo derivado do grafo, não do estágio"),
            (False, "Espessura codifica volume, não topologia"),
            (False, "Conexões de retorno ficam ilegíveis")]),
        ("Este trabalho", "Power BI + Power Query + Deneb", True, [
            (True, "Coluna imposta pelo estágio declarado"),
            (True, "Combustíveis como eixos rotulados"),
            (True, "Conexões de retorno desenhadas"),
            (True, "Interativo, dentro do Power BI")]),
    ]
    wc, gap = 3.6, (LARG - 3 * 3.6) / 2
    for i, (tit, sub, destaque, itens) in enumerate(cartoes):
        x = X0 + i * (wc + gap)
        c = caixa(s, x, 2.0, wc, 3.75, fundo=AZUL if destaque else CINZA_FUNDO, nome=tit)
        ct, cs = (BRANCO, AZUL_CLARO) if destaque else (ESCURO, CINZA_TXT)
        pars = [{"runs": tit, "tam": 20, "negrito": True, "cor": ct},
                {"runs": sub, "tam": 13, "cor": cs, "depois": 10}]
        for ok, t in itens:
            marca = {"char": "✓" if ok else "✗", "recuo": 0.28,
                     "cor": (OK_CLARO if destaque else OK) if ok else NAO}
            pars.append({"runs": t, "tam": 15, "cor": ct, "antes": 8, "marcador": marca})
        preenche(c.text_frame, pars, margem=0.25)
    texto(s, X0, 6.0, LARG, 0.35,
          ["Na revisão realizada, não foi identificada implementação equivalente no Power BI "
           "ou em ferramenta similar."], tam=13, cor=CINZA_TXT, alinhar=PP_ALIGN.CENTER)


def objetivos(prs):
    s = novo_slide(prs, "Objetivos", "Objetivos", (
        "[~40 s] O objetivo geral foi desenvolver o Diagrama Dinâmico de Fluxo Energético, o "
        "DDFE: gerar automaticamente o diagrama de fluxo de energia completo e interativo a "
        "partir das duas tabelas que o modelador já mantém, dentro do Power BI. Os objetivos "
        "específicos foram: preservar a semântica do estágio; calcular a disposição sem "
        "sobreposição, incluindo as conexões de retorno; permitir isolar cadeias com um clique; "
        "e manter o código versionado e documentado, em repositório público."))
    g = caixa(s, X0, 1.95, LARG, 1.4, fundo=AZUL, nome="Objetivo geral")
    preenche(g.text_frame, [
        {"runs": "OBJETIVO GERAL", "tam": 12, "negrito": True, "cor": AZUL_CLARO},
        {"runs": [("Desenvolver o Diagrama Dinâmico de Fluxo Energético (DDFE): ",
                   {"negrito": True}),
                  "gerar automaticamente o diagrama de fluxo de energia completo e interativo "
                  "a partir de duas tabelas que o modelador já mantém, dentro do Power BI."],
         "tam": 18, "cor": BRANCO, "antes": 4},
    ], margem=0.25, ancora=MSO_ANCHOR.MIDDLE)
    texto(s, X0, 3.62, 6, 0.3, [[("OBJETIVOS ESPECÍFICOS", {"negrito": True})]], tam=12,
          cor=AZUL)
    itens = [
        ("Semântica preservada", ["Coluna de cada combustível definida pelo estágio energético "
                                  "declarado"]),
        ("Disposição automática", ["Posições e traçado sem sobreposição, inclusive conexões "
                                   "de retorno"]),
        ("Interatividade", ["Um clique isola a cadeia energética correspondente"]),
        ("Código auditável", ["Versionado como texto e documentado:",
                              [("github.com/Freddieij/",
                                {"link": "https://" + REPO, "cor": AZUL, "tam": 13})],
                              [("Power_BI_Borba",
                                {"link": "https://" + REPO, "cor": AZUL, "tam": 13})]]),
    ]
    wc = 2.6
    gap = (LARG - 4 * wc) / 3
    for i, (tit, desc) in enumerate(itens):
        x = X0 + i * (wc + gap)
        caixa(s, x, 4.0, wc, 2.6, fundo=CINZA_FUNDO, nome=f"Especifico {i + 1}")
        n = caixa(s, x + 0.25, 4.25, 0.6, 0.6, fundo=AZUL, forma=MSO_SHAPE.OVAL)
        preenche(n.text_frame, [{"runs": str(i + 1), "tam": 18, "negrito": True,
                                 "cor": BRANCO}], alinhar=PP_ALIGN.CENTER,
                 ancora=MSO_ANCHOR.MIDDLE)
        texto(s, x + 0.25, 5.05, wc - 0.4, 1.5,
              [{"runs": tit, "tam": 16, "negrito": True, "depois": 4}] +
              [{"runs": d, "tam": 14, "cor": CINZA_TXT, "antes": 2} for d in desc])


def arquitetura(prs):
    s = novo_slide(prs, "Resultados", "Solução: motor próprio em duas camadas", (
        "[~50 s] Em vez de usar um visual pronto, construímos um motor em duas camadas. A "
        "entrada são duas abas de Excel: Fuels, com combustível, estágio e cor; e Techs, com "
        "tecnologia, entrada e saída. A camada de cálculo, em Power Query, na linguagem M, tem "
        "nove consultas e 556 linhas e calcula todas as coordenadas. A camada de desenho, no "
        "Deneb, só desenha e cuida da interação. Separar as camadas permitiu desenvolver e "
        "depurar cada uma isoladamente. Nenhuma coordenada é desenhada à mão."))
    etapas = [
        (CINZA_FUNDO, ESCURO, "ENTRADA", "Excel", "2 abas: Fuels e Techs"),
        (TINTA, ESCURO, "CÁLCULO", "Power Query (M)", "9 consultas · 556 linhas\n"
                                                       "calcula as coordenadas"),
        (TINTA, ESCURO, "DESENHO", "Deneb (Vega)", "~1.030 linhas\n"
                                                   "desenha e interage"),
        (AZUL, BRANCO, "SAÍDA", "Diagrama interativo", "no Power BI"),
    ]
    wb, ga = 2.5, (LARG - 4 * 2.5) / 3
    for i, (fundo, cor, rot, tit, desc) in enumerate(etapas):
        x = X0 + i * (wb + ga)
        c = caixa(s, x, 1.95, wb, 1.6, fundo=fundo, nome=tit)
        preenche(c.text_frame, [
            {"runs": rot, "tam": 11, "negrito": True, "cor": AZUL_CLARO if cor == BRANCO else AZUL},
            {"runs": tit, "tam": 18, "negrito": True, "cor": cor, "antes": 2},
            {"runs": desc, "tam": 13, "cor": AZUL_CLARO if cor == BRANCO else CINZA_TXT,
             "antes": 2},
        ], margem=0.15, alinhar=PP_ALIGN.CENTER, ancora=MSO_ANCHOR.MIDDLE)
        if i < 3:
            seta(s, x + wb + (ga - 0.3) / 2, 1.95 + 0.6, 0.3, 0.4)
    pic, w, h = figura(s, FIG / "fig-entrada-excel.png", X0, 3.95, h=2.85, nome="Entrada Excel")
    xd = X0 + w + 0.4
    texto(s, xd, 3.95, X0 + LARG - xd, 2.85, [
        {"runs": "Entrada mínima: a planilha que o modelador já mantém", "tam": 17,
         "negrito": True, "depois": 8},
        {"runs": [("Fuels: ", {"negrito": True}), "combustível, estágio e cor"], "tam": 15,
         "marcador": True, "depois": 4},
        {"runs": [("Techs: ", {"negrito": True}), "tecnologia, entrada e saída"], "tam": 15,
         "marcador": True, "depois": 4},
        {"runs": "Várias saídas = várias linhas (em destaque: produção de etanol)", "tam": 15,
         "marcador": True, "depois": 4},
        {"runs": "Nenhuma coordenada desenhada à mão", "tam": 15, "marcador": True,
         "negrito": True, "cor": AZUL},
    ])


def fantasmas(prs):
    s = novo_slide(prs, "Resultados", "Raias elásticas com “nós fantasmas”", (
        "[~60 s] Este é o principal resultado técnico. Cada faixa horizontal do diagrama é uma "
        "raia. Uma conexão longa, por exemplo de um combustível do estágio 1 até uma demanda do "
        "estágio 5, passa por cima de caixas de outras tecnologias, como em (a). Desviar a "
        "linha exigiria busca em grade, inviável na linguagem M, que não tem estado mutável nem "
        "laços. A solução foi reservar espaço antes de desenhar: cada coluna ocupada que a "
        "conexão cruza recebe um nó fantasma, invisível, que conta na densidade da raia, como "
        "em (b). A raia passa a reservar mais linhas, e em (c) a conexão percorre uma linha "
        "livre. Tudo é feito com agrupamentos, somas acumuladas e junções de tabela. A troca é "
        "deliberada: o diagrama fica um pouco mais alto, mas o algoritmo é determinístico."))
    LX = 4.6                       # início das raias
    FIM = X0 + LARG                # fim das raias
    BW, BH = 1.15, 0.42            # caixa de tecnologia
    C1, C2, C3 = 5.95, 8.65, 10.35  # centro das colunas de T1, T2, T3
    XSETA = FIM - 0.2

    def tec(cx, cy, rot, borda=RAIA_TXT, cor=CAIXA_TXT):
        c = caixa(s, cx - BW / 2, cy - BH / 2, BW, BH, fundo=BRANCO, borda=borda, raio=0.12,
                  espessura=1.75, nome=rot)
        preenche(c.text_frame, [{"runs": rot, "tam": 15, "cor": cor}],
                 alinhar=PP_ALIGN.CENTER, ancora=MSO_ANCHOR.MIDDLE)

    def raia(y, h, rot, fundo=RAIA_FUNDO, borda=RAIA_BORDA, cor=RAIA_TXT, cy=None):
        caixa(s, LX, y, FIM - LX, h, fundo=fundo, borda=borda, forma=MSO_SHAPE.RECTANGLE,
              nome=rot)
        cy = cy if cy is not None else y + h / 2
        texto(s, LX + 0.08, cy - 0.15, 0.75, 0.3, [[(rot, {"negrito": True})]], tam=12,
              cor=cor, ancora=MSO_ANCHOR.MIDDLE)

    def legenda(y, tit, desc):
        texto(s, X0, y, LX - X0 - 0.3, 1.45, [
            {"runs": tit, "tam": 17, "negrito": True, "cor": AZUL},
            {"runs": desc, "tam": 14, "cor": CINZA_TXT, "antes": 3}])

    # (a) o problema
    cy = 2.35
    raia(2.0, 0.7, "raia A")
    # caixas atravessadas ficam com borda vermelha e a linha passa por cima delas
    tec(C1, cy, "T1")
    tec(C2, cy, "T2", borda=VERMELHO)
    tec(C3, cy, "T3", borda=VERMELHO)
    linha(s, C1 + BW / 2, cy, XSETA, cy, VERMELHO, seta_fim=True)
    legenda(2.0, "(a) O problema",
            "A conexão longa que sai da tecnologia T1 passa por cima de T2 e T3.")

    # (b) a reserva
    y1, y2 = 3.62, 4.2
    raia(3.1, 1.4, "raia A", cy=y1)
    for cx in (C2, C3):
        texto(s, cx - BW / 2 - 0.1, 3.13, BW + 0.2, 0.25, [[("nó fantasma", {"italico": True})]],
              tam=12, cor=FANTASMA_BORDA, alinhar=PP_ALIGN.CENTER)
        caixa(s, cx - BW / 2, y1 - BH / 2, BW, BH, fundo=FANTASMA_FUNDO, borda=FANTASMA_BORDA,
              raio=0.12, espessura=1.5, tracejado=True, nome="no fantasma")
        caixa(s, cx + BW / 2 + 0.06, y1 + 0.12, 0.16, 0.3, fundo=SETA, forma=MSO_SHAPE.DOWN_ARROW)
    linha(s, C1 + BW / 2, y1, XSETA, y1, VERDE, seta_fim=True)
    tec(C1, y1, "T1")
    tec(C2, y2, "T2")
    tec(C3, y2, "T3")
    legenda(3.1, "(b) A reserva",
            "Cada coluna cruzada recebe um “nó fantasma”: invisível, ele toma a linha da "
            "conexão e empurra T2 e T3 para baixo.")

    # (c) o resultado
    ya, yb = 5.05, 5.75
    raia(4.75, 0.6, "raia A")
    raia(5.45, 0.6, "raia B", fundo=LARANJA_FUNDO, borda=LARANJA_BORDA, cor=LARANJA)
    linha(s, C1 + BW / 2, ya, XSETA, ya, VERDE, seta_fim=True)
    tec(C1, ya, "T1")
    tec(C2, yb, "T2", borda=LARANJA, cor=LARANJA)
    tec(C3, yb, "T3", borda=LARANJA, cor=LARANJA)
    legenda(4.75, "(c) O resultado",
            "A conexão segue por uma linha livre; T2 e T3 passam para a raia seguinte.")

    texto(s, X0, 6.3, LARG, 0.5,
          [[("Por que funciona na linguagem M: ", {"negrito": True, "cor": AZUL}),
            "sem busca em grade nem estado mutável, apenas agrupamentos, somas acumuladas e "
            "junções de tabela."]], tam=14, cor=CINZA_TXT)


def retorno(prs):
    s = novo_slide(prs, "Resultados", "Conexões de retorno no diagrama", (
        "[~45 s] Um caso que os visuais prontos não tratam é a conexão de retorno. A "
        "termelétrica a gás natural usa gás processado, que está no estágio 3, para gerar "
        "eletricidade, que está no estágio 2. Isso não é erro do modelo: a energia segue o "
        "sentido normal, do gás para a eletricidade. Mas, como as colunas seguem o estágio, a "
        "entrada fica à direita da saída, e a linha precisa voltar para a esquerda, contornando "
        "as caixas. O cálculo detecta esses casos comparando os estágios de entrada e saída, "
        "sem o usuário declarar nada. No sistema de validação há quatro casos, todos desenhados "
        "automaticamente."))
    arq = TMP / "retorno_zoom.png"
    larg_px = Image.open(arq).width / F4_ESCALA
    esc = LARG / larg_px  # polegadas por pixel da figura original

    def xpos(x_original):
        return X0 + _x_fig4(x_original) * esc

    texto(s, xpos(F4_X_GAS) - 3.4, 1.9, 3.5, 0.35,
          [[("gás natural processado (estágio 3)  ↓", {"negrito": True})]],
          tam=13, cor=COR_GAS, alinhar=PP_ALIGN.RIGHT)
    pic, w, h = figura(s, arq, X0, 2.3, w=LARG, nome="Conexoes de retorno")
    yl = 2.3 + h + 0.05
    texto(s, xpos(F4_X_TERMICAS) - 1.4, yl, 2.8, 0.35,
          [[("termelétricas a gás natural", {"negrito": True})]], tam=13, cor=CAIXA_TXT,
          alinhar=PP_ALIGN.CENTER)
    texto(s, xpos(F4_X_ELETRICIDADE) - 1.4, yl, 2.8, 0.35,
          [[("↑  eletricidade (estágio 2)", {"negrito": True})]], tam=13, cor=COR_ELETRICIDADE,
          alinhar=PP_ALIGN.CENTER)

    cartoes = [
        ("O que acontece", "A termelétrica usa gás processado (estágio 3) para gerar "
                           "eletricidade (estágio 2).", False),
        ("Não é erro do modelo", "A energia segue o sentido normal. Como a entrada está num "
                                 "estágio posterior ao da saída, a linha volta para a esquerda.",
         False),
        ("Detecção automática", "4 casos no sistema, identificados pela comparação dos "
                                "estágios, sem declaração do usuário.", True),
    ]
    wc, gap = 3.6, (LARG - 3 * 3.6) / 2
    for i, (tit, desc, destaque) in enumerate(cartoes):
        c = caixa(s, X0 + i * (wc + gap), 4.95, wc, 1.85,
                  fundo=AZUL if destaque else CINZA_FUNDO, nome=tit)
        preenche(c.text_frame, [
            {"runs": tit, "tam": 17, "negrito": True, "cor": BRANCO if destaque else AZUL},
            {"runs": desc, "tam": 14, "cor": AZUL_CLARO if destaque else ESCURO, "antes": 4}],
            margem=0.22, ancora=MSO_ANCHOR.MIDDLE)


def interatividade(prs):
    s = novo_slide(prs, "Resultados", "Interatividade: um clique isola a cadeia", (
        "[~45 s] O diagrama deixou de ser imagem e virou interface. Sem nenhuma seleção, todas "
        "as cadeias aparecem iguais. Ao clicar em um combustível ou tecnologia, as demais "
        "cadeias ficam esmaecidas, mas continuam visíveis como contexto. À esquerda, cliquei na "
        "biomassa: biomassa e cana-de-açúcar compartilham a cor no cadastro, então o grupo "
        "inteiro é destacado, incluindo as demandas de biomassa, a usina a biomassa e a rota "
        "de etanol. A cor expressa a classe do vetor energético. À direita, cliquei no carvão, "
        "que tem cor exclusiva: só a cadeia do carvão fica em destaque. Cada linha tem 2 "
        "pixels, mas a área de clique invisível tem 45 pixels, o que torna o clique viável num "
        "diagrama denso."))
    paineis = [
        ("Figura6a.png", "Selecionando um grupo",
         "Biomassa e cana têm a mesma cor: o grupo todo é destacado"),
        ("Figura6b.png", "Selecionando uma cadeia",
         "O carvão tem cor exclusiva: só a sua cadeia é destacada"),
    ]
    wc = (LARG - 0.4) / 2
    hmax = 3.2
    for i, (arq, tit, desc) in enumerate(paineis):
        x = X0 + i * (wc + 0.4)
        texto(s, x, 1.95, wc, 0.35, [[(tit, {"negrito": True})]], tam=17, cor=AZUL)
        r = proporcao(FIG / arq)
        w, h = (wc, wc / r) if wc / r <= hmax else (hmax * r, hmax)
        figura(s, FIG / arq, x, 2.4, w=w, h=h, nome=tit)
        texto(s, x, 2.4 + hmax + 0.08, wc, 0.4, [desc], tam=14, cor=CINZA_TXT)
    b = caixa(s, X0, 6.15, LARG, 0.65, fundo=TINTA, nome="Esmaecimento")
    preenche(b.text_frame, ["Ao clicar em um combustível ou tecnologia, as demais cadeias ficam "
                            "esmaecidas, mas continuam visíveis como contexto."],
             tam=15, margem=0.25, ancora=MSO_ANCHOR.MIDDLE)


def validacao(prs):
    s = novo_slide(prs, "Resultados",
                   "Validação com a estrutura do sistema energético brasileiro", (
        "[~45 s] A ferramenta foi validada com a estrutura do sistema energético brasileiro: "
        "70 combustíveis em 5 estágios, 101 tecnologias e 106 ligações declaradas na planilha, "
        "incluindo 4 conexões de retorno. É a estrutura do sistema, ou seja, quais "
        "combustíveis e tecnologias existem e como se ligam, sem quantidades de energia. "
        "Também foi testada com bases de topologia aleatória, com casos difíceis, para "
        "confirmar que a disposição não depende deste sistema específico. A figura é só um "
        "detalhe: o diagrama inteiro tem milhares de pixels nos dois eixos, por isso zoom e "
        "destaque são essenciais. O ganho principal: o que levava dias à mão agora se atualiza "
        "em segundos, e o diagrama passa a acompanhar o modelo automaticamente."))
    pic, w, h = figura(s, TMP / "panorama_zoom.png", X0, 1.95, h=4.5, nome="Detalhe")
    texto(s, X0, 1.95 + h + 0.06, w, 0.3, ["Detalhe do diagrama gerado automaticamente"],
          tam=11, cor=CINZA_TXT, alinhar=PP_ALIGN.CENTER)
    xd = X0 + w + 0.4
    wd = X0 + LARG - xd
    stats = [("70", "combustíveis"), ("5", "estágios"), ("101", "tecnologias"),
             ("106", "ligações declaradas"), ("4", "conexões de retorno"),
             ("0", "coordenadas à mão")]
    g = 0.15
    wc, hc = (wd - 2 * g) / 3, 1.15
    for i, (n, rot) in enumerate(stats):
        x = xd + (i % 3) * (wc + g)
        y = 1.95 + (i // 3) * (hc + g)
        c = caixa(s, x, y, wc, hc, fundo=CINZA_FUNDO, nome=f"Stat {rot}")
        preenche(c.text_frame, [{"runs": n, "tam": 28, "negrito": True, "cor": AZUL},
                                {"runs": rot, "tam": 12, "cor": CINZA_TXT}],
                 alinhar=PP_ALIGN.CENTER, ancora=MSO_ANCHOR.MIDDLE, margem=0.04)
    texto(s, xd, 1.95 + 2 * (hc + g) + 0.05, wd, 0.75,
          ["Estrutura do sistema: quais combustíveis e tecnologias existem e como se ligam, "
           "sem quantidades de energia."], tam=13, cor=CINZA_TXT)
    yb = 5.3
    b = caixa(s, xd, yb, wd, 1.15, fundo=AZUL, nome="Ganho")
    preenche(b.text_frame, [
        {"runs": [("Antes: ", {"negrito": True}), "dias de desenho manual"], "tam": 15,
         "cor": AZUL_CLARO},
        {"runs": [("Agora: ", {"negrito": True}), "altera a planilha e atualiza em segundos"],
         "tam": 15, "cor": BRANCO, "antes": 6},
    ], margem=0.2, ancora=MSO_ANCHOR.MIDDLE)


def conclusoes(prs):
    s = novo_slide(prs, "Conclusões", "Conclusões", (
        "[~50 s] Para concluir: entregamos um gerador automático e interativo do diagrama de "
        "fluxo de energia, funcional e documentado. O ganho mais importante é a atualização "
        "automática: o diagrama acompanha o modelo sem redesenho. O algoritmo de nós fantasmas "
        "resolve a sobreposição só com transformações de tabela, e o método opera sobre a forma "
        "do grafo, então tem aplicação geral, para outros fluxos em camadas, como materiais e "
        "cadeias produtivas. Como trabalhos futuros: parametrizar a disposição, reativar a "
        "rastreabilidade de forma otimizada, dimensionar as linhas pelo volume de fluxo e usar "
        "o grafo para diagnosticar inconsistências no modelo. O código está público no GitHub. "
        "Obrigado."))
    itens = [
        ("Ferramenta entregue", "Gera o diagrama completo e interativo a partir de duas "
                                "tabelas, funcional e documentada"),
        ("Atualização automática do diagrama", "O diagrama acompanha o modelo: altera a "
                                               "planilha e atualiza"),
        ("Contribuição técnica", "“Nós fantasmas”: disposição sem sobreposição apenas com "
                                 "transformações de tabela"),
        ("Método de aplicação geral", "Opera sobre a forma do grafo: serve a outros fluxos, "
                                      "como materiais e cadeias produtivas"),
    ]
    wl = 6.9
    for i, (tit, desc) in enumerate(itens):
        y = 1.95 + i * 1.22
        n = caixa(s, X0, y + 0.1, 0.55, 0.55, fundo=AZUL, forma=MSO_SHAPE.OVAL)
        preenche(n.text_frame, [{"runs": "✓", "tam": 18, "negrito": True, "cor": BRANCO}],
                 alinhar=PP_ALIGN.CENTER, ancora=MSO_ANCHOR.MIDDLE)
        texto(s, X0 + 0.8, y, wl - 0.8, 1.1, [
            {"runs": tit, "tam": 18, "negrito": True},
            {"runs": desc, "tam": 15, "cor": CINZA_TXT, "antes": 2}])
    xd = X0 + wl + 0.35
    c = caixa(s, xd, 1.95, X0 + LARG - xd, 4.75, fundo=TINTA, nome="Trabalhos futuros")
    futuros = ["Parametrizar as constantes de disposição na interface",
               "Reativar a rastreabilidade com cálculo otimizado",
               "Espessura das linhas proporcional ao fluxo",
               "Diagnósticos automáticos de consistência do modelo"]
    preenche(c.text_frame,
             [{"runs": "Trabalhos futuros", "tam": 20, "negrito": True, "cor": AZUL,
               "depois": 6}] +
             [{"runs": f, "tam": 15, "marcador": True, "antes": 10} for f in futuros] +
             [{"runs": "Código-fonte", "tam": 13, "negrito": True, "cor": CINZA_TXT,
               "antes": 22},
              {"runs": [(REPO, {"link": "https://" + REPO})], "tam": 13, "cor": AZUL}],
             margem=0.3)


def encerramento(prs):
    """Duplica a capa (fundo azul e logos) para o slide final."""
    capa_sl = prs.slides[0]
    s = prs.slides.add_slide(capa_sl.slide_layout)
    for ph in list(s.placeholders):
        ph._element.getparent().remove(ph._element)
    # fundo
    bg = capa_sl._element.cSld.find(qn("p:bg"))
    if bg is not None:
        s._element.cSld.insert(0, copy.deepcopy(bg))
    # imagens: relaciona as mesmas partes de mídia
    mapa = {}
    for rid, rel in capa_sl.part.rels.items():
        if rel.reltype.endswith("/image"):
            mapa[rid] = s.part.relate_to(rel.target_part, rel.reltype)
    arvore = s.shapes._spTree
    for el in capa_sl.shapes._spTree.iterchildren():
        if el.tag in (qn("p:sp"), qn("p:pic"), qn("p:grpSp")):
            novo = copy.deepcopy(el)
            for blip in novo.iter(qn("a:blip")):
                antigo = blip.get(qn("r:embed"))
                blip.set(qn("r:embed"), mapa[antigo])
            arvore.append(novo)
    for sh in s.shapes:
        if not sh.has_text_frame:
            continue
        txt = sh.text_frame.text
        if txt.startswith("Computação Paralela"):
            r = sh.text_frame.paragraphs[0].runs[0]
            r.text = "Obrigado!"
            r.font.size = Pt(54)
        elif txt.startswith("Bolsista"):
            runs = [r for p in sh.text_frame.paragraphs for r in p.runs]
            runs[0].text = BOLSISTA
            runs[1].text = f"{REPO}  ·  Apoio: CNPq (PIBITI/PIBINOVA UFF 2025-2026)"
            # sem hyperlink: a cor de link do tema ficaria ilegível sobre o fundo azul
            runs[1].font.size = Pt(18)
    s.notes_slide.notes_text_frame.text = "[~10 s] Obrigado. Fico à disposição para perguntas."


def main():
    prepara_imagens()
    prs = Presentation(str(TEMPLATE))
    capa(prs)
    for f in (contexto, res, lacuna, objetivos, arquitetura, fantasmas, retorno,
              interatividade, validacao, conclusoes, encerramento):
        f(prs)
    prs.save(str(SAIDA))
    print(f"Gerado: {SAIDA} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
