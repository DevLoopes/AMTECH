senha = str(input("Digite sua senha: "))
confirm_senha = str(input("Confirme sua senha: "))
if senha == confirm_senha:
    print("Sua senha foi criada com sucesso! " + str(senha == confirm_senha))
else:
    print("Sua senha está errada! " + str(senha == confirm_senha))