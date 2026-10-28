import sqlite3

def inspecionar():
    conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')
    cur = conn.cursor()

    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]
    print(f"Total de tabelas no banco: {len(tables)}")
    
    print("\n=== TABELAS RELACIONADAS A ESTUDANTES, LAUDOS, PEI E PAEE ===")
    for t in tables:
        if any(k in t.lower() for k in ['estudante', 'aluno', 'laudo', 'aee', 'pei', 'paee', 'neuro', 'saude', 'cuidador', 'praticas']):
            cur.execute(f"PRAGMA table_info({t});")
            cols = [c[1] for c in cur.fetchall()]
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            cnt = cur.fetchone()[0]
            print(f"- {t} ({cnt} registros) -> Colunas: {cols[:8]}...")

    # Verificar turmas e contagem em dim_estudante
    if 'dim_estudante' in tables:
        cur.execute("SELECT ano_escolar, count(*) FROM dim_estudante GROUP BY ano_escolar;")
        print("\n=== ESTUDANTES POR ANO ESCOLAR EM dim_estudante ===")
        for row in cur.fetchall():
            print(f" Ano {row[0]}: {row[1]} alunos")

    conn.close()

if __name__ == '__main__':
    inspecionar()
