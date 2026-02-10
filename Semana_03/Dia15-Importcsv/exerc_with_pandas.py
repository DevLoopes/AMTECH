import pandas as pd
import numpy as np
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
arqv = open(base_dir + "/src/alunos_notas.csv", "r", encoding="utf-8")

df = pd.read_csv(arqv)

# ====== Question 01 ======
# print(df[["aluno_id","nome","turma","idade","cidade","disciplina","prova1","prova2","trabalho","faltas","data_matricula"]].head(8))

# ====== Question 02 ======
# print(df.dtypes()) # Detalhes da coluna

# ====== Question 03 ======
# print(df.info()) # Detalhes do tip

# ====== Question 04 ======
df["media"] = (df["prova1"]*0.4 + df["prova2"]*0.4 + df["trabalho"]*0.2).round(1)
# print(df.head())

# ====== Question 05 ======
# df["Aprovado"] = df["media"] >= 6.0

# ====== Question 06 ======
# df["Reprovado"] = df["media"] < 6.0

# ====== Question 07 ======
# df["ReprovadoFalta"] = df["faltas"] >= 5

# SITUAÇÂO DO ALUNO QUEST 08, 09, 10
df["status"] = np.where(df["faltas"] >= 5, "ReprovadoFalta",
                    np.where(df["media"] >= 6, "Aprovado","Reprovado"))
# print(df.head(8))

# ====== Question 08 ======
alunosManaus = df[df["cidade"] == "Manaus"]

infoReprovadosNotas = alunosManaus[df["media"] < 6]
print("\n==== Dados dos alunos reprovados por notas de Manaus ===")
print(infoReprovadosNotas[["aluno_id","nome","turma","idade","status","cidade"]])

infoReprovadosFaltas = alunosManaus[df["faltas"] >= 5]
print("\n==== Dados dos alunos reprovados por faltas de Manaus ===")
print(infoReprovadosFaltas[["aluno_id","nome","turma","idade","status","cidade"]])

# ====== Question 09 ======
alunosManacapuru = df[df["cidade"] == "Manacapuru"]

infoAprovadosNotas = alunosManacapuru[df["media"] >= 6]
print("\n==== Dados dos alunos aprovados de Manaus ===")
print(infoAprovadosNotas[["aluno_id","nome","turma","idade", "status", "cidade"]])

# ====== Question 10 ======


# print(df[["aluno_id","nome","turma","idade","cidade","disciplina","prova1","prova2","trabalho", "media", "faltas","data_matricula"]])