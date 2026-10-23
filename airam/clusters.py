"""Agrupamentos exploratórios locais; identificadores de retorno são restritos."""
from collections import Counter
from copy import deepcopy
import hashlib
import json
import warnings

import numpy as np
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans
from sklearn.exceptions import ConvergenceWarning
from sklearn.metrics import adjusted_rand_score, silhouette_samples
from threadpoolctl import ThreadpoolController

_THREADPOOLS = ThreadpoolController()


def resumo(values):
    """Distribuição sem inventar zero para estatística ausente."""
    x = np.asarray(values, dtype=float)
    x = x[np.isfinite(x)]
    if not len(x):
        return dict(n=0, minimo=None, p10=None, mediana=None, media=None, maximo=None)
    return dict(n=len(x), minimo=float(x.min()), p10=float(np.quantile(x,.1,method='linear')),
                mediana=float(np.median(x)), media=float(x.mean()), maximo=float(x.max()))


def _hash(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(',',':'),ensure_ascii=False,
                                      allow_nan=False).encode()).hexdigest()


def _fit(x,k,seed,config,n_init=1):
    if len(np.unique(x,axis=0)) < k or len(x)<=k:
        return None,'perfis_insuficientes'
    with warnings.catch_warnings(record=True) as caught, _THREADPOOLS.limit(limits=1):
        warnings.simplefilter('always',ConvergenceWarning)
        fit=KMeans(n_clusters=k,random_state=seed,n_init=n_init,algorithm='lloyd',
                   max_iter=config['max_iter'],tol=config['tol']).fit(x)
    if caught or len(np.unique(fit.labels_))!=k:
        return None,'colapso'
    if fit.n_iter_>=config['max_iter']:
        return None,'limite_iteracoes'
    order=sorted(range(k),key=lambda label:tuple(fit.cluster_centers_[label]))
    mapping={old:new for new,old in enumerate(order)}
    labels=np.array([mapping[int(v)] for v in fit.labels_])
    return dict(labels=labels,inercia=float(fit.inertia_),seed=int(seed),
                iteracoes=int(fit.n_iter_),centroides=fit.cluster_centers_[order].tolist()),None


def _match(reference,other,k):
    """Correspondência um-a-um; grupos com suporte <2 não são avaliáveis."""
    eligible=[i for i in range(k) if int((reference==i).sum())>=2]
    out={i:None for i in range(k)}
    if not eligible:
        return out
    score=np.zeros((len(eligible),k))
    for a,i in enumerate(eligible):
        for j in range(k):
            score[a,j]=np.sum((reference==i)&(other==j))/np.sum((reference==i)|(other==j))
    rows,cols=linear_sum_assignment(-score)
    for a,j in zip(rows,cols):
        i=eligible[a]
        overlap=int(np.sum((reference==i)&(other==j)))
        out[i]=dict(jaccard=float(score[a,j]),retencao=overlap/int((reference==i).sum()),
                    intrusos=int(np.sum((reference!=i)&(other==j))),
                    tamanho_correspondente=int((other==j).sum()))
    return out


def _group_summary(matches,i,planned):
    valid=[m[i] for m in matches if m[i] is not None]
    return dict(planejadas=planned,avaliaveis=len(valid),sem_suporte=sum(m[i] is None for m in matches),
                ajustes_invalidos=planned-len(matches),jaccard=resumo([m['jaccard'] for m in valid]),
                retencao=resumo([m['retencao'] for m in valid]),
                intrusos=resumo([m['intrusos'] for m in valid]),
                tamanho_correspondente=resumo([m['tamanho_correspondente'] for m in valid]),
                dissolucoes=sum(m['jaccard']==0 for m in valid))


def avaliar_candidato(candidate,config):
    """Gate operacional reutilizável em sensibilidades, sem reajustar modelos."""
    if candidate.get('referencia') is None:
        return ['sem_referencia']
    thresholds=config['limiares']; failures=[]
    if min(candidate['tamanhos'])<config['min_grupo']:
        failures.append('tamanho_original')
    for name in ('seeds','subamostras'):
        item=candidate[name]
        if item['validas']/item['planejadas'] < thresholds['fracao_validas']:
            failures.append('ajustes_'+name)
        d=item['ari']
        if d['n']==0 or d['mediana']<thresholds['ari_mediana'] or d['p10']<thresholds['ari_p10']:
            failures.append('ari_'+name)
    if candidate['separacao']['media']<=thresholds['silhueta_media']:
        failures.append('separacao_global')
    for g in candidate['por_grupo']:
        for name in ('seeds','subamostras'):
            item=g[name]; d=item['jaccard']
            if (item['avaliaveis']/item['planejadas']<thresholds['suporte_grupo'] or d['n']==0
                    or d['mediana']<thresholds['jaccard_mediana'] or d['p10']<thresholds['jaccard_p10']):
                failures.append('estabilidade_grupo')
        if (g['silhueta']['mediana']<thresholds['silhueta_mediana_grupo'] or
                g['fracao_silhueta_negativa']>thresholds['fracao_negativa_grupo']):
            failures.append('separacao_grupo')
    return sorted(set(failures))


def _candidate(x,k,config,seed):
    originals=[]; failures=Counter()
    for initial in config['seeds']:
        fit,reason=_fit(x,k,initial,config)
        if fit is None: failures[reason]+=1
        else: originals.append(fit)
    base=dict(k=k,referencia=None,seeds=dict(planejadas=len(config['seeds']),validas=len(originals),
        falhas=dict(failures),ari=resumo([])),subamostras=dict(planejadas=config['subamostras'],
        validas=0,falhas={},ari=resumo([]),tamanho=int(np.floor(len(x)*config['fracao_subamostra'])),
        minimos_tamanhos=[]),por_grupo=[],tamanhos=[],separacao=resumo([]))
    if not originals:
        base['subamostras']['falhas']={'sem_referencia':config['subamostras']}
        base.update(reprovacoes=['sem_referencia'],liberado=False)
        return base
    aris=np.eye(len(originals))
    pairs=[]
    for i in range(len(originals)):
        for j in range(i):
            value=float(adjusted_rand_score(originals[i]['labels'],originals[j]['labels']))
            aris[i,j]=aris[j,i]=value; pairs.append(value)
    idx=min(range(len(originals)),key=lambda i:(-aris[i].mean(),originals[i]['inercia'],originals[i]['seed']))
    ref=originals[idx]; labels=ref['labels']
    base['referencia']={key:value for key,value in ref.items() if key!='labels'}
    base['rotulos']=labels.tolist()
    base['tamanhos']=[int((labels==i).sum()) for i in range(k)]
    base['seeds'].update(ari=resumo(pairs),minimos_tamanhos=[int(np.bincount(v['labels'],minlength=k).min()) for v in originals],
                         execucoes=[dict(seed=v['seed'],iteracoes=v['iteracoes'],inercia=v['inercia']) for v in originals])
    silhouette=silhouette_samples(x,labels)
    base['separacao']=resumo(silhouette)
    seed_matches=[_match(labels,v['labels'],k) for v in originals]
    sample_matches=[]; sample_aris=[]; failed=Counter(); sample_hashes=[]
    rng=np.random.default_rng(seed)
    m=base['subamostras']['tamanho']
    for _ in range(config['subamostras']):
        sample=np.sort(rng.choice(len(x),size=m,replace=False))
        local_seed=int(rng.integers(0,2**31-1))
        sample_hashes.append(_hash(sample.tolist()))
        fit,reason=_fit(x[sample],k,local_seed,config,config['n_init_subamostra'])
        if fit is None:
            failed[reason]+=1; continue
        sample_aris.append(float(adjusted_rand_score(labels[sample],fit['labels'])))
        sample_matches.append(_match(labels[sample],fit['labels'],k))
        base['subamostras']['minimos_tamanhos'].append(int(np.bincount(fit['labels'],minlength=k).min()))
    base['subamostras'].update(validas=len(sample_aris),falhas=dict(failed),ari=resumo(sample_aris),
                                sorteios_sha256=_hash(sample_hashes))
    for i in range(k):
        base['por_grupo'].append(dict(grupo_id=f'cluster_{i+1}',n=int((labels==i).sum()),
            seeds=_group_summary(seed_matches,i,len(config['seeds'])),
            subamostras=_group_summary(sample_matches,i,config['subamostras']),
            silhueta=resumo(silhouette[labels==i]),fracao_silhueta_negativa=float((silhouette[labels==i]<0).mean())))
    base['reprovacoes']=avaliar_candidato(base,config)
    base['liberado']=not base['reprovacoes']
    return base


def agrupar(features:dict,config:dict,seed:int)->dict:
    """K=2..min(5,floor(N/5)); nenhum cluster é um resultado legítimo.

    Valores são proporções [0,1]; listas de alunos e membros nunca são públicas.
    Casos incompletos são excluídos com motivo, não imputados. Ordem canônica precede
    todo ajuste e sorteio. Contexto é transportado, nunca usado como feature.
    """
    students=features['alunos']; columns=features['colunas']
    x=np.asarray(features['valores'],dtype=float)
    if not students and x.size==0:
        x=x.reshape(0,len(columns))
    coverage=np.asarray(features['cobertura'],dtype=float)
    if (len(set(students))!=len(students) or len(set(columns))!=len(columns)
            or x.shape!=(len(students),len(columns)) or coverage.shape!=(len(students),)):
        raise ValueError('Eixos invalidos ou duplicados')
    if (np.isinf(x).any() or ((x[np.isfinite(x)]<0)|(x[np.isfinite(x)]>1)).any()
            or not np.isfinite(coverage).all() or ((coverage<0)|(coverage>1)).any()):
        raise ValueError('Proporcoes ou cobertura invalidas')
    if (len(config['seeds'])<2 or len(set(config['seeds']))!=len(config['seeds']) or
            config['subamostras']<1 or not 0<config['fracao_subamostra']<1 or config['min_grupo']<5):
        raise ValueError('Configuracao de estabilidade invalida')
    rows=sorted(range(len(students)),key=lambda i:students[i]); cols=sorted(range(len(columns)),key=lambda i:columns[i])
    x=x[np.ix_(rows,cols)]; coverage=coverage[rows]
    students=[students[i] for i in rows]; columns=[columns[i] for i in cols]
    valid=np.isfinite(x).all(axis=1)&(coverage>=config['cobertura_minima'])
    excluded=[dict(aluno_local_id=students[i],motivo='cobertura_insuficiente' if coverage[i]<config['cobertura_minima']
                    else 'matriz_incompleta') for i in range(len(students)) if not valid[i]]
    students=[v for v,ok in zip(students,valid) if ok]; x=x[valid]
    weights=np.asarray(features.get('pesos',[1]*len(columns)),dtype=float)[cols]
    if weights.shape!=(len(columns),) or not np.isfinite(weights).all() or (weights<=0).any():
        raise ValueError('Pesos invalidos')
    weighted=x*np.sqrt(weights)
    out=dict(versao='airam-clusters-t08-v1',contexto=deepcopy(features['contexto']),
        status='sem_agrupamento_estavel',motivo=None,k=None,grupos=[],alunos=students,colunas=columns,
        excluidos=excluded,cobertura=dict(cadastrados=len(rows),elegiveis=len(students),excluidos=len(excluded),
            distribuicao=resumo(coverage),corte=config['cobertura_minima']),
        colunas_constantes=[c for i,c in enumerate(columns) if len(x) and np.ptp(x[:,i])==0],
        criterios=deepcopy(config),seed=seed,candidatos=[],
        amplitude_por_coluna=[float(np.ptp(x[:,i])) if len(x) else None for i in range(len(columns))],
        geometria=dict(pesos=weights.tolist(),padronizacao=False,metrica='euclidiana'),
        eixos_sha256=_hash(dict(alunos=students,colunas=columns)))
    if len(students)<10 or not columns:
        out['motivo']='amostra_ou_colunas_insuficientes'; return out
    if len(np.unique(x,axis=0))<2:
        out['motivo']='perfis_sem_variacao'; return out
    for k in range(2,min(5,config['max_k'],len(x)//5)+1):
        out['candidatos'].append(_candidate(weighted,k,config,seed))
    approved=[c for c in out['candidatos'] if c['liberado']]
    if approved:
        selected=approved[0]; out.update(status='exploratorio_estavel',k=selected['k'])
        for i,g in enumerate(selected['por_grupo']):
            out['grupos'].append(dict(grupo_id=g['grupo_id'],tipo='cluster',n=g['n'],
                membros=[s for s,label in zip(students,selected['rotulos']) if label==i],
                criterio='particao medoide KMeans; todos controles globais e por grupo satisfeitos',
                estabilidade=deepcopy(g)))
    else:
        out['motivo']='criterios_nao_satisfeitos'
    return out


def preparar_bracos(bloco:dict,grafo:dict,config:dict,passos=1,sem_retorno=False,pesos=None)->dict:
    """Mesmos E/Fs; seleção estrutural anterior à busca de K. Não chama matriz T07."""
    m=bloco['matrizes']; p=np.asarray(m['P'],dtype=float); d=np.asarray(m['D'],dtype=float)
    q=np.asarray(m['Q'],dtype=float); a=np.asarray(grafo['A'],dtype=float)
    kernel=a if passos==1 else a@a
    if sem_retorno:
        kernel=kernel.copy(); np.fill_diagonal(kernel,0)
    field='sem_retorno' if sem_retorno else 'propagado'
    propagated=np.asarray(bloco['propagacoes'][str(passos)][field],dtype=float)
    predicted=np.full_like(p,np.nan); shared=[]
    for j in range(p.shape[1]):
        nodes=np.flatnonzero(q[j]>0)
        if len(nodes) and np.all(kernel[nodes].sum(axis=1)>0):
            shared.append(j)
            good=np.isfinite(propagated[:,nodes]).all(axis=1)
            predicted[good,j]=(propagated[np.ix_(good,nodes)]@q[j,nodes])/q[j,nodes].sum()
    expected=m.get('denominadores_previstos')
    if expected is None:
        expected=[float(np.nanmax(d[:,j])) if np.isfinite(d[:,j]).any() else 0 for j in range(d.shape[1])]
    expected=np.asarray(expected,dtype=float)
    coverage=np.nansum(d,axis=1)/expected.sum() if expected.sum()>0 else np.zeros(len(p))
    eligible=np.isfinite(p).all(axis=1)&(coverage>=config['cobertura_minima'])
    if shared: eligible &= np.isfinite(predicted[:,shared]).all(axis=1)
    out=dict(status='comparavel' if shared else 'comparacao_indisponivel',
        motivo=None if shared else 'sem_colunas_com_suporte_estrutural',bracos={},
        selecao=dict(cadastrados=len(p),casos_completos_observados=int(np.isfinite(p).all(axis=1).sum()),
            elegiveis=int(eligible.sum()) if shared else 0,features_total=p.shape[1],features_comuns=len(shared),
            cobertura=resumo(coverage),denominadores_previstos=expected.tolist()),
        passos=passos,sem_retorno=sem_retorno)
    if not shared: return out
    for name,values,cols in [('observado_total',p,list(range(p.shape[1]))),
                             ('observado_controle',p,shared),('propagado_controle',predicted,shared)]:
        out['bracos'][name]=dict(contexto=deepcopy(bloco['contexto']),
            alunos=[s for s,ok in zip(m['alunos'],eligible) if ok],colunas=[m['posicoes'][j] for j in cols],
            valores=values[np.ix_(eligible,cols)].tolist(),cobertura=coverage[eligible].tolist(),
            pesos=[pesos[j] for j in cols] if pesos is not None else [1]*len(cols))
    return out


def comparar_particoes(left,right):
    """Comparações por K fixo, inclusive candidatos reprovados explicitamente."""
    if left['alunos']!=right['alunos'] or left['contexto']!=right['contexto']:
        raise ValueError('Comparacao exige mesmos alunos/contexto')
    comparisons=[]
    for first in left['candidatos']:
        second=next((c for c in right['candidatos'] if c['k']==first['k']),None)
        if not second or 'rotulos' not in first or 'rotulos' not in second: continue
        a=np.asarray(first['rotulos']); b=np.asarray(second['rotulos']); k=first['k']
        transitions=[[int(np.sum((a==i)&(b==j))) for j in range(k)] for i in range(k)]
        changed=sum((a[i]==a[j]) != (b[i]==b[j]) for i in range(len(a)) for j in range(i))
        comparisons.append(dict(k=k,n=len(a),ari=float(adjusted_rand_score(a,b)),
            transicao=transitions,pares_coagrupamento_alterados=int(changed),
            liberado_esquerda=first['liberado'],liberado_direita=second['liberado'],
            interpretacao='descritivo; nao efeito causal nem superioridade pedagogica'))
    return comparisons
