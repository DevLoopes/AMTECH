def Questao_01():
    print("\n========= Questão 01 =========")
    frase = input("\nDigite uma frase: ")
    frase = frase.lower()
    # def tamanho():
    #     return len(frase)
    # def semEspaco():
    #     return frase.strip()
    print("\nponto 01\nO tamanho da frase é: ", len(frase))
    print("ponto 02\nretirando espaços a direita e a esquerda: ", frase.strip())
    print("ponto 03\nFrase lower: ", frase.lower(), "\nFrase upper: ", frase.upper())

def Questao_02():
    print("\n========= Questão 02 =========")
    frase = input("\nDigite um texto fixo: ")
    substring = input("Digite uma palavra chave: ")
    if substring in frase:
        print(f"{substring} aparece em {frase}")
        print(f"Primeira ocorrencia: {frase.find(substring)}")
        print(f"Quantidade: {frase.count(substring)}")
    else:
        print(f"{substring} não aparece em {frase}")

def Questao_03():
    print("\n========= Questão 03 =========")
    lista = input("\nInforme uma lista de itens (separe por virgula): ")
    lista_ = lista.split(",")
    lista2_ = []
    for i in lista_:
        lista2_.append(i.strip())
    print(lista2_)
    
def Questao_04():
    print("\n========= Questão 04 =========")
    nome = input("\nInforme seu nome: ")
    if (6 <= len(nome) <= 12) and (nome.count(" ") == 0) and (nome[0].isalpha()):
        print("Nome de usuário válido!")
    else:
        print("Nome de usuário inválido!")
        
def Questao_05():
    print("\n========= Questão 05 =========")
    email = input("\nInforme seu email: ")
    checkValido = email.split("@")
    print(checkValido)
    if len(checkValido) == 2:
        print("Email válido!")
        if email.endswith("@empresa.com"):
            print("Email Corporativo")
        elif email.endswith("@gmail.com") or email.endswith("@outloock.com"):
            print("Email Pessoal")
    else:
        print("Email inválido!")

            

op = 0
while True:
    print("\n========= LISTA DE QUESTÕES =========")
    op = int(input("Qual questão deseja testar?\n1 - Questão 01\t\t2 - Questão 02\n3 - Questão 03\t\t4 - Questão 04\n5 - Questão 05\t\t6 - Questão 06\n7 - Questão 07\t\t8 - Questão 08\n9 - Questão 09\t\t10 - Questão 010\n\n\tSELECT OPTION: "))
    if op == 1:
       Questao_01() 
    elif op == 2:
        Questao_02()
    elif op == 3:
        Questao_03()
    elif op == 4:
        Questao_04()
    elif op == 5:
        Questao_05()
    # elif op == 6:
    #     Questao_06()
    # elif op == 7:
    #     Questao_07()
    # elif op == 8:
    #     Questao_08()
    # elif op == 9:
    #     Questao_09()
    # elif op == 10:
    #     Questao_010()
    
    else:
        False
# if texto != textKey.find():
#     print("Não aparece")
# else:
#     print("Aparece")
    