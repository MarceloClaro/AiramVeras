import sqlite3

conn = sqlite3.connect("datamining/dados/airam_veras_ecossistema.sqlite")
cur = conn.cursor()

print("Colunas de sys_trilha_auditoria:")
cur.execute("PRAGMA table_info(sys_trilha_auditoria);")
for col in cur.fetchall():
    print(" ", col)

print("\nAmostra de dim_estudantes:")
cur.execute("PRAGMA table_info(dim_estudantes);")
for col in cur.fetchall():
    print(" ", col)

cur.execute("SELECT aluno_hash_id, turma_id, ano_escolar FROM dim_estudantes LIMIT 10;")
for row in cur.fetchall():
    print(" ", row)

cur.execute("SELECT DISTINCT turma_id, ano_escolar FROM dim_estudantes;")
print("\nTurmas distintas:")
for row in cur.fetchall():
    print(" ", row)

conn.close()
