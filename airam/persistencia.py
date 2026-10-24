"""SQLite e CSV individuais exclusivamente no armazenamento local restrito."""
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import tempfile
from contextlib import closing

from airam.cache import sha
from airam.identidade import _validar_sem_nominais


def persistir(tabelas,destino,projeto,fontes):
    root=Path(projeto).resolve(); target=Path(destino).resolve()
    if not target.is_relative_to(root/'restrito'):
        raise ValueError('Dados individuais exigem destino restrito local')
    _validar_sem_nominais(tabelas)
    if not fontes or not isinstance(tabelas,dict) or not tabelas:
        raise ValueError('Persistencia sem proveniencia ou tabelas')
    for table,rows in tabelas.items():
        if not re.fullmatch('[a-z][a-z0-9_]*',table) or table=='proveniencia' or not isinstance(rows,list) or not all(isinstance(r,dict) for r in rows):
            raise ValueError('Tabela invalida')
    raw=json.dumps({'tabelas':tabelas,'fontes':fontes},ensure_ascii=False,sort_keys=True,allow_nan=False).encode()
    digest=hashlib.sha256(raw).hexdigest()
    final=target/digest
    if final.exists():
        receipt=json.loads((final/'manifesto.json').read_text(encoding='utf-8'))
        expected_files={'analise.sqlite3',*(table+'.csv' for table in tabelas)}
        if (receipt.get('schema')!=1 or receipt.get('conteudo_sha256')!=digest
            or set(receipt.get('hashes',{}))!=expected_files):
            raise ValueError('Manifesto de persistencia incompleto ou divergente')
        if any(sha(final/p)!=h for p,h in receipt['hashes'].items()):
            raise ValueError('Persistencia anterior adulterada')
    else:
        target.mkdir(parents=True,exist_ok=True)
        staging=Path(tempfile.mkdtemp(prefix='.persistencia-',dir=target))
        try:
            with closing(sqlite3.connect(staging/'analise.sqlite3')) as db, db:
                db.execute('PRAGMA user_version=1')
                db.execute('CREATE TABLE proveniencia (schema_versao INTEGER NOT NULL, fontes_json TEXT NOT NULL, conteudo_sha256 TEXT NOT NULL)')
                db.execute('INSERT INTO proveniencia VALUES (1,?,?)',(json.dumps(fontes,sort_keys=True),digest))
                for table, rows in tabelas.items():
                    fields=sorted({k for row in rows for k in row})
                    db.execute(f'CREATE TABLE "{table}" (ordem INTEGER PRIMARY KEY, fonte_id TEXT, ano_escolar INTEGER, componente TEXT, avaliacao_local_id TEXT, registro_json TEXT NOT NULL)')
                    db.executemany(f'INSERT INTO "{table}" VALUES (?,?,?,?,?,?)',[(i,row.get('fonte_id'),row.get('ano_escolar'),row.get('componente'),row.get('avaliacao_local_id'),json.dumps(row,ensure_ascii=False,sort_keys=True,allow_nan=False)) for i,row in enumerate(rows)])
                    with (staging/(table+'.csv')).open('w',encoding='utf-8-sig',newline='') as stream:
                        writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader()
                        for row in rows:
                            writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in row.items()})
            hashes={p.name:sha(p) for p in staging.iterdir()}
            (staging/'manifesto.json').write_text(json.dumps({'schema':1,'conteudo_sha256':digest,'hashes':hashes},sort_keys=True),encoding='utf-8')
            staging.rename(final)
        finally:
            if staging.exists(): shutil.rmtree(staging)
    return {'sqlite':str(final/'analise.sqlite3'),'csv':{t:str(final/(t+'.csv')) for t in tabelas},
        'manifesto':str(final/'manifesto.json'),'conteudo_sha256':digest,
        'privacidade':'pseudonimos pessoais; local ignorado; ACL/criptografia nao certificadas'}
