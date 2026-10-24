"""Importa o catálogo de matrizes do portal Ceará, preservando as edições."""
import csv
import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
import pdfplumber
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent
SOURCES = json.loads((ROOT/'fontes.json').read_text(encoding='utf-8'))
CODE = re.compile(r'^\s*(D\d+(?:_[A-Za-z0-9]+)?)\s*(.*)$')
CODE_WORD = re.compile(r'D\d+(?:_[A-Za-z0-9]+)?')
TOPIC = re.compile(r'^(?:[ivx]+\.|eix\s*o\s+\d+:|\d+\.\d+\s*[-–])',re.I)
def clean(s):
    return re.sub(r'\s+', ' ', s).strip().replace('T eorema','Teorema')

records, documents, pages, checks = [], [], [], []
for path in sorted((ROOT/'fontes').rglob('*.pdf')):
    relative = path.relative_to(ROOT).as_posix()
    doc_id = hashlib.sha256(relative.encode()).hexdigest()[:16]
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    archive = 'anteriores' in path.parts
    source = next(s for s in SOURCES if s['arquivo']==('Matrizes_edicoes_anteriores_CE.zip' if archive else path.name))
    year = re.search(r'20\d{2}', relative).group()
    reader = PdfReader(path)
    doc = dict(documento_id=doc_id,arquivo=relative,ano_edicao=int(year),sha256=digest,
               url=source['url'],origem='arquivo ZIP do portal' if archive else 'PDF do portal',
               paginas=len(reader.pages),membro_zip=path.relative_to(ROOT/'fontes/anteriores').as_posix() if archive else '')
    documents.append(doc)
    component='Matemática' if re.search(r'(?:^|[ _])MT(?:[ _.]|$)|\d{4}MT\d',path.name) else 'Língua Portuguesa'
    grade, stage, modality, topic = None, '', 'padrão', ''
    with pdfplumber.open(path) as spatial:
        for pi, page in enumerate(reader.pages,1):
            text=page.extract_text()
            pages.append(dict(documento_id=doc_id,pagina=pi,texto=text))
            first_record=len(records)
            active=None
            def flush():
                if active is None:return
                raw='\n'.join(active.pop('_lines'))
                active['texto_linha_extraido']=raw
                # Matrizes Diagnóstico 2022 publicam correspondências em duas colunas.
                if 'SPAECE Diagnóstico 2022' in relative:
                    secondary=re.search(r'\b(HLP\d+|HMT\d+|D\d+(?:_\w+)?)\b',raw)
                else:secondary=None
                active['descricao']=clean(raw[:secondary.start()] if secondary else raw)
                active['codigo_relacionado_publicado']=secondary.group(1) if secondary else ''
                active['descricao_relacionada_publicada']=clean(raw[secondary.end():]) if secondary else ''
                records.append(active)
            for line in text.splitlines():
                line=line.strip()
                if not line:continue
                if '|' in line and (m:=re.search(r'(\d+)\s*[ºª°]\s*(?:ANO|S[ÉE]RIE)',line,re.I)):
                    flush();active=None
                    grade=int(m.group(1));stage='EM' if re.search('MÉDIO',line,re.I) else 'EF'
                    modality='resposta construída' if 'CONSTRUÍDA' in line.upper() else 'padrão'
                    topic=''
                    continue
                if TOPIC.match(line):
                    flush();active=None;topic=line;continue
                m=CODE.match(line)
                if m:
                    flush()
                    assert grade is not None,(path,pi,'etapa ausente')
                    matrix=f'{doc_id}_{stage}{grade}_{"RC" if modality!="padrão" else "PAD"}'
                    active=dict(matriz_id=matrix,documento_id=doc_id,ano_edicao=int(year),componente=component,
                        etapa=stage,ano_serie=grade,tipo_instrumento=modality,codigo=m.group(1),
                        eixo_topico_extraido=topic,pagina_pdf=pi,fonte_arquivo=relative,
                        fonte_url=source['url'],fonte_sha256=digest,_lines=[m.group(2)])
                elif active:
                    if re.match(r'^(?:DESCRITOR|DESCRIÇÃO|SPAECE|CEARÁ|■|\d+$)',line,re.I):
                        flush();active=None
                    else:active['_lines'].append(line)
            flush()
            words=[w for w in spatial.pages[pi-1].extract_words() if CODE_WORD.fullmatch(w['text'])]
            if words:
                left=min(w['x0'] for w in words)
                codes=[w['text'] for w in words if w['x0']<left+25]
            else:codes=[]
            actual=[r['codigo'] for r in records[first_record:]]
            checks.append(dict(documento_id=doc_id,pagina=pi,codigos_geometria=len(codes),
                               codigos_extraidos=len(actual),ok=Counter(codes)==Counter(actual)))
            assert Counter(codes)==Counter(actual),(relative,pi,codes,actual)
    print(path.name,len(records),flush=True)

assert all(r['descricao'] for r in records)
assert len({(r['matriz_id'],r['codigo']) for r in records})==len(records), 'Chaves duplicadas'
OUT=ROOT/'dados';OUT.mkdir(exist_ok=True)
def write(name,rows):
    (OUT/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter=';');w.writeheader();w.writerows(rows)
write('descritores',records);write('catalogo_documentos',documents)
write('descritores_2026',[r for r in records if r['ano_edicao']==2026])
(OUT/'paginas_extraidas.json').write_text(json.dumps(pages,ensure_ascii=False,indent=2),encoding='utf-8')
db=sqlite3.connect(OUT/'caed.sqlite')
with db:
    for name,rows in [('documentos',documents),('descritores',records),('paginas',pages)]:
        db.execute('DROP TABLE IF EXISTS '+name)
        cols=','.join('"'+k+'" '+('INTEGER' if isinstance(v,int) else 'TEXT') for k,v in rows[0].items())
        db.execute('CREATE TABLE '+name+' ('+cols+')')
        db.executemany('INSERT INTO '+name+' VALUES ('+','.join('?' for _ in rows[0])+')',[tuple(r.values()) for r in rows])
    db.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_matriz_codigo ON descritores(matriz_id,codigo)')
    assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
    assert not db.execute('SELECT DISTINCT d.documento_id FROM descritores d LEFT JOIN documentos f USING(documento_id) WHERE f.documento_id IS NULL').fetchall()
db.close()
summary=dict(documentos=len(documents),paginas=len(pages),matrizes=len(set(r['matriz_id'] for r in records)),
             registros=len(records),por_ano=dict(Counter(r['ano_edicao'] for r in records)),
             verificacao_paginas=checks,integridade_sqlite='ok',chave='matriz_id + codigo')
(ROOT/'validacao.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k!='verificacao_paginas'},ensure_ascii=False,indent=2))
