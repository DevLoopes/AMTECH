def barraEne():
    print("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n")
soma = 0
while True:
    numUser = int(input("Defina um número secreto (de 1 a 20): "))
    
    # Validação para saber se o número escolido
    # está dentro das opções permitidas
    if numUser < 1 or numUser > 20:
        print("Número Inválido!")

    # Se o número escolido for valido o while quebra
    else:
        barraEne()
        break

while True:
    tentativa = int(input("Escolha um número (de 1 a 20): "))
    
    # validação de tentativa, para saber se o número 
    # escolido está dentro das opções permitidas
    if tentativa < 1 or tentativa > 20:
        print("Número Inválido!")

    # Se número escolido estiver errado, o sistema
    # informa que o usuário errou e soma+1 tentativa
    elif tentativa != numUser:
        soma+=1
        print("Você errou, tente novamente!")

    # Se o usuário acertar ele soma + 1 tentativa e
    # mostra em qual tentativa o usuário acertou 
    elif tentativa == numUser:
        soma+=1
        print("MEUS PARABÉENS!")
        print(f"Você acertou na {soma}º tentativa")
        break   