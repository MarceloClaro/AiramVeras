"""Contraprova independente: stdlib/Fraction, sem importar airam ou seu coletor."""
from collections import Counter
from fractions import Fraction
from math import ceil
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(relative, expected=None):
    p=ROOT/relative
    if expected is not None:
        assert sha(p)==expected, 'Entrada nao autenticada'
    return json.loads(p.read_text(encoding='utf-8'))


def need(condition):
    if not condition:
        raise AssertionError('Contraprova aritmetica divergente; detalhes individuais omitidos')


def main():
    source=read('estatistica/t05/checkpoint.json','5bfa87b38394d171589a7799751127dceb7d81587bbbfcefa67d2bb4a8420231')
    original=read('restrito/t05/checkpoint.json','6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b')
    actual=read('estatistica/t09/checkpoint.json'); private=read('restrito/t09/checkpoint.json')
    config=read('config/cenarios.json')
    need(config['metas']=={'A':.8,'B':.8})
    scopes={tuple(r[k] for k in ('ano_escolar','componente','nivel','turma')):r for r in source['metas_A']}
    a_checks=0
    for result in [*actual['cenarios'],*actual['sensibilidade_meta_A']]:
        key=tuple(result[k] for k in ('ano_escolar','componente','nivel','turma'))
        categories=scopes[key]['categorias_contagens']
        n=sum(categories.values()); a=categories.get('Adequado',0); t=ceil(Fraction(4,5)*n)
        hyp=result.get('hipoteses',{'entradas_adequado':0,'saidas_adequado':result.get('saidas',0)})
        e,s=hyp['entradas_adequado'],hyp['saidas_adequado']
        r=result['meta_A']; minimum=max(0,t-a+s)
        need((r['avaliados'],r['adequados'],r['alvo'],r['conversoes'])==(n,a,t,max(0,t-a)))
        need((r['adequados_projetados'],r['atingida_projetada'])==(a+e-s,a+e-s>=t))
        need(r['entradas_minimas_com_perdas']==minimum and r['viavel']==(minimum<=n-a))
        need(r['fracao_projetada']=={'numerador':a+e-s,'denominador':n})
        need(r['acertos_ate_adequacao'] is None)
        a_checks+=1
    applications={r['avaliacao_local_id']:r for r in original['observado']['avaliacoes']}
    scenario_map={r['nome']:r['hipoteses'] for r in config['cenarios']}
    b_checks=0; expected_summaries={}
    for row in private['cenarios_individuais']:
        observed=applications[row['avaliacao_local_id']]
        need(row['resultado_observado']==dict(observed,unidade='itens'))
        need(row['aluno_local_id']==observed['aluno_local_id'])
        x,n=observed['acertos'],observed['oportunidades']; r=row['meta_B']; hyp=scenario_map[row['cenario']]
        delta=hyp['ganho_acertos']-hyp['perda_acertos']
        if x is None:
            need(n is None and not observed['participacao'])
            need(r['status']=='prova_ausente' and all(r[k] is None for k in ('alvo','lacuna','acertos_projetados','lacuna_projetada','atingida_projetada')))
        else:
            need(type(x) is int and 0<=x<=n and n==22)
            t=ceil(Fraction(4,5)*n); projected=min(n,max(0,x+delta))
            need((r['alvo'],r['lacuna'],r['atingida'])==(t,max(0,t-x),x>=t))
            need((r['acertos_projetados'],r['lacuna_projetada'],r['atingida_projetada'])==(projected,max(0,t-projected),projected>=t))
            need(r['deslocamento_bruto']==delta and r['deslocamento_realizado']==projected-x)
        b_checks+=1
    # Agregação independente dos individuais, inclusive escopos turma sobrepostos.
    for result in actual['cenarios']:
        selected=[r for r in private['cenarios_individuais'] if r['cenario']==result['cenario']
            and r['ano_escolar']==result['ano_escolar'] and r['componente']==result['componente']
            and (result['nivel']=='escola' or r['turma']==result['turma'])]
        valid=[r['meta_B'] for r in selected if r['meta_B']['acertos_observados'] is not None]
        want=dict(cadastros=len(selected),disponiveis=len(valid),ausentes=len(selected)-len(valid),
            unidade='acertos_por_estudante',alvo_individual=18,
            atingiram_observado=sum(r['atingida'] for r in valid),atingiram_projetado=sum(r['atingida_projetada'] for r in valid),
            lacunas_observadas=dict(Counter(str(r['lacuna']) for r in valid)),
            lacunas_projetadas=dict(Counter(str(r['lacuna_projetada']) for r in valid)))
        need(want==result['meta_B_resumo'])
    own_checks=0
    for row in private['outros_instrumentos']:
        observed=row['resultado_observado']; need(observed==applications[observed['avaliacao_local_id']])
        table='escrita' if observed['componente']=='ESCRITA' else 'fluencia'
        measures=[r for r in original['observado'][table] if r['avaliacao_local_id']==observed['avaliacao_local_id']]
        need(row['medidas_observadas']==measures)
        need(row['meta_A_status']==row['meta_B_status']=='unidade_nao_aplicavel')
        own_checks+=1
    raw=(ROOT/'estatistica/t09/checkpoint.json').read_text(encoding='utf-8')
    need(not any(r[k] in raw for r in applications.values() for k in ('aluno_local_id','avaliacao_local_id')))
    need(len(actual['cenarios'])==96 and len(actual['sensibilidade_meta_A'])==96)
    need(len(private['cenarios_individuais'])==1376 and own_checks==296)
    need({r['ciclo'] for r in applications.values()}=={'I'})
    need({r['ano_avaliacao'] for r in applications.values()}=={2026})
    need(all(r['data_aplicacao'] is None for r in applications.values()))
    need(actual['gate_temporal']['previsao_temporal_validada'] is False)
    need(actual['gate_temporal']['prontidao_inputs_temporais'] is False and actual['gate_temporal']['cenarios_disponiveis'] is True)
    result=dict(metodo='stdlib_Fraction_independente_sem_airam',coincide=True,
        escopos_meta_A=len(scopes),conferencias_meta_A=a_checks,conferencias_meta_B=b_checks,
        resumos_meta_B=96,outras_aplicacoes_preservadas=own_checks,sigilo_publico=True,
        publico_sha256=sha(ROOT/'estatistica/t09/checkpoint.json'),restrito_sha256=sha(ROOT/'restrito/t09/checkpoint.json'))
    (ROOT/'evidencias/T09/contraprova-resultado.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':
    main()
