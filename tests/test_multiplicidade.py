"""T17: BH planejado, valores ausentes, família e correções independentes."""
from importlib import util, import_module
import pytest
from scipy.stats import false_discovery_control


def api(name):
    assert util.find_spec('airam.correlacoes') is not None, 'Funcionalidade de multiplicidade ausente'
    fn=getattr(import_module('airam.correlacoes'),name,None)
    assert callable(fn), 'Funcionalidade de multiplicidade ausente'
    return fn


def test_T17_bh_confronto_scipy_e_valores_literais():
    ps=[.01,.04,.03,.002]
    assert api('ajustar_bh')(ps)==pytest.approx([.02,.04,.04,.008])
    assert api('ajustar_bh')(ps)==pytest.approx(false_discovery_control(ps))


def test_T17_ausencia_preserva_m_planejado_sem_q_zero():
    assert api('ajustar_bh')([.01,None,.04])==[.03,None,.06]
    assert api('ajustar_bh')([None,None])==[None,None]
    assert api('ajustar_bh')([])==[]


@pytest.mark.parametrize('p',[-.1,1.1,float('nan'),True])
def test_T17_recusa_p_impossivel(p):
    with pytest.raises(ValueError):api('ajustar_bh')([p])


def test_T17_familias_predeclaradas_ambos_coeficientes_e_by_global():
    rows=[dict(familia='A',p=.01,metodo='pearson'),dict(familia='A',p=None,metodo='spearman'),
          dict(familia='B',p=.04,metodo='pearson'),dict(familia='B',p=.03,metodo='spearman')]
    out=api('ajustar_familias')(rows)
    assert [r['q'] for r in out]==pytest.approx([.02,None,.04,.04],nan_ok=True)
    assert out[0]['m_planejado']==2 and out[0]['m_elegivel']==1 and out[0]['m_bh']==2
    assert out[0]['q_by']==pytest.approx(.03) and out[0]['q_bh_global']==pytest.approx(.04)
    assert out[1]['q_by'] is None and out[1]['q_bh_global'] is None
