import sqlite3
import os

DB_PATH = os.path.join(".", "datamining", "dados", "airam_veras_ecossistema.sqlite")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

print("--- Estudantes do 1º Ano com AEE / Laudo / Cuidador ---")
q = """
SELECT r.nome_completo_criptografado,
       d.possui_laudo_aee,
       cat.codigo_cid,
       cat.descricao_cid,
       perfil.observacoes_clinico_pedagogicas,
       cuid.nome_cuidador,
       cuid.tipo_deficiencia_necessidade,
       cuid.cid_informado
FROM dim_estudantes d
JOIN dim_estudantes_nominal_restrito r ON d.aluno_hash_id = r.aluno_hash_id
LEFT JOIN fato_estudante_aee_perfil perfil ON d.id = perfil.aluno_hash_id OR d.aluno_hash_id = perfil.aluno_hash_id
LEFT JOIN dim_cid_catalogo cat ON perfil.cid_primario_id = cat.id
LEFT JOIN dim_aee_cuidadores_relacao_oficial_2026 cuid ON cuid.aluno_nome_completo = r.nome_completo_criptografado
WHERE d.ano_escolar = 1
ORDER BY r.nome_completo_criptografado;
"""
for row in c.execute(q).fetchall():
    print(row)

print("\n--- Verificando dim_aee_cuidadores_relacao_oficial_2026 para 1º Ano ---")
q2 = """
SELECT aluno_nome_completo, turma, turno, nome_cuidador, tipo_deficiencia_necessidade, cid_informado
FROM dim_aee_cuidadores_relacao_oficial_2026
WHERE turma LIKE '%1%' OR aluno_nome_completo IN (SELECT nome_completo_criptografado FROM dim_estudantes_nominal_restrito WHERE aluno_hash_id IN (SELECT aluno_hash_id FROM dim_estudantes WHERE ano_escolar = 1));
"""
for row in c.execute(q2).fetchall():
    print(row)

conn.close()
