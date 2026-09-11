# -*- coding: utf-8 -*-
"""Conteudo dimensionado para as caixas do formulario."""

TITULO = ("DIAGRAMA DINÂMICO DE FLUXO ENERGÉTICO (DDFE): GERAÇÃO AUTOMÁTICA DE DIAGRAMAS "
          "DE SISTEMA ENERGÉTICO DE REFERÊNCIA (RES) A PARTIR DE DADOS TABULARES, EM POWER BI")

RESUMO = """Modelos de planejamento energético de longo prazo, como os construídos em OSeMOSYS, MESSAGE ou TIMES, são descritos por um Diagrama de Fluxo de Energia de Referência (Reference Energy System, RES): um grafo dirigido em que combustíveis e vetores energéticos são conectados por tecnologias de extração, conversão, transporte e uso final. Esse diagrama é a especificação visual do modelo, mas na prática corrente é desenhado à mão em ferramentas de diagramação genéricas, o que o torna caro de produzir e faz com que desatualize a cada alteração do modelo.

Este projeto desenvolveu o Diagrama Dinâmico de Fluxo Energético (DDFE): uma ferramenta que gera automaticamente o diagrama RES completo, com posições, roteamento de linhas, cores e interatividade, a partir de duas tabelas que o próprio modelador já mantém. Não há nenhuma coordenada desenhada manualmente.

A solução é implementada sobre a pilha Excel, Power Query (linguagem M) e Deneb (Vega v5), dentro do Microsoft Power BI, e divide-se em duas camadas: um back-end geométrico em M, que resolve o layout de grafo em camadas sob restrição semântica de camada, e um front-end declarativo em Vega, que renderiza as coordenadas pré-calculadas e implementa destaque interativo. As contribuições técnicas centrais são a alocação do eixo horizontal por look-ahead de densidade, a alocação do eixo vertical por raias elásticas com nós fantasmas, e o roteamento explícito de fluxos retroalimentados.

A ferramenta foi validada sobre um sistema energético nacional estilizado com 70 combustíveis em 5 estágios e 101 tecnologias, além de testes de esforço com topologias aleatórias. O resultado é genérico: qualquer base relacional que siga a matriz origem-destino padronizada é renderizada sem reconfiguração. Todo o código está versionado como texto auditável, com documentação de usuário e de desenvolvedor."""

DIAGNOSTICO = """Ferramentas de modelagem energética representam o setor energético como uma rede de fluxos. A formulação do OSeMOSYS e das famílias MARKAL/TIMES parte da mesma abstração: combustíveis, e tecnologias que os consomem e produzem, organizados por estágio da cadeia energética. O RES não é ilustração: é o contrato de especificação entre o modelador, o orientador e o tomador de decisão.

Um RES de porte realista tem da ordem de 170 nós e mais de 100 arestas. Desenhado à mão, consome dias de trabalho, e toda alteração estrutural do modelo invalida o desenho: o diagrama congela numa versão antiga e passa a divergir do modelo que deveria documentar. Por estar em arquivo separado da base de dados, também não oferece garantia de fidelidade.

A geração automática de RES não é território virgem. O comando otoole viz res, da suíte oficial do ecossistema OSeMOSYS, monta o grafo com networkx e o desenha com o motor dot do Graphviz. Resolve o custo de produção, mas a coluna é inferida da topologia pelo algoritmo, e não do estágio declarado nos dados; os combustíveis viram pontos sem rótulo; e a saída é imagem estática, sem clique ou rastreamento. Visuais de Sankey de plataformas de BI têm os mesmos defeitos e ainda não tratam fluxos reversos.

A lacuna atacada não é gerar o RES automaticamente, e sim gerar um RES em que a coluna seja imposta pelo dado semântico, os combustíveis sejam eixos rotulados, os fluxos reversos sejam roteados e o resultado seja interrogável, dentro da plataforma de BI em que a análise já vive."""

SOLUCOES = """A decisão arquitetural central foi abandonar os visuais de Sankey prontos e construir um motor próprio em duas camadas. O back-end, em Power Query (linguagem M), lê a topologia, aloca coordenadas absolutas, resolve colisões e classifica arestas. O front-end, em Deneb/Vega v5, recebe uma tabela achatada com as coordenadas já calculadas e apenas desenha, além de gerenciar a interação. Isso permitiu desenvolver e depurar cada camada isoladamente.

A entrada são duas abas de planilha: Fuels, com fuel, stage e color; e Techs, com tech, fuel_in e fuel_out. Múltiplas entradas ou saídas de uma tecnologia são expressas como múltiplas linhas de mesmo identificador, o que mantém a planilha editável por quem não programa. O back-end tem nove consultas encadeadas e 556 linhas de M.

Três algoritmos sustentam o layout. No eixo horizontal dos combustíveis, a largura de cada faixa usa look-ahead de densidade, considerando o próprio estágio e o seguinte. No eixo horizontal das tecnologias, cada estágio é reduzido a duas paredes e a posição é resolvida por três casos, com inversão das referências espaciais quando se detecta fluxo reverso. No eixo vertical, conexões longas geram nós fantasmas nas colunas ocupadas que atravessam; eles entram na contagem de densidade, elevam a altura reservada da raia e liberam a linha por onde a conexão passa. O espaço é negociado na alocação, e não no roteamento, o que permite expressar tudo como transformações de tabela.

A interação usa nove conjuntos de dados e dezesseis marcas. Cada elemento clicável é desenhado duas vezes: uma marca visual de 2 pixels e uma de captura invisível de 45 pixels. Cinco sinais reativos isolam cadeias por cor, com destaque por opacidade. Todo o código foi externalizado para arquivos-texto versionados, com protocolo de sincronização e auditoria de divergência."""

RESULTADOS = """Foi entregue uma ferramenta funcional, documentada e versionada que gera diagramas RES completos e interativos a partir de duas tabelas, sem nenhuma coordenada desenhada manualmente. A validação usou um sistema energético nacional estilizado com 70 combustíveis em 5 estágios, 101 tecnologias e 106 arestas, incluindo 25 tecnologias-fonte e 4 fluxos reversos roteados automaticamente.

O mesmo diagrama desenhado à mão representa trabalho da ordem de dias; com a ferramenta, alterar uma linha na planilha e atualizar reconstrói tudo em segundos. Mais relevante que o ganho na primeira produção é o da manutenção: o custo de manter o diagrama sincronizado com o modelo cai a praticamente zero, o que elimina a causa raiz do problema diagnosticado.

A distinção em relação à arte prévia está em quem decide a coluna: em layouts do tipo dot ela é derivada da topologia pelo algoritmo; aqui é imposta pelo campo de estágio declarado nos dados. Na revisão realizada não foi identificada implementação equivalente nativa em plataforma de BI.

A principal dificuldade foi a limitação da linguagem M para algoritmos de grafo: sem estado mutável e sem laços imperativos, todo o layout precisou ser reexpresso como agrupamentos, acumulações e junções de tabela. Essa restrição produziu a solução dos nós fantasmas. Como trabalhos futuros destacam-se a parametrização das constantes de layout, a reativação otimizada da rastreabilidade, o dimensionamento das linhas por volume de fluxo e o uso do grafo já construído para emitir diagnósticos automáticos de consistência do modelo."""

REFERENCIAS = """HOWELLS, M. et al. OSeMOSYS: The Open Source Energy Modeling System. Energy Policy, v. 39, n. 10, p. 5850-5870, 2011.
BARNES, T.; USHER, W. otoole: OSeMOSYS Tools for Energy Work. Journal of Open Source Software, v. 8, n. 92, art. 5511, 2023.
LOULOU, R. et al. Documentation for the TIMES Model. ETSAP, 2005.
SUGIYAMA, K.; TAGAWA, S.; TODA, M. Methods for Visual Understanding of Hierarchical System Structures. IEEE Trans. on Systems, Man, and Cybernetics, v. 11, n. 2, p. 109-125, 1981.
GANSNER, E. R. et al. A technique for drawing directed graphs. IEEE Trans. on Software Engineering, v. 19, n. 3, p. 214-230, 1993.
RIEHMANN, P.; HANFLER, M.; FROEHLICH, B. Interactive Sankey diagrams. IEEE InfoVis, p. 233-240, 2005.
SCHMIDT, M. The Sankey diagram in energy and material flow management. Journal of Industrial Ecology, v. 12, n. 1-2, 2008.
ALEMASOOM, H. et al. EnergyViz: an interactive system for visualization of energy systems. The Visual Computer, v. 32, n. 3, p. 403-413, 2016.
SATYANARAYAN, A. et al. Reactive Vega: a streaming dataflow architecture for declarative interactive visualization. IEEE TVCG, v. 22, n. 1, p. 659-668, 2016.
MARSH-PATRICK, D. Deneb: Declarative Visualization in Power BI. Documentação oficial.
MICROSOFT. Power Query M formula language reference. Documentação oficial."""
