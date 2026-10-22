"""Execução/contraprova local T03; imprime só metadados, contagens e hashes."""
from collections import Counter
from copy import deepcopy
import csv
from datetime import datetime
import hashlib
import importlib.metadata
from itertools import combinations
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from airam.identidade import carregar_ou_criar_segredo, pseudonimizar_tabelas
from airam.pareamento import parear_componentes, auditar_pareamento


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2,
                               allow_nan=False) + '\n', encoding='utf-8')


def check(condition, label):
    if not condition:
        raise ValueError(label)


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else 'real'
    check(label.isalnum(), 'Rotulo invalido')
    directory = ROOT / 'evidencias/T03'
    source = ROOT / 'restrito/t02/tabelas.json'
    expected_hash = '82a24045cb75d85eeefd4394a73cb0dcec37dbbd8a542350fb04d7da0653d9f5'
    check(digest(source) == expected_hash, 'Checkpoint T02 alterado')
    original = json.loads(source.read_text(encoding='utf-8'))
    catalog_path = ROOT / 'catalogo/fontes.json'
    catalog = json.loads(catalog_path.read_text(encoding='utf-8'))
    config = json.loads((ROOT / 'config/analise.json').read_text(encoding='utf-8-sig'))
    source_root = (ROOT / config['raiz_fontes']).resolve()
    source_paths = {r['caminho']: source_root / r['caminho'] for r in original['avaliacoes']}
    hashes_data = {'restrito/t02/tabelas.json': digest(source), 'catalogo/fontes.json': digest(catalog_path)}
    hashes_data.update({relative: digest(path) for relative, path in source_paths.items()})
    hashes_code = {p.relative_to(ROOT).as_posix(): digest(p)
                   for folder in ['airam', 'tests', 'evidencias/T03']
                   for p in (ROOT / folder).glob('*.py')}
    hashes_code.update({name: digest(ROOT / name) for name in
                        ['requirements.lock.txt', 'pyproject.toml', 'config/analise.json']})
    before = dict(timestamp=datetime.now().astimezone().isoformat(), hashes_codigo=hashes_code,
                  hashes_dados=hashes_data,
                  versoes=dict(python=platform.python_version(), pytest=importlib.metadata.version('pytest')),
                  head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                  executor='Codex', comando=f'.venv/Scripts/python.exe evidencias/T03/auditar_checkpoint.py {label}')
    write(directory / f'checkpoint-{label}-antes.json', before)
    # Segredo persistente fora do repositório; seu conteúdo e seu hash não entram no recibo.
    secret_path = Path.home() / '.airam-local/secrets/spec001-hmac.key'
    key_existed = secret_path.exists()
    secret = carregar_ou_criar_segredo(secret_path)
    tables, mapping = pseudonimizar_tabelas(original, secret)
    lookup = {r['matricula_local_id']: r['aluno_local_id'] for r in mapping}
    check(len(mapping) == len(lookup) == len(set(lookup.values())) == 172, 'Mapa nao bijetivo')
    check(Counter(r['matricula_local_id'] for r in mapping) ==
          Counter(r['matricula_local_id'] for r in original['matriculas']), 'Mapa incompleto')
    # Referência independente do pareador, construída diretamente do T02 imutável.
    reference = []
    for table in ['avaliacoes', 'habilidades', 'escrita', 'fluencia']:
        check(len(tables[table]) == len(original[table]), 'Cobertura divergente')
        for old, new in zip(original[table], tables[table]):
            expected = deepcopy(old)
            expected['aluno_local_id'] = lookup[expected.pop('matricula_local_id')]
            expected['qualidade_vinculo'] = 'local_provisorio_sem_id_institucional'
            check(new == expected, 'Valores ou proveniencia alterados na transformacao')
            if table == 'avaliacoes':
                reference.append(expected)
    for table in ['agregados', 'disponibilidade_arquivos']:
        check(tables[table] == original[table], 'Agregado ou disponibilidade alterado')
    # Confronto independente dos brutos com cada CSV original autenticado por hash.
    raw = {}
    for relative, path in source_paths.items():
        with path.open(encoding='utf-8-sig', newline='') as stream:
            for line, row in enumerate(csv.DictReader(stream, delimiter=';'), 2):
                raw[(relative, line)] = row
    for row in original['avaliacoes']:
        check(hashes_data[row['caminho']] == row['sha256'], 'Hash de fonte divergente')
        raw_row = raw[(row['caminho'], row['linha_fonte'])]
        check(raw_row[row['campo_categoria_original']] == row['categoria_bruto'], 'Categoria nao coincide com fonte')
        participation = raw_row.get('Avaliado', raw_row.get('Participação'))
        check(participation == row['participacao_bruto'], 'Participacao nao coincide com fonte')
    for table in ['habilidades', 'escrita', 'fluencia']:
        for row in original[table]:
            check(raw[(row['caminho'], row['linha_fonte'])][row['campo_original']] == row['bruto'],
                  'Medida bruta nao coincide com fonte')
    outputs, coverage = {}, {}
    for left, right in combinations(sorted({r['componente'] for r in tables['avaliacoes']}), 2):
        pairs, unmatched = parear_componentes(tables['avaliacoes'], left, right)
        stats = auditar_pareamento(reference, pairs, unmatched, left, right)
        # Ataque T38 na base real: altera valor sem alterar IDs, sem imprimir registros.
        altered = deepcopy(pairs)
        if altered:
            altered[0]['esquerda']['categoria_bruto'] = 'ADULTERACAO_SINTETICA'
            try:
                auditar_pareamento(reference, altered, unmatched, left, right)
            except ValueError:
                stats['adulteracao_detectada'] = True
            else:
                raise ValueError('Contraprova nao detectou adulteracao')
        stats['pares_taxas_disponiveis'] = sum(p['esquerda']['participacao'] is True
            and p['direita']['participacao'] is True and p['esquerda'].get('taxa') is not None
            and p['direita'].get('taxa') is not None for p in pairs)
        stats['motivos_nao_pareados'] = dict(Counter(r['motivo'] for r in unmatched))
        query = left + '--' + right
        coverage[query] = stats
        outputs[query] = dict(pares=pairs, nao_pareados=unmatched)
    checkpoint = ROOT / 'restrito/t03/tabelas.json'
    map_path = ROOT / 'restrito/t03/mapa-nominal.json'
    pairs_path = ROOT / 'restrito/t03/pareamentos.json'
    write(checkpoint, tables)
    write(map_path, mapping)
    write(pairs_path, outputs)
    schemas = {table: {field: sorted({type(r.get(field)).__name__ for r in rows})
                      for field in sorted({k for r in rows for k in r})}
               for table, rows in tables.items()}
    write(ROOT / 'docs/esquemas-t03.json', schemas)
    # Sigilo: varredura literal de todos os nomes completos reais nas saídas públicas.
    names = {r[k] for r in original['matriculas'] for k in ['nome_bruto', 'nome_normalizado']}
    public_paths = [p for folder in ['airam', 'tests', 'docs', 'evidencias/T03']
                    for p in (ROOT / folder).rglob('*') if p.suffix in {'.py', '.json', '.log', '.md'}]
    leaks = sum(any(name and name in p.read_text(encoding='utf-8-sig') for name in names) for p in public_paths)
    check(leaks == 0, 'Conteudo nominal encontrado em arquivo publico')
    check(digest(source) == expected_hash, 'Checkpoint T02 modificado')
    check(all(digest(path) == hashes_data[relative] for relative, path in source_paths.items()), 'Fonte alterada')
    summary = dict(timestamp_final=datetime.now().astimezone().isoformat(), executor='Codex',
                   estado='SUCESSO', codigo_saida=0, contagens={k: len(v) for k, v in tables.items()},
                   cobertura=coverage, conflitos=0, exposicoes_nominais_literais=leaks,
                   grupos_homonimos_multiturma=sum(len({r['turma'] for r in original['matriculas']
                       if r['nome_normalizado'] == name}) > 1 for name in
                       {r['nome_normalizado'] for r in original['matriculas']}),
                   segredo_preexistente=key_existed, segredo_persistente_fora_git=True,
                   checkpoint_sha256=digest(checkpoint), mapa_restrito_sha256=digest(map_path),
                   pareamentos_restritos_sha256=digest(pairs_path), esquema_sha256=digest(ROOT / 'docs/esquemas-t03.json'),
                   referencia_execucao_previa=f'checkpoint-{label}-antes.json',
                   limites=['Ligacao local provisoria sem identidade institucional ou longitudinal validada.',
                       'Pares cadastrais preservam nao participantes; N analitico requer filtro explicito.',
                       'Datas de aplicacao ausentes; rotulos historicos nao comprovam temporalidade.',
                       'Validacao documental local Codex; nenhuma inferencia Core ou validacao pedagogica externa.'])
    write(directory / f'checkpoint-{label}.json', summary)
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    raise SystemExit(main())
