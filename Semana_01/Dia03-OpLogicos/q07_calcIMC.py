altura = float(input("Qual sua altura: "))
peso = float(input("Qual seu peso: "))
imc = (peso /(altura**2))

if imc < 18.5:
    print("\nAbaixo")
elif imc >= 18.5 and imc <= 24.9:
    print("\nNormal")
elif imc >= 25 and imc <= 29.9:
    print("\nSobrepeso")
elif imc >= 30:
    print("\nObesidade") 
    
print(f"\n-- DADOS DO IMC --\nPeso: {peso:.2f}\nAltura: {altura:.2f}\nIMC: {imc:.2f}\n")