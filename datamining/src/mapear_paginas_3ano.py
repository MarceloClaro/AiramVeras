import pypdf
import os

vol3_path = r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_3ano_v1.0.pdf"
reader_v3 = pypdf.PdfReader(vol3_path)
print(f"Total páginas Volume 3 v1.0: {len(reader_v3.pages)}")
for i in [0, 1, 2, 10, 20, 25, 26, 27, 50, 100, 200, 300, 500, 600]:
    if i < len(reader_v3.pages):
        txt = reader_v3.pages[i].extract_text() or ""
        first_line = txt.split('\n')[0] if txt else "(vazia)"
        print(f"Página {i+1}: {first_line[:80]}")

f1_path = "Dossie_Integrado_1e2_Airam_Veras_2026_Fonico_Kumon_CAPA_PADRAO.pdf"
reader_f1 = pypdf.PdfReader(f1_path)
print(f"\nTotal páginas F1: {len(reader_f1.pages)}")
for i in [0, 677, 1404, 1500, 1501, 1612, 1613, 1700, 1800, 1804]:
    if i < len(reader_f1.pages):
        txt = reader_f1.pages[i].extract_text() or ""
        first_line = txt.split('\n')[0] if txt else "(vazia)"
        print(f"F1 Página {i+1}: {first_line[:80]}")
