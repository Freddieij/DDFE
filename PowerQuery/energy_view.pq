let
    // 1. Junta as tabelas
    Fonte = Table.Combine({FuelLayout, TechLayout}),

    // 2. CÁLCULO DOS LIMITES GLOBAIS
    LarguraNecessaria = List.Max(FuelLayout[x_fuel]),
    AlturaNecessaria = List.Max(TechLayout[y_tech_idx]),

    // 3. Adiciona esses valores em TODAS as linhas
    #"Adicionado MaxX" = Table.AddColumn(Fonte, "GlobalMaxX", each LarguraNecessaria),
    #"Adicionado MaxY" = Table.AddColumn(#"Adicionado MaxX", "GlobalMaxY", each AlturaNecessaria), 

    // --- NOVO BLOCO: MERGE DE RASTREABILIDADE ---
    
    // --- BLOCO COMENTADO PARA PERFORMANCE ---
    // #"Key Criada" = Table.AddColumn(#"Adicionado MaxY", "JoinKey", each if [kind]="fuel" then [fuel] else [tech]),
    // #"Merge Traceability" = Table.NestedJoin(#"Key Criada", {"JoinKey"}, TraceabilityEngine, {"NodeID"}, "TraceData", JoinKind.LeftOuter),
    // #"Expandido Trace" = Table.ExpandTableColumn(#"Merge Traceability", "TraceData", {"Ancestors_Path", "Descendants_Path"}, {"Ancestors_Path", "Descendants_Path"}),
    // #"Limpeza Final" = Table.RemoveColumns(#"Expandido Trace", {"JoinKey"}),
    // ----------------------------------------

    // --- CORREÇÃO: O Input deste passo agora é #"Adicionado MaxY" (Pulamos a Limpeza Final) ---
    #"Tipo Alterado Final" = Table.TransformColumnTypes(#"Adicionado MaxY",{  // <--- MUDE AQUI DE #"Limpeza Final" PARA #"Adicionado MaxY"
        {"x_fuel", Int64.Type},
        {"stage", Int64.Type},
        {"x_tech", Int64.Type},
        {"y_tech_idx", Int64.Type},
        {"in_offset", Int64.Type},
        {"out_offset", Int64.Type},
        {"x_in", Int64.Type},
        {"x_out", Int64.Type},
        {"GlobalMaxX", Int64.Type},
        {"GlobalMaxY", Int64.Type},
        {"color", type text},
        {"color_in", type text},
        {"color_out", type text},
        {"IsHidden", type logical},
        {"tech_color_calculated", type text},
        {"IsBackflow", type logical}
    })
in
    #"Tipo Alterado Final"
