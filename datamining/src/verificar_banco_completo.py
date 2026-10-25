import sqlite3

conn = sqlite3.connect(r'datamining/dados/airam_veras_ecossistema.sqlite')
cur = conn.cursor()
tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name").fetchall()]
print(f"Total tables: {len(tables)}")
print("Tables list:")
for t in tables:
    cnt = cur.execute(f"SELECT COUNT(*) FROM '{t}'").fetchone()[0]
    print(f"  - {t}: {cnt} rows")

fk_violations = cur.execute("PRAGMA foreign_key_check").fetchall()
print(f"\nFK violations count: {len(fk_violations)}")
if fk_violations:
    print("Violations:", fk_violations)

conn.close()
