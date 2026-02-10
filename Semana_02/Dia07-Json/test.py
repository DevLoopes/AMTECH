
print("=====================================\n\tAGENDA TELEFÔNICA\n=====================================")
op = 0
agenda = []
while op != -1: # quando for -1 vai ter que parar
    op = int(input("\nEscolha a opção desejada:\n1 - Novo usuário\n2 - Deletar o ultimo elemento\n3 - Procurar nome na agenda\n4 - Verificar agenda\n5 - Para sair coloque (-1):\n\n\tSELECIONAR OPÇÃO: "))
    
    if op == 1:
        nome = input("Digite o nome do usuário: ")
        agenda.append(nome)
        print(f"Nome: {nome} foi inserido com sucesso!\n")
        
    elif op == 2:
        del agenda[len(agenda)-1]
        print(f"\nDeletado com sucesso!\nLista: {agenda}")
    elif op == 3:
        buscar = input("\nInforme um nome: ")
        if buscar in agenda:
            print(f"\nNome: {buscar} faz parte da agenda!")
        else:
            print(f"\nNome: {agenda} não faz parte na lista")
    else:
        print(f"\nAgenda: {agenda}")
        