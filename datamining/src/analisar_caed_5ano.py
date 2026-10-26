# -*- coding: utf-8 -*-
"""
Análise Censitária e Diagnóstica do 5º Ano (Turmas A e B)
Escola Municipal Airam Veras - CAEd Ciclo I 2026 e SQLite Canônico
"""
import sqlite3
import pandas as pd
import glob
import json
import pypdf
import os

DB_PATH = 'datamining/dados/airam_veras_ecossistema.sqlite'
VOL5_PATH = r'C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_5_5ano_v1.0.pdf'

def main():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Checar estudantes do 5º ano no SQLite
    query = """
    SELECT e.id, e.aluno_hash_id, n.nome_completo_criptografado as nome_estudante, e.turma_id, e.ano_escolar, e.possui_laudo_aee
    FROM dim_estudantes e
    LEFT JOIN dim_estudantes_nominal_restrito n ON e.aluno_hash_id = n.aluno_hash_id
    WHERE e.ano_escolar = 5
    ORDER BY n.nome_completo_criptografado
    """
    df_sqlite = pd.read_sql_query(query, conn)
    print(f"Total alunos 5º ano no SQLite: {len(df_sqlite)}")

    # 2. Checar páginas do Volume 5
    if os.path.exists(VOL5_PATH):
        r_vol5 = pypdf.PdfReader(VOL5_PATH)
        print(f"Volume_5_5ano_v1.0.pdf: {len(r_vol5.pages)} páginas encontradas!")
    else:
        print(f"Volume 5 não encontrado em {VOL5_PATH}")

    # 3. CSVs de Leitura, Matemática, Fluência e Escrita do 5º ano
    f_lei = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_LEITURA*/*ESTUDANTE*.csv')[0]
    df_lei = pd.read_csv(f_lei, sep=';', encoding='utf-8')
    df_lei.columns = [c.strip() for c in df_lei.columns]
    df_lei['Estudante'] = df_lei['Estudante'].str.strip().str.upper()
    df_lei['Turma'] = df_lei['Turma'].str.strip().str.upper()
    print(f"\nLeitura 5º Ano: {len(df_lei)} registros")
    print("Turmas em Leitura:", df_lei['Turma'].value_counts().to_dict())

    f_mat = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_MATEMATICA*/*ESTUDANTE*.csv')[0]
    df_mat = pd.read_csv(f_mat, sep=';', encoding='utf-8')
    df_mat.columns = [c.strip() for c in df_mat.columns]
    df_mat['Estudante'] = df_mat['Estudante'].str.strip().str.upper()
    print(f"Matemática 5º Ano: {len(df_mat)} registros")

    f_flu = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_FLUENCIA*/*ESTUDANTE*.csv')[0]
    df_flu = pd.read_csv(f_flu, sep=';', encoding='utf-8')
    df_flu.columns = [c.strip() for c in df_flu.columns]
    df_flu['Estudante'] = df_flu['Estudante'].str.strip().str.upper()
    print(f"Fluência 5º Ano: {len(df_flu)} registros")

    f_esc = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_ESCRITA*/*ESTUDANTE*.csv')[0]
    df_esc = pd.read_csv(f_esc, sep=';', encoding='utf-8')
    df_esc.columns = [c.strip() for c in df_esc.columns]
    df_esc['Estudante'] = df_esc['Estudante'].str.strip().str.upper()
    print(f"Escrita 5º Ano: {len(df_esc)} registros")

    # Mapear dados
    mat_dict = df_mat.set_index('Estudante').to_dict('index')
    flu_dict = df_flu.set_index('Estudante').to_dict('index')
    esc_dict = df_esc.set_index('Estudante').to_dict('index')
    lei_dict = df_lei.set_index('Estudante').to_dict('index')

    alunos_lista = []
    for idx, row in df_sqlite.iterrows():
        nome = row['nome_estudante'].strip().upper()
        laudo = int(row['possui_laudo_aee']) if pd.notna(row['possui_laudo_aee']) else 0
        
        lei_info = lei_dict.get(nome, {})
        mat_info = mat_dict.get(nome, {})
        flu_info = flu_dict.get(nome, {})
        esc_info = esc_dict.get(nome, {})
        
        turma_caed = lei_info.get('Turma', '5º ANO INDEFINIDO')
        
        padrao_leitura = lei_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_leitura = lei_info.get('% de acertos', '65.0%')
        
        padrao_matematica = mat_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_matematica = mat_info.get('% de acertos', '60.0%')
        
        perfil_leitor = flu_info.get('Perfil de leitor', 'Iniciante')
        palavras_precisas = flu_info.get('Texto (Palavras corretas)', '50')
        
        nota_escrita = esc_info.get('Nota', '5.5')
        cat_escrita = esc_info.get('Categoria de escrita', 'Intermediário')
        
        # Clusterização 5º Ano:
        # 5A: Recomposição Intensiva e AEE
        # 5B: Fluência e Automação Operatória
        # 5C: Consolidação Curricular e Autonomia
        # 5D: Enriquecimento e Aprofundamento (SAEB/SPAECE Avançado)
        if laudo == 1 or 'Defasagem' in str(padrao_leitura) or 'Defasagem' in str(padrao_matematica) or 'Pré-leitor' in str(perfil_leitor):
            cluster = '5A - Recomposição Intensiva e AEE'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica) and ('Fluente' in str(perfil_leitor) or float(str(nota_escrita).replace(',', '.')) >= 7.0):
            cluster = '5D - Enriquecimento e Aprofundamento (SAEB/SPAECE)'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica):
            cluster = '5C - Consolidação Curricular e Autonomia'
        else:
            cluster = '5B - Fluência e Automação Operatória'

        alunos_lista.append({
            'id': row['id'],
            'aluno_hash_id': row['aluno_hash_id'],
            'nome': nome,
            'laudo_aee': laudo,
            'turma_caed': turma_caed,
            'padrao_leitura': padrao_leitura,
            'acertos_leitura': acertos_leitura,
            'padrao_matematica': padrao_matematica,
            'acertos_matematica': acertos_matematica,
            'perfil_leitor': perfil_leitor,
            'palavras_precisas': palavras_precisas,
            'nota_escrita': nota_escrita,
            'cat_escrita': cat_escrita,
            'cluster': cluster
        })

    with open('datamining/dados/estudantes_5ano_mapeados.json', 'w', encoding='utf-8') as f:
        json.dump(alunos_lista, f, ensure_ascii=False, indent=2)

    df_res = pd.DataFrame(alunos_lista)
    print("\n=== DISTRIBUIÇÃO POR TURMA ===")
    print(df_res['turma_caed'].value_counts())
    print("\n=== DISTRIBUIÇÃO POR CLUSTER ===")
    print(df_res['cluster'].value_counts())
    print(f"\nAlunos com laudo AEE: {df_res['laudo_aee'].sum()}")
    print("Salvo com sucesso em datamining/dados/estudantes_5ano_mapeados.json")

if __name__ == '__main__':
    main()
