"""T04-T06: pessoas exclusivamente sintéticas; não lê fontes nominais."""
from copy import deepcopy
import importlib
import importlib.util
import json

import pytest


def api(name):
    assert importlib.util.find_spec('airam.identidade') is not None, 'Funcionalidade identidade ausente'
    return getattr(importlib.import_module('airam.identidade'), name)


def cadastro(ref='antiga-1', turma='5 A', nome='Pessoa Sintética'):
    return dict(matricula_local_id=ref, escola_codigo='ESC-SINTETICA', ano_escolar=5,
                turma=turma, nome_bruto=nome, nome_normalizado=nome.upper(),
                qualidade_vinculo='local_provisorio_sem_id_institucional',
                origens=[dict(fonte_id='fonte-sintetica', sha256='a' * 64, linha_fonte=2,
                              nome_bruto=nome, nome_normalizado=nome.upper(),
                              turma_bruto=turma, componente='leitura')])


def test_t05_homonimos_turmas_distintas_e_t06_qualidade_e_origens():
    rows = [cadastro(), cadastro('antiga-2', '5 B')]
    original = deepcopy(rows)
    public, private = api('vincular_localmente')(rows, b'x' * 32)
    assert len({r['aluno_local_id'] for r in public}) == 2
    assert all(r['qualidade_vinculo'] == 'local_provisorio_sem_id_institucional' for r in public)
    assert public[0]['origens'][0]['fonte_id'] == 'fonte-sintetica'
    assert public[0]['origens'][0]['linha_fonte'] == 2
    assert 'nome' not in json.dumps(public).lower()
    assert 'matricula_local_id' not in json.dumps(public)
    assert len(private) == 2 and private[0]['matricula_local_id'] == 'antiga-1'
    assert private[0]['aluno_local_id'] == public[0]['aluno_local_id']
    assert private[0]['nome_bruto'] == 'Pessoa Sintética'
    assert rows == original


@pytest.mark.parametrize('rows', [
    [cadastro(), cadastro('antiga-2', ' 5 a ', 'PESSOA sintetica')],
    [cadastro(), cadastro('antiga-1', '5 B', 'Outra Pessoa')],
])
def test_t04_duplicata_normalizada_ou_referencia_repetida_bloqueia(rows):
    with pytest.raises(ValueError, match='Duplicata'):
        api('vincular_localmente')(rows, b'x' * 32)


def test_hmac_estavel_normalizacao_e_dependencia_do_segredo():
    f = api('vincular_localmente')
    first = f([cadastro()], b'x' * 32)[0][0]['aluno_local_id']
    equivalent = f([cadastro('outra-ref', ' 5 a ', 'PESSOA sintetica')], b'x' * 32)[0][0]['aluno_local_id']
    assert first == equivalent
    assert first != f([cadastro()], b'y' * 32)[0][0]['aluno_local_id']
    assert len(first) == 64


@pytest.mark.parametrize('change', [{'nome_bruto': ''}, {'escola_codigo': ''}, {'ano_escolar': None},
                                   {'turma': ''}, {'matricula_local_id': ''}])
def test_chave_incompleta_bloqueia(change):
    row = cadastro()
    row.update(change)
    with pytest.raises(ValueError):
        api('vincular_localmente')([row], b'x' * 32)


def test_segredo_persistente_nao_e_regenerado_se_invalido(tmp_path):
    f = api('carregar_ou_criar_segredo')
    path = tmp_path / 'segredo' / 'chave.key'
    secret = f(path)
    assert len(secret) == 32 and f(path) == secret
    path.write_bytes(b'invalido')
    with pytest.raises(ValueError):
        f(path)
    assert path.read_bytes() == b'invalido'


def test_t06_substitui_relacoes_sem_perder_medidas_e_bloqueia_orfaos():
    f = api('pseudonimizar_tabelas')
    row = dict(matricula_local_id='antiga-1', avaliacao_local_id='aplicacao-sintetica',
               bruto='0/2', numerador=0, denominador=2, fonte_id='fonte-sintetica')
    tables = dict(matriculas=[cadastro()], avaliacoes=[dict(row)], habilidades=[dict(row)],
                  escrita=[], fluencia=[], agregados=[], disponibilidade_arquivos=[])
    original = deepcopy(tables)
    result, mapping = f(tables, b'x' * 32)
    assert result['habilidades'][0]['numerador'] == 0
    assert result['habilidades'][0]['denominador'] == 2
    assert result['habilidades'][0]['bruto'] == '0/2'
    assert result['habilidades'][0]['fonte_id'] == 'fonte-sintetica'
    assert result['habilidades'][0]['aluno_local_id'] == mapping[0]['aluno_local_id']
    assert 'matricula_local_id' not in json.dumps(result)
    assert 'nome' not in json.dumps(result).lower()
    assert tables == original
    tables['habilidades'][0]['matricula_local_id'] = 'orfao'
    with pytest.raises(ValueError, match='Vinculo'):
        f(tables, b'x' * 32)


def test_relacao_medida_aplicacao_divergente_bloqueia():
    tables = dict(matriculas=[cadastro(), cadastro('antiga-2', '5 B')],
                  avaliacoes=[dict(matricula_local_id='antiga-1', avaliacao_local_id='app')],
                  habilidades=[dict(matricula_local_id='antiga-2', avaliacao_local_id='app')],
                  escrita=[], fluencia=[], agregados=[], disponibilidade_arquivos=[])
    with pytest.raises(ValueError, match='Vinculo'):
        api('pseudonimizar_tabelas')(tables, b'x' * 32)


def test_nominais_aninhados_no_lado_pseudonimizado_bloqueiam():
    row = cadastro()
    row['origens'][0]['origem_metadados'] = {'extra': {'nome_bruto': 'Pessoa Sintética'}}
    with pytest.raises(ValueError, match='nominal'):
        api('vincular_localmente')([row], b'x' * 32)


def test_nominal_inesperado_em_avaliacao_bloqueia():
    tables = dict(matriculas=[cadastro()], avaliacoes=[dict(matricula_local_id='antiga-1',
                  avaliacao_local_id='app', extra={'Estudante': 'Pessoa Sintética'})],
                  habilidades=[], escrita=[], fluencia=[], agregados=[], disponibilidade_arquivos=[])
    with pytest.raises(ValueError, match='nominal'):
        api('pseudonimizar_tabelas')(tables, b'x' * 32)


@pytest.mark.parametrize('secret', [b'', b'curto', 'x' * 32])
def test_segredo_fraco_ou_tipo_incorreto_rejeitado(secret):
    with pytest.raises(ValueError, match='Segredo'):
        api('vincular_localmente')([cadastro()], secret)
