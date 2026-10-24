"""Snapshot contemporâneo e execução sem expor registros individuais."""
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    label, phase, *args = sys.argv[1:]
    folder = ROOT / 'evidencias/T06'
    before_path = folder / (label + '-antes.json')
    if before_path.exists():
        raise ValueError('Rotulo existente: preservar historico')
    paths = [p for part in ['airam', 'tests', 'config', 'docs', 'evidencias/T06']
        for p in (ROOT / part).rglob('*') if p.is_file()
        and '__pycache__' not in p.parts and p.suffix in {'.py', '.md', '.json'}
        and not p.name.endswith(('-antes.json', '-recibo.json'))]
    paths += [ROOT / p for p in ['requirements.lock.txt', 'pyproject.toml']]
    paths += [ROOT / p for p in ['.gitattributes','.gitignore'] if (ROOT/p).exists()]
    sources = ROOT.parent / 'resultados-caed-ciclo-i-2026'
    inputs = [ROOT / p for p in ['restrito/t05/checkpoint.json', 'estatistica/t05/checkpoint.json', 'restrito/t03/tabelas.json', 'curriculo/t04/checkpoint.json']]
    inputs += [ROOT / p for p in ['restrito/t06/entrega/plano-pares.json',
        'estatistica/t06/entrega/checkpoint.json', 'estatistica/t06/entrega/associacoes.csv',
        'estatistica/t06/entrega/plano.json', 'estatistica/t06/entrega/instrumentos.json']]
    inputs += [sources / 'manifesto_coleta.json', *sources.rglob('*.zip'), *sources.rglob('csv_originais/**/*.csv')]
    snapshot = dict(timestamp=datetime.now(timezone.utc).isoformat(), comando=[sys.executable, *args],
        python=platform.python_version(), versoes={d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        hashes_codigo={os.path.relpath(p,ROOT).replace('\\','/'):sha(p) for p in sorted(set(paths))},
        hashes_entradas={os.path.relpath(p,ROOT).replace('\\','/'):sha(p) for p in sorted(set(inputs))},
        ausentes=[f'airam/{m}.py' for m in ['correlacoes'] if not (ROOT/f'airam/{m}.py').exists()])
    before_path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    process = subprocess.run([sys.executable,*args], cwd=ROOT, capture_output=True,text=True,encoding='utf-8',
        env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
    log = folder / (label+'.log')
    log.write_text(process.stdout+process.stderr,encoding='utf-8')
    receipt = dict(fase=phase,codigo_saida=process.returncode,
        fim=datetime.now(timezone.utc).isoformat(),snapshot=before_path.name,snapshot_sha256=sha(before_path),
        log=log.name,log_sha256=sha(log))
    (folder/(label+'-recibo.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    print(process.stdout[-1600:])
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())

