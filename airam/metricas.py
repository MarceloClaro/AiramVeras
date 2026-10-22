"""Estatística observada por instrumento; resultados individuais são restritos."""
from collections import defaultdict
import hashlib
import json

CONTEXTO = ('avaliacao_id', 'ano_avaliacao', 'ciclo', 'ano_escolar', 'componente',
            'fonte_id', 'sha256', 'exportacao')


def taxa_por_itens(acertos: list[int], oportunidades: list[int]) -> float | None:
    """Razão das somas. Lista vazia é ausência, contagem inválida é erro."""
    if len(acertos) != len(oportunidades):
        raise ValueError('Contagens de comprimentos distintos')
    if any(type(n) is not int or type(d) is not int or d <= 0 or not 0 <= n <= d
           for n, d in zip(acertos, oportunidades)):
        raise ValueError('Contagens invalidas')
    return sum(acertos) / sum(oportunidades) if oportunidades else None


def agregar_habilidades(rows: list[dict]) -> list[dict]:
    """Agrega uma vez por ocorrência H, conservando versão, máscaras e proveniência.

    Saída inclui aluno, turma/escola e H em turma/escola. Não mistura instrumentos
    nem aplica adequação por contagem. O chamador guarda a saída em área restrita.
    """
    groups = defaultdict(list)
    seen = set()
    flags = {}
    for row in rows:
        required = (*CONTEXTO, 'aluno_local_id', 'avaliacao_local_id', 'turma', 'posicao',
                    'participacao', 'disponibilidade', 'unidade', 'numerador', 'denominador',
                    'caminho', 'linha_fonte', 'bruto')
        if any(k not in row for k in required):
            raise ValueError('Observacao sem contexto obrigatorio')
        if row['componente'] not in ('LEITURA', 'MATEMATICA') or row['unidade'] != 'acertos_itens':
            raise ValueError('Unidade/instrumento nao admite taxa H')
        if type(row['participacao']) is not bool or type(row['disponibilidade']) is not bool:
            raise ValueError('Mascara invalida')
        context = tuple(row[k] for k in CONTEXTO)
        student = context + (row['aluno_local_id'],)
        identity = student + (row['posicao'],)
        if identity in seen:
            raise ValueError('H duplicada na ocorrencia')
        seen.add(identity)
        declaration = (row['participacao'], row['turma'], row['avaliacao_local_id'])
        if student in flags and flags[student] != declaration:
            raise ValueError('Participacao/turma/aplicacao divergente')
        flags[student] = declaration
        n, d = row['numerador'], row['denominador']
        if row['disponibilidade']:
            if not row['participacao']:
                raise ValueError('Medida em nao participante')
            taxa_por_itens([n], [d])
        elif n is not None or d is not None:
            raise ValueError('Ausencia com contagem')
        for level, class_name, individual, position in (
            ('aluno', row['turma'], row['aluno_local_id'], None),
            ('turma', row['turma'], None, None), ('escola', None, None, None),
            ('turma', row['turma'], None, row['posicao']),
            ('escola', None, None, row['posicao'])):
            groups[context + (level, class_name, individual, position)].append(row)
    result = []
    for key, values in groups.items():
        valid = [r for r in values if r['disponibilidade'] and r['participacao']]
        ns, ds = [r['numerador'] for r in valid], [r['denominador'] for r in valid]
        n, d = sum(ns), sum(ds)
        participants = {r['aluno_local_id'] for r in values if r['participacao']}
        missing_participant = any(r['participacao'] and not r['disponibilidade'] for r in values)
        canonical = sorted(json.dumps(r, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False) for r in values)
        item = dict(zip(CONTEXTO, key[:len(CONTEXTO)]))
        item.update(zip(('nivel','turma','aluno_local_id','posicao'), key[len(CONTEXTO):]))
        item.update(cadastros=len({r['aluno_local_id'] for r in values}), avaliados=len(participants),
            validas=len(valid), ausentes=len(values)-len(valid),
            acertos=n, oportunidades=d, taxa_observada=taxa_por_itens(ns, ds),
            taxa=None if missing_participant else taxa_por_itens(ns, ds),
            fracao_observada={'numerador':n,'denominador':d} if d else None,
            proveniencia_sha256=hashlib.sha256(('\n'.join(canonical)).encode('utf-8')).hexdigest())
        result.append(item)
    return sorted(result, key=lambda x: json.dumps(x,sort_keys=True,ensure_ascii=False))
