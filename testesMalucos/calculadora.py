x = float(input("Escolha um numero: "))
y = float(input("Escolha um outro numero: "))
operation = str(input("Digite a operação que deseja realizar [ + | - | * | / ]: "))
if operation == "+":
    print("Resultado", x + y)
elif operation == "-":
    print("Resultado", x - y)
elif operation == "*":
    print("Resultado", x * y)
elif operation == "/":
    if y != 0:
        print(f"Resultado {x / y:.2f}")
    else:
        print("Valor invalido")
else:
    print("Nenhum resultado obtido")
    
# print("A soma desses valores é: ", n1 + str(operatioin) + n2)