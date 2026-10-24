"""T16/T37-T39: limites, parte-todo, conteúdo e desenhos de reamostragem."""
from copy import deepcopy
from importlib import import_module, util
import itertools
import math
import numpy as np
import pytest
from scipy import stats


def api(name):
    assert util.find_spec('airam.correlacoes') is not None, 'Funcionalidade de correlacao ausente'
    fn = getattr(import_module('airam.correlacoes'), name, None)
    assert callable(fn), 'Funcionalidade de correlacao ausente'
    return fn


STRATA = ['turma', 'ano_escolar', 'ano_avaliacao', 'ciclo', 'instrumento']
CFG = dict(permutacoes=199, teto_exato=1000, bootstrap=199, lote=64,
    min_n_inferencia=3, min_fracao_bootstrap_valida=.9, quantis=[.025,.975],
    desenho='Y_dentro_estrato_X_fixo', bilateral='duas_caudas_duplicadas')


def pairs(x, y, classes=None):
    return [dict(aluno_local_id=f'fixture-{i}', turma=classes[i] if classes else 'A',
        ano_escolar=1, ano_avaliacao=2026, ciclo='I', instrumento='fixture', x=a,y=b)
        for i,(a,b) in enumerate(zip(x,y))]


def calc(rows, **kwargs):
    return api('correlacionar')(rows, 'x','y', STRATA, 719, config=CFG | kwargs)


@pytest.mark.parametrize('x,y,motivo', [([],[],'pares_insuficientes'),
    ([1],[2],'pares_insuficientes'), ([1,1,1],[1,2,3],'coluna_constante')])
def test_T16_indefinido_nao_recebe_zero(x,y,motivo):
    for out in calc(pairs(x,y)):
        assert out['coeficiente'] is None and out['p'] is None and out['q'] is None
        assert out['motivo_coeficiente'] == motivo


def test_dois_pares_algebra_sem_p_nem_faixa():
    for out in calc(pairs([0,1],[8,2])):
        assert out['coeficiente'] == pytest.approx(-1)
        assert out['p'] is None and out['q'] is None
        assert out['motivo_inferencia'] == 'N_abaixo_minimo'
        assert out['sensibilidade']['faixa'] is None


def test_empates_scipy_e_contraprova_algebrica_independente():
    x,y=[0,1,1,3,4], [4,1,2,0,2]
    result=calc(pairs(x,y))
    n=len(x)
    cov=n*sum(a*b for a,b in zip(x,y))-sum(x)*sum(y)
    algebra=cov/math.sqrt((n*sum(a*a for a in x)-sum(x)**2)*(n*sum(b*b for b in y)-sum(y)**2))
    assert result[0]['coeficiente']==pytest.approx(algebra)
    assert result[0]['coeficiente']==pytest.approx(stats.pearsonr(x,y).statistic)
    assert result[1]['coeficiente']==pytest.approx(stats.spearmanr(x,y).statistic)


def test_T39_permutacao_exata_confrontada_scipy_pairings():
    x,y=np.array([1.,2,4,8]),np.array([1.,4,2,8])
    out=calc(pairs(x,y))[0]
    expected=stats.permutation_test((y,),lambda yy:stats.pearsonr(x,yy).statistic,
        permutation_type='pairings',n_resamples=np.inf,alternative='two-sided')
    assert out['p']==pytest.approx(expected.pvalue)
    assert out['permutacao']['modo']=='exato' and out['permutacao']['replicacoes']==24


def test_T39_estratos_preservam_turma_composicao_e_null_degenerada():
    rows=pairs([1,1,1,9,9,9],[2,2,2,8,8,8],['A']*3+['B']*3)
    out=calc(rows)[0]
    assert out['coeficiente']==pytest.approx(1)
    assert out['p'] is None and out['motivo_inferencia']=='nula_degenerada'
    assert out['estratos']==[{'turma':'A','n':3},{'turma':'B','n':3}]


def test_T39_rejeita_desenho_errado_ou_estratos_omitidos():
    rows=pairs([0,1,2],[2,1,0])
    with pytest.raises(ValueError):
        calc(rows, desenho='XY_mesmo_indice')
    with pytest.raises(ValueError):
        api('correlacionar')(rows,'x','y',['ano_escolar'],1,config=CFG)


