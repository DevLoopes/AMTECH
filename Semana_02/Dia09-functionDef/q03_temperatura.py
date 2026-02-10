def temp(t):
    if t < 18:
        return "Frio"
    elif 18 <= t and t <= 26:
        return "Agradavel"
    elif t > 26:
        return "Quente"
    
t = int(input("informe uma temperatura: "))
print(f"\n\tQ03\nA temperatura é: {temp(t)}")