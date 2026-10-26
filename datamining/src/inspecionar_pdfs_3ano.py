import pypdf
import os

pdf_candidates = [
    r"C:\Users\marce\Downloads\3ANO-U.pdf",
    r"C:\Users\marce\Downloads\saap 3 ano.pdf",
    r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_3ano_v1.2.pdf"
]

for p in pdf_candidates:
    if os.path.exists(p):
        size_mb = os.path.getsize(p) / (1024 * 1024)
        try:
            reader = pypdf.PdfReader(p)
            n_pages = len(reader.pages)
            print(f"\n==========================================")
            print(f"PDF: {p}")
            print(f"Tamanho: {size_mb:.2f} MB | Total Páginas: {n_pages}")
            text_p0 = reader.pages[0].extract_text() or ""
            print(f"Página 1 (primeiros 300 chars):\n{text_p0[:300]}")
            if n_pages > 1:
                text_p1 = reader.pages[1].extract_text() or ""
                print(f"Página 2 (primeiros 200 chars):\n{text_p1[:200]}")
            if n_pages > 25:
                text_p25 = reader.pages[25].extract_text() or ""
                print(f"Página 26 (primeiros 200 chars):\n{text_p25[:200]}")
        except Exception as e:
            print(f"Erro lendo {p}: {e}")
