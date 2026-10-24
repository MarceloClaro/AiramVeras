"""Associação descritiva e inferência condicional; nunca efeito de ensino.

Pares/linhas individuais retornados pelo preparo são exclusivamente restritos.
correlacionar devolve apenas agregados, sem identificadores individuais.
"""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
import hashlib
import json
import math
from numbers import Real
from pathlib import Path
import unicodedata

import numpy as np
from scipy.stats import rankdata

from airam.metricas import CONTEXTO, agregar_habilidades

ESTRATOS = ('turma', 'ano_escolar', 'ano_avaliacao', 'ciclo', 'instrumento')


def configuracao():
    return json.loads((Path(__file__).resolve().parents[1]/'config/correlacoes.json').read_text(encoding='utf-8'))


def _serial(value):
    return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)


def _instrumento(context):
    return hashlib.sha256(_serial(context).encode()).hexdigest()


def ajustar_bh(p_values: list[float | None]) -> list[float | None]:
    """BH com m planejado: None ocupa hipótese não testada, mas seu q é None."""
    if any(p is not None and (type(p) not in (int,float) or not math.isfinite(p) or not 0<=p<=1) for p in p_values):
        raise ValueError('p invalido')
    m=len(p_values)
    order=sorted(range(m),key=lambda i:1 if p_values[i] is None else p_values[i])
    result=[None]*m
    running=1.0
    for rank in range(m,0,-1):
        i=order[rank-1]
        p=1 if p_values[i] is None else p_values[i]
        running=min(running,p*m/rank)
        if p_values[i] is not None:result[i]=running
    return result


def ajustar_familias(rows: list[dict]) -> list[dict]:
    groups=defaultdict(list)
    out=[dict(r) for r in rows]
    global_q=ajustar_bh([r['p'] for r in rows])
    for i,row in enumerate(rows):groups[row['familia']].append(i)
    for indices in groups.values():
        ps=[rows[i]['p'] for i in indices]
        qs=ajustar_bh(ps)
        harmonic=sum(1/k for k in range(1,len(indices)+1))
        for i,q in zip(indices,qs):
            out[i].update(q=q,q_by=None if q is None else min(1,q*harmonic),
                q_bh_global=global_q[i],m_planejado=len(indices),m_bh=len(indices),
                m_elegivel=sum(p is not None for p in ps),m_global=len(rows))
    return out


def _coef(x,y):
    """Último eixo, vetorizado, None representado internamente por NaN."""
    a=x-np.mean(x,axis=-1,keepdims=True)
    b=y-np.mean(y,axis=-1,keepdims=True)
    den=np.sqrt(np.sum(a*a,axis=-1)*np.sum(b*b,axis=-1))
    with np.errstate(invalid='ignore',divide='ignore'):
        return np.clip(np.sum(a*b,axis=-1)/den,-1,1)


def _permutar(x,y,groups,seed,cfg):
    space=math.prod(math.factorial(len(g)) for g in groups)
    exact=space<=cfg['teto_exato']
    count=space if exact else cfg['permutacoes']
    rng=np.random.default_rng(seed)
    null=[]
    if exact:
        iterator=product(*(permutations(g.tolist()) for g in groups))
    for start in range(0,count,cfg['lote']):
        size=min(cfg['lote'],count-start)
        indices=np.tile(np.arange(len(y)),(size,1))
        if exact:
            for j in range(size):
                for group,perm in zip(groups,next(iterator)):indices[j,group]=perm
        else:
            for group in groups:
                # Cada linha é uma permutação independente de Y, X permanece fixo.
                indices[:,group]=rng.permuted(np.tile(group,(size,1)),axis=1)
        null.append(_coef(x,y[indices]))
    vals=np.concatenate(null)
    observed=float(_coef(x,y)); tolerance=1e-12
    meta=dict(modo='exato' if exact else 'monte_carlo',replicacoes=count,
        espaco_permutacoes=str(space),validas=int(np.isfinite(vals).sum()),
        resolucao_bilateral=2/count if exact else 2/(count+1),
        minimo=float(np.min(vals)),maximo=float(np.max(vals)),
        seed=seed,convencao='duas_caudas_duplicadas')
    if not np.isfinite(vals).all() or np.ptp(vals)<=tolerance:
        return None,'nula_degenerada',meta
    add=0 if exact else 1
    lo=(int(np.sum(vals<=observed+tolerance))+add)/(count+add)
    hi=(int(np.sum(vals>=observed-tolerance))+add)/(count+add)
    return min(1.,2*min(lo,hi)),None,meta


