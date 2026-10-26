import pypdf
import os
import sqlite3
import pandas as pd

f1_path = 'Dossie_Integrado_1e2_Airam_Veras_2026_Fonico_Kumon_CAPA_PADRAO.pdf'
if os.path.exists(f1_path):
    r1 = pypdf.PdfReader(f1_path)
    print(f"F1 total pages: {len(r1.pages)}")

vol3_paths = [
    r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_3ano_v1.0.pdf",
    r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_3ano_v1.1.pdf",
    r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_3ano_v1.2.pdf",
    r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_2e3ano.pdf",
]
for vp in vol3_paths:
    if os.path.exists(vp):
        rv = pypdf.PdfReader(vp)
        print(f"Volume: {os.path.basename(vp)} -> {len(rv.pages)} páginas")

db_path = 'datamining/dados/airam_veras_ecossistema.sqlite'
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

print("\n--- Alunos do 3º Ano em dim_estudantes ---")
cur.execute("""
    SELECT e.id, e.aluno_hash_id, e.nome_estudante, e.genero, e.ano_escolar, e.turma_id
    FROM dim_estudantes e
    WHERE e.ano_escolar = 3
    ORDER BY e.nome_estudante
""")
alunos_3ano = cur.fetchall()
print(f"Total alunos 3º ano no banco: {len(alunos_3ano)}")
for a in alunos_3ano[:5]:
    print(dict(a))

print("\n--- Desempenho dos Alunos do 3º Ano em vw_estudante_raiox_360 ---")
cur.execute("""
    SELECT aluno_hash_id, ano_escolar, acerto_lp_pct, nivel_caed_lp, meta_b_lp,
           acerto_mat_pct, nivel_caed_mat, meta_b_mat, estagio_fonico_atual,
           nivel_kumon_mat_atual, nivel_kumon_leit_atual, probabilidade_risco_defasagem,
           nivel_risco_ews, protocolo_intervencao_sugerido
    FROM vw_estudante_raiox_360
    WHERE ano_escolar = 3
    LIMIT 5
""")
raiox = cur.fetchall()
print(f"Encontrados no Raio-X 360: {len(raiox)}")
for r in raiox:
    print(dict(r))
