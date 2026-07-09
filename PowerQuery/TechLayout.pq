let
    Fonte = tech_map,
    
    // 1. PREPARAÇÃO
    CheckHidden = if Table.HasColumns(Fonte, "IsHidden") then Fonte else Table.AddColumn(Fonte, "IsHidden", each false),
    #"Colunas Iniciais" = Table.SelectColumns(CheckHidden,{"tech", "fuel_in", "fuel_out", "IsHidden"}),
    #"Kind Adicionado" = Table.AddColumn(#"Colunas Iniciais", "kind", each "tech"),

    // =======================================================
    // BLOCO 2: UNIFICAÇÃO & HERANÇA DE COR
    // =======================================================
    
    #"Merge IN" = Table.NestedJoin(#"Kind Adicionado", {"fuel_in"}, FuelLayout, {"fuel"}, "DadosIN", JoinKind.LeftOuter),
    #"Exp IN" = Table.ExpandTableColumn(#"Merge IN", "DadosIN", 
        {"stage", "x_fuel", "Fuel_Global_ID"}, 
        {"stage_in", "x_fuel_in", "ID_Input_Original"}
    ),

    #"Merge OUT" = Table.NestedJoin(#"Exp IN", {"fuel_out"}, FuelLayout, {"fuel"}, "DadosOUT", JoinKind.LeftOuter),
    #"Exp OUT" = Table.ExpandTableColumn(#"Merge OUT", "DadosOUT", 
        {"stage", "x_fuel", "color"}, 
        {"stage_out", "x_fuel_out", "color_out"}
    ),

    #"Agrupar Tech" = Table.Group(#"Exp OUT", {"tech"}, {
        {"Max_Stage_In", each List.Max([stage_in]), type number},
        {"Min_Stage_Out", each List.Min([stage_out]), type number},
        {"ID_Raia_Mestra", each Number.Round(List.Average(List.Select([ID_Input_Original], each _ <> null)), 0), Int64.Type},
        {"tech_color_calculated", each 
            let 
                ListaCores = List.RemoveNulls([color_out]),
                CorFinal = if List.IsEmpty(ListaCores) then "#555555" else List.First(ListaCores)
            in 
                CorFinal, type text
        },
        {"TodasLinhas", each _, type table}
    }),
    
    #"Expandir Techs" = Table.ExpandTableColumn(#"Agrupar Tech", "TodasLinhas", 
        {"fuel_in", "fuel_out", "kind", "IsHidden", "x_fuel_in", "x_fuel_out", "color_out"},
        {"fuel_in", "fuel_out", "kind", "IsHidden", "x_fuel_in", "x_fuel_out", "color_out"}
    ),
    
    #"Recuperar Cor In" = Table.NestedJoin(#"Expandir Techs", {"fuel_in"}, FuelLayout, {"fuel"}, "CorTab", JoinKind.LeftOuter),
    #"Exp Cor In" = Table.ExpandTableColumn(#"Recuperar Cor In", "CorTab", {"color"}, {"color_in"}),

    // =======================================================
    // BLOCO 3: CÁLCULO GEOMÉTRICO X (COM ALINHAMENTO DE PRODUCERS)
    // =======================================================

    StatsPorEstagio = Table.Group(FuelLayout, {"stage"}, {
        {"ParedeDireita", each List.Max([x_fuel]), type number}, 
        {"ParedeEsquerda", each List.Min([x_fuel]), type number}
    }),

    // 1. Índices
    #"Add Indexes" = Table.AddColumn(#"Exp Cor In", "Indices", each [
        Prev = if [Min_Stage_Out] <> null then [Min_Stage_Out] - 1 else null,
        Next = if [Max_Stage_In] <> null then [Max_Stage_In] + 1 else null
    ]),
    #"Expand Indexes" = Table.ExpandRecordColumn(#"Add Indexes", "Indices", {"Prev", "Next"}, {"Prev_Stage_Out", "Next_Stage_In"}),

    // 2. Paredes
    #"Merge Wall IN" = Table.NestedJoin(#"Expand Indexes", {"Max_Stage_In"}, StatsPorEstagio, {"stage"}, "StatsIn", JoinKind.LeftOuter),
    #"Exp Wall IN" = Table.ExpandTableColumn(#"Merge Wall IN", "StatsIn", {"ParedeDireita", "ParedeEsquerda"}, {"ParedeDireita_IN", "ParedeEsquerda_IN"}),

    #"Merge Wall OUT" = Table.NestedJoin(#"Exp Wall IN", {"Min_Stage_Out"}, StatsPorEstagio, {"stage"}, "StatsOut", JoinKind.LeftOuter),
    #"Exp Wall OUT" = Table.ExpandTableColumn(#"Merge Wall OUT", "StatsOut", {"ParedeEsquerda"}, {"ParedeEsquerda_OUT"}),

    // Anterior ao Output
    #"Merge Wall PREV" = Table.NestedJoin(#"Exp Wall OUT", {"Prev_Stage_Out"}, StatsPorEstagio, {"stage"}, "StatsPrev", JoinKind.LeftOuter),
    #"Exp Wall PREV" = Table.ExpandTableColumn(#"Merge Wall PREV", "StatsPrev", {"ParedeDireita"}, {"ParedeDireita_PREV_OUT"}),

    // Próximo ao Input
    #"Merge Wall NEXT" = Table.NestedJoin(#"Exp Wall PREV", {"Next_Stage_In"}, StatsPorEstagio, {"stage"}, "StatsNext", JoinKind.LeftOuter),
    #"Exp Wall NEXT" = Table.ExpandTableColumn(#"Merge Wall NEXT", "StatsNext", {"ParedeEsquerda"}, {"ParedeEsquerda_NEXT_IN"}),

    // 3. Cálculo Mestre X
    #"x_tech Calculado" = Table.AddColumn(#"Exp Wall NEXT", "x_tech", each Number.Round(
        if [Max_Stage_In] <> null and [Min_Stage_Out] <> null then 
            // CASO 1: Tem Input e Output
            if [Max_Stage_In] >= [Min_Stage_Out] then
                // 1.1 Backflow
                if [ParedeDireita_PREV_OUT] <> null then ([ParedeDireita_PREV_OUT] + [ParedeEsquerda_OUT]) / 2 
                else [ParedeEsquerda_OUT] - 200 
            else
                // 1.2 Forward
                if [ParedeEsquerda_NEXT_IN] <> null then ([ParedeDireita_IN] + [ParedeEsquerda_NEXT_IN]) / 2
                else [ParedeDireita_IN] + 150
        
        else if [Max_Stage_In] <> null and [Min_Stage_Out] = null then
            // CASO 2: Só tem Input
            if [ParedeEsquerda_NEXT_IN] <> null then ([ParedeDireita_IN] + [ParedeEsquerda_NEXT_IN]) / 2
            else [ParedeDireita_IN] + 150
            
        else if [Max_Stage_In] = null and [Min_Stage_Out] <> null then
            // CASO 3: Só tem Output
            if [ParedeDireita_PREV_OUT] <> null then ([ParedeDireita_PREV_OUT] + [ParedeEsquerda_OUT]) / 2
            else [ParedeEsquerda_OUT] - 150
        else 
            0
    , 0), type number),

    #"Add IsBackflow" = Table.AddColumn(#"x_tech Calculado", "IsBackflow", each 
        if [Max_Stage_In] <> null and [Min_Stage_Out] <> null and [Max_Stage_In] >= [Min_Stage_Out] then true else false
    , type logical),

    // =======================================================
    // BLOCO 4: CÁLCULO DO EIXO Y (RAIAS ELÁSTICAS / VARIABLE HEIGHT SWIMLANES)
    // =======================================================
    
    // 1. Preparação Básica
    #"Tratar Nulos ID" = Table.AddColumn(#"Add IsBackflow", "Fuel_Global_ID", each if [ID_Raia_Mestra] = null then 999 else [ID_Raia_Mestra], Int64.Type),
    #"Add X Grid" = Table.AddColumn(#"Tratar Nulos ID", "x_grid", each Number.Round([x_tech] / 50, 0) * 50, Int64.Type),
    
    // O Group ID continua importante para identificar a Raia
    #"Add Y Group ID" = Table.AddColumn(#"Add X Grid", "Y_Group_ID", each [Fuel_Global_ID], Int64.Type),

    // -----------------------------------------------------------------------
    // GERAÇÃO DE NÓS FANTASMAS (MANTIDO E CRUCIAL)
    // Os fantasmas agora servem para "inflar" a raia onde a linha passa
    // -----------------------------------------------------------------------
    
    ListaGridsOcupados = List.Buffer(List.Distinct(Table.SelectRows(#"Add Y Group ID", each [kind]="tech")[x_grid])),

    FiltraLongHaul = Table.SelectRows(#"Add Y Group ID", each 
        [x_fuel_out] <> null and [x_tech] <> null and Number.Abs([x_fuel_out] - [x_tech]) > 70
    ),

    GeraGhostsGeometricos = Table.AddColumn(FiltraLongHaul, "GhostGrid", each 
        let
            Start = List.Min({[x_tech], [x_fuel_out]}),
            End = List.Max({[x_tech], [x_fuel_out]}),
            GridsNoCaminho = List.Select(ListaGridsOcupados, (g) => g > (Start + 25) and g < (End - 25))
        in
            GridsNoCaminho
    ),

    ExpandGhosts = Table.ExpandListColumn(GeraGhostsGeometricos, "GhostGrid"),
    GhostsValidos = Table.SelectRows(ExpandGhosts, each [GhostGrid] <> null),

    TabelaFantasmas = Table.SelectColumns(GhostsValidos, {"tech", "Y_Group_ID", "Fuel_Global_ID", "GhostGrid"}),
    RenomeiaFantasmas = Table.RenameColumns(TabelaFantasmas, {{"GhostGrid", "x_grid"}}),
    
    TechFantasmaID = Table.TransformColumns(RenomeiaFantasmas, {
        {"tech", each _ & "_GHOST_" & Text.NewGuid(), type text}
    }),

    TabelaRealFlag = Table.SelectColumns(Table.AddColumn(#"Add Y Group ID", "IsGhost", each false), {"tech", "Y_Group_ID", "x_grid", "Fuel_Global_ID", "IsGhost"}),
    TabelaGhostFlag = Table.AddColumn(TechFantasmaID, "IsGhost", each true),
    
    // Tabela Mestra contendo TUDO (Caixas + Linhas/Fantasmas)
    TabelaCombinada = Table.Combine({TabelaRealFlag, TabelaGhostFlag}),

    // -----------------------------------------------------------------------
    // NOVA LÓGICA: CÁLCULO DA ESPESSURA VARIÁVEL DE CADA RAIA (CORRIGIDA)
    // -----------------------------------------------------------------------

    // [CORREÇÃO 1] Agrupa e conta itens ÚNICOS (Distinct) para não inflar a altura com múltiplas saídas
    #"Stats: Densidade Local" = Table.Group(TabelaCombinada, {"Fuel_Global_ID", "x_grid"}, {
        {"QtdItens", each Table.RowCount(Table.Distinct(_, {"tech"})), Int64.Type}
    }),

    // 2. Descobre qual é o PIOR CASO (Max Height) para cada Combustível
    #"Stats: Altura da Raia" = Table.Group(#"Stats: Densidade Local", {"Fuel_Global_ID"}, {
        {"Altura_Reservada", each List.Max([QtdItens]), Int64.Type}
    }),

    // 3. Ordena as Raias
    #"Raias Ordenadas" = Table.Sort(#"Stats: Altura da Raia", {{"Fuel_Global_ID", Order.Ascending}}),

    // 4. Cria o "Y Base" acumulado
    ListaAlturas = #"Raias Ordenadas"[Altura_Reservada],
    Y_Iniciais = List.Accumulate(ListaAlturas, {1}, (estado, atual) => estado & {List.Last(estado) + atual}),
    Y_Finais_Clean = List.RemoveLastN(Y_Iniciais, 1),

    #"Mapa de Raias Y" = Table.FromColumns(
        Table.ToColumns(#"Raias Ordenadas") & {Y_Finais_Clean},
        Table.ColumnNames(#"Raias Ordenadas") & {"Y_Base_Raia"}
    ),

    // -----------------------------------------------------------------------
    // APLICAÇÃO DO POSICIONAMENTO (CORRIGIDA - SINGLE BOX)
    // -----------------------------------------------------------------------

    // Junta a informação de onde começa cada raia de volta na tabela de dados
    #"Merge Y Base" = Table.NestedJoin(TabelaCombinada, {"Fuel_Global_ID"}, #"Mapa de Raias Y", {"Fuel_Global_ID"}, "DadosRaia", JoinKind.LeftOuter),
    #"Expande Y Base" = Table.ExpandTableColumn(#"Merge Y Base", "DadosRaia", {"Y_Base_Raia"}, {"Y_Base_Raia"}),

    // Agora fazemos o "Tetris"
    #"Agrupado Por X e Fuel" = Table.Group(#"Expande Y Base", {"x_grid", "Fuel_Global_ID"}, {{"Conteudo", each _, type table}}),

    // [CORREÇÃO 2] Lógica de Indexação Única
    #"Y Calculado Final" = Table.TransformColumns(#"Agrupado Por X e Fuel", {{"Conteudo", (t) => 
            let 
                // A. Isola apenas os Techs ÚNICOS para calcular a posição (evita duplicatas)
                DistinctTechs = Table.Distinct(t, {"tech"}),

                // B. Ordena: Caixas Reais primeiro, depois Fantasmas
                Ordenado = Table.Sort(DistinctTechs, {{"IsGhost", Order.Ascending}, {"tech", Order.Ascending}}),
                
                // C. Atribui o Índice Y apenas aos itens únicos
                Indexado = Table.AddIndexColumn(Ordenado, "Indice_Interno", 0, 1),
                
                // D. Calcula o Y Final (Base + Posição)
                CalcY = Table.AddColumn(Indexado, "y_tech_idx_calculado", each [Y_Base_Raia] + [Indice_Interno]),
                
                // E. Mapeia de volta para a tabela original 't' (Join)
                // Isso garante que todas as 3 saídas da mesma Tech recebam o MESMO Y
                MapaY = Table.SelectColumns(CalcY, {"tech", "y_tech_idx_calculado"}),
                JoinBack = Table.Join(t, "tech", MapaY, "tech", JoinKind.Inner),
                
                Renomeado = Table.RenameColumns(JoinBack, {{"y_tech_idx_calculado", "y_tech_idx"}})
            in 
                Renomeado
    }}),
    
    #"Techs Com Y" = Table.ExpandTableColumn(#"Y Calculado Final", "Conteudo", {"tech", "y_tech_idx"}, {"tech", "y_tech_idx"}),

    // =======================================================
    // BLOCO 5: FINALIZAÇÃO (Merge de volta)
    // =======================================================
    
    // Merge de volta com a original para pegar os metadados e descartar as linhas de ghosts
    #"Merge Y Automatico" = Table.NestedJoin(#"Add Y Group ID", {"tech"}, #"Techs Com Y", {"tech"}, "DadosY", JoinKind.LeftOuter),
    #"Expandido Y" = Table.ExpandTableColumn(#"Merge Y Automatico", "DadosY", {"y_tech_idx"}, {"y_tech_idx"}),

    #"Offsets Zerados" = Table.AddColumn(#"Expandido Y", "in_offset", each 0, Int64.Type),
    #"Offsets Zerados 2" = Table.AddColumn(#"Offsets Zerados", "out_offset", each 0, Int64.Type),

    #"Merge Final X_IN" = Table.NestedJoin(#"Offsets Zerados 2", {"fuel_in"}, FuelLayout, {"fuel"}, "X_IN_Tab", JoinKind.LeftOuter),
    #"Exp Final X_IN" = Table.ExpandTableColumn(#"Merge Final X_IN", "X_IN_Tab", {"x_fuel"}, {"x_in"}),
    
    #"Merge Final X_OUT" = Table.NestedJoin(#"Exp Final X_IN", {"fuel_out"}, FuelLayout, {"fuel"}, "X_OUT_Tab", JoinKind.LeftOuter),
    #"Exp Final X_OUT" = Table.ExpandTableColumn(#"Merge Final X_OUT", "X_OUT_Tab", {"x_fuel"}, {"x_out"}),

    #"Resultado Final" = Table.SelectColumns(#"Exp Final X_OUT", 
        {"tech", "fuel_in", "fuel_out", "kind", "x_tech", "y_tech_idx", "in_offset", "out_offset", "x_in", "x_out", "color_in", "color_out", "IsHidden", "tech_color_calculated", "IsBackflow"}
    )
in
    #"Resultado Final"
