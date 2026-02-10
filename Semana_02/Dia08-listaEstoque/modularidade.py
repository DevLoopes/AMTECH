import math
def de_boas_vindas():
    print("Olá, seja bem vinde!\n")
de_boas_vindas()

op = 0

while op != -1:
    
    op = int(input("\n1 - SOMA\n2 - SUB\n3 - MULT\n4 - DIV\n5- RAIZ\n6 - RAIO\n7 - RAIZ CUBICA\n8 - POTENCIA\nDIGITE -1 PARA SAIR\n\tSELECT OPTION: "))
    
    if op == 1 or op == 2 or op == 3 or op == 4:
        x = input(f"\nDigite o 1º valor: ")
        y = input(f"Digite o 2º valor: ")
    
    if op == 1:
        def soma(x, y):
            return x+y
        print(f"\nA soma é: {soma(x, y)}")
        
    elif op == 2:
        def sub(x, y):
            return x-y
        print(f"\nA subtração é: {sub(x,y)}")
        
    elif op == 3:
        def mult(x, y):
            return x*y
        print(f"\nA multiplicação é: {mult(x,y)}")
        
    elif op == 4:
        def div(x, y):
            return x/y
        print(f"\nA divisão é: {div(x,y)}")
        
    elif op == 5:
        def area_circle(r):
            return math.pi * r * r
        raio = float(input('Raio: '))
        print(f'Área: {area_circle(raio):.2f}\n')
        
    elif op == 6:
        def Calc_raiz(r):
            return math.sqrt(r)
        raio = float(input('Raio: '))
        print(f'Raiz é: {Calc_raiz(raio):.2f}\n')
        
    elif op == 7:
        def raiz_cubica(r):
            return math.pow(r,1/3)  
    elif op == 8:
        def potencia(r):
            return math.pow(r,3)
    elif op == -1:
        break
        
        

    

    

    
    
    
    

    

    