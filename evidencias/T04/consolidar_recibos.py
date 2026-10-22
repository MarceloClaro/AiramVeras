"""Converte registros já preservados ao contrato T53, sem reexecutar ou retroatribuir hashes."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from airam.recibos import gravar_recibo


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


directory = ROOT / 'evidencias/T04'
labels = ['red-funcional', 'red-unicidade', 'green-focal-01', 'green-focal-final', 'green-suite-integral',
          'mutacao-centro_ciclo', 'mutacao-uniao_global', 'mutacao-bncc_inativa', 'mutacao-sem_ressalva']
for label in labels:
    source = directory / f'{label}-recibo.json'
    receipt = json.loads(source.read_text(encoding='utf-8'))
    before = directory / receipt['snapshot']
    snapshot = json.loads(before.read_text(encoding='utf-8'))
    log = directory / f'{label}.log'
    assert digest(before) == receipt['snapshot_sha256'] and digest(log) == receipt['log_sha256']
    payload = dict(incremento='T04', requisitos=['R01', 'R12', 'R21', 'R22', 'R23', 'R24'],
        testes=['T26', 'T27', 'T28', 'T29', 'T30', 'T31', 'unicidade_e_pesos'],
        estado=receipt['estado'], comando=snapshot['comando'], timestamp=snapshot['timestamp'],
        codigo_saida=receipt['codigo_saida'], hashes_codigo=snapshot['hashes_codigo'],
        hashes_dados=snapshot['hashes_dados'], versoes=dict(snapshot['versoes'], python=snapshot['python']),
        mutacao=label if label.startswith('mutacao-') else None,
        artefatos=[dict(caminho=p.relative_to(ROOT).as_posix(), sha256=digest(p)) for p in [before, source, log]],
        limites=['Consolidacao T53 posterior de registros reais preservados; hashes e timestamp sao os capturados ANTES da execucao original, sem retroatribuicao.',
                 'Lista T26-T31 identifica o incremento; o comando e o log delimitam os testes realmente executados em cada recibo.',
                 'Validacao documental/computacional local; sem inferencia Core ou validacao pedagogica externa.'],
        executor='Codex executor local')
    gravar_recibo(directory / f'{label}-rastreavel.json', payload)
print(json.dumps({'recibos_t53_consolidados': len(labels), 'originais_preservados': True,
                  'red_inicial_com_setup_errors_excluido': True}))
