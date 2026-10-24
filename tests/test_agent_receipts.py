"""T49/T51: o consumidor não promove cadastro ou evento configurado a execução."""
from test_cli import api


def test_perfil_registrado_sem_recibo_nao_vira_inferencia():
    status=api('operacao').estado_agente({'configurado':True,'validado':True,'ativado':True,
        'status':'pending_executor','spec_id':'TSPEC-artificial'})
    assert status['executado'] is False
    assert status['entregue'] is False


def test_execucao_bloqueada_com_spec_preserva_zero_passos():
    status=api('operacao').estado_agente({'status':'blocked','spec_id':'TSPEC-artificial','steps':0,'agent_id':None})
    assert status['executado'] is False and status['spec_id']=='TSPEC-artificial'


def test_evento_configurado_sem_disparo_real_nao_e_ativo():
    status=api('operacao').estado_evento({'configurado':True,'estado':'contract_only'})
    assert status['ativo_verificado'] is False


def test_contrato_consumido_autentica_recibo_e_nao_promove_registro(tmp_path):
    import json
    from test_cli import sha
    operation=api('operacao'); fn=getattr(operation,'carregar_contratos',None)
    assert callable(fn),'Consumo de contratos ausente'
    receipt=tmp_path/'core.json'
    receipt.write_text(json.dumps({'spec_id':'TSPEC-artificial','status':'blocked','steps':0,'agent_id':None}))
    contract=tmp_path/'contratos.json'
    contract.write_text(json.dumps({'primario':'marceloclaro','perfis':[{'id':'plugin-data','configurado':True,
        'validado':True,'ativado':True,'executado':True,'recibo':{'caminho':'core.json','sha256':sha(receipt)}}],
        'eventos_sessao':{'configurado':True,'estado':'contract_only'}}))
    status=fn(tmp_path,{'caminho':'contratos.json','sha256':sha(contract)})
    assert status['perfis'][0]['executado'] is False
    assert status['eventos_sessao']['ativo_verificado'] is False
    receipt.write_text('{}')
    import pytest
    with pytest.raises(ValueError): fn(tmp_path,{'caminho':'contratos.json','sha256':sha(contract)})
