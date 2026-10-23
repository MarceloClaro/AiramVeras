"""Cenários aritméticos condicionais, sem inferir aprendizagem ou nível CAEd."""
from copy import deepcopy
from .metas import meta_acertos, meta_adequados


def _count(value):
    if type(value) is not int or value < 0:
        raise ValueError('Contagem hipotetica invalida')
    return value


def projetar_cenario(observacoes: list[dict], metas: dict, hipoteses: dict) -> dict:
    """Uma base/escopo homogêneo. Nunca altera a categoria original por acertos.

    Ganho/perda de acertos são deslocamentos líquidos com saturação; entradas e
    saídas de Adequado são hipóteses institucionais independentes. A lista meta_B
    conserva a ordem de entrada e pertence à área restrita quando individual.
    """
    allowed = {'entradas_adequado', 'saidas_adequado', 'ganho_acertos', 'perda_acertos', 'corte_adequacao'}
    if not isinstance(hipoteses, dict) or hipoteses.keys() - allowed:
        raise ValueError('Campo de hipotese nao autorizado')
    if not isinstance(metas, dict) or set(metas) != {'A', 'B'}:
        raise ValueError('Duas metas separadas obrigatorias')
    meta_adequados(0, 0, metas['A']); meta_acertos(None, None, metas['B'])
    counts = {k: _count(hipoteses.get(k, 0)) for k in allowed - {'corte_adequacao'}}
    cutoff = hipoteses.get('corte_adequacao')
    if cutoff is not None:
        if not isinstance(cutoff, dict) or set(cutoff) != {'valor', 'status', 'referencia'}:
            raise ValueError('Corte exige regra ou hipotese explicita')
        _count(cutoff['valor'])
        # Não existe regra oficial auditada nesta base; um rótulo não a cria.
        if cutoff['status'] != 'hipotese_nao_oficial' or not isinstance(cutoff['referencia'], str) or not cutoff['referencia'].strip():
            raise ValueError('Corte sem proveniencia e status')
    if not isinstance(observacoes, list) or not all(isinstance(r, dict) for r in observacoes):
        raise ValueError('Observacoes invalidas')
    context = ['componente', 'ano_escolar', 'avaliacao_id', 'fonte_id', 'sha256', 'ciclo', 'ano_avaliacao', 'unidade']
    for key in context:
        if any(key in r for r in observacoes) and any(r.get(key) != observacoes[0].get(key) for r in observacoes):
            raise ValueError('Base mistura contextos ou instrumentos')
    identifiers = [r['avaliacao_local_id'] for r in observacoes if 'avaliacao_local_id' in r]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError('Aplicacao duplicada')
    component = observacoes[0].get('componente') if observacoes else None
    compatible = component in {'LEITURA', 'MATEMATICA'} or not observacoes
    if observacoes and component not in {'LEITURA', 'MATEMATICA', 'ESCRITA', 'FLUENCIA'}:
        raise ValueError('Componente sem contrato')
    for row in observacoes:
        if type(row.get('participacao')) is not bool:
            raise ValueError('Participacao obrigatoria')
        if compatible:
            if row.get('unidade', 'itens') != 'itens':
                raise ValueError('Unidade incompativel com itens')
            if row['participacao'] and not isinstance(row.get('categoria'), str):
                raise ValueError('Categoria original ausente')
            if not row['participacao'] and (row.get('acertos') is not None or row.get('oportunidades') is not None):
                raise ValueError('Ausencia de participacao com contagens')
            if row['participacao'] and row.get('acertos') is None and row.get('oportunidades') is None:
                raise ValueError('Participacao sem contagens completas')
    evaluated = [r for r in observacoes if r['participacao']]
    if compatible:
        a = meta_adequados(len(evaluated), sum(r['categoria'] == 'Adequado' for r in evaluated), metas['A'])
        entries, exits = counts['entradas_adequado'], counts['saidas_adequado']
        if entries > a['avaliados'] - a['adequados'] or exits > a['adequados']:
            raise ValueError('Transicao de categoria impossivel')
        future = a['adequados'] + entries - exits
        minimum = max(0, a['alvo'] - a['adequados'] + exits) if a['alvo'] is not None else None
        a.update(adequados_projetados=future if evaluated else None,
            atingida_projetada=future >= a['alvo'] if evaluated else None,
            entradas=entries, saidas=exits, entradas_minimas_com_perdas=minimum,
            viavel=minimum <= a['avaliados'] - a['adequados'] if evaluated else None,
            fracao_projetada={'numerador':future, 'denominador':len(evaluated)} if evaluated else None,
            unidade='estudantes_na_categoria_original')
    else:
        if counts['entradas_adequado'] or counts['saidas_adequado'] or cutoff is not None:
            raise ValueError('Meta A sem regra aplicavel ao instrumento')
        a = dict(meta='A', status='unidade_nao_aplicavel', acertos_ate_adequacao=None,
                 alvo=None, adequados_projetados=None, atingida_projetada=None)
    b = []
    for index, row in enumerate(observacoes):
        if not compatible:
            b.append(dict(observacao_indice=index, status='unidade_nao_aplicavel',
                          unidade=row.get('unidade'), alvo=None, lacuna=None,
                          acertos_projetados=None, lacuna_projetada=None, atingida_projetada=None))
            continue
        x, n = row.get('acertos'), row.get('oportunidades')
        target = meta_acertos(x, n, metas['B'])
        delta = counts['ganho_acertos'] - counts['perda_acertos']
        future = min(n, max(0, x + delta)) if x is not None else None
        if cutoff is not None and n is not None and cutoff['valor'] > n:
            raise ValueError('Corte fora da unidade observada')
        b.append(dict(target, observacao_indice=index, acertos_observados=x, oportunidades=n,
            unidade='itens', ganho=counts['ganho_acertos'], perda=counts['perda_acertos'],
            deslocamento_bruto=delta, deslocamento_realizado=future-x if x is not None else None,
            acertos_projetados=future,
            lacuna_projetada=max(0, target['alvo']-future) if future is not None else None,
            atingida_projetada=future >= target['alvo'] if future is not None else None,
            distancia_adequacao_condicional=dict(lacuna=max(0,cutoff['valor']-x),
                status=cutoff['status'], referencia=cutoff['referencia']) if cutoff is not None and x is not None else None))
    return dict(tipo_resultado='cenario_condicional',
        premissas=['Participacao e composicao constantes no mesmo instrumento/contexto.',
            'Entradas/saidas de Adequado independem dos deslocamentos de acertos.',
            'Ganhos/perdas sao hipoteses liquidas saturadas, nao transicoes fisicas comprovadas.',
            'Sem probabilidades calibradas, efeito causal, eficacia ou numero de aulas.'],
        unidade={'meta_A':'estudantes_na_categoria_original', 'meta_B':'acertos_por_estudante'},
        comparabilidade='mesma_base_observada_sem_validacao_longitudinal',
        status_validacao='aritmetica_condicional_sem_validacao_pedagogica',
        hipoteses=deepcopy(hipoteses), metas=deepcopy(metas), meta_A=a, meta_B=b)
