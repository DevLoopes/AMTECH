
a = float(input("Digite o valor de a: "))
b = float(input("Digite o valor de b: "))
c = float(input("Digite o valor de c: "))

val_MAX = 0
if b < a and a > c:
    val_MAX = a
    print("\nLetra A")
elif a < b and b > c:
    val_MAX = b
    print("\nLetra B")
elif a < c and c > b:
    val_MAX = c
    print("\nLetra C")

print(val_MAX)
