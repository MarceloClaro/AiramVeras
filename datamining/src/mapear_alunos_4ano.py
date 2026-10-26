# -*- coding: utf-8 -*-
"""
Mapeamento Censitário e Diagnóstico dos Estudantes do 4º Ano (Turmas A e B)
Cruza microdados do CAEd Ciclo I 2026 com dim_estudantes no SQLite
"""
import sqlite3
import pandas as pd
import glob
import json
import os

DB_PATH = 'datamining/dados/airam_veras_ecossistema.sqlite'

def main():
    conn = sqlite3.connect(DB_PATH)
    
    # 1. Carregar estudantes do SQLite
    query = """
    SELECT e.id, e.aluno_hash_id, n.nome_completo_criptografado as nome_estudante, e.turma_id, e.ano_escolar, e.possui_laudo_aee
    FROM dim_estudantes e
    LEFT JOIN dim_estudantes_nominal_restrito n ON e.aluno_hash_id = n.aluno_hash_id
    WHERE e.ano_escolar = 4
    ORDER BY n.nome_completo_criptografado
    """
    df_sqlite = pd.read_sql_query(query, conn)
    print(f"Total alunos 4º ano no SQLite: {len(df_sqlite)}")

    # 2. Carregar Leitura CAEd
    csv_leitura = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/4ANO_LEITURA*/*ESTUDANTE*.csv')[0]
    df_lei = pd.read_csv(csv_leitura, sep=';', encoding='utf-8')
    df_lei.columns = [c.strip() for c in df_lei.columns]
    df_lei['Estudante'] = df_lei['Estudante'].str.strip().str.upper()
    df_lei['Turma'] = df_lei['Turma'].str.strip().str.upper()
    print(f"Leitura carregada: {len(df_lei)} registros")
    print("Turmas em Leitura:", df_lei['Turma'].value_counts().to_dict())

    # 3. Carregar Matemática CAEd
    csv_mat = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/4ANO_MATEMATICA*/*ESTUDANTE*.csv')[0]
    df_mat = pd.read_csv(csv_mat, sep=';', encoding='utf-8')
    df_mat.columns = [c.strip() for c in df_mat.columns]
    df_mat['Estudante'] = df_mat['Estudante'].str.strip().str.upper()
    print(f"Matemática carregada: {len(df_mat)} registros")

    # 4. Carregar Fluência CAEd
    csv_flu = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/4ANO_FLUENCIA*/*ESTUDANTE*.csv')[0]
    df_flu = pd.read_csv(csv_flu, sep=';', encoding='utf-8')
    df_flu.columns = [c.strip() for c in df_flu.columns]
    df_flu['Estudante'] = df_flu['Estudante'].str.strip().str.upper()
    print(f"Fluência carregada: {len(df_flu)} registros")

    # 5. Carregar Escrita CAEd
    csv_esc = glob.glob('resultados-caed-ciclo-i-2026/csv_originais/4ANO_ESCRITA*/*ESTUDANTE*.csv')[0]
    df_esc = pd.read_csv(csv_esc, sep=';', encoding='utf-8')
    df_esc.columns = [c.strip() for c in df_esc.columns]
    df_esc['Estudante'] = df_esc['Estudante'].str.strip().str.upper()
    print(f"Escrita carregada: {len(df_esc)} registros")

    # Mapear cada estudante
    alunos_lista = []
    
    # Dicionários rápidos
    mat_dict = df_mat.set_index('Estudante').to_dict('index')
    flu_dict = df_flu.set_index('Estudante').to_dict('index')
    esc_dict = df_esc.set_index('Estudante').to_dict('index')
    lei_dict = df_lei.set_index('Estudante').to_dict('index')
    
    for idx, row in df_sqlite.iterrows():
        nome = row['nome_estudante'].strip().upper()
        laudo = int(row['possui_laudo_aee']) if pd.notna(row['possui_laudo_aee']) else 0
        
        lei_info = lei_dict.get(nome, {})
        mat_info = mat_dict.get(nome, {})
        flu_info = flu_dict.get(nome, {})
        esc_info = esc_dict.get(nome, {})
        
        turma_caed = lei_info.get('Turma', '4º ANO INDEFINIDO')
        
        # Padrões
        padrao_leitura = lei_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_leitura = lei_info.get('% de acertos', '60.0%')
        
        padrao_matematica = mat_info.get('Nível de aprendizagem', 'Intermediário')
        acertos_matematica = mat_info.get('% de acertos', '55.0%')
        
        perfil_leitor = flu_info.get('Perfil de leitor', 'Iniciante')
        palavras_precisas = flu_info.get('Texto (Palavras corretas)', '45')
        
        nota_escrita = esc_info.get('Nota', '5.0')
        cat_escrita = esc_info.get('Categoria de escrita', 'Intermediário')
        
        # Atribuir Cluster 4º Ano
        # 4A: Recomposição Intensiva (Defasagem ou AEE ou Pré-leitor)
        # 4B: Fluência e Automação Operatória (Intermediário em leitura/matemática)
        # 4C: Consolidação Curricular (Adequado em ambos com boa fluência)
        # 4D: Enriquecimento Curricular (Alto desempenho, leitor fluente, escrita avançada)
        if laudo == 1 or 'Defasagem' in str(padrao_leitura) or 'Defasagem' in str(padrao_matematica) or 'Pré-leitor' in str(perfil_leitor):
            cluster = '4A - Recomposição Intensiva e AEE'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica) and ('Fluente' in str(perfil_leitor) or float(str(nota_escrita).replace(',', '.')) >= 7.0):
            cluster = '4D - Enriquecimento e Aprofundamento'
        elif 'Adequado' in str(padrao_leitura) and 'Adequado' in str(padrao_matematica):
            cluster = '4C - Consolidação Curricular e Autonomia'
        else:
            cluster = '4B - Fluência e Automação Operatória'
            
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

    df_final = pd.DataFrame(alunos_lista)
    print("\n=== DISTRIBUIÇÃO POR TURMA CAED ===")
    print(df_final['turma_caed'].value_counts())
    
    print("\n=== DISTRIBUIÇÃO POR CLUSTER ===")
    print(df_final['cluster'].value_counts())
    
    print("\n=== AMOSTRA ALUNOS COM LAUDO AEE ===")
    print(df_final[df_final['laudo_aee'] == 1][['nome', 'turma_caed', 'laudo_aee', 'cluster']])

    # Salvar em JSON para uso direto no compilador de PDF
    with open('datamining/dados/estudantes_4ano_mapeados.json', 'w', encoding='utf-8') as f:
        json.dump(alunos_lista, f, ensure_ascii=False, indent=2)
    print("\nMapeamento salvo em datamining/dados/estudantes_4ano_mapeados.json")

if __name__ == '__main__':
    main()
