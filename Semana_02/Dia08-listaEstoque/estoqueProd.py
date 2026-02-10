
print("=====================================\n\tESTOQUE DE PRODUTOS\n=====================================")
op = 0
estoque = {}

while op != -1: # quando for -1 vai ter que parar
    op = int(input("\nEscolha a opção desejada:\n1 - Inserir produtos no estoque\n2 - Mostrar estoque\n3 - Atualize a quantidade de um item no estoque\n4 - Sair do estoque\n\n\tSELECIONAR OPÇÃO: "))
    if op == 1:
        addProd = int(input("\nQuantos produtos deseja adicionar: "))
        for x in range(1, addProd + 1, 1):
            addProd_nome = str(input("\nDigite qual produto deseja adicionar: "))
            addProd_und = int(input("Digite a quantidade em unidade desse produto: "))
            estoque[addProd_nome] = addProd_und
            print(f"Produto: {addProd_nome} foi inserido com sucesso!\n")
        
    elif op == 2:
        print(f"\nEstoque: {estoque}")
    elif op == 3:
        buscar = input("\nDeseja alterar a quantidade de qual produto: ")
        if buscar in estoque:
            addProd_und = int(input("\nDigite qual a nova quantidade desse produto: "))
            estoque.update({addProd_nome:addProd_und})
        else:
            print(f"\nNome: {buscar}\nnão faz parte na lista")
        
        print(f"\nestoque: {estoque}")
    elif op == 4:
        print(f"\nestoque: {estoque}")
        print(f"\Estoque finalizado!")
        
    