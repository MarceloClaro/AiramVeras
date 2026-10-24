"""Associação curricular exploratória por instrumento; não é modelo treinado."""
from collections import defaultdict
import json
import numpy as np

CONTEXTO_VINCULO = ('avaliacao_id','ano_avaliacao','ano_avaliado','ciclo_avaliado',
                    'componente','fonte_posicao','versao_posicao')


def construir_bipartida(vinculos: list[dict], policy: str) -> dict:
    """Uma unidade por ocorrência elegível, dividida entre BNCC distintas.

    Aceita um instrumento apenas. Fonte/versão integram as identidades; candidatos
    ficam como nós sem massa, sem transferir resultados de outros anos ou ciclos.
    Duplicatas idênticas são idempotentes; divergentes são recusadas.
    """
    if policy not in ('estrita','ressalvada'):
        raise ValueError('Politica curricular invalida')
    contexts, unique, node_meta, bncc_meta = set(), {}, {}, {}
    for r in vinculos:
        try:
            context = tuple(r[k] for k in CONTEXTO_VINCULO)
            node = (r['fonte_matriz'],r['sha256_pdf'],r['ocorrencia_id'])
            provenance = (r.get('bncc') or {}).get('proveniencia_dataset', {})
            skill = (provenance.get('documento'),provenance.get('commit'),r['codigo_bncc'])
            key = (r['posicao_id'],node,skill)
            weight = r['peso_analitico']
            if isinstance(weight,bool) or not isinstance(weight,(float,int)) or not np.isfinite(weight) or weight < 0:
                raise ValueError('Peso invalido')
        except (KeyError,TypeError):
            raise ValueError('Vinculo sem contexto obrigatorio') from None
        contexts.add(context)
        canonical = json.dumps(r,sort_keys=True,ensure_ascii=False)
        if key in unique and unique[key][0] != canonical:
            raise ValueError('Vinculo duplicado divergente')
        unique[key] = (canonical,r)
        if r['ocorrencia_id'] is not None:
            node_meta[node] = {'fonte_matriz':node[0],'sha256_pdf':node[1],'ocorrencia_id':node[2]}
        if r['codigo_bncc'] is not None:
            bncc_meta[skill] = {'documento':skill[0],'commit':skill[1],'codigo_bncc':skill[2]}
    if len(contexts) > 1:
        raise ValueError('Instrumentos distintos nao podem compartilhar grafo')
    nodes = sorted(node_meta, key=str)
    skills = sorted(bncc_meta, key=str)
    ni, si = {n:i for i,n in enumerate(nodes)}, {s:i for i,s in enumerate(skills)}
    b = np.zeros((len(nodes),len(skills)))
    eligible, associations = set(), defaultdict(set)
    for (_,node,skill), (_,r) in unique.items():
        ok = (r['peso_analitico'] > 0 and r['status_contextual'] == 'proprio_ano_ciclo_confirmado'
              and r['status_bncc'] == 'confirmado' and node in ni and skill in si)
        if policy == 'estrita' and r['status_semantico'] == 'associacao_publicada_com_ressalva_semantica':
            ok = False
        if ok:
            eligible.add((ni[node],si[skill]))
            associations[r['posicao']].add(ni[node])
    for i,j in eligible:
        b[i,j] = 1
    total = b.sum(axis=1,keepdims=True)
    np.divide(b,total,out=b,where=total>0)
    w = b @ b.T
    shared = w.copy()
    np.fill_diagonal(shared,0)
    degree_mass = shared.sum(axis=1)
    a = np.divide(shared,degree_mass[:,None],out=np.zeros_like(shared),where=degree_mass[:,None]>0)
    return dict(policy=policy, contexto=dict(zip(CONTEXTO_VINCULO,next(iter(contexts),()))),
        nos=[node_meta[n] for n in nodes], bncc=[bncc_meta[s] for s in skills],
        B=b,W=w,A=a,graus=(shared>0).sum(axis=1),massa_grau=degree_mass,
        posicoes_ocorrencias={p:sorted(v) for p,v in sorted(associations.items())},
        vinculos_distintos=len(unique),arestas_elegiveis=len(eligible))


