import pypdf

v3_path = r"C:\Users\marce\Downloads\Alfabetizar_Bem\Volume_3_3ano_v1.0.pdf"
r = pypdf.PdfReader(v3_path)

print(f"Volume 3 total páginas: {len(r.pages)}")
p25 = r.pages[24] # 0-indexed: página 25
print("Página 25 mediaBox:", p25.mediabox)
txt25 = p25.extract_text() or ""
print("Página 25 texto (primeiros 150 chars):", repr(txt25[:150]))

p41 = r.pages[40] # 0-indexed: página 41 (Plancheta 0.1)
print("Página 41 mediaBox:", p41.mediabox)
txt41 = p41.extract_text() or ""
print("Página 41 texto (primeiros 150 chars):", repr(txt41[:150]))
