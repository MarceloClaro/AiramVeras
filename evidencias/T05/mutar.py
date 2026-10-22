"""T55 em cópia isolada; snapshot mutado anterior ao pytest e falha preservada."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
folder=ROOT/'restrito/t05/mutacao-T55'
folder.mkdir(parents=True,exist_ok=False)
for part in ('airam','tests'):
    shutil.copytree(ROOT/part,folder/part,ignore=shutil.ignore_patterns('__pycache__'))
for name in ('pyproject.toml','requirements.lock.txt'):
    shutil.copyfile(ROOT/name,folder/name)
p=folder/'airam/metricas.py'
source=p.read_text(encoding='utf-8')
old='return sum(acertos) / sum(oportunidades) if oportunidades else None'
assert source.count(old)==1
p.write_text(source.replace(old,'return sum(n/d for n,d in zip(acertos,oportunidades)) / len(oportunidades) if oportunidades else None'),encoding='utf-8')
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
command=[sys.executable,'-m','pytest','tests/test_metricas.py::test_T10_razao_de_somas_nunca_media_simples','-q']
before=dict(timestamp=datetime.now(timezone.utc).isoformat(),comando=command,
    hashes={p.relative_to(folder).as_posix():sha(p) for p in sorted(folder.rglob('*')) if p.is_file()},
    mutacao='T55: razao de somas substituida por media simples das taxas',isolado=True)
evidence=ROOT/'evidencias/T05'
(evidence/'T55-antes.json').write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
result=subprocess.run(command,cwd=folder,capture_output=True,text=True,encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8'})
log=evidence/'T55.log'
log.write_text(result.stdout+result.stderr,encoding='utf-8')
receipt=dict(codigo_saida=result.returncode,mutacao_morta=result.returncode==1 and 'assert 0.5 == 0.25' in result.stdout,
    log_sha256=sha(log),snapshot_sha256=sha(evidence/'T55-antes.json'))
(evidence/'T55-recibo.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
if not receipt['mutacao_morta']:
    raise SystemExit(1)
