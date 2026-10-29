import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("--- Estudantes do 1º Ano no Banco de Dados ---")
query = """
SELECT id_estudante, nome_estudante, turma, turno, is_paee, possui_pei, possui_laudo_aee, status_resultado
FROM dim_estudantes
WHERE turma LIKE '%1%'
ORDER BY nome_estudante;
"""
for row in c.execute(query).fetchall():
    print(row)

print("\n--- Verificando laudos / CID do 1º Ano ---")
query_aee = """
SELECT e.nome_estudante, a.diagnostico_laudo, a.cid10, a.cid11, a.status_laudo, a.cuidador_dedicado
FROM dim_estudantes e
LEFT JOIN fato_estudante_aee_perfil a ON e.id_estudante = a.id_estudante
WHERE e.turma LIKE '%1%' AND (e.is_paee = 1 OR a.id_estudante IS NOT NULL OR e.possui_laudo_aee = 1)
ORDER BY e.nome_estudante;
"""
for row in c.execute(query_aee).fetchall():
    print(row)

conn.close()
