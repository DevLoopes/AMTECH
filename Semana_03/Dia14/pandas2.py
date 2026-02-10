import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
arqv = open(base_dir + "/src/vendas_loja.csv", "r", encoding="utf-8")

print(arqv)
df = pd.read_csv(arqv)
print("\n===== Primeiras Linhas =====")
print(df.head())

# df["desconto_pct"] = (
#     df["desconto_pct"]
#         .astype(str)
#         .str.replace(",", ".", regex=False)
#         .astype(float)
# )

# df["valor_bruto"] = df["quantidade"] * df["preco_unit"]
# df["valor_liquido"] = df["valor_bruto"] * (1 - df["desconto_pct"])

# quantidademaior = df[df["quantidade"] >= 2]
# print(quantidademaior[["loja", "produto", "valor_liquido" ]])

# console = df[ df["categoria"] == "Console"]
# print("\n==== Vendas de Console ====")
# print(console[["data", "loja", "projetos", "quantidade", "valor_liquido"]])

# FILTRAGEM DE DADOS / SOMA DE DADOS FILTRADOS
# === df["valor_bruto"] = df["quantidade"] * df["preco_unit"]
# === df["valor_liquido"] = df["valor_bruto"] * (1 - df["desconto_pct"])
# print(df[["id_pedido", "data", "produto", "quantidade", "preco_unit", "valor_bruto", "valor_liquido"]])

# Colunas com quantidade de itens maior ou igual a 2
# === console = df[ df["categoria"] == "Console"]
# print("\n==== Vendas de Console ====")
# print(console[["data", "loja", "projetos", "quantidade", "valor_liquido"]])

# ESTATISTICAS RÁPIDAS
# print("\n=== ESTATISTICAS ===")
# print(df["produto"].describe())

# AGRUPAR E SOMAR FATURAMENTO / LOJA
# fat_por_loja = (df.groupby("loja")["valor_liquido"].sum())
# print("\n=== AGRUPAMENTO POT LOJA ===")
# print(fat_por_loja)

# AGRUPAR E SOMAR FATURAMENTO / PRODUTO
# fat_por_prod = (df.groupby("produto")["valor_liquido"].sum())
# print("\n=== AGRUPAMENTO POT PRODUTO ===")
# print(fat_por_prod)

# TOP 3 FATURAMENTOS POR PRODUTO
# fat_por_data = (df.groupby("data")["valor_liquido"]
#                 .sum()
#                 .sort_values(ascending=False) # ascending=False = do maior para o menor
#                 .head(3) # Mostrar os 3 primeiros
#             )
# print("\n=== TOP 3 FATURAMENTOS POR PRODUTO ===")
# print(fat_por_data)

# EXPORTAR TABELA PARA CSV

# fat_por_dia.to_csv(r"C:\Users\Capacitacao1\Documents\Pandas\Relatorios\faturamento_por_dia.csv")
# console.to_csv(r"C:\Users\Capacitacao1\Documents\Pandas\Relatorios\.csv")
