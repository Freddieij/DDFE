"""Gera a apresentação do XVI Seminário de Iniciação à Inovação (PIBITI 2025-2026).

Parte do template oficial da AGIR (Template_XVI_Seminario.pptx), preserva capa, cores,
fontes e layouts, e acrescenta os slides de conteúdo com as figuras do repositório.

Uso:  python Apresentacao/gera_apresentacao.py
Saída: Apresentacao/Apresentacao_XVI_Seminario_PIBITI.pptx
"""
import copy
from pathlib import Path

import pymupdf
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
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

FONTE = "Calibri"  # fonte dos layouts de conteúdo do template
X0, LARG = 1.0, 11.33  # coluna de conteúdo alinhada ao texto do título


# ----------------------------------------------------------------------------- imagens
def prepara_imagens():
    TMP.mkdir(exist_ok=True)
    # cadeias.png tem margens brancas largas: recorta ao conteúdo.
    img = Image.open(RAIZ / "cadeias.png").convert("RGB")
    cinza = img.convert("L").point(lambda v: 255 if v < 245 else 0)
    x0, y0, x1, y1 = cinza.getbbox()
    pad = 12
    img.crop((x0 - pad, y0 - pad, x1 + pad, y1 + pad)).save(TMP / "cadeias_recorte.png")

    # Esquema dos nós fantasmas: recorta do PDF do relatório, onde o Typst embutiu as fontes.
    doc = pymupdf.open(RAIZ / "Relatorio" / "Relatorio_Final_PIBITI_2025-2026.pdf")
    for pagina in doc:
        legenda = pagina.search_for("Algoritmo de raias elásticas com nós")
        topo = pagina.search_for("(a) O problema")
        if legenda and topo:
            leg, t = legenda[0], topo[0]
            xs = [d["rect"].x1 for d in pagina.get_drawings()
                  if d["rect"].y0 > t.y0 - 10 and d["rect"].y1 < leg.y0]
            xs += [w[2] for w in pagina.get_text("words") if w[1] > t.y0 - 10 and w[3] < leg.y0]
            clip = pymupdf.Rect(t.x0 - 6, t.y0 - 6, max(xs) + 6, leg.y0 - 8)
            pagina.get_pixmap(matrix=pymupdf.Matrix(6, 6), clip=clip).save(TMP / "fantasmas.png")
            break
    else:
        raise RuntimeError("Figura dos nós fantasmas não encontrada no PDF do relatório")


def proporcao(caminho):
    w, h = Image.open(caminho).size
    return w / h


