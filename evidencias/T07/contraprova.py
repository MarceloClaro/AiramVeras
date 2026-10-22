"""Rota independente: Fraction e laços, sem importar airam/numpy.

Reconstrói B/A por conjuntos documentais e todos os valores por caminhos de
comprimento 1/2 a partir das contagens T05. Falhas nunca imprimem dados pessoais.
"""
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def same(actual,expected):
    if expected is None:
        assert actual is None, 'Ausencia divergente'
    else:
        assert actual is not None and math.isclose(actual,float(expected),rel_tol=1e-12,abs_tol=1e-12), 'Valor divergente'


def main():
    paths = ['curriculo/t04/checkpoint.json','restrito/t05/checkpoint.json',
             'restrito/t07/checkpoint.json','estatistica/t07/checkpoint.json']
    hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    assert hashes[paths[0]] == 'a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796'
    assert hashes[paths[1]] == '6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b'
    curricular,t05,protected,public = [json.loads((ROOT/p).read_text(encoding='utf-8')) for p in paths]
    count = 0
    for block,pub in zip(protected['blocos'],public['blocos'],strict=True):
        ctx,policy = block['contexto'],block['policy']
        assert ctx == pub['contexto'] and policy == pub['policy']
        rows = [r for r in t05['observado']['habilidades'] if all(r[k]==v for k,v in ctx.items())]
        source = [r for r in curricular['vinculos_posicoes'] if r['avaliacao_id']==ctx['avaliacao_id']
            and r['ano_avaliacao']==ctx['ano_avaliacao'] and r['ciclo_avaliado']==ctx['ciclo']
            and r['ano_avaliado']==ctx['ano_escolar'] and r['componente']==ctx['componente']]
        nodes = [n['ocorrencia_id'] for n in pub['grafo']['nos']]
        skills = [n['codigo_bncc'] for n in pub['grafo']['bncc']]
        sets,positions = defaultdict(set),defaultdict(set)
        for r in source:
            if r['peso_analitico']<=0 or r['status_contextual']!='proprio_ano_ciclo_confirmado' or r['status_bncc']!='confirmado':
                continue
            if policy=='estrita' and r['status_semantico']=='associacao_publicada_com_ressalva_semantica':
                continue
            sets[r['ocorrencia_id']].add(r['codigo_bncc'])
            positions[r['posicao']].add(r['ocorrencia_id'])
        b = [[F(1,len(sets[n])) if s in sets[n] else F(0) for s in skills] for n in nodes]
        w = [[sum((x*y for x,y in zip(b[i],b[j])),F(0)) for j in range(len(nodes))] for i in range(len(nodes))]
        a = []
        for i,r in enumerate(w):
            den = sum(v for j,v in enumerate(r) if i!=j)
            a.append([v/den if den and i!=j else F(0) for j,v in enumerate(r)])
        for field,expected in [('B',b),('W',w),('A',a)]:
            for actualrow,expectedrow in zip(pub['grafo'][field],expected,strict=True):
                for actual,exp in zip(actualrow,expectedrow,strict=True):
                    same(actual,exp)
                    count += 1
        matrix = block['matrizes']
        by_student = defaultdict(dict)
        for r in rows:
            assert r['posicao'] not in by_student[r['aluno_local_id']], 'Observacao repetida na origem'
            by_student[r['aluno_local_id']][r['posicao']] = r
        assert len(by_student)==len(matrix['alunos'])
        for si,student in enumerate(matrix['alunos']):
            original = by_student[student]
            allocated_c = [F(0) for _ in nodes]
            allocated_d = [F(0) for _ in nodes]
            for pi,position in enumerate(matrix['posicoes']):
                r = original[position]
                valid = r['disponibilidade'] and r['participacao']
                same(matrix['C'][si][pi],r['numerador'] if valid else None)
                same(matrix['D'][si][pi],r['denominador'] if valid else None)
                same(matrix['P'][si][pi],F(r['numerador'],r['denominador']) if valid else None)
                assert matrix['observado_mask'][si][pi] == valid
                for node in positions[position]:
                    if valid:
                        k = nodes.index(node)
                        allocated_c[k] += F(r['numerador'],len(positions[position]))
                        allocated_d[k] += F(r['denominador'],len(positions[position]))
            p = [c/d if d else None for c,d in zip(allocated_c,allocated_d)]
            for j,v in enumerate(p):
                same(matrix['P_ocorrencias'][si][j],v)
                same(matrix['C_alocada'][si][j],allocated_c[j])
                same(matrix['D_alocada'][si][j],allocated_d[j])
            for step in (1,2):
                kernel = a if step==1 else [[sum((a[j][k]*a[k][l] for k in range(len(nodes))),F(0))
                                             for l in range(len(nodes))] for j in range(len(nodes))]
                result = block['propagacoes'][str(step)]
                for j in range(len(nodes)):
                    mass = sum((kernel[j][k] for k in range(len(nodes)) if p[k] is not None),F(0))
                    num = sum((kernel[j][k]*p[k] for k in range(len(nodes)) if p[k] is not None),F(0))
                    ret = kernel[j][j] if p[j] is not None else F(0)
                    without = mass-ret
                    same(result['propagado'][si][j],num/mass if mass else None)
                    same(result['cobertura'][si][j],mass)
                    same(result['massa_retorno'][si][j],ret)
                    same(result['sem_retorno'][si][j],(num-ret*p[j])/without if without and ret else (num/without if without else None))
                    same(result['cobertura_sem_retorno'][si][j],without)
                    assert result['fontes_distintas'][si][j]==sum(kernel[j][k]>0 and p[k] is not None for k in range(len(nodes)))
                    count += 6
        if ctx['ano_escolar']==1 and ctx['componente']=='MATEMATICA':
            assert not any(any(r) for r in a)
            assert all(v is None for result in block['propagacoes'].values() for r in result['propagado'] for v in r)
    applications = {a['avaliacao_local_id']:a for a in t05['observado']['avaliacoes']}
    for view in public['visoes']+protected['visoes_aluno']:
        subset = [r for r in t05['observado']['habilidades'] if all(r[k]==view[k] for k in
            ['avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente','fonte_id','sha256','exportacao'])]
        if view['nivel']=='aluno':
            subset = [r for r in subset if r['aluno_local_id']==view['aluno_local_id']]
        elif view['nivel']=='turma':
            subset = [r for r in subset if applications[r['avaliacao_local_id']]['turma']==view['turma']]
        elif view['nivel']=='grupo':
            by_id = defaultdict(list)
            for r in subset:
                by_id[r['aluno_local_id']].append(r)
            allowed = set()
            for student,values in by_id.items():
                if not all(r['disponibilidade'] and r['participacao'] for r in values):
                    continue
                if view['grupo_id']=='evidencia_completa' or sum(r['numerador'] for r in values)*5 < sum(r['denominador'] for r in values)*4:
                    allowed.add(student)
            subset = [r for r in subset if r['aluno_local_id'] in allowed]
        valid = [r for r in subset if r['participacao'] and r['disponibilidade']]
        n,d = sum(r['numerador'] for r in valid),sum(r['denominador'] for r in valid)
        assert (view['acertos'],view['oportunidades']) == (n,d)
        assert view['cadastros']==len({r['aluno_local_id'] for r in subset})
        assert view['avaliados']==len({r['aluno_local_id'] for r in subset if r['participacao']})
        same(view['taxa_observada'],F(n,d) if d else None)
        count += 5
    # Contas manuais fechadas: cadeia a-b-c, P=(1,ausente,0).
    # A² linhas (1/2,0,1/2),(0,1,0),(1/2,0,1/2); retirando retorno dá (0,ausente,1).
    manual = dict(A=[[0,1,0],[.5,0,.5],[0,1,0]],P=[1,None,0],
        dois_passos=[.5,None,.5],massa_retorno=[.5,0,.5],sem_retorno=[0,None,1],
        par_dois_nos='A^2=I; sem retorno inteiramente ausente',
        fanout='H1 2/4 em duas ocorrencias: massa 1/2 em cada; BNCC duplicada nao acrescenta itens')
    report = dict(status='PASS',metodo='Fraction e lacos independentes sem airam/numpy',
        comparacoes=count,fontes=hashes,contraprova_manual=manual,blocos=20,
        limites='Validacao computacional local; nao e validacao pedagogica externa')
    (ROOT/'evidencias/T07/contraprova-resultado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PASS',comparacoes=count,blocos=20)))


if __name__ == '__main__':
    main()
