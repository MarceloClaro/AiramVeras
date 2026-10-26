import glob
import pandas as pd
import json

base_dir = "resultados-caed-ciclo-i-2026/csv_originais"
f_leit = glob.glob(f"{base_dir}/3ANO_LEITURA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_leit = pd.read_csv(f_leit, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
f_mat = glob.glob(f"{base_dir}/3ANO_MATEMATICA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_mat = pd.read_csv(f_mat, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
f_flu = glob.glob(f"{base_dir}/3ANO_FLUENCIA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_flu = pd.read_csv(f_flu, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
f_esc = glob.glob(f"{base_dir}/3ANO_ESCRITA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_esc = pd.read_csv(f_esc, sep=';', encoding='utf-8-sig', on_bad_lines='skip')

std_names = sorted(df_leit['Estudante'].unique().tolist())
print(f"Total alunos no 3º Ano: {len(std_names)}")

# Cruzamento e definição de clusters
# 3A: Recomposição Intensiva (Defasagem em Matemática ou Intermediário em LP + Pré-leitor)
# 3B: Automação e Fluência Leitora (Iniciantes na leitura / Intermediário em Matemática)
# 3C: Consolidação Curricular e Resolução de Problemas (Adequado em ambos / Fluente)
# 3D: Enriquecimento Curricular / Altas Habilidades (Adequado alto em ambos / Fluente pleno / Escrita alta)

clusters = {}
for name in std_names:
    r_l = df_leit[df_leit['Estudante'] == name].iloc[0]
    r_m = df_mat[df_mat['Estudante'] == name].iloc[0]
    r_f = df_flu[df_flu['Estudante'] == name].iloc[0] if len(df_flu[df_flu['Estudante'] == name]) > 0 else {}
    r_e = df_esc[df_esc['Estudante'] == name].iloc[0] if len(df_esc[df_esc['Estudante'] == name]) > 0 else {}

    nl = r_l.get('Nível de aprendizagem', '')
    nm = r_m.get('Nível de aprendizagem', '')
    pf = r_f.get('Perfil de leitor', '') if isinstance(r_f, pd.Series) else ''
    cat_e = r_e.get('Categoria de escrita', '') if isinstance(r_e, pd.Series) else ''

    if nm == 'Defasagem' or (nl == 'Intermediário' and 'Pré' in str(pf)):
        cl = "3A"
    elif 'Iniciante' in str(pf) or nm == 'Intermediário' or nl == 'Intermediário':
        cl = "3B"
    elif nl == 'Adequado' and nm == 'Adequado' and ('Fluente' in str(pf) or cat_e == 'Alto'):
        # checar se é candidato a 3D
        if 'Fluente' in str(pf) and cat_e == 'Alto':
            cl = "3D"
        else:
            cl = "3C"
    else:
        cl = "3C"
    clusters[name] = cl

print("\n--- DISTRIBUIÇÃO DOS CLUSTERS DO 3º ANO ---")
counts = pd.Series(clusters).value_counts().sort_index()
print(counts)

print("\n--- LISTAGEM NOMINAL COMPLETA DOS 24 ALUNOS ---")
for i, name in enumerate(std_names):
    r_l = df_leit[df_leit['Estudante'] == name].iloc[0]
    r_m = df_mat[df_mat['Estudante'] == name].iloc[0]
    nl = r_l.get('Nível de aprendizagem', '')
    nm = r_m.get('Nível de aprendizagem', '')
    print(f"{i+1:02d}. {name} | LP: {nl} | MAT: {nm} | Cluster: {clusters[name]}")
