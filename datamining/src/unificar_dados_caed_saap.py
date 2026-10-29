import sqlite3
import pandas as pd

conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')

df_saap_dist = pd.read_sql_query("""
    SELECT DISTINCT aluno_hash_id, nome_estudante, possui_laudo_cid, codigo_cid10,
           diagnostico_resumo, cuidador_dedicado
    FROM fato_saap_avaliacao_bimestral_1ano
    ORDER BY nome_estudante
""", conn)
print("Estudantes distintos no SAAP:", len(df_saap_dist))
for idx, r in df_saap_dist.iterrows():
    print(f"{r['nome_estudante']:<40} | CID: {r['possui_laudo_cid']} | {r['codigo_cid10'] or 'N/A':<15} | Cuidador: {r['cuidador_dedicado'] or 'Nenhum'}")

# Verificar quem esta no CAEd
df_caed_st = pd.read_sql_query("""
    SELECT DISTINCT nr.nome_completo_criptografado as nome_estudante, e.aluno_hash_id
    FROM fato_evolucao_longitudinal_ciclos ev
    JOIN dim_estudantes e ON ev.aluno_hash_id = e.aluno_hash_id
    JOIN dim_estudantes_nominal_restrito nr ON e.aluno_hash_id = nr.aluno_hash_id
    WHERE ev.ano_escolar = 1
    ORDER BY nr.nome_completo_criptografado
""", conn)
print("\nEstudantes distintos no CAEd:", len(df_caed_st))

caed_names = set(df_caed_st['nome_estudante'])
saap_names = set(df_saap_dist['nome_estudante'])

print("\nPresentes no CAEd mas não no SAAP:")
print(caed_names - saap_names)

print("\nPresentes no SAAP mas não no CAEd:")
print(saap_names - caed_names)

conn.close()
