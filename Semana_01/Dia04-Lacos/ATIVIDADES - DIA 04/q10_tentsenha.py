senha = str(input("Digite sua senha: "))
tentativa = 3
for i in range(0,tentativa + 1, 1):
    confirm_senha = str(input("Confirme sua senha: "))
    if senha == confirm_senha:
        print("\nSua senha foi criada com sucesso! ")
        break
    elif tentativa < 1:
        print("\nAs suas tentativas expiraram,\ntente novamente em outro momento!")
        break
    else:
        print(f"\nSua senha está errada!\nVocê tem apenas {tentativa} tentativas")
        tentativa-=1