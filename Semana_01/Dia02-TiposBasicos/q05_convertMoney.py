cotacao_dolar = float(input("Qual o valor da cotação em dolar: "))
val_real = float(input("Qual o valor você deseja converter para dolar: "))
valDolar = val_real / cotacao_dolar
print(f"O valor é R$ {val_real:.2f} representa {valDolar:.2f} dolares")