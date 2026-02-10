valor = float(input("Qual o valor você deseja separar real de centavos: "))
total_centavos = int(valor*100)
reais = total_centavos//100
centavos = total_centavos%100
print(f"Fica R$ {reais} reais e {centavos} centavos")