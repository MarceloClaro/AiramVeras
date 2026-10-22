"""T10/T11: trocar soma de itens por média, perder máscaras ou misturar contexto."""
from copy import deepcopy
from importlib import import_module, util
import pytest


def api(module, name):
    qualified = 'airam.' + module
    assert util.find_spec(qualified) is not None, 'Funcionalidade estatistica ausente'
    function = getattr(import_module(qualified), name, None)
    assert callable(function), 'Funcionalidade estatistica ausente'
    return function


def h(student='sintetico-1', position='H 01', n=1, d=1, **changes):
    row = dict(aluno_local_id=student, avaliacao_local_id=student + ':aplicacao',
        avaliacao_id='AV', ano_avaliacao=2026, ciclo='I', ano_escolar=1,
        componente='LEITURA', fonte_id='fixture', sha256='a'*64, exportacao='fixture',
        caminho='fixture.csv', linha_fonte=2 if student == 'sintetico-1' else 3,
        turma='A', posicao=position, participacao=True, disponibilidade=True,
        numerador=n, denominador=d, unidade='acertos_itens', bruto=f'{n}/{d}')
    row.update(changes)
    return row


def test_T10_razao_de_somas_nunca_media_simples():
    assert api('metricas', 'taxa_por_itens')([1, 0], [1, 3]) == .25


@pytest.mark.parametrize('n,d', [([1], []), ([-1], [1]), ([2], [1]), ([0], [0]), ([True], [1])])
def test_contagens_invalidas_nao_produzem_taxa(n, d):
    with pytest.raises(ValueError):
        api('metricas', 'taxa_por_itens')(n, d)


def test_vazio_e_ausencia_nao_viram_zero():
    assert api('metricas', 'taxa_por_itens')([], []) is None


def test_T11_reordenar_alunos_h_preserva_totais_e_proveniencia():
    rows = [h(), h(position='H 02', n=0, d=3), h('sintetico-2', n=0)]
    before = deepcopy(rows)
    aggregate = api('metricas', 'agregar_habilidades')
    output = aggregate(rows)
    assert output == aggregate(list(reversed(rows)))
    assert rows == before
    school = [x for x in output if x['nivel'] == 'escola' and x['posicao'] is None][0]
    assert (school['acertos'], school['oportunidades'], school['taxa_observada']) == (1, 5, .2)
    assert school['avaliados'] == 2


def test_ausencia_separada_de_zero_e_nao_participante():
    rows = [h(n=0), h('sintetico-2', n=None, d=None, participacao=False,
        disponibilidade=False, bruto='-')]
    output = api('metricas', 'agregar_habilidades')(rows)
    school = [x for x in output if x['nivel'] == 'escola' and x['posicao'] is None][0]
    assert (school['cadastros'], school['avaliados'], school['validas'], school['ausentes']) == (2, 1, 1, 1)
    assert school['taxa_observada'] == 0


@pytest.mark.parametrize('change', [dict(unidade='palavras'), dict(componente='FLUENCIA'),
    dict(numerador=2), dict(disponibilidade=False), dict(participacao=False)])
def test_nao_converte_ou_aceita_contagem_inconsistente(change):
    with pytest.raises(ValueError):
        api('metricas', 'agregar_habilidades')([h(**change)])


def test_duplicata_h_bloqueia_fanout():
    with pytest.raises(ValueError):
        api('metricas', 'agregar_habilidades')([h(), h()])


def test_contextos_e_fontes_nao_sao_fundidos():
    rows = [h(), h(ano_escolar=2), h(sha256='b'*64)]
    output = api('metricas', 'agregar_habilidades')(rows)
    assert len([x for x in output if x['nivel'] == 'escola' and x['posicao'] is None]) == 3


def test_cobertura_parcial_nao_vira_prova_completa():
    rows = [h(), h(position='H 02', n=None, d=None, disponibilidade=False, bruto='-')]
    row = [x for x in api('metricas', 'agregar_habilidades')(rows) if x['nivel'] == 'aluno'][0]
    assert row['taxa'] is None and row['taxa_observada'] == 1
