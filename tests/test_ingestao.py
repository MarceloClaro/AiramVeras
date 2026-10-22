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


def fonte(tmp_path, monkeypatch, component='LEITURA', rows=None, year=1):
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
    if component == 'ESCRITA':
        escola = {'Escola': 'ESCOLA SINTETICA', 'Previstos': str(len(rows)),
                  'Avaliados': str(sum(r['Participação'] == 'Sim' for r in rows)),
                  '% Participação': '100%', 'Nota média': '7.5', 'Alto': '100%'}
    elif component == 'FLUENCIA':
        escola = {'Escola': 'ESCOLA SINTETICA', 'Previstos': str(len(rows)),
                  'Avaliados': str(sum(r['Participação'] == 'Sim' for r in rows)),
                  '% Participação': '100', 'Pré-leitor (Total)': '0',
                  **{f'Pré-leitor (Nível {i})': '0' for i in range(1, 5)},
                  'Leitor Iniciante': '0', 'Leitor Fluente': str(len(rows))}
    else:
        escola = {'Escola': 'ESCOLA SINTETICA', 'Avaliados (%)': '100',
                  'Aprendizado adequado': '100', 'H 01 (%)': '75'}
        component_internal = 'LÍNGUA PORTUGUESA' if component == 'LEITURA' else 'MATEMÁTICA'
        rows = [{'Componente Curricular': component_internal, **r} for r in rows]
        escola['Componente Curricular'] = component_internal
    tables = {'ESTUDANTE': rows, 'ESCOLA': [escola],
              'TURMA': [{**{k: v for k, v in escola.items() if k != 'Escola'},
                         'Turma': rows[0].get('Turma', rows[0].get('Turmma'))}]}
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
    assert len(result['habilidades']) == 2
    h = result['habilidades'][0]
    assert (h['bruto'], h['numerador'], h['denominador'], h['unidade']) == (' 3 / 4', 3, 4, 'acertos_itens')
    av = result['avaliacoes'][0]
    assert (av['acertos'], av['oportunidades']) == (3, 6)
    assert av['data_aplicacao'] is None
    assert av['data_exportacao'] == '2026-10-22'
    assert av['origem_metadados']['ano_escolar'] == 'manifesto'
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
