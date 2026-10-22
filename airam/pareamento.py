"""Pares cadastrais entre componentes; sem interpretação temporal implícita."""
from __future__ import annotations

from collections import Counter
from copy import deepcopy
import json

_KEY = ('aluno_local_id', 'avaliacao_id', 'ano_avaliacao', 'ciclo', 'ano_escolar')


def _key(row):
    if any(row.get(k) is None or row.get(k) == '' for k in _KEY):
        raise ValueError('Contexto de pareamento incompleto')
    return tuple(row[k] for k in _KEY)


def parear_componentes(rows: list[dict], esquerda: str, direita: str) -> tuple[list[dict], list[dict]]:
    """Um para um por aluno e contexto completo; sem fanout ou imputação.

    Universo: somente os dois componentes pedidos. Ausência de participação
    não elimina o cadastro: pares preservam máscaras para filtragem analítica.
    Duplicata na mesma chave/lado bloqueia toda a operação.
    """
    if not esquerda or not direita or esquerda == direita:
        raise ValueError('Componentes de pareamento invalidos')
    groups = {}
    for row in rows:
        component = row.get('componente')
        if component not in {esquerda, direita}:
            continue
        group = groups.setdefault(_key(row), {})
        if component in group:
            raise ValueError('Duplicata de chave e componente: pareamento bloqueado')
        group[component] = row
    pairs, unmatched = [], []
    for key, group in groups.items():
        if esquerda in group and direita in group:
            pairs.append(dict(aluno_local_id=key[0], qualidade_vinculo='local_provisorio_sem_id_institucional',
                              esquerda=deepcopy(group[esquerda]), direita=deepcopy(group[direita])))
        else:
            left = esquerda in group
            unmatched.append(dict(lado='esquerda' if left else 'direita',
                motivo='componente_direito_ausente' if left else 'componente_esquerdo_ausente',
                registro=deepcopy(group[esquerda if left else direita])))
    return pairs, unmatched


def auditar_pareamento(rows: list[dict], pares: list[dict], nao_pareados: list[dict],
                      esquerda: str, direita: str) -> dict:
    """Contraprova de conteúdo contra referência independente fornecida.

    Não chama o pareador; compara multiconjuntos de registros completos, valida
    contexto, exclusividade e motivos. Fonte adulterada também exige auditoria
    prévia contra CSV/hash; esta função não autentica a referência recebida.
    """
    if not esquerda or not direita or esquerda == direita:
        raise ValueError('Componentes de pareamento invalidos')

    def serial(row):
        return json.dumps(row, sort_keys=True, ensure_ascii=False, allow_nan=False)

    source = [r for r in rows if r.get('componente') in {esquerda, direita}]
    index = {}
    for row in source:
        key = tuple(row.get(k) for k in _KEY)
        if any(v is None or v == '' for v in key):
            raise ValueError('Contexto de referencia incompleto')
        identity = (key, row['componente'])
        if identity in index:
            raise ValueError('Duplicata na referencia independente')
        index[identity] = row
    consumed = []
    for pair in pares:
        if (set(pair) != {'aluno_local_id', 'qualidade_vinculo', 'esquerda', 'direita'}
                or pair['qualidade_vinculo'] != 'local_provisorio_sem_id_institucional'):
            raise ValueError('Adulteracao de metadados do par')
        a, b = pair.get('esquerda', {}), pair.get('direita', {})
        key_a, key_b = tuple(a.get(k) for k in _KEY), tuple(b.get(k) for k in _KEY)
        if (key_a != key_b or a.get('componente') != esquerda or b.get('componente') != direita
                or pair.get('aluno_local_id') != key_a[0]):
            raise ValueError('Adulteracao de pareamento ou contexto')
        consumed.extend([serial(a), serial(b)])
    for item in nao_pareados:
        row = item.get('registro', {})
        component = row.get('componente')
        left = component == esquerda
        other = direita if left else esquerda
        key = tuple(row.get(k) for k in _KEY)
        if (component not in {esquerda, direita} or (key, other) in index
                or item.get('lado') != ('esquerda' if left else 'direita')
                or item.get('motivo') != ('componente_direito_ausente' if left else 'componente_esquerdo_ausente')):
            raise ValueError('Adulteracao de nao pareados ou motivos')
        consumed.append(serial(row))
    if Counter(consumed) != Counter(serial(r) for r in source):
        raise ValueError('Adulteracao de valores, proveniencia ou cobertura')
    return dict(registros_consultados=len(source), pares=len(pares), nao_pareados=len(nao_pareados),
                pares_ambos_participantes=sum(p['esquerda'].get('participacao') is True
                    and p['direita'].get('participacao') is True for p in pares))
