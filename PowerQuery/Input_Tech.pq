let
    Fonte = Excel.Workbook(File.Contents(CaminhoArquivo), null, true),
    SheetTechs = Fonte{[Item="Techs",Kind="Sheet"]}[Data],
    #"Cabeçalhos Promovidos" = Table.PromoteHeaders(SheetTechs, [PromoteAllScalars=true]),
    #"Colunas Selecionadas" = Table.SelectColumns(#"Cabeçalhos Promovidos",{"tech", "fuel_in", "fuel_out"}),

    // 1. LIMPEZA E PADRONIZAÇÃO (Essencial para os Joins funcionarem)
    #"Texto Padronizado" = Table.TransformColumns(#"Colunas Selecionadas",{
        {"fuel_in", each if _ = null then null else Text.Proper(Text.Clean(Text.Trim(_))), type text},
        {"fuel_out", each if _ = null then null else Text.Proper(Text.Clean(Text.Trim(_))), type text},
        {"tech", each if _ = null then null else Text.Clean(Text.Trim(_)), type text}
    }),

    // 2. LÓGICA DE HUB PARA LINKS
    // Em vez de IndexLinha (que separa tudo), usamos fuel_in (que agrupa por origem)
    #"Gerar IDs de Hub" = Table.AddColumn(#"Texto Padronizado", "tech_tratado", each 
        if [tech] = null or [tech] = "" then 
            if [fuel_in] <> null then 
                "LINK_HUB_" & [fuel_in]  // Cria um Hub único por Combustível
            else 
                "LINK_ORFAO_" & Text.NewGuid() // Fallback para casos estranhos
        else 
            [tech]
    , type text),

    // 3. FINALIZAÇÃO
    #"Selecionar Finais" = Table.SelectColumns(#"Gerar IDs de Hub", {"tech_tratado", "fuel_in", "fuel_out"}),
    #"Renomear Final" = Table.RenameColumns(#"Selecionar Finais", {{"tech_tratado", "tech"}}),

    // Identifica Link
    #"Add IsHidden" = Table.AddColumn(#"Renomear Final", "IsHidden", each Text.StartsWith([tech], "LINK_HUB_") or Text.StartsWith([tech], "LINK_ORFAO_"), type logical)
in
    #"Add IsHidden"
