"""Contraprova independente das contagens e do handoff, sem importar airam."""
from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
CONTEXT=('avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente','fonte_id','sha256','exportacao')


def read(path):
    return json.loads((ROOT/path).read_text(encoding='utf-8'))


def check(condition,message):
    if not condition: raise AssertionError(message)


def choose2(n):
    return n*(n-1)//2


def ari(left,right):
    cells=Counter(zip(left,right)); a=Counter(left); b=Counter(right)
    pairs=choose2(len(left)); index=sum(choose2(n) for n in cells.values())
    expected=Fraction(sum(choose2(n) for n in a.values())*sum(choose2(n) for n in b.values()),pairs)
    maximum=Fraction(sum(choose2(n) for n in a.values())+sum(choose2(n) for n in b.values()),2)
    return float((index-expected)/(maximum-expected)) if maximum!=expected else 1.


def main():
    source=read('restrito/t05/checkpoint.json')['observado']
    protected=read('restrito/t08/checkpoint.json'); public=read('estatistica/t08/checkpoint.json')
    check(public['checkpoint_restrito_sha256']==hashlib.sha256((ROOT/'restrito/t08/checkpoint.json').read_bytes()).hexdigest(),
          'Hash restrito divergente')
    applications={r['avaliacao_local_id']:r for r in source['avaliacoes']}
    rows=defaultdict(list)
    for table in ('habilidades','escrita','fluencia'):
        for row in source[table]: rows[tuple(row[k] for k in CONTEXT)].append(row)
    checks=0; profiles_checked=0; comparisons_checked=0

    def profile_check(profile):
        nonlocal checks,profiles_checked
        ctx=tuple(profile['contexto'][k] for k in CONTEXT); members=set(profile['membros'])
        originals=[r for r in rows[ctx] if r['aluno_local_id'] in members]
        check(len(members)==profile['n'],'N do perfil divergente')
        check(profile['cobertura']['celulas_previstas']==len(originals),'Cobertura de celulas divergente')
        check(profile['cobertura']['celulas_disponiveis']==sum(r['disponibilidade'] for r in originals),'Cobertura disponivel divergente')
        valid=[r for r in originals if r['disponibilidade'] and r['unidade']=='acertos_itens']
        n=sum(r['numerador'] for r in valid) if valid else None
        d=sum(r['denominador'] for r in valid) if valid else None
        check((n,d)==(profile['observado']['acertos'],profile['observado']['oportunidades']),'Total observado divergente')
        rate=float(Fraction(n,d)) if d else None
        check(rate==profile['observado']['taxa'],'Taxa observada divergente')
        for h in profile['habilidades']:
            v=[r for r in valid if r['posicao']==h['posicao']]
            a=sum(r['numerador'] for r in v) if v else None
            b=sum(r['denominador'] for r in v) if v else None
            check((a,b)==(h['acertos'],h['oportunidades']),'Fanout ou contagem H divergente')
            check(h['taxa']==(float(Fraction(a,b)) if b else None),'Taxa H divergente')
            checks+=2
        apps={r['aluno_local_id']:applications[r['avaliacao_local_id']] for r in originals}
        categories=dict(Counter(a['categoria'] or 'sem_resultado' for a in apps.values()))
        check(categories==profile['categorias_caed_originais'],'Categoria original divergente')
        check(profile['revisao_docente']=='pendente' and profile['reavaliacao']['data'] is None,'Revisao inventada')
        profiles_checked+=1; checks+=7

    diagnostics=[]
    for inst in protected['instrumentos']:
        for p in inst['perfis_regras']+inst['perfis_observado']: profile_check(p)
        for scenario in inst['cenarios']:
            for ps in scenario['perfis'].values():
                for p in ps: profile_check(p)
            results=scenario['resultados']
            for result in results.values():
                for c in result['candidatos']:
                    for axis in ('seeds','subamostras'):
                        record=c[axis]
                        check(record['planejadas']==record['validas']+sum(record['falhas'].values()),'Tentativas omitidas')
                        checks+=1
                    if 'rotulos' in c:
                        check(sum(c['tamanhos'])==len(result['alunos']),'Tamanhos divergentes')
                        check(c['tamanhos']==[c['rotulos'].count(i) for i in range(c['k'])],'Rotulos divergentes')
                        if c['liberado']: check(min(c['tamanhos'])>=5 and not c['reprovacoes'],'Cluster liberado indevido')
                        checks+=3
            for comparison in scenario['comparacoes']:
                left,right=('observado_total','observado_controle') if comparison['contraste']=='selecao_features' else (
                    'observado_controle','propagado_controle')
                a=results[left]; b=results[right]
                check(a['alunos']==b['alunos'],'Comparacao com alunos diferentes')
                if comparison['contraste']=='transformacao_curricular':
                    check(a['colunas']==b['colunas'] and a['geometria']==b['geometria'],'Comparacao com features/pesos diferentes')
                labels_a=next(c['rotulos'] for c in a['candidatos'] if c['k']==comparison['k'])
                labels_b=next(c['rotulos'] for c in b['candidatos'] if c['k']==comparison['k'])
                check(abs(ari(labels_a,labels_b)-comparison['ari'])<1e-12,'ARI independente divergente')
                check(sum(sum(row) for row in comparison['transicao'])==len(labels_a),'Transicao divergente')
                comparisons_checked+=1; checks+=4
        primary=next(s for s in inst['cenarios'] if s['cenario']=='ressalvada_passo1')
        distance_difference=None
        if primary['status']=='comparavel':
            f=primary['definicao_bracos']; left=f['observado_controle']; right=f['propagado_controle']
            distances=[]
            for i in range(len(left['alunos'])):
                for j in range(i):
                    a=sum(w*(x-y)**2 for w,x,y in zip(left['pesos'],left['valores'][i],left['valores'][j]))
                    b=sum(w*(x-y)**2 for w,x,y in zip(right['pesos'],right['valores'][i],right['valores'][j]))
                    distances.append(abs(a-b))
            distance_difference=max(distances,default=0)
        diagnostics.append(dict(ano=inst['contexto']['ano_escolar'],componente=inst['contexto']['componente'],
            n=inst['observado_operacional']['cobertura']['elegiveis'],
            observado_status=inst['observado_operacional']['status'],observado_k=inst['observado_operacional']['k'],
            comparacao=primary['status'],features_comuns=primary['selecao']['features_comuns'],
            max_diferenca_distancias_quadradas_controle=distance_difference,
            interpretacao_geometria='Geometrias iguais ate precisao numerica podem produzir selecoes distintas por empates/inicializacao; nao atribuir ganho ao grafo',
            controle={arm:dict(status=r['status'],k=r['k']) for arm,r in primary['resultados'].items()}))
    for inst in protected['unidades_proprias']:
        original=rows[tuple(inst['contexto'][k] for k in CONTEXT)]
        by_student=defaultdict(list)
        for row in original: by_student[row['aluno_local_id']].append(row)
        available=sum(any(r['disponibilidade'] for r in rs) for rs in by_student.values())
        coverage=inst['regras']['cobertura']
        check(coverage['cadastrados']==len(by_student),'Cadastro E/F divergente')
        check(coverage['elegiveis']==coverage['com_resultado']==available,'Elegibilidade E/F divergente')
        check(coverage['sem_resultado']==len(by_student)-available,'Ausencia E/F divergente')
        check(coverage['cobertura_resultados']==float(Fraction(available,len(by_student))),'Taxa de cobertura E/F divergente')
        check(coverage['corte'] is None,'Corte de oportunidades indevido em E/F')
        check(coverage['participantes']==sum(any(r['participacao'] for r in rs) for rs in by_student.values()),'Participacao E/F divergente')
        check(coverage['com_categoria_original']==sum(applications[rs[0]['avaliacao_local_id']]['categoria'] is not None
                                                    for rs in by_student.values()),'Categoria E/F divergente')
        checks+=7
        for p in inst['perfis']:
            profile_check(p)
            check(p['cobertura']['universo']==coverage,'Cobertura do perfil E/F divergente')
            check(p['meta_B']['status']=='unidade_nao_aplicavel' and p['habilidades']==[],'Escala E/F alterada')
            checks+=2
    tokens=set()
    def collect(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in ('aluno_local_id','avaliacao_local_id','nome','nome_normalizado') and isinstance(v,str) and len(v)>3:
                    tokens.add(v)
                collect(v)
        elif isinstance(value,list):
            for v in value: collect(v)
    collect(source)
    paths=[ROOT/'estatistica/t08/checkpoint.json',ROOT/'estatistica/t08/perfis-pedagogicos.md']+[p for p in (ROOT/'evidencias/T08').glob('*')
        if p.suffix in ('.py','.json','.log','.md')]
    for path in paths:
        raw=path.read_text(encoding='utf-8-sig')
        check(not any(token in raw for token in tokens),'Identificador individual em artefato agregado/log')
    def no_individual(value):
        if isinstance(value,dict):
            check(not set(value)&{'alunos','membros','rotulos','aluno_local_id','avaliacao_local_id','valores'},'Campo individual no agregado')
            for v in value.values(): no_individual(v)
        elif isinstance(value,list):
            for v in value: no_individual(v)
    no_individual(public)
    report=dict(status='PASS',verificacoes=checks,perfis_conferidos=profiles_checked,
        comparacoes_ARI_Fraction=comparisons_checked,arquivos_sem_identificadores=len(paths),diagnosticos=diagnostics,
        hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
                ['restrito/t08/checkpoint.json','estatistica/t08/checkpoint.json']},
        limites='Contraprova de aritmetica/identidade/privacidade; nao e validacao externa ou docente; armazenamento ignorado nao certifica ACL')
    label='fix1-contraprova-resultado.json' if 'proveniencia_fix1' in protected else 'contraprova-resultado.json'
    (ROOT/'evidencias/T08'/label).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ('diagnosticos','hashes')}))


if __name__=='__main__': main()
