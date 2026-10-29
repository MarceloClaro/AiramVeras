import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
print(f"Total tables: {len(tables)}")
for t in tables:
    count = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    print(f"  {t} ({count} rows)")

conn.close()
