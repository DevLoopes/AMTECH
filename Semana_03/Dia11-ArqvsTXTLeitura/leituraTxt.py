# "C:\\Users\\Capacitacao1\\Documents\\AMTECH\\Dia 11 - Arqvs TXT\\src\\first-arqv.txt"

import os

base_dir = os.path.dirname(os.path.abspath(__file__))
caminho = os.path.join(base_dir, "src/firstarqv.txt")

try:
    arquivo = open(caminho)
    conteudo = arquivo.read()
    print(conteudo)
except:
    print("Não foi posslível abrir o arquivo.")