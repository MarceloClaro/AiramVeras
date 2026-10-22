"""Casos sintéticos: nomes locais fictícios nunca são emitidos em recibos."""
import csv
import hashlib
import importlib
import importlib.util
import io
import json
from pathlib import Path
import zipfile

import pytest


def api(module, name):
    spec = importlib.util.find_spec('airam.' + module)
    assert spec is not None, 'Funcionalidade de ingestao ausente'
    function = getattr(importlib.import_module('airam.' + module), name, None)
    assert callable(function), 'Funcionalidade solicitada ausente'
    return function


def fonte(tmp_path, monkeypatch, component='LEITURA', rows=None, year=1, sem_coluna=None):
    """Exportação completa sintética com BOM, manifesto e hashes reais."""
    root = tmp_path / 'fontes'
    root.mkdir(exist_ok=True)
    export = root / 'coleta'
    export.mkdir(exist_ok=True)
    target = export / 'csv_originais' / f'{year}_{component}'
    target.mkdir(parents=True, exist_ok=True)
    if rows is None:
        rows = [{'Turma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Avaliado': 'Sim',
                 'Nível de aprendizagem': 'Aprendizado adequado', 'H 01': ' 3 / 4', 'H 02': '0/2'}]
    aspects = {2: [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1)],
               3: [(1, 1), (2, 1), (3, 1), (3, 2), (4, 1), (4, 2), (4, 3), (4, 4)],
               4: [(1, 1), (1, 2), (1, 3), (1, 4)],
               5: [(1, 1), (1, 2), (1, 3), (1, 4)]}
    if component == 'ESCRITA':
        categories = ['Inadequado', 'Muito baixo', 'Baixo', 'Médio', 'Alto'] if year < 4 else [
            'Inadequado', 'Insuficiente', 'Insatisfatório', 'Intermediário', 'Satisfatório', 'Avançado']
        defaults = {'Turmma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Participação': 'Sim',
                    'Nota': '7.5', 'Categoria de escrita': categories[-1],
                    **{f'Questão {q} - Aspecto {a}': '0' for q, a in aspects[year]}}
        rows = [{**defaults, **r} for r in rows]
        escola = {'Escola': 'ESCOLA SINTETICA', 'Previstos': str(len(rows)),
                  'Avaliados': str(sum(r['Participação'] == 'Sim' for r in rows)),
                  '% Participação': '100%', 'Nota média': '7.5',
                  **{c: '0%' for c in categories},
                  **{f'Questão {q} - Aspecto {a}': '0' for q, a in aspects[year]}}
    elif component == 'FLUENCIA':
        defaults = {'Turmma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Participação': 'Sim',
                    'Perfil de leitor': 'Leitor Fluente', 'Palavras (leitura global)': '1 de 60',
                    'Palavras possivelmente desconhecidas': '1 de 40',
                    'Texto (Palavras corretas)': '-', 'Texto (Compreensão)': '1/3'}
        rows = [{**defaults, **r} for r in rows]
        escola = {'Escola': 'ESCOLA SINTETICA', 'Previstos': str(len(rows)),
                  'Avaliados': str(sum(r['Participação'] == 'Sim' for r in rows)),
                  '% Participação': '100', 'Pré-leitor (Total)': '0',
                  **{f'Pré-leitor (Nível {i})': '0' for i in range(1, 5)},
                  'Leitor Iniciante': '0', 'Leitor Fluente': str(len(rows))}
    else:
        count = {'LEITURA': {1: 9, 2: 11, 3: 11, 4: 13, 5: 16},
                 'MATEMATICA': {1: 7, 2: 11, 3: 12, 4: 15, 5: 19}}[component][year]
        component_internal = 'LÍNGUA PORTUGUESA' if component == 'LEITURA' else 'MATEMÁTICA'
        defaults = {'Rede': 'MUNICIPAL', 'Ano Escolar': f'ENSINO FUNDAMENTAL DE 9 ANOS - {year}º ANO',
                    'Componente Curricular': component_internal, 'Estado': 'CE', 'Município': 'SINTETICO',
                    'Código da Turma': '123', 'Turma': 'T1', 'Estudante': 'PESSOA SINTETICA',
                    'Avaliado': 'Sim', 'Nível de aprendizagem': 'Aprendizado adequado',
                    **{f'H {i:02}': '0/1' for i in range(1, count + 1)}}
        rows = [{**defaults, **r} for r in rows]
        escola = {'Escola': 'ESCOLA SINTETICA', 'Avaliados (%)': '100',
                  'Defasagem': '0', 'Aprendizado intermediário': '0', 'Aprendizado adequado': '100',
                  **{f'H {i:02} (%)': '75' for i in range(1, count + 1)},
                  **{k: defaults[k] for k in ['Rede', 'Ano Escolar', 'Componente Curricular', 'Estado', 'Município']},
                  'Regional': 'SINTETICA'}
    for row in rows:
        if row.get('Avaliado', row.get('Participação')) == 'Não':
            for field in list(row):
                if field.startswith(('H ', 'Questão')) or field in {'Nota', 'Nível de aprendizagem',
                    'Categoria de escrita', 'Perfil de leitor', 'Palavras (leitura global)',
                    'Palavras possivelmente desconhecidas', 'Texto (Palavras corretas)', 'Texto (Compreensão)'}:
                    row[field] = '-'
    turmas = []
    for turma in dict.fromkeys(r.get('Turma', r.get('Turmma')) for r in rows):
        row = {k: v for k, v in escola.items() if k not in {'Escola', 'Regional'}}
        row['Turma'] = turma
        if component in {'LEITURA', 'MATEMATICA'}:
            row.update({'Código da Escola': '123', 'Código da Turma': '123'})
        else:
            row['Código do estado' if component == 'ESCRITA' else 'Código da escola'] = '123'
            group = [r for r in rows if r.get('Turma', r.get('Turmma')) == turma]
            row['Previstos'] = str(len(group))
            row['Avaliados'] = str(sum(r['Participação'] == 'Sim' for r in group))
        turmas.append(row)
    tables = {'ESTUDANTE': rows, 'ESCOLA': [escola], 'TURMA': turmas}
    if sem_coluna:
        role, field = sem_coluna
        for row in tables[role]:
            assert field in row
            del row[field]
    archive = export / f'{year}_{component}.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        for role, data in tables.items():
            stream = io.StringIO(newline='')
            writer = csv.DictWriter(stream, fieldnames=list(data[0]), delimiter=';')
            writer.writeheader()
            writer.writerows(data)
            raw = stream.getvalue().encode('utf-8-sig')
            path = target / f'{role}.csv'
            path.write_bytes(raw)
            z.writestr(path.name, raw)
    manifest_path = export / 'manifesto_coleta.json'
    entries = json.loads(manifest_path.read_text())['exportacoes'] if manifest_path.exists() else []
    entries.append({'arquivo': archive.name, 'sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
                    'ano_escolar': year, 'componente': component, 'status': 'baixado'})
    manifest_path.write_text(json.dumps({'programa': 'CNCA', 'codigo_escola': '123',
        'ciclo': 'I', 'ano_avaliacao': 2026, 'avaliacao_id': 'AV12026',
        'data_coleta': '2026-10-22', 'exportacoes': entries}), encoding='utf-8')
    config = tmp_path / 'config.json'
    config.write_text(json.dumps({'raiz_fontes': str(root), 'fontes': {
        'coleta_ciclo_i_2026': {'caminho': 'coleta/manifesto_coleta.json'}}}), encoding='utf-8')
    monkeypatch.setenv('AIRAM_CONFIG', str(config))
    from airam.catalogo import catalogar
    return catalogar(root), target


