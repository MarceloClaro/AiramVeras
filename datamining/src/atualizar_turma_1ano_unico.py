import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "..", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

print("Turmas antes:")
for r in cur.execute("SELECT * FROM dim_turmas"):
    print(r)

cur.execute("UPDATE dim_turmas SET nome_turma = '1º ANO ÚNICO' WHERE ano_escolar = 1 OR id = 1;")
conn.commit()

print("\nTurmas depois:")
for r in cur.execute("SELECT * FROM dim_turmas"):
    print(r)

conn.close()
