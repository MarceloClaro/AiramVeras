"""Parsing estrito de medidas CAEd, sem imputação nem equivalência de escalas."""
from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re


def validar_esquema(header: list[str], familia: str, nivel: str, avaliacao: dict) -> None:
    """Contrato dos 36 cabeçalhos observados de AV12026/I/2026.

    Campos de resultado e identificação são estruturais, mesmo quando todas as
    células têm hífen. Não há colunas opcionais neste contrato. A única
    alternativa é Turmma/Turma nos individuais de escrita/fluência. Colunas ou
    contextos novos exigem revisão explícita de esquema, não parsing por acaso.
    """
    if (avaliacao.get('avaliacao_id'), avaliacao.get('ano_avaliacao'), avaliacao.get('ciclo')) != ('AV12026', 2026, 'I'):
        raise ValueError('Esquema sem contrato para o contexto da avaliacao')
    year, component = avaliacao.get('ano_escolar'), avaliacao.get('componente')
    required = set()
    if familia == 'habilidades':
        counts = {'LEITURA': {1: 9, 2: 11, 3: 11, 4: 13, 5: 16},
                  'MATEMATICA': {1: 7, 2: 11, 3: 12, 4: 15, 5: 19}}
        count = counts.get(component, {}).get(year)
        if count is None:
            raise ValueError('Esquema sem contrato para ano e componente')
        required.update(['Rede', 'Ano Escolar', 'Componente Curricular', 'Estado', 'Município'])
        if nivel == 'estudante':
            required.update(['Código da Turma', 'Turma', 'Estudante', 'Avaliado', 'Nível de aprendizagem'])
            required.update(f'H {i:02}' for i in range(1, count + 1))
        else:
            required.update(['Avaliados (%)', 'Defasagem', 'Aprendizado intermediário', 'Aprendizado adequado'])
            required.update(f'H {i:02} (%)' for i in range(1, count + 1))
            required.update(['Regional', 'Escola'] if nivel == 'escola'
                            else ['Código da Escola', 'Código da Turma', 'Turma'])
    elif familia in {'escrita', 'fluencia'} and year in {2, 3, 4, 5}:
        if familia == 'escrita':
            aspects = {2: [(1, 1), (1, 2), (2, 1), (2, 2), (3, 1)],
                       3: [(1, 1), (2, 1), (3, 1), (3, 2), (4, 1), (4, 2), (4, 3), (4, 4)],
                       4: [(1, 1), (1, 2), (1, 3), (1, 4)],
                       5: [(1, 1), (1, 2), (1, 3), (1, 4)]}[year]
            required.update(f'Questão {q} - Aspecto {a}' for q, a in aspects)
            if nivel == 'estudante':
                required.update(['Nota', 'Categoria de escrita'])
            else:
                required.add('Nota média')
                required.update(['Inadequado', 'Muito baixo', 'Baixo', 'Médio', 'Alto'] if year < 4
                    else ['Inadequado', 'Insuficiente', 'Insatisfatório', 'Intermediário', 'Satisfatório', 'Avançado'])
        elif nivel == 'estudante':
            required.update(['Perfil de leitor', 'Palavras (leitura global)', 'Palavras possivelmente desconhecidas',
                             'Texto (Palavras corretas)', 'Texto (Compreensão)'])
        else:
            required.update(['Pré-leitor (Total)', 'Pré-leitor (Nível 1)', 'Pré-leitor (Nível 2)',
                             'Pré-leitor (Nível 3)', 'Pré-leitor (Nível 4)', 'Leitor Iniciante', 'Leitor Fluente'])
        if nivel == 'estudante':
            aliases = set(header) & {'Turmma', 'Turma'}
            if len(aliases) != 1:
                raise ValueError('Coluna de turma ausente ou ambigua no esquema')
            required.update(aliases | {'Estudante', 'Participação'})
        else:
            required.update(['Previstos', 'Avaliados', '% Participação'])
            required.update(['Escola'] if nivel == 'escola' else
                ['Turma', 'Código do estado' if familia == 'escrita' else 'Código da escola'])
    else:
        raise ValueError('Esquema sem contrato para familia e ano')
    if not required.issubset(header):
        raise ValueError('Coluna obrigatoria ausente no esquema')
    if set(header) - required:
        raise ValueError('Coluna sem contrato no esquema')


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
