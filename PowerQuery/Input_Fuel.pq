let
    // 1. Conecta ao arquivo Excel usando o Parâmetro
    Fonte = Excel.Workbook(File.Contents(CaminhoArquivo), null, true),
    
    // 2. Navega até a aba 'Fuels'
    SheetFuels = Fonte{[Item="Fuels",Kind="Sheet"]}[Data],
    
    // 3. Promove cabeçalhos (caso o Excel não tenha detectado automaticamente)
    #"Cabeçalhos Promovidos" = Table.PromoteHeaders(SheetFuels, [PromoteAllScalars=true]),
    
    // 4. Seleciona apenas as colunas necessárias para garantir a integridade
    #"Colunas Selecionadas" = Table.SelectColumns(#"Cabeçalhos Promovidos",{"fuel", "stage", "color"}),
    
    // 5. Limpeza de Texto (Trim/Clean) para evitar erros de digitação no Excel
    #"Limpar Texto" = Table.TransformColumns(#"Colunas Selecionadas",{
        {"fuel", each Text.Clean(Text.Trim(_)), type text},
        {"color", each Text.Clean(Text.Trim(_)), type text}
    }),
    
    // 6. Define Tipos
    #"Tipo Alterado" = Table.TransformColumnTypes(#"Limpar Texto",{
        {"fuel", type text}, 
        {"stage", Int64.Type}, 
        {"color", type text}
    })
in
    #"Tipo Alterado"
