
print("=====================================\n\tVETOR\n=====================================")
vetor = ['Python', 'Html', 'CSS', 'C', 'Java']

#Q1
vetor.append('C#')
print("\nvetor: ", vetor)

#Q2
vetor.reverse()
print("\nvetor: ", vetor)

#Q3
print("\\Primeiro elemento: ", vetor[0])

#Q4
print("\nPrimeiro caractere do 2º elemento: ", vetor[1][0])

#Q5
print("\nPosição 2: ", vetor[2])

#Q6
print("\nPosição 1 sem o 1º caractere: ", vetor[1][1:])

#Q7
print("\nPrimeiro Caractere de cada elemento: ")
for x in range(len(vetor)):
    vetores = vetor[x][0]
    print("\nvetor: ", vetores)
    
#Q8
if "PHP" in vetor:
    print("\nFaz parte da lista")
else:
    print("\nFaz parte da lista")


#Q9
print("\nQuantidade da lista: ", len(vetor))

#Q10
nova_list = []
for x in range(len(vetor)):
    nova_list.append(len(vetor[x]))
print("\nNova Lista: ", nova_list)

#Q11
print("\nMaior Elemanto: ", max(nova_list), "\nMenor Elemento: ", min(nova_list))
    





