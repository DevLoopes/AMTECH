N = int(input("Digite um número: "))

a, b = 0, 1
soma = 0

for _ in range(N):
    print(a, end=" ")
    a, b = b, a + b
    soma+=a
    media = (soma)/N
print(f"\nA soma dos termos é: {soma}\nE a media do dos termos [A,B] é: {media:.1f}")