# Relatório Final — PIBITI/PIBINOVA 2025/2026

**Vigência:** setembro de 2025 a setembro de 2026.

> **Como usar este documento.** Ele está organizado **exatamente** na ordem dos campos do
> formulário oficial da AGIR/PROPPI (o mesmo modelo do relatório-exemplo analisado):
> Título → Orientador → Bolsista → Resumo → Diagnóstico → Soluções Propostas →
> Resultados Alcançados → Referências Bibliográficas → Agenda Acadêmica.
> Cada seção abaixo corresponde a **uma caixa de texto do PDF**: basta copiar o conteúdo
> da seção e colar no campo correspondente.
> Os blocos `[FIGURA N]` são marcadores — substitua por prints/imagens antes de montar
> a versão de apresentação (pôster/slides do Seminário). O formulário PDF em si é só
> texto; as figuras vão para a apresentação e para um anexo opcional.

---

## Título do Projeto

**DIAGRAMA DINÂMICO DE FLUXO ENERGÉTICO (DDFE): GERAÇÃO AUTOMÁTICA DE DIAGRAMAS DE SISTEMA
ENERGÉTICO DE REFERÊNCIA (RES) A PARTIR DE DADOS TABULARES, EM POWER BI**

*(Alternativa mais curta, caso o campo limite caracteres: "Geração automática de Diagramas
de Fluxo de Energia de Referência (RES) a partir de dados tabulares em Power BI")*

## Orientador

**Tiago Abud**

## Bolsista

**Frederico José Poli Antunes**

---

## Resumo do Projeto (Publicável pela Agência de Inovação)

Modelos de planejamento energético de longo prazo — como os construídos em OSeMOSYS, MESSAGE
ou TIMES — são descritos por um **Diagrama de Fluxo de Energia de Referência** (*Reference
Energy System*, RES): um grafo dirigido em que combustíveis e vetores energéticos são
conectados por tecnologias de extração, conversão, transporte e uso final. Esse diagrama é,
na prática, a especificação visual do modelo. Na prática corrente, ele é **desenhado à mão**
em ferramentas de diagramação genéricas (PowerPoint, Visio, draw.io) — artefato caro de
produzir, que desatualiza a cada alteração do modelo e não pode ser auditado nem
interrogado. Existe geração automática fora do ambiente de BI, notadamente o comando
`otoole viz res` (BARNES; USHER, 2023), que produz o diagrama via Graphviz; ela resolve o
custo de produção, mas entrega uma **imagem estática**, cujas colunas são inferidas pela
topologia do grafo e não pelo **estágio energético declarado nos dados**.

Este projeto desenvolveu o **Diagrama Dinâmico de Fluxo Energético (DDFE)**: uma ferramenta
que **gera automaticamente** o diagrama RES completo — posições, roteamento de linhas,
cores e interatividade — a partir de **duas tabelas** que o próprio modelador já mantém
(uma de combustíveis, uma de tecnologias). Não há nenhuma coordenada desenhada manualmente.

A solução é integralmente implementada sobre a pilha **Excel → Power Query (linguagem M) →
Deneb (Vega v5)**, dentro do Microsoft Power BI, e se divide em duas camadas: um *back-end*
geométrico em M, que resolve o problema de *layout* de grafo em camadas (alocação do eixo X
por estágios energéticos com *look-ahead* de densidade; alocação do eixo Y por raias
elásticas com **nós fantasmas** para evitar que conexões longas cortem caixas; detecção
automática de fluxos retroalimentados, os *backflows*); e um *front-end* declarativo em
Vega, que renderiza as coordenadas pré-calculadas e implementa destaque interativo por
*hitboxes* invisíveis, permitindo isolar visualmente uma cadeia de conversão com um clique.

A ferramenta foi validada sobre um sistema energético nacional estilizado com **70
combustíveis em 5 estágios e 101 tecnologias (106 arestas)**, além de uma bateria de
*stress test* com topologias aleatórias geradas por script. O resultado é genérico: qualquer
base relacional que siga a matriz origem–destino padronizada é renderizada sem
reconfiguração. Todo o código (9 consultas M e a especificação Vega) está versionado em
repositório Git, com documentação de usuário e de desenvolvedor.

`[FIGURA 1 — Diagrama RES completo gerado pela ferramenta: captura em tela cheia do visual
Deneb em Modo de Foco. Ainda não existe no repositório — é a captura de maior prioridade.
Ver o passo a passo no Apêndice.]`

---

## Diagnóstico

### 1. O contexto: o RES é a espinha dorsal do modelo energético

Ferramentas de modelagem energética de sistemas (*energy system optimization models*, ESOM)
representam o setor energético de um país ou região como uma rede de fluxos. A formulação
canônica do OSeMOSYS (HOWELLS et al., 2011) e das famílias MARKAL/TIMES (LOULOU et al.,
2005) parte da mesma abstração: **combustíveis** (*fuels* / *commodities*) e **tecnologias**
(*technologies*) que consomem um conjunto de combustíveis de entrada e produzem um conjunto
de saída. Os combustíveis são organizados por **estágio** da cadeia energética — recurso
primário, secundário, final, útil, demanda — e essa ordenação define a leitura do diagrama
da esquerda para a direita.

O RES não é ilustração: é o **contrato de especificação** entre o modelador, o orientador,
o revisor e o tomador de decisão. É por ele que se verifica se uma rota tecnológica foi
esquecida, se um combustível ficou órfão (produzido e nunca consumido), se há um ciclo
indevido, ou se a mesma demanda está sendo atendida por duas cadeias concorrentes.

### 2. O problema observado

Durante o levantamento inicial do projeto, com a base de um sistema energético nacional
estilizado (70 combustíveis, 101 tecnologias), os seguintes gargalos foram caracterizados:

**(a) Custo de produção manual e altíssimo custo de manutenção.**
Um RES desse porte tem da ordem de 170 nós e mais de 100 arestas. Desenhado à mão, ele
consome dias de trabalho — o próprio projeto produziu essa evidência: a especificação visual
que serviu de alvo (`cadeias.png`) precisou ser desenhada caixa a caixa em ferramenta de
diagramação antes que a automação existisse. Pior: **toda alteração estrutural do modelo invalida o desenho**.
Acrescentar um único combustível intermediário obriga a reposicionar manualmente dezenas de
caixas e a redesenhar as linhas que passavam por ali. Na prática, o diagrama congela numa
versão antiga e passa a **divergir do modelo que ele deveria documentar** — o pior
resultado possível para um artefato de especificação.

**(b) Ausência de garantia de fidelidade.**
Como o desenho é feito num arquivo separado da base de dados, nada impede que ele omita uma
conexão existente ou mostre uma conexão que não existe. Não há verificação possível: o
diagrama é uma segunda fonte da verdade, e uma fonte não auditável.

**(c) O que já existe, e onde para.**
A geração automática de RES **não é território virgem**, e o levantamento do estado da arte
foi refeito antes da redação deste relatório. O achado mais relevante é o comando
**`otoole viz res`**, parte do `otoole` — a suíte oficial de ferramentas do ecossistema
OSeMOSYS (BARNES; USHER, 2023). Ele monta um grafo dirigido com `networkx` a partir dos
parâmetros `InputActivityRatio` e `OutputActivityRatio` do modelo e o desenha com o motor
`dot` do **Graphviz**, configurado com `rankdir=LR`, `splines=ortho` e `concentrate=true`,
exportando uma imagem estática (PNG, PDF etc.) e um arquivo `.graphml`.

É a peça de arte prévia mais próxima deste projeto, e ela **resolve o custo de produção**.
Suas limitações, verificadas diretamente no código-fonte do módulo `otoole/visualise/res.py`,
são o que delimita o espaço deste trabalho:

- **A coluna é inferida, não declarada.** O `dot` atribui a camada (*rank*) de cada nó a
  partir da topologia do grafo, minimizando o comprimento das arestas. O **estágio
  energético** — informação semântica que o modelador conhece e que define a leitura
  "primário → secundário → final → útil → demanda" — não é entrada do algoritmo. Um nó pode
  ser deslocado de coluna por conveniência do layout, quebrando a leitura setorial.
- **Os combustíveis não são entidades visuais de primeira classe.** No código, nós de
  combustível recebem `height: 0.1`, `width: 0.1` e `label: ""` — são pontos minúsculos e
  **sem rótulo**. A leitura do diagrama passa a depender inteiramente dos nomes das
  tecnologias.
- **A saída é uma imagem.** Não há clique, destaque, filtro ou rastreamento.
- **A extração de subgrafos é uma demanda aberta e não atendida.** A *issue* #14 do
  repositório `otoole` pede exatamente isso — caminho mais curto entre dois nós, todos os
  predecessores de um nó, tudo conectado a um combustível — e está **aberta desde outubro de
  2019**, sem implementação. A mesma lacuna aparece na *issue* #102 do `tz-osemosys`, que
  pede auto-geração de RES e também segue aberta.

**(d) Inadequação das visualizações prontas de plataformas de BI.**
A outra resposta óbvia — usar um visual de Sankey ou de rede pronto do Power BI — falha por
três motivos estruturais:

- **Sankey codifica espessura por volume, não topologia.** O RES precisa mostrar *quais*
  rotas existem, não *quanto* flui por elas (e, na fase de especificação, os volumes sequer
  são conhecidos).
- **O eixo X do Sankey é derivado do grafo**, e não do **estágio energético** — o mesmo
  defeito do `dot`. Visuais de rede da categoria vão além e usam layout por força dirigida
  (Fruchterman–Reingold), que abandona por completo a noção de coluna.
- **Fluxos reversos não são tratados.** Quando uma tecnologia consome um combustível de
  estágio posterior e devolve para um estágio anterior — situação legítima e frequente,
  p. ex. a termelétrica a gás que consome gás processado (estágio 3) e produz eletricidade de
  geração (estágio 2) — Sankeys convencionais produzem sobreposição ilegível ou rejeitam o
  caso como ciclo.

**(e) Ausência de interrogabilidade.**
Mesmo um diagrama bem desenhado, acima de ~50 nós, torna-se um emaranhado. A pergunta que o
modelador realmente faz — *"me mostre tudo que depende deste combustível"* — não tem
resposta num PNG estático. Há trabalho acadêmico em visualização interativa de sistemas
energéticos (ALEMASOOM et al., 2016), mas voltado à exploração de **grandezas** — séries
temporais, distribuição espacial, emissões — e não à especificação topológica do modelo,
além de existir como protótipo de pesquisa, fora do ferramental de trabalho do modelador.

### 3. Formulação do problema técnico

Reduzido à sua essência, o problema é um caso restrito de **desenho de grafo em camadas**
(*layered graph drawing*), a classe de problemas formalizada por SUGIYAMA, TAGAWA e TODA
(1981) e implementada em ferramentas como o `dot` (GANSNER et al., 1993). A diferença — e a
dificuldade adicional — é que, no RES:

1. **A atribuição de camadas é imposta pelos dados**, não otimizada pelo algoritmo: o
   estágio do combustível é semântico e não pode ser alterado pelo layout;
2. **Existem arestas retrógradas legítimas** que precisam ser desenhadas, não removidas;
3. **A ferramenta de destino não é um motor de grafos** — é o Power BI, cujas primitivas de
   cálculo são a linguagem M (funcional, orientada a tabelas, **sem estruturas mutáveis e
   sem laços imperativos**) e cuja camada de renderização acessível é a gramática
   declarativa Vega, via conector Deneb.

**A lacuna que o projeto ataca**, portanto, não é "gerar o RES automaticamente" — isso o
`otoole` já faz. É gerar um RES em que **a coluna é imposta pelo dado semântico** (o estágio
energético), em que os combustíveis são eixos rotulados de primeira classe, em que fluxos
reversos são roteados em vez de rejeitados, e em que o resultado é **interrogável** — tudo
isso dentro da plataforma de BI em que o restante da análise do grupo já vive.

`[FIGURA 2 — "Antes e depois": à esquerda, cadeias.png — a referência de projeto desenhada
manualmente no Canva, que define o resultado pretendido; à direita, a saída automática da
ferramenta (Figura 1). Além de documentar o custo do caminho manual, o par demonstra a
fidelidade: a ferramenta reproduz a estrutura especificada partindo só de duas planilhas.]`

---

## Soluções Propostas

### 1. Princípio de projeto: separar geometria de renderização

A decisão arquitetural central foi **abandonar os visuais de Sankey prontos** e construir
uma *engine* própria, dividida em duas camadas com contrato explícito entre elas:

| Camada | Tecnologia | Responsabilidade |
|---|---|---|
| **Back-end geométrico** | Power Query / linguagem M | Ler a topologia; alocar coordenadas X e Y **absolutas**; resolver colisões; classificar arestas (normal, *backflow*, *hub*) |
| **Front-end de renderização** | Deneb / Vega v5 | Receber um *dataset* achatado com coordenadas já calculadas e desenhá-lo com primitivas vetoriais; gerenciar interação |

O contrato é uma única tabela achatada (`energy_view`), em que cada linha já carrega tudo
que o renderizador precisa. **O Vega não calcula posição** — ele apenas desenha. Essa
separação foi o que tornou o problema tratável: cada camada pôde ser desenvolvida, testada e
depurada isoladamente.

A entrada do sistema são **duas abas de Excel**, deliberadamente mínimas:

- **`Fuels`** — `fuel` (identificador), `stage` (estágio numérico 1..N), `color` (cor);
- **`Techs`** — `tech` (identificador da tecnologia), `fuel_in`, `fuel_out`.

Múltiplas entradas ou saídas de uma mesma tecnologia são expressas como **múltiplas linhas
com o mesmo `tech`** — decisão que mantém a planilha plana e editável por quem não programa.

`[FIGURA 3 — Print das duas abas do Excel lado a lado (Fuels e Techs), com algumas linhas
visíveis, para mostrar quão simples é a entrada. Destaque em vermelho uma tecnologia que
aparece em 3 linhas — ex.: PROETA1, que produz EAN, EHY e BAG.]`

### 2. Pipeline de transformação (9 consultas em linguagem M)

O *back-end* foi decomposto em nove consultas encadeadas, cada uma com responsabilidade
única e testável:

```
CaminhoArquivo (parâmetro)
      │
      ├──► Input_Tech ──► tech_map ──┐
      └──► Input_Fuel ──► fuel_map ──┴──► FuelLayout ──► TechLayout ──► energy_view ──► Deneb
                                                              └──► TraceabilityEngine
```

`[FIGURA 4 — Print do painel de consultas do Power Query (barra lateral esquerda) ou do
diagrama de dependências de consultas (Exibir → Dependências de Consulta), mostrando o
encadeamento real das 9 queries.]`

### 3. As quatro contribuições técnicas do projeto

#### 3.1. Alocação do eixo X com *look-ahead* de densidade (`FuelLayout`)

A abordagem ingênua — colunas de largura fixa por estágio — produz diagramas desbalanceados:
estágios com poucos combustíveis desperdiçam espaço, e estágios densos ficam comprimidos.

A solução implementada calcula a largura de cada faixa em função da **densidade do próprio
estágio e da do estágio seguinte**:

```m
LarguraDesteStage =
    GapBasico + ( List.Max({ ContagemDesteStage, ContagemDoProximoStage }) × PixelsPorItem )
```

As posições finais são obtidas por soma acumulada (`List.Accumulate`) dessas larguras. O
*look-ahead* é o que evita que as linhas que **saem** de um estágio denso colidam ao entrar
no próximo: reserva-se espaço para o pior caso local antes de ele acontecer. Dentro de cada
faixa, os combustíveis são distribuídos por um desvio normalizado em torno do centro,
garantindo que nenhum par de colunas verticais se sobreponha.

#### 3.2. Paredes geométricas para posicionar tecnologias (`TechLayout`, eixo X)

Uma tecnologia não pertence a um estágio: ela **vive entre estágios**. Para posicioná-la,
cada estágio é reduzido a duas "paredes" — `ParedeEsquerda` (o menor X entre seus
combustíveis) e `ParedeDireita` (o maior X). Para cada tecnologia, calculam-se
`Max_Stage_In` e `Min_Stage_Out`, e o X é resolvido por três casos:

- **Caso 1 — tem entrada e saída.** Se `Max_Stage_In < Min_Stage_Out` (fluxo direto), a
  caixa é centrada entre a parede direita da entrada e a parede esquerda do estágio seguinte.
  Se `Max_Stage_In ≥ Min_Stage_Out`, trata-se de um ***backflow***: as referências espaciais
  são **invertidas**, e a caixa é posicionada antes do destino, do lado correto para o
  roteamento retrógrado.
- **Caso 2 — só entrada** (tecnologia de demanda/exportação): posicionada à direita da
  origem.
- **Caso 3 — só saída** (extração, importação, fonte renovável sem insumo — no dataset de
  validação são **28 tecnologias**, como `MINOIL`, `IMPCOA`, `PWRSOL1`, `PWRWND1`):
  posicionada à esquerda do destino.

A classificação `IsBackflow` é derivada aqui e propagada até o Vega, que aplica regras de
desenho diferentes. No sistema de validação, **4 arestas são backflows** (`PWRBAG`,
`PWRNGS1`, `PWRNGS2`, `PWRHFO` — termelétricas que consomem combustível de estágio 3 e
alimentam a eletricidade de geração, estágio 2), todas roteadas automaticamente.

`[FIGURA 5 — Zoom numa região do diagrama mostrando um backflow: a linha que sobe por cima
das caixas, faz a volta e desce no destino. Recorte do print principal.]`

#### 3.3. Raias elásticas e **nós fantasmas** — o núcleo do algoritmo (`TechLayout`, eixo Y)

Este é o principal resultado técnico do projeto.

**O problema.** Empilhar as tecnologias verticalmente por "raia" (*swimlane*) do combustível
de origem resolve a colisão entre caixas, mas **não resolve a colisão entre caixas e
linhas**. Uma conexão de longo alcance (*long haul*) — por exemplo, um combustível do
estágio 1 consumido por uma demanda do estágio 5 — atravessa horizontalmente várias colunas
e passa **por cima de caixas de tecnologia alheias**, produzindo um cruzamento ilegível.

**A solução.** Em vez de rotear a linha desviando dos obstáculos (o que exigiria busca em
grade, algo inviável em M puro), o algoritmo **reserva espaço antes de desenhar**. Para cada
conexão longa, gera-se um conjunto de **nós fantasmas** (*ghost nodes*) — entidades
invisíveis, uma para cada coluna ocupada que a linha cruza:

```m
GeraGhostsGeometricos = Table.AddColumn(FiltraLongHaul, "GhostGrid", each
    let
        Start = List.Min({[x_tech], [x_fuel_out]}),
        End   = List.Max({[x_tech], [x_fuel_out]}),
        GridsNoCaminho = List.Select(ListaGridsOcupados, (g) => g > (Start + 25) and g < (End - 25))
    in
        GridsNoCaminho
)
```

Os fantasmas são então **contabilizados como se fossem caixas reais** no cálculo de
densidade local. A altura reservada para cada raia passa a ser o **pior caso** ao longo de
toda a sua extensão horizontal:

```
Altura_Reservada(raia) = máx sobre todas as colunas de  QtdItens(raia, coluna)
Y_Base(raia_k)         = Σ Altura_Reservada(raia_i), para i < k     (soma acumulada)
```

O efeito é que a raia **se dilata elasticamente** exatamente onde a linha precisa passar,
abrindo um corredor livre. A linha é desenhada reta, sem desvio, e mesmo assim não colide —
porque o espaço foi negociado na fase de alocação, e não na de roteamento. É uma troca
deliberada: aceita-se um diagrama um pouco mais alto em favor de um algoritmo determinístico,
sem busca e expressável em transformações de tabela.

Duas correções foram necessárias para que o algoritmo ficasse estável, ambas documentadas no
código:

- a contagem de densidade usa `Table.Distinct` por `tech`, para que uma tecnologia com três
  saídas não infle a altura da raia como se fossem três caixas;
- o índice vertical é atribuído sobre a lista de tecnologias **distintas** e depois
  reassociado por *join*, garantindo que todas as arestas de uma mesma tecnologia apontem
  para a **mesma** caixa.

`[FIGURA 6 — Diagrama conceitual do algoritmo de nós fantasmas (pode ser desenhado à mão ou
em draw.io): (a) uma linha longa cortando caixas; (b) os nós fantasmas gerados ao longo do
caminho, em tracejado; (c) a raia inflada e a linha passando livre. Esta é a figura que
explica a contribuição central — vale investir nela.]`

#### 3.4. Lógica de *hub* e tratamento de anomalias (`Input_Tech`)

Nem toda aresta do RES tem tecnologia associada — há ligações diretas entre combustíveis. O
sistema gera identificadores sintéticos para esses casos (`LINK_HUB_[fuel_in]`, agrupando
por origem, ou `LINK_ORFAO_[GUID]` como último recurso) e os marca com `IsHidden = true`,
instruindo o Vega a desenhar **apenas a linha**, sem a caixa. Isso mantém uma única
representação interna para todas as arestas, sem ramificação especial no renderizador.

Há também um mecanismo de **herança automática de cor**: combustíveis de demanda (estágio
final) herdam a cor do combustível que os origina, de modo que uma cadeia inteira permanece
cromaticamente coerente sem que o usuário precise preencher a coluna `color` para dezenas de
nós de demanda — no dataset de validação, **46 dos 70 combustíveis** são nós de demanda que
se beneficiam dessa regra.

### 4. Camada de interação (`Deneb` / Vega v5)

A especificação Vega (≈1.030 linhas) organiza-se em **9 *datasets* derivados** do dataset
único vindo do Power Query, por filtro e fórmula, e **16 marcas** de desenho.

**Técnica de *hitbox* invisível.** Cada elemento clicável é desenhado **duas vezes**: uma
marca visual fina (traço de 2 px) e uma marca de captura com `strokeWidth: 45` e
`strokeOpacity: 0.001`. O usuário vê uma linha fina e elegante, mas dispõe de uma área de
clique de 45 px. Sem isso, acertar uma linha de 2 px com o mouse num diagrama denso é
inviável na prática. O padrão é aplicado a combustíveis, entradas, saídas e *backflows*.

**Destaque por sinais reativos.** Cinco sinais Vega implementam a interrogação do diagrama:

| Sinal | Evento | Efeito |
|---|---|---|
| `sel_fuel_color` | `@fuel_hitbox:click` | Isola a coluna do combustível e **todos** os fluxos da mesma cor |
| `sel_tech_color` | `@tech_box:click` | Destaca a tecnologia e seus fluxos de entrada e saída |
| `sel_line_color` | `@input_hitbox:click` | Ilumina os fluxos horizontais de entrada |
| `sel_line_bf1_color` | `@bf1_hitbox:click` | Destaca especificamente rotas de *backflow* |
| `sel_line_out_color` | `@output_hitbox:click` | Destaca fluxos de saída |

Todos respondem a `dblclick[!event.item]` (duplo clique no fundo) restaurando o estado
integral. O destaque opera por **opacidade**, não por remoção: o contexto permanece
visível, atenuado — o que preserva a leitura global enquanto se examina um detalhe.

**Roteamento de *backflow* em quatro regras.** Fluxos retrógrados são desenhados por quatro
marcas coordenadas (`bf_travel`, `bf_down`, `bf_enter`, `bf_point`), apoiadas em coordenadas
auxiliares calculadas ainda no Power Query: `yBridge` (altura da "ponte" que passa por cima
das caixas) e `xTurn` (ponto da curva de retorno).

`[FIGURA 7 — Sequência de 2 ou 3 prints mostrando a interação: (a) diagrama completo;
(b) após clique num combustível — só aquela cadeia acesa; (c) após clique numa tecnologia.
Monte lado a lado, é a demonstração mais convincente da ferramenta.]`

### 5. Motor de rastreabilidade (`TraceabilityEngine`)

Para responder à pergunta *"o que depende deste nó?"*, foi implementada busca em grafo
(ancestrais e descendentes) em M puro. Como a linguagem não oferece estruturas mutáveis, a
travessia usa `List.Generate` (iteração funcional com estado em registro) sobre **mapas de
adjacência pré-construídos** como registros M (`Record.FromList`), o que converte a busca
de vizinhos de uma varredura de tabela O(n) para um acesso direto por chave via
`Record.Field`. A recursão é limitada a 20 níveis como salvaguarda contra ciclos. As saídas
são as colunas `Ancestors_Path` e `Descendants_Path`, cadeias delimitadas por `|`
diretamente consumíveis por um teste de substring no Vega.

O motor está **implementado e funcional, porém desativado por padrão** no *pipeline* final:
sua materialização impacta sensivelmente o tempo de atualização do modelo, e o destaque por
cor já cobre a maior parte dos casos de uso exploratório. A decisão, seus motivos e o
caminho de reativação estão documentados no Tutorial do Desenvolvedor. Trata-se de um
*trade-off* explícito, não de código morto.

### 6. Engenharia de processo: o repositório como fonte da verdade

Um problema recorrente em projetos de BI é que **o código fica preso dentro do binário**.
Um arquivo `.pbix` não é diferenciável, não é revisável e não tem histórico útil. Isso
inviabiliza revisão por pares e torna impossível saber *o que* mudou entre duas versões.

A solução adotada foi **externalizar todo o código como texto versionado**, com mapeamento
1:1 entre arquivo e objeto do Power BI:

```
PowerQuery/*.pq             9 arquivos, 1 por consulta M      (556 linhas)
Deneb/RES_FlowDiagram.json  especificação Vega v5           (1.032 linhas)
SYNC.md                     protocolo de sincronização + mapa arquivo → destino
build.py                    reconstrói o pacote e valida para auditar divergências
```

O repositório Git é a fonte da verdade; o `.pbix` é apenas o *runtime*, e é comitado
**junto** com a alteração de texto, de modo que nunca fiquem dessincronizados no histórico.
O script `build.py --check` valida a integridade dos arquivos e do JSON, e
`build.py -o _rebuilt.txt` reconstrói o pacote completo para comparação (`diff`) contra o
que está efetivamente carregado no Power BI — um mecanismo simples de auditoria de deriva.

### 7. Validação por dados sintéticos

Foi desenvolvido um gerador (`Generator/generator.py`, 239 linhas) que produz bases com
topologias aleatórias — inclusive casos patológicos: combustíveis órfãos, tecnologias sem
entrada, conexões de altíssimo alcance e múltiplos *backflows* simultâneos. A ferramenta foi
exercitada contra essas bases para verificar que o algoritmo de layout **não depende de
propriedades particulares** do sistema energético real utilizado no desenvolvimento.

`[FIGURA 8 — Print do diagrama gerado a partir da base de caos (RES_Dados_Caos.xlsx),
lado a lado com o diagrama do sistema real, demonstrando que o layout se sustenta em
topologias arbitrárias.]`

---

## Resultados Alcançados

### 1. Produto entregue

Foi entregue uma ferramenta **funcional, documentada e versionada** que gera diagramas RES
completos e interativos a partir de duas tabelas, sem nenhuma coordenada desenhada
manualmente. A ferramenta está operacional no Power BI Desktop e foi validada sobre um
sistema energético nacional estilizado com:

| Métrica | Valor |
|---|---|
| Combustíveis (nós verticais) | **70** |
| Estágios energéticos | **5** (8 / 2 / 10 / 4 / 46 combustíveis por estágio) |
| Tecnologias distintas | **101** |
| Arestas (linhas da aba `Techs`) | **106** |
| Tecnologias-fonte (só saída) | **28** |
| Tecnologias multi-saída | **4** |
| *Backflows* detectados e roteados automaticamente | **4** |
| Cores semânticas distintas | **10** |
| Coordenadas desenhadas manualmente | **0** |

Do ponto de vista de esforço de produção: o mesmo diagrama, desenhado à mão, é trabalho da
ordem de **dias**; com a ferramenta, a alteração de uma linha na planilha e um clique em
*Atualizar* reconstroem o diagrama inteiro — reposicionamento, roteamento e cores —
em **segundos**. Mais relevante do que o ganho na primeira produção é o ganho na
manutenção: o custo marginal de manter o diagrama sincronizado com o modelo **cai a
praticamente zero**, o que elimina a causa raiz do problema diagnosticado (a divergência
entre o desenho e o modelo que ele documenta).

`[Ver FIGURA 1 — a captura em tela cheia do resultado final serve tanto ao Resumo quanto a
esta seção; é a "figura de capa" do relatório e do pôster.]`

### 2. Resultados técnicos específicos

**(a) Algoritmo de layout determinístico para grafos em camadas com restrição semântica.**
A combinação *look-ahead* de densidade no eixo X + raias elásticas com nós fantasmas no eixo
Y resolve o problema de sobreposição **sem busca e sem iteração de otimização** — apenas com
transformações de tabela. Isso é o que torna possível executá-lo dentro do motor do Power
Query, um ambiente que não foi projetado para algoritmos de grafo.

A distinção em relação à arte prévia é precisa e vale enunciá-la sem exagero. A geração
automática de RES já existe: o `otoole viz res` a oferece desde o ecossistema oficial do
OSeMOSYS. A diferença deste trabalho está em **quem decide a coluna**. Em layouts do tipo
`dot`, a camada de cada nó é *derivada* da topologia pelo algoritmo; aqui, ela é *imposta*
pelo campo `stage` declarado nos dados, e o algoritmo trabalha sob essa restrição em vez de
otimizá-la. Essa inversão é o que preserva a leitura semântica do RES
("primário → secundário → final → útil → demanda") e é também o que cria o problema de
sobreposição que os nós fantasmas resolvem — um motor livre para mover nós entre camadas
simplesmente não enfrenta esse caso.

**Na revisão realizada, não foi identificada** implementação equivalente — layout RES com
camada imposta pelos dados, combustíveis rotulados como eixos de primeira classe,
roteamento explícito de fluxos reversos e interatividade — nativa em plataforma de BI.

**(b) Tratamento nativo de fluxos retroalimentados.** *Backflows* são detectados
automaticamente pela comparação de estágios (`Max_Stage_In ≥ Min_Stage_Out`), sem nenhuma
declaração do usuário, e roteados por um conjunto dedicado de quatro regras de desenho com
coordenadas de ponte. Esta é justamente a classe de caso que os visuais de Sankey de mercado
rejeitam ou renderizam de forma ilegível.

**(c) Interrogabilidade do diagrama.** O diagrama deixou de ser uma imagem e passou a ser
uma interface: o usuário clica num combustível e a ferramenta isola a cadeia inteira daquela
cor; clica numa tecnologia e vê exatamente o que entra e o que sai. A técnica de *hitbox*
invisível (captura de 45 px sobre traço visível de 2 px) foi o que tornou essa interação
utilizável na densidade real do diagrama. Vale registrar que essa capacidade — extrair e
destacar o subgrafo conectado a um nó — é precisamente o que a *issue* #14 do repositório
`otoole` solicita **desde outubro de 2019 e segue sem implementação**: o
`TraceabilityEngine` deste projeto endereça, ainda que noutro ambiente, uma demanda
reconhecidamente em aberto na ferramenta de referência do ecossistema.

**(d) Genericidade comprovada.** O algoritmo não contém nenhuma regra específica do sistema
energético brasileiro nem do vocabulário utilizado. Opera sobre a **forma** do grafo
(estágios, graus de entrada e saída, alcance das arestas). A validação com bases sintéticas
aleatórias confirma que qualquer matriz origem–destino no formato padronizado é renderizada
sem reconfiguração — o que abre aplicação para fluxos de materiais, cadeias produtivas,
processos industriais e outros domínios com a mesma estrutura.

**(e) Código auditável.** A externalização do código para 10 arquivos-texto versionados, com
protocolo de sincronização documentado e script de verificação, resolve o problema de
opacidade do artefato `.pbix` e torna o projeto revisável, continuável e transferível.

### 3. Produção documental

| Documento | Público | Conteúdo |
|---|---|---|
| **Guia do Usuário** (3 p.) | Modelador energético | Estrutura das planilhas, atualização de dados, leitura e interação com o diagrama, comportamento dos *backflows* |
| **Tutorial do Desenvolvedor** (4 p.) | Futuro mantenedor | Arquitetura em duas camadas, dissecação de cada consulta M, lógica de *hub*, cálculo de paredes, nós fantasmas, motor de rastreabilidade, tabela de sinais Vega, padrão *hitbox*, roteamento de *backflow*, próximos passos |
| **Resumo de Resultados e Arquitetura** (1 p.) | Avaliador / divulgação | Síntese executiva das inovações |
| **`README.md` + `SYNC.md`** | Continuidade do projeto | Arquitetura, mapa arquivo → objeto do Power BI, ordem de dependências, procedimento de auditoria |

### 4. Registro do processo de desenvolvimento

O desenvolvimento está registrado em repositório Git, com histórico que documenta a
progressão do trabalho: da versão inicial monolítica, passando pela consolidação da versão
estável, pela produção da documentação, até a reestruturação final em mini-repositório com
código fatiado, protocolo de sincronização e script de auditoria. As mensagens de *commit*
descrevem a **causa** de cada mudança, não apenas o que mudou.

### 5. Dificuldades encontradas

**(a) Limitações da linguagem M para algoritmos de grafo.** M é funcional e sem estado
mutável: não há vetores indexados para escrita, não há laços `for`, não há recursão
convencional eficiente. Todo o algoritmo de layout precisou ser reexpresso como sequência
de `Table.Group`, `List.Accumulate`, `Table.NestedJoin` e `Table.AddIndexColumn`. Foi a
principal dificuldade do projeto — e também o que produziu a solução dos nós fantasmas, que
é uma resposta *direta* a essa restrição: não sendo possível **rotear** desviando de
obstáculos, optou-se por **reservar espaço** antes de desenhar. A limitação da ferramenta
determinou a forma da contribuição técnica.

**(b) Desempenho do motor de rastreabilidade.** A implementação por mapas de adjacência
reduziu drasticamente o custo da busca, mas a materialização das colunas de caminho ainda
onera a atualização do modelo. A decisão foi desativá-la por padrão e documentar a
reativação — um *trade-off* explícito entre funcionalidade e tempo de carga.

**(c) Estabilidade do cálculo do eixo Y.** Duas classes de defeito exigiram correção: a
inflação espúria da altura da raia quando uma tecnologia tinha múltiplas saídas, e a
dispersão de uma mesma tecnologia por posições Y distintas. Ambas foram resolvidas pela
introdução de deduplicação por `tech` antes da indexação, com reassociação posterior por
*join* — hoje documentadas como comentários no código.

**(d) Ausência de ponte automatizada com o Power BI.** O Power BI não expõe API de escrita
para consultas M ou especificações Deneb. O ciclo de edição exige transporte manual do
arquivo-texto para o editor da ferramenta. O protocolo `SYNC.md` e o `build.py` foram
criados justamente para tornar esse ciclo confiável e para permitir detectar quando o
runtime divergiu da fonte.

### 6. Trabalhos futuros

1. **Parametrização via interface.** Externalizar as constantes de layout (`techW`, `techH`,
   `techRowGap`, `hookGap`, `GapBasico`, `PixelsPorItem`) para campos de parâmetro do Power
   BI, permitindo ajuste fino sem editar código.
2. **Reativação otimizada da rastreabilidade.** Avaliar cálculo incremental ou pré-computação
   externa dos caminhos, evitando o gargalo na atualização.
3. **Dimensionamento por volume.** Acrescentar uma coluna opcional de fluxo e modular a
   espessura das linhas, unindo a expressividade topológica do RES à quantitativa do Sankey.
4. **Exportação vetorial.** Gerar SVG/PDF em resolução de publicação, para uso direto em
   artigos e relatórios técnicos.
5. **Validação semântica da base.** Aproveitar o grafo já construído para emitir
   diagnósticos automáticos — combustível órfão, tecnologia inalcançável, demanda não
   atendida, ciclo não declarado —, transformando a ferramenta de visualizador em
   **verificador de consistência do modelo**.
6. **Aplicação a outros domínios.** Testar a ferramenta sobre fluxos de materiais e cadeias
   produtivas, domínios com a mesma estrutura de grafo em camadas.

### 7. Conclusão

O projeto entregou aquilo a que se propôs: **um gerador automático, dinâmico e interativo de
diagramas de fluxo de energia**, que elimina o gargalo do desenho manual e, mais importante,
o custo de manutenção que fazia o diagrama divergir do modelo. O resultado técnico central —
o algoritmo de raias elásticas com nós fantasmas — é uma resposta original às restrições de
um ambiente de cálculo funcional sem estado mutável, e é generalizável a qualquer grafo em
camadas com restrição semântica de camada. A ferramenta é escalável a qualquer base
relacional que siga a matriz origem–destino padronizada, está documentada em três níveis
(usuário, desenvolvedor, executivo) e tem seu código versionado como texto auditável,
pronto para continuidade.

---

## Referências Bibliográficas

HOWELLS, Mark et al. **OSeMOSYS: The Open Source Energy Modeling System — An introduction to
its ethos, structure and development.** *Energy Policy*, v. 39, n. 10, p. 5850–5870, 2011.

OSEMOSYS. **Create a model in OSeMOSYS — Reference Energy System.** Documentação oficial.
Disponível em:
<https://osemosys.readthedocs.io/en/latest/manual/Create%20a%20model%20in%20OSeMOSYS.html>.
Acesso em: `[DATA]`.

BARNES, Trevor; USHER, Will. **otoole: OSeMOSYS Tools for Energy Work.** *Journal of Open
Source Software*, v. 8, n. 92, art. 5511, 2023. DOI: 10.21105/joss.05511.

OTOOLE. **Core Functionality — `otoole viz res`.** Documentação oficial. Disponível em:
<https://otoole.readthedocs.io/en/latest/functionality.html>. Acesso em: `[DATA]`.

OSEMOSYS/OTOOLE. **Issue #14 — `otoole viz res`: Visualise subgraph of the reference energy
system.** Repositório GitHub, aberta em out. 2019. Disponível em:
<https://github.com/OSeMOSYS/otoole/issues/14>. Acesso em: `[DATA]`.

TRANSITION ZERO. **Issue #102 — ENH: auto-generate a Reference Energy System (RES)
diagram.** Repositório `tz-osemosys`, GitHub. Disponível em:
<https://github.com/transition-zero/tz-osemosys/issues/102>. Acesso em: `[DATA]`.

ALEMASOOM, Haleh; SAMAVATI, Faramarz; BRODLIE, Ken; LAYZELL, David. **EnergyViz: an
interactive system for visualization of energy systems.** *The Visual Computer*, v. 32,
n. 3, p. 403–413, 2016.

LOULOU, Richard; REMME, Uwe; KANUDIA, Amit; LEHTILÄ, Antti; GOLDSTEIN, Gary. **Documentation
for the TIMES Model.** Energy Technology Systems Analysis Programme (ETSAP), 2005.

SUGIYAMA, Kozo; TAGAWA, Shojiro; TODA, Mitsuhiko. **Methods for Visual Understanding of
Hierarchical System Structures.** *IEEE Transactions on Systems, Man, and Cybernetics*,
v. 11, n. 2, p. 109–125, 1981.

GANSNER, Emden R.; KOUTSOFIOS, Eleftherios; NORTH, Stephen C.; VO, Kiem-Phong. **A Technique
for Drawing Directed Graphs.** *IEEE Transactions on Software Engineering*, v. 19, n. 3,
p. 214–230, 1993.

RIEHMANN, Patrick; HANFLER, Manfred; FROEHLICH, Bernd. **Interactive Sankey Diagrams.** In:
IEEE Symposium on Information Visualization (InfoVis), 2005, p. 233–240.

SCHMIDT, Mario. **The Sankey Diagram in Energy and Material Flow Management — Part I:
History; Part II: Methodology and Current Applications.** *Journal of Industrial Ecology*,
v. 12, n. 1–2, 2008.

SATYANARAYAN, Arvind; RUSSELL, Ryan; HOFFSWELL, Jane; HEER, Jeffrey. **Reactive Vega: A
Streaming Dataflow Architecture for Declarative Interactive Visualization.** *IEEE
Transactions on Visualization and Computer Graphics*, v. 22, n. 1, p. 659–668, 2016.

SATYANARAYAN, Arvind; MORITZ, Dominik; WONGSUPHASAWAT, Kanit; HEER, Jeffrey. **Vega-Lite: A
Grammar of Interactive Graphics.** *IEEE Transactions on Visualization and Computer
Graphics*, v. 23, n. 1, p. 341–350, 2017.

VEGA. **Vega — A Visualization Grammar (v5).** Documentação oficial. Disponível em:
<https://vega.github.io/vega/>. Acesso em: `[DATA]`.

MARSH-PATRICK, Daniel. **Deneb: Declarative Visualization in Power BI.** Documentação
oficial. Disponível em: <https://deneb-viz.github.io/>. Acesso em: `[DATA]`.

MICROSOFT. **Power Query M formula language reference.** Disponível em:
<https://learn.microsoft.com/en-us/powerquery-m/>. Acesso em: `[DATA]`.

EMPRESA DE PESQUISA ENERGÉTICA (EPE). **Balanço Energético Nacional.** Rio de Janeiro: EPE.
Disponível em:
<https://www.epe.gov.br/pt/publicacoes-dados-abertos/publicacoes/balanco-energetico-nacional>.
Acesso em: `[DATA]`.

UNIVERSIDADE FEDERAL FLUMINENSE. **Edital para submissão de projetos PIBITI/CNPq –
PIBINOVA/PDI/UFF 2025-2026.** Agência de Inovação (AGIR/PROPPI). Disponível em:
<https://agir.uff.br/wp-content/uploads/sites/351/2025/05/Edital-PIBITI-PIBINOVA-2025-2026-revisado.pdf>.
Acesso em: `[DATA]`.

---

## Agenda Acadêmica

*(Campos de marcação do formulário — preencher conforme sua situação. Reproduzidos aqui
apenas para conferência.)*

- **Comparecimento no Seminário de Iniciação à Inovação em outubro de 2026:**
  ☐ Sim  ☐ Não
  *(Item 5.6 do edital: a apresentação é **obrigação do bolsista**. O item 5.6.1 esclarece
  que **não há inscrição separada** — ela decorre da entrega deste Relatório Final. O item
  11.8 prevê que o não comparecimento sem justificativa pode acarretar inadimplência do
  orientador junto à PROPPI.)*
- **Justificativa de não comparecimento:** `[preencher apenas se marcou "Não"]`
- **Será necessário sigilo na apresentação?** ☐ Sim  ☐ Não
  *(Recomendação: **Não** — o projeto é uma ferramenta metodológica aberta, e a divulgação
  favorece a avaliação no critério "potencial de transferência de conhecimento para a
  sociedade". Marque "Sim" apenas se houver intenção de registro de programa de computador
  em andamento — nesse caso, converse antes com o orientador e com a AGIR.)*
- **O bolsista é de unidade da UFF fora de sede (fora de Niterói)?** ☐ Sim, cidade: ____  ☐ Não
- **Necessidade de transporte oferecido pela UFF:**
  ☐ Sim, o bolsista precisará
  ☐ Sim, o orientador precisará
  ☐ Sim, ambos precisarão
  ☐ Não, nenhum precisará

> **Observação do formulário:** as apresentações são feitas em slides, levados pelo bolsista
> em *pen drive*.

---

## Apêndice — Inventário de figuras e reconstrução do PDF

A versão entregável é **`Relatorio/Relatorio_Final_PIBITI_2025-2026.pdf`** (21 páginas),
gerada de `Relatorio/relatorio.typ`. Todas as nove figuras estão inseridas; não há mais
marcadores pendentes.

```bash
typst compile --root . Relatorio/relatorio.typ Relatorio/Relatorio_Final_PIBITI_2025-2026.pdf
typst watch   --root . Relatorio/relatorio.typ    # regenera a cada gravação
```

### Inventário

| # | Figura | Arquivo | Origem |
|---|---|---|---|
| 1 | Especificação desenhada à mão | `cadeias.png` | Referência de projeto (Canva) |
| 2 | Abas `Fuels` e `Techs` | `Figuras/fig-entrada-excel.png` | **Composto** de `Figura2a` + `Figura2b` |
| 3 | Dependências das nove consultas | `Figuras/Figura3.png` | Captura (58% da largura) |
| 4 | Fluxos reversos roteados | `Figuras/Figura4.png` | Captura |
| 5 | Algoritmo dos nós fantasmas | `Figuras/fig6_nos_fantasmas.svg` | Desenho vetorial |
| 6 | Estado íntegro | `Figuras/Figura6c.png` | Captura (90%) |
| 7 | Seleção de `BIO` | `Figuras/Figura6a.png` | Captura |
| 8 | Seleção de `COA` | `Figuras/Figura6b.png` | Captura (90%) |
| 9 | Panorama do diagrama | `Figuras/Figura7.png` | Captura |

`Figura2a.png` e `Figura2b.png` são insumos do composto e não entram no PDF diretamente.
O composto é reprodutível: ele normaliza as duas capturas para a mesma altura, rotula os
painéis com os nomes das colunas — a captura da aba `Techs` saiu sem cabeçalho — e marca em
vermelho as três linhas do `PROETA1`.

### Scripts de verificação

Dois controles foram usados e valem para qualquer alteração futura:

- **Conferência de referências cruzadas.** Extrai o texto do PDF, localiza a página real de
  cada legenda e compara com o que a Lista de Figuras/Tabelas declara. Foi o que revelou que
  o posicionamento flutuante (`placement: auto`) erra 8 das 12 referências; o documento usa
  fluxo inline, que acerta todas as 12.
- **Medição de vãos.** Mede a mancha branca no pé de cada página. Vãos restantes: páginas
  iniciais (resumo, sumário, listas), p. 7 e p. 12 (antes de figuras grandes) e a página
  final das referências. Nenhum vão acima de 8 cm no corpo.

### Decisões tomadas na diagramação

- **Dataset `Siglas`.** Todas as capturas do diagrama usam `RES_Dados_Siglas.xlsx`. O texto
  e as legendas referenciam siglas (`BIO`, `COA`, `PROETA1`) de forma consistente.
- **O diagrama ASCII do *pipeline* foi removido.** Duplicava o que a Figura 3 mostra a
  partir do próprio Power BI, e estourava a largura do bloco de código.
- **A seção "Fidelidade à especificação" foi removida.** Ela previa uma comparação lado a
  lado entre `cadeias.png` e a saída da ferramenta. Como a referência do Canva e a base real
  não descrevem a mesma topologia — a referência tem as demandas como colunas, a base as tem
  como tecnologias — a comparação não sustentaria a afirmação de fidelidade. `cadeias.png`
  permanece como Figura 1, no Diagnóstico, documentando o custo do caminho manual.
- **A Figura 9 é declarada panorama, não recorte legível.** É a captura mais ampla e seus
  rótulos ficam abaixo do limite de leitura em impressão; a legenda e o texto dizem que ela
  serve para dimensionar a extensão do traçado, e que o detalhe está nas figuras anteriores.

### Pendência

Nas referências de páginas web, o campo "Acesso em" foi removido, conforme decidido.