def test_t09_h_contagens_bom_e_origem_manifesto(tmp_path, monkeypatch):
    # Retirar o BOM, perder as oportunidades ou inferir data de aplicação quebra o contrato.
    catalogo, _ = fonte(tmp_path, monkeypatch)
    result = api('ingestao', 'ler_exportacoes')(catalogo)
    assert len(result['matriculas']) == 1
    assert len(result['avaliacoes']) == 1
    assert len(result['habilidades']) == 9
    h = result['habilidades'][0]
    assert (h['bruto'], h['numerador'], h['denominador'], h['unidade']) == (' 3 / 4', 3, 4, 'acertos_itens')
    av = result['avaliacoes'][0]
    assert (av['acertos'], av['oportunidades']) == (3, 13)
    assert av['data_aplicacao'] is None
    assert av['data_exportacao'] == '2026-10-22'
    assert av['origem_metadados']['ano_escolar'] == 'csv_e_manifesto_conferidos'
    assert h['linha_fonte'] == 2 and h['sha256'] and h['fonte_id']


def test_copias_catalogo_nao_multiplicam_observacoes(tmp_path, monkeypatch):
    # Aceitar cópias verificadas por hash em outro local duplicaria os estudantes.
    catalogo, target = fonte(tmp_path, monkeypatch)
    copied = tmp_path / 'fontes' / 'historico'
    copied.mkdir()
    for path in target.glob('*.csv'):
        (copied / path.name).write_bytes(path.read_bytes())
    from airam.catalogo import catalogar
    result = api('ingestao', 'ler_exportacoes')(catalogar(tmp_path / 'fontes'))
    assert len(result['avaliacoes']) == 1


