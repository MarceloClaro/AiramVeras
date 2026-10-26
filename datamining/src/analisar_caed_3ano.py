import os
import glob
import pandas as pd
import json

base_dir = "resultados-caed-ciclo-i-2026/csv_originais"

print("=== ANÁLISE DOS DADOS CAED DO 3º ANO (24 ALUNOS) ===")

# 1. Leitura
f_leit = glob.glob(f"{base_dir}/3ANO_LEITURA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_leit = pd.read_csv(f_leit, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
print(f"\n1. LEITURA 3º ANO ({len(df_leit)} alunos):")
print(f"Colunas: {list(df_leit.columns)}")
print("Níveis de aprendizagem:")
print(df_leit['Nível de aprendizagem'].value_counts())

# Habilidades de leitura escola / turma
f_leit_hab = glob.glob(f"{base_dir}/3ANO_LEITURA_CICLO_I_2026/*HABILIDADE_DESEMPENHO_TURMA*.csv")
if f_leit_hab:
    df_lh = pd.read_csv(f_leit_hab[0], sep=';', encoding='utf-8-sig', on_bad_lines='skip')
    print("\nHabilidades Leitura Turma:")
    for _, row in df_lh.iterrows():
        cod = row.get('Código da Habilidade', row.iloc[0])
        pct = row.get('% de acerto', row.iloc[-1])
        desc = row.get('Descrição da Habilidade', '')
        print(f"  {cod}: {pct}% - {str(desc)[:60]}")

# 2. Matemática
f_mat = glob.glob(f"{base_dir}/3ANO_MATEMATICA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_mat = pd.read_csv(f_mat, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
print(f"\n2. MATEMÁTICA 3º ANO ({len(df_mat)} alunos):")
print("Níveis de aprendizagem:")
print(df_mat['Nível de aprendizagem'].value_counts())

f_mat_hab = glob.glob(f"{base_dir}/3ANO_MATEMATICA_CICLO_I_2026/*HABILIDADE_DESEMPENHO_TURMA*.csv")
if f_mat_hab:
    df_mh = pd.read_csv(f_mat_hab[0], sep=';', encoding='utf-8-sig', on_bad_lines='skip')
    print("\nHabilidades Matemática Turma:")
    for _, row in df_mh.iterrows():
        cod = row.get('Código da Habilidade', row.iloc[0])
        pct = row.get('% de acerto', row.iloc[-1])
        desc = row.get('Descrição da Habilidade', '')
        print(f"  {cod}: {pct}% - {str(desc)[:60]}")

# 3. Fluência
f_flu = glob.glob(f"{base_dir}/3ANO_FLUENCIA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_flu = pd.read_csv(f_flu, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
print(f"\n3. FLUÊNCIA 3º ANO ({len(df_flu)} alunos):")
print(f"Colunas: {list(df_flu.columns)}")
col_perfil = [c for c in df_flu.columns if 'Perfil' in c or 'perfil' in c or 'Nível' in c or 'leitor' in c.lower()]
if col_perfil:
    print(df_flu[col_perfil[0]].value_counts())

# 4. Escrita
f_esc = glob.glob(f"{base_dir}/3ANO_ESCRITA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_esc = pd.read_csv(f_esc, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
print(f"\n4. ESCRITA 3º ANO ({len(df_esc)} alunos):")
print(f"Colunas: {list(df_esc.columns)}")
col_esc = [c for c in df_esc.columns if 'Nível' in c or 'Total' in c or 'Pontos' in c or 'Escrita' in c]
for c in col_esc:
    print(f"{c}: {df_esc[c].value_counts() if df_esc[c].nunique() < 10 else df_esc[c].describe()}")
