"""Recibo reprodutível dos testes sintéticos; não lê linhas nominais."""
from datetime import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from airam.recibos import gravar_recibo


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    label, state, *args = sys.argv[1:]
    directory = ROOT / 'evidencias/T02'
    command = [sys.executable, '-m', 'pytest', *args, '-q', '--tb=short']
    timestamp = datetime.now().astimezone().isoformat()
    hashes = {p.relative_to(ROOT).as_posix(): digest(p)
              for folder in ['airam', 'tests'] for p in (ROOT / folder).glob('*.py')}
    hashes['config/analise.json'] = digest(ROOT / 'config/analise.json')
    hashes['evidencias/T02/executar_testes.py'] = digest(Path(__file__))
    hashes_dados = {'catalogo/fontes.json': digest(ROOT / 'catalogo/fontes.json'),
        'manifesto_prioritario': digest(ROOT.parent / 'resultados-caed-ciclo-i-2026/manifesto_coleta.json')}
    execution = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8',
                               env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, errors='strict')
    log = directory / (label + '.log')
    log.write_text(execution.stdout + execution.stderr, encoding='utf-8')
    payload = dict(incremento='T02', requisitos=['R01', 'R02', 'R03', 'R05', 'R08', 'R22'],
        testes=['T07-T09', 'T12-T14', 'T18-T19', 'BOM-Turmma', 'guardas_ingestao'] +
               (['FIX1_P2_esquemas_obrigatorios'] if 'fix1' in label else []),
        estado=state, comando=['.venv/Scripts/python.exe -m pytest ' + ' '.join(command[3:])],
        timestamp=timestamp, codigo_saida=execution.returncode, hashes_codigo=hashes,
        hashes_dados=hashes_dados,
        versoes={'python': platform.python_version(), 'pytest': importlib.metadata.version('pytest')},
        mutacao=None, artefatos=[dict(caminho=log.relative_to(ROOT).as_posix(), sha256=digest(log))],
        limites=['Testes sinteticos locais; nao comprova execucao Core nem validacao externa.'], executor='Codex')
    if (state == 'RED') == (execution.returncode != 0):
        gravar_recibo(directory / (label + '.json'), payload)
    else:
        # Tentativa inesperada permanece explícita, sem recibo com estado falso.
        payload['estado_solicitado'] = payload.pop('estado')
        payload['estado_observado'] = 'FALHA' if execution.returncode else 'SUCESSO_INESPERADO'
        (directory / (label + '-tentativa.json')).write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(execution.stdout.splitlines()[-1] if execution.stdout.splitlines() else 'Sem stdout')
    return execution.returncode


if __name__ == '__main__':
    raise SystemExit(main())
