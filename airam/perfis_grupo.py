"""Perfis pedagógicos revisáveis; observação não implica domínio curricular."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json

from airam.clusters import resumo
from airam.metricas import CONTEXTO


def _validate(rows,context=None):
    contexts={tuple(r[k] for k in CONTEXTO) for r in rows}
    if len(contexts)!=1:
        raise ValueError('Perfil exige um contexto unico')
    ctx=dict(zip(CONTEXTO,next(iter(contexts))))
    if context is not None and ctx!=context:
        raise ValueError('Contexto do grupo e observacoes divergem')
    keys=set()
    for r in rows:
        key=(r['aluno_local_id'],r['posicao'] if r['posicao'] is not None else r['campo_original'])
        if key in keys: raise ValueError('Observacao duplicada no perfil')
        keys.add(key)
        if r['disponibilidade'] and not r['participacao']:
            raise ValueError('Medida em nao participante')
        if r['unidade']=='acertos_itens':
            n,d=r['numerador'],r['denominador']
            if r['disponibilidade']:
                if type(n) is not int or type(d) is not int or not 0<=n<=d or d<=0:
                    raise ValueError('Contagem invalida')
            elif n is not None or d is not None:
                raise ValueError('Ausencia com contagem')
    return ctx


def _total(rows):
    valid=[r for r in rows if r['disponibilidade'] and r['unidade']=='acertos_itens']
    return (sum(r['numerador'] for r in valid),sum(r['denominador'] for r in valid)) if valid else (None,None)


def grupos_por_regras(observacoes,cobertura_minima=0.8):
    """Alternativa explícita; Meta B total e categorias originais E/F separadas."""
    ctx=_validate(observacoes)
    by_student=defaultdict(list)
    for r in observacoes: by_student[r['aluno_local_id']].append(r)
    groups=defaultdict(list)
    criteria={
        'cobertura_insuficiente':'sem contagem ou cobertura menor que corte; priorizar verificacao e acesso a avaliacao',
        'abaixo_meta_B':'total observado C/D < 4/5, cobertura suficiente; nao e categoria CAEd',
        'atinge_meta_B':'total observado C/D >= 4/5, cobertura suficiente; nao e categoria CAEd'}
    counts=ctx['componente'] in ('LEITURA','MATEMATICA')
    for student,rows in sorted(by_student.items()):
        if counts:
            n,d=_total(rows)
            expected={r.get('oportunidades_previstas') for r in rows}
            if len(expected)!=1 or None in expected or next(iter(expected))<=0:
                raise ValueError('Oportunidades previstas necessarias para regra')
            coverage=(d or 0)/next(iter(expected))
            label='cobertura_insuficiente' if d is None or coverage<cobertura_minima else (
                'abaixo_meta_B' if n*5<d*4 else 'atinge_meta_B')
        else:
            categories={r.get('categoria') for r in rows}
            if len(categories)!=1: raise ValueError('Categorias originais divergentes')
            category=next(iter(categories))
            available=any(r['disponibilidade'] for r in rows)
            label='categoria_original:'+str(category) if available and category is not None else 'sem_resultado_original'
            criteria[label]='categoria original do instrumento; sem conversao para acertos ou classificacao de capacidade'
        groups[label].append(student)
    return dict(versao='airam-regras-t08-v1',contexto=ctx,status='grupo_por_regra',
        grupos=[dict(grupo_id=k,tipo='regra',criterio=criteria[k],membros=v,n=len(v)) for k,v in sorted(groups.items())],
        cobertura=dict(cadastrados=len(by_student),elegiveis=len(by_student)-len(groups.get('cobertura_insuficiente',[])),
                       corte=cobertura_minima),criterios=dict(versao='airam-regras-t08-v1',
            meta_B='total observado C/D >=4/5 apenas acertos_itens',meta_A='categoria original Adequado separada'))


def _curriculum(links,context,position):
    fields=('codigo_caed','texto_caed','codigo_bncc','texto_bncc','ressalva','fonte_matriz',
        'sha256_pdf','pagina_matriz','fonte_posicao','versao_posicao','ocorrencia_id',
        'status_contextual','status_semantico','peso_analitico','localizador_bncc')
    selected=[]; seen=set()
    for v in links:
        if v['posicao']!=position or any(v[a]!=context[b] for a,b in (
            ('avaliacao_id','avaliacao_id'),('ano_avaliacao','ano_avaliacao'),('ano_avaliado','ano_escolar'),
            ('ciclo_avaliado','ciclo'),('componente','componente'))): continue
        out={k:v.get(k) for k in fields}
        out['versao_bncc']=(v.get('bncc') or {}).get('proveniencia_dataset')
        canonical=json.dumps(out,sort_keys=True,ensure_ascii=False)
        if canonical not in seen: selected.append(out); seen.add(canonical)
    return sorted(selected,key=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False))


def _activities(context,skill,curriculum):
    descriptors=sorted({v['texto_caed'] for v in curriculum if v.get('texto_caed')})
    focus=' / '.join(descriptors) if descriptors else f'posição {skill}: descritor não documentado'
    reading=context['componente']=='LEITURA'
    return [
        dict(etapa='sondagem docente',proposta=f'Para {focus}, apresentar duas tarefas novas de estrutura comparavel; pedir explicacao oral da estrategia e registrar oportunidades e respostas. Os blocos agregados nao identificam os itens errados.',
             evidencia_esperada='registro docente de procedimento e respostas; sem presumir erro individual'),
        dict(etapa='pratica orientada',proposta=(
            f'Trabalhar {focus} com palavras, frases ou texto curto selecionado pelo professor conforme o descritor; modelar leitura, localizar pistas e comparar respostas em duplas, com apoio gradualmente retirado.' if reading else
            f'Trabalhar {focus} com situacoes-problema selecionadas pelo professor conforme o descritor; usar materiais ou desenhos quando pertinentes, comparar estrategias e explicitar a passagem para registro simbolico.'),
             evidencia_esperada='observacao da estrategia, tipo de ajuda e justificativa; adequacao do recurso pendente'),
        dict(etapa='verificacao autonoma',proposta='Aplicar novas tarefas comparaveis sem o apoio inicial, preservando instrumento, unidade, data e denominador. Rever composicao do grupo com o professor; nao prometer eficacia.',
             evidencia_esperada='nova medida observada e revisao docente; avaliacao temporal ainda pendente')]


def descrever_grupos(resultado:dict,observacoes:list[dict],vinculos:list[dict])->list[dict]:
    """Distribuições e propostas vêm das observações originais, inclusive constantes."""
    context=_validate(observacoes,resultado['contexto'])
    all_students={r['aluno_local_id'] for r in observacoes}
    output=[]
    for group in resultado['grupos']:
        members=sorted(group['membros'])
        if len(members)!=len(set(members)) or not set(members)<=all_students:
            raise ValueError('Membros sem observacao ou duplicados')
        rows=[r for r in observacoes if r['aluno_local_id'] in set(members)]
        if not rows: continue
        by_student=defaultdict(list)
        for r in rows: by_student[r['aluno_local_id']].append(r)
        categories={}
        for s,items in by_student.items():
            found={r.get('categoria') for r in items}
            if len(found)!=1: raise ValueError('Categoria original divergente')
            categories[s]=next(iter(found))
        n,d=_total(rows); totals=[_total(rs) for rs in by_student.values()]
        ratio=[a/b for a,b in totals if b is not None]
        count_unit=all(r['unidade']=='acertos_itens' for r in rows)
        positions=sorted({r['posicao'] for r in rows if r['posicao'] is not None})
        skills=[]
        for pos in positions:
            subset=[r for r in rows if r['posicao']==pos]; a,b=_total(subset)
            proportions=[r['numerador']/r['denominador'] for r in subset if r['disponibilidade']]
            curriculum=_curriculum(vinculos,context,pos)
            skills.append(dict(posicao=pos,acertos=a,oportunidades=b,taxa=a/b if b else None,
                disponiveis=len(proportions),ausentes=len(subset)-len(proportions),
                distribuicao=resumo(proportions),constante=len(set(proportions))==1,
                curriculo=curriculum,status_curricular='documentado' if curriculum else 'sem_vinculo_documentado',
                atividades=_activities(context,pos,curriculum)))
        ordered=sorted([s for s in skills if s['taxa'] is not None],key=lambda s:(s['taxa'],s['posicao']))
        for skill in skills:
            skill['prioridade_observada']=next((i+1 for i,v in enumerate(ordered) if v['posicao']==skill['posicao']),None)
        own=[]
        if not count_unit:
            for field,unit in sorted({(r['campo_original'],r['unidade']) for r in rows}):
                values=[r for r in rows if r['campo_original']==field and r['unidade']==unit]
                valid=[r['valor'] for r in values if r['disponibilidade'] and r.get('valor') is not None]
                own.append(dict(campo_original=field,unidade=unit,disponiveis=len(valid),ausentes=len(values)-len(valid),
                    distribuicao=resumo(valid),bncc='sem_associacao_documentada',
                    atividades='Rever amostras e rubrica original de escrita com producao orientada e revisao textual.' if context['componente']=='ESCRITA'
                    else 'Rever tarefa original de fluencia, registrar precisao, tempo e tipo de apoio; praticar leitura modelada e nova leitura comparavel sem converter unidades.'))
        coverage=[sum(r['disponibilidade'] for r in rs)/len(rs) for rs in by_student.values()]
        opportunity_coverage=[]
        for rs in by_student.values():
            _,den=_total(rs); expected=rs[0].get('oportunidades_previstas')
            if expected: opportunity_coverage.append((den or 0)/expected)
        low=[s['posicao'] for s in ordered if s['taxa']<1][:3]
        high=[s['posicao'] for s in sorted(ordered,key=lambda s:(-s['taxa'],s['posicao'])) if s['taxa']>0][:3]
        descriptive='acompanhamento das evidencias em '+', '.join(low) if low else 'acompanhamento no instrumento original'
        candidates=resultado.get('candidatos',[])
        selected=next((c for c in candidates if c['k']==resultado.get('k')),None)
        provenance=hashlib.sha256(json.dumps(sorted(rows,key=lambda r:json.dumps(r,sort_keys=True)),sort_keys=True,
                                            ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        output.append(dict(versao='airam-perfil-t08-v1',contexto=deepcopy(context),grupo_id=group['grupo_id'],
            tipo=group.get('tipo','cluster'),nome=descriptive,n=len(members),membros=members,
            turmas=dict(sorted(Counter(rs[0]['turma'] for rs in by_student.values()).items())),
            criterio_pertencimento=group['criterio'],status_liberacao='exploratorio_revisao_docente_pendente',
            observado=dict(acertos=n,oportunidades=d,taxa=n/d if d else None,
                distribuicao_taxas_individuais=resumo(ratio),
                distribuicao_acertos=resumo([a for a,b in totals if a is not None]),
                distribuicao_oportunidades=resumo([b for a,b in totals if b is not None])),
            categorias_caed_originais=dict(sorted(Counter(v if v is not None else 'sem_resultado' for v in categories.values()).items())),
            meta_A=dict(status='categoria_original_separada' if count_unit else 'sem_contrato_de_adequacao',
                        adequados=sum(v=='Adequado' for v in categories.values()) if count_unit else None),
            meta_B=dict(status='total_observado' if count_unit else 'unidade_nao_aplicavel',
                        atingem=sum(a*5>=b*4 for a,b in totals if b) if count_unit else None),
            cobertura=dict(celulas_previstas=len(rows),celulas_disponiveis=sum(r['disponibilidade'] for r in rows),
                celulas_ausentes=sum(not r['disponibilidade'] for r in rows),por_aluno=resumo(coverage),
                por_oportunidades=resumo(opportunity_coverage),
                alunos_sem_cobertura=sum(not any(r['disponibilidade'] for r in rs) for rs in by_student.values()),
                universo=deepcopy(resultado['cobertura'])),
            habilidades=skills,medidas_proprias=own,lacunas_priorizadas=low,forcas_relativas=high,
            criterio_prioridade='menor taxa observada por posicao; relativo ao grupo, sem corte 80% por habilidade; ausencia demanda verificacao',
            estabilidade=deepcopy(group.get('estabilidade')),
            estabilidade_global={k:deepcopy(selected[k]) for k in ('k','seeds','subamostras','separacao','reprovacoes')} if selected else None,
            revisao_docente='pendente',reavaliacao=dict(data=None,status='pendente',
                gatilho='apos ciclo de atividades acordado com docente ou nova avaliacao comparavel; registrar data, instrumento, unidade, oportunidades e apoio antes de rever grupos'),
            ressalvas=['Identidade local provisoria; nenhuma validacao longitudinal.',
                'Associacao CAEd/BNCC documental nao comprova dominio integral ou pre-requisito causal.',
                'Contagens observadas uma vez por posicao; vinculos multiplos nao somam oportunidades.',
                'Propagacao e estimativa curricular; nao substitui observacao nem cria acertos.',
                'Ausencias nao sao deficits. Forcas e lacunas sao relativas a este instrumento e cobertura.',
                'Atividades propostas precisam de adequacao docente; nao ha eficacia demonstrada.',
                'Sem rotulo de capacidade fixa, retencao, promocao, exclusao ou diagnostico.',
                'Meta B usa total observado; nenhuma obrigacao de 80% por H e nenhuma soma de tetos por bloco.'],
            fontes_sha256=sorted({r['sha256'] for r in rows}),proveniencia_observacoes_sha256=provenance))
    return output


def perfis_publicos(perfis):
    """Projeção agregada explícita: pequenos grupos permanecem só no restrito."""
    output=[]
    for profile in perfis:
        if profile['n']<5:
            output.append(dict(versao=profile['versao'],contexto=deepcopy(profile['contexto']),
                grupo_id=profile['grupo_id'],tipo=profile['tipo'],n_intervalo='1-4',
                status_publicacao='suprimido_n_menor_5',revisao_docente='pendente'))
        else:
            item={k:deepcopy(v) for k,v in profile.items() if k!='membros'}
            item['status_publicacao']='agregado_local_revisao'
            output.append(item)
    return output