def propagar(observado: np.ndarray, observado_mask: np.ndarray,
             adjacency: np.ndarray, passos: int) -> dict:
    """P' = (MP)(A^s)^T / M(A^s)^T. A máscara permanece a original.

    Cobertura é massa de grafo observada, não quantidade de itens. Autorretorno
    de A² é reportado e removido em uma sensibilidade separada, sem novo ajuste.
    """
    p = np.asarray(observado,dtype=float)
    m = np.asarray(observado_mask)
    a = np.asarray(adjacency,dtype=float)
    if type(passos) is not int or passos not in (1,2):
        raise ValueError('Passos devem ser um ou dois')
    if p.ndim != 2 or m.shape != p.shape or m.dtype != bool or a.shape != (p.shape[1],p.shape[1]):
        raise ValueError('Dimensoes ou mascara invalidas')
    if not np.isfinite(a).all() or (a<0).any() or np.any(np.diag(a)!=0):
        raise ValueError('Adjacencia deve ser nao negativa e sem autolacos')
    sums = a.sum(axis=1)
    if not np.all(np.isclose(sums,1) | (sums==0)):
        raise ValueError('Adjacencia deve ter linhas normalizadas ou nulas')
    if not np.isfinite(p[m]).all() or np.any((p[m]<0)|(p[m]>1)) or np.any(np.isfinite(p[~m])):
        raise ValueError('Observado e mascara inconsistentes')
    kernel = a.copy() if passos == 1 else a @ a
    values = np.where(m,p,0)
    mass = m.astype(float) @ kernel.T
    numerator = values @ kernel.T
    out = np.divide(numerator,mass,out=np.full_like(p,np.nan),where=mass>0)
    no_return = kernel.copy()
    np.fill_diagonal(no_return,0)
    mass_no_return = m.astype(float) @ no_return.T
    without = np.divide(values @ no_return.T,mass_no_return,out=np.full_like(p,np.nan),where=mass_no_return>0)
    return dict(observado=p.copy(),observado_mask=m.copy(),propagado=out,cobertura=mass,
        fontes_distintas=m.astype(int) @ (kernel>0).T.astype(int),passos=passos,
        kernel=kernel,massa_retorno=m*np.diag(kernel)[None,:],sem_retorno=without,
        cobertura_sem_retorno=mass_no_return)


def matrizes_evidencia(rows: list[dict], posicoes: list[str], grafo: dict) -> dict:
    """Conserva C/D por posição e aloca massa a ocorrências sem fanout.

    Cada posição reparte uma unidade entre ocorrências elegíveis distintas.
    C_alocada/D_alocada são massas fracionáveis, nunca novas contagens de itens.
    """
    if len(posicoes) != len(set(posicoes)):
        raise ValueError('Posicoes duplicadas')
    students = sorted({r['aluno_local_id'] for r in rows})
    student_index = {s:i for i,s in enumerate(students)}
    pi = {p:i for i,p in enumerate(posicoes)}
    c = np.full((len(students),len(posicoes)),np.nan)
    d = c.copy()
    seen = set()
    for r in rows:
        if r['posicao'] not in pi:
            raise ValueError('Posicao fora do instrumento')
        key = (student_index[r['aluno_local_id']],pi[r['posicao']])
        if key in seen:
            raise ValueError('Observacao duplicada')
        seen.add(key)
        n,den = r['numerador'],r['denominador']
        if type(r['participacao']) is not bool or type(r['disponibilidade']) is not bool:
            raise ValueError('Mascara invalida')
        if r['disponibilidade']:
            if not r['participacao'] or type(n) is not int or type(den) is not int or not 0 <= n <= den or den<=0:
                raise ValueError('Contagens invalidas')
            c[key],d[key] = n,den
        elif n is not None or den is not None:
            raise ValueError('Ausencia com contagem')
    mask = np.isfinite(c)
    p = np.divide(c,d)
    q = np.zeros((len(posicoes),len(grafo['nos'])))
    for position,nodes in grafo['posicoes_ocorrencias'].items():
        if position not in pi:
            raise ValueError('Grafo fora do instrumento')
        q[pi[position],nodes] = 1/len(nodes)
    allocated_c = np.nan_to_num(c) @ q
    allocated_d = np.nan_to_num(d) @ q
    mask_nodes = allocated_d>0
    p_nodes = np.divide(allocated_c,allocated_d,out=np.full_like(allocated_c,np.nan),where=mask_nodes)
    return dict(alunos=students,posicoes=posicoes,C=c,D=d,P=p,observado_mask=mask,
        Q=q,C_alocada=allocated_c,D_alocada=allocated_d,P_ocorrencias=p_nodes,
        mask_ocorrencias=mask_nodes,cobertura_observada=mask.mean(axis=1) if posicoes else np.zeros(len(students)))
