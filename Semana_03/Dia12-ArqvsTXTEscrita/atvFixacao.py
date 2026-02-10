import os

base_dir = os.path.dirname(os.path.abspath(__file__))

try:
    print("=====================================\n\tAGENDA TELEFÔNICA\n=====================================")
    op = 0
    agenda = []
    arqv = open(base_dir+ "\\src\\""agendaTelefonica.txt", "a", encoding="utf-8")
    while True: # quando for -1 vai ter que parar
        op = int(input("\nEscolha a opção desejada:\n1 - Cadastrar novo usuário\n2 - Mostrar contatos da agenda\n3 - Digite -1, para sair\n\n\tSELECIONAR OPÇÃO: "))
        if op == 1:
            nome = input("\nDigite seu nome: ")
            tel = input("Digite seu telefone: ")
            arqv.write(nome + ", " + tel)
            arqv.write("\n")
            
            print(f"Nome: {nome} foi inserido com sucesso!\n")
            
        elif op == 2:
            print(f"\nAgenda: {agenda}")
        elif op == 3:
            arqv.close()
            break
except:
    print("Arquivo não encontrado com sucesso!")
        