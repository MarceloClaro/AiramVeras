"""Parsing estrito de medidas CAEd, sem imputação nem equivalência de escalas."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re


def numero(raw: str, *, percentual: bool = False, inteiro: bool = False) -> float | int:
    text = raw.strip()
    if percentual:
        text = text.removesuffix('%').strip()
    try:
        value = Decimal(text)
    except (InvalidOperation, ValueError):
        raise ValueError('Formato numerico nao reconhecido') from None
    if not value.is_finite() or value < 0 or (percentual and value > 100):
        raise ValueError('Valor numerico fora dos limites')
    if inteiro and value != value.to_integral():
        raise ValueError('Contagem deve ser inteira')
    return int(value) if inteiro else float(value)


def medida(bruto: str | None, unidade: str, participacao: bool | None,
           *, aplicavel: bool | None = None) -> dict:
    """Retém bruto, disponibilidade e participação como atributos independentes.

    Aplicabilidade só é falsa por declaração explícita. Um hífen da fonte não
    prova que a tarefa não se aplicava. Duração e denominador não são inferidos.
    """
    result = dict(bruto=bruto, numerador=None, denominador=None, valor=None,
                  unidade=unidade, participacao=participacao, aplicavel=aplicavel,
                  disponibilidade=False, motivo_ausencia=None, percentual=None,
                  percentual_unidade=None, duracao_segundos=None)
    text = '' if bruto is None else bruto.strip()
    missing = text.casefold() in {'', '-', 'sem resultado'}
    if aplicavel is False:
        if not missing:
            raise ValueError('Tarefa nao aplicavel com resultado declarado')
        result['motivo_ausencia'] = 'nao_aplicavel'
        return result
    if missing:
        result['motivo_ausencia'] = 'nao_participacao' if participacao is False else 'resultado_ausente'
        return result
    if participacao is False:
        raise ValueError('Nao participante com resultado numerico declarado')
    if unidade in {'acertos_itens', 'palavras_total'}:
        separator = '/' if unidade == 'acertos_itens' else 'de'
        match = re.fullmatch(r'\s*(\d+)\s*' + separator + r'\s*(\d+)\s*', text)
        if not match:
            raise ValueError('Par de contagens nao reconhecido')
        numerator, denominator = map(int, match.groups())
        if denominator <= 0 or numerator > denominator:
            raise ValueError('Contagens impossiveis')
        result.update(numerador=numerator, denominador=denominator, valor=numerator)
    elif unidade == 'palavras_corretas':
        match = re.fullmatch(r'(\d+)\s*-\s*(\d+(?:\.\d+)?)%', text)
        if not match:
            raise ValueError('Quantidade e percentual de palavras nao reconhecidos')
        result.update(valor=int(match[1]), unidade='palavras',
                      percentual=numero(match[2], percentual=True),
                      percentual_unidade='pontos_percentuais')
    elif unidade in {'nota_escrita', 'percentual', 'contagem'}:
        result['valor'] = numero(text, percentual=unidade == 'percentual', inteiro=unidade == 'contagem')
    else:
        raise ValueError('Unidade de medida desconhecida')
    result['disponibilidade'] = True
    return result
