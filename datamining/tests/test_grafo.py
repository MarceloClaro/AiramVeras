"""T32-T34: hand-derived expectations; synthetic identifiers only."""
import importlib
import importlib.util
import numpy as np
import pytest


def api(name):
    assert importlib.util.find_spec('airam.grafo'), 'Funcionalidade de grafo ainda ausente'
    fn = getattr(importlib.import_module('airam.grafo'), name, None)
    assert callable(fn), 'Funcionalidade de grafo ainda ausente'
    return fn


def edge(node, bncc, position=None, **changes):
    row = dict(ocorrencia_id=node, codigo_bncc=bncc, posicao_id=position or node,
        posicao=position or node, avaliacao_id='SINTETICO', ano_avaliacao=2026,
        ano_avaliado=1, ciclo_avaliado='I', componente='LEITURA',
        fonte_posicao='mapa', versao_posicao='v1', fonte_matriz='pdf', sha256_pdf='v1',
        peso_analitico=1, status_bncc='confirmado',
        status_contextual='proprio_ano_ciclo_confirmado',
        status_semantico='associacao_publicada_sem_equivalencia_integral',
        bncc={'proveniencia_dataset': {'documento':'bncc', 'commit':'v1'}})
    row.update(changes)
    return row


def test_t32_many_edges_and_duplicates_do_not_multiply_mass():
    rows = [edge('a', b) for b in ['x','y','z']] + [edge('b','x')]
    graph = api('construir_bipartida')(rows + [rows[0]], 'ressalvada')
    np.testing.assert_allclose(graph['B'], [[1/3]*3,[1,0,0]])
    np.testing.assert_allclose(graph['A'], [[0,1],[1,0]])
    np.testing.assert_allclose(graph['W'], [[1/3,1/3],[1/3,1]])


def test_t32_uncertain_and_semantic_policies_preserve_isolated_nodes():
    rows = [edge('a','x'), edge('b','x', status_semantico='associacao_publicada_com_ressalva_semantica'),
        edge('c','x', peso_analitico=0, status_contextual='fonte_anterior_integracao_a_confirmar')]
    g = api('construir_bipartida')(rows,'estrita')
    np.testing.assert_allclose(g['B'].sum(axis=1), [1,0,0])
    assert not g['A'].any()
    g = api('construir_bipartida')(rows,'ressalvada')
    np.testing.assert_allclose(g['B'].sum(axis=1), [1,1,0])


def test_t32_mixed_contexts_or_conflicting_duplicate_rejected():
    fn = api('construir_bipartida')
    with pytest.raises(ValueError):
        fn([edge('a','x'),edge('b','x', ano_avaliado=2)], 'estrita')
    with pytest.raises(ValueError):
        fn([edge('a','x'),edge('a','x', peso_analitico=0)], 'estrita')
    with pytest.raises(ValueError):
        fn([edge('a','x')], 'desconhecida')


def test_t33_manual_weighted_mask_zero_is_observed_and_isolated_absent():
    a = np.array([[0,.25,.75,0],[1,0,0,0],[1,0,0,0],[0,0,0,0]])
    p = np.array([[.2,0,np.nan,.9],[np.nan]*4])
    mask = np.isfinite(p)
    result = api('propagar')(p,mask,a,1)
    np.testing.assert_allclose(result['propagado'][0], [0,.2,.2,np.nan], equal_nan=True)
    np.testing.assert_allclose(result['cobertura'][0], [.25,1,1,0])
    assert np.isnan(result['propagado'][1]).all()
    assert result['fontes_distintas'][0].tolist() == [1,1,1,0]
    np.testing.assert_equal(p, result['observado'])
    assert not np.shares_memory(p,result['observado'])


def test_t34_two_steps_use_original_mask_and_expose_return():
    a = np.array([[0,1,0],[.5,0,.5],[0,1,0]])
    p = np.array([[1,np.nan,0]])
    r = api('propagar')(p,np.isfinite(p),a,2)
    np.testing.assert_allclose(r['propagado'], [[.5,np.nan,.5]], equal_nan=True)
    np.testing.assert_allclose(r['massa_retorno'], [[.5,0,.5]])
    np.testing.assert_allclose(r['sem_retorno'], [[0,np.nan,1]], equal_nan=True)
    np.testing.assert_allclose(r['cobertura_sem_retorno'], [[.5,0,.5]])
    assert not r['observado_mask'][0,1]
    pair = api('propagar')(np.array([[.3,.8]]),np.ones((1,2),bool),np.array([[0,1],[1,0]]),2)
    np.testing.assert_allclose(pair['propagado'], [[.3,.8]])
    assert np.isnan(pair['sem_retorno']).all()


def test_t34_consistent_column_permutation_is_equivariant():
    p = np.array([[0,.4,1]])
    a = np.array([[0,.3,.7],[1,0,0],[1,0,0]])
    order = [2,0,1]
    fn = api('propagar')
    r = fn(p,np.isfinite(p),a,2)
    other = fn(p[:,order],np.isfinite(p[:,order]),a[np.ix_(order,order)],2)
    np.testing.assert_allclose(other['propagado'],r['propagado'][:,order],equal_nan=True)


@pytest.mark.parametrize('a,mask,steps', [([[1,0],[0,1]],[[True,True]],1),
    ([[0,-1],[1,0]],[[True,True]],1), ([[0,.5],[1,0]],[[True,True]],1),
    ([[0,1],[1,0]],[[1,1]],1), ([[0,1],[1,0]],[[True,True]],3)])
def test_t33_invalid_graph_mask_or_steps_rejected(a,mask,steps):
    with pytest.raises(ValueError):
        api('propagar')(np.array([[0,1]]),np.array(mask),np.array(a),steps)


def test_evidence_retains_original_counts_and_normalizes_occurrence_fanout():
    graph = api('construir_bipartida')([edge('a','x','H1'),edge('a','y','H1'),edge('b','z','H1')], 'estrita')
    rows = [dict(aluno_local_id='SINTETICO',posicao='H1',numerador=2,denominador=4,
                 disponibilidade=True,participacao=True)]
    r = api('matrizes_evidencia')(rows, ['H1','H2'], graph)
    np.testing.assert_allclose(r['C'], [[2,np.nan]],equal_nan=True)
    np.testing.assert_allclose(r['D'], [[4,np.nan]],equal_nan=True)
    np.testing.assert_allclose(r['C_alocada'], [[1,1]])
    np.testing.assert_allclose(r['D_alocada'], [[2,2]])
    np.testing.assert_allclose(r['P_ocorrencias'], [[.5,.5]])
