"""Mutações temporárias, restauradas mesmo em falha; somente testes sintéticos."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def main():
    cases = [
        ('mutacao-limite-contagens', 'airam/esquemas.py', 'numerator > denominator', 'False',
         'tests/test_ingestao.py::test_t07_rejeita_contagens_impossiveis[3/2]'),
        ('mutacao-duplicata', 'airam/ingestao.py', 'if duplicate_key in seen:',
         'if False and duplicate_key in seen:', 'tests/test_ingestao.py::test_duplicata_intracomponente_rejeitada'),
        ('mutacao-ausencia-zero', 'airam/esquemas.py', 'denominador=None, valor=None,',
         'denominador=None, valor=0,', 'tests/test_participacao.py::test_t19_hifen_nao_vira_zero_nem_imputa_motivo')]
    evidence = []
    for label, relative, original, replacement, test in cases:
        path = ROOT / relative
        before = path.read_bytes()
        text = before.decode('utf-8')
        assert text.count(original) == 1
        try:
            path.write_text(text.replace(original, replacement), encoding='utf-8')
            run = subprocess.run([sys.executable, 'evidencias/T02/executar_testes.py', label, 'RED', test],
                                 cwd=ROOT, capture_output=True, text=True)
            assert run.returncode != 0
            receipt_path = ROOT / ('evidencias/T02/' + label + '.json')
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            receipt['mutacao'] = label
            sys.path.insert(0, str(ROOT))
            from airam.recibos import gravar_recibo
            gravar_recibo(receipt_path, receipt)
        finally:
            path.write_bytes(before)
        assert path.read_bytes() == before
        evidence.append(dict(mutacao=label, codigo_saida=run.returncode,
                             sha256_restaurado=hashlib.sha256(before).hexdigest()))
    (ROOT / 'evidencias/T02/mutacoes-restauracao.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
    print('3 mutacoes detectadas; fontes de codigo restauradas byte a byte')


if __name__ == '__main__':
    main()
