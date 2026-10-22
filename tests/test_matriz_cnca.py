"""T27/T31: regressões documentais públicas, sem dados de participantes."""
import importlib
import importlib.util
from functools import lru_cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT.parent / 'MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf'
COMMIT = '9c268978efa2aa250834c6a9edb6074432752838'


def api(module, name):
    # Ausência é falha funcional controlada; o MESMO teste exerce a API futura.
    assert importlib.util.find_spec('airam.' + module) is not None, f'Funcionalidade ausente: {module}.{name}'
    value = getattr(importlib.import_module('airam.' + module), name, None)
    assert callable(value), f'Funcionalidade ausente: {module}.{name}'
    return value


@lru_cache(maxsize=1)
def extrair():
    return api('matriz_cnca', 'extrair_ocorrencias')(PDF)


def test_inventario_real_tem_ocorrencias_independentes_com_proveniencia():
    ocorrencias = extrair()
    # Remover continuação, colapsar códigos ou invadir escrita/fluência quebra isto.
    assert len(ocorrencias) == 202
    assert len({o['codigo_caed'] for o in ocorrencias}) == 131
    assert len({o['ocorrencia_id'] for o in ocorrencias}) == 202
    assert all(o['texto_caed'] and o['codigos_bncc'] and o['ciclos'] for o in ocorrencias)
    assert all(o['sha256_pdf'] == '2728d640c98510ff323cb542282ffc51db8288c021560aa55cac7b908c5f5f0e' for o in ocorrencias)


@pytest.mark.parametrize('codigo,ano,want', [
    ('3EF06_M', 3, ['EF02MA06', 'EF03MA05']),
    ('3EF06_M', 4, ['EF03MA05']),
    ('3EF07_M', 3, ['EF02MA06', 'EF03MA06']),
    ('3EF07_M', 4, ['EF03MA06']),
    ('3EF07_M', 5, ['EF03MA06']),
    ('3EF09_M', 3, ['EF02MA06', 'EF03MA06']),
    ('3EF09_M', 4, ['EF03MA06']),
    ('3EF09_M', 5, ['EF03MA06']),
    ('4EF07_M', 4, ['EF02MA07', 'EF03MA07', 'EF04MA06']),
    ('4EF07_M', 5, ['EF04MA06']),
])
def test_T27_conjunto_bncc_pertence_a_celula_contextual(codigo, ano, want):
    ocorrencias = extrair()
    found = [o for o in ocorrencias if o['codigo_caed'] == codigo and o['ano_tabela'] == ano]
    assert len(found) == 1
    assert found[0]['codigos_bncc'] == want


def test_T31_x_deslocado_pagina7_pertence_a_celula_ciclo_i():
    ocorrencias = extrair()
    row = next(o for o in ocorrencias if o['pagina_matriz'] == 7 and o['codigo_caed'] == '3EF16_P')
    assert 'I' in row['ciclos']
    marca = next(m for m in row['marcas_ciclo'] if m['ciclo'] == 'I')
    assert 554 < marca['bbox'][0] < 560  # literal conferido da fonte, distante do centro usual
    assert row['celulas']['I'][0] <= marca['bbox'][0] < row['celulas']['I'][2]


def test_bncc_canonica_preserva_texto_e_localizador_separado():
    data = api('bncc', 'carregar_bncc')(ROOT.parent / 'bncc-dados', COMMIT)
    row = data['EF01LP02']
    assert row['texto'].startswith('Escrever, espontaneamente')
    assert row['fonte']['localizador_pdf'] == 'Base-Nacional-Comum-Curricular-BNCC.pdf, página PDF 101'
    assert row['proveniencia_dataset']['commit'] == COMMIT
    assert len(data) > 1200


def test_bncc_recusa_commit_divergente():
    with pytest.raises(ValueError, match='commit'):
        api('bncc', 'carregar_bncc')(ROOT.parent / 'bncc-dados', '0' * 40)