def _sensibilidade(x,y,groups,seed,cfg,method):
    count=cfg['bootstrap']
    result=dict(replicacoes=count,validas=0,degeneradas=0,faixa=None,
        rotulo='sensibilidade_a_recomposicao_dos_avaliados',motivo=None)
    if len(x)<3:
        result.update(replicacoes=0,motivo='N_abaixo_3')
        return result
    rng=np.random.default_rng(seed)
    values=[]
    for start in range(0,count,cfg['lote']):
        size=min(cfg['lote'],count-start)
        indices=np.tile(np.arange(len(x)),(size,1))
        for group in groups:indices[:,group]=rng.choice(group,size=(size,len(group)),replace=True)
        a,b=x[indices],y[indices]
        if method=='spearman':a,b=rankdata(a,axis=1),rankdata(b,axis=1)
        values.append(_coef(a,b))
    vals=np.concatenate(values)
    good=vals[np.isfinite(vals)]
    result.update(validas=len(good),degeneradas=count-len(good))
    if len(good)/count<cfg['min_fracao_bootstrap_valida']:
        result['motivo']='replicacoes_validas_insuficientes'
    else:result['faixa']=np.quantile(good,cfg['quantis']).tolist()
    return result


def _influencia(x,y,method,observed):
    values=[]
    if len(x)>=4:
        for i in range(len(x)):
            a,b=np.delete(x,i),np.delete(y,i)
            if method=='spearman':a,b=rankdata(a),rankdata(b)
            value=float(_coef(a,b))
            if math.isfinite(value):values.append(value)
    return dict(validas=len(values),degeneradas=len(x)-len(values) if len(x)>=4 else 0,
        minimo=min(values) if values else None,maximo=max(values) if values else None,
        max_delta=max(abs(v-observed) for v in values) if values else None,
        motivo=None if values else 'exclusao_individual_nao_interpretavel')


def correlacionar(pares: list[dict], x: str, y: str, strata: list[str], seed: int,
                  *, config: dict | None=None) -> list[dict]:
    """Um contexto ano/instrumento; permutação de Y restrita às turmas.

    x/y devem estar mascarados previamente por participação e disponibilidade.
    None é ausência; zero é medida. Não oferece opção de permutar XY juntos.
    """
    cfg=configuracao() if config is None else config
    if (set(strata)!=set(ESTRATOS) or len(strata)!=len(ESTRATOS)
        or cfg['desenho']!='Y_dentro_estrato_X_fixo' or cfg['bilateral']!='duas_caudas_duplicadas'):
        raise ValueError('Desenho de permutacao invalido')
    if any(type(cfg[k]) is not int or cfg[k]<1 for k in ('permutacoes','teto_exato','bootstrap','lote')):
        raise ValueError('Resolucao computacional invalida')
    if cfg['min_n_inferencia']<3 or not 0<cfg['min_fracao_bootstrap_valida']<=1:
        raise ValueError('Politica de elegibilidade invalida')
    contexts=set(); seen=set()
    for row in pares:
        if any(row.get(k) in (None,'') for k in (*ESTRATOS,'aluno_local_id')):
            raise ValueError('Contexto do par incompleto')
        contexts.add(tuple(row[k] for k in ESTRATOS[1:]))
        if row['aluno_local_id'] in seen:raise ValueError('Estudante duplicado')
        seen.add(row['aluno_local_id'])
        for field in (x,y):
            value=row[field]
            if value is not None and (isinstance(value,(bool,np.bool_)) or not isinstance(value,Real) or not math.isfinite(value)):
                raise ValueError('Medida nao quantitativa ou nao finita')
    if len(contexts)>1:raise ValueError('Ano/instrumento incompativel')
    complete=sorted((r for r in pares if r[x] is not None and r[y] is not None),
                    key=lambda r:(tuple(str(r[k]) for k in ESTRATOS),str(r['aluno_local_id'])))
    n=len(complete)
    a=np.array([r[x] for r in complete],dtype=float)
    b=np.array([r[y] for r in complete],dtype=float)
    grouped=defaultdict(list)
    for i,r in enumerate(complete):grouped[tuple(r[k] for k in ESTRATOS)].append(i)
    groups=[np.array(g,dtype=int) for g in grouped.values()]
    reason='pares_insuficientes' if n<2 else 'coluna_constante' if np.ptp(a)==0 or np.ptp(b)==0 else None
    common=dict(n=n,n_x=sum(r[x] is not None for r in pares),n_y=sum(r[y] is not None for r in pares),
        cadastros=len(pares),excluidos=len(pares)-n,estratos=[dict(turma=k[0],n=len(v)) for k,v in grouped.items()],
        distintos_x=len(np.unique(a)),distintos_y=len(np.unique(b)),
        amplitude_x=[float(min(a)),float(max(a))] if n else None,
        amplitude_y=[float(min(b)),float(max(b))] if n else None,
        estimando='correlacao_descritiva_dos_pares_avaliados_no_ano',
        hipotese='pareamento_Y_intercambiavel_condicional_a_turma_ano_instrumento',
        limite='nao_causal;intercambiabilidade_assumida_nao_demonstrada;sem_generalizacao_automatica')
    out=[]
    for method in ('pearson','spearman'):
        ax,by=(rankdata(a),rankdata(b)) if method=='spearman' else (a,b)
        r=None if reason else float(_coef(ax,by))
        row=common|dict(metodo=method,coeficiente=r,motivo_coeficiente=reason,
            p=None,q=None,motivo_inferencia=reason,permutacao=None,
            sensibilidade=dict(replicacoes=0,validas=0,degeneradas=0,faixa=None,motivo=reason,
                rotulo='sensibilidade_a_recomposicao_dos_avaliados'),influencia=None)
        if r is not None:
            row['sensibilidade']=_sensibilidade(a,b,groups,seed+1,cfg,method)
            row['influencia']=_influencia(a,b,method,r)
            if n<cfg['min_n_inferencia']:row['motivo_inferencia']='N_abaixo_minimo'
            else:
                row['p'],row['motivo_inferencia'],row['permutacao']=_permutar(ax,by,groups,seed,cfg)
        out.append(row)
    return out


