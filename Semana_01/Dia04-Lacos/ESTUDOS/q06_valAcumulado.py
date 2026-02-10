num = 0
soma = 0
a = 0
while True:
    num = float(input("Digite um valor (0 para sair): "))
    if num == 0:
        break
    soma+=num
    a+=1
print("A soma é: ", soma)
print("A quantidade é: ", a-1)