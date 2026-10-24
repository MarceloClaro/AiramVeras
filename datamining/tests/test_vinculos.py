"""T26–T30: vínculos não transportam resultados nem fundem contextos."""
from copy import deepcopy
import csv

import pytest

from test_matriz_cnca import ROOT, PDF, COMMIT, api


def pos(ano=3, codigo='3EF06_M', componente='MATEMATICA', **kw):
    return dict(avaliacao_id='AV12026', ano_avaliacao=2026, ano_escolar=ano,
                componente=componente, posicao='H 01', codigo_caed_observado=codigo,
                ciclo='I', fonte_posicao='fixture_publica', versao_posicao='v1', **kw)


def occurrence(ano=3, codigo='3EF06_M', componente='MATEMATICA', codes=None,
               texto='Descritor contextual A', pagina=23, ciclos=None):
    return dict(ocorrencia_id=f'publica:{ano}:{pagina}:{codigo}', ano_tabela=ano,
                codigo_caed=codigo, componente=componente, codigos_bncc=codes or ['EF03MA05'],
                texto_caed=texto, pagina_matriz=pagina, ciclos=ciclos or ['I'],
                fonte_matriz='matriz.pdf', sha256_pdf='a' * 64, nota_integracao=None)


def normative(code='EF03MA05', status='vigente'):
    return dict(codigo=code, texto='Texto normativo ' + code, vigencia={'status': status},
                fonte={'localizador_pdf': {'pagina': 285}}, componente='Matemática', anos=[3])


def link(positions, occurrences, bncc=None):
    return api('vinculos', 'vincular_posicoes')(positions, occurrences,
              bncc if bncc is not None else {'EF03MA05': normative()})


def test_T26_h01_nao_confunde_ano_componente_ou_avaliacao():
    positions = [pos(), pos(4), pos(3, '3EF06_P', 'LEITURA')]
    occurrences = [occurrence(), occurrence(4, texto='Descritor B', pagina=25),
                   occurrence(3, '3EF06_P', 'LEITURA', texto='Ler frases.', pagina=6)]
    result = link(positions, occurrences)
    assert len({v['posicao_id'] for v in result}) == 3
    assert [(v['ano_avaliado'], v['ano_tabela'], v['texto_caed']) for v in result] == [
        (3, 3, 'Descritor contextual A'), (4, 4, 'Descritor B'), (3, 3, 'Ler frases.')]


def test_T27_nao_une_conjuntos_de_anos_ou_textos_divergentes():
    occurrences = [occurrence(codes=['EF02MA06', 'EF03MA05']),
                   occurrence(4, texto='Outro texto oficial', pagina=25)]
    result = link([pos(4)], occurrences,
                  {'EF02MA06': normative('EF02MA06'), 'EF03MA05': normative()})
    assert [(v['codigo_bncc'], v['texto_caed'], v['pagina_matriz']) for v in result] == [
        ('EF03MA05', 'Outro texto oficial', 25)]


def test_T28_fonte_anterior_nao_vira_ocorrencia_5_ano():
    result = link([pos(5, '3EF11_M')], [occurrence(3, '3EF11_M'), occurrence(4, '3EF11_M', pagina=26)])
    assert {v['ano_tabela'] for v in result} == {3, 4}
    assert all(v['status_contextual'] == 'fonte_anterior_integracao_a_confirmar' for v in result)
    assert all(v['peso_analitico'] == 0 and v['ano_avaliado'] == 5 for v in result)


@pytest.mark.parametrize('bncc', [{}, {'EF03MA05': normative(status='inativo')}])
def test_T29_inexistente_ou_inativo_permanece_nao_confirmado(bncc):
    row = link([pos()], [occurrence()], bncc)[0]
    assert row['codigo_bncc'] == 'EF03MA05'
    assert row['status_bncc'] == 'nao_confirmado'
    assert row['peso_analitico'] == 0