def test_T39_permutacoes_restritas_contraprova_enumeracao():
    x,y=[0,1,2,10,11,14],[1,0,4,16,11,10]
    out=calc(pairs(x,y,['A']*3+['B']*3))[0]
    null=[stats.pearsonr(x,a+b).statistic for a,b in itertools.product(
        itertools.permutations(y[:3]),itertools.permutations(y[3:]))]
    r=stats.pearsonr(x,y).statistic
    p=min(1,2*min(sum(v<=r+1e-12 for v in null),sum(v>=r-1e-12 for v in null))/36)
    assert out['p']==pytest.approx(p)


def test_mascaras_n_por_variavel_zero_real_e_reordenacao_deterministica():
    rows=pairs([0,1,None,3,5,9],[0,None,2,3,8,5],['A']*3+['B']*3)
    before=deepcopy(rows)
    out=calc(rows,teto_exato=1)
    assert out==calc(list(reversed(rows)),teto_exato=1) and rows==before
    assert out[0]['n']==4 and out[0]['n_x']==5 and out[0]['n_y']==5
    assert out[0]['cadastros']==6
    assert out[0]['permutacao']['modo']=='monte_carlo'
    assert out[0]['p']>=2/200


def test_bootstrap_pareado_preserva_relacao_e_degeneradas_contadas():
    out=calc(pairs([0,1,2,3,4],[0,2,4,6,8]))[0]
    assert out['sensibilidade']['faixa']==pytest.approx([1,1])
    assert out['sensibilidade']['validas']+out['sensibilidade']['degeneradas']==199
    assert out['influencia']['max_delta']==pytest.approx(0,abs=1e-12)


def test_bootstrap_muitas_degeneradas_suprime_faixa():
    out=calc(pairs([0]*9+[1],[0]*9+[1]))[0]
    assert out['sensibilidade']['faixa'] is None
    assert out['sensibilidade']['motivo']=='replicacoes_validas_insuficientes'


@pytest.mark.parametrize('change',[{'ano_escolar':2},{'instrumento':'outro'}, {'turma':None}])
def test_recusa_mistura_de_instrumento_ano_ou_contexto_ausente(change):
    rows=pairs([0,1,2],[2,1,0]); rows[1].update(change)
    with pytest.raises(ValueError): calc(rows)


def test_recusa_duplicata_e_numeros_invalidos():
    rows=pairs([0,1,2],[2,1,0])
    with pytest.raises(ValueError): calc(rows+rows[:1])
    rows[0]['x']=float('nan')
    with pytest.raises(ValueError): calc(rows)


def h(student,position,n,d):
    return dict(aluno_local_id=student,avaliacao_local_id=student,avaliacao_id='AV',
        ano_avaliacao=2026,ciclo='I',ano_escolar=1,componente='LEITURA',fonte_id='fixture',
        sha256='a'*64,exportacao='fixture',turma='A',posicao=position,participacao=True,
        disponibilidade=n is not None,unidade='acertos_itens',numerador=n,denominador=d,
        caminho='fixture.csv',linha_fonte=2,bruto='fixture')


def test_T37_retira_numerador_e_denominador_e_muda_associacao():
    rows=[h('a','H 01',1,1),h('a','H 02',0,3), h('b','H 01',0,1),h('b','H 02',1,3)]
    out=api('total_sem_bloco')(rows,'H 01')
    assert [(r['x'],r['y'],r['acertos_restantes'],r['oportunidades_restantes']) for r in out]==[(1,0,0,3),(0,1/3,1,3)]
    # Totais inclusivos seriam iguais (1/4): associação indefinida; corrigido é -1.
    assert calc(out)[0]['coeficiente']==pytest.approx(-1)


def test_T37_cobertura_incompleta_ou_bloco_unico_nao_inventa_total():
    rows=[h('a','H 01',1,1),h('a','H 02',None,None)]
    assert api('total_sem_bloco')(rows,'H 01')[0]['y'] is None
    assert api('total_sem_bloco')(rows[:1],'H 01')[0]['y'] is None
    with pytest.raises(ValueError):api('total_sem_bloco')(rows+rows[:1],'H 01')


