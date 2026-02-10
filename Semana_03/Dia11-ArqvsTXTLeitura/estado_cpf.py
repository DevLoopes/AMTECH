import os

base_dir = os.path.dirname(os.path.abspath(__file__))
cpf = os.path.join(base_dir, "src/cpf.txt")

try:
    arquivo = open(cpf)
    conteudo = arquivo.read() 
    # readline() = Lê uma linha de cada, 
    #readlines() = retorna todas as linhas em um vetor
    
    print("Seu CPF é: ", conteudo)
    arquivo.close()
except:
    print("Não foi posslível encontrar essa localização.")
  
if conteudo[10] == "1":
    print("Seu Estado é: Mato Grosso do Sul (MS)")
elif conteudo[10] == "2":
    print("Seu Estado é: Amazonas (AM)")
elif conteudo[10] == "3":
    print("Seu Estado é: Ceará (CE)")
elif conteudo[10] == "4":
    print("Seu Estado é: Alagoas (AL)")
elif conteudo[10] == "5":
    print("Seu Estado é: Bahia (BA)")
elif conteudo[10] == "6":
    print("Seu Estado é: Minas Gerais (MG)")
elif conteudo[10] == "7":
    print("Seu Estado é: Espírito Santo (ES)")
elif conteudo[10] == "8":
    print("Seu Estado é: São Paulo (SP)")
elif conteudo[10] == "9":
    print("Seu Estado é: Paraná (PR)")
elif conteudo[10] == "0":
    print("Seu Estado é: Rio Grande do Sul (RS)")
    

# 1: Mato Grosso do Sul (MS)
# 2: Amazonas (AM)
# 3: Ceará (CE);
# 4: Alagoas (AL);
# 5: Bahia (BA);
# 6: Minas Gerais (MG);
# 7: Espírito Santo (ES);
# 8: São Paulo (SP);
# 9: Paraná (PR);
# 0: Rio Grande do Sul (RS)