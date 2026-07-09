let
    Fonte = fuel_map,
    
    // Limpeza Inicial
    #"Texto Limpo" = Table.TransformColumns(Fonte,{{"fuel", each Text.Proper(Text.Trim(_)), type text}}),

    // ===============================================================
    // SESSÃO DE REGRAS DE CORES (HERANÇA AUTOMÁTICA)
    // ===============================================================
    
    // 1. Descobre quem gera este combustível
    #"Merge Tech Origem" = Table.NestedJoin(#"Texto Limpo", {"fuel"}, tech_map, {"fuel_out"}, "DadosTech", JoinKind.LeftOuter),
    #"Expandir Fuel In" = Table.ExpandTableColumn(#"Merge Tech Origem", "DadosTech", {"fuel_in"}, {"Pai_Fuel_In"}),

    // 2. Descobre a cor do combustível pai
    #"Merge Cor Pai" = Table.NestedJoin(#"Expandir Fuel In", {"Pai_Fuel_In"}, #"Texto Limpo", {"fuel"}, "DadosCorPai", JoinKind.LeftOuter),
    #"Expandir Cor Pai" = Table.ExpandTableColumn(#"Merge Cor Pai", "DadosCorPai", {"color"}, {"Cor_Herdada"}),

    // 3. Aplica a Regra de Negócio
    #"Aplicar Regra Cores" = Table.AddColumn(#"Expandir Cor Pai", "NovaColor", each 
        if [stage] = 5 and [Cor_Herdada] <> null then 
            [Cor_Herdada] 
        else 
            [color]
    , type text),

    // 4. Limpeza
    #"Remover Colunas Auxiliares" = Table.RemoveColumns(#"Aplicar Regra Cores",{"color", "Pai_Fuel_In", "Cor_Herdada"}),
    #"Renomear para Color" = Table.RenameColumns(#"Remover Colunas Auxiliares",{{"NovaColor", "color"}}),

    // [CORREÇÃO CRÍTICA] Remove duplicatas geradas por combustíveis com múltiplas fontes (Ex: Carvão)
    // Se houver múltiplas origens, ele mantém a primeira encontrada, garantindo unicidade para o relacionamento.
    #"Remover Duplicatas Fuel" = Table.Distinct(#"Renomear para Color", {"fuel"}),

    // ===============================================================
    // FIM DA SESSÃO DE REGRAS DE CORES
    // ===============================================================

    // Agrupamento para contar itens por Stage
    // O Input agora é a tabela deduplicada #"Remover Duplicatas Fuel"
    #"Agrupado por Stage" = Table.Group(#"Remover Duplicatas Fuel", {"stage"}, {
        {"Conteudo", each _, type table [fuel=nullable text, stage=nullable number, color=nullable text]},
        {"Contagem", each Table.RowCount(_), Int64.Type}
    }),

    // ===============================================================
    // BLOCO 1: CÁLCULO DINÂMICO COM SALVAGUARDA DE ESPAÇO (LOOK-AHEAD)
    // ===============================================================
    
    #"Stages Ordenados" = Table.Sort(#"Agrupado por Stage", {{"stage", Order.Ascending}}),
    #"Add Index Stage" = Table.AddIndexColumn(#"Stages Ordenados", "Idx_Stage", 0, 1, Int64.Type),

    // PARÂMETROS
    GapBasico = 400,
    PixelsPorItem = 30,
    
    #"Add Largura" = Table.AddColumn(#"Add Index Stage", "LarguraDesteStage", each 
        let
            MinhaContagem = [Contagem],
            ProximaContagem = try #"Add Index Stage"[Contagem]{[Idx_Stage] + 1} otherwise 0,
            MaiorContagem = List.Max({MinhaContagem, ProximaContagem}),
            LarguraCalculada = GapBasico + (MaiorContagem * PixelsPorItem)
        in
            LarguraCalculada, type number
    ),

    ListaLarguras = #"Add Largura"[LarguraDesteStage],
    PosicoesAcumuladas = List.Accumulate(ListaLarguras, {150}, (estado, atual) => estado & {List.Last(estado) + atual}),
    PosicoesFinais = List.RemoveLastN(PosicoesAcumuladas, 1),

    #"Tabela Com X Base" = Table.FromColumns(
        Table.ToColumns(#"Add Largura") & {PosicoesFinais},
        Table.ColumnNames(#"Add Largura") & {"X_Base_Stage"}
    ),

    // ===============================================================
    // BLOCO 2: ESPALHAMENTO INTERNO E FINALIZAÇÃO
    // ===============================================================

    #"Index Adicionado" = Table.TransformColumns(#"Tabela Com X Base", {
        {"Conteudo", (t) => Table.AddIndexColumn(t, "IndiceLocal", 1, 1), type table}
    }),
    
    #"Expandido Conteudo" = Table.ExpandTableColumn(#"Index Adicionado", "Conteudo", 
        {"fuel", "IndiceLocal", "color"}, 
        {"fuel", "IndiceLocal", "color"}
    ),

    #"Stage Visual Calculado" = Table.AddColumn(#"Expandido Conteudo", "Desvio_Visual", each 
        if [Contagem] = 1 then -0.30 
        else (([IndiceLocal] / ([Contagem] + 1)) - 0.5) * 0.9 
    , type number),

    #"X Calculado" = Table.AddColumn(#"Stage Visual Calculado", "x_fuel", each Number.Round(
        [X_Base_Stage] + 
        ([Desvio_Visual] * ([Contagem] * 30 + 150)), 
        0
    ), type number),

    #"Kind Adicionado" = Table.AddColumn(#"X Calculado", "kind", each "fuel"),
    
    // ===============================================================
    // BLOCO 3: CRIAÇÃO DO ID GLOBAL PARA SWIMLANES (RAIAS)
    // ===============================================================
    
    #"Ordenado Para ID" = Table.Sort(#"Kind Adicionado",{{"stage", Order.Ascending}, {"fuel", Order.Ascending}}),
    #"ID Combustivel Adicionado" = Table.AddIndexColumn(#"Ordenado Para ID", "Fuel_Global_ID", 1, 1, Int64.Type),

    #"Colunas Finais" = Table.SelectColumns(#"ID Combustivel Adicionado",{"fuel", "stage", "x_fuel", "kind", "color", "Fuel_Global_ID"})
in
    #"Colunas Finais"
