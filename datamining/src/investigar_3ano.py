import sqlite3
import glob
import os
import zipfile
import pandas as pd

db_path = 'datamining/dados/airam_veras_ecossistema.sqlite'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("--- Consultando dim_turmas ---")
cur.execute("SELECT * FROM dim_turmas")
for r in cur.fetchall():
    print(dict(r))

print("\n--- Consultando dim_estudantes por ano_escolar / turma ---")
try:
    cur.execute("SELECT ano_escolar, COUNT(*) as total FROM dim_estudantes GROUP BY ano_escolar")
    for r in cur.fetchall():
        print(f"ano_escolar: {r['ano_escolar']} -> {r['total']} alunos")
except Exception as e:
    print(f"Erro: {e}")

try:
    cur.execute("SELECT t.ano_escolar, t.nome_turma, COUNT(e.id) as total FROM dim_estudantes e JOIN dim_turmas t ON e.turma_id = t.id GROUP BY t.ano_escolar, t.nome_turma")
    for r in cur.fetchall():
        print(f"Turma {r['nome_turma']} ({r['ano_escolar']}): {r['total']} alunos")
except Exception as e:
    print(f"Erro join: {e}")

print("\n--- Descompactando ZIPs restantes do 3º Ano ---")
for modalidade in ['3ANO_ESCRITA_CICLO_I_2026', '3ANO_LEITURA_CICLO_I_2026', '3ANO_FLUENCIA_CICLO_I_2026', '3ANO_MATEMATICA_CICLO_I_2026']:
    zip_p = f"resultados-caed-ciclo-i-2026/originais/{modalidade}.zip"
    dest_dir = f"resultados-caed-ciclo-i-2026/csv_originais/{modalidade}"
    os.makedirs(dest_dir, exist_ok=True)
    if os.path.exists(zip_p):
        with zipfile.ZipFile(zip_p, 'r') as zf:
            zf.extractall(dest_dir)
        print(f"Extraído com sucesso: {dest_dir} ({len(os.listdir(dest_dir))} arquivos)")

print("\n--- Analisando Alunos do 3º Ano nos CSVs CAEd ---")
csv_estudantes_leitura = glob.glob("resultados-caed-ciclo-i-2026/csv_originais/3ANO_LEITURA_CICLO_I_2026/*ESTUDANTE*.csv")
if csv_estudantes_leitura:
    df_l = pd.read_csv(csv_estudantes_leitura[0], sep=';', encoding='utf-8-sig', on_bad_lines='skip')
    print(f"Leitura 3º Ano CSV colunas: {list(df_l.columns[:10])}")
    print(f"Total registros leitura: {len(df_l)}")
    if 'Estudante' in df_l.columns:
        print(f"Total estudantes únicos Leitura: {df_l['Estudante'].nunique()}")
        print(f"Exemplo estudantes: {df_l['Estudante'].unique()[:5]}")

csv_estudantes_mat = glob.glob("resultados-caed-ciclo-i-2026/csv_originais/3ANO_MATEMATICA_CICLO_I_2026/*ESTUDANTE*.csv")
if csv_estudantes_mat:
    df_m = pd.read_csv(csv_estudantes_mat[0], sep=';', encoding='utf-8-sig', on_bad_lines='skip')
    print(f"Matemática 3º Ano CSV colunas: {list(df_m.columns[:10])}")
    print(f"Total registros mat: {len(df_m)}")
    if 'Estudante' in df_m.columns:
        print(f"Total estudantes únicos Matemática: {df_m['Estudante'].nunique()}")


