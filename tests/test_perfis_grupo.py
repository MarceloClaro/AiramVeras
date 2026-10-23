"""T48: descrições baseadas em observações, com proveniência e ausência."""
import importlib.util
from copy import deepcopy
import pytest


def api(name):
    assert importlib.util.find_spec('airam.perfis_grupo') is not None, 'Funcionalidade T08 ausente'
    from airam import perfis_grupo
    return getattr(perfis_grupo,name)


def fixture():
    ctx=dict(avaliacao_id='teste',ano_avaliacao=2026,ciclo='I',ano_escolar=2,
             componente='LEITURA',fonte_id='f',sha256='a'*64,exportacao='v1')
    obs=[dict(**ctx,aluno_local_id=f's{i}',posicao=h,numerador=n,denominador=d,
              disponibilidade=d is not None,participacao=d is not None,unidade='acertos_itens',
              turma='A',categoria='Adequado' if i%2 else 'Intermediário',campo_original=h,
              oportunidades_previstas=4) for i in range(6) for h,n,d in [('H1',0,2),('H2',2,2)]]
    links=[dict(avaliacao_id='teste',ano_avaliacao=2026,ano_avaliado=2,ciclo_avaliado='I',
                componente='LEITURA',posicao='H1',codigo_caed='2EF01_P',texto_caed='Ler palavras.',
                codigo_bncc='EF02LP01',texto_bncc='Ler e escrever palavras.',ressalva='Associação parcial.',
                fonte_matriz='matriz.pdf',sha256_pdf='b'*64,pagina_matriz=2,
                fonte_posicao='mapa',versao_posicao='v1',ocorrencia_id='o1',peso_analitico=1,
                status_contextual='proprio_ano_ciclo_confirmado',status_semantico='com_ressalva',
                bncc={'proveniencia_dataset':{'commit':'c'*40}},localizador_bncc={'arquivo':'bncc.json'})]
    result=dict(contexto=ctx,status='grupo_por_regra',grupos=[dict(grupo_id='regra',membros=[f's{i}' for i in range(6)],
        criterio='total C/D abaixo de 4/5',tipo='regra')],cobertura={'cadastrados':6,'elegiveis':6},
        criterios={'versao':'v1'})
    return result,obs,links


def test_T48_constante_lacuna_contagens_fontes_e_revisao():
    r,obs,links=fixture()
    p=api('descrever_grupos')(r,obs,links)[0]
    assert p['n']==6 and p['observado']['acertos']==12 and p['observado']['oportunidades']==24
    assert p['observado']['taxa']==0.5
    assert p['habilidades'][0]['acertos']==0
    assert p['habilidades'][0]['oportunidades']==12
    assert p['habilidades'][0]['constante'] is True
    assert p['habilidades'][0]['curriculo'][0]['codigo_bncc']=='EF02LP01'
    assert p['habilidades'][0]['curriculo'][0]['ressalva']=='Associação parcial.'
    assert p['habilidades'][0]['atividades']
    assert p['revisao_docente']=='pendente' and p['reavaliacao']['data'] is None
    assert p['reavaliacao']['gatilho']
    assert p['categorias_caed_originais']=={'Adequado':3,'Intermediário':3}


def test_T48_fanout_nao_multiplica_contagens_e_contexto_nao_mistura():
    r,obs,links=fixture()
    duplicate=deepcopy(links[0]); duplicate['codigo_bncc']='EF02LP02'
    other=deepcopy(links[0]); other['ano_avaliado']=3; other['codigo_bncc']='ERRADO'
    p=api('descrever_grupos')(r,obs,links+[duplicate,other])[0]
    assert p['observado']['oportunidades']==24
    assert len(p['habilidades'][0]['curriculo'])==2
    obs[0]['ano_escolar']=3
    with pytest.raises(ValueError): api('descrever_grupos')(r,obs,links)


def test_T47_regras_separam_ausentes_e_metaB_total():
    r,obs,links=fixture()
    for row in obs:
        if row['aluno_local_id']=='s0':
            row.update(numerador=None,denominador=None,disponibilidade=False,participacao=False)
    result=api('grupos_por_regras')(obs,0.8)
    counts={g['grupo_id']:len(g['membros']) for g in result['grupos']}
    assert counts=={'abaixo_meta_B':5,'cobertura_insuficiente':1}
    p=api('descrever_grupos')(result,obs,links)
    missing=next(x for x in p if x['grupo_id']=='cobertura_insuficiente')
    assert missing['observado']['taxa'] is None
    assert missing['observado']['acertos'] is None


def test_T48_escrita_fluencia_mantem_unidades_sem_metaB_ou_bncc():
    _,obs,_=fixture()
    for row in obs:
        row.update(componente='ESCRITA',unidade='pontuacao_original',valor=1.5,numerador=None,
                   denominador=None,posicao=None,campo_original='palavras')
    obs=obs[::2]
    result=api('grupos_por_regras')(obs,0.8)
    p=api('descrever_grupos')(result,obs,[])[0]
    assert p['meta_B']['status']=='unidade_nao_aplicavel'
    assert p['medidas_proprias'][0]['distribuicao']['mediana']==1.5
    assert p['medidas_proprias'][0]['unidade']=='pontuacao_original'
    assert p['habilidades']==[] and p['observado']['taxa'] is None


def test_T48_publico_remove_membros_e_suprime_grupo_pequeno():
    r,obs,links=fixture()
    p=api('descrever_grupos')(r,obs,links)
    public=api('perfis_publicos')(p)
    assert 'membros' not in public[0]
    r['grupos'][0]['membros']=['s0']
    small=api('perfis_publicos')(api('descrever_grupos')(r,obs,links))[0]
    assert small['status_publicacao']=='suprimido_n_menor_5'
    assert 'observado' not in small and 'turmas' not in small


def test_T48_nao_inventa_lacuna_em_acerto_integral_ou_forca_em_zero():
    # Catches naming the three smallest rates as deficits even when all are 100%.
    r,obs,links=fixture()
    for row in obs: row['numerador']=row['denominador']
    assert api('descrever_grupos')(r,obs,links)[0]['lacunas_priorizadas']==[]
    for row in obs: row['numerador']=0
    assert api('descrever_grupos')(r,obs,links)[0]['forcas_relativas']==[]
