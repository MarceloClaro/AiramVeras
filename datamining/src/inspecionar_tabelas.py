import sqlite3

conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')
c = conn.cursor()

print("--- dim_estudantes ---")
print([col[1] for col in c.execute('PRAGMA table_info(dim_estudantes)').fetchall()])

print("--- dim_estudantes_nominal_restrito ---")
print([col[1] for col in c.execute('PRAGMA table_info(dim_estudantes_nominal_restrito)').fetchall()])

print("--- fato_participacao_estudante ---")
print([col[1] for col in c.execute('PRAGMA table_info(fato_participacao_estudante)').fetchall()])

print("\n--- Sample 1 ano students ---")
c.execute("SELECT id, aluno_hash_id, turma_ano FROM dim_estudantes WHERE turma_ano LIKE '%1%' LIMIT 5")
for r in c.fetchall():
    print(r)

print("\n--- Sample nominal restrito ---")
c.execute("SELECT * FROM dim_estudantes_nominal_restrito LIMIT 5")
for r in c.fetchall():
    print(r)

conn.close()
