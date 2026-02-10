produtos = []
produtos.append({'nome':'Caneta','preco':3.0})
produtos.append({'nome':'Cadereno','preco':12.5})
for p in produtos:
    print(f"{p['nome']}: R$ {p['preco']:.2f}")

addProd = int(input("\nDigite quantos produtos deseja adicionar: "))
for x in range(1, addProd + 1, 1):
    addProd_nome = str(input("\nDigite qual produto deseja adicionar: "))
    addProd_preco = float(input("\nDigite qual preço desse produto: "))
    produtos.append([addProd_nome, addProd_preco])

print(produtos)