# Protocolo de Sincronização — mini-repo ↔ Power BI

Este repositório é a **fonte da verdade** do código. O `.pbix` é apenas o *runtime*.
O código vive fatiado em arquivos-texto, um por objeto do Power BI.

## Regra de ouro

1. **Você nunca edita código dentro do Power BI.** Toda alteração é feita aqui (por mim,
   o Claude), e você apenas **cola** no destino.
2. **1 arquivo = 1 objeto do Power BI.** O nome do arquivo é o nome **exato** da query.
3. Você cola sempre o **conteúdo inteiro** do arquivo (CTRL+A → CTRL+C → CTRL+V) no
   editor correspondente, substituindo tudo.

## Mapa arquivo → destino no Power BI

Cada query M é colada em: **Página Inicial → Transformar dados → (selecione a query) →
Página Inicial → Editor Avançado → CTRL+A, colar, Concluído.**

| Arquivo | Query no Power BI | Papel |
|---|---|---|
| `PowerQuery/CaminhoArquivo.pq` | `CaminhoArquivo` | **Parâmetro** com o caminho do `.xlsx`. Editar via Editor Avançado ou *Gerenciar Parâmetros*. Contém caminho absoluto — ajuste ao mudar de máquina. |
| `PowerQuery/Input_Tech.pq` | `Input_Tech` | Leitura crua da aba `Techs`. |
| `PowerQuery/tech_map.pq` | `tech_map` | Tabela de conexões (`tech`, `fuel_in`, `fuel_out`). |
| `PowerQuery/Input_Fuel.pq` | `Input_Fuel` | Leitura crua da aba `Fuels`. |
| `PowerQuery/fuel_map.pq` | `fuel_map` | Estágios verticais dos combustíveis. |
| `PowerQuery/FuelLayout.pq` | `FuelLayout` | Distribuição horizontal (X) dos combustíveis, anti-colisão. |
| `PowerQuery/TechLayout.pq` | `TechLayout` | Centro geométrico das caixas Tech, portas de conexão (offsets). |
| `PowerQuery/energy_view.pq` | `energy_view` | Tabela final consumida pelo visual Deneb. |
| `PowerQuery/TraceabilityEngine.pq` | `TraceabilityEngine` | Rastreabilidade/highlight por cor (ancestrais/descendentes). |

O visual Deneb é colado em: **selecione o visual Deneb → Editar (Edit) → aba `JSON` →
CTRL+A, colar, aplicar.** É uma spec **Vega v5** (não Vega-Lite).

| Arquivo | Destino |
|---|---|
| `Deneb/RES_FlowDiagram.json` | Spec JSON do único visual Deneb. |

## Ordem de dependência (para reconstruir do zero num pbix novo)

`CaminhoArquivo` → `Input_Tech`/`Input_Fuel` → `tech_map`/`fuel_map` →
`FuelLayout` → `TechLayout` → `energy_view` → `TraceabilityEngine` → Deneb.

(O Power BI resolve referências sozinho; a ordem acima é só para leitura humana.)

## Auditoria / detecção de divergência

Se suspeitar que o Power BI divergiu do repo:

```bash
python build.py --check          # valida que todos os arquivos existem e o JSON é válido
python build.py -o _rebuilt.txt  # reconstrói o bundle completo (igual ao antigo Codigo.txt)
```

Reexporte o M/Deneb do pbix e faça `diff` contra `_rebuilt.txt` para achar a diferença.
O `_rebuilt.txt` é ignorado pelo git.
