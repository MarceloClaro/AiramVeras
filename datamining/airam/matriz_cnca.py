"""Ocorrências oficiais de leitura/matemática, extraídas pelas células vetoriais."""
import hashlib
from pathlib import Path
import re

import pdfplumber

PDF_SHA256 = '2728d640c98510ff323cb542282ffc51db8288c021560aa55cac7b908c5f5f0e'
CAED = re.compile(r'[1-5]EF\d{2}_[PM]')
BNCC = re.compile(r'EF\d{2}(?:LP|MA)\d{2}')
# Perfil documental explícito: continuações pertencem a estes blocos, não ao prefixo CAEd.
BLOCOS = [('LEITURA', 1, [4]), ('LEITURA', 2, [5]), ('LEITURA', 3, [6, 7]),
          ('LEITURA', 4, [8, 9]), ('LEITURA', 5, [10, 11]),
          ('MATEMATICA', 1, [20]), ('MATEMATICA', 2, [21, 22]),
          ('MATEMATICA', 3, [23, 24]), ('MATEMATICA', 4, [25, 26]),
          ('MATEMATICA', 5, [27, 28])]


def _colunas(page, componente):
    """Limites vêm dos retângulos de cabeçalho, inclusive as três células de ciclo."""
    values = sorted(v for r in page.rects if 120 < r['top'] < 160 and r['bottom'] < 180
                    and r['x0'] > 60 and r['width'] > 20 for v in (r['x0'], r['x1']))
    limites = []
    for value in values:
        if not limites or abs(value - limites[-1]) > .1:
            limites.append(value)
    labels = (['ut'] if componente == 'MATEMATICA' else []) + ['codigo', 'descritor', 'bncc', 'I', 'II', 'III']
    if len(limites) != len(labels) + 1:
        raise ValueError('Geometria de cabecalho nao reconhecida')
    return dict(zip(labels, zip(limites, limites[1:])))


def _texto(page, bbox):
    return page.crop(tuple(bbox)).extract_text(x_tolerance=2, y_tolerance=2) or ''


def extrair_ocorrencias(pdf: Path) -> list[dict]:
    """Lê somente o PDF/versionamento auditado; nunca infere vínculos pelo prefixo."""
    pdf = Path(pdf)
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if sha != PDF_SHA256:
        raise ValueError('PDF diverge da versao/geometria auditada')
    result = []
    with pdfplumber.open(pdf) as document:
        for componente, ano, paginas in BLOCOS:
            block = []
            notes = []
            for number in paginas:
                page = document.pages[number - 1]
                columns = _colunas(page, componente)
                words = page.extract_words(x_tolerance=2, y_tolerance=2)
                left, right = columns['codigo']
                codigos = [w for w in words if CAED.fullmatch(w['text'])
                           and left <= w['x0'] and w['x1'] <= right]
                edges = [e for e in page.edges if e['orientation'] == 'h'
                         and abs(e['x0'] - left) < .1 and abs(e['x1'] - right) < .1]
                page_rows = []
                for word in codigos:
                    top = max(e['top'] for e in edges if e['top'] <= word['top'])
                    bottom = min(e['top'] for e in edges if e['top'] >= word['bottom'])
                    cells = {name: [x0, top, x1, bottom] for name, (x0, x1) in columns.items()}
                    raw = _texto(page, cells['descritor'])
                    raw_bncc = _texto(page, cells['bncc'])
                    marks = []
                    for ciclo in ['I', 'II', 'III']:
                        x0, y0, x1, y1 = cells[ciclo]
                        marks.extend(dict(ciclo=ciclo, bbox=[w['x0'], w['top'], w['x1'], w['bottom']])
                                     for w in words if w['text'].upper() == 'X'
                                     and x0 <= w['x0'] and w['x1'] <= x1
                                     and y0 <= w['top'] and w['bottom'] <= y1)
                    codes = list(dict.fromkeys(BNCC.findall(raw_bncc)))
                    if not raw.strip() or not codes or not marks:
                        raise ValueError(f'Celula incompleta na pagina publica {number}')
                    row = dict(ocorrencia_id=f'{sha}:p{number}:y{top:.4f}:{word["text"]}',
                        fonte_matriz=pdf.name, sha256_pdf=sha, pagina_matriz=number,
                        ano_tabela=ano, componente=componente, codigo_caed=word['text'],
                        texto_caed=' '.join(raw.split()), texto_caed_celula=raw,
                        bncc_celula=raw_bncc, codigos_bncc=codes,
                        ciclos=[c for c in ['I', 'II', 'III'] if any(m['ciclo'] == c for m in marks)],
                        marcas_ciclo=marks, celulas=cells,
                        unidade_tematica=_texto(page, cells['ut']).strip() if 'ut' in cells else None,
                        nota_integracao=None)
                    page_rows.append(row)
                if page_rows:
                    tail = _texto(page, [60, max(r['celulas']['codigo'][3] for r in page_rows),
                                         page.width - 35, page.height - 35])
                    if 'blocos de integração' in tail:
                        notes.append(dict(pagina_matriz=number, texto=' '.join(tail.split())))
                block.extend(page_rows)
            for row in block:
                row['nota_integracao'] = notes or None
            result.extend(block)
    return result
