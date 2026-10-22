"""T38: adulteração detectada comparando valores e proveniência à fonte sintética."""
from copy import deepcopy
import importlib
import importlib.util

import pytest


def api(name='parear_componentes'):
    assert importlib.util.find_spec('airam.pareamento') is not None, 'Funcionalidade pareamento ausente'
    return getattr(importlib.import_module('airam.pareamento'), name)


def observacao(component='leitura', student='sintetico-A', **changes):
    row = dict(aluno_local_id=student, avaliacao_local_id='app-' + component,
               avaliacao_id='AV-SINTETICA', ano_avaliacao=2026, ciclo='I', ano_escolar=5,
               componente=component, participacao=True, taxa=0.5, acertos=11,
               oportunidades=22, fonte_id='fonte-' + component, sha256='b' * 64,
               linha_fonte=2, qualidade_vinculo='local_provisorio_sem_id_institucional',
               data_aplicacao=None)
    row.update(changes)
    return row


def test_t38_pares_preservam_valores_proveniencia_e_ausencia_temporal():
    rows = [observacao(), observacao('matematica', acertos=0, taxa=0.0),
            observacao(student='sintetico-B')]
    original = deepcopy(rows)
    pairs, unmatched = api()(rows, 'leitura', 'matematica')
    assert len(pairs) == 1
    assert pairs[0]['esquerda'] == original[0]
    assert pairs[0]['direita'] == original[1]
    assert pairs[0]['direita']['acertos'] == 0
    assert pairs[0]['direita']['fonte_id'] == 'fonte-matematica'
    assert pairs[0]['direita']['data_aplicacao'] is None
    assert unmatched == [dict(lado='esquerda', motivo='componente_direito_ausente', registro=original[2])]
    pairs[0]['direita']['taxa'] = 99
    assert rows == original


@pytest.mark.parametrize('field,value', [('acertos', 99), ('taxa', 0.9),
                                      ('fonte_id', 'adulterada'), ('linha_fonte', 900)])
def test_t38_auditoria_rejeita_par_adulterado_mesmo_com_mesmos_ids(field, value):
    source = [observacao(), observacao('matematica')]
    pairs, unmatched = api()(source, 'leitura', 'matematica')
    assert api('auditar_pareamento')(source, pairs, unmatched, 'leitura', 'matematica')['pares'] == 1
    pairs[0]['direita'][field] = value
    with pytest.raises(ValueError, match='Adulteracao'):
        api('auditar_pareamento')(source, pairs, unmatched, 'leitura', 'matematica')


def test_duplicata_bloqueia_fanout_e_nao_faz_produto_cartesiano():
    rows = [observacao(), observacao(avaliacao_local_id='outra-app'), observacao('matematica')]
    with pytest.raises(ValueError, match='Duplicata'):
        api()(rows, 'leitura', 'matematica')


def test_contextos_distintos_nao_pareiam_e_terceiro_componente_fora_universo():
    rows = [observacao(), observacao('matematica', ciclo='II'), observacao('escrita')]
    pairs, unmatched = api()(rows, 'leitura', 'matematica')
    assert pairs == []
    assert sorted(r['motivo'] for r in unmatched) == [
        'componente_direito_ausente', 'componente_esquerdo_ausente']
    assert api('auditar_pareamento')(rows, pairs, unmatched, 'leitura', 'matematica')['nao_pareados'] == 2


def test_nao_participante_preserva_mascara_sem_criar_resultado():
    rows = [observacao(), observacao('matematica', participacao=False, taxa=None, acertos=None)]
    pairs, unmatched = api()(rows, 'leitura', 'matematica')
    assert not unmatched and len(pairs) == 1
    assert pairs[0]['direita']['participacao'] is False
    assert pairs[0]['direita']['acertos'] is None


def test_auditoria_rejeita_omissao_e_repeticao_de_pares():
    rows = [observacao(), observacao('matematica')]
    pairs, unmatched = api()(rows, 'leitura', 'matematica')
    for altered in [[], pairs + pairs]:
        with pytest.raises(ValueError):
            api('auditar_pareamento')(rows, altered, unmatched, 'leitura', 'matematica')


def test_auditoria_rejeita_par_unico_com_componentes_iguais():
    row = observacao()
    pairs = [dict(aluno_local_id=row['aluno_local_id'], esquerda=row, direita=row)]
    with pytest.raises(ValueError):
        api('auditar_pareamento')([row], pairs, [], 'leitura', 'leitura')


def test_contexto_ausente_bloqueia_sem_inventar_ciclo():
    with pytest.raises(ValueError, match='incompleto'):
        api()([observacao(ciclo=None)], 'leitura', 'matematica')


@pytest.mark.parametrize('field,value', [('qualidade_vinculo', 'institucional_validada'),
                                      ('nome_bruto', 'Pessoa Sintética')])
def test_auditoria_rejeita_metadados_adulterados_no_envelope(field, value):
    rows = [observacao(), observacao('matematica')]
    pairs, unmatched = api()(rows, 'leitura', 'matematica')
    pairs[0][field] = value
    with pytest.raises(ValueError, match='Adulteracao'):
        api('auditar_pareamento')(rows, pairs, unmatched, 'leitura', 'matematica')


def test_auditoria_recusa_consulta_com_componentes_iguais_mesmo_vazia():
    with pytest.raises(ValueError):
        api('auditar_pareamento')([], [], [], 'leitura', 'leitura')
