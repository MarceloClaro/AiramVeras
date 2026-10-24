"""Extrai as sete matrizes baixadas, preservando texto bruto e proveniência."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
sources = json.loads((ROOT / 'fontes.json').read_text(encoding='utf-8'))
records = []
counts = {}
for source in sources:
    path = ROOT / 'fontes' / source['arquivo']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == source['sha256']
    _, component, stage, year = path.stem.split('_')
    matrix = f'SPAECE_{component}_{stage}_{year}'
    text = PdfReader(path).pages[0].extract_text()
    section, subsection, active = '', '', None
    def flush():
        if active:
            raw = '\n'.join(active.pop('_lines'))
            active['descricao_extraida'] = raw
            # Corrige somente espaços de extração; conserva o texto bruto.
            normalized = re.sub(r'\s+', ' ', raw).strip()
            normalized = normalized.replace('situação- problema', 'situação-problema')
            normalized = normalized.replace('T eorema', 'Teorema')
            active['descricao'] = normalized
            records.append(active)
    for line in text.splitlines()[3:]:
        line = line.strip()
        if not line:
            continue
        if re.match(r'(?i)^(?:[ivx]+\.|eix\s*o\s+\d+:)', line):
            flush(); active = None
            section, subsection = line, ''
        elif re.match(r'^\d+\.\d+\s', line):
            flush(); active = None
            subsection = line
        elif (match := re.match(r'^(D\d{2})\s+(.*)', line)):
            flush()
            active = {
                'matriz_id': matrix, 'sistema': 'SPAECE-Alfa' if year == '2' else 'SPAECE',
                'componente': 'Língua Portuguesa' if component == 'LP' else 'Matemática',
                'etapa': 'Ensino Fundamental' if stage == 'EF' else 'Ensino Médio',
                'ano_serie': int(year), 'codigo': match[1],
                'eixo_topico_extraido': section, 'subeixo': subsection,
                'fonte_url': source['url'], 'fonte_arquivo': source['arquivo'],
                'pagina_pdf': 1, 'fonte_sha256': source['sha256'],
                'vigencia_2026': 'não confirmada', '_lines': [match[2]],
            }
        elif active:
            active['_lines'].append(line)
        elif section:
            section += ' ' + line
    flush()
    extracted = [r['codigo'] for r in records if r['matriz_id'] == matrix]
    original = re.findall(r'\bD\d{2}\b', text)
    assert extracted == original, (matrix, extracted, original)
    assert len(set(extracted)) == len(extracted)
    counts[matrix] = len(extracted)

assert all(r['descricao'] and r['eixo_topico_extraido'] for r in records)
assert len({(r['matriz_id'], r['codigo']) for r in records}) == len(records)
out = ROOT / 'dados'; out.mkdir(exist_ok=True)
(out / 'descritores.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
with (out / 'descritores.csv').open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=list(records[0]), delimiter=';')
    writer.writeheader(); writer.writerows(records)
db = sqlite3.connect(out / 'spaece.sqlite')
with db:
    # Esta tabela é exclusivamente o derivado gerado por este extrator.
    db.execute('DROP TABLE IF EXISTS descritores')
    columns = ','.join('"'+k+'" '+('INTEGER' if k in ('ano_serie','pagina_pdf') else 'TEXT') for k in records[0])
    db.execute('CREATE TABLE descritores ('+columns+', PRIMARY KEY(matriz_id,codigo))')
    keys = ','.join('"'+k+'"' for k in records[0])
    db.executemany('INSERT INTO descritores ('+keys+') VALUES ('+','.join('?' for _ in records[0])+')', [tuple(r.values()) for r in records])
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    assert db.execute('SELECT count(*) FROM descritores').fetchone()[0] == len(records)
db.close()
report = {'total_descritores_por_matriz': len(records), 'contagens': counts,
          'validacao': 'SHA256 das fontes, códigos completos e únicos por matriz, campos obrigatórios e integridade SQLite aprovados',
          'limite': 'Não confirma vigência específica em 2026; não estabelece equivalências com BNCC ou CAEd.',
          'normalizacao': 'Espaços e quebras de linha; situação- problema -> situação-problema; T eorema -> Teorema. Texto bruto preservado.'}
(ROOT / 'validacao.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
