import pdfplumber

for fname in ["SAAP- 1ANO- ESCRITA.pdf", "SAAP- 1ANO- LEITURA.pdf"]:
    print(f"\n==================== {fname} ====================")
    with pdfplumber.open(fname) as pdf:
        for idx, page in enumerate(pdf.pages):
            print(f"Page {idx+1}:")
            tables = page.extract_tables()
            for t_idx, t in enumerate(tables):
                print(f"  Table {t_idx+1} rows={len(t)}:")
                for r in t[:5]:
                    print("   ", r)
            print("  Object keys:", page.objects.keys())
            for k in page.objects:
                print(f"    {k}: {len(page.objects[k])}")