def test_revalida_hash_antes_de_ler(tmp_path, monkeypatch):
    catalogo, target = fonte(tmp_path, monkeypatch)
    path = target / 'ESTUDANTE.csv'
    path.write_bytes(path.read_bytes() + b'x')
    with pytest.raises(ValueError, match='hash'):
        api('ingestao', 'ler_exportacoes')(catalogo)


def test_duplicata_intracomponente_rejeitada(tmp_path, monkeypatch):
    row = {'Turma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Avaliado': 'Sim', 'H 01': '1/1'}
    catalogo, _ = fonte(tmp_path, monkeypatch, rows=[row, dict(row)])
    with pytest.raises(ValueError, match='uplic'):
        api('ingestao', 'ler_exportacoes')(catalogo)


def test_matricula_compartilhada_e_homonimo_em_outra_turma(tmp_path, monkeypatch):
    row = {'Turma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Avaliado': 'Sim', 'H 01': '1/1'}
    fonte(tmp_path, monkeypatch, rows=[row, {**row, 'Turma': 'T2'}])
    catalogo, _ = fonte(tmp_path, monkeypatch, component='MATEMATICA', rows=[row, {**row, 'Turma': 'T2'}])
    result = api('ingestao', 'ler_exportacoes')(catalogo)
    assert len(result['matriculas']) == 2
    assert len(result['avaliacoes']) == 4
    assert sorted(len(m['origens']) for m in result['matriculas']) == [2, 2]


@pytest.mark.parametrize('raw', ['3/2', '-1/2', '0/0', '1.5/2', '1/?'])
def test_t07_rejeita_contagens_impossiveis(raw):
    # Qualquer coerção de número impossível para valor utilizável é defeito.
    with pytest.raises(ValueError):
        api('esquemas', 'medida')(raw, 'acertos_itens', True)


def test_t08_reconciliacao_rejeita_total_divergente():
    rows = [{'avaliacao_local_id': 'A', 'campo_original': 'H 01', 'numerador': 1,
             'denominador': 2, 'participacao': True, 'disponibilidade': True,
             'total_acertos': 2, 'total_oportunidades': 2}]
    with pytest.raises(ValueError, match='reconcil'):
        api('ingestao', 'reconciliar_blocos')(rows)


def test_reconciliacao_soma_blocos_e_nao_media_taxas():
    rows = [{'avaliacao_local_id': 'A', 'campo_original': 'H 01', 'numerador': 1,
             'denominador': 1, 'participacao': True, 'disponibilidade': True},
            {'avaliacao_local_id': 'A', 'campo_original': 'H 02', 'numerador': 0,
             'denominador': 3, 'participacao': True, 'disponibilidade': True}]
    total = api('ingestao', 'reconciliar_blocos')(rows)[0]
    assert (total['acertos'], total['oportunidades'], total['taxa']) == (1, 4, .25)


@pytest.mark.parametrize('change', [{'Ano Escolar': '2º ANO'}, {'Componente Curricular': 'MATEMÁTICA'}])
def test_metadados_internos_contraditorios_rejeitados(tmp_path, monkeypatch, change):
    row = {'Turma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Avaliado': 'Sim', 'H 01': '1/1', **change}
    catalogo, _ = fonte(tmp_path, monkeypatch, rows=[row])
    with pytest.raises(ValueError, match='componente|ano|incompativel'):
        api('ingestao', 'ler_exportacoes')(catalogo)


