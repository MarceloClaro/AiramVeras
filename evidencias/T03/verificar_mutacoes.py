"""Mutações temporárias; restauração garantida e recibos reais do código mutado."""
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
cases = [
    ('duplicata-matricula', 'airam/identidade.py', 'if key in keys or ref in refs:',
     'if False:', 'tests/test_identidade.py::test_t04_duplicata_normalizada_ou_referencia_repetida_bloqueia'),
    ('fanout', 'airam/pareamento.py', 'if component in group:', 'if False:',
     'tests/test_pareamento.py::test_duplicata_bloqueia_fanout_e_nao_faz_produto_cartesiano'),
    ('valores-t38', 'airam/pareamento.py',
     'if Counter(consumed) != Counter(serial(r) for r in source):', 'if False:',
     'tests/test_pareamento.py::test_t38_auditoria_rejeita_par_adulterado_mesmo_com_mesmos_ids'),
]
for label, filename, old, new, test in cases:
    path = ROOT / filename
    original = path.read_bytes()
    text = original.decode('utf-8')
    if text.count(old) != 1:
        raise ValueError('Mutacao ambigua')
    try:
        path.write_text(text.replace(old, new), encoding='utf-8')
        execution = subprocess.run([sys.executable, 'evidencias/T03/executar_testes.py',
                                    'mutacao-' + label, 'RED', test], cwd=ROOT)
        if execution.returncode != 1:
            raise ValueError('Mutacao nao detectada como falha funcional')
    finally:
        path.write_bytes(original)
