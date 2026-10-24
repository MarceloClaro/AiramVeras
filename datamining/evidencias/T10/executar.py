"""Recibos contemporâneos T10. Nunca imprime o conteúdo de entradas restritas."""
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
NODE = Path('C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    label, phase, engine, *args = sys.argv[1:]
    folder = ROOT / 'evidencias/T10'
    before = folder / (label + '-antes.json')
    if before.exists():
        raise ValueError('Rotulo existente; preservar historico')
    exe = str(NODE) if engine == 'node' else sys.executable
    paths = [p for part in ['airam','tests','config','docs','reports','evidencias/T10']
             for p in (ROOT/part).rglob('*') if p.is_file() and '__pycache__' not in p.parts
             and p.suffix in {'.py','.mjs','.md','.json','.html'}
             and not p.name.endswith(('-antes.json','-recibo.json'))]
    paths += [ROOT/p for p in ['requirements.lock.txt','pyproject.toml','.gitignore','.gitattributes'] if (ROOT/p).exists()]
    inputs = [p for part in ['restrito/t03','restrito/t05','restrito/t08','restrito/t09',
                            'estatistica/t05','estatistica/t06/entrega','estatistica/t07','estatistica/t08',
                            'estatistica/t09','curriculo/t04'] for p in (ROOT/part).glob('*.json')]
    inputs += [ROOT/p for p in ['evidencias/T08/contraprova-resultado.json','evidencias/T08/fix1-contraprova-resultado.json'] if (ROOT/p).exists()]
    inputs += [ROOT/a for a in args if a.endswith('.json') and (ROOT/a).is_file()]
    primary_pdf=ROOT.parent/'MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf'
    if primary_pdf.is_file():inputs.append(primary_pdf)
    tool_manifest=Path('C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/@oai/artifact-tool/package.json')
    snap = dict(timestamp=datetime.now(timezone.utc).isoformat(), comando=[exe,*args],
        python=platform.python_version(),node=subprocess.check_output([str(NODE),'--version'],text=True).strip(),
        runtime_bundle='26.1020.11127',artifact_tool=json.loads(tool_manifest.read_text(encoding='utf-8'))['version'],
        artifact_tool_manifest_sha256=sha(tool_manifest),
        versoes={d.metadata['Name']:d.version for d in importlib.metadata.distributions()},
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        branch=subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        hashes_codigo={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(set(paths))},
        hashes_entradas={os.path.relpath(p,ROOT).replace('\\','/'):sha(p) for p in sorted(set(inputs))},
        ausentes=[p for p in ['airam/relatorio.py','reports/build_workbook.mjs','reports/templates/relatorio.html'] if not (ROOT/p).exists()]
            +([] if primary_pdf.exists() else ['../'+primary_pdf.name]))
    before.write_text(json.dumps(snap,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    log = folder/(label+'.log')
    with log.open('w',encoding='utf-8') as stream:
        process = subprocess.run([exe,*args],cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,text=True,encoding='utf-8',
            env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
    receipt = dict(fase=phase,codigo_saida=process.returncode,fim=datetime.now(timezone.utc).isoformat(),
        snapshot=before.name,snapshot_sha256=sha(before),log=log.name,log_sha256=sha(log))
    (folder/(label+'-recibo.json')).write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
    # Executores reais só publicam agregados. Logs de pytest usam fixtures artificiais.
    print(log.read_text(encoding='utf-8')[-2200:])
    return process.returncode


if __name__ == '__main__':
    raise SystemExit(main())
