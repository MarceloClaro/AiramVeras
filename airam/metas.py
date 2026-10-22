"""Metas aritméticas separadas, sem inferir cortes CAEd ou eficácia de intervenção."""
from fractions import Fraction


def _target(total, meta):
    try:
        ratio = Fraction(str(meta))
    except (ValueError,TypeError,ZeroDivisionError):
        raise ValueError('Meta invalida') from None
    if not 0 <= ratio <= 1:
        raise ValueError('Meta fora do intervalo')
    return -(-(total * ratio.numerator) // ratio.denominator)


def meta_adequados(avaliados: int, adequados: int, meta: float) -> dict:
    if type(avaliados) is not int or type(adequados) is not int or not 0 <= adequados <= avaliados:
        raise ValueError('Contagens de avaliados/adequados invalidas')
    target = _target(avaliados,meta)
    return dict(meta='A',avaliados=avaliados,adequados=adequados,
        alvo=target if avaliados else None,conversoes=max(0,target-adequados) if avaliados else None,
        atingida=adequados >= target if avaliados else None,acertos_ate_adequacao=None,
        status='disponivel' if avaliados else 'sem_avaliados')


def meta_acertos(acertos: int, oportunidades: int, meta: float) -> dict:
    _target(0,meta)
    if acertos is None and oportunidades is None:
        return dict(meta='B',alvo=None,lacuna=None,atingida=None,status='prova_ausente')
    if type(acertos) is not int or type(oportunidades) is not int or oportunidades <= 0 or not 0 <= acertos <= oportunidades:
        raise ValueError('Contagens individuais invalidas')
    target = _target(oportunidades,meta)
    return dict(meta='B',alvo=target,lacuna=max(0,target-acertos),atingida=acertos >= target,status='disponivel')


def corte_empirico(rows: list[dict]) -> dict:
    """Mínimo observado, sempre hipótese; nunca fornece acertos até adequação."""
    values = [r['acertos'] for r in rows if r.get('categoria') == 'Adequado' and r.get('acertos') is not None]
    return dict(valor=min(values) if values else None,status='hipotese_empirica_nao_oficial',acertos_ate_adequacao=None)
