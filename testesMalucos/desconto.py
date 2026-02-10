preco = float(input("Preço: "))
desconto = float(input("Desconto (%): "))
final = preco * (1 - desconto/100)
print(f"Preço final: R$ {final:.2f}")