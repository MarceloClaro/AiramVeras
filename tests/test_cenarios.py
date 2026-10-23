"""T40/T41: catches causal labels, frozen adequate pupils and conflated goals."""
from copy import deepcopy
import pytest
from test_metricas import api


def project(rows, **hypotheses):
    return api('cenarios', 'projetar_cenario')(rows, {'A': .8, 'B': .8}, hypotheses)


def observation(x=17, category='Intermediário', component='LEITURA', **extra):
    return dict(componente=component, participacao=True, categoria=category,
                acertos=x, oportunidades=22, unidade='itens', **extra)


def test_T40_cenario_condicional_nao_promete_eficacia():
    result = project([observation()], ganho_acertos=1)
    assert result['tipo_resultado'] == 'cenario_condicional'
    assert result['status_validacao'] == 'aritmetica_condicional_sem_validacao_pedagogica'
    assert result['comparabilidade'] == 'mesma_base_observada_sem_validacao_longitudinal'
    assert result['premissas'] and result['unidade']['meta_B'] == 'acertos_por_estudante'
    assert result['meta_B'][0]['acertos_projetados'] == 18
    assert result['meta_B'][0]['lacuna_projetada'] == 0
    with pytest.raises(ValueError, match='hipotese'):
        project([observation()], interpretacao='efeito_causal')


def test_T41_adequados_podem_perder_categoria_e_acertos():
    rows = [observation(18, 'Adequado') for _ in range(4)] + [observation(17)]
    stable = project(rows)
    loss = project(rows, saidas_adequado=1, perda_acertos=1)
    assert (stable['meta_A']['adequados_projetados'], stable['meta_A']['atingida_projetada']) == (4, True)
    assert (loss['meta_A']['adequados_projetados'], loss['meta_A']['atingida_projetada']) == (3, False)
    assert loss['meta_A']['entradas_minimas_com_perdas'] == 1
    assert loss['meta_B'][0]['lacuna_projetada'] == 1


@pytest.mark.parametrize('x,g,p,want,gap,delta', [
    (17,0,0,17,1,0), (18,0,0,18,0,0), (18,0,1,17,1,-1),
    (0,0,0,0,18,0), (0,0,2,0,18,0), (21,4,0,22,0,1),
    (17,1,0,18,0,1), (18,1,2,17,1,-1)])
def test_B_aritmetica_individual_saturacao_nao_mascara_deslocamento(x,g,p,want,gap,delta):
    row = project([observation(x)], ganho_acertos=g, perda_acertos=p)['meta_B'][0]
    assert (row['alvo'], row['acertos_projetados'], row['lacuna_projetada']) == (18,want,gap)
    assert row['deslocamento_bruto'] == g-p and row['deslocamento_realizado'] == delta


def test_meta_A_original_nao_deriva_nivel_de_acertos():
    result = project([observation(22), observation(0, 'Adequado')], ganho_acertos=22)
    assert (result['meta_A']['avaliados'], result['meta_A']['adequados'], result['meta_A']['alvo']) == (2,1,2)
    assert result['meta_A']['acertos_ate_adequacao'] is None
    assert result['meta_A']['adequados_projetados'] == 1


def test_corte_de_adequacao_so_com_regra_documentada_ou_hipotese_explicita():
    with pytest.raises(ValueError):
        project([observation()], corte_adequacao=18)
    result = project([observation()], corte_adequacao={'valor':18, 'status':'hipotese_nao_oficial', 'referencia':'exemplo sintetico'})
    row = result['meta_B'][0]['distancia_adequacao_condicional']
    assert row == {'lacuna':1, 'status':'hipotese_nao_oficial', 'referencia':'exemplo sintetico'}
    assert result['meta_A']['acertos_ate_adequacao'] is None


def test_rotulo_de_regra_oficial_sozinho_nao_autoriza_distancia_exata():
    with pytest.raises(ValueError):
        project([observation()], corte_adequacao={'valor':18, 'status':'regra_oficial_documentada', 'referencia':'rotulo sem regra auditada'})


def test_sem_avaliados_e_prova_ausente_nao_sao_zero():
    result = project([dict(componente='LEITURA', participacao=False, categoria=None,
                           acertos=None, oportunidades=None, unidade='itens')])
    assert result['meta_A']['status'] == 'sem_avaliados'
    assert result['meta_A']['atingida_projetada'] is None
    assert result['meta_A']['entradas_minimas_com_perdas'] is None
    assert result['meta_B'][0]['status'] == 'prova_ausente'
    assert result['meta_B'][0]['acertos_projetados'] is None


@pytest.mark.parametrize('component,unit', [('ESCRITA','nota'),('FLUENCIA','tarefas')])
def test_escrita_fluencia_preservam_medida_e_nao_viram_22(component,unit):
    row = dict(componente=component, unidade=unit, participacao=True, categoria='Categoria própria', nota=7)
    original = deepcopy(row)
    result = project([row])
    assert result['meta_A']['status'] == 'unidade_nao_aplicavel'
    assert result['meta_B'][0]['status'] == 'unidade_nao_aplicavel'
    assert result['meta_B'][0]['unidade'] == unit and row == original


@pytest.mark.parametrize('hyp', [{'entradas_adequado':2}, {'saidas_adequado':1},
    {'ganho_acertos':-1}, {'perda_acertos':True}, {'probabilidade_ganho':.9}])
def test_cenarios_impossiveis_ou_probabilidades_arbitrarias_rejeitados(hyp):
    with pytest.raises(ValueError):
        project([observation()], **hyp)


@pytest.mark.parametrize('x,n', [(None,22), (1,None), (1,0), (23,22),(-1,22),(True,22),(1.5,22)])
def test_observado_invalido_nao_e_corrigido_por_saturacao(x,n):
    row = observation(x)
    row['oportunidades'] = n
    with pytest.raises(ValueError):
        project([row])


def test_mistura_de_instrumentos_duplicatas_e_ausencia_inconsistente_rejeitadas():
    with pytest.raises(ValueError):
        project([observation(), observation(component='MATEMATICA')])
    with pytest.raises(ValueError):
        project([observation(avaliacao_local_id='sintetico'), observation(avaliacao_local_id='sintetico')])
    row = observation(); row['participacao'] = False
    with pytest.raises(ValueError):
        project([row])


def test_institucional_calcula_teto_no_escopo_e_nao_soma_tetos():
    rows = [observation() for _ in range(6)]
    assert project(rows)['meta_A']['alvo'] == 5
    assert project(rows[:3])['meta_A']['alvo'] == 3
    assert project([])['meta_A']['atingida_projetada'] is None
