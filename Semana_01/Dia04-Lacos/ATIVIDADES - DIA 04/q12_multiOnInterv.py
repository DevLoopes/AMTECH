N = int(input("Digite um número: "))

a, b = 0, 1
vetor = []

multi_3 = 0
multi_5 = 0
soma = 0

for _ in range(N):
    vetor.append(a)
    a, b = b, a + b
    soma+=a
    media = soma/N

    if a%3==0: 
        multi_3+=1
    elif a%5==0: 
        multi_5+=1
print(f"\nA soma dos termos é: {soma}\nE a media do dos termos [A,B] é: {media:.1f}\n")
print(f"Multiplos de três: {multi_3}")
print(f"Multiplos de cinco: {multi_5}")