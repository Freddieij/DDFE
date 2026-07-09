let
    Fonte = Input_Fuel,
    #"Tipo Alterado" = Table.TransformColumnTypes(Fonte,{
        {"fuel", type text}, 
        {"stage", Int64.Type},
        {"color", type text} // <--- NOVO
    })
in
    #"Tipo Alterado"
