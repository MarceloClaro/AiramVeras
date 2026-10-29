from PIL import Image

im = Image.open("datamining/dados/saap_renders/SAAP__1ANO__LEITURA_p1.png")
w, h = im.size
# Top portion with header and first 5 rows
crop1 = im.crop((0, int(h * 0.20), w, int(h * 0.40)))
crop1.save("datamining/dados/saap_renders/crop_leitura_p1_top5.png")
print("Saved crop_leitura_p1_top5.png")
