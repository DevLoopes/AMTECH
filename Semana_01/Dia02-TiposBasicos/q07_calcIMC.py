p = float(input("Digite seu peso(kg): "))
a = float(input("Digitesua altura(m): "))
imc = p / (a**2)
print(f"Seu IMC é: {imc:.1f}\nIMC fracionado: {imc:.2f}")