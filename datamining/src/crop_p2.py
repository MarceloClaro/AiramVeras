from PIL import Image
import os

img_path = r"datamining\dados\saap_renders\SAAP__1ANO__LEITURA_p2.png"
if os.path.exists(img_path):
    im = Image.open(img_path)
    # The table is in the top portion
    w, h = im.size
    crop_table = im.crop((0, 0, w, int(h * 0.45)))
    crop_path = r"datamining\dados\saap_renders\crop_leitura_p2.png"
    crop_table.save(crop_path)
    print("Crop saved:", crop_path, crop_table.size)

img_path2 = r"datamining\dados\saap_renders\SAAP__1ANO__ESCRITA_p2.png"
if os.path.exists(img_path2):
    im2 = Image.open(img_path2)
    w2, h2 = im2.size
    crop_table2 = im2.crop((0, 0, w2, int(h2 * 0.45)))
    crop_path2 = r"datamining\dados\saap_renders\crop_escrita_p2.png"
    crop_table2.save(crop_path2)
    print("Crop 2 saved:", crop_path2, crop_table2.size)
