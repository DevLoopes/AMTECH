texto = input("Digite uma frase: ")
texto = texto.lower()
print("a --> ", texto.count('a'))
print("e --> ", texto.count('e'))
print("i --> ", texto.count('i'))
print("o --> ", texto.count('o'))
print("u --> ", texto.count('u'))

# Q02
if len(texto) == 0 or (texto[0] == " " and len(texto) == 1):
    print("String vazia")
else:
    print(f"Primeira letra: {texto[0]}")
    print(f"Ultima letra: {texto[len(texto)-1]}")