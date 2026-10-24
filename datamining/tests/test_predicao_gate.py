"""T42–T44: exports, asserted historical labels, leakage and overlaps fail closed."""
from copy import deepcopy
import pytest
from test_metricas import api


def gate(evaluations, links):
    return api('predicao_gate', 'avaliar_prontidao_temporal')(evaluations, links)


def evidence():
    return {'fonte_sha256':'a'*64, 'referencia':'fixture sintetica documentada'}


def complete():
    rows = []
    for key,cycle,date,cut,part in [('a','I','2025-05-20','2025-04-20','treino'),
                                     ('b','II','2026-05-20','2026-04-20','teste')]:
        rows.append(dict(avaliacao_id=key,ciclo=cycle,ciclo_evidencia=evidence(),
            data_aplicacao={'valor':date,'tipo':'aplicacao','evidencia':evidence()},
            comparabilidade={'grupo':'mesmo_contrato','evidencia':evidence()},
            desfecho_observado=evidence(),particao=part,data_limite_features=cut,
            variaveis_entrada=['medida_previa'],alvo='resultado_futuro',componentes_alvo=['item_futuro'],
            processamento={'ajustado_em':'treino','evidencia':evidence()}))
    links = [dict(avaliacao_id='a',aluno_local_id='sintetico_A', identidade_longitudinal=evidence()),
             dict(avaliacao_id='b',aluno_local_id='sintetico_B', identidade_longitudinal=evidence())]
    return rows, links


def test_T42_ciclo_unico_bloqueia_previsao_preserva_cenario():
    result = gate([{'ciclo':'I','ano_avaliacao':2026}], [])
    assert result['previsao_temporal_validada'] is False
    assert result['prontidao_inputs_temporais'] is False
    assert 'ciclos_documentados_insuficientes' in result['motivos']
    assert result['cenarios_disponiveis'] is True
    assert result['tipo_resultado'] == 'gate_documental_temporal'
    assert all(k in result for k in ['premissas','unidade','comparabilidade','status_validacao'])


def test_ausencia_de_metadados_nao_afirma_vazamento_ou_ajuste_observado():
    result=gate([{'ciclo':'I'}],[])
    assert 'vazamento_temporal' not in result['motivos']
    assert 'processamento_fora_treino' not in result['motivos']
    assert 'corte_temporal_nao_comprovado' in result['motivos']
    assert 'processamento_treino_nao_comprovado' in result['motivos']


def test_exportacao_e_rotulos_assumidos_nao_provam_aplicacao():
    rows, links = complete()
    rows[0]['data_aplicacao']['tipo'] = 'exportacao'
    rows[1]['ciclo_evidencia'] = {'rotulo':'contraprova','assumido':True}
    result = gate(rows,links)
    assert result['prontidao_inputs_temporais'] is False
    assert 'datas_aplicacao_nao_comprovadas' in result['motivos']
    assert 'ciclos_documentados_insuficientes' in result['motivos']


def test_contrato_completo_habilita_prontidao_de_inputs_mas_nao_valida_modelo():
    result = gate(*complete())
    assert result['prontidao_inputs_temporais'] is True
    assert result['previsao_temporal_validada'] is False
    assert result['pendencias_modelo'] and result['status_validacao'] == 'sem_modelo_temporal_validado'


@pytest.mark.parametrize('field,value,motive', [
    ('variaveis_entrada',['resultado_futuro'],'vazamento_alvo'),
    ('variaveis_entrada',['item_futuro'],'vazamento_alvo'),
    ('data_limite_features','2026-06-20','vazamento_temporal'),
    ('processamento',{'ajustado_em':'todos','evidencia':evidence()},'processamento_fora_treino'),
    ('comparabilidade',{'grupo':'mesmo_contrato','evidencia':True},'comparabilidade_nao_comprovada'),
    ('desfecho_observado',True,'desfecho_futuro_nao_comprovado')])
def test_T43_vazamento_e_precondicoes_sem_evidencia_bloqueiam(field,value,motive):
    rows,links = complete(); rows[1][field]=value
    result=gate(rows,links)
    assert result['prontidao_inputs_temporais'] is False and motive in result['motivos']


def test_T44_mesmo_estudante_em_treino_teste_recusado():
    rows,links = complete(); links[1]['aluno_local_id']=links[0]['aluno_local_id']
    result=gate(rows,links)
    assert result['prontidao_inputs_temporais'] is False
    assert 'estudante_em_treino_e_teste' in result['motivos']


def test_particoes_invertidas_datas_invalidas_vinculo_provisorio_recusados():
    rows,links = complete()
    rows[0]['particao']='teste'; rows[1]['particao']='treino'
    links[1]['identidade_longitudinal']=True
    result=gate(rows,links)
    assert 'particao_temporal_invalida' in result['motivos']
    assert 'identidade_longitudinal_nao_comprovada' in result['motivos']
    rows,links=complete(); rows[0]['data_aplicacao']['valor']='2025-02-30'
    assert 'datas_aplicacao_nao_comprovadas' in gate(rows,links)['motivos']


def test_gate_nao_muta_entradas_e_nao_publica_chaves_individuais():
    rows,links=complete(); before=deepcopy((rows,links))
    result=gate(rows,links)
    assert (rows,links)==before
    assert 'sintetico_A' not in str(result) and 'sintetico_B' not in str(result)
    assert gate([],[])['prontidao_inputs_temporais'] is False
