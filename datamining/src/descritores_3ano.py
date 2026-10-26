import glob
import pandas as pd

base_dir = "resultados-caed-ciclo-i-2026/csv_originais"

# Leitura
f_leit = glob.glob(f"{base_dir}/3ANO_LEITURA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_leit = pd.read_csv(f_leit, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
print("--- VALORES AMOSTRAIS LEITURA 3º ANO ---")
print(df_leit[['Estudante', 'H 01', 'H 02', 'H 03', 'H 04', 'H 05', 'H 06']].head(3))

# Matemática
f_mat = glob.glob(f"{base_dir}/3ANO_MATEMATICA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_mat = pd.read_csv(f_mat, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
print("\n--- VALORES AMOSTRAIS MATEMÁTICA 3º ANO ---")
print(df_mat[['Estudante', 'H 01', 'H 02', 'H 03', 'H 04', 'H 05', 'H 06']].head(3))

# Calcular % de acerto por habilidade considerando que 'Correto' ou '1' ou 'A' é acerto
for nome_comp, df in [('LEITURA', df_leit), ('MATEMÁTICA', df_mat)]:
    print(f"\n--- TAXA DE ACERTO REAL {nome_comp} ---")
    hab_cols = [c for c in df.columns if c.startswith('H ')]
    for h in hab_cols:
        vc = df[h].value_counts().to_dict()
        # Se for 'Acertou' / 'Errou'
        acertos = sum(cnt for val, cnt in vc.items() if str(val).lower() in ['acertou', 'correto', '1', 'a', 'sim'])
        total = len(df[df[h].notna()])
        taxa = (acertos / total * 100) if total > 0 else 0
        print(f"  {h}: {taxa:.1f}% ({vc})")


# Escrita
f_esc = glob.glob(f"{base_dir}/3ANO_ESCRITA_CICLO_I_2026/*ESTUDANTE*.csv")[0]
df_esc = pd.read_csv(f_esc, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
print("\n--- NOTA MÉDIA ESCRITA 3º ANO ---")
if 'Nota' in df_esc.columns:
    notas = pd.to_numeric(df_esc['Nota'].astype(str).str.replace(',', '.'), errors='coerce')
    print(f"Média: {notas.mean():.2f} / 10 | Mediana: {notas.median():.2f}")
if 'Categoria de escrita' in df_esc.columns:
    print(df_esc['Categoria de escrita'].value_counts())
