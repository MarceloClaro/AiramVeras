import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("Schema fato_estudante_aee_perfil:")
for col in c.execute("PRAGMA table_info(fato_estudante_aee_perfil)").fetchall():
    print(col)

print("\n1st year students in dim_estudantes_nominal_restrito:")
q = """
SELECT r.id, r.aluno_hash_id, r.nome_completo_criptografado, d.ano_escolar, d.possui_laudo_aee
FROM dim_estudantes_nominal_restrito r
JOIN dim_estudantes d ON r.aluno_hash_id = d.aluno_hash_id
WHERE d.ano_escolar = 1
ORDER BY r.nome_completo_criptografado;
"""
rows = c.execute(q).fetchall()
print(f"Total: {len(rows)}")
for r in rows:
    print(r)

conn.close()
