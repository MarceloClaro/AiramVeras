"""Captura estado ANTES de comandos T04; somente entradas públicas e hashes restritos."""
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
PDF = ROOT.parent / 'MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf'
BNCC = ROOT.parent / 'bncc-dados'
MAPA = ROOT.parent / 'resultados-caed-ciclo-i-2026/conferencia/mapa_posicao_codigo_caed.csv'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    label, phase, *args = sys.argv[1:]
    directory = ROOT / 'evidencias/T04'
    if (directory / f'{label}-antes.json').exists():
        raise ValueError('Nome de execucao ja utilizado; preserve o historico')
    command = [sys.executable, *args]
    paths = [p for folder in ['airam', 'tests', 'config', 'docs', 'evidencias/T04']
             for p in (ROOT / folder).rglob('*')
             if p.is_file() and p.suffix in {'.py', '.json', '.md'} and '__pycache__' not in p.parts]
    paths += [ROOT / name for name in ['requirements.lock.txt', 'pyproject.toml']]
    inputs = [PDF, MAPA, BNCC / 'dados/bncc-2018/ensino-fundamental.json',
              ROOT / 'restrito/t03/tabelas.json']
    checkpoint = ROOT / 'curriculo/t04/checkpoint.json'
    if checkpoint.exists():
        inputs.append(checkpoint)
    before = dict(timestamp=datetime.now(timezone.utc).isoformat(), comando=command,
        hashes_codigo={p.relative_to(ROOT).as_posix(): digest(p) for p in sorted(set(paths))},
        hashes_dados={os.path.relpath(p, ROOT).replace('\\', '/'): digest(p) for p in inputs},
        versoes={name: importlib.metadata.version(name) for name in ['pytest', 'pdfplumber', 'pypdf']},
        python=platform.python_version(),
        head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        bncc_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=BNCC, text=True).strip(),
        ausentes=[f'airam/{name}.py' for name in ['matriz_cnca', 'bncc', 'vinculos']
                  if not (ROOT / f'airam/{name}.py').exists()])
    (directory / f'{label}-antes.json').write_text(json.dumps(before, indent=2) + '\n', encoding='utf-8')
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                            env={**os.environ, 'PYTHONIOENCODING': 'utf-8', 'PYTHONUTF8': '1'})
    log = directory / f'{label}.log'
    log.write_text(result.stdout + result.stderr, encoding='utf-8')
    receipt = dict(estado=('RED' if result.returncode else 'SUCESSO_INESPERADO') if phase == 'RED'
                   else (phase if result.returncode == 0 else 'FALHA'),
                   fase_solicitada=phase, codigo_saida=result.returncode,
                   fim=datetime.now(timezone.utc).isoformat(), snapshot=f'{label}-antes.json',
                   snapshot_sha256=digest(directory / f'{label}-antes.json'), log_sha256=digest(log))
    (directory / f'{label}-recibo.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(receipt))
    print(result.stdout[-2000:])
    return result.returncode


if __name__ == '__main__':
    raise SystemExit(main())
