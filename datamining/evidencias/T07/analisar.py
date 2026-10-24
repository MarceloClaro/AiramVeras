"""Execução real T07. Identificadores e matrizes individuais só em restrito/."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.grafo import construir_bipartida, propagar, matrizes_evidencia
from airam.agregacoes import agregar_observacoes
from airam.metricas import CONTEXTO

EXPECTED = {'curriculo/t04/checkpoint.json':'a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796',
            'restrito/t05/checkpoint.json':'6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b'}


def clean(obj):
    if isinstance(obj,np.ndarray):
        return clean(obj.tolist())
    if isinstance(obj,dict):
        return {k:clean(v) for k,v in obj.items()}
    if isinstance(obj,(tuple,list)):
        return [clean(v) for v in obj]
    if isinstance(obj,float) and not np.isfinite(obj):
        return None
    return obj


def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    raw = (json.dumps(clean(obj),ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode('utf-8')
    if path.exists() and path.read_bytes() != raw:
        raise ValueError('Checkpoint anterior diferente: preservar antes de substituir')
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def main():
    for p,h in EXPECTED.items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest() != h:
            raise ValueError('Entrada autenticada divergente')
    curriculum = json.loads((ROOT/'curriculo/t04/checkpoint.json').read_text(encoding='utf-8'))
    source = json.loads((ROOT/'restrito/t05/checkpoint.json').read_text(encoding='utf-8'))['observado']
    applications = {r['avaliacao_local_id']:r for r in source['avaliacoes']}
    if len(applications) != len(source['avaliacoes']):
        raise ValueError('Aplicacoes duplicadas')
    fields = (*CONTEXTO,'aluno_local_id','avaliacao_local_id','posicao','numerador','denominador',
              'participacao','disponibilidade','unidade')
    rows = []
    for original in source['habilidades']:
        row = {k:original[k] for k in fields}
        app = applications[row['avaliacao_local_id']]
        if any(row[k] != app[k] for k in (*CONTEXTO,'aluno_local_id','participacao')):
            raise ValueError('Join de aplicacao divergente')
        row['turma'] = app['turma']
        rows.append(row)
    contexts = defaultdict(list)
    for r in rows:
        contexts[tuple(r[k] for k in CONTEXTO)].append(r)
    restricted = dict(versao_schema='airam-grafo-restrito-t07-v1',fontes=EXPECTED,blocos=[],visoes_aluno=[])
    public = dict(versao_schema='airam-grafo-t07-v1',fontes=EXPECTED,blocos=[],visoes=[],
        politica=dict(universo='instrumento_mesmo_ano_componente_edicao_ciclo',
            B='uma unidade por ocorrencia elegivel dividida entre BNCC distintas',
            A='B B^T, diagonal zero, normalizacao por linha nao nula',
            propagacao='(M P) (A^s)^T / (M (A^s)^T), s=1,2; mascara original',
            autorretorno='incluido e quantificado; sensibilidade retira diagonal de A^s sem renormalizar kernel',
            contagens='C,D originais por posicao; C_alocada,D_alocada sao massas, nao novos itens',
            limites='associacao curricular exploratoria; sem GCN treinada, dominio BNCC ou previsao validada',
            grupos='regras operacionais sobrepostas, nao clusters ou rotulos de capacidade'))
    restricted['visoes_aluno'] = agregar_observacoes(rows,'aluno')
    public['visoes'] = agregar_observacoes(rows,'turma') + agregar_observacoes(rows,'escola')
    for context, subset in sorted(contexts.items(),key=lambda kv:str(kv[0])):
        ctx = dict(zip(CONTEXTO,context))
        candidates = [v for v in curriculum['vinculos_posicoes'] if
            all(v[a] == ctx[b] for a,b in [('avaliacao_id','avaliacao_id'),('ano_avaliacao','ano_avaliacao'),
                ('ano_avaliado','ano_escolar'),('ciclo_avaliado','ciclo'),('componente','componente')])]
        positions = sorted({r['posicao'] for r in subset})
        if positions != sorted({v['posicao'] for v in candidates}):
            raise ValueError('Cobertura de posicoes diverge da fonte curricular')
        totals = agregar_observacoes(subset,'aluno')
        groups = [dict(grupo_id='evidencia_completa',membros=[r['aluno_local_id'] for r in totals if
                       r['taxa'] is not None and r['ausentes']==0]),
                  dict(grupo_id='abaixo_meta_B_observada',membros=[r['aluno_local_id'] for r in totals if
                       r['taxa'] is not None and r['acertos']*5 < r['oportunidades']*4])]
        public['visoes'].extend(agregar_observacoes(subset,'grupo',groups))
        for policy in ('estrita','ressalvada'):
            graph = construir_bipartida(candidates,policy)
            matrix = matrizes_evidencia(subset,positions,graph)
            propagation = {str(s):propagar(matrix['P_ocorrencias'],matrix['mask_ocorrencias'],graph['A'],s) for s in (1,2)}
            restricted['blocos'].append(dict(contexto=ctx,policy=policy,matrizes=matrix,
                                            propagacoes=propagation,grupos=groups))
            summaries = {}
            for step,result in propagation.items():
                supported = np.isfinite(result['propagado'])
                no_return = np.isfinite(result['sem_retorno'])
                summaries[step] = dict(celulas_suportadas=int(supported.sum()),
                    celulas_suportadas_sem_retorno=int(no_return.sum()),
                    celulas_com_retorno=int((result['massa_retorno']>0).sum()),
                    soma_massa_retorno=float(result['massa_retorno'].sum()),
                    fontes_por_no=result['fontes_distintas'].sum(axis=0),
                    alunos_com_suporte_por_no=supported.sum(axis=0),
                    alunos_com_suporte_sem_retorno_por_no=no_return.sum(axis=0))
            public['blocos'].append(dict(contexto=ctx,policy=policy,grafo=graph,
                posicoes=positions,alunos_cadastrados=len(matrix['alunos']),
                celulas_observadas=int(matrix['observado_mask'].sum()),
                celulas_ausentes=int((~matrix['observado_mask']).sum()),
                posicoes_associadas=len(graph['posicoes_ocorrencias']),
                propagacoes=summaries))
    protected_hash = write(ROOT/'restrito/t07/checkpoint.json',restricted)
    public['checkpoint_restrito_sha256'] = protected_hash
    public_hash = write(ROOT/'estatistica/t07/checkpoint.json',public)
    print(json.dumps(dict(status='analise_real_concluida',contextos=len(contexts),politicas=2,
        observacoes=len(rows),blocos=len(public['blocos']),checkpoint_restrito_sha256=protected_hash,
        checkpoint_agregado_sha256=public_hash)))


if __name__ == '__main__':
    main()
