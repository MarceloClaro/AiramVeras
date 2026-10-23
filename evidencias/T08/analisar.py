"""Handoff real T08; somente agregados no stdout e fora da área restrita."""
from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from sklearn.metrics import adjusted_rand_score

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.clusters import agrupar, preparar_bracos, comparar_particoes, avaliar_candidato, resumo
from airam.metricas import CONTEXTO
from airam.perfis_grupo import grupos_por_regras, descrever_grupos, perfis_publicos

EXPECTED={
    'restrito/t05/checkpoint.json':'6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b',
    'estatistica/t05/checkpoint.json':'5bfa87b38394d171589a7799751127dceb7d81587bbbfcefa67d2bb4a8420231',
    'restrito/t07/checkpoint.json':'17916019d8a8787c95ec3db580aae7987b11c5c93a72c34ad13846a7bf1bb8fe',
    'estatistica/t07/checkpoint.json':'71a0302d7ec9ae0f837069eea3b5c867052ff3885d5a9fb7491eee616abd9d58',
    'curriculo/t04/checkpoint.json':'a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()


def write(path,obj):
    raw=(json.dumps(obj,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists() and path.read_bytes()!=raw:
        raise ValueError('Checkpoint anterior diferente: preservar antes de substituir')
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def context_key(row):
    return tuple(row[k] for k in CONTEXTO)


def resultado_publico(result):
    allowed=('versao','contexto','status','motivo','k','cobertura','colunas','colunas_constantes',
             'seed','amplitude_por_coluna','geometria','eixos_sha256')
    out={k:deepcopy(result[k]) for k in allowed if k in result}
    out['grupos']=[{k:deepcopy(v) for k,v in g.items() if k!='membros'} for g in result['grupos']]
    out['candidatos']=[]
    for c in result.get('candidatos',[]):
        candidate={k:deepcopy(v) for k,v in c.items() if k!='rotulos'}
        if candidate['referencia'] and any(n<5 for n in candidate['tamanhos']):
            candidate['referencia']['centroides']=None
        candidate['por_grupo']=[g if g['n']>=5 else dict(grupo_id=g['grupo_id'],n_intervalo='1-4',
            status_publicacao='suprimido_n_menor_5') for g in candidate['por_grupo']]
        out['candidatos'].append(candidate)
    return out


def sensitivities(result,config):
    settings=[('min_grupo_'+str(n),dict(min_grupo=n)) for n in config['sensibilidade_min_grupo']]
    settings.extend((name,dict(limiares={**config['limiares'],**change}))
                    for name,change in config['sensibilidade_limiares'].items())
    results=[]
    for name,change in settings:
        local={**config,**change}
        candidates=[dict(k=c['k'],reprovacoes=avaliar_candidato(c,local)) for c in result['candidatos']]
        approved=[c['k'] for c in candidates if not c['reprovacoes']]
        results.append(dict(cenario=name,k=approved[0] if approved else None,
            mudou_selecao=(approved[0] if approved else None)!=result['k'],candidatos=candidates,
            metodo='reuso dos diagnosticos, sem novos ajustes'))
    return results


def compare_rules(result,rules):
    mapping={s:g['grupo_id'] for g in rules['grupos'] for s in g['membros']}
    order=sorted(set(mapping[s] for s in result['alunos']))
    y=[order.index(mapping[s]) for s in result['alunos']]
    output=[]
    for c in result['candidatos']:
        if 'rotulos' not in c: continue
        labels=c['rotulos']
        table=[[sum(a==i and b==j for a,b in zip(labels,y)) for j in range(len(order))] for i in range(c['k'])]
        output.append(dict(k=c['k'],n=len(y),grupos_regras=order,transicao=table,
            ari=float(adjusted_rand_score(labels,y)) if len(order)>1 else None,
            status='descritivo' if len(order)>1 else 'regra_unica_pouco_informativa'))
    return output


def _public_comparison(items):
    output=deepcopy(items)
    for item in output:
        item['transicao']=[[str(n) if n==0 or n>=5 else '1-4' for n in row] for row in item['transicao']]
        item['supressao']='celulas 1-4 preservadas somente no restrito'
    return output


def produzir(t05,t07,t07public,t04,config):
    source=t05['observado']; applications={r['avaliacao_local_id']:r for r in source['avaliacoes']}
    if len(applications)!=len(source['avaliacoes']): raise ValueError('Aplicacoes duplicadas')
    rows_by_context=defaultdict(list)
    fields=(*CONTEXTO,'aluno_local_id','posicao','numerador','denominador','disponibilidade',
            'participacao','unidade','campo_original')
    for table in ('habilidades','escrita','fluencia'):
        for raw in source[table]:
            app=applications[raw['avaliacao_local_id']]
            if any(raw[k]!=app[k] for k in (*CONTEXTO,'aluno_local_id','participacao')):
                raise ValueError('Join de aplicacao/contexto divergente')
            row={k:raw[k] for k in fields}
            row.update(turma=app['turma'],categoria=app['categoria'],valor=raw.get('valor'),
                       oportunidades_previstas=app['oportunidades'])
            rows_by_context[context_key(row)].append(row)
    graphs={(context_key(b['contexto']),b['policy']):b['grafo'] for b in t07public['blocos']}
    blocks={(context_key(b['contexto']),b['policy']):b for b in t07['blocos']}
    private=dict(versao_schema='airam-grupos-restrito-t08-v1',config=deepcopy(config),instrumentos=[],unidades_proprias=[])
    public=dict(versao_schema='airam-grupos-t08-v1',config=deepcopy(config),instrumentos=[],unidades_proprias=[])
    cache={}; fit_count=0

    def fit(features):
        nonlocal fit_count
        key=digest(features)
        if key not in cache:
            cache[key]=agrupar(features,config,config['seed']); fit_count+=1
        return deepcopy(cache[key])

    for key,rows in sorted(rows_by_context.items(),key=lambda kv:str(kv[0])):
        context=dict(zip(CONTEXTO,key))
        if context['componente'] not in ('LEITURA','MATEMATICA'):
            rules=grupos_por_regras(rows,config['cobertura_minima'])
            profiles=descrever_grupos(rules,rows,[])
            private['unidades_proprias'].append(dict(contexto=context,regras=rules,perfis=profiles))
            public['unidades_proprias'].append(dict(contexto=context,perfis=perfis_publicos(profiles),
                status='categorias_originais_sem_cluster_nem_mapeamento_BNCC',meta_B='nao_aplicavel'))
            continue
        block=deepcopy(blocks[key,'ressalvada']); matrix=block['matrizes']
        d=np.asarray(matrix['D'],dtype=float); p=np.asarray(matrix['P'],dtype=float)
        denominators=[]
        for j in range(d.shape[1]):
            observed=set(d[np.isfinite(d[:,j]),j].tolist())
            if len(observed)!=1: raise ValueError('Oportunidades de posicao nao constantes/documentadas')
            denominators.append(int(next(iter(observed))))
        expected=sum(denominators)
        if any(r['oportunidades_previstas'] not in (None,expected) for r in rows):
            raise ValueError('Composicao por posicao difere de total do instrumento')
        # A composição é a do instrumento auditado, inclusive para não participantes.
        for r in rows: r['oportunidades_previstas']=expected
        matrix['denominadores_previstos']=denominators
        coverage=np.nansum(d,axis=1)/expected
        rules=grupos_por_regras(rows,config['cobertura_minima'])
        profiles=descrever_grupos(rules,rows,t04['vinculos_posicoes'])
        observed=fit(dict(contexto=context,alunos=matrix['alunos'],colunas=matrix['posicoes'],
            valores=matrix['P'],cobertura=coverage.tolist(),pesos=[1]*len(denominators)))
        observed_profiles=descrever_grupos(observed,rows,t04['vinculos_posicoes'])
        item=dict(contexto=context,regras=rules,perfis_regras=profiles,observado_operacional=observed,
                  perfis_observado=observed_profiles,cenarios=[],sensibilidade_observado=sensitivities(observed,config))
        pub=dict(contexto=context,perfis_regras=perfis_publicos(profiles),
            observado_operacional=resultado_publico(observed),perfis_observado=perfis_publicos(observed_profiles),
            cenarios=[],sensibilidade_observado=sensitivities(observed,config),
            observado_versus_regras=_public_comparison(compare_rules(observed,rules)))
        for name in config['cenarios']:
            policy='estrita' if name.startswith('estrita') else 'ressalvada'
            steps=2 if 'passo2' in name else 1
            no_return='sem_retorno' in name
            weights=denominators if 'peso_oportunidades' in name else None
            local=deepcopy(blocks[key,policy]); local['matrizes']['denominadores_previstos']=denominators
            prepared=preparar_bracos(local,graphs[key,policy],config,steps,no_return,weights)
            outputs={arm:fit(f) for arm,f in prepared['bracos'].items()}
            comparisons=[]
            for left,right,purpose in [('observado_total','observado_controle','selecao_features'),
                                      ('observado_controle','propagado_controle','transformacao_curricular')]:
                if left in outputs:
                    for c in comparar_particoes(outputs[left],outputs[right]):
                        comparisons.append(dict(contraste=purpose,**c))
            arm_profiles={arm:descrever_grupos(result,rows,t04['vinculos_posicoes']) for arm,result in outputs.items()}
            cover_sensitivity=[]
            if name=='ressalvada_passo1':
                for cut in config['sensibilidade_cobertura']:
                    alternate=preparar_bracos(local,graphs[key,policy],{**config,'cobertura_minima':cut},steps,no_return,weights)
                    identical=digest(alternate['bracos'])==digest(prepared['bracos'])
                    # Caso diferente tem corte próprio; mesmos E/colunas reutilizam diagnóstico.
                    alternative_results=outputs if identical else {arm:agrupar(f,{**config,'cobertura_minima':cut},config['seed'])
                                                                  for arm,f in alternate['bracos'].items()}
                    cover_sensitivity.append(dict(corte=cut,selecao=alternate['selecao'],mesmos_eixos_e_valores=identical,
                        status=alternate['status'],bracos={arm:dict(status=r['status'],k=r['k'],eixos_sha256=r['eixos_sha256'])
                                                         for arm,r in alternative_results.items()}))
            sensitivity={arm:sensitivities(r,config) for arm,r in outputs.items()}
            propagation=local['propagacoes'][str(steps)]
            support_field='sem_retorno' if no_return else 'propagado'
            support=np.asarray(propagation[support_field],dtype=float)
            support_report=dict(celulas_com_suporte=int(np.isfinite(support).sum()),
                celulas_sem_suporte=int((~np.isfinite(support)).sum()),
                soma_massa_retorno=float(np.sum(propagation['massa_retorno'])),
                nota='massa de grafo nao e D; dois passos podem repetir o proprio valor; sensibilidade retira diagonal')
            common=dict(cenario=name,policy=policy,status=prepared['status'],motivo=prepared['motivo'],
                selecao=prepared['selecao'],propagacao=support_report,sensibilidade_limiares=sensitivity,
                sensibilidade_cobertura=cover_sensitivity)
            item['cenarios'].append(dict(**common,definicao_bracos=prepared['bracos'],resultados=outputs,
                comparacoes=comparisons,perfis=arm_profiles,
                versus_regras={arm:compare_rules(r,rules) for arm,r in outputs.items()}))
            pub['cenarios'].append(dict(**common,resultados={arm:resultado_publico(r) for arm,r in outputs.items()},
                comparacoes=_public_comparison(comparisons),perfis={arm:perfis_publicos(ps) for arm,ps in arm_profiles.items()},
                versus_regras={arm:_public_comparison(compare_rules(r,rules)) for arm,r in outputs.items()}))
        private['instrumentos'].append(item); public['instrumentos'].append(pub)
    public['execucao']=private['execucao']=dict(estimandos_distintos_ajustados=fit_count,
        cache='reuso somente quando contexto/alunos/colunas/valores/cobertura/pesos identicos',
        limites='descritivo local; sem validacao docente/externa; nenhum dado enviado a servico externo')
    return private,public


def main():
    for path,expected in EXPECTED.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=expected:
            raise ValueError('Checkpoint de entrada divergente')
    config=json.loads((ROOT/'config/agrupamentos.json').read_text(encoding='utf-8'))
    inputs=[json.loads((ROOT/path).read_text(encoding='utf-8')) for path in
        ['restrito/t05/checkpoint.json','restrito/t07/checkpoint.json','estatistica/t07/checkpoint.json','curriculo/t04/checkpoint.json']]
    private,public=produzir(*inputs,config)
    for obj in (private,public):
        obj['fontes']=EXPECTED
        obj['config_sha256']=hashlib.sha256((ROOT/'config/agrupamentos.json').read_bytes()).hexdigest()
    protected_hash=write(ROOT/'restrito/t08/checkpoint.json',private)
    public['checkpoint_restrito_sha256']=protected_hash
    public_hash=write(ROOT/'estatistica/t08/checkpoint.json',public)
    print(json.dumps(dict(status='analise_real_concluida',instrumentos=len(public['instrumentos']),
        unidades_proprias=len(public['unidades_proprias']),checkpoint_restrito_sha256=protected_hash,
        checkpoint_agregado_sha256=public_hash,estimandos_ajustados=public['execucao']['estimandos_distintos_ajustados'])))


if __name__=='__main__':
    main()
