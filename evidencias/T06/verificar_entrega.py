"""Auditoria de estrutura declarada, sigilo e recibos; não é motor JSON Schema geral."""
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT=Path(__file__).resolve().parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def need(value):
    if not value:raise ValueError('Conferencia T06 falhou; conteudo individual suprimido')


def validate(value,schema,root):
    """Só os keywords usados nos dois schemas versionados, com recusas explícitas."""
    known={'$schema','$id','title','$defs','$ref','type','properties','additionalProperties','required',
           'items','minItems','maxItems','minimum','maximum','enum','const','pattern'}
    need(not set(schema)-known)
    if '$ref' in schema:
        target=root
        for part in schema['$ref'].split('/')[1:]:target=target[part]
        return validate(value,target,root)
    if 'const' in schema:need(value==schema['const'])
    if 'enum' in schema:need(value in schema['enum'])
    if 'type' in schema:
        types=schema['type'] if isinstance(schema['type'],list) else [schema['type']]
        actual='null' if value is None else 'boolean' if type(value) is bool else 'integer' if type(value) is int else 'number' if type(value) is float else 'string' if isinstance(value,str) else 'array' if isinstance(value,list) else 'object' if isinstance(value,dict) else 'invalid'
        need(actual in types or actual=='integer' and 'number' in types)
    if type(value) in (int,float):
        need(math.isfinite(value))
        if 'minimum' in schema:need(value>=schema['minimum'])
        if 'maximum' in schema:need(value<=schema['maximum'])
    if isinstance(value,str) and 'pattern' in schema:need(re.fullmatch(schema['pattern'],value) is not None)
    if isinstance(value,dict):
        need(not set(schema.get('required',[]))-set(value))
        properties=schema.get('properties',{})
        extra=set(value)-set(properties)
        additional=schema.get('additionalProperties',True)
        if additional is False:need(not extra)
        for k,v in value.items():
            if k in properties:validate(v,properties[k],root)
            elif isinstance(additional,dict):validate(v,additional,root)
    if isinstance(value,list):
        if 'minItems' in schema:need(len(value)>=schema['minItems'])
        if 'maxItems' in schema:need(len(value)<=schema['maxItems'])
        for v in value:
            if 'items' in schema:validate(v,schema['items'],root)


label=sys.argv[1]
public=ROOT/'estatistica/t06'/label
private=ROOT/'restrito/t06'/label
data=json.loads((public/'checkpoint.json').read_text(encoding='utf-8'))
pairs=json.loads((private/'plano-pares.json').read_text(encoding='utf-8'))
for content,path in ((data,'docs/esquema-t06.json'),(pairs,'docs/esquema-restrito-t06.json')):
    schema=json.loads((ROOT/path).read_text(encoding='utf-8'));validate(content,schema,schema)
need(data['config_sha256']==sha(ROOT/'config/correlacoes.json'))
need(data['plano_sha256']==sha(public/'plano.json'))
need(data['instrumentos_sha256']==sha(public/'instrumentos.json'))
for path,digest in data['fontes'].items():need(sha(ROOT/path)==digest)
summary=json.loads((ROOT/'evidencias/T06'/('analise-'+label+'.json')).read_text(encoding='utf-8'))
need(summary['checkpoint_sha256']==sha(public/'checkpoint.json'))
need(summary['restrito_sha256']==sha(private/'plano-pares.json'))
need(summary['csv_sha256']==sha(public/'associacoes.csv'))
rows=data['associacoes'];need(len(rows)==428)
need(Counter(r['metodo'] for r in rows)=={'pearson':214,'spearman':214})
for r in rows:
    need(r['n']<=min(r['n_x'],r['n_y'])<=r['cadastros'])
    need(sum(g['n'] for g in r['estratos'])==r['n'])
    need(r['excluidos']==r['cadastros']-r['n'])
    need(r['m_bh']==r['m_planejado'] and r['m_elegivel']<=r['m_bh'])
    if r['p'] is None:need(r['q'] is None and r['q_by'] is None and r['q_bh_global'] is None and r['motivo_inferencia'] is not None)
    if r['coeficiente'] is None:need(r['motivo_coeficiente'] is not None)
    s=r['sensibilidade'];need(s['validas']+s['degeneradas']==s['replicacoes'])
    if s['faixa'] is not None:need(s['validas']/s['replicacoes']>=.9)
need(sum(f['planejadas'] for f in data['familias'])==len(rows))
tables=json.loads((ROOT/'restrito/t03/tabelas.json').read_text(encoding='utf-8'))
identifiers={r['aluno_local_id'] for r in tables['matriculas']}|{r['avaliacao_local_id'] for r in tables['avaliacoes']}
for path in (ROOT.parent/'resultados-caed-ciclo-i-2026/csv_originais').rglob('*.csv'):
    with path.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f,delimiter=';'):
            name=row.get('Estudante','').strip()
            if name:identifiers.add(name)
paths=[p for folder in ('airam','tests','docs','config','estatistica/t06','evidencias/T06') for p in (ROOT/folder).rglob('*')
    if p.is_file() and p.suffix in {'.py','.json','.log','.md','.csv'} and '__pycache__' not in p.parts]
for path in paths:
    content=path.read_text(encoding='utf-8-sig');need(not any(i in content for i in identifiers))
receipts=0
for path in (ROOT/'evidencias/T06').glob('*-recibo.json'):
    r=json.loads(path.read_text(encoding='utf-8'))
    need(sha(path.parent/r['snapshot'])==r['snapshot_sha256'])
    need(sha(path.parent/r['log'])==r['log_sha256']);receipts+=1
result=dict(status='CONFERIDO',arquivos_sem_identificadores=len(paths),ocorrencias_identificadoras=0,
    schemas_keywords_utilizados_conferidos=True,motor_json_schema_geral=False,
    associacoes=len(rows),familias=len(data['familias']),recibos_conferidos=receipts,
    checkpoint_sha256=sha(public/'checkpoint.json'),limite='Conferencia local; nao certifica ACL nem anonimato externo')
dest=ROOT/'evidencias/T06'/('verificacao-'+label+'.json')
need(not dest.exists())
dest.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
