salario = float(input("Informa seu salário atual: "))
new_salario = 0
if salario <= 280:
    aumento = 0.20
elif salario > 280 and salario <= 700:
    aumento = 0.15
elif salario > 700 and salario <= 1500:
    aumento = 0.10
elif salario > 1500:
    aumento = 0.05
val_aumento = aumento*salario
new_salario = salario + val_aumento
print(f"\nCom um aumento de {aumento*100:.0f}%,\nAplicando mais R$ {val_aumento:.2f} em cima do valor total \nSeu novo salário será R$ {new_salario:.2f}")