def total_sem_bloco(rows: list[dict], posicao: str) -> list[dict]:
    """Remove numerador E oportunidades do bloco, sem cobrir ausências."""
    agregar_habilidades(rows)  # Contrato de contagens, máscaras e contexto T05.
    groups=defaultdict(list)
    denominators=defaultdict(set)
    for r in rows:
        context=tuple(r[k] for k in CONTEXTO)
        groups[context+(r['aluno_local_id'],)].append(r)
        if r['disponibilidade']:denominators[context+(r['posicao'],)].add(r['denominador'])
    if any(len(ds)>1 for ds in denominators.values()):
        raise ValueError('Oportunidades de H incompativeis no instrumento')
    compositions=defaultdict(set)
    for key,group in groups.items():
        compositions[key[:-1]].add(frozenset(r['posicao'] for r in group))
    if any(len(sets)>1 for sets in compositions.values()):
        raise ValueError('Composicao de H difere entre estudantes')
    out=[]
    for key,group in sorted(groups.items()):
        target=[r for r in group if r['posicao']==posicao]
        if len(target)!=1:raise ValueError('Bloco requerido ausente')
        h=target[0]; rest=[r for r in group if r['posicao']!=posicao]
        valid=bool(rest) and all(r['disponibilidade'] and r['participacao'] for r in rest)
        ns=sum(r['numerador'] for r in rest) if valid else None
        ds=sum(r['denominador'] for r in rest) if valid else None
        out.append(dict(aluno_local_id=h['aluno_local_id'],turma=h['turma'],
            ano_escolar=h['ano_escolar'],ano_avaliacao=h['ano_avaliacao'],ciclo=h['ciclo'],
            instrumento=_instrumento(dict(zip(CONTEXTO,key[:-1]))),
            x=h['numerador']/h['denominador'] if h['disponibilidade'] and h['participacao'] else None,
            y=ns/ds if valid else None,acertos_restantes=ns,oportunidades_restantes=ds,
            blocos_restantes=len(rest),cobertura_completa=valid))
    return out


def auditar_pares(pares: list[dict], referencia: list[dict]) -> dict:
    """T38: compara conteúdo completo a referência fornecida por rota independente."""
    if Counter(map(_serial,pares))!=Counter(map(_serial,referencia)):
        raise ValueError('Conteudo ou cobertura dos pares diverge da referencia')
    return dict(pares_conferidos=len(pares))


def _turma(value):
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',value) if not unicodedata.combining(c)).upper().split())


def preparar_analises(tables: dict, *, config: dict | None=None) -> list[dict]:
    """Plano completo, independente de p; saída individual exclusivamente restrita.

    Ausência de instrumento num ano mantém hipóteses planejadas com N=0.
    Versões distintas no mesmo ano/componente são recusadas para revisão.
    """
    cfg=configuracao() if config is None else config
    evaluations=tables['avaliacoes']
    index={}; by_context=defaultdict(dict); declarations={}; instruments=defaultdict(set)
    for av in evaluations:
        context=(av['ano_escolar'],av['ano_avaliacao'],av['ciclo'])
        key=context+(av['aluno_local_id'],av['componente'])
        if key in index or av['avaliacao_local_id'] in declarations:
            raise ValueError('Avaliacao duplicada no pareamento')
        index[key]=av; declarations[av['avaliacao_local_id']]=av
        class_name=_turma(av['turma'])
        students=by_context[context]
        if av['aluno_local_id'] in students and students[av['aluno_local_id']]!=class_name:
            raise ValueError('Turma diverge entre componentes')
        students[av['aluno_local_id']]=class_name
        instruments[context+(av['componente'],)].add(tuple(av[k] for k in CONTEXTO))
    if any(len(v)!=1 for v in instruments.values()):
        raise ValueError('Mais de uma versao de instrumento no contexto')
    measures={}; denominators=defaultdict(set)
    for table in ('escrita','fluencia'):
        for row in tables[table]:
            av=declarations.get(row['avaliacao_local_id'])
            if av is None or any(row[k]!=av[k] for k in (*CONTEXTO,'aluno_local_id','participacao')):
                raise ValueError('Vinculo de medida diverge')
            key=(row['avaliacao_local_id'],row['campo_original'])
            if key in measures:raise ValueError('Medida duplicada')
            measures[key]=row
            if row['disponibilidade'] and row.get('denominador') is not None:
                denominators[tuple(row[k] for k in CONTEXTO)+(row['campo_original'],)].add(row['denominador'])
    if any(len(ds)>1 for ds in denominators.values()):
        raise ValueError('Contagens com denominadores incompativeis')
    plan=[]
    for context,students in sorted(by_context.items()):
        year,assessment,cycle=context
        for vx,vy in combinations(cfg['variaveis'],2):
            if vx['componente']==vy['componente']:continue
            inst={v['componente']:sorted(instruments.get(context+(v['componente'],),set())) for v in (vx,vy)}
            iid=_instrumento(inst)
            pairs=[]
            for student,class_name in sorted(students.items()):
                row=dict(aluno_local_id=student,turma=class_name,ano_escolar=year,
                    ano_avaliacao=assessment,ciclo=cycle,instrumento=iid)
                for axis,var in (('x',vx),('y',vy)):
                    av=index.get(context+(student,var['componente']))
                    value=None
                    if av and av['participacao']:
                        if var['tabela']=='avaliacoes':value=av[var['campo']]
                        else:
                            measure=measures.get((av['avaliacao_local_id'],var['campo_original']))
                            if measure and measure['disponibilidade']:
                                unit=measure.get('percentual_unidade') if var['campo']=='percentual' else measure['unidade']
                                if unit!=var['unidade']:raise ValueError('Escala da medida diverge do plano')
                                value=measure[var['campo']]
                    row[axis]=value
                pairs.append(row)
            plan.append(dict(tipo='intercomponentes',ano_escolar=year,ano_avaliacao=assessment,ciclo=cycle,
                familia=f'inter:{year}:{assessment}:{cycle}',instrumento=iid,x=vx['nome'],y=vy['nome'],
                unidade_x=vx['unidade'],unidade_y=vy['unidade'],pares=pairs,
                selecao_texto='texto' in vx['nome'] or 'texto' in vy['nome'] or 'compreensao' in vx['nome'] or 'compreensao' in vy['nome']))
    hgroups=defaultdict(list)
    for row in tables['habilidades']:
        av=declarations.get(row['avaliacao_local_id'])
        if av is None or any(row[k]!=av[k] for k in (*CONTEXTO,'aluno_local_id','participacao')):
            raise ValueError('Vinculo de H diverge')
        hgroups[tuple(row[k] for k in CONTEXTO)].append(row|dict(turma=_turma(av['turma'])))
    for context,rows in sorted(hgroups.items()):
        ctx=dict(zip(CONTEXTO,context)); iid=_instrumento(ctx)
        for position in sorted({r['posicao'] for r in rows}):
            plan.append(dict(tipo='H_total_corrigido',ano_escolar=ctx['ano_escolar'],ano_avaliacao=ctx['ano_avaliacao'],
                ciclo=ctx['ciclo'],familia='H:'+iid,instrumento=iid,componente=ctx['componente'],
                x=position,y='total_sem_bloco',unidade_x='fracao_acertos_itens',unidade_y='fracao_acertos_itens',
                pares=total_sem_bloco(rows,position),selecao_texto=False))
    return plan
