"""Inspeção somente leitura de células vetoriais públicas, não é parser de produto."""
import json
from pathlib import Path
import pdfplumber

root = Path(__file__).resolve().parents[2]
with pdfplumber.open(root.parent / 'MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf') as pdf:
    for number in [4, 7, 9, 11, 20, 26, 28]:
        page = pdf.pages[number - 1]
        rects = [dict(x0=r['x0'], x1=r['x1'], top=r['top'], bottom=r['bottom'])
                 for r in page.rects if r['top'] > 170 and r['x0'] < 200]
        print(json.dumps(dict(pagina=number, rects=rects[:14], lines=len(page.lines),
              text=page.extract_text()[-900:],
              edges=[dict(x0=e['x0'], x1=e['x1'], top=e['top'], bottom=e['bottom'], orientation=e['orientation'])
                     for e in page.edges if e['orientation'] == 'h' and 125 < e['top'] < 180][:15]), ensure_ascii=False))
data = json.loads((root.parent / 'bncc-dados/dados/bncc-2018/ensino-fundamental.json').read_text(encoding='utf-8'))
print(json.dumps(next(h for h in data['habilidades'] if h['codigo'] == 'EF01LP02'), ensure_ascii=False))
