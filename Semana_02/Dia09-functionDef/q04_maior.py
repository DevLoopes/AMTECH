num = []   
def maior(num):
    for i in range(1, 5 + 1, 1):
        numb = int(input(f"Digite o número {i}: "))
        num.append([numb])
    return max(num)
print(f"\n\tQ04\nO Maior é: {maior(num)}")