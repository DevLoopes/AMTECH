soma = 0
notas = int(input("Quantas provas você fez: ")) # Quantas provas foram feitas
for x in range(1, notas + 1):
    nota = float(input(f"Digite a nota {x}: "))
    soma+=nota
print(f"Sua média final é: {soma / notas}")