def test_largura_csv_invalida_rejeitada(tmp_path, monkeypatch):
    catalogo, target = fonte(tmp_path, monkeypatch)
    path = target / 'ESTUDANTE.csv'
    path.write_bytes(path.read_bytes().rstrip() + b';EXTRA\r\n')
    record = next(c for c in catalogo if c['caminho'].endswith('ESTUDANTE.csv'))
    record['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError):
        api('ingestao', 'ler_exportacoes')(catalogo)


def test_ano_do_csv_com_ordinal_nao_confunde_duracao_etapa(tmp_path, monkeypatch):
    # NFKD converte º em o; a etapa de nove anos não substitui o ano escolar.
    row = {'Turma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Avaliado': 'Sim',
           'Ano Escolar': 'ENSINO FUNDAMENTAL DE 9 ANOS - 1º ANO', 'H 01': '1/1'}
    catalogo, _ = fonte(tmp_path, monkeypatch, rows=[row])
    result = api('ingestao', 'ler_exportacoes')(catalogo)
    assert result['avaliacoes'][0]['ano_escolar'] == 1
    assert result['avaliacoes'][0]['origem_metadados']['ano_escolar'] == 'csv_e_manifesto_conferidos'


def test_turma_agregada_usa_mesma_normalizacao_da_matricula(tmp_path, monkeypatch):
    row = {'Turma': '1º ANO A', 'Estudante': 'PESSOA SINTETICA', 'Avaliado': 'Sim', 'H 01': '1/1'}
    catalogo, _ = fonte(tmp_path, monkeypatch, rows=[row])
    result = api('ingestao', 'ler_exportacoes')(catalogo)
    aggregate = next(r for r in result['agregados'] if r['nivel'] == 'turma')
    assert aggregate['avaliados_observados'] == 1


@pytest.mark.parametrize('component,year,role,field', [
    ('LEITURA', 1, 'ESTUDANTE', 'Nível de aprendizagem'),
    ('LEITURA', 1, 'ESTUDANTE', 'H 09'),
    ('LEITURA', 2, 'ESTUDANTE', 'H 11'),
    ('LEITURA', 3, 'ESTUDANTE', 'H 11'),
    ('LEITURA', 4, 'ESTUDANTE', 'H 13'),
    ('LEITURA', 5, 'ESTUDANTE', 'H 16'),
    ('MATEMATICA', 1, 'ESTUDANTE', 'H 07'),
    ('MATEMATICA', 2, 'ESTUDANTE', 'H 11'),
    ('MATEMATICA', 3, 'ESTUDANTE', 'H 12'),
    ('MATEMATICA', 4, 'ESTUDANTE', 'H 15'),
    ('MATEMATICA', 5, 'ESTUDANTE', 'H 19'),
    ('LEITURA', 1, 'ESCOLA', 'Aprendizado adequado'),
    ('LEITURA', 1, 'ESCOLA', 'H 09 (%)'),
    ('MATEMATICA', 5, 'TURMA', 'H 19 (%)'),
    ('ESCRITA', 2, 'ESTUDANTE', 'Categoria de escrita'),
    ('ESCRITA', 2, 'ESTUDANTE', 'Nota'),
    ('ESCRITA', 2, 'ESTUDANTE', 'Questão 3 - Aspecto 1'),
    ('ESCRITA', 3, 'ESTUDANTE', 'Questão 4 - Aspecto 4'),
    ('ESCRITA', 4, 'ESTUDANTE', 'Questão 1 - Aspecto 4'),
    ('ESCRITA', 5, 'ESTUDANTE', 'Questão 1 - Aspecto 4'),
    ('ESCRITA', 2, 'ESCOLA', 'Nota média'),
    ('ESCRITA', 3, 'TURMA', 'Questão 4 - Aspecto 4'),
    ('ESCRITA', 4, 'ESCOLA', 'Avançado'),
    ('FLUENCIA', 2, 'ESTUDANTE', 'Perfil de leitor'),
    ('FLUENCIA', 3, 'ESTUDANTE', 'Texto (Compreensão)'),
    ('FLUENCIA', 4, 'ESTUDANTE', 'Palavras (leitura global)'),
    ('FLUENCIA', 5, 'ESTUDANTE', 'Texto (Palavras corretas)'),
    ('FLUENCIA', 2, 'ESCOLA', 'Previstos'),
    ('FLUENCIA', 3, 'TURMA', 'Pré-leitor (Nível 4)'),
    ('FLUENCIA', 4, 'ESCOLA', 'Leitor Fluente'),
])
def test_fix1_coluna_obrigatoria_ausente_rejeitada(tmp_path, monkeypatch, component, year, role, field):
    # Perder uma coluna estrutural não pode virar valor nulo nem cobertura completa.
    if component in {'ESCRITA', 'FLUENCIA'}:
        rows = [{'Turmma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Participação': 'Sim'}]
    else:
        rows = None
    catalogo, _ = fonte(tmp_path, monkeypatch, component=component, year=year,
                        rows=rows, sem_coluna=(role, field))
    with pytest.raises(ValueError, match='[Cc]oluna|[Ee]squema'):
        api('ingestao', 'ler_exportacoes')(catalogo)


@pytest.mark.parametrize('component,year', [(c, y) for c in ['LEITURA', 'MATEMATICA', 'ESCRITA', 'FLUENCIA']
                                         for y in range(1 if c in {'LEITURA', 'MATEMATICA'} else 2, 6)])
def test_fix1_esquema_completo_continua_legivel(tmp_path, monkeypatch, component, year):
    rows = None if component in {'LEITURA', 'MATEMATICA'} else [
        {'Turmma': 'T1', 'Estudante': 'PESSOA SINTETICA', 'Participação': 'Sim'}]
    catalogo, _ = fonte(tmp_path, monkeypatch, component=component, year=year, rows=rows)
    assert len(api('ingestao', 'ler_exportacoes')(catalogo)['avaliacoes']) == 1
