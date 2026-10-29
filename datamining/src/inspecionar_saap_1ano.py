import os
import pypdf

for fname in ["SAAP- 1ANO- ESCRITA.pdf", "SAAP- 1ANO- LEITURA.pdf"]:
    fpath = os.path.join(".", fname)
    print(f"\n==================== {fname} ====================")
    if not os.path.exists(fpath):
        print("Arquivo nao encontrado!")
        continue
    reader = pypdf.PdfReader(fpath)
    print(f"Total de paginas: {len(reader.pages)}")
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        print(f"--- Pagina {i+1} (tamanho {len(text)} chars) ---")
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:25]:
            print(f"  {line}")
        if len(lines) > 25:
            print(f"  ... [mais {len(lines)-25} linhas]")