# ----------------------------------------------------------------------------- texto
def _run(par, texto, tam, cor, negrito=False, italico=False):
    r = par.add_run()
    r.text = texto
    f = r.font
    f.name, f.size, f.bold, f.italic = FONTE, Pt(tam), negrito, italico
    f.color.rgb = cor
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
    runs/tam/cor/negrito/italico/alinhar/antes/depois/marcador. Run = str ou (str, dict)."""
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
                 o.get("negrito", p.get("negrito", False)), o.get("italico", p.get("italico", False)))


def caixa(slide, x, y, w, h, fundo=None, borda=None, forma=MSO_SHAPE.ROUNDED_RECTANGLE,
          raio=0.06, nome=None):
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
        s.line.width = Pt(0.75)
    # Sem <p:style>: o estilo padrão herda a sombra do tema, que o Google Slides e o
    # LibreOffice desenham mesmo com <a:effectLst/> vazio.
    estilo = s._element.find(qn("p:style"))
    if estilo is not None:
        s._element.remove(estilo)
    if nome:
        s.name = nome
    return s


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
        "Borba no projeto de P&D 'Impactos do Crescimento da Frota de Veículos Elétricos no "
        "Sistema Eletro-Energético e Avaliação do Ciclo de Vida em Comparação com Veículos à "
        "Combustão', por causa da alta demanda de trabalho desse projeto. O tema continua ligado "
        "à proposta: planejamento energético do sistema elétrico, REDs e VEs. É comum que o "
        "bolsista faça um trabalho um pouco diferente do submetido. No P&D, o planejamento é "
        "feito com o OSeMOSYS, e foi dali que surgiu o problema que este trabalho resolve."))
    y, h = 2.05, 3.5
    c1 = caixa(s, X0, y, 4.55, h, fundo=CINZA_FUNDO, nome="Proposta")
    preenche(c1.text_frame, [
        {"runs": "PROPOSTA SUBMETIDA (PIBITI)", "tam": 12, "negrito": True, "cor": CINZA_TXT},
        {"runs": "Computação paralela aplicada à simulação estocástica de redes elétricas "
                 "com REDs", "tam": 20, "antes": 10},
        {"runs": "OpenDSS + Python, para reduzir o tempo de simulação", "tam": 14,
         "cor": CINZA_TXT, "antes": 12},
    ], margem=0.3, ancora=MSO_ANCHOR.MIDDLE)
    seta(s, 5.8, y + h / 2 - 0.35, 1.1, 0.7)
    texto(s, 5.55, y + h / 2 + 0.45, 1.6, 0.6, ["mudança de enfoque"], tam=12, cor=CINZA_TXT,
          alinhar=PP_ALIGN.CENTER)
    c2 = caixa(s, 7.1, y, X0 + LARG - 7.1, h, fundo=AZUL, nome="PeD")
    preenche(c2.text_frame, [
        {"runs": "PROJETO DE P&D (VEÍCULOS ELÉTRICOS)", "tam": 12, "negrito": True,
         "cor": AZUL_CLARO},
        {"runs": "“Impactos do Crescimento da Frota de Veículos Elétricos no Sistema "
                 "Eletro-Energético e Avaliação do Ciclo de Vida em Comparação com Veículos "
                 "à Combustão”", "tam": 16, "italico": True, "cor": BRANCO, "antes": 10},
        {"runs": "Planejamento energético do SEP, REDs e VEs, com modelagem no OSeMOSYS. "
                 "Atuação junto ao Prof. Bruno Borba.", "tam": 14, "cor": AZUL_CLARO,
         "antes": 12},
    ], margem=0.3, ancora=MSO_ANCHOR.MIDDLE)
    b = caixa(s, X0, 5.85, LARG, 0.95, fundo=TINTA, nome="Motivo")
    preenche(b.text_frame, [[("Por quê: ", {"negrito": True, "cor": AZUL}),
                             "alta demanda de trabalho do P&D, em tema ligado à proposta "
                             "original. Este trabalho automatiza um instrumento do planejamento: "
                             "o diagrama RES."]],
             tam=16, margem=0.25, ancora=MSO_ANCHOR.MIDDLE)


def res(prs):
    s = novo_slide(prs, "Introdução", "Diagrama de Fluxo de Energia de Referência", (
        "[~50 s] No OSeMOSYS, o sistema energético é descrito como uma rede: combustíveis, "
        "organizados por estágio da cadeia energética, ligados por tecnologias de extração, "
        "conversão, transporte e uso final. O desenho dessa rede é o RES, a especificação "
        "visual do modelo. À esquerda está o RES de referência do projeto, desenhado à mão. "
        "Um RES realista tem cerca de 170 nós e mais de 100 arestas e leva dias para desenhar. "
        "O problema maior é a manutenção: qualquer alteração no modelo invalida o desenho, que "
        "congela numa versão antiga e deixa de documentar o modelo."))
    pic, w, h = figura(s, TMP / "cadeias_recorte.png", X0, 1.95, h=4.6, nome="RES manual")
    texto(s, X0, 1.95 + h + 0.06, w, 0.3, ["RES de referência do projeto, desenhado à mão"],
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
        "[~50 s] Gerar o RES automaticamente não é novidade. O otoole, suíte oficial do "
        "OSeMOSYS, faz isso com o Graphviz, mas a coluna de cada nó é inferida pela topologia, "
        "e não pelo estágio que o modelador declarou; os combustíveis viram pontos sem rótulo; "
        "e a saída é uma imagem estática. Os visuais de Sankey do Power BI codificam volume, "
        "derivam o eixo do grafo e não tratam fluxos reversos. A lacuna é gerar um RES que "
        "respeite o estágio declarado, com combustíveis rotulados, fluxos reversos roteados e "
        "interatividade, dentro da plataforma de BI. Na revisão feita, não encontramos "
        "implementação equivalente nativa em plataforma de BI."))
    cartoes = [
        ("otoole viz res", "suíte oficial do OSeMOSYS", False, [
            (True, "Gera o RES automaticamente"),
            (False, "Coluna inferida pela topologia, não pelo estágio"),
            (False, "Combustíveis viram pontos sem rótulo"),
            (False, "Saída é imagem estática")]),
        ("Sankey e visuais de rede", "plataformas de BI", False, [
            (True, "Já dentro do Power BI"),
            (False, "Eixo derivado do grafo, não do estágio"),
            (False, "Espessura codifica volume, não topologia"),
            (False, "Fluxos reversos ficam ilegíveis")]),
        ("DDFE (este trabalho)", "Power BI + Power Query + Deneb", True, [
            (True, "Coluna imposta pelo estágio declarado"),
            (True, "Combustíveis como eixos rotulados"),
            (True, "Fluxos reversos roteados"),
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
          ["Na revisão realizada, não foi identificada implementação equivalente nativa em "
           "plataforma de BI."], tam=13, cor=CINZA_TXT, alinhar=PP_ALIGN.CENTER)


def objetivos(prs):
    s = novo_slide(prs, "Objetivos", "Objetivos", (
        "[~40 s] O objetivo geral foi desenvolver o Diagrama Dinâmico de Fluxo Energético, o "
        "DDFE: gerar automaticamente o RES completo e interativo a partir das duas tabelas que "
        "o modelador já mantém, dentro do Power BI. Os objetivos específicos foram: preservar a "
        "semântica do estágio; calcular o layout sem sobreposição, incluindo fluxos reversos; "
        "permitir isolar cadeias com um clique; e manter o código versionado e documentado."))
    g = caixa(s, X0, 1.95, LARG, 1.4, fundo=AZUL, nome="Objetivo geral")
    preenche(g.text_frame, [
        {"runs": "OBJETIVO GERAL", "tam": 12, "negrito": True, "cor": AZUL_CLARO},
        {"runs": [("Desenvolver o Diagrama Dinâmico de Fluxo Energético (DDFE): ",
                   {"negrito": True}),
                  "gerar automaticamente o RES completo e interativo a partir de duas tabelas "
                  "que o modelador já mantém, dentro do Power BI."],
         "tam": 18, "cor": BRANCO, "antes": 4},
    ], margem=0.25, ancora=MSO_ANCHOR.MIDDLE)
    texto(s, X0, 3.62, 6, 0.3, [[("OBJETIVOS ESPECÍFICOS", {"negrito": True})]], tam=12,
          cor=AZUL)
    itens = [
        ("Semântica preservada", "Coluna de cada combustível definida pelo estágio energético "
                                 "declarado"),
        ("Layout automático", "Posições e roteamento sem sobreposição, inclusive fluxos "
                              "reversos"),
        ("Interatividade", "Um clique isola a cadeia energética correspondente"),
        ("Código auditável", "Versionado como texto e documentado para usuário e "
                             "desenvolvedor"),
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
        texto(s, x + 0.25, 5.05, wc - 0.5, 1.6, [
            {"runs": tit, "tam": 16, "negrito": True, "depois": 4},
            {"runs": desc, "tam": 14, "cor": CINZA_TXT}])


def arquitetura(prs):
    s = novo_slide(prs, "Resultados", "Solução: motor próprio em duas camadas", (
        "[~50 s] Em vez de usar um visual pronto, construímos um motor em duas camadas. A "
        "entrada são duas abas de Excel: Fuels, com combustível, estágio e cor; e Techs, com "
        "tecnologia, entrada e saída. O back-end em Power Query, linguagem M, tem nove consultas "
        "e 556 linhas e calcula todas as coordenadas. O front-end em Deneb, com Vega, só "
        "desenha e cuida da interação. Separar as camadas permitiu desenvolver e depurar cada "
        "uma isoladamente. Nenhuma coordenada é desenhada à mão."))
    etapas = [
        (CINZA_FUNDO, ESCURO, "ENTRADA", "Excel", "2 abas: Fuels e Techs"),
        (TINTA, ESCURO, "BACK-END", "Power Query (M)", "9 consultas · 556 linhas\n"
                                                        "calcula as coordenadas"),
        (TINTA, ESCURO, "FRONT-END", "Deneb (Vega v5)", "~1.030 linhas · 16 marcas\n"
                                                         "desenha e interage"),
        (AZUL, BRANCO, "SAÍDA", "Diagrama RES", "interativo no Power BI"),
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
        {"runs": "Várias saídas = várias linhas (ex.: PROETA1)", "tam": 15, "marcador": True,
         "depois": 4},
        {"runs": "Nenhuma coordenada desenhada à mão", "tam": 15, "marcador": True,
         "negrito": True, "cor": AZUL},
    ])


def fantasmas(prs):
    s = novo_slide(prs, "Resultados", "Raias elásticas com nós fantasmas", (
        "[~60 s] Este é o principal resultado técnico. Uma conexão longa, por exemplo de um "
        "combustível do estágio 1 até uma demanda do estágio 5, passa por cima de caixas de "
        "outras tecnologias, como em (a). Desviar a linha exigiria busca em grade, inviável em "
        "M, que não tem estado mutável nem laços. A solução foi reservar espaço antes de "
        "desenhar: cada coluna ocupada que a conexão cruza recebe um nó fantasma invisível, que "
        "conta na densidade da raia, como em (b). A raia passa a reservar mais linhas, e em (c) "
        "a conexão percorre uma linha livre. Tudo é feito com agrupamentos, somas acumuladas e "
        "junções de tabela. A troca é deliberada: o diagrama fica um pouco mais alto, mas o "
        "algoritmo é determinístico."))
    pic, w, h = figura(s, TMP / "fantasmas.png", X0, 2.0, w=7.7, moldura=False,
                       nome="Nos fantasmas")
    texto(s, X0, 2.0 + h + 0.15, w, 0.35,
          ["Troca deliberada: diagrama um pouco mais alto, algoritmo determinístico."],
          tam=13, cor=CINZA_TXT, alinhar=PP_ALIGN.CENTER)
    xd = X0 + w + 0.4
    blocos = [
        ("O problema", "Conexões longas passam por cima de caixas de outras tecnologias."),
        ("A ideia", "Reservar espaço antes de desenhar: cada coluna cruzada ganha um nó "
                    "fantasma invisível."),
        ("Por que cabe em M", "Sem busca em grade nem estado mutável: só agrupamentos, somas "
                              "acumuladas e junções de tabela."),
    ]
    yb = 2.0
    for tit, desc in blocos:
        c = caixa(s, xd, yb, X0 + LARG - xd, 1.42, fundo=CINZA_FUNDO, nome=tit)
        preenche(c.text_frame, [{"runs": tit, "tam": 16, "negrito": True, "cor": AZUL},
                                {"runs": desc, "tam": 14, "antes": 3}],
                 margem=0.18, ancora=MSO_ANCHOR.MIDDLE)
        yb += 1.42 + 0.2


def reversos(prs):
    s = novo_slide(prs, "Resultados", "Fluxos reversos roteados automaticamente", (
        "[~35 s] Um caso que os visuais de mercado rejeitam é o fluxo reverso: a termelétrica a "
        "gás consome gás processado, do estágio 3, e gera eletricidade, que está no estágio 2. "
        "O back-end detecta isso comparando os estágios de entrada e saída, sem o usuário "
        "declarar nada, e o Vega desenha uma rota em ponte por cima das caixas. No sistema de "
        "validação há quatro casos, todos roteados automaticamente."))
    pic, w, h = figura(s, FIG / "Figura4.png", X0, 2.0, w=7.9, nome="Fluxos reversos")
    texto(s, X0, 2.0 + h + 0.06, w, 0.3,
          ["Termelétricas PWRHFO, PWRNGS1 e PWRNGS2: o retorno contorna as caixas pela esquerda"],
          tam=11, cor=CINZA_TXT, alinhar=PP_ALIGN.CENTER)
    xd = X0 + w + 0.4
    wd = X0 + LARG - xd
    st = caixa(s, xd, 2.0, wd, 1.75, fundo=AZUL, nome="Stat 4")
    preenche(st.text_frame, [{"runs": "4", "tam": 48, "negrito": True, "cor": BRANCO},
                             {"runs": "fluxos reversos detectados e roteados", "tam": 14,
                              "cor": AZUL_CLARO}],
             alinhar=PP_ALIGN.CENTER, ancora=MSO_ANCHOR.MIDDLE, margem=0.15)
    texto(s, xd, 3.95, wd, 2.0, [
        {"runs": [("Exemplo: ", {"negrito": True}), "PWRNGS1 consome gás processado "
                  "(estágio 3) e gera eletricidade (estágio 2)."], "tam": 15, "depois": 10},
        {"runs": [("Detecção: ", {"negrito": True}), "comparação dos estágios de entrada e "
                  "saída, sem declaração do usuário."], "tam": 15},
    ])
    b = caixa(s, X0, 5.75, LARG, 0.95, fundo=TINTA, nome="Contraste Sankey")
    preenche(b.text_frame, ["Visuais de Sankey rejeitam esse caso como ciclo ou o desenham "
                            "sobreposto. Aqui ele ganha uma rota própria."],
             tam=16, margem=0.25, ancora=MSO_ANCHOR.MIDDLE)


def interatividade(prs):
    s = novo_slide(prs, "Resultados", "Interatividade: um clique isola a cadeia", (
        "[~50 s] O diagrama deixou de ser imagem e virou interface. No estado íntegro, tudo "
        "aparece em opacidade plena. Ao clicar em BIO, acende todo o grupo de cor: BIO e CAN "
        "compartilham a cor no cadastro, então as demandas de biomassa, a usina PWRBIO e a rota "
        "de etanol PROETA1 acendem juntas. A cor expressa a classe do vetor energético. Ao "
        "clicar em COA, que tem cor exclusiva, só a cadeia do carvão fica em destaque, e a da "
        "biomassa continua visível ao fundo, atenuada. Cada linha tem 2 pixels, mas a área de "
        "clique invisível tem 45 pixels, o que torna o clique viável num diagrama denso."))
    paineis = [
        ("Figura6c.png", "1  Estado íntegro", "Todas as cadeias em opacidade plena"),
        ("Figura6a.png", "2  Clique em BIO", "BIO e CAN têm a mesma cor: o grupo acende junto"),
        ("Figura6b.png", "3  Clique em COA", "Cor exclusiva: só a cadeia do carvão"),
    ]
    wc, gap = 3.6, (LARG - 3 * 3.6) / 2
    for i, (arq, tit, desc) in enumerate(paineis):
        x = X0 + i * (wc + gap)
        texto(s, x, 1.95, wc, 0.35, [[(tit, {"negrito": True})]], tam=16, cor=AZUL)
        figura(s, FIG / arq, x, 2.4, w=wc, nome=tit)
        texto(s, x, 5.6, wc, 0.5, [desc], tam=13, cor=CINZA_TXT)
    b = caixa(s, X0, 6.15, LARG, 0.75, fundo=TINTA, nome="Opacidade")
    preenche(b.text_frame, [[("Destaque por opacidade, não por remoção: ",
                              {"negrito": True, "cor": AZUL}),
                             "o contexto continua visível. Linha de 2 px, área de clique de 45 px."]],
             tam=15, margem=0.25, ancora=MSO_ANCHOR.MIDDLE)


def validacao(prs):
    s = novo_slide(prs, "Resultados", "Validação em sistema nacional estilizado", (
        "[~45 s] A ferramenta foi validada num sistema energético nacional estilizado com 70 "
        "combustíveis em 5 estágios, 101 tecnologias e 106 arestas, incluindo 25 "
        "tecnologias-fonte e 4 fluxos reversos. Também foi testada com bases de topologia "
        "aleatória, com casos patológicos, para confirmar que o layout não depende deste "
        "sistema específico. A figura é só um recorte: o diagrama inteiro tem milhares de "
        "pixels nos dois eixos, por isso zoom e destaque são essenciais. O ganho principal: o "
        "que levava dias à mão agora se atualiza em segundos, e manter o diagrama sincronizado "
        "com o modelo passa a custar praticamente zero."))
    pic, w, h = figura(s, FIG / "Figura7.png", X0, 1.95, h=4.45, nome="Panorama")
    texto(s, X0, 1.95 + h + 0.06, w, 0.3,
          ["Recorte do diagrama gerado: combustíveis primários e secundários"],
          tam=11, cor=CINZA_TXT, alinhar=PP_ALIGN.CENTER)
    xd = X0 + w + 0.4
    wd = X0 + LARG - xd
    stats = [("70", "combustíveis"), ("5", "estágios"), ("101", "tecnologias"),
             ("106", "arestas"), ("4", "fluxos reversos"), ("0", "coordenadas à mão")]
    wc, hc, g = (wd - 0.2) / 2, 0.95, 0.15
    for i, (n, rot) in enumerate(stats):
        x = xd + (i % 2) * (wc + 0.2)
        y = 1.95 + (i // 2) * (hc + g)
        c = caixa(s, x, y, wc, hc, fundo=CINZA_FUNDO, nome=f"Stat {rot}")
        preenche(c.text_frame, [{"runs": n, "tam": 28, "negrito": True, "cor": AZUL},
                                {"runs": rot, "tam": 12, "cor": CINZA_TXT}],
                 alinhar=PP_ALIGN.CENTER, ancora=MSO_ANCHOR.MIDDLE, margem=0.03)
    yb = 1.95 + 3 * (hc + g) + 0.05
    b = caixa(s, xd, yb, wd, 6.4 - yb + 0.0, fundo=AZUL, nome="Ganho")
    preenche(b.text_frame, [
        {"runs": [("Antes: ", {"negrito": True}), "dias de desenho manual"], "tam": 15,
         "cor": AZUL_CLARO},
        {"runs": [("Agora: ", {"negrito": True}), "altera a planilha e atualiza em segundos"],
         "tam": 15, "cor": BRANCO, "antes": 6},
    ], margem=0.2, ancora=MSO_ANCHOR.MIDDLE)


def conclusoes(prs):
    s = novo_slide(prs, "Conclusões", "Conclusões e trabalhos futuros", (
        "[~50 s] Para concluir: entregamos um gerador automático e interativo de diagramas RES, "
        "funcional e documentado. O ganho mais importante é na manutenção: manter o diagrama "
        "sincronizado com o modelo passa a custar praticamente zero. O algoritmo de nós "
        "fantasmas resolve a sobreposição só com transformações de tabela, e o método opera "
        "sobre a forma do grafo, então serve para outros fluxos em camadas, como materiais e "
        "cadeias produtivas. Como próximos passos: parametrizar o layout, reativar a "
        "rastreabilidade de forma otimizada, dimensionar as linhas pelo volume de fluxo e usar "
        "o grafo para diagnosticar inconsistências no modelo. Obrigado."))
    itens = [
        ("Ferramenta entregue", "Gera o RES completo e interativo a partir de duas tabelas, "
                                "funcional e documentada"),
        ("Manutenção a custo quase zero", "O diagrama acompanha o modelo: altera a planilha e "
                                          "atualiza"),
        ("Contribuição técnica", "Nós fantasmas: layout sem sobreposição só com "
                                 "transformações de tabela"),
        ("Método genérico", "Opera sobre a forma do grafo: serve a outros fluxos, como "
                            "materiais e cadeias produtivas"),
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
    futuros = ["Parametrizar as constantes de layout na interface",
               "Reativar a rastreabilidade com cálculo otimizado",
               "Espessura das linhas proporcional ao fluxo",
               "Diagnósticos automáticos de consistência do modelo"]
    preenche(c.text_frame,
             [{"runs": "Trabalhos futuros", "tam": 20, "negrito": True, "cor": AZUL,
               "depois": 6}] +
             [{"runs": f, "tam": 15, "marcador": True, "antes": 10} for f in futuros],
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
            runs[1].text = "Apoio: CNPq · PIBITI/PIBINOVA UFF 2025-2026"
            runs[1].font.size = Pt(18)
    s.notes_slide.notes_text_frame.text = "[~10 s] Obrigado. Fico à disposição para perguntas."


def main():
    prepara_imagens()
    prs = Presentation(str(TEMPLATE))
    capa(prs)
    for f in (contexto, res, lacuna, objetivos, arquitetura, fantasmas, reversos,
              interatividade, validacao, conclusoes, encerramento):
        f(prs)
    prs.save(str(SAIDA))
    print(f"Gerado: {SAIDA} ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
