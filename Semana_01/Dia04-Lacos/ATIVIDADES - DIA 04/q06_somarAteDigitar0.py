num = 0
soma = 0
while bool != 0:
    N = float(input(f"Digite o {num+1}º número: "))
    soma+=N 
    num+=1 
    if N == 0: break 
print(soma)

# soma+=N - Pega o valor que o usuário digitou e 
# soma com o valor atribuido anteriormente ( 0 = 0 + N) 
# num+=1 - Contador 1+1 para colocar na pergunta inicial