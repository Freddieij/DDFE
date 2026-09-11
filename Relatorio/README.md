# Relatório Final PIBITI/CNPq 2025-2026

Dois entregáveis, produzidos a partir de fontes versionadas neste diretório.

| Arquivo | O que é |
|---|---|
| `Relatorio_Final_PIBITI_2025-2026.pdf` | Relatório completo, 21 páginas, com figuras, tabelas e referências. Documento complementar. |
| `Formulario_Relatorio_Final_PIBITI_2025-2026.pdf` | **Entregável oficial à AGIR.** Formulário da agência preenchido, com campos ainda editáveis. |
| `relatorio.typ` | Fonte do relatório completo (Typst). |
| `scripts/` | Ferramentas de geração e verificação. |

## Recompilar o relatório

Requer [Typst](https://typst.app) (`winget install Typst.Typst`). Sempre a partir da
**raiz do repositório**, porque as figuras são referenciadas a partir dela:

```bash
typst compile --root . Relatorio/relatorio.typ Relatorio/Relatorio_Final_PIBITI_2025-2026.pdf
typst watch   --root . Relatorio/relatorio.typ    # regenera a cada gravação
```

## Regerar o formulário

Requer `pymupdf`. O script parte do **formulário em branco da AGIR**, que não é versionado
aqui — baixe-o em [agir.uff.br/bolsas](http://agir.uff.br/bolsas) e informe o caminho:

```bash
python Relatorio/scripts/preenche_formulario.py "caminho/para/formulario_em_branco.pdf"
```

Sem argumento, ele procura o arquivo em `~/Downloads`. O conteúdo de cada caixa fica em
`scripts/textos_formulario.py` — edite lá e rode de novo.

## Scripts

| Script | Para quê |
|---|---|
| `preenche_formulario.py` | Preenche os campos do formulário oficial, preservando header, logos e layout. |
| `textos_formulario.py` | Conteúdo de cada caixa do formulário, dimensionado para caber sem rolagem. |
| `mede_caixas.py` | Mede quantas linhas cada caixa comporta e quantas o texto ocupa. Roda antes de preencher. |
| `verifica_referencias.py` | Confere se a Lista de Figuras/Tabelas aponta a página real de cada legenda. |
| `mede_vaos.py` | Mede a mancha branca no pé de cada página, para achar quebras ruins. |
| `audita_numeros.py` | Confere os números citados no relatório contra as planilhas, o JSON do Vega e os `.pq`. |
| `simula_layout.py` | Reimplementa `FuelLayout`/`TechLayout` em Python para inspecionar o efeito dos nós fantasmas. |
| `monta_fig_entrada.py` | Compõe a Figura 2 a partir de `Figuras/Figura2a.png` e `Figura2b.png`. |

### Verificação antes de entregar

```bash
python Relatorio/scripts/verifica_referencias.py     # numeração de figuras e tabelas
python Relatorio/scripts/audita_numeros.py           # números do texto vs. dados reais
python Relatorio/scripts/mede_caixas.py              # caixas do formulário sem transbordo
```

Para `mede_vaos.py`, renderize as páginas antes:

```bash
typst compile --root . --format png --ppi 72 Relatorio/relatorio.typ "Relatorio/_previa/p{0p}.png"
python Relatorio/scripts/mede_vaos.py
```

`Relatorio/_previa/` é descartável e está no `.gitignore`.
