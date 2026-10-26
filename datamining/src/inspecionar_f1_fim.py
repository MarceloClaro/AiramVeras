import pypdf

f1_path = "Dossie_Integrado_1e2_Airam_Veras_2026_Fonico_Kumon_CAPA_PADRAO.pdf"
reader_f1 = pypdf.PdfReader(f1_path)

print("Inspecionando páginas 1600 a 1805 do F1...")
for p_idx in range(1600, len(reader_f1.pages), 10):
    txt = reader_f1.pages[p_idx].extract_text() or ""
    lines = [l.strip() for l in txt.split('\n') if l.strip()]
    header = " | ".join(lines[:3]) if lines else "(vazia)"
    print(f"Página {p_idx+1}: {header[:120]}")
