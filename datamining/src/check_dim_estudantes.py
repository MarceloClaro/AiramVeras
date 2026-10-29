import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Schema dim_estudantes:")
for col in c.execute("PRAGMA table_info(dim_estudantes)").fetchall():
    print(col)

print("\nSample 1st row:")
r = c.execute("SELECT * FROM dim_estudantes LIMIT 1").fetchone()
print(r)

conn.close()
