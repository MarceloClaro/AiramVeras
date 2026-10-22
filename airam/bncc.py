"""Consumo somente leitura do núcleo canônico de habilidades EF da BNCC."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess

BNCC_COMMIT = '9c268978efa2aa250834c6a9edb6074432752838'
CANONICO = 'dados/bncc-2018/ensino-fundamental.json'


def carregar_bncc(root: Path, expected_commit: str) -> dict[str, dict]:
    root = Path(root)
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if expected_commit != BNCC_COMMIT or head != expected_commit:
        raise ValueError('commit BNCC diverge da versao fixada')
    raw = (root / CANONICO).read_bytes()
    committed = subprocess.check_output(['git', 'show', f'{expected_commit}:{CANONICO}'], cwd=root)
    # Windows pode converter LF para CRLF no checkout; esta é a única normalização admitida.
    if raw.replace(b'\r\n', b'\n') != committed.replace(b'\r\n', b'\n'):
        raise ValueError('Fonte canonica BNCC modificada em relacao ao commit')
    source = dict(commit=head, arquivo=CANONICO, sha256=hashlib.sha256(raw).hexdigest(),
                  sha256_git=hashlib.sha256(committed).hexdigest(), documento='bncc-2018')
    result = {}
    for original in json.loads(raw)['habilidades']:
        if original['vigencia']['status'] != 'vigente':
            continue
        code = original['codigo']
        if code in result:
            raise ValueError('Codigo BNCC canonico duplicado')
        row = deepcopy(original)
        row['proveniencia_dataset'] = dict(source)
        result[code] = row
    return result
