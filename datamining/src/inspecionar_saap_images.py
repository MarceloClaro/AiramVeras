import os
import pypdf
import pdfplumber

for fname in ["SAAP- 1ANO- ESCRITA.pdf", "SAAP- 1ANO- LEITURA.pdf"]:
    print(f"\n==================== {fname} ====================")
    reader = pypdf.PdfReader(fname)
    for idx, page in enumerate(reader.pages):
        print(f"Page {idx+1}:")
        print(f"  Images count: {len(page.images)}")
        for img_idx, img in enumerate(page.images):
            print(f"    Image {img_idx}: name={img.name}, size={len(img.data)} bytes")
    
    with pdfplumber.open(fname) as pdf:
        for idx, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            print(f"  Pdfplumber Page {idx+1}: tables={len(tables)}, chars={len(page.chars)}")
            if len(page.chars) > 0:
                print("  Chars sample:", "".join([c['text'] for c in page.chars[:50]]))
