let
    Fonte = Input_Tech,
    // Garantia de tipagem para evitar erros futuros no motor
    #"Tipo Alterado" = Table.TransformColumnTypes(Fonte,{
        {"tech", type text}, 
        {"fuel_in", type text}, 
        {"fuel_out", type text}
    })
in
    #"Tipo Alterado"
