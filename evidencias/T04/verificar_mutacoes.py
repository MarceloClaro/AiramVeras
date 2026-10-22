"""Contraprovas reais: alterar regra, rodar teste, restaurar bytes originais."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
CASES = [
    ('centro_ciclo', 'airam/matriz_cnca.py', "and x0 <= w['x0'] and w['x1'] <= x1",
     "and abs(w['x0'] - (x0 + x1) / 2) < 10 and w['x1'] <= x1",
     'tests/test_matriz_cnca.py::test_T31_x_deslocado_pagina7_pertence_a_celula_ciclo_i'),
    ('uniao_global', 'airam/vinculos.py', "candidates = own or [o for o in matches if o['ano_tabela'] < year]",
     'candidates = matches  # mutacao: mistura contextos de anos diferentes',
     'tests/test_vinculos.py::test_T27_nao_une_conjuntos_de_anos_ou_textos_divergentes'),
    ('bncc_inativa', 'airam/vinculos.py', "and normative.get('vigencia', {}).get('status') == 'vigente'",
     'and True  # mutacao: ignora vigencia\n                             ',
     'tests/test_vinculos.py::test_T29_inexistente_ou_inativo_permanece_nao_confirmado'),
    ('sem_ressalva', 'airam/vinculos.py', "semantica = any(code in r['codigos_caed'] and bc == r['codigo_bncc'] for r in config['regras'])",
     'semantica = False  # mutacao: omite ressalva semantica',
     'tests/test_vinculos.py::test_T30_ressalva_semantica_preserva_os_dois_textos'),
]


def main():
    results = []
    for name, filename, before, after, test in CASES:
        path = ROOT / filename
        raw = path.read_bytes()
        source = raw.decode('utf-8')
        if source.count(before) != 1:
            raise ValueError('Alvo de mutacao ambiguo')
        try:
            path.write_text(source.replace(before, after), encoding='utf-8')
            code = subprocess.run([sys.executable, 'evidencias/T04/executar.py', 'mutacao-' + name,
                                   'RED', '-m', 'pytest', test, '-q', '--tb=short'], cwd=ROOT).returncode
            results.append(dict(mutacao=name, teste=test, codigo_saida=code,
                                original_sha256=hashlib.sha256(raw).hexdigest(), detectada=code == 1))
            if code != 1:
                raise ValueError('Mutacao nao foi detectada por falha de assercao')
        finally:
            path.write_bytes(raw)
            if path.read_bytes() != raw:
                raise ValueError('Restauracao de fonte falhou')
    (ROOT / 'evidencias/T04/mutacoes-resumo.json').write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results))


if __name__ == '__main__':
    main()