def test_T30_ressalva_semantica_preserva_os_dois_textos():
    result = link([pos(1, '1EF10_P', 'LEITURA')],
                  [occurrence(1, '1EF10_P', 'LEITURA', ['EF01LP02'], 'Ler frases.', 4)],
                  {'EF01LP02': normative('EF01LP02')})
    assert result[0]['status_semantico'] == 'associacao_publicada_com_ressalva_semantica'
    assert result[0]['texto_caed'] == 'Ler frases.'
    assert result[0]['texto_bncc'] == 'Texto normativo EF01LP02'
    assert result[0]['ressalva']
    assert result[0]['localizador_bncc']['localizador_pdf']['pagina'] == 285
    assert result[0]['pagina_matriz'] == 4


def test_multimapeamento_tem_peso_unitario_sem_resultados_replicados():
    p = pos(acertos=2, oportunidades=3)
    original = deepcopy(p)
    rows = link([p], [occurrence(codes=['EF03MA05', 'EF02MA06'])],
                {'EF03MA05': normative(), 'EF02MA06': normative('EF02MA06')})
    assert [r['peso_analitico'] for r in rows] == [.5, .5]
    assert all('acertos' not in r and 'oportunidades' not in r for r in rows)
    assert p == original


def test_ciclo_sem_marca_nao_confirma_e_posicao_sem_fonte_tem_cobertura_explicita():
    rows = link([pos(), pos(5, '5EF99_M')], [occurrence(ciclos=['II'])])
    assert rows[0]['status_contextual'] == 'ciclo_nao_assinalado'
    assert rows[0]['peso_analitico'] == 0
    assert rows[1]['status_contextual'] == 'sem_ocorrencia_contextual'


def test_rejeita_posicao_duplicada_em_vez_de_multiplicar():
    with pytest.raises(ValueError, match='duplicada'):
        link([pos(), pos()], [occurrence()])


def test_rejeita_ocorrencia_repetida_em_vez_de_duplicar_arestas():
    with pytest.raises(ValueError, match='ocorrencia duplicada'):
        link([pos()], [occurrence(), occurrence()])


def test_rejeita_bncc_repetida_na_mesma_celula_em_vez_de_duplicar_arestas():
    with pytest.raises(ValueError, match='BNCC duplicado'):
        link([pos()], [occurrence(codes=['EF03MA05', 'EF03MA05'])])


def test_fonte_ou_versao_de_posicao_nao_desaparece_da_identidade():
    rows = link([pos(), dict(pos(), versao_posicao='v2'), dict(pos(), avaliacao_id='AV22026')], [occurrence()])
    assert len({r['posicao_id'] for r in rows}) == 3
    assert len({r['vinculo_id'] for r in rows}) == 3


def test_conferencia_real_cobre_124_posicoes_e_ressalva_6_excecoes():
    occurrences = api('matriz_cnca', 'extrair_ocorrencias')(PDF)
    bncc = api('bncc', 'carregar_bncc')(ROOT.parent / 'bncc-dados', COMMIT)
    path = ROOT.parent / 'resultados-caed-ciclo-i-2026/conferencia/mapa_posicao_codigo_caed.csv'
    with path.open(encoding='utf-8-sig', newline='') as stream:
        positions = [dict(row, ano_escolar=int(row['ano_escolar']), ano_avaliacao=2026,
                          ciclo='I', fonte_posicao=path.name, versao_posicao='fixture_real')
                     for row in csv.DictReader(stream, delimiter=';')]
    rows = link(positions, occurrences, bncc)
    assert len(positions) == len({v['posicao_id'] for v in rows}) == 124
    assert len({p['codigo_caed_observado'] for p in positions}) == 93
    assert len({v['posicao_id'] for v in rows if v['status_contextual'] == 'proprio_ano_ciclo_confirmado'}) == 118
    exceptions = {v['codigo_caed'] for v in rows if v['status_contextual'] == 'fonte_anterior_integracao_a_confirmar'}
    assert exceptions == {'3EF09_P', '3EF15_P', '4EF10_P', '3EF11_M', '3EF12_M', '3EF17_M'}
    assert all(v['status_bncc'] == 'confirmado' for v in rows)
    observed = {p['codigo_caed_observado'] for p in positions}
    union = {c for o in occurrences if o['codigo_caed'] in observed for c in o['codigos_bncc']}
    assert len(union) == 73
    assert union <= bncc.keys()
