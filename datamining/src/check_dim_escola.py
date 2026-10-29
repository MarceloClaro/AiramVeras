import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Columns of dim_escola:")
for col in c.execute("PRAGMA table_info(dim_escola)").fetchall():
    print(col)

print("\nContent of dim_escola:")
for row in c.execute("SELECT * FROM dim_escola").fetchall():
    print(row)

conn.close()
