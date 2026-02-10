import os

base_dir = os.path.dirname(os.path.abspath(__file__))
lista = os.path.join(base_dir, "src/tarefa_01.txt")
soma = 0
contador = 0
try:
    arquivo = open(lista)
    linha = arquivo.readline()
    while len(linha) != 0:
        linha = arquivo.readline()
        
         # O segundo len() sevre para verificar 
         # se o tamanho da ultima linha é menor que zero(0), 
         # se for o while não se repete e o resultado não 
         # cai em error de except
        if len(linha) != 0:
            vetor1 = linha.split(";")
            print(vetor1[2].strip())
            valor = float(vetor1[2].strip())
            soma += valor
    arquivo.close()
except:
    print("Não foi posslível encontrar.")
    
print("Valor Total: ", soma)