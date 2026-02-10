val = float(input("Valor da compra: "))
if val <= 100 :
    desconto = 0.05
elif val > 100 and val <= 300:
    desconto = 0.10
elif val > 300:
    desconto = 0.15

final = val * (1 - desconto/100)

print(f"Seu desconto para essa compra é de (%): {desconto:.2f}")
print(f"Preço final com desconto fica: R$ {final:.2f}")