"""T35/T36: deduplication and no ecological assignment."""
import importlib
import importlib.util
import pytest


def api():
    assert importlib.util.find_spec('airam.agregacoes'), 'Agregacao multinivel ainda ausente'
    return importlib.import_module('airam.agregacoes').agregar_observacoes


def row(student,n,d,position='H1',**changes):
    r = dict(aluno_local_id=student, avaliacao_local_id=student+'-app', turma='A',
        avaliacao_id='SINTETICO',ano_avaliacao=2026,ciclo='I',ano_escolar=1,
        componente='LEITURA',fonte_id='csv',sha256='v1',exportacao='v1',posicao=position,
        numerador=n,denominador=d,participacao=True,disponibilidade=n is not None,
        unidade='acertos_itens')
    r.update(changes)
    return r


def test_t35_overlapping_groups_school_deduplicates_and_uses_ratio_of_sums():
    rows = [row('s1',1,1), row('s2',0,3), row('s3',1,2)]
    groups = [{'grupo_id':'g1','membros':['s1','s2']},{'grupo_id':'g2','membros':['s2','s3']}]
    fn = api()
    views = fn(rows,'grupo',groups)
    assert [(r['acertos'],r['oportunidades'],r['avaliados']) for r in views] == [(1,4,2),(1,5,2)]
    school = fn(rows+[rows[1]],'escola',groups)[0]
    assert (school['acertos'],school['oportunidades'],school['avaliados']) == (2,6,3)
    assert school['taxa_observada'] == 1/3
    assert 'aluno_local_id' not in school and 'membros' not in school


def test_t35_absence_and_zero_not_confused_and_context_kept():
    fn = api()
    rows = [row('s1',0,2),row('s2',None,None),row('s3',None,None,participacao=False)]
    r = fn(rows,'turma')[0]
    assert (r['cadastros'],r['avaliados'],r['validas'],r['ausentes']) == (3,2,1,2)
    assert r['taxa_observada'] == 0 and r['taxa'] is None
    assert len(fn(rows+[row('s1',1,2,ano_escolar=2)],'escola')) == 2


def test_t36_aggregate_cannot_be_reassigned_to_individual():
    fn = api()
    with pytest.raises(ValueError):
        fn([dict(nivel='escola',acertos=2,oportunidades=6)],'aluno')
    r = fn([row('s1',1,1),row('s2',0,3)],'aluno')
    assert sorted(x['taxa_observada'] for x in r) == [0,1]


def test_t35_conflicting_duplicates_and_changed_application_rejected():
    fn = api()
    with pytest.raises(ValueError):
        fn([row('s1',1,2),row('s1',0,2)],'escola')
    with pytest.raises(ValueError):
        fn([row('s1',1,2),row('s1',1,2,'H2',turma='B')],'escola')
