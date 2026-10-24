"""Rota independente: somente stdlib/SQL/Fraction, sem importar o cálculo principal."""
from fractions import Fraction
import hashlib
import json
import sqlite3


def contraprovar(rows: list[dict]) -> dict:
    """Releitura das observações, agrupamento SQL e frações sem totais do produtor."""
    fields = ('avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente',
              'fonte_id','sha256','exportacao')
    contexts, raw_groups, flags, unique = {}, {}, {}, set()
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE observacoes (g TEXT, pessoa TEXT, participou INT, valido INT, n INT, d INT)')
        for r in rows:
            try:
                context = tuple(r[f] for f in fields)
                student = context + (r['aluno_local_id'],)
                occurrence = student + (r['posicao'],)
                declaration = (r['participacao'],r['turma'],r['avaliacao_local_id'])
                if occurrence in unique or (student in flags and flags[student] != declaration):
                    raise ValueError
                unique.add(occurrence)
                flags[student] = declaration
                if r['componente'] not in ('LEITURA','MATEMATICA') or r['unidade'] != 'acertos_itens':
                    raise ValueError
                if type(r['participacao']) is not bool or type(r['disponibilidade']) is not bool:
                    raise ValueError
                n, d = r['numerador'], r['denominador']
                if r['disponibilidade']:
                    if not r['participacao'] or type(n) is not int or type(d) is not int or not 0 <= n <= d or d <= 0:
                        raise ValueError
                elif n is not None or d is not None:
                    raise ValueError
                # Os campos de proveniência são obrigatórios, inclusive sem medida.
                for f in ('caminho','linha_fonte','bruto'):
                    r[f]
                for level, cls, who, h in [('aluno',r['turma'],r['aluno_local_id'],None),
                    ('turma',r['turma'],None,None),('escola',None,None,None),
                    ('turma',r['turma'],None,r['posicao']),('escola',None,None,r['posicao'])]:
                    group = json.dumps([*context,level,cls,who,h],ensure_ascii=False)
                    contexts[group] = dict(zip(fields,context)) | dict(nivel=level,turma=cls,aluno_local_id=who,posicao=h)
                    raw_groups.setdefault(group,[]).append(json.dumps(r,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False))
                    db.execute('INSERT INTO observacoes VALUES (?,?,?,?,?,?)',
                        (group,r['aluno_local_id'],r['participacao'],r['disponibilidade'],n or 0,d or 0))
            except (KeyError,TypeError,ValueError):
                raise ValueError('Observacao invalida na contraprova; valores suprimidos') from None
        result = []
        query = '''SELECT g, COUNT(DISTINCT pessoa), COUNT(DISTINCT CASE WHEN participou THEN pessoa END),
            SUM(valido), COUNT(*)-SUM(valido), SUM(n), SUM(d),
            SUM(CASE WHEN participou AND NOT valido THEN 1 ELSE 0 END)
            FROM observacoes GROUP BY g'''
        for group, cad, assessed, valid, missing, n, d, partial in db.execute(query):
            rate = float(Fraction(n,d)) if d else None
            result.append(contexts[group] | dict(cadastros=cad,avaliados=assessed,validas=valid,ausentes=missing,
                acertos=n,oportunidades=d,taxa_observada=rate,taxa=None if partial else rate,
                fracao_observada=dict(numerador=n,denominador=d) if d else None,
                proveniencia_sha256=hashlib.sha256('\n'.join(sorted(raw_groups[group])).encode('utf-8')).hexdigest()))
    return dict(resultados=sorted(result,key=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False)),
                observacoes_conferidas=len(rows),metodo='SQL+Fraction_independente')


def auditar_resultados(rows: list[dict], resultados: list[dict]) -> dict:
    """Compara valores, máscaras, contextos e digest de todas as linhas de origem."""
    reference = contraprovar(rows)['resultados']
    ordered = sorted(resultados,key=lambda x:json.dumps(x,sort_keys=True,ensure_ascii=False))
    if reference != ordered:
        raise ValueError('Divergencia de resultado ou proveniencia; detalhes restritos')
    return dict(coincide=True,grupos_conferidos=len(reference),observacoes_conferidas=len(rows))
