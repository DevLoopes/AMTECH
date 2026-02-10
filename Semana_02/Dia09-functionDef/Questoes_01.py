num = []
def dobro(n):
    return n*2

def parOUimpar(n):
    if n%2==0:
        return True
    else:
        return False
    
def temp(t):
    if t < 18:
        return "Frio"
    elif 18 <= t and t <= 26:
        return "Agradavel"
    elif t > 26:
        return "Quente"
    
def maior(num):
    for i in range(1, 5 + 1, 1):
        numb = int(input(f"Digite o número {i}: "))
        num.append([numb])
        
    return max(num)


n = int(input("Digite um número: "))
t = int(input("informe uma temperatura: "))



print(f"\n\tQ01\nO dobro é: {dobro(n)}")
print(f"\n\tQ02\nEsse número é par? {parOUimpar(n)}")
print(f"\n\tQ03\nA temperatura é: {temp(t)}")
print(f"\n\tQ04\nO Maior é: {maior(num)}")