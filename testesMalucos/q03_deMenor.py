ano_nasc = int(input("Informe seu ano de nascimento: "))
ano_atual = int(input("Em que ano estamos: "))

if ano_nasc >= ano_atual or ano_nasc < 1926 :
    print("Ano de nascimento invalido!\n")
else: 
    idade = ano_atual - ano_nasc
    if idade >= 18:
        print("Sua idade é: ", idade)
    else:
        print("Você é menor de idade")
