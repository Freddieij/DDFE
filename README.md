# Diagrama de Fluxo de Energia de Referência (RES) — Power BI

Projeto de Iniciação Científica. Um **Diagrama de Fluxo de Energia de Referência (RES)**
dinâmico no Power BI, inspirado em modelos [OSeMOSYS](https://osemosys.readthedocs.io/).

A posição **X (horizontal)** de cada elemento é calculada matematicamente a partir dos
estágios de energia; a posição **Y (vertical)** é organizada automaticamente para evitar
sobreposições. A renderização é feita em **Deneb (Vega-Lite)** sobre dados pré-calculados
em **Power Query (linguagem M)**.

## Arquitetura

```
Excel (fonte)  ──►  Power Query / M  ──►  Deneb (Vega-Lite)
RES_Dados_*.xlsx    Codigo.txt            (dentro do .pbix)
   Techs               FuelLayout  → distribui combustíveis no eixo X
   Fuels               TechLayout  → centro geométrico das caixas Tech, portas de conexão
                       TraceabilityEngine → highlight/rastreabilidade por cor
```

- **`fuel_map` (aba Fuels)** define os estágios verticais dos combustíveis.
- **`tech_map` (aba Techs)** define as conexões (`tech`, `fuel_in`, `fuel_out`).
- O eixo Y é calculado automaticamente (empilhamento) para caixas na mesma coluna.

## Arquivos

| Arquivo | Descrição |
|---|---|
| `cadeias4.pbix` | **Relatório Power BI principal** (arquivo de trabalho). |
| `Codigo.txt` | Export do código Power Query / M — fonte da verdade das queries (`Input_Tech`, `TechLayout`, `FuelLayout`, `TraceabilityEngine`). |
| `RES_Dados_Siglas.xlsx` | **Fonte de dados ATIVA** (referenciada no parâmetro `CaminhoArquivo` do Codigo.txt). Usa siglas dos combustíveis. |
| `RES_Dados_Nome.xlsx` | Variante da fonte com nomes completos dos combustíveis. |
| `Generator/generator.py` | Gera `RES_Dados_Caos.xlsx` (dados aleatórios de stress-test). |
| `TechLayout_EspacamentoMaior.txt` | Variante alternativa do algoritmo de layout (abordagem *Ghost Nodes* geométricos). |
| `Prompt_de_Transicao.txt` | Prompt de handoff/contexto do projeto para continuidade com IA. |
| `pauta.txt` | Notas das reuniões com o orientador. |
| `cadeias.png` | Captura do diagrama. |
| `Documentacao/` | PDFs: Guia do Usuário, Tutorial do Desenvolvedor, Resumo de Resultados. |

## Como usar

1. Abra `cadeias4.pbix` no Power BI Desktop.
2. A fonte de dados é o parâmetro `CaminhoArquivo`, apontando para `RES_Dados_Siglas.xlsx`.
   Ao mover o projeto, ajuste esse caminho em *Transformar dados → Gerenciar parâmetros*.
3. Edite os dados nas abas **Techs** e **Fuels** do Excel e atualize o relatório.

### Gerar dados de teste (caos)

```bash
cd Generator
python generator.py   # requer: pandas, openpyxl
```

Gera `RES_Dados_Caos.xlsx` com conexões aleatórias. É um artefato reproduzível
(ignorado pelo git).
