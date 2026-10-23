"""O handoff precisa executar a integração e publicar somente agregados."""
import importlib.util
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]


def test_T48_handoff_real_com_regras_sem_inventar_clusters():
    # Catches collectors that expose labels/members, lose source totals, or ship only APIs.
    path=ROOT/'evidencias/T08/analisar.py'
    assert path.exists(), 'Coletor de entrega T08 ausente'
    spec=importlib.util.spec_from_file_location('coletor_t08',path)
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    from test_clusters import config
    from test_perfis_grupo import fixture
    _,rows,links=fixture()
    apps=[]
    for i in range(6):
        app={k:rows[0][k] for k in module.CONTEXTO}
        app.update(aluno_local_id=f's{i}',avaliacao_local_id=f'ap{i}',turma='A',participacao=True,
                   categoria='Adequado',oportunidades=4)
        apps.append(app)
    for r in rows: r['avaliacao_local_id']='ap'+r['aluno_local_id'][1:]
    ctx={k:rows[0][k] for k in module.CONTEXTO}
    matrix=dict(alunos=[f's{i}' for i in range(6)],posicoes=['H1','H2'],
                P=[[0,1]]*6,D=[[2,2]]*6,Q=[[1,0],[0,1]])
    propagations={str(s):dict(propagado=[[1,0]]*6 if s==1 else [[0,1]]*6,
        sem_retorno=[[1,0]]*6 if s==1 else [[None,None]]*6,massa_retorno=[[0,0]]*6 if s==1 else [[1,1]]*6)
        for s in (1,2)}
    block=dict(contexto=ctx,policy='ressalvada',matrizes=matrix,propagacoes=propagations)
    import copy, json
    strict=copy.deepcopy(block); strict['policy']='estrita'
    private,public=module.produzir(
        dict(observado=dict(habilidades=rows,avaliacoes=apps,escrita=[],fluencia=[])),
        dict(blocos=[block,strict]),
        dict(blocos=[dict(contexto=ctx,policy=p,grafo={'A':[[0,1],[1,0]]}) for p in ('estrita','ressalvada')]),
        dict(vinculos_posicoes=links),config())
    assert len(private['instrumentos'])==1 and len(public['instrumentos'])==1
    profile=public['instrumentos'][0]['perfis_regras'][0]
    assert profile['observado']['acertos']==12 and profile['observado']['oportunidades']==24
    assert public['instrumentos'][0]['observado_operacional']['status']=='sem_agrupamento_estavel'
    serialized=json.dumps(public)
    assert all(f's{i}' not in serialized for i in range(6))
    assert '"membros"' not in serialized and '"rotulos"' not in serialized and '"valores"' not in serialized
    assert private['instrumentos'][0]['regras']['grupos'][0]['membros']==[f's{i}' for i in range(6)]
    assert len(public['instrumentos'][0]['cenarios'])==5
