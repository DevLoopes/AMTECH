# COMO EU FIZ
N = int(input("Digite um número inteiro: "))
numPares = list(range(2, N + 1, 2))
numTotal = 0
for x in numPares:
    numTotal = numTotal + 1
print(numPares, " = ", numTotal)

# OR - COMO O COLEGUINHA FEZ     
resultado=0
for cont in range(1,N +1):
    if cont % 2==0:
        resultado=resultado+1  
print("numros Pares é:",resultado)