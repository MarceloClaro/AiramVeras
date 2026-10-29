import pdfplumber
import os

out_dir = os.path.join(".", "datamining", "dados", "saap_renders")
os.makedirs(out_dir, exist_ok=True)

for fname in ["SAAP- 1ANO- ESCRITA.pdf", "SAAP- 1ANO- LEITURA.pdf"]:
    base = fname.replace(".pdf", "").replace(" ", "_").replace("-", "_")
    with pdfplumber.open(fname) as pdf:
        for idx, page in enumerate(pdf.pages):
            img_path = os.path.join(out_dir, f"{base}_p{idx+1}.png")
            img = page.to_image(resolution=300)
            img.save(img_path)
            print(f"Saved: {img_path}")
