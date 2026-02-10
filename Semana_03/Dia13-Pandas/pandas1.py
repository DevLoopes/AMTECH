import pandas as pd
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
arqv = open(base_dir + "/src/vendas_loja.csv", "r", encoding="utf-8")

df = pd.read_csv(arqv)
# print("\n===== Primeiras Linhas =====")
# print(df.head())

df["desconto_pct"] = (
    df["desconto_pct"]
        .astype(str)
        .str.replace(",", ".", regex=False)
        .astype(float)
)

# FILTRAGEM DE DADOS / SOMA DE DADOS FILTRADOS
df["valor_bruto"] = df["quantidade"] * df["preco_unit"]
df["valor_liquido"] = df["valor_bruto"] * (1 - df["desconto_pct"])
print(df[["id_pedido", "data", "produto", "quantidade", "preco_unit", "valor_bruto", "valor_liquido"]])

# Colunas com quantidade de itens maior ou igual a 2
# console = df[ df["categoria"] == "Console"]
# print("\n==== Vendas de Console ====")
# print(console[["data", "loja", "projetos", "quantidade", "valor_liquido"]])

