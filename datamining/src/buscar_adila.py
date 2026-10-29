import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Buscando FRANCISCA ADILA em todas as tabelas:")
for t in ["dim_estudantes_nominal_restrito", "dim_aee_cuidadores_relacao_oficial_2026", "fato_aee_estudo_caso_e_relatorios", "fato_praticas_diarias_leitura_fluencia"]:
    try:
        cols = [col[1] for col in c.execute(f"PRAGMA table_info({t})").fetchall()]
        name_cols = [col for col in cols if "nome" in col.lower() or "aluno" in col.lower()]
        for nc in name_cols:
            rows = c.execute(f"SELECT * FROM {t} WHERE {nc} LIKE '%ADILA%' OR {nc} LIKE '%FRANCISCA%'").fetchall()
            if rows:
                print(f"Table {t}, col {nc}: {len(rows)} rows found")
                for r in rows:
                    print("  ", r)
    except Exception as e:
        print(f"Error {t}: {e}")

conn.close()
