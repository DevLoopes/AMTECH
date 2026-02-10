n = int(input("Informe um número: "))
soma = 0
a = 0
print("\n--- VALOR ACUMULADO ---")
while a < n: # IMPORTANTE: Sempre ao usar um acumulador o valor inicial é zero.
    soma = soma + a
    a+=1
print("\t--", soma, "--")