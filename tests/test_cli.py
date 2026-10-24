"""T11: fixtures artificiais; ataques nomeiam falhas de contrato observáveis."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]


def api(module):
    assert importlib.util.find_spec('airam.' + module), 'Funcionalidade T11 ausente: ' + module
    return __import__('airam.' + module, fromlist=['*'])


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fixture_config(tmp_path):
    source = tmp_path / 'fontes'
    source.mkdir()
    original = source / 'original.txt'
    original.write_text('fonte artificial intacta', encoding='utf-8')
    baseline = tmp_path / 'baseline.json'
    baseline.write_text(json.dumps({'versao': 1, 'fontes': {'original.txt': sha(original)}}))
    config = tmp_path / 'analise.json'
    config.write_text(json.dumps({'spec_id':'SPEC-AIRAM-001', 'projeto': str(tmp_path),
        'raiz_fontes':'fontes', 'baseline': {'caminho':'baseline.json','sha256':sha(baseline)},
        'catalogo': {'saida':'catalogo/fontes.json', 'excluir_diretorios':[], 'excluir_arquivos':[]}}))
    return config, original


def invoke(config, command, *args):
    api('cli')
    return subprocess.run([sys.executable, '-m', 'airam', command, '--config', str(config), *args],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8')


def test_catalogo_regenerado_nao_promove_fonte_adulterada(tmp_path):
    config, original = fixture_config(tmp_path)
    assert invoke(config, 'catalogar').returncode == 0
    original.write_text('fonte adulterada')
    result = invoke(config, 'catalogar')
    assert result.returncode != 0
    assert 'fonte adulterada' not in result.stdout + result.stderr
    assert json.loads((tmp_path/'catalogo/fontes.json').read_text())[0]['sha256'] != sha(original)


def test_validar_recibo_operacional_separado_de_green(tmp_path):
    config, _ = fixture_config(tmp_path)
    result = invoke(config, 'validar')
    assert result.returncode == 0, result.stderr
    receipt = json.loads(result.stdout)
    assert receipt['tipo'] == 'operacional'
    assert receipt['codigo_saida'] == 0
    assert receipt['estado'] not in ('GREEN','RED','REFACTOR')
    assert receipt['snapshot_sha256']
    assert receipt['hooks'][0]['nome'] == 'preflight'
    assert receipt['hooks'][0]['codigo_saida'] == 0


def test_exclui_navegacao_worktrees_e_arquivo_exato(tmp_path, monkeypatch):
    api('cli')
    from airam.catalogo import catalogar
    config, _ = fixture_config(tmp_path)
    data=json.loads(config.read_text())
    data['catalogo']['excluir_diretorios']=['00_ORGANIZACAO','.airam-cenarios-t09','.airam-cli-t11']
    data['catalogo']['excluir_arquivos']=['COMECE_AQUI.lnk']
    config.write_text(json.dumps(data))
    for name in data['catalogo']['excluir_diretorios']:
        p=tmp_path/'fontes'/name; p.mkdir(); (p/'derivado.txt').write_text('derivado')
    (tmp_path/'fontes/COMECE_AQUI.lnk').write_text('atalho')
    (tmp_path/'fontes/original.lnk').write_text('original')
    monkeypatch.setenv('AIRAM_CONFIG',str(config))
    assert {r['caminho'] for r in catalogar(tmp_path/'fontes')} == {'original.txt','original.lnk'}


def test_gate_temporal_falso_mantem_analise_e_bloqueia_previsao():
    gate=api('gates').avaliar_gate('temporal',{'avaliacoes':[],'vinculos':[]})
    assert gate['codigo_saida'] == 0
    assert gate['analise_disponivel'] is True
    assert gate['previsao_temporal_validada'] is False
    assert api('gates').avaliar_gate('previsao',{'avaliacoes':[],'vinculos':[]})['codigo_saida'] != 0


def test_gate_desconhecido_falha_fechado():
    assert api('gates').avaliar_gate('desconhecido',{})['codigo_saida'] != 0


def release_fixture(tmp_path):
    producer=tmp_path/'produtor.py'; producer.write_text('# versao artificial testada')
    snapshot=tmp_path/'testes-antes.json'
    snapshot.write_text(json.dumps({'hashes_codigo':{'produtor.py':sha(producer)}}))
    log=tmp_path/'testes.log'; log.write_text('1 passed (fixture artificial)')
    receipts={}
    for kind in ['testes','contraprova','inspecao']:
        p=tmp_path/(kind+'.json'); p.write_text(json.dumps({'codigo_saida':0, 'estado':'PASS',
            'snapshot':snapshot.name,'snapshot_sha256':sha(snapshot),'log':log.name,'log_sha256':sha(log)}))
        receipts[kind]={'caminho':p.name,'sha256':sha(p)}
    output=tmp_path/'agregado.json'; output.write_text(json.dumps({'total':25}))
    return {'raiz':str(tmp_path),'recibos':receipts,'artefatos':{'agregado.json':sha(output)},
        'publicos':['agregado.json'], 'limites':['Validacao local; T02 RED historico incompleto.'],
        'rastreabilidade':[{'requisito':'R'+str(i),'testes':['T'+str(i)],
            'artefatos':['agregado.json'],'recibos':['testes']} for i in range(1,25)]}


@pytest.mark.parametrize('attack',['teste_falhou','hash','rastro','nominal','sem_inspecao'])
def test_t53_t58_release_rejeita_evidencia_incompleta_ou_vazada(tmp_path,attack):
    gates=api('gates'); fixture=release_fixture(tmp_path)
    assert gates.avaliar_gate('release',fixture)['codigo_saida']==0
    if attack=='teste_falhou':
        p=tmp_path/'testes.json'; p.write_text(json.dumps({'codigo_saida':1}))
        fixture['recibos']['testes']['sha256']=sha(p)
    elif attack=='hash': (tmp_path/'agregado.json').write_text('{}')
    elif attack=='rastro': fixture['rastreabilidade'].pop()
    elif attack=='sem_inspecao': del fixture['recibos']['inspecao']
    else:
        p=tmp_path/'agregado.json'; p.write_text(json.dumps({'detalhes':{'nome':'FICTICIO'}}))
        fixture['artefatos']['agregado.json']=sha(p)
    assert gates.avaliar_gate('release',fixture)['codigo_saida'] != 0


@pytest.mark.parametrize('axis',['entrada','codigo','config','runtime','saida'])
def test_cache_invalida_cada_dependencia_sem_promover_nova_inferencia(tmp_path,axis):
    cache=api('cache')
    for name in ['entrada','codigo','config','saida']: (tmp_path/name).write_text(name)
    manifest=cache.criar_manifesto(tmp_path,['entrada'],['codigo'],['config'],['saida'],{'python':'3.12'},'teste_artificial')
    assert cache.verificar_cache(tmp_path,manifest,{'python':'3.12'})['reutilizavel']
    runtime={'python':'3.12'}
    if axis=='runtime': runtime['python']='3.13'
    else: (tmp_path/axis).write_text('alterado')
    result=cache.verificar_cache(tmp_path,manifest,runtime)
    assert result['reutilizavel'] is False
    assert result['nova_inferencia'] is False


def test_persistencia_conserva_zero_ausencia_contexto_e_nao_duplica(tmp_path):
    module=api('persistencia')
    tables={'avaliacoes':[{'aluno_local_id':'artificial','avaliacao_local_id':'app',
        'fonte_id':'f','ano_escolar':1,'componente':'LEITURA','acertos':0,'taxa':None,
        'origens':[{'sha256':'a'*64,'linha_fonte':2}]}]}
    first=module.persistir(tables,tmp_path/'restrito/banco',tmp_path,{'fonte':'a'*64})
    assert module.persistir(tables,tmp_path/'restrito/banco',tmp_path,{'fonte':'a'*64}) == first
    import sqlite3,csv
    with sqlite3.connect(first['sqlite']) as db:
        row=db.execute('SELECT registro_json FROM avaliacoes').fetchone()
        assert json.loads(row[0]) == tables['avaliacoes'][0]
        assert db.execute('SELECT count(*) FROM avaliacoes').fetchone()[0] == 1
        assert db.execute('PRAGMA user_version').fetchone()[0] == 1
    with Path(first['csv']['avaliacoes']).open(encoding='utf-8-sig',newline='') as f:
        row=next(csv.DictReader(f)); assert row['acertos']=='0' and row['taxa']==''


@pytest.mark.parametrize('attack',['fora_restrito','nome_aninhado'])
def test_persistencia_bloqueia_nominal_e_destino_publico(tmp_path,attack):
    module=api('persistencia'); row={'aluno_local_id':'artificial'}
    target=tmp_path/'restrito/banco'
    if attack=='nome_aninhado': row['origens']=[{'nome_normalizado':'FICTICIO'}]
    else: target=tmp_path/'publico'
    with pytest.raises(ValueError): module.persistir({'avaliacoes':[row]},target,tmp_path,{'fonte':'a'*64})
    assert not target.exists()


def test_validar_verifica_esquema_real_antes_de_persistir(tmp_path,monkeypatch):
    from test_ingestao import fonte
    _,target=fonte(tmp_path,monkeypatch,sem_coluna=('ESTUDANTE','Estudante'))
    old=json.loads((tmp_path/'config.json').read_text())
    baseline=tmp_path/'baseline.json'
    baseline.write_text(json.dumps({'fontes':{p.relative_to(tmp_path/'fontes').as_posix():sha(p)
        for p in (tmp_path/'fontes').rglob('*') if p.is_file()}}))
    config=tmp_path/'analise.json'
    config.write_text(json.dumps(old|{'projeto':str(tmp_path),'baseline':{'caminho':'baseline.json','sha256':sha(baseline)}}))
    assert invoke(config,'validar').returncode != 0
    assert not (tmp_path/'restrito').exists()


def analytic_fixture(tmp_path):
    config,_=fixture_config(tmp_path)
    cfg=json.loads(config.read_text()); cfg['meta_a']={'proporcao_adequados':0.8}; cfg['meta_b']={'proporcao_acertos':0.8}
    tables={'avaliacoes':[{'aluno_local_id':'ficticio','avaliacao_local_id':'app','acertos':0,'oportunidades':22}],
        'habilidades':[],'matriculas':[{'aluno_local_id':'ficticio'}]}
    for rel,data in [('restrito/t03/tabelas.json',tables),('estatistica/t05/checkpoint.json',{'agregados':[],'metas_A':[]}),
        ('estatistica/t09/checkpoint.json',{'gate_temporal':{'previsao_temporal_validada':False,'cenarios_disponiveis':True}})]:
        p=tmp_path/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(data))
    (tmp_path/'produtor.py').write_text('# produtor artificial')
    (tmp_path/'parametros.json').write_text('{}')
    cache=api('cache')
    manifest=cache.criar_manifesto(tmp_path,['fontes/original.txt'],['produtor.py'],['parametros.json'],
        ['restrito/t03/tabelas.json','estatistica/t05/checkpoint.json','estatistica/t09/checkpoint.json'],
        cache.runtime(),'execucao_artificial_previa')
    manifest['parametros']={'meta_a':cfg['meta_a'],'meta_b':cfg['meta_b']}
    p=tmp_path/'cache.json'; p.write_text(json.dumps(manifest))
    cfg['cache_analise']={'caminho':'cache.json','sha256':sha(p)}
    config.write_text(json.dumps(cfg)); return config


def test_analisar_reusa_autenticado_e_grava_sqlite_csv_sem_dados_stdout(tmp_path):
    config=analytic_fixture(tmp_path)
    result=invoke(config,'analisar')
    assert result.returncode==0, result.stdout
    receipt=json.loads(result.stdout)
    assert receipt['resultado']['modo']=='reutilizacao_autenticada'
    assert receipt['resultado']['nova_inferencia'] is False
    assert len(list((tmp_path/'restrito').rglob('analise.sqlite3')))==1
    assert 'ficticio' not in result.stdout


def test_analisar_nao_reutiliza_meta_diferente(tmp_path):
    config=analytic_fixture(tmp_path)
    cfg=json.loads(config.read_text()); cfg['meta_b']['proporcao_acertos']=0.9
    config.write_text(json.dumps(cfg))
    assert invoke(config,'analisar').returncode!=0
    assert not list((tmp_path/'restrito').rglob('analise.sqlite3'))


def test_release_csv_nominal_sem_mapa_nao_passa(tmp_path):
    fixture=release_fixture(tmp_path); p=tmp_path/'vazamento.csv'
    p.write_text('nome,total\nPESSOA ARTIFICIAL,2\n')
    fixture['artefatos'][p.name]=sha(p); fixture['publicos'].append(p.name)
    assert api('gates').avaliar_gate('release',fixture)['codigo_saida']!=0


def test_snapshot_cli_autentica_fontes_antes_da_execucao(tmp_path):
    config,original=fixture_config(tmp_path)
    assert invoke(config,'validar').returncode==0
    before=[json.loads(p.read_text()) for p in (tmp_path/'evidencias/operacionais').rglob('antes.json')]
    assert any(b.get('entradas',{}).get('original.txt')==sha(original) for b in before)


def test_persistencia_inclui_derivados_sem_renomear_nomes_individuais(tmp_path):
    config=analytic_fixture(tmp_path)
    cfg=json.loads(config.read_text()); manifest=json.loads((tmp_path/'cache.json').read_text())
    derived={
        'restrito/t05/checkpoint.json':{'metricas_alunos':[{'aluno_local_id':'ficticio','acertos':0}],
            'metas_individuais':[{'aluno_local_id':'ficticio','meta_B':{'lacuna':18}}]},
        'restrito/t07/checkpoint.json':{'blocos':[{'observado':[[0,None]],'mask':[[True,False]]}],
            'visoes_aluno':[{'aluno_local_id':'ficticio','derivado':0.5}]},
        'restrito/t08/checkpoint.json':{'instrumentos':[{'perfis_regras':[{'nome':'PERFIL ARTIFICIAL','n':5}]}],
            'unidades_proprias':[]},
        'restrito/t09/checkpoint.json':{'cenarios_individuais':[{'aluno_local_id':'ficticio','hipotese':0.1}],
            'outros_instrumentos':[]}}
    for rel,obj in derived.items():
        p=tmp_path/rel; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj))
        manifest['saidas'][rel]=sha(p)
    (tmp_path/'cache.json').write_text(json.dumps(manifest)); cfg['cache_analise']['sha256']=sha(tmp_path/'cache.json')
    config.write_text(json.dumps(cfg))
    result=invoke(config,'analisar'); assert result.returncode==0,result.stdout
    import sqlite3
    dbpath=next((tmp_path/'restrito').rglob('analise.sqlite3'))
    with sqlite3.connect(dbpath) as db:
        assert db.execute('SELECT count(*) FROM t05_metas_individuais').fetchone()[0]==1
        assert json.loads(db.execute('SELECT registro_json FROM t07_blocos').fetchone()[0])['mask']==[[True,False]]
        profile=json.loads(db.execute('SELECT registro_json FROM t08_instrumentos').fetchone()[0])['perfis_regras'][0]
        assert profile['titulo_perfil']=='PERFIL ARTIFICIAL'
        assert db.execute('SELECT count(*) FROM t09_cenarios_individuais').fetchone()[0]==1


def test_gravacao_versionada_preserva_bytes_anteriores(tmp_path):
    operation=api('operacao')
    fn=getattr(operation,'gravar_versionado',None)
    assert callable(fn),'Preservacao versionada ausente'
    path=tmp_path/'dados.json'
    fn(path,{'valor':1}); original=path.read_bytes()
    fn(path,{'valor':2})
    assert json.loads(path.read_text())=={'valor':2}
    assert any(p.read_bytes()==original for p in (tmp_path/'versoes').rglob('dados.json'))


def test_catalogar_nao_escreve_sobre_fonte_primaria(tmp_path):
    config,original=fixture_config(tmp_path); before=original.read_bytes()
    cfg=json.loads(config.read_text());cfg['catalogo']['saida']='fontes/original.txt'
    config.write_text(json.dumps(cfg))
    assert invoke(config,'catalogar').returncode!=0
    assert original.read_bytes()==before


def test_release_inspecao_pendente_com_exit_zero_bloqueia(tmp_path):
    fixture=release_fixture(tmp_path)
    path=tmp_path/'inspecao.json';path.write_text(json.dumps({'codigo_saida':0,'estado':'PENDING'}))
    fixture['recibos']['inspecao']['sha256']=sha(path)
    assert api('gates').avaliar_gate('release',fixture)['codigo_saida']!=0


@pytest.mark.parametrize('attack',['codigo_posterior','log_adulterado','snapshot_adulterado'])
def test_release_rejeita_testes_obsoletos_ou_sem_recibo_autenticado(tmp_path,attack):
    fixture=release_fixture(tmp_path)
    assert api('gates').avaliar_gate('release',fixture)['codigo_saida']==0
    filename={'codigo_posterior':'produtor.py','log_adulterado':'testes.log','snapshot_adulterado':'testes-antes.json'}[attack]
    (tmp_path/filename).write_text('alterado apos teste')
    assert api('gates').avaliar_gate('release',fixture)['codigo_saida']!=0


def test_persistencia_manifesto_truncado_nao_esconde_saida_adulterada(tmp_path):
    module=api('persistencia');tables={'avaliacoes':[{'aluno_local_id':'artificial','acertos':0}]}
    output=module.persistir(tables,tmp_path/'restrito/banco',tmp_path,{'fonte':'a'*64})
    manifest=Path(output['manifesto']);data=json.loads(manifest.read_text())
    data['hashes']={};manifest.write_text(json.dumps(data))
    Path(output['sqlite']).write_bytes(b'ADULTERADO ARTIFICIAL')
    with pytest.raises(ValueError):module.persistir(tables,tmp_path/'restrito/banco',tmp_path,{'fonte':'a'*64})
