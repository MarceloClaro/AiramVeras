import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Schema dim_estudantes_nominal_restrito:")
for col in c.execute("PRAGMA table_info(dim_estudantes_nominal_restrito)").fetchall():
    print(col)

print("\nAlunos do 1º Ano em dim_estudantes_nominal_restrito:")
query = """
SELECT r.id, r.aluno_hash_id, r.nome_completo_criptografado, d.ano_escolar, d.possui_laudo_aee,
       a.diagnostico_laudo, a.cid10, a.cid11, a.status_laudo, a.cuidador_dedicado
FROM dim_estudantes_nominal_restrito r
JOIN dim_estudantes d ON r.aluno_hash_id = d.aluno_hash_id
LEFT JOIN fato_estudante_aee_perfil a ON d.id = a.id_estudante
WHERE d.ano_escolar = 1
ORDER BY r.nome_completo_criptografado;
"""
for row in c.execute(query).fetchall():
    print(row)

conn.close()
