import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("Turmas antes:")
for r in cur.execute("SELECT * FROM dim_turmas"):
    print(r)

cur.execute("UPDATE dim_turmas SET nome_turma = '1º ANO ÚNICO' WHERE id = 1;")
cur.execute("UPDATE dim_turmas SET nome_turma = '2º ANO ÚNICO' WHERE id = 2;")
cur.execute("UPDATE dim_turmas SET nome_turma = '3º ANO ÚNICO' WHERE id = 3;")
cur.execute("UPDATE dim_turmas SET nome_turma = '4º ANO (TURMAS A E B)' WHERE id = 4;")
cur.execute("UPDATE dim_turmas SET nome_turma = '5º ANO (TURMAS A E B)' WHERE id = 5;")
conn.commit()

print("\nTurmas depois:")
for r in cur.execute("SELECT * FROM dim_turmas"):
    print(r)

conn.close()
