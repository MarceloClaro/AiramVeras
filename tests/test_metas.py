"""T20–T25: não fundir metas, promover corte empírico ou excluir grande lacuna."""
import pytest
from test_metricas import api


def test_T20_meta_A_usa_avaliados_e_categoria_original():
    result = api('metas', 'meta_adequados')(24, 10, .8)
    assert result['alvo'] == 20 and result['conversoes'] == 10
    assert result['acertos_ate_adequacao'] is None


def test_T21_corte_observado_permanece_hipotese():
    result = api('metas', 'corte_empirico')([dict(categoria='Adequado', acertos=14),
        dict(categoria='Intermediário', acertos=18), dict(categoria='Adequado', acertos=16)])
    assert result == dict(valor=14, status='hipotese_empirica_nao_oficial', acertos_ate_adequacao=None)


def test_T22_meta_B_individual_22_itens_exige_18():
    result = api('metas', 'meta_acertos')(17, 22, .8)
    assert (result['alvo'], result['lacuna'], result['atingida']) == (18, 1, False)


def test_T23_limite_exato_sem_erro_binario():
    assert api('metas', 'meta_acertos')(4, 5, .8)['atingida'] is True
    assert api('metas', 'meta_adequados')(35, 28, .8)['conversoes'] == 0


def test_T23_zero_itens_recusado_ausencia_indisponivel():
    with pytest.raises(ValueError):
        api('metas', 'meta_acertos')(0, 0, .8)
    assert api('metas', 'meta_acertos')(None, None, .8)['atingida'] is None
    assert api('metas', 'meta_adequados')(0, 0, .8)['atingida'] is None


@pytest.mark.parametrize('args', [(24,25,.8), (-1,0,.8), (24,1,1.1), (True,0,.8)])
def test_meta_A_recusa_limites_invalidos(args):
    with pytest.raises(ValueError):
        api('metas', 'meta_adequados')(*args)


@pytest.mark.parametrize('args', [(23,22,.8), (-1,22,.8), (1,22,-.1), (None,22,.8)])
def test_meta_B_recusa_limites_invalidos(args):
    with pytest.raises(ValueError):
        api('metas', 'meta_acertos')(*args)


def test_T24_T25_lacunas_independem_ordem_empates_nao_excluem_apoio():
    values = [(17,22), (0,22), (17,22), (22,22)]
    function = api('metas', 'meta_acertos')
    forward = [function(n,d,.8)['lacuna'] for n,d in values]
    backward = [function(n,d,.8)['lacuna'] for n,d in reversed(values)]
    assert forward == list(reversed(backward)) == [1,18,1,0]
