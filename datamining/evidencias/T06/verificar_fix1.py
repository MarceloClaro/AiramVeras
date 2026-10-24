"""Compatibilidade real da correção de composição, sem repetir inferência."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.correlacoes import preparar_analises

BASE='5fb71c7fc641b7073cb9646bcf6667c67c6a8138'
PINNED={
    'restrito/t05/checkpoint.json':'6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b',
    'restrito/t06/entrega/plano-pares.json':'dc4f3d0721db427c7001cabbd5199f98a653881be021d274fde2bfead4c58af6',
    'estatistica/t06/entrega/checkpoint.json':'2a0472e9b391e0a1c66af53c6d4572f00109a81b49ff547fd5cf8bf8c3e42570',
    'estatistica/t06/entrega/plano.json':'48cbc2886971720c62d734edf6b6292432174054e38e409039e0197a0e6e4cbb',
    'estatistica/t06/entrega/associacoes.csv':'8df29410e5323f693703e06ccf705843bccb86607c137bd97f8b791b937a9cc9'}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(ok):
    if not ok:raise ValueError('Compatibilidade FIX1 divergiu; dados individuais suprimidos')


for name,digest in PINNED.items():need(sha(ROOT/name)==digest)
old_snapshot=json.loads((ROOT/'evidencias/T06/08-analise-entrega-antes.json').read_text(encoding='utf-8'))
need(sha(ROOT/'config/correlacoes.json')==old_snapshot['hashes_codigo']['config/correlacoes.json'])
baseline=subprocess.check_output(['git','show',BASE+':airam/correlacoes.py'],cwd=ROOT).decode('utf-8')
current=(ROOT/'airam/correlacoes.py').read_text(encoding='utf-8')
old={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(baseline).body if isinstance(n,ast.FunctionDef)}
new={n.name:ast.dump(n,include_attributes=False) for n in ast.parse(current).body if isinstance(n,ast.FunctionDef)}
need(set(old)==set(new))
changed=sorted(k for k in old if old[k]!=new[k])
need(changed==['preparar_analises','total_sem_bloco'])
unchanged=sorted(set(old)-set(changed))
observed=json.loads((ROOT/'restrito/t05/checkpoint.json').read_text(encoding='utf-8'))['observado']
prepared=preparar_analises(observed)
original=json.loads((ROOT/'restrito/t06/entrega/plano-pares.json').read_text(encoding='utf-8'))
need(prepared==original)
serialized=(json.dumps(prepared,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
original_bytes=(ROOT/'restrito/t06/entrega/plano-pares.json').read_bytes()
need(original_bytes.replace(b'\r\n',b'\n')==serialized)
dest=ROOT/'restrito/t06/fix1/plano-pares.json'
need(not dest.exists())
dest.parent.mkdir(parents=True,exist_ok=True)
# Reproduzir a escrita textual nativa usada na entrega (CRLF no Windows).
dest.write_text(serialized.decode('utf-8'),encoding='utf-8')
new_hash=sha(dest)
need(new_hash==PINNED['restrito/t06/entrega/plano-pares.json'])
for name,digest in PINNED.items():need(sha(ROOT/name)==digest)
result=dict(status='COMPATIVEL',base=BASE,funcoes_alteradas=changed,funcoes_identicas_ast=unchanged,
    baseline_modulo_sha256=hashlib.sha256(baseline.encode()).hexdigest(),modulo_atual_sha256=sha(ROOT/'airam/correlacoes.py'),
    config_sha256=sha(ROOT/'config/correlacoes.json'),associacoes_preparadas=len(prepared),
    serializacao_original_crlf=original_bytes.count(b'\r\n'),
    serializacao_memoria_lf=serialized.count(b'\n'),
    linhas_de_pares_conferidas=sum(len(a['pares']) for a in prepared),plano_regerado_sha256=new_hash,
    handoff_preservado_sha256=PINNED['estatistica/t06/entrega/checkpoint.json'],
    inferencia_reexecutada=False,fonte_resultados='08-analise-entrega: execucao original preservada',
    justificativa='Todos os pares/metadados e configuracao identicos; funcoes de inferencia/multiplicidade/reamostragem inalteradas.',
    limites='Valida compatibilidade do preparo, nao reatribui a execucao inferencial antiga ao codigo novo.')
report=ROOT/'evidencias/T06/fix1-compatibilidade.json';need(not report.exists())
report.write_text(json.dumps(result,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
