"""Auditoria sem chamar APIs produtoras; fontes públicas via leitor PDF independente."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    path = ROOT / 'curriculo/t04/checkpoint.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    canonical = json.loads((ROOT.parent / 'bncc-dados/dados/bncc-2018/ensino-fundamental.json').read_text(encoding='utf-8'))
    by_code = {r['codigo']: r for r in canonical['habilidades']}
    for code, row in data['bncc'].items():
        assert {k: v for k, v in row.items() if k != 'proveniencia_dataset'} == by_code[code]
    pdf = ROOT.parent / data['fontes']['matriz']['arquivo']
    assert digest(pdf) == data['fontes']['matriz']['sha256']
    reader = PdfReader(pdf)
    occurrences = data['ocorrencias_matriz']
    for page in {r['pagina_matriz'] for r in occurrences}:
        text = reader.pages[page - 1].extract_text()
        rows = [o for o in occurrences if o['pagina_matriz'] == page]
        assert Counter(re.findall(r'\b[1-5]EF\d{2}_[PM]\b', text)) == Counter(o['codigo_caed'] for o in rows)
        assert Counter(re.findall(r'\bEF\d{2}(?:LP|MA)\d{2}\b', text)) == Counter(c for o in rows for c in o['codigos_bncc'])
        for row in rows:
            for mark in row['marcas_ciclo']:
                x0, y0, x1, y1 = row['celulas'][mark['ciclo']]
                mx0, my0, mx1, my1 = mark['bbox']
                assert x0 <= mx0 < mx1 <= x1 and y0 <= my0 < my1 <= y1
    links = data['vinculos_posicoes']
    assert len({r['vinculo_id'] for r in links}) == len(links)
    semantic = []
    weights = {}
    for row in links:
        assert not {'aluno_local_id', 'nome', 'acertos', 'oportunidades', 'taxa', 'percentual'} & row.keys()
        o = next(o for o in occurrences if o['ocorrencia_id'] == row['ocorrencia_id'])
        assert row['texto_caed'] == o['texto_caed']
        assert row['codigo_bncc'] in o['codigos_bncc']
        assert row['texto_bncc'] == by_code[row['codigo_bncc']]['texto']
        assert row['localizador_bncc'] == by_code[row['codigo_bncc']]['fonte']
        assert row['ano_tabela'] == o['ano_tabela'] and row['pagina_matriz'] == o['pagina_matriz']
        if row['status_contextual'] == 'fonte_anterior_integracao_a_confirmar':
            assert row['ano_tabela'] < row['ano_avaliado'] and row['peso_analitico'] == 0
        else:
            assert row['ano_tabela'] == row['ano_avaliado'] and row['ciclo_avaliado'] in o['ciclos']
        weights.setdefault(row['posicao_id'], []).append(row['peso_analitico'])
        if row['status_semantico'] == 'associacao_publicada_com_ressalva_semantica':
            semantic.append(row['posicao_id'])
    weight_counts = Counter(round(sum(w), 10) for w in weights.values())
    assert weight_counts == {1.: 118, 0.: 6}
    assert len(set(semantic)) == 9
    assert all(o['nota_integracao'] for o in occurrences if o['ano_tabela'] in {4, 5})
    renderer = shutil.which('pdftoppm')
    assert renderer
    figures = ROOT / 'evidencias/T04/figuras'
    figures.mkdir(exist_ok=True)
    hashes = {}
    for page in [23, 25, 27]:
        prefix = figures / f'matriz-pagina-{page}'
        subprocess.run([renderer, '-f', str(page), '-l', str(page), '-singlefile', '-r', '110',
                        '-png', str(pdf), str(prefix)], check=True, capture_output=True)
        hashes[str(page)] = digest(prefix.with_suffix('.png'))
    result = dict(status='PASS', checkpoint_sha256=digest(path), leitor_independente='pypdf',
        paginas_conferidas=len({o['pagina_matriz'] for o in occurrences}),
        ocorrencias=len(occurrences), vinculos=len(links), posicoes=len(weights),
        conferencia_bncc='Textos e fontes iguais ao JSON canônico, sem reescrita',
        pesos_por_posicao={'unitario': weight_counts[1.], 'zero_integracao_a_confirmar': weight_counts[0.]},
        figuras_sha256=hashes, renderer_sha256=digest(Path(renderer)))
    (ROOT / 'evidencias/T04/auditoria-checkpoint.json').write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    main()
