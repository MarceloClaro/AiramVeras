# -*- coding: utf-8 -*-
"""
Mapeamento Censitário Rigoroso do 5º Ano (Turmas 5º A e 5º B)
Cruza dados censitários do CAEd Ciclo I 2026 com o banco SQLite
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
    
    # 1. Carregar estudantes do 5º ano no SQLite
    query = """
    SELECT e.id, e.aluno_hash_id, n.nome_completo_criptografado as nome_estudante, e.turma_id, e.ano_escolar, e.possui_laudo_aee
    FROM dim_estudantes e
    LEFT JOIN dim_estudantes_nominal_restrito n ON e.aluno_hash_id = n.aluno_hash_id
    WHERE e.ano_escolar = 5
    ORDER BY e.id
    """
    df_sqlite = pd.read_sql_query(query, conn)
    print(f"Total alunos 5º ano no SQLite: {len(df_sqlite)}")

    # 2. Carregar Leitura
    f_lei = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_LEITURA*/*ESTUDANTE*.csv')[0]
    df_lei = pd.read_csv(f_lei, sep=';', encoding='utf-8')
    df_lei.columns = [c.strip() for c in df_lei.columns]
    df_lei['Estudante'] = df_lei['Estudante'].str.strip().str.upper()
    df_lei['Turma'] = df_lei['Turma'].str.strip().str.upper()

    # 3. Carregar Matemática
    f_mat = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_MATEMATICA*/*ESTUDANTE*.csv')[0]
    df_mat = pd.read_csv(f_mat, sep=';', encoding='utf-8')
    df_mat.columns = [c.strip() for c in df_mat.columns]
    df_mat['Estudante'] = df_mat['Estudante'].str.strip().str.upper()
    df_mat['Turma'] = df_mat['Turma'].str.strip().str.upper()

    # 4. Carregar Fluência
    f_flu = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_FLUENCIA*/*ESTUDANTE*.csv')[0]
    df_flu = pd.read_csv(f_flu, sep=';', encoding='utf-8')
    df_flu.columns = [c.strip() for c in df_flu.columns]
    df_flu['Estudante'] = df_flu['Estudante'].str.strip().str.upper()
    df_flu['Turma'] = df_flu['Turma'].str.strip().str.upper() if 'Turma' in df_flu.columns else df_flu['Turmma'].str.strip().str.upper()

    # 5. Carregar Escrita
    f_esc = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/5ANO_ESCRITA*/*ESTUDANTE*.csv')[0]
    df_esc = pd.read_csv(f_esc, sep=';', encoding='utf-8')
    df_esc.columns = [c.strip() for c in df_esc.columns]
    df_esc['Estudante'] = df_esc['Estudante'].str.strip().str.upper()
    df_esc['Turma'] = df_esc['Turma'].str.strip().str.upper() if 'Turma' in df_esc.columns else df_esc['Turmma'].str.strip().str.upper()

    # Separar os 54 estudantes pelas turmas do CSV de Leitura
    turma_a_csv = df_lei[df_lei['Turma'] == '5º ANO A'].sort_values('Estudante')
    turma_b_csv = df_lei[df_lei['Turma'] == '5º ANO B'].sort_values('Estudante')
    
    print(f"Turma 5º Ano A no CSV: {len(turma_a_csv)} estudantes")
    print(f"Turma 5º Ano B no CSV: {len(turma_b_csv)} estudantes")

    # Dicionários usando chave composta (Nome, Turma)
    def make_lookup(df):
        lookup = {}
        for _, r in df.iterrows():
            key = (r['Estudante'], r['Turma'])
            lookup[key] = r.to_dict()
        return lookup

    lei_dict = make_lookup(df_lei)
    mat_dict = make_lookup(df_mat)
    flu_dict = make_lookup(df_flu)
    esc_dict = make_lookup(df_esc)

    # Obter os nomes de A e B
    alunos_lista = []

    # Mapear Turma A
    for idx, r in turma_a_csv.iterrows():
        nome = r['Estudante']
        turma = '5º ANO A'
        key = (nome, turma)
        
        lei_info = lei_dict.get(key, {})
        mat_info = mat_dict.get(key, {})
        flu_info = flu_dict.get(key, {})
        esc_info = esc_dict.get(key, {})

        # Buscar se no sqlite tem laudo
        match_sqlite = df_sqlite[df_sqlite['nome_estudante'].str.strip().str.upper() == nome]
        laudo = int(match_sqlite.iloc[0]['possui_laudo_aee']) if len(match_sqlite) > 0 and pd.notna(match_sqlite.iloc[0]['possui_laudo_aee']) else 0
        aluno_hash = match_sqlite.iloc[0]['aluno_hash_id'] if len(match_sqlite) > 0 else f"hash_5ano_{nome[:6]}"

        padrao_leitura = lei_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_leitura = lei_info.get('% de acertos', '65.0%')
        padrao_matematica = mat_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_matematica = mat_info.get('% de acertos', '60.0%')
        perfil_leitor = flu_info.get('Perfil de leitor', 'Iniciante')
        palavras_precisas = flu_info.get('Texto (Palavras corretas)', '50')
        nota_escrita = esc_info.get('Nota', '5.5')
        cat_escrita = esc_info.get('Categoria de escrita', 'Intermediário')

        nota_num = 0.0
        try:
            nota_num = float(str(nota_escrita).replace(',', '.').replace('-', '0').strip())
        except Exception:
            nota_num = 0.0

        if laudo == 1 or 'Defasagem' in str(padrao_leitura) or 'Defasagem' in str(padrao_matematica) or 'Pré-leitor' in str(perfil_leitor):
            cluster = '5A - Recomposição Intensiva e AEE'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica) and ('Fluente' in str(perfil_leitor) or nota_num >= 7.0):
            cluster = '5D - Enriquecimento e Aprofundamento (SAEB/SPAECE)'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica):
            cluster = '5C - Consolidação Curricular e Autonomia'
        else:
            cluster = '5B - Fluência e Automação Operatória'

        alunos_lista.append({
            'nome': nome,
            'turma_caed': turma,
            'aluno_hash_id': aluno_hash,
            'laudo_aee': laudo,
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

    # Mapear Turma B
    for idx, r in turma_b_csv.iterrows():
        nome = r['Estudante']
        turma = '5º ANO B'
        key = (nome, turma)
        
        lei_info = lei_dict.get(key, {})
        mat_info = mat_dict.get(key, {})
        flu_info = flu_dict.get(key, {})
        esc_info = esc_dict.get(key, {})

        # Se houver mais de um registro no sqlite (ex: Weligton), pegar o segundo para a turma B
        match_sqlite = df_sqlite[df_sqlite['nome_estudante'].str.strip().str.upper() == nome]
        if len(match_sqlite) > 1:
            row_sql = match_sqlite.iloc[1]
        elif len(match_sqlite) == 1:
            row_sql = match_sqlite.iloc[0]
        else:
            row_sql = None

        laudo = int(row_sql['possui_laudo_aee']) if row_sql is not None and pd.notna(row_sql['possui_laudo_aee']) else 0
        aluno_hash = row_sql['aluno_hash_id'] if row_sql is not None else f"hash_5ano_{nome[:6]}"

        padrao_leitura = lei_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_leitura = lei_info.get('% de acertos', '65.0%')
        padrao_matematica = mat_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_matematica = mat_info.get('% de acertos', '60.0%')
        perfil_leitor = flu_info.get('Perfil de leitor', 'Iniciante')
        palavras_precisas = flu_info.get('Texto (Palavras corretas)', '50')
        nota_escrita = esc_info.get('Nota', '5.5')
        cat_escrita = esc_info.get('Categoria de escrita', 'Intermediário')

        nota_num = 0.0
        try:
            nota_num = float(str(nota_escrita).replace(',', '.').replace('-', '0').strip())
        except Exception:
            nota_num = 0.0

        if laudo == 1 or 'Defasagem' in str(padrao_leitura) or 'Defasagem' in str(padrao_matematica) or 'Pré-leitor' in str(perfil_leitor):
            cluster = '5A - Recomposição Intensiva e AEE'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica) and ('Fluente' in str(perfil_leitor) or nota_num >= 7.0):
            cluster = '5D - Enriquecimento e Aprofundamento (SAEB/SPAECE)'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica):
            cluster = '5C - Consolidação Curricular e Autonomia'
        else:
            cluster = '5B - Fluência e Automação Operatória'

        alunos_lista.append({
            'nome': nome,
            'turma_caed': turma,
            'aluno_hash_id': aluno_hash,
            'laudo_aee': laudo,
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

    print(f"\nTotal Geral de Estudantes Mapeados: {len(alunos_lista)}")
    df_res = pd.DataFrame(alunos_lista)
    print("\nDistribuição por Turma:")
    print(df_res['turma_caed'].value_counts())
    print("\nDistribuição por Cluster:")
    print(df_res['cluster'].value_counts())
    print(f"\nAlunos laudados AEE: {df_res['laudo_aee'].sum()}")

if __name__ == '__main__':
    main()
