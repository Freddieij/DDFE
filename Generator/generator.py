import pandas as pd
import random

# ==========================================
# 1. Dados da Tabela TECHS (Fluxos)
# ==========================================
# Nota: "None" representa as células vazias da sua imagem
techs_data = [
    # --- Produção e Importação (Início da cadeia) ---
    {"tech": "Produção óleo", "fuel_in": None, "fuel_out": "Óleo"},
    {"tech": "Importação óleo", "fuel_in": None, "fuel_out": "Óleo"},
    {"tech": "Import. derivados", "fuel_in": None, "fuel_out": "Diesel 1"},
    {"tech": "Produção GN", "fuel_in": None, "fuel_out": "Gás natural 1"},
    {"tech": "Importação GN", "fuel_in": None, "fuel_out": "Gás natural 1"},
    {"tech": "Produção carvão", "fuel_in": None, "fuel_out": "Carvão"},
    {"tech": "Importação carvão", "fuel_in": None, "fuel_out": "Carvão"},
    {"tech": "Produção cana", "fuel_in": None, "fuel_out": "Cana de açúcar"},
    {"tech": "Produção milho", "fuel_in": None, "fuel_out": "Milho"},
    {"tech": "Produção oleag.", "fuel_in": None, "fuel_out": "Oleaginosas"},
    {"tech": "Produção biomassa", "fuel_in": None, "fuel_out": "Biomassa"},
    {"tech": "Produção urânio", "fuel_in": None, "fuel_out": "Urânio"},

    # --- Refinarias e Processamento ---
    {"tech": "Refinaria 1", "fuel_in": "Óleo", "fuel_out": "Diesel 1"},
    {"tech": "Refinaria 1", "fuel_in": None, "fuel_out": "Gasolina 1"}, # Exemplo: Ajuste se Óleo for input para todos
    {"tech": "Refinaria 1", "fuel_in": None, "fuel_out": "Óleo combustível"},
    {"tech": "Refinaria 1", "fuel_in": None, "fuel_out": "Outros derivados"},
    # *Nota: Na imagem, Refinaria 1 aparece 4 vezes. Se o input "Óleo" se aplica a todos, 
    # o Power BI costuma propagar ou você repete "Óleo" no fuel_in. 
    # Vou replicar visualmente onde parece mesclado, mas repetindo para garantir integridade dos dados.*
    {"tech": "Refinaria 1", "fuel_in": "Óleo", "fuel_out": "Gasolina 1"},
    {"tech": "Refinaria 1", "fuel_in": "Óleo", "fuel_out": "Óleo combustível"},
    {"tech": "Refinaria 1", "fuel_in": "Óleo", "fuel_out": "Outros derivados"},
    
    {"tech": "Refinaria 2", "fuel_in": "Óleo", "fuel_out": "Diesel 1"},
    {"tech": "Refinaria 2", "fuel_in": "Óleo", "fuel_out": "Gasolina 1"},
    {"tech": "Refinaria 2", "fuel_in": "Óleo", "fuel_out": "Óleo combustível"},
    {"tech": "Refinaria 2", "fuel_in": "Óleo", "fuel_out": "Outros derivados"},

    {"tech": "Processamento GN", "fuel_in": "Gás natural 1", "fuel_out": "Gás natural 2"},

    # --- Biocombustíveis ---
    {"tech": "Produção etanol 1", "fuel_in": "Cana de açúcar", "fuel_out": "Etanol anidro"},
    {"tech": "Produção etanol 1", "fuel_in": "Cana de açúcar", "fuel_out": "Etanol hidratado"},
    {"tech": "Produção etanol 1", "fuel_in": "Cana de açúcar", "fuel_out": "Bagaço de cana"},
    
    {"tech": "Produção etanol 2", "fuel_in": "Milho", "fuel_out": "Etanol anidro"},
    {"tech": "Produção etanol 2", "fuel_in": "Milho", "fuel_out": "Etanol hidratado"},
    
    {"tech": "Produção biodiesel", "fuel_in": "Oleaginosas", "fuel_out": "Biodiesel"},

    # --- Geração Elétrica ---
    {"tech": "Usina a biomassa", "fuel_in": "Biomassa", "fuel_out": "Eletricidade 1"},
    {"tech": "Usina nuclear", "fuel_in": "Urânio", "fuel_out": "Eletricidade 1"},
    {"tech": "Usina a carvão", "fuel_in": "Carvão", "fuel_out": "Eletricidade 1"},
    {"tech": "Usina GN 1", "fuel_in": "Gás natural 2", "fuel_out": "Eletricidade 1"},
    {"tech": "Usina GN 2", "fuel_in": "Gás natural 2", "fuel_out": "Eletricidade 1"},
    {"tech": "Usina óleo", "fuel_in": "Óleo combustível", "fuel_out": "Eletricidade 1"},
    {"tech": "Usina bagaço", "fuel_in": "Etanol hidratado", "fuel_out": "Eletricidade 1"}, # Conferir imagem se é Etanol ou Bagaço
    {"tech": "Usina solar 1", "fuel_in": None, "fuel_out": "Eletricidade 1"},
    {"tech": "Usina solar 2", "fuel_in": None, "fuel_out": "Eletricidade 1"},
    {"tech": "Usina eólica 1", "fuel_in": None, "fuel_out": "Eletricidade 1"},
    {"tech": "Usina eólica 2", "fuel_in": None, "fuel_out": "Eletricidade 1"},
    {"tech": "Usina hidro 1", "fuel_in": None, "fuel_out": "Eletricidade 1"},
    {"tech": "Usina hidro 2", "fuel_in": None, "fuel_out": "Eletricidade 1"},
    {"tech": "Usina hidro 3", "fuel_in": None, "fuel_out": "Eletricidade 1"},
    {"tech": "Import. eletricidade", "fuel_in": None, "fuel_out": "Eletricidade 1"},

    # --- Misturas ---
    {"tech": "Mistura Gasolina", "fuel_in": "Etanol anidro", "fuel_out": "Gasolina 2"},
    {"tech": "Mistura Gasolina", "fuel_in": "Gasolina 1", "fuel_out": "Gasolina 2"},
    {"tech": "Mistura Gasolina", "fuel_in": None, "fuel_out": "Demanda Transportes"}, # Flow direto?
    
    {"tech": "Mistura Diesel", "fuel_in": "Bagaço de cana", "fuel_out": "Diesel 2"}, # Estranho na imagem, mas seguindo transcrição visual
    {"tech": "Mistura Diesel", "fuel_in": "Diesel 1", "fuel_out": "Diesel 2"},
    {"tech": "Mistura Diesel", "fuel_in": None, "fuel_out": "Demanda agropecuária"},
    {"tech": "Mistura Diesel", "fuel_in": None, "fuel_out": "Demanda industrial"},
    {"tech": "Mistura Diesel", "fuel_in": None, "fuel_out": "Demanda Transportes"},
    {"tech": "Mistura Diesel", "fuel_in": None, "fuel_out": "Demanda comercial / serviços"},

    # --- Rede Elétrica ---
    {"tech": "Transmissão", "fuel_in": "Eletricidade 1", "fuel_out": "Eletricidade 2"},
    {"tech": "Distribuição", "fuel_in": "Eletricidade 2", "fuel_out": "Demanda residencial"},
    {"tech": "Distribuição", "fuel_in": "Eletricidade 2", "fuel_out": "Demanda agropecuária"},
    {"tech": "Distribuição", "fuel_in": "Eletricidade 2", "fuel_out": "Demanda industrial"},
    {"tech": "Distribuição", "fuel_in": "Eletricidade 2", "fuel_out": "Demanda Transportes"},
    {"tech": "Distribuição", "fuel_in": "Eletricidade 2", "fuel_out": "Demanda comercial / serviços"},

    # --- Solar GD ---
    {"tech": "Solar GD", "fuel_in": None, "fuel_out": "Demanda residencial"},
    {"tech": "Solar GD", "fuel_in": None, "fuel_out": "Demanda comercial / serviços"},
    {"tech": "Solar GD", "fuel_in": None, "fuel_out": "Demanda Transportes"},

    # --- Exportações (Sinks sem output definido) ---
    {"tech": "Exportações", "fuel_in": "Óleo", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Diesel 1", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Gasolina 1", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Óleo combustível", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Outros derivados", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Gás Natural 2", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Etanol anidro", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Etanol hidratado", "fuel_out": None},
    {"tech": "Exportações", "fuel_in": "Biodiesel", "fuel_out": None},

    # --- Demandas Finais (Onde TECH é vazio na imagem) ---
    {"tech": None, "fuel_in": "Bagaço de cana", "fuel_out": "Demanda industrial"},
    {"tech": None, "fuel_in": "Etanol hidratado", "fuel_out": "Demanda agropecuária"},
    {"tech": None, "fuel_in": "Etanol hidratado", "fuel_out": "Demanda Transportes"},
    {"tech": None, "fuel_in": "Gás natural 2", "fuel_out": "Demanda residencial"},
    {"tech": None, "fuel_in": "Gás natural 2", "fuel_out": "Demanda industrial"},
    {"tech": None, "fuel_in": "Gás natural 2", "fuel_out": "Demanda Transportes"},
    {"tech": None, "fuel_in": "Gás natural 2", "fuel_out": "Demanda comercial / serviços"},
    {"tech": None, "fuel_in": "Óleo combustível", "fuel_out": "Demanda agropecuária"},
    {"tech": None, "fuel_in": "Óleo combustível", "fuel_out": "Demanda industrial"},
    {"tech": None, "fuel_in": "Óleo combustível", "fuel_out": "Demanda Transportes"},
    {"tech": None, "fuel_in": "Óleo combustível", "fuel_out": "Demanda comercial / serviços"},
    {"tech": None, "fuel_in": "Biodiesel", "fuel_out": "Demanda agropecuária"},
    {"tech": None, "fuel_in": "Biodiesel", "fuel_out": "Demanda industrial"},
    {"tech": None, "fuel_in": "Biodiesel", "fuel_out": "Demanda Transportes"},
    {"tech": None, "fuel_in": "Biodiesel", "fuel_out": "Demanda comercial / serviços"},
    {"tech": None, "fuel_in": "Carvão", "fuel_out": "Demanda industrial"},
    {"tech": None, "fuel_in": "Biomassa", "fuel_out": "Demanda residencial"},
    {"tech": None, "fuel_in": "Biomassa", "fuel_out": "Demanda agropecuária"},
    {"tech": None, "fuel_in": "Biomassa", "fuel_out": "Demanda industrial"},
    {"tech": None, "fuel_in": "Biomassa", "fuel_out": "Demanda comercial / serviços"},
    {"tech": None, "fuel_in": "Outros derivados", "fuel_out": "Demanda residencial"},
    {"tech": None, "fuel_in": "Outros derivados", "fuel_out": "Demanda agropecuária"},
    {"tech": None, "fuel_in": "Outros derivados", "fuel_out": "Demanda industrial"},
    {"tech": None, "fuel_in": "Outros derivados", "fuel_out": "Demanda Transportes"},
    {"tech": None, "fuel_in": "Outros derivados", "fuel_out": "Demanda comercial / serviços"},
]

# ==========================================
# 2. Dados da Tabela FUELS (Cores/Estágios)
# ==========================================
fuels_data = [
    {"fuel": "Óleo", "stage": 1, "color": "#333333"},
    {"fuel": "Gás Natural 1", "stage": 1, "color": "#d95f02"},
    {"fuel": "Carvão", "stage": 1, "color": "#666666"},
    {"fuel": "Cana De Açúcar", "stage": 1, "color": "#1b9e77"},
    {"fuel": "Milho", "stage": 1, "color": "#e7298a"},
    {"fuel": "Oleaginosas", "stage": 1, "color": "#8c564b"},
    {"fuel": "Biomassa", "stage": 1, "color": "#1b9e77"},
    {"fuel": "Urânio", "stage": 1, "color": "#377eb8"},
    {"fuel": "Diesel 1", "stage": 2, "color": "#333333"},
    {"fuel": "Gasolina 1", "stage": 2, "color": "#333333"},
    {"fuel": "Óleo Combustível", "stage": 2, "color": "#333333"},
    {"fuel": "Outros Derivados", "stage": 2, "color": "#333333"},
    {"fuel": "Gás Natural 2", "stage": 2, "color": "#d95f02"},
    {"fuel": "Etanol Anidro", "stage": 2, "color": "#1b9e77"},
    {"fuel": "Etanol Hidratado", "stage": 2, "color": "#1b9e77"},
    {"fuel": "Bagaço De Cana", "stage": 2, "color": "#1b9e77"},
    {"fuel": "Biodiesel", "stage": 2, "color": "#8c564b"},
    {"fuel": "Eletricidade 1", "stage": 2, "color": "#7570b3"},
    {"fuel": "Diesel 2", "stage": 3, "color": "#333333"},
    {"fuel": "Gasolina 2", "stage": 3, "color": "#333333"},
    {"fuel": "Eletricidade 2", "stage": 3, "color": "#7570b3"},
    {"fuel": "Demanda Residencial", "stage": 4, "color": "#000000"},
    {"fuel": "Demanda Agropecuária", "stage": 4, "color": "#000000"},
    {"fuel": "Demanda Industrial", "stage": 4, "color": "#000000"},
    {"fuel": "Demanda Transportes", "stage": 4, "color": "#000000"},
    {"fuel": "Demanda Comercial / Serviços", "stage": 4, "color": "#000000"},
]

# ==========================================
# 3. Geração do Arquivo Excel
# ==========================================

# Criar DataFrames
df_techs = pd.DataFrame(techs_data)
df_fuels = pd.DataFrame(fuels_data)

# 2. Extraímos a lista de combustíveis válidos existentes
lista_combustiveis_validos = df_fuels['fuel'].unique().tolist()

# 3. Geramos dados aleatórios que SE CONECTAM ao fluxo existente
extra_rows = []
for i in range(1000): # 1000 conexões aleatórias
    
    # Escolhe um input e um output aleatórios da lista real
    input_random = random.choice(lista_combustiveis_validos)
    output_random = random.choice(lista_combustiveis_validos)
    
    # Evita que entrada seja igual a saída (loop direto), se desejar
    while output_random == input_random:
        output_random = random.choice(lista_combustiveis_validos)

    extra_rows.append({
        "tech": f"Tech_Caos_{i}", 
        "fuel_in": input_random, 
        "fuel_out": output_random
    })

# 4. Junta tudo
df_big = pd.concat([df_techs, pd.DataFrame(extra_rows)])

# 5. Salva
with pd.ExcelWriter("RES_Dados_Caos.xlsx", engine='openpyxl') as writer:
    df_big.to_excel(writer, sheet_name="Techs", index=False)
    df_fuels.to_excel(writer, sheet_name="Fuels", index=False)

print("Arquivo 'RES_Dados_Caos.xlsx' gerado com conexões aleatórias.")

# ==========================================
# 3. Geração do Arquivo Excel
# ==========================================

# # Criar DataFrames
# df_techs = pd.DataFrame(techs_data)
# df_fuels = pd.DataFrame(fuels_data)

# # Nome do arquivo de saída
# output_file = "RES_Dados.xlsx"

# try:
#     with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
#         df_techs.to_excel(writer, sheet_name="Techs", index=False)
#         df_fuels.to_excel(writer, sheet_name="Fuels", index=False)
#     print(f"Sucesso! Arquivo '{output_file}' gerado.")
#     print(f"Linhas em Techs: {len(df_techs)}")
#     print(f"Linhas em Fuels: {len(df_fuels)}")
# except Exception as e:
#     print(f"Erro ao salvar arquivo: {e}")

# # ==========================================
# # DICA EXTRA PARA EDGE CASES (OPCIONAL)
# # ==========================================
# # Se quiser gerar uma tabela gigante para teste de carga no Power BI,
# # descomente as linhas abaixo:

# # import random
# # extra_rows = []
# # for i in range(10000): # Adiciona 10 mil linhas
# #    extra_rows.append({
# #        "tech": f"Tech_Teste_{i}", 
# #        "fuel_in": "Fonte_Genérica", 
# #        "fuel_out": "Destino_Genérico"
# #    })
# # df_big = pd.concat([df_techs, pd.DataFrame(extra_rows)])
# # print(f"Tabela estressada gerada com {len(df_big)} linhas.")