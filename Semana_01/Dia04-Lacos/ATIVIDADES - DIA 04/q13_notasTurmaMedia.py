nota = 0
soma = 0
incrementador = 0
media = 0

while nota != -1:
    nota = float(input("Digite uma nota: "))
    soma+=nota # Soma = soma + nota
    incrementador+=1
    
media = (soma+1)/(incrementador-1)
print(f"A média final é: {media}")
print(f"A quantidade de vezes é: {incrementador+1}")