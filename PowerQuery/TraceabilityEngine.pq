let
    // =======================================================
    // 1. PREPARAÇÃO DOS DADOS
    // =======================================================
    Fonte = TechLayout,
    
    // Lista de Arestas (Conexões)
    Arestas1 = Table.SelectColumns(Fonte, {"fuel_in", "tech"}),
    Ren1 = Table.RenameColumns(Arestas1, {{"fuel_in", "Source"}, {"tech", "Target"}}),
    
    Arestas2 = Table.SelectColumns(Fonte, {"tech", "fuel_out"}),
    Ren2 = Table.RenameColumns(Arestas2, {{"tech", "Source"}, {"fuel_out", "Target"}}),
    
    // Tabela única de arestas, removendo nulos
    EdgesRaw = Table.Distinct(Table.Combine({Ren1, Ren2})),
    Edges = Table.SelectRows(EdgesRaw, each [Source] <> null and [Target] <> null),

    // =======================================================
    // 2. CRIAÇÃO DOS "HASH MAPS" (REGISTROS DE BUSCA RÁPIDA)
    // =======================================================
    
    // Função auxiliar para criar o Mapa (Dicionário)
    CriarMapa = (Tabela as table, ColChave as text, ColValor as text) =>
        let
            Agrupado = Table.Group(Tabela, {ColChave}, {{"Destinos", each Table.Column(_, ColValor)}}),
            Registros = Record.FromList(Agrupado[Destinos], Table.Column(Agrupado, ColChave))
        in
            Registros,

    // Mapa DOWNSTREAM: Quem é o Pai -> Lista de Filhos
    Map_Down = CriarMapa(Edges, "Source", "Target"),
    
    // Mapa UPSTREAM: Quem é o Filho -> Lista de Pais
    Map_Up = CriarMapa(Edges, "Target", "Source"),

    // =======================================================
    // 3. FUNÇÃO DE RASTREAMENTO (AGORA INSTANTÂNEA)
    // =======================================================
    
    FindPath = (StartNode as text, Map as record) =>
        let
            // Loop Recursivo usando Record.Field (Lookup direto, sem scan de tabela)
            Loop = List.Generate(
                () => [CurrentNodes = {StartNode}, AllNodes = {}, Level = 0],
                each not List.IsEmpty([CurrentNodes]) and [Level] < 20,
                each [
                    // AQUI ESTÁ A MUDANÇA: Busca direta no Registro com tratamento de erro
                    NextNodes = List.Combine(
                        List.Transform([CurrentNodes], each try Record.Field(Map, _) otherwise {})
                    ),
                    // Remove duplicatas e nós já visitados
                    UniqueNext = List.Distinct(List.Difference(NextNodes, [AllNodes])),
                    
                    CurrentNodes = UniqueNext,
                    AllNodes = List.Combine({[AllNodes], UniqueNext}),
                    Level = [Level] + 1
                ],
                each [AllNodes]
            ),
            Result = List.Combine(Loop)
        in
            Result,

    // =======================================================
    // 4. EXECUÇÃO FINAL
    // =======================================================
    
    // Lista de todos os nós únicos
    AllNodesList = List.Distinct(List.Combine({Edges[Source], Edges[Target]})),
    TableNodes = Table.FromList(AllNodesList, Splitter.SplitByNothing(), {"NodeID"}),

    // Calcula Ancestrais usando o Mapa UP
    #"Com Ancestrais" = Table.AddColumn(TableNodes, "Ancestors_Path", each 
        "|" & Text.Combine(FindPath([NodeID], Map_Up), "|") & "|"
    ),

    // Calcula Descendentes usando o Mapa DOWN
    #"Com Descendentes" = Table.AddColumn(#"Com Ancestrais", "Descendants_Path", each 
        "|" & Text.Combine(FindPath([NodeID], Map_Down), "|") & "|"
    )
in
    #"Com Descendentes"
