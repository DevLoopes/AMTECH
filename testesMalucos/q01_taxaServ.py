preco = float(input("Qual o valor de sua conta: "))
taxa = float(input("Qual a taxa de servirço: "))
qtd_pessoas = int(input("Informe a quantidade de pessoas presentes: "))

taxa = ((taxa/100) * 100)
val_com_taxa = (preco + taxa)
naVaquinha = (val_com_taxa / qtd_pessoas)

print(f"\nO valor deu R$ {preco:.2f}\ncom a tacha de R$ {taxa}, fica R$ {val_com_taxa:.2f}")
print(f"\nSe fizer a vaquinha dividindo em {qtd_pessoas} pessoas, sai por R$ {naVaquinha:.2f} cada")
print(" --------------- fim --------------- \n")