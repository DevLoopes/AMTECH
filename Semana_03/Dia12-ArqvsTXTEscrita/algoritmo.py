import os

base_dir = os.path.dirname(os.path.abspath(__file__))
lista = os.path.join(base_dir, "src/user.txt")

try:
    arquivo = open(lista, "r", encoding="utf-8")
    linha = arquivo.readline().split(",")
    print(f"Olá {linha[0].strip()}")
    print(f"Sua idade é: {linha[1].strip()}")
    print(f"Você mora em: {linha[2].strip()}")
    print(f"e seu telefone é: {linha[3].strip()}")
    arquivo.close()
except:
    print("Não foi posslível encontrar o arquivo.")

