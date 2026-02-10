# Acumula valores
num = int(input("Informe um número: "))
soma = 0 # IMPORTANTE: Sempre ao usar um acumulador o valor inicial é zero.
print("\n--- VALOR ACUMULADO ---")
for x in num:
    soma = soma + x
    print(soma)
print("\t--", soma, "--")