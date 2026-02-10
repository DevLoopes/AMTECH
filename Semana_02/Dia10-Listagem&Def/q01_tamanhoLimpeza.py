frase = input("Digite uma frase: ")
frase = frase.lower()
def tamanho():
    return len(frase)

def semEspaco():
    return frase.strip()

def upperAndLower():
    fraseLower = frase.lower()
    fraseUpper = frase.upper()
    print("\nFrase lower: ", fraseLower, "\nFrase upper: ", fraseUpper)

print("\nponto 01\nO tamanho da frase é: ", tamanho())
print("\nponto 02\nO tamanho da frase é: ", semEspaco())
print("\nponto 02\nO tamanho da frase é: ", upperAndLower())

