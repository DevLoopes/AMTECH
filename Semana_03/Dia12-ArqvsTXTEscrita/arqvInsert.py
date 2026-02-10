import os

base_dir = os.path.dirname(os.path.abspath(__file__))

try:
    for x in range(1, 5+1, 1):
        print(f"\n{x}º cadastro")
        print(base_dir)
        nome = input("Digite seu nome: ")
        arqv = open(base_dir+ "\\src\\" + nome + ".txt", "a", encoding="utf-8")
        idade = input("Digite sua idade: ")
        tel = input("Digite seu telefone: ")
        arqv.write(nome + ", " + idade + ", " + tel)
        arqv.write("\n")
        arqv.close()
except:
    print("Arquivo não encontrado com sucesso!")
        
    