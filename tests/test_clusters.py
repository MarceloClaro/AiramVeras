"""T45-47: fixtures sintéticas; nenhuma identificação real em recibos."""
import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


def api(name):
    assert importlib.util.find_spec('airam.clusters') is not None, 'Funcionalidade T08 ausente'
    from airam import clusters
    return getattr(clusters, name)


def config():
    c = json.loads((ROOT/'config/agrupamentos.json').read_text(encoding='utf-8'))
    c.update(seeds=[11, 29, 47], subamostras=8)
    return c


def features(n=20):
    return dict(contexto={'ano_escolar': 2, 'componente': 'LEITURA'},
                alunos=[f'sintetico-{i:02d}' for i in range(n)], colunas=['H1','H2','H3'],
                valores=[[0.05+(i%5)*0.01,0.1,0] if i<n//2 else
                         [0.85+(i%5)*0.01,0.9,0] for i in range(n)], cobertura=[1.0]*n)


def test_T45_sementes_subamostras_grupos_e_ordem():
    # Catches row-position membership, missing per-group stability and a single-seed shortcut.
    f, c = features(), config()
    r = api('agrupar')(f,c,18)
    assert r['status']=='exploratorio_estavel'
    assert r['k']==2
    assert [g['n'] for g in r['grupos']]==[10,10]
    assert r['candidatos'][0]['seeds']['planejadas']==3
    assert r['candidatos'][0]['subamostras']['planejadas']==8
    assert r['candidatos'][0]['seeds']['ari']['n']==3
    assert all(g['subamostras']['jaccard']['mediana']==1 for g in r['candidatos'][0]['por_grupo'])
    reverse = deepcopy(f)
    for key in ('alunos','valores','cobertura'):
        reverse[key].reverse()
    assert api('agrupar')(reverse,c,18)==r


def test_T46_um_perfil_e_grupo_pequeno_nao_sao_liberados():
    f=features()
    f['valores']=[[0,0,0]]*20
    r=api('agrupar')(f,config(),18)
    assert r['status']=='sem_agrupamento_estavel' and r['grupos']==[]
    assert r['motivo']=='perfis_sem_variacao'
    f=features(12)
    f['valores']=[[0,0,0]]*3+[[1,1,0]]*9
    r=api('agrupar')(f,config(),18)
    assert r['status']=='sem_agrupamento_estavel'
    assert 'tamanho_original' in r['candidatos'][0]['reprovacoes']


def test_T47_ausencia_excluida_zero_obtido_e_constante_preservados():
    f=features()
    f['valores'][0]=[None,None,None]
    f['cobertura'][0]=0
    r=api('agrupar')(f,config(),18)
    assert r['cobertura']['elegiveis']==19
    assert len(r['excluidos'])==1
    assert r['colunas_constantes']==['H3']
    assert all(f['alunos'][0] not in g['membros'] for g in r['grupos'])


def test_T46_replicacao_nao_impoe_minimo_cinco():
    f=features(24)
    f['valores']=[[i//6/3, (i//6)%2,0] for i in range(24)]
    r=api('agrupar')(f,config(),18)
    k4=next(x for x in r['candidatos'] if x['k']==4)
    assert k4['subamostras']['tamanho']==19
    assert k4['subamostras']['validas']==8
    assert min(k4['subamostras']['minimos_tamanhos'])<5


def test_T45_falhas_planejadas_e_sem_separacao():
    f=features(10)
    f['valores']=[[0,0,0]]+[[1,1,0]]*9
    c=config(); c['subamostras']=20
    r=api('agrupar')(f,c,18)
    d=r['candidatos'][0]['subamostras']
    assert d['planejadas']==20 and d['validas']<20
    assert sum(d['falhas'].values())+d['validas']==20
    assert all(g['subamostras']['avaliaveis']<=20 for g in r['candidatos'][0]['por_grupo'])


@pytest.mark.parametrize('alteracao',['duplicada','fora_escala','cobertura_invalida'])
def test_T47_rejeita_identidade_duplicada_e_dados_invalidos(alteracao):
    f=features()
    if alteracao=='duplicada': f['alunos'][1]=f['alunos'][0]
    elif alteracao=='fora_escala': f['valores'][0][0]=2
    else: f['cobertura'][0]=-1
    with pytest.raises(ValueError): api('agrupar')(f,config(),18)


def test_T45_controle_mesmos_alunos_colunas_e_isolado():
    block=dict(contexto=features()['contexto'],matrizes=dict(alunos=['x','y'],posicoes=['A','B','C'],
        P=[[0,1,0],[1,0,None]],D=[[1,1,1],[1,1,None]],Q=[[1,0,0],[0,1,0],[0,0,1]]),
        propagacoes={'1':{'propagado':[[1,0,None],[0,1,None]],'sem_retorno':[[1,0,None],[0,1,None]]}})
    graph={'A':[[0,1,0],[1,0,0],[0,0,0]]}
    r=api('preparar_bracos')(block,graph,config())
    assert r['status']=='comparavel'
    assert r['bracos']['observado_total']['alunos']==['x']
    assert r['bracos']['observado_controle']['colunas']==['A','B']
    assert r['bracos']['propagado_controle']['valores']==[[1,0]]
    graph['A']=[[0,0,0]]*3
    r=api('preparar_bracos')(block,graph,config())
    assert r['status']=='comparacao_indisponivel'


def test_T45_comparar_particoes_recusa_identidades_diferentes():
    r=api('agrupar')(features(),config(),18)
    other=deepcopy(r); other['alunos'][0]='outro'
    with pytest.raises(ValueError): api('comparar_particoes')(r,other)
    same=api('comparar_particoes')(r,r)
    assert same[0]['ari']==1 and same[0]['pares_coagrupamento_alterados']==0


def test_T46_filtro_grupo_reprova_mesmo_com_ari_alto():
    r=api('agrupar')(features(),config(),18)
    cand=deepcopy(r['candidatos'][0])
    cand['por_grupo'][0]['subamostras']['jaccard']['mediana']=0.1
    assert 'estabilidade_grupo' in api('avaliar_candidato')(cand,config())


def test_T47_sem_casos_elegiveis_continua_resultado_explicito():
    f=features(); f.update(alunos=[],valores=[],cobertura=[])
    r=api('agrupar')(f,config(),18)
    assert r['status']=='sem_agrupamento_estavel'
    assert r['cobertura']['elegiveis']==0
