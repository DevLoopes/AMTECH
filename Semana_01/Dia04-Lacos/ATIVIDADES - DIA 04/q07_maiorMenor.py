# Segundo o META do WhatsApp
N = int(input("Digite a quantidade de números: "))
numeros = [
    float(input(f"Digite o número {i+1}: ")) 
    for i in range(N)
]
print(f"Maior: {max(numeros)}")
print(f"Menor: {min(numeros)}")