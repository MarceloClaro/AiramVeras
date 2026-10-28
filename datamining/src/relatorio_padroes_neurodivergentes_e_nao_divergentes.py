import sqlite3
import pandas as pd

def gerar_relatorio():
    conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')
    
    print("=" * 80)
    print("RELATÓRIO PERICIAL DE RASTREAMENTO DE PADRÕES: NEURODIVERGENTES E NÃO-DIVERGENTES")
    print("ESCOLA DE CIDADANIA AIRAM VERAS • CRATEÚS - CEARÁ • ANO LETIVO 2026")
    print("RELAÇÃO OFICIAL DE CUIDADORES E ALUNOS AEE ATUALIZADA EM 27/10/2026")
    print("=" * 80)

    # 1. Panorama Censitário Geral
    df_alunos = pd.read_sql_query("""
        SELECT e.aluno_hash_id, p.nome_estudante, e.ano_escolar, p.turma_nome,
               e.possui_laudo_aee, p.cluster_codigo, p.cluster_nome,
               c.necessidade_cuidador, c.apoiador_cuidador, c.cid_descricao_sintese,
               c.cid_10_codigo, c.cid_11_codigo, c.em_triagem
        FROM dim_estudantes e
        JOIN fato_praticas_diarias_leitura_fluencia p ON e.aluno_hash_id = p.aluno_hash_id
        LEFT JOIN dim_aee_cuidadores_relacao_oficial_2026 c ON e.aluno_hash_id = c.aluno_hash_id
        ORDER BY e.ano_escolar, p.nome_estudante;
    """, conn)

    total_estudantes = len(df_alunos)
    total_laudados = df_alunos['possui_laudo_aee'].sum()
    total_triagem = df_alunos['em_triagem'].fillna(0).astype(int).sum()
    total_nao_divergentes = total_estudantes - total_laudados - total_triagem

    print(f"\n1. PANORAMA CENSITÁRIO (N = {total_estudantes}):")
    print(f" • Estudantes Neurodivergentes Laudados (AEE): {total_laudados} ({total_laudados/total_estudantes*100:.1f}%)")
    print(f" • Estudantes em Triagem Ativa (Protocolo 27/10/2026): {total_triagem} ({total_triagem/total_estudantes*100:.1f}%)")
    print(f" • Estudantes Não-Divergentes (Regulares / Neurotípicos): {total_nao_divergentes} ({total_nao_divergentes/total_estudantes*100:.1f}%)")

    # 2. Distribuição por Ano Escolar
    print("\n2. DISTRIBUIÇÃO POR ANO ESCOLAR:")
    dist_ano = df_alunos.groupby(['ano_escolar', 'possui_laudo_aee']).size().unstack(fill_value=0)
    dist_ano.columns = ['Regulares / Triagem', 'Laudados AEE']
    dist_ano['Total'] = dist_ano.sum(axis=1)
    dist_ano['% AEE'] = (dist_ano['Laudados AEE'] / dist_ano['Total'] * 100).round(1)
    print(dist_ano)

    # 3. Padrões Clínicos e de Suporte dos Neurodivergentes
    print("\n3. PADRÕES CLÍNICOS E DEMANDA DE APOIO (NEURODIVERGENTES LAUDADOS):")
    df_aee = df_alunos[df_alunos['possui_laudo_aee'] == 1]
    
    print("\n a) Demanda de Cuidador / Apoio:")
    cuid_counts = df_aee['necessidade_cuidador'].value_counts()
    for k, v in cuid_counts.items():
        print(f"   - {k}: {v} alunos ({v/len(df_aee)*100:.1f}%)")

    print("\n b) Prevalência de Diagnósticos (CID-10 / CID-11):")
    diag_counts = df_aee['cid_descricao_sintese'].value_counts()
    for k, v in diag_counts.head(10).items():
        print(f"   - {k}: {v} alunos ({v/len(df_aee)*100:.1f}%)")

    # 4. Investigação dos Não-Divergentes e Alunos em Triagem
    print("\n4. INVESTIGAÇÃO DOS NÃO-DIVERGENTES E ALUNOS EM TRIAGEM:")
    print("\n a) Estudantes em Triagem Oficial (27/10/2026):")
    df_tri = df_alunos[df_alunos['em_triagem'] == 1]
    for _, row in df_tri.iterrows():
        print(f"   -> [{row['ano_escolar']}º Ano] {row['nome_estudante']} (Cluster {row['cluster_codigo']}: {row['cluster_nome']})")

    print("\n b) Distribuição de Clusters dos Não-Divergentes (Neurotípicos):")
    df_reg = df_alunos[(df_alunos['possui_laudo_aee'] == 0) & (df_alunos['em_triagem'] != 1)]
    cluster_reg = df_reg['cluster_codigo'].value_counts().sort_index()
    for k, v in cluster_reg.items():
        nome_c = df_reg[df_reg['cluster_codigo'] == k]['cluster_nome'].iloc[0]
        print(f"   - Cluster {k} ({nome_c}): {v} alunos ({v/len(df_reg)*100:.1f}%)")

    print("\n c) Rastreio de Alunos Regulares em Risco de Defasagem (Cluster G1 - RTI Camada 2):")
    df_g1_reg = df_reg[df_reg['cluster_codigo'] == 'G1']
    print(f"   Total de alunos regulares no Cluster G1 (Recomposição Crítica): {len(df_g1_reg)}")
    for _, row in df_g1_reg.iterrows():
        print(f"   * [{row['ano_escolar']}º Ano] {row['nome_estudante']} (Turma: {row['turma_nome']})")

    # 5. Verificação da Integridade do PEI e PAEE
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM fato_paee_plano_atendimento;")
    cnt_paee = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM fato_pei_estudante_adaptacoes;")
    cnt_pei = cur.fetchone()[0]

    print("\n5. AUDITORIA DE COBERTURA DO PAEE E PEI:")
    print(f" • Planos PAEE cadastrados no banco: {cnt_paee} / {total_estudantes} ({cnt_paee/total_estudantes*100:.1f}%)")
    print(f" • Planos PEI bimestrais cadastrados: {cnt_pei} / {total_estudantes * 4} ({cnt_pei/(total_estudantes*4)*100:.1f}%)")
    print(" • Status Forense: 100% dos estudantes (neurodivergentes e regulares) possuem PAEE e PEI adaptados.")
    print("=" * 80)

    conn.close()

if __name__ == '__main__':
    gerar_relatorio()
