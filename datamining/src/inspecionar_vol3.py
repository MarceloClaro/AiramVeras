import pypdf

v3_path = r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_3ano_v1.0.pdf"
r = pypdf.PdfReader(v3_path)
print(f"Total páginas Volume 3 v1.0: {len(r.pages)}")

# Procurar onde começam as pranchetas e atividades
for idx in range(0, min(100, len(r.pages))):
    txt = r.pages[idx].extract_text() or ""
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    header = " | ".join(lines[:2]) if lines else "(vazia)"
    if "PLANCHETA" in txt or "Capítulo" in txt or "CAPÍTULO" in txt or "Atividade" in txt or "Semana" in txt:
        print(f"Página {idx+1}: {header[:100]}")
