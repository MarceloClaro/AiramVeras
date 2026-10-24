"""T48/T52: gerar artefatos reais agregados e bloquear vazamento antes da escrita."""
from copy import deepcopy
import importlib
import importlib.util
import json
from pathlib import Path
import pytest


def api():
    assert importlib.util.find_spec('airam.relatorio') is not None, 'Funcionalidade T10 ausente'
    return importlib.import_module('airam.relatorio').gerar_relatorio


def aggregate():
    return dict(versao_schema='airam-relatorio-t10-v1',fontes={'fixture':'a'*64},
        componentes=[dict(ano_escolar=2,componente='LEITURA',cadastros=5,participantes=5,com_resultado=5,unidades=['itens'])],
        metas_A=[dict(ano_escolar=2,componente='LEITURA',nivel='escola',turma=None,
            avaliados=5,adequados=3,alvo=4,conversoes=1,meta=.8)],
        habilidades=[],associacoes=[],grupos=[],cenarios=[],sensibilidade=[],diagnosticos=[],
        limites=['Sem previsão temporal validada.'],resumo={})


def test_gera_html_figuras_e_tabelas_agregadas_rastreaveis(tmp_path):
    obj=aggregate()
    paths=api()(obj,tmp_path)
    assert all(p.is_file() for p in paths)
    assert (tmp_path/'relatorio.html') in paths
    assert (tmp_path/'figuras/meta-a.png') in paths
    assert (tmp_path/'figuras/meta-a.svg') in paths
    # Metadados tabulares permitem recuperar denominadores sem extrair texto de PNG.
    table=json.loads((tmp_path/'tabelas.json').read_text(encoding='utf-8'))
    assert table['metas_A'][0]['avaliados']==5 and table['metas_A'][0]['conversoes']==1
    html=(tmp_path/'relatorio.html').read_text(encoding='utf-8')
    assert 'figuras/meta-a.svg' in html


@pytest.mark.parametrize('field',['nome','nome_bruto','aluno_local_id','avaliacao_local_id','membros','origens'])
def test_t52_bloqueia_identidade_aninhada_antes_de_escrever(tmp_path,field):
    obj=aggregate();obj['resumo']={'aninhado':[{field:'IDENTIDADE ARTIFICIAL'}]}
    with pytest.raises(ValueError,match='privacidade'):
        api()(obj,tmp_path)
    assert not list(tmp_path.iterdir())


def test_t48_perfil_sem_fonte_ou_descricao_curricular_bloqueia_entrega(tmp_path):
    obj=aggregate();obj['grupos']=[{'grupo_id':'regra','n':5,'ano_escolar':2,'componente':'LEITURA'}]
    with pytest.raises(ValueError,match='perfil incompleto'):
        api()(obj,tmp_path)
    assert not list(tmp_path.iterdir())


def test_nao_modifica_entrada_e_escapa_texto_html(tmp_path):
    obj=aggregate();obj['limites'].append('<script>artificial</script>');before=deepcopy(obj)
    api()(obj,tmp_path)
    assert obj==before
    assert '<script>artificial</script>' not in (tmp_path/'relatorio.html').read_text(encoding='utf-8')


def test_perfil_pequeno_conserva_supressao_sem_exigir_revelacao(tmp_path):
    obj=aggregate();obj['grupos']=[dict(versao='fixture',contexto={'ano_escolar':2,'componente':'LEITURA'},
        grupo_id='grupo',tipo='regra',n_intervalo='1-4',status_publicacao='suprimido_n_menor_5',revisao_docente='pendente')]
    api()(obj,tmp_path)
    out=json.loads((tmp_path/'tabelas.json').read_text(encoding='utf-8'))
    assert out['grupos'][0]['n_intervalo']=='1-4'
    assert 'n' not in out['grupos'][0]
