"""Conferência final estrutural, hashes e ausência de identificadores no pacote público."""
import csv
import hashlib
import json
from pathlib import Path
import sys
import subprocess

ROOT=Path(__file__).resolve().parents[2]
tables=json.loads((ROOT/'restrito/t03/tabelas.json').read_text(encoding='utf-8'))
identifiers={r['aluno_local_id'] for r in tables['matriculas']}
identifiers.update(r['avaliacao_local_id'] for r in tables['avaliacoes'])
for path in (ROOT.parent/'resultados-caed-ciclo-i-2026/csv_originais').rglob('HABILIDADES_DESEMPENHO_ESTUDANTE*.csv'):
    with path.open(encoding='utf-8-sig',newline='') as f:
        for row in csv.DictReader(f,delimiter=';'):
            if row.get('Estudante','').strip():
                identifiers.add(row['Estudante'].strip())
paths=[p for folder in ('airam','tests','docs','estatistica/t05','evidencias/T05') for p in (ROOT/folder).rglob('*')
       if p.is_file() and p.suffix in {'.py','.json','.log','.md'} and '__pycache__' not in p.parts]
leaks=0
for path in paths:
    content=path.read_text(encoding='utf-8')
    leaks+=any(identifier in content for identifier in identifiers)
if leaks:
    raise SystemExit('Sigilo: pacote publico bloqueado; detalhes individuais suprimidos')
public=json.loads((ROOT/'estatistica/t05/checkpoint.json').read_text(encoding='utf-8'))
schema=json.loads((ROOT/'docs/esquema-t05.json').read_text(encoding='utf-8'))
assert set(public)==set(schema['required'])
assert len(public['agregados'])==335
for row in public['agregados']:
    assert set(row)==set(schema['$defs']['agregado']['required'])
    assert row['nivel'] in ('escola','turma') and 'aluno_local_id' not in row
    for field in ('acertos','oportunidades','cadastros','avaliados','validas','ausentes'):
        assert type(row[field]) is int and row[field]>=0
    for field in ('taxa','taxa_observada'):
        assert row[field] is None or 0<=row[field]<=1
school=next(r for r in public['agregados'] if r['nivel']=='escola' and r['ano_escolar']==5
            and r['componente']=='LEITURA' and r['posicao'] is None)
assert (school['cadastros'],school['avaliados'],school['acertos'],school['oportunidades'])==(54,53,891,1166)
goal=next(r for r in public['metas_A'] if r['nivel']=='escola' and r['ano_escolar']==5 and r['componente']=='LEITURA')
assert (goal['meta_A']['alvo'],goal['meta_A']['conversoes'],goal['meta_A']['acertos_ate_adequacao'])==(43,0,None)
individual=json.loads((ROOT/'restrito/t05/checkpoint.json').read_text(encoding='utf-8'))
assert individual['observado']==tables
assert len(individual['metricas_alunos'])==344 and len(individual['metas_individuais'])==640
assert all(r['meta_B']['status']=='unidade_nao_aplicavel' for r in individual['metas_individuais'] if r['componente'] in ('ESCRITA','FLUENCIA'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
analysis=json.loads((ROOT/'evidencias/T05/analise-real.json').read_text(encoding='utf-8'))
assert sha(ROOT/'restrito/t05/checkpoint.json')==analysis['handoff']['restrito_sha256']
assert sha(ROOT/'estatistica/t05/checkpoint.json')==analysis['handoff']['agregado_sha256']
receipts=0
for receipt_path in (ROOT/'evidencias/T05').glob('*-recibo.json'):
    if receipt_path.name=='T55-recibo.json':
        continue
    recorded=json.loads(receipt_path.read_text(encoding='utf-8'))
    assert sha(receipt_path.parent/recorded['snapshot'])==recorded['snapshot_sha256']
    assert sha(receipt_path.parent/recorded['log'])==recorded['log_sha256']
    receipts+=1
receipt=dict(sigilo_conferido=True,arquivos_publicos_inspecionados=len(paths),ocorrencias_identificadoras=0,
    estrutura_campos_tipos_conferida=True,motor_json_schema_completo_executado=False,
    checkpoint_restrito_igual_observado_T03=True,denominador_5_leitura_conferido=True,
    hashes_handoff_confirmados=True,recibos_logs_snapshots_reconciliados=receipts,
    meta_A_5_leitura_alvo=43,limite='Conferencia local; nao certifica ACL ou anonimato estatistico externo')
(ROOT/'evidencias/T05/verificacao-entrega.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