def test_T37_oportunidades_heterogeneas_nao_viram_total_comparavel():
    # Mesma posição/contexto mas instrumentos de comprimentos incompatíveis.
    rows=[h('a','H 01',1,1),h('a','H 02',1,3),h('b','H 01',0,1),h('b','H 02',1,4)]
    with pytest.raises(ValueError):api('total_sem_bloco')(rows,'H 01')


def test_T37_linha_omitida_na_api_direta_nao_vira_cobertura_completa():
    rows=[h('a','H 01',1,1),h('a','H 02',1,2),h('a','H 03',0,2),
          h('b','H 01',0,1),h('b','H 02',1,2)]
    with pytest.raises(ValueError,match='Composicao'):
        api('total_sem_bloco')(rows,'H 01')


def test_T37_linha_mascarada_preserva_composicao_mas_total_ausente():
    rows=[h('a','H 01',1,1),h('a','H 02',1,2),h('a','H 03',0,2),
          h('b','H 01',0,1),h('b','H 02',1,2),h('b','H 03',None,None)]
    out=api('total_sem_bloco')(rows,'H 01')
    assert [(r['blocos_restantes'],r['cobertura_completa'],r['y']) for r in out]==[(2,True,.25),(2,False,None)]


@pytest.mark.parametrize('context_change',[{'ano_escolar':2},{'sha256':'b'*64}])
def test_T37_composicoes_diferentes_permitidas_em_contextos_distintos(context_change):
    first=[h('a','H 01',1,1),h('a','H 02',1,2),h('a','H 03',0,2)]
    second=[h('a','H 01',0,1)|context_change,h('a','H 02',1,2)|context_change]
    out=api('total_sem_bloco')(first+second,'H 01')
    assert len({r['instrumento'] for r in out})==2
    assert sorted((r['blocos_restantes'],r['cobertura_completa'],r['y']) for r in out)==[(1,True,.5),(2,True,.25)]


def test_T38_auditoria_confere_valores_nao_apenas_ids():
    rows=pairs([0,1,2],[2,1,0]); bad=deepcopy(rows); bad[1]['y']=99
    assert api('auditar_pares')(rows,list(reversed(rows)))['pares_conferidos']==3
    with pytest.raises(ValueError):api('auditar_pares')(bad,rows)


def fixture_tables():
    av=[]; measures=[]; skills=[]
    for i in range(4):
        for comp in ['LEITURA','MATEMATICA','ESCRITA','FLUENCIA']:
            row=dict(aluno_local_id=f'fixture-{i}',avaliacao_local_id=f'fixture-{i}-{comp}',
                ano_escolar=1,ano_avaliacao=2026,ciclo='I',turma='A',componente=comp,
                avaliacao_id=comp,fonte_id=comp,sha256='a'*64,exportacao='fixture',
                participacao=True,taxa=i/3 if comp in ['LEITURA','MATEMATICA'] else None)
            av.append(row)
            if comp=='ESCRITA':measures.append(row|dict(campo_original='Nota',disponibilidade=i!=1,valor=i+2 if i!=1 else None,unidade='nota_escrita'))
            if comp=='LEITURA':
                for pos in ['H 01','H 02']:skills.append(h(f'fixture-{i}',pos,i,3)|row)
    return dict(avaliacoes=av,habilidades=skills,escrita=measures,fluencia=[])


def test_R08_R15_planeja_todos_componentes_sem_converter_nota():
    out=api('preparar_analises')(fixture_tables())
    match=next(a for a in out if a['x']=='leitura_taxa' and a['y']=='escrita_nota')
    assert [r['y'] for r in match['pares']]==[2,None,4,5]
    assert match['unidade_y']=='nota_escrita'
    flu=[a for a in out if a['y'].startswith('fluencia')]
    assert len(flu)==15 and all(all(r['y'] is None for r in a['pares']) for a in flu)


def test_R15_recusa_alteracao_turma_entre_componentes():
    tables=fixture_tables(); tables['avaliacoes'][1]['turma']='B'
    with pytest.raises(ValueError):api('preparar_analises')(tables)


def test_T37_preparador_preserva_recusa_de_linha_omitida():
    tables=fixture_tables()
    tables['habilidades']=[r for r in tables['habilidades']
        if not (r['aluno_local_id']=='fixture-0' and r['posicao']=='H 02')]
    with pytest.raises(ValueError,match='Composicao'):
        api('preparar_analises')(tables)
