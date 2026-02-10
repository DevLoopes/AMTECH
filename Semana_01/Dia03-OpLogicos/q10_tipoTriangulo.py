l1 = int(input("Digite o tamanho do lado 1 do triângulo: "))
l2 = int(input("Digite o tamanho do lado 2 do triângulo: "))
l3 = int(input("Digite o tamanho do lado 3 do triângulo: "))

if l1 == l2 and l2 == l3:
    print("\nEquilátero") # Equilátero (3 lados iguais)
elif l1 == l2 and l2 != l3 or l3 == l1 and l1 != l2 or l2 == l3 and l3 != l1:
    print("\nIsósceles") # Isósceles (2 lados iguais)
elif l1 != l2 and l2 != l3:
    print("\nEscaleno") # Escaleno ( todos os lados diferentes)