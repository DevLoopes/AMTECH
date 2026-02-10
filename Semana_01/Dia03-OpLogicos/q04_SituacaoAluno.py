n1 = float(input("Digite sua nota 1: "))
n2 = float(input("Digite sua nota 2: "))
n3 = float(input("Digite sua nota 3: "))
n4 = float(input("Digite sua nota 4: "))
n5 = float(input("Digite sua nota 5: "))

media = ((n1 + n2 + n3 + n4 + n5) / 5)
if media >= 7:
    print(f"\nNota: {media:.2f}")
    print("Situação do aluno: Aprovado")
elif media >= 5 and media < 7:
    print(f"\nNota: {media:.2f}")
    print("Situação do aluno: Recuperação")
elif media < 5:
    print(f"\nNota: {media:.2f}")
    print("Situação do aluno: Reprovado")