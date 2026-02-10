idade = int(input("Digite sua idade: "))
if idade >= 18: 
    podeDirigir = True
    situacao = "maior"
else: 
    podeDirigir = False
    situacao = "menor"
print(f"Você é {situacao} de idade\nPode dirigir?\n(True/False): ", podeDirigir)

# Eu fiz dessa forma pois quiz "automatizar" o resultado do print(""),
# não sendo mais necessário repassar o print("") varias vezes,
# uma pra cada condição só por causa do "maior/menor" da string, 
# mas creio que isso tem maior ganho em sistemas maiores e mais
# complexos em que você busca ao máximo evitar a repetição de códigos, 
# como vemos no metodo de Paradigma Orientado a Objetos(POO)