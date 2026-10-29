import pdfplumber
from PIL import Image

with pdfplumber.open("SAAP- 1ANO- LEITURA.pdf") as pdf:
    p2 = pdf.pages[1]
    tab = p2.find_tables()[0]
    im = p2.to_image(resolution=150).original
    for r_idx, r in enumerate(tab.rows):
        c0 = r.cells[0]
        if c0:
            # Crop name area
            # p2 is in 72 dpi points, im is in 150 dpi
            scale = 150 / 72
            x0, top, x1, bottom = [int(v * scale) for v in c0]
            crop = im.crop((x0, top, x1, bottom))
            crop.save(f"datamining/dados/saap_renders/row_name_r{r_idx}.png")
            print(f"Saved row {r_idx} name crop, bbox: {c0}")
