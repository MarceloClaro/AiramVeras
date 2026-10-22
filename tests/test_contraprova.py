"""T15: a segunda implementação detecta corrupção mesmo com mesmos totais/IDs."""
from copy import deepcopy
import pytest
from test_metricas import api, h


def test_T15_independente_quando_principal_falha(monkeypatch):
    main = api('metricas', 'agregar_habilidades')
    checker = api('contraprova', 'contraprovar')
    rows = [h(), h(position='H 02', n=0, d=3)]
    wanted = main(rows)
    def unavailable(*a, **k):
        raise RuntimeError('Principal indisponivel')
    import airam.metricas as module
    monkeypatch.setattr(module, 'agregar_habilidades', unavailable)
    monkeypatch.setattr(module, 'taxa_por_itens', unavailable)
    assert checker(rows)['resultados'] == wanted


def test_contraprova_confere_zero_ausencia_e_turma():
    rows = [h(n=0), h('sintetico-2', n=None, d=None, participacao=False,
        disponibilidade=False, bruto='-', turma='B')]
    assert api('contraprova', 'contraprovar')(rows)['resultados'] == api('metricas', 'agregar_habilidades')(rows)


@pytest.mark.parametrize('field,value', [('numerador', 0), ('sha256', 'b'*64), ('linha_fonte', 9), ('bruto', '01/1')])
def test_auditoria_detecta_adulteracao_de_valor_ou_proveniencia(field, value):
    rows = [h()]
    result = api('metricas', 'agregar_habilidades')(rows)
    changed = deepcopy(rows)
    changed[0][field] = value
    with pytest.raises(ValueError):
        api('contraprova', 'auditar_resultados')(changed, result)


def test_auditoria_compara_resultado_completo_nao_so_total():
    rows = [h()]
    result = api('metricas', 'agregar_habilidades')(rows)
    result[0]['taxa'] = .123
    with pytest.raises(ValueError):
        api('contraprova', 'auditar_resultados')(rows, result)


def test_contraprova_recusa_duplicacao():
    with pytest.raises(ValueError):
        api('contraprova', 'contraprovar')([h(), h()])


def test_contraprova_interface_dict_rastreia_observacoes():
    result = api('contraprova', 'contraprovar')([h()])
    assert isinstance(result, dict), 'Contraprova deve entregar dict rastreavel'
    assert result['observacoes_conferidas'] == 1
    assert len(result['resultados']) == 5
