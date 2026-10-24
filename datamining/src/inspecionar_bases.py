import sqlite3
from pathlib import Path

root = Path("c:/Users/marce/Downloads/Airam veras")
dbs = list(root.glob("**/*.sqlite*"))
for db in dbs:
    if ".venv" in db.parts:
        continue
    print(f"\n=== DB: {db} ===")
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cur.fetchall()]
        print("Tables:", tables)
        for t in tables[:5]:
            cur.execute(f"SELECT COUNT(*) FROM {t}")
            cnt = cur.fetchone()[0]
            print(f"  - {t}: {cnt} rows")
        conn.close()
    except Exception as e:
        print("Error:", e)
