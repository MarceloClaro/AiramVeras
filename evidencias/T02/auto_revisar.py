"""Confere artefatos/hashes e ausência literal dos nomes reais nas saídas públicas."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    suffix = '-' + sys.argv[1] if len(sys.argv) > 1 else ''
    if suffix and not re.fullmatch(r'-[a-z0-9-]+', suffix):
        raise ValueError('Rotulo de evidencia invalido')
    checkpoint = ROOT / 'restrito/t02/tabelas.json'
    data = json.loads(checkpoint.read_text(encoding='utf-8'))
    paths = [*(ROOT / 'airam').glob('*.py'), *(ROOT / 'tests').glob('*.py'),
             *(ROOT / 'docs').rglob('*'), *(ROOT / 'evidencias/T02').glob('*')]
    paths = [p for p in paths if p.is_file()]
    names = {m['nome_bruto'].strip().casefold() for m in data['matriculas']}
    leaked = sum(any(name in p.read_text(encoding='utf-8-sig').casefold() for name in names)
                 for p in paths)
    assert leaked == 0, 'Saida publica exige revisao de sigilo'
    artifacts_verified = 0
    for path in (ROOT / 'evidencias/T02').glob('*.json'):
        record = json.loads(path.read_text(encoding='utf-8-sig'))
        if not isinstance(record, dict) or 'artefatos' not in record:
            continue
        for artifact in record['artefatos']:
            assert digest(ROOT / artifact['caminho']) == artifact['sha256']
            artifacts_verified += 1
    receipt = json.loads((ROOT / ('evidencias/T02/final' + suffix + '.json')).read_text(encoding='utf-8'))
    for relative, expected in receipt['hashes_codigo'].items():
        assert digest(ROOT / relative) == expected
    current = json.loads((ROOT / ('evidencias/T02/checkpoint-recibo' + suffix + '.json')).read_text(encoding='utf-8'))
    for relative, expected in current['hashes_codigo'].items():
        assert digest(ROOT / relative) == expected
    ignored = subprocess.run(['git', 'check-ignore', 'restrito/t02/tabelas.json'],
                             cwd=ROOT, capture_output=True, text=True)
    assert ignored.returncode == 0
    output = dict(timestamp=datetime.now().astimezone().isoformat(),
        arquivos_publicos_inspecionados=len(paths), arquivos_com_nomes_reais=leaked,
        artefatos_hashes_conferidos=artifacts_verified, hashes_codigo_final_conferidos=len(receipt['hashes_codigo']),
        checkpoint_sha256=digest(checkpoint), checkpoint_nominal_ignorado=True,
        limites=['Busca literal de nomes completos nao substitui revisao humana de sigilo.',
                 'Hashes historicos de RED/mutacoes nao sao substituidos pelos hashes atuais.',
                 'Relatorio local em .superpowers permanece ignorado; bootstrap alheio nao sera commitado.'],
        revisao=['Interfaces e cinco tabelas centrais conferidas contra brief e regras do controlador.',
                 'Duplicatas intracompontente bloqueadas; origens entre componentes preservadas.',
                 'Zeros, nao participantes e campos ausentes separados; aplicabilidade nao inferida.',
                 'CSV canonico, manifesto, ZIP e metadados conferidos; fontes nao alteradas.',
                 'T03 recebe referencia local e nomes somente no checkpoint restrito.'])
    (ROOT / ('evidencias/T02/auto-revisao' + suffix + '.json')).write_text(json.dumps(output, indent=2), encoding='utf-8')
    print('Auto revisao: hashes conferidos, nomes reais ausentes das saidas publicas, checkpoint ignorado')


if __name__ == '__main__':
    main()
