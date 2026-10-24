"""Visões a partir de observações originais, nunca de somas de grupos."""
from collections import defaultdict
import json
from .metricas import CONTEXTO, taxa_por_itens


def agregar_observacoes(rows: list[dict], nivel: str,
                        grupos: list[dict] | None = None) -> list[dict]:
    """Deduplica observação por contexto/aluno/posição antes de agregar.

    Grupos contêm grupo_id/membros; sobreposição é permitida. Escola/turma sempre
    partem das linhas originais. Agregados não podem ser redistribuídos a alunos.
    """
    if nivel not in ('aluno','grupo','turma','escola'):
        raise ValueError('Nivel invalido')
    if nivel == 'grupo' and grupos is None:
        raise ValueError('Grupos necessarios')
    memberships, group_ids = defaultdict(set), set()
    for group in grupos or []:
        if group['grupo_id'] in group_ids:
            raise ValueError('Grupo duplicado')
        group_ids.add(group['grupo_id'])
        for student in set(group['membros']):
            memberships[student].add(group['grupo_id'])
    unique, declarations = {}, {}
    required = (*CONTEXTO,'aluno_local_id','avaliacao_local_id','turma','posicao',
                'numerador','denominador','participacao','disponibilidade','unidade')
    for r in rows:
        if any(k not in r for k in required) or r.get('nivel') in ('grupo','turma','escola'):
            raise ValueError('Somente observacoes individuais completas sao aceitas')
        if r['unidade'] != 'acertos_itens' or r['componente'] not in ('LEITURA','MATEMATICA'):
            raise ValueError('Unidade nao admite agregacao por itens')
        if type(r['participacao']) is not bool or type(r['disponibilidade']) is not bool:
            raise ValueError('Mascara invalida')
        if r['disponibilidade']:
            if not r['participacao']:
                raise ValueError('Medida de nao participante')
            taxa_por_itens([r['numerador']],[r['denominador']])
        elif r['numerador'] is not None or r['denominador'] is not None:
            raise ValueError('Ausencia com contagem')
        context = tuple(r[k] for k in CONTEXTO)
        identity = context + (r['aluno_local_id'],)
        declaration = (r['turma'],r['avaliacao_local_id'],r['participacao'])
        if identity in declarations and declarations[identity] != declaration:
            raise ValueError('Aplicacao individual divergente')
        declarations[identity] = declaration
        key = identity + (r['posicao'],)
        semantic = {k:r[k] for k in required}
        if key in unique and unique[key] != semantic:
            raise ValueError('Duplicata de observacao divergente')
        unique[key] = semantic
    buckets = defaultdict(list)
    for r in unique.values():
        context = tuple(r[k] for k in CONTEXTO)
        entities = ({'aluno': [r['aluno_local_id']], 'turma':[r['turma']], 'escola':[None],
                     'grupo': sorted(memberships[r['aluno_local_id']])})[nivel]
        for entity in entities:
            buckets[context+(entity,)].append(r)
    result = []
    for key, values in sorted(buckets.items(),key=lambda kv:str(kv[0])):
        valid = [r for r in values if r['disponibilidade']]
        n,d = sum(r['numerador'] for r in valid),sum(r['denominador'] for r in valid)
        item = dict(zip(CONTEXTO,key[:-1]))
        item.update(nivel=nivel,acertos=n,oportunidades=d,
            cadastros=len({r['aluno_local_id'] for r in values}),
            avaliados=len({r['aluno_local_id'] for r in values if r['participacao']}),
            validas=len(valid),ausentes=len(values)-len(valid),
            taxa_observada=n/d if d else None,
            taxa=None if any(r['participacao'] and not r['disponibilidade'] for r in values) else (n/d if d else None))
        if nivel != 'escola':
            item[{'aluno':'aluno_local_id','grupo':'grupo_id','turma':'turma'}[nivel]] = key[-1]
        result.append(item)
    return result
