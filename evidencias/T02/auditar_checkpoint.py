"""Contraprova independente de CSV bruto; só imprime contagens e hashes."""
from collections import Counter, defaultdict
import csv
from datetime import datetime
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from airam.ingestao import ler_exportacoes
from airam.recibos import gravar_recibo


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def main():
    suffix = '-' + sys.argv[1] if len(sys.argv) > 1 else ''
    if suffix and not re.fullmatch(r'-[a-z0-9-]+', suffix):
        raise ValueError('Rotulo de evidencia invalido')
    timestamp = datetime.now().astimezone().isoformat()
    config = json.loads((ROOT / 'config/analise.json').read_text(encoding='utf-8-sig'))
    sources = (ROOT / config['raiz_fontes']).resolve()
    manifest = sources / config['fontes']['coleta_ciclo_i_2026']['caminho']
    catalog_path = ROOT / 'catalogo/fontes.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8-sig'))
    canonical = list((manifest.parent / 'csv_originais').rglob('*.csv'))
    before = {p.relative_to(sources).as_posix(): digest(p) for p in canonical}
    data = ler_exportacoes(catalog)
    assert len(canonical) == 54
    assert len({r['exportacao'] for r in data['avaliacoes']}) == 18
    assert {k: len(v) for k, v in data.items()} == dict(matriculas=172, avaliacoes=640,
        habilidades=4618, escrita=864, fluencia=592, agregados=44, disponibilidade_arquivos=20)
    # Deriva contagens e cada par H dos CSVs, sem chamar parser/somador do produto.
    raw_rows = {}
    source_by_path = {r['caminho']: r for r in catalog}
    independent = defaultdict(lambda: dict(cadastros=0, avaliados=0, total_22=0))
    for path in canonical:
        relative = path.relative_to(sources).as_posix()
        with path.open(encoding='utf-8-sig', newline='') as stream:
            reader = csv.DictReader(stream, delimiter=';')
            for line, row in enumerate(reader, 2):
                if 'Estudante' not in row:
                    continue
                raw_rows[(relative, line)] = row
                assessment = source_by_path[relative]['avaliacao']
                key = (assessment['ano_escolar'], assessment['componente'])
                counts = independent[key]
                counts['cadastros'] += 1
                flag = row.get('Avaliado', row.get('Participação')).strip()
                assert flag in {'Sim', 'Não'}
                counts['avaliados'] += flag == 'Sim'
                fields = [h for h in row if re.fullmatch(r'H \d+', h)]
                if fields and flag == 'Sim':
                    total = 0
                    for h in fields:
                        parts = row[h].strip().split('/')
                        assert len(parts) == 2
                        n, d = [int(p.strip()) for p in parts]
                        assert 0 <= n <= d and d > 0
                        total += d
                    assert total == 22
                    counts['total_22'] += 1
    expected_sizes = {1: 24, 2: 28, 3: 24, 4: 42, 5: 54}
    absences = {(5, 'LEITURA'): 1, (4, 'ESCRITA'): 1, (5, 'ESCRITA'): 2, (5, 'FLUENCIA'): 2}
    for key, counts in independent.items():
        assert counts['cadastros'] == expected_sizes[key[0]]
        assert counts['avaliados'] == expected_sizes[key[0]] - absences.get(key, 0)
    assert len(independent) == 18
    for av in data['avaliacoes']:
        row = raw_rows[(av['caminho'], av['linha_fonte'])]
        assert av['participacao'] == (row.get('Avaliado', row.get('Participação')).strip() == 'Sim')
        fields = [h for h in row if re.fullmatch(r'H \d+', h)]
        if fields and av['participacao']:
            n = sum(int(row[h].split('/')[0].strip()) for h in fields)
            d = sum(int(row[h].split('/')[1].strip()) for h in fields)
            assert (av['acertos'], av['oportunidades']) == (n, d)
        elif fields:
            assert av['acertos'] is None and av['oportunidades'] is None
        assert av['data_aplicacao'] is None
    for table in ['habilidades', 'escrita', 'fluencia']:
        for m in data[table]:
            row = raw_rows[(m['caminho'], m['linha_fonte'])]
            raw = row[m['campo_original']]
            assert m['bruto'] == raw
            missing = raw.strip().casefold() in {'', '-', 'sem resultado'}
            assert m['disponibilidade'] is not missing
            if missing:
                assert m['valor'] is None and m['numerador'] is None and m['denominador'] is None
            elif m['unidade'] in {'acertos_itens', 'palavras_total'}:
                parts = re.split('/| de ', raw.strip())
                assert (m['numerador'], m['denominador']) == tuple(int(p.strip()) for p in parts)
            elif m['unidade'] == 'nota_escrita':
                assert m['valor'] == float(raw.strip())
            elif m['unidade'] == 'palavras':
                n, p = raw.strip().split('-')
                assert m['valor'] == int(n.strip()) and m['percentual'] == float(p.strip().removesuffix('%'))
                assert m['denominador'] is None and m['duracao_segundos'] is None
    available_text = {year: sum(m['ano_escolar'] == year and m['disponibilidade']
        and m['campo_original'] == 'Texto (Palavras corretas)' for m in data['fluencia']) for year in range(2, 6)}
    assert available_text == {2: 0, 3: 8, 4: 31, 5: 41}
    missing_aspects = Counter(m['campo_original'] for m in data['escrita']
                              if m['ano_escolar'] == 2 and not m['disponibilidade'])
    assert dict(missing_aspects) == {'Questão 1 - Aspecto 1': 6, 'Questão 2 - Aspecto 1': 6, 'Questão 3 - Aspecto 1': 6}
    assert sum(not m['disponibilidade'] for m in data['habilidades']) == 16
    assert sum(a['oportunidades'] == 22 for a in data['avaliacoes']) == 343
    assert [digest(p) for p in canonical] == [before[p.relative_to(sources).as_posix()] for p in canonical]
    checkpoint = ROOT / 'restrito/t02/tabelas.json'
    write(checkpoint, data)
    files = [checkpoint]
    for table, rows in data.items():
        path = checkpoint.parent / (table + '.json')
        write(path, rows)
        files.append(path)
    schemas = {table: {field: sorted({type(row[field]).__name__ for row in rows if field in row})
                       for field in sorted({f for row in rows for f in row})}
               for table, rows in data.items()}
    schema_path = ROOT / 'docs/esquemas-t02.json'
    write(schema_path, schemas)
    summary = dict(timestamp=timestamp, contagens={k: len(v) for k, v in data.items()},
        exportacoes=18, csvs=54, oportunidades_22_avaliados=343,
        contagens_independentes=[dict(ano_escolar=y, componente=c, **v)
                               for (y, c), v in sorted(independent.items())],
        disponibilidade_texto_fluencia_por_ano=available_text,
        ausencias_h=16, ausencias_aspectos_escrita_2ano=dict(missing_aspects),
        zeros_legitimos={table: sum(m['disponibilidade'] and m['valor'] == 0 for m in data[table])
                        for table in ['habilidades', 'escrita', 'fluencia']},
        checkpoint=[dict(caminho=p.relative_to(ROOT).as_posix(), sha256=digest(p)) for p in files],
        hashes_fontes=before, hash_catalogo=digest(catalog_path), hash_manifesto=digest(manifest),
        fontes_inalteradas=True)
    summary_path = ROOT / ('evidencias/T02/contraprova' + suffix + '.json')
    write(summary_path, summary)
    gravar_recibo(ROOT / ('evidencias/T02/checkpoint-recibo' + suffix + '.json'), dict(incremento='T02',
        requisitos=['R01', 'R02', 'R03', 'R05', 'R08', 'R22'],
        testes=['T07-T09', 'T12-T14', 'T18-T19', 'contraprova_54_csv'] + (['FIX1_P2_esquemas_obrigatorios'] if suffix else []), estado='GREEN',
        comando=['.venv/Scripts/python.exe evidencias/T02/auditar_checkpoint.py' + (' ' + sys.argv[1] if suffix else '')],
        timestamp=timestamp, codigo_saida=0,
        hashes_codigo={p.relative_to(ROOT).as_posix(): digest(p) for p in
                       [ROOT / 'airam/ingestao.py', ROOT / 'airam/esquemas.py', Path(__file__)]},
        hashes_dados={**before, 'catalogo/fontes.json': digest(catalog_path),
                      'manifesto_prioritario': digest(manifest)},
        versoes={'python': platform.python_version(), 'pytest': importlib.metadata.version('pytest')},
        mutacao=None, artefatos=[dict(caminho=p.relative_to(ROOT).as_posix(), sha256=digest(p))
                                for p in files + [schema_path, summary_path]],
        limites=['Contraprova independente usa stdlib e os CSVs brutos, sem reutilizar parser/somador do produto.',
                 'Checkpoint nominal local restrito e ignorado pelo Git; pseudonimizacao na T03.',
                 'Nao comprova inferencia Core nem validacao externa das classificacoes CAEd.'], executor='Codex'))
    print(json.dumps({'contagens': summary['contagens'], 'checkpoint_sha256': digest(checkpoint)}, sort_keys=True))


if __name__ == '__main__':
    main()
