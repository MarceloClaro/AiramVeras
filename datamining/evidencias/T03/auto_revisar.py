"""Confere estado final e sigilo literal sem imprimir nomes, IDs ou segredo."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    folder = ROOT / 'evidencias/T03'
    timestamp = datetime.now().astimezone().isoformat()
    before = dict(timestamp=timestamp, python=platform.python_version(),
                  hashes_codigo={p.relative_to(ROOT).as_posix(): digest(p)
                      for directory in ['airam', 'tests', 'evidencias/T03']
                      for p in (ROOT / directory).glob('*.py')},
                  hashes_dados={'restrito/t03/tabelas.json': digest(ROOT / 'restrito/t03/tabelas.json'),
                                'restrito/t03/mapa-nominal.json': digest(ROOT / 'restrito/t03/mapa-nominal.json')})
    (folder / 'auto-revisao-antes.json').write_text(json.dumps(before, indent=2), encoding='utf-8')
    summary = json.loads((folder / 'suite-atual.json').read_text(encoding='utf-8'))
    if summary['codigo_saida'] != 0:
        raise ValueError('Suite final nao aprovada')
    for filename, expected in summary['hashes_codigo'].items():
        if digest(ROOT / filename) != expected:
            raise ValueError('Codigo atual diverge da suite final')
    for artifact in summary['artefatos']:
        if digest(ROOT / artifact['caminho']) != artifact['sha256']:
            raise ValueError('Log da suite alterado')
    data = json.loads((ROOT / 'restrito/t02/tabelas.json').read_text(encoding='utf-8'))
    mapping = json.loads((ROOT / 'restrito/t03/mapa-nominal.json').read_text(encoding='utf-8'))
    forbidden = {r[k] for r in data['matriculas'] for k in ['nome_bruto', 'nome_normalizado', 'matricula_local_id']}
    forbidden.update(r['aluno_local_id'] for r in mapping)
    paths = [p for directory in ['airam', 'tests', 'docs', 'evidencias/T03']
             for p in (ROOT / directory).rglob('*') if p.suffix in {'.py', '.json', '.log', '.md'}]
    leaks = sum(any(term and term in p.read_text(encoding='utf-8-sig') for term in forbidden) for p in paths)
    if leaks:
        raise ValueError('Dado individual encontrado na area publica')
    ignored = subprocess.run(['git', 'check-ignore', '-q', 'restrito/t03/tabelas.json'], cwd=ROOT).returncode == 0
    if not ignored:
        raise ValueError('Checkpoint nao esta ignorado')
    result = dict(timestamp=timestamp, executor='Codex', codigo_saida=0,
                  arquivos_publicos_conferidos=len(paths), correspondencias_individuais=leaks,
                  suite_atual_hashes_reconciliados=True, checkpoint_ignorado=True,
                  checkpoint_sha256=digest(ROOT / 'restrito/t03/tabelas.json'))
    (folder / 'auto-revisao.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
