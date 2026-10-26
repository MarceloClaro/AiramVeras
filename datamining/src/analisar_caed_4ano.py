# -*- coding: utf-8 -*-
"""
Análise Censitária e Diagnóstica do 4º Ano (Turmas A e B)
Escola Municipal Airam Veras - CAEd Ciclo I 2026 e SQLite Canônico
"""
import sqlite3
import pandas as pd
import glob
import os

DB_PATH = 'datamining/dados/airam_veras_ecossistema.sqlite'

def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=== TURMAS REGISTRADAS NO SQLITE ===")
    cursor.execute("SELECT id, turma_codigo, ano_escolar, nome_turma, turno FROM dim_turmas")
    for r in cursor.fetchall():
        print(r)

    print("\n=== ESTUDANTES 4º ANO NO SQLITE ===")
    query = """
    SELECT e.id, e.aluno_hash_id, n.nome_completo_criptografado as nome_estudante, e.turma_id, t.nome_turma, t.turma_codigo, e.ano_escolar, e.possui_laudo_aee
    FROM dim_estudantes e
    LEFT JOIN dim_estudantes_nominal_restrito n ON e.aluno_hash_id = n.aluno_hash_id
    LEFT JOIN dim_turmas t ON e.turma_id = t.id
    WHERE e.ano_escolar = 4 OR t.ano_escolar = 4
    ORDER BY t.turma_codigo, n.nome_completo_criptografado
    """
    df_sqlite_alunos = pd.read_sql_query(query, conn)
    print(f"Total de estudantes do 4º ano no SQLite: {len(df_sqlite_alunos)}")
    print(df_sqlite_alunos.to_string())

    print("\n=== CSVs ORIGINAIS DO 4º ANO CAED CICLO I 2026 ===")
    csv_paths = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/4ANO*/*.csv')
    for p in sorted(csv_paths):
        filename = os.path.basename(p)
        folder = os.path.basename(os.path.dirname(p))
        try:
            df = pd.read_csv(p, sep=';', encoding='utf-8')
        except Exception:
            try:
                df = pd.read_csv(p, sep=';', encoding='latin1')
            except Exception:
                df = pd.read_csv(p, sep=',', encoding='utf-8')
        
        print(f"\n--- Pasta: {folder} | Arquivo: {filename} ---")
        print(f"Shape: {df.shape}")
        print("Colunas:", df.columns.tolist()[:10])
        
        turma_col = [c for c in df.columns if 'TURMA' in c.upper()]
        aluno_col = [c for c in df.columns if 'ESTUDANTE' in c.upper() or 'ALUNO' in c.upper()]
        
        if turma_col:
            t_col = turma_col[0]
            print(f"Turmas em {t_col}:", df[t_col].value_counts().to_dict())
        
        if aluno_col:
            a_col = aluno_col[0]
            print(f"Alunos únicos em {a_col}: {df[a_col].nunique()}")
            if turma_col:
                for turma, group in df.groupby(turma_col[0]):
                    print(f"  Turma {turma}: {group[a_col].nunique()} estudantes únicos")

if __name__ == '__main__':
    main()
