"""T24/T25: contas manuais e decisões individuais, sem usar produto como oráculo."""
from copy import deepcopy
import importlib
import importlib.util
import pytest
import json
from pathlib import Path
import subprocess
import zipfile
import xml.etree.ElementTree as ET


def api():
    assert importlib.util.find_spec('airam.relatorio') is not None, 'Funcionalidade T10 ausente'
    return importlib.import_module('airam.relatorio').preparar_intervencao


def app(key='x', acertos=17, component='LEITURA', **changes):
    row = dict(aluno_local_id='artificial-'+key, avaliacao_local_id='app-'+key,
        avaliacao_id='instrumento',ano_avaliacao=2026,ciclo='I',ano_escolar=2,turma='A',
        componente=component,fonte_id='fonte',sha256='a'*64,exportacao='v1',
        participacao=True,categoria='Abaixo',acertos=acertos,oportunidades=22,
        habilidades=[],medidas=[],nome='PESSOA ARTIFICIAL '+key)
    row.update(changes)
    return row


def test_t25_maior_lacuna_recebe_apoio_e_empate_independe_da_ordem():
    rows=[app('c',17),app('b',0),app('a',17)]
    original=deepcopy(rows)
    result=api()(rows,{'A':.8,'B':.8},[],[])
    assert [r['avaliacao_local_id'] for r in result] == ['app-b','app-a','app-c']
    assert [r['meta_B']['lacuna'] for r in result] == [18,1,1]
    assert all(r['apoio_sugerido'] and r['revisao_docente']=='pendente' for r in result)
    assert rows==original
    assert [r['chave'] for r in api()(rows[::-1],{'A':.8,'B':.8},[],[])]==[r['chave'] for r in result]


def test_proximidade_nao_exclui_lacuna_grande_e_controle_muda_fila():
    rows=[app('a',17),app('b',0)]
    result=api()(rows,{'A':.8,'B':.8,'ordenacao':'proximidade'},[],[])
    assert [r['avaliacao_local_id'] for r in result]==['app-a','app-b']
    assert len(result)==2
    result=api()(rows,{'A':.8,'B':.5},[],[])
    assert [r['meta_B']['lacuna'] for r in result]==[11,0]


def test_total80_nao_exige_80_em_cada_h_e_so_usa_evidencia_individual():
    rows=[app('a',18,habilidades=[dict(posicao='H01',acertos=0,oportunidades=2,disponibilidade=True)]),
          app('b',22,habilidades=[dict(posicao='H01',acertos=2,oportunidades=2,disponibilidade=True)])]
    result=api()(rows,{'A':.8,'B':.8},[],[])
    by={r['avaliacao_local_id']:r for r in result}
    assert by['app-a']['meta_B']['lacuna']==0
    assert len(by['app-a']['habilidades_prioritarias'])==1
    assert by['app-b']['habilidades_prioritarias']==[]
    assert by['app-a']['acertos_ate_adequacao'] is None


@pytest.mark.parametrize('component',['ESCRITA','FLUENCIA'])
def test_unidades_proprias_preservam_zero_ausencia_e_categoria(component):
    rows=[app('a',None,component,oportunidades=None,categoria='Categoria original',
            medidas=[dict(campo_original='Tarefa',valor=0,unidade='contagem_original',disponibilidade=True)]),
          app('b',None,component,oportunidades=None,medidas=[dict(campo_original='Tarefa',valor=None,unidade='contagem_original',disponibilidade=False)])]
    result=api()(rows,{'A':.8,'B':.8},[],[])
    by={r['avaliacao_local_id']:r for r in result}
    assert by['app-a']['meta_B']['status']=='unidade_nao_aplicavel'
    assert by['app-a']['medidas'][0]['valor']==0
    assert by['app-a']['categoria']=='Categoria original'
    assert by['app-a']['disponivel'] is True
    assert by['app-b']['disponivel'] is False
    assert by['app-b']['meta_B']['lacuna'] is None


def test_ausencia_nao_vira_zero_e_pede_sondagem():
    r=api()([app('a',None,oportunidades=None,participacao=False)],{'A':.8,'B':.8},[],[])[0]
    assert r['acertos'] is None and r['meta_B']['lacuna'] is None
    assert r['classe_prioridade']==0 and r['disponivel'] is False


def test_vinculo_contextual_nao_confunde_ano_nem_multiplica_h():
    row=app('a',1,habilidades=[dict(posicao='H01',acertos=0,oportunidades=2,disponibilidade=True)])
    edges=[dict(ano_avaliado=year,ano_avaliacao=2026,ciclo_avaliado='I',avaliacao_id='instrumento',
        componente='LEITURA',fonte_posicao='mapa',versao_posicao='v1',posicao='H01',
        codigo_caed='codigo',codigo_bncc=bncc,texto_caed='Descritor',texto_bncc='Texto',
        pagina_matriz=7,sha256_pdf='b'*64,ocorrencia_id='ocorrencia-'+bncc,
        status_contextual='proprio_ano_ciclo_confirmado',status_semantico='ressalva',
        ressalva='associacao documental',peso_analitico=.5) for year,bncc in [(2,'EF02LP01'),(2,'EF02LP02'),(3,'EF03LP01')]]
    r=api()([row],{'A':.8,'B':.8},edges,[])[0]
    h=r['habilidades_prioritarias']
    assert len(h)==1 and h[0]['acertos']==0 and h[0]['oportunidades']==2
    assert [v['codigo_bncc'] for v in h[0]['vinculos']]==['EF02LP01','EF02LP02']
    assert r['meta_B']['lacuna']==17


def test_nao_mescla_versoes_de_mapa_na_mesma_posicao():
    row=app('a',1,habilidades=[dict(posicao='H01',acertos=0,oportunidades=2,disponibilidade=True)])
    base=dict(ano_avaliado=2,ano_avaliacao=2026,ciclo_avaliado='I',avaliacao_id='instrumento',
        componente='LEITURA',fonte_posicao='mapa',versao_posicao='v1',posicao='H01',
        codigo_bncc='EF02LP01',ocorrencia_id='oc1')
    with pytest.raises(ValueError,match='curricular'):
        api()([row],{'A':.8,'B':.8},[base,dict(base,versao_posicao='v2')],[])


@pytest.mark.parametrize('change',[{'acertos':23},{'oportunidades':0},{'participacao':False}, {'acertos':None}])
def test_recusa_contagens_ou_mascara_incoerentes(change):
    with pytest.raises(ValueError):
        api()([app(**change)],{'A':.8,'B':.8},[],[])


def test_chave_contextual_recusa_duplicata_e_distingue_versao():
    r=app()
    with pytest.raises(ValueError):
        api()([r,deepcopy(r)],{'A':.8,'B':.8},[],[])
    second=app(exportacao='v2',avaliacao_local_id='app-v2')
    result=api()([r,second],{'A':.8,'B':.8},[],[])
    assert result[0]['chave']!=result[1]['chave']


def test_t24_excel_recalcula_metas_fila_e_notas_com_reordenacao(tmp_path):
    root=Path(__file__).resolve().parents[1]
    builder=root/'reports/build_workbook.mjs'
    assert builder.is_file(), 'Builder funcional T24 ausente'
    inp=root/'tests/fixtures/t10_workbook.json'
    node='C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    run=subprocess.run([node,str(builder),'--verify-fixture',str(inp),str(tmp_path)],cwd=root,
        capture_output=True,text=True,encoding='utf-8')
    assert run.returncode==0, 'Verificacao funcional do workbook falhou; consultar recibo sintetico'
    report=json.loads((tmp_path/'verificacao.json').read_text(encoding='utf-8'))
    assert report['ordem_inicial']==['k-d','k-f','k-b','k-a','k-c','k-e']
    assert report['lacunas_iniciais']=={'k-c':1,'k-b':18,'k-a':1,'k-d':None,'k-e':None,'k-f':None}
    assert report['ordem_meta50']==['k-d','k-f','k-b','k-e','k-a','k-c']
    assert report['ordem_proximidade']==['k-d','k-f','k-a','k-c','k-b','k-e']
    assert report['ordem_reversa']==report['ordem_inicial']
    assert report['nota_permanece_com_chave'] is True
    assert report['notas_fila_inicial']=={'k-d':'','k-f':'','k-b':'NOTA ARTIFICIAL B','k-a':'','k-c':'','k-e':''}
    assert report['notas_fila_reversa']==report['notas_fila_inicial']
    assert report['controles_invalidos_expostos'] is True
    assert report['fontes_curriculares_conferidas']==1
    assert report['fluxo_pre_requisitos_verificado'] is True
    assert report['detector_erros_comprovado'] is True
    assert report['roundtrip_sem_erros'] is True


def test_previa_substitui_toda_observacao_individual_por_regra_artificial(tmp_path):
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'tests/fixtures/t10_workbook.json').read_text(encoding='utf-8'))
    data['intervencao'][0]['habilidades_prioritarias']=[dict(posicao='H19',acertos=17,oportunidades=19,vinculos=[])]
    data['intervencao'][0]['grupos']=[dict(grupo_id='GRUPO INDIVIDUAL ORIGINAL',versao='v1')]
    data['habilidades']=[dict(chave='k-c',ano_escolar=2,turma='A',componente='LEITURA',posicao='H19',
        valor=17,denominador=19,unidade='itens',disponibilidade=True,fonte='FONTE INDIVIDUAL',linha_fonte=29)]
    inp=tmp_path/'entrada.json';inp.write_text(json.dumps(data),encoding='utf-8')
    node='C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    run=subprocess.run([node,str(root/'reports/build_workbook.mjs'),'--verify-fixture',str(inp),str(tmp_path/'out')],
        cwd=root,capture_output=True,text=True,encoding='utf-8')
    assert run.returncode==0
    report=json.loads((tmp_path/'out/verificacao.json').read_text(encoding='utf-8'))
    assert 'amostra_previa_artificial' in report, 'Transformacao integral da previa ausente'
    sample=report['amostra_previa_artificial']
    assert len(sample['intervencao'])==8
    assert [r['acertos'] for r in sample['intervencao']]==[0,3,6,9,None,None,None,None]
    assert all(r['grupos']==[] and r['notas_docentes'].startswith('ARTIFICIAL') for r in sample['intervencao'])
    assert all(r['fonte']=='ARTIFICIAL' and r['linha_fonte']==1 for r in sample['intervencao'])
    assert all(h['posicao']=='H01' and h['acertos']==0 and h['oportunidades']==2
        for r in sample['intervencao'] for h in r['habilidades_prioritarias'])
    assert len(sample['habilidades'])==16
    assert all(r['fonte']=='ARTIFICIAL' and r['linha_fonte']==1 and r['posicao']=='H01'
        for r in sample['habilidades'])
    assert 'k-c' not in json.dumps(sample) and 'GRUPO INDIVIDUAL ORIGINAL' not in json.dumps(sample)
    assert sample['maior_nome']==len('PESSOA ARTIFICIAL c')


def test_workbook_recusa_hipotese_comum_em_denominadores_heterogeneos(tmp_path):
    root=Path(__file__).resolve().parents[1]
    node='C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    run=subprocess.run([node,str(root/'reports/build_workbook.mjs'),'--verify-fixture',
        str(root/'tests/fixtures/t10_workbook_heterogeneo.json'),str(tmp_path)],cwd=root,capture_output=True,text=True,encoding='utf-8')
    assert run.returncode!=0
    status=json.loads(run.stderr.strip().splitlines()[-1])
    assert status['etapa']=='validar', 'Hipotese de D comum precisa ser recusada antes da autoria'
    assert not list(tmp_path.iterdir())


def test_exportacao_reaberta_preservada_se_renderer_nativo_falhar(tmp_path):
    root=Path(__file__).resolve().parents[1]
    node='C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    run=subprocess.run([node,str(root/'reports/build_workbook.mjs'),'--build',
        str(root/'tests/fixtures/t10_workbook.json'),str(tmp_path)],cwd=root,capture_output=True,text=True,encoding='utf-8')
    assert (tmp_path/'intervencao-restrita.xlsx').is_file(), 'Crash de imagem descartou exportacao calculada'
    report=json.loads((tmp_path/'verificacao.json').read_text(encoding='utf-8'))
    assert report['roundtrip_sem_erros'] is True
    assert report['renderizacao']['isolada_sem_dados_individuais_reais'] is True
    assert run.returncode==0
    assert report['renderizacao']['status']=='preparada_sem_render_local'
    assert report['renderizacao']['tentativa_automatica'] is False
    assert report['renderizacao']['imagens']==0
    assert (tmp_path/'previas-sinteticas/inspecao-artificial.xlsx').is_file()


def _ooxml(path):
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(t.text or '' for t in item.iter('{'+ns['m']+'}t')) for item in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rel={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheets={}
        for item in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',ns):
            target=rel[item.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            tree=ET.fromstring(z.read(target.lstrip('/') if target.startswith('/') else 'xl/'+target))
            values={}
            for c in tree.findall('.//m:sheetData/m:row/m:c',ns):
                v=c.find('m:v',ns);f=c.find('m:f',ns);value=v.text if v is not None else None
                if c.attrib.get('t')=='s':value=strings[int(value)]
                if c.attrib.get('t')=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//m:t',ns))
                values[c.attrib['r']]=(value,f.text if f is not None else None)
            sheets[item.attrib['name']]=(tree,values)
    return sheets,ns


def test_layout_legivel_e_refinamento_preserva_valores_formulas(tmp_path):
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'tests/fixtures/t10_workbook.json').read_text(encoding='utf-8'))
    data['grupos']=[dict(contexto={'ano_escolar':2,'componente':'LEITURA'},grupo_id='ARTIFICIAL',n=5,
        observado={'acertos':22,'oportunidades':33,'taxa':2/3,
            'distribuicao_acertos':{'n':5,'media':4.123456789,'mediana':4,'minimo':1,'maximo':7,'p10':1.5}},
        habilidades=[],medidas_proprias=[],fontes_sha256=['a'*64]),
        dict(contexto={'ano_escolar':2,'componente':'ESCRITA'},grupo_id='ARTIFICIAL-E',n=5,
            habilidades=[],medidas_proprias=[dict(campo_original='Nota',unidade='nota_escrita',disponiveis=3,
                ausentes=2,distribuicao={'n':3,'media':0,'mediana':0,'minimo':0,'maximo':0,'p10':0})],fontes_sha256=['a'*64]),
        dict(contexto={'ano_escolar':2,'componente':'LEITURA'},grupo_id='ARTIFICIAL-S',n_intervalo='1-4',
            status_publicacao='suprimido_n_menor_5')]
    inp=tmp_path/'dados.json';inp.write_text(json.dumps(data),encoding='utf-8')
    node='C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
    run=subprocess.run([node,str(root/'reports/build_workbook.mjs'),'--verify-fixture',str(inp),str(tmp_path/'base')],
        cwd=root,capture_output=True,text=True,encoding='utf-8')
    assert run.returncode==0
    source=tmp_path/'base/fixture.xlsx';sheets,ns=_ooxml(source)
    def width(name,column):
        return next(float(c.attrib.get('width',0)) for c in sheets[name][0].findall('m:cols/m:col',ns)
            if int(c.attrib['min'])<=column<=int(c.attrib['max']))
    assert width('Metas',3)>=26, 'Rotulo de oportunidades ainda truncavel'
    assert width('Intervenção nominal',9)>=30, 'Unidade/nao aplicacao precisa caber'
    assert width('Intervenção nominal',26)==0, 'Coluna tecnica precisa de largura minima'
    assert sheets['Intervenção nominal'][1]['Z7'][0] in (None,''), 'Rotulo tecnico ainda visivel'
    with zipfile.ZipFile(source) as package:
        styles=ET.fromstring(package.read('xl/styles.xml'))
        custom={x.attrib['numFmtId']:x.attrib['formatCode'] for x in styles.findall('m:numFmts/m:numFmt',ns)}
        cell=next(c for c in sheets['Intervenção nominal'][0].findall('.//m:row/m:c',ns) if c.attrib['r']=='Z8')
        style=styles.find('m:cellXfs',ns)[int(cell.attrib['s'])]
        assert custom[style.attrib['numFmtId']]==';;;', 'Indice tecnico ainda exibido'
    summary=sheets['Grupos'][1]['G8'][0]
    group_row=next(row for row in sheets['Grupos'][0].findall('m:sheetData/m:row',ns) if row.attrib['r']=='8')
    # Each explicit newline consumes a new line in the saved display, even when
    # every individual segment is short. Count all wrapped segments, not only max.
    minimum_lines=sum(max(1,(len(line)+59)//60) for line in summary.split('\n'))
    assert float(group_row.attrib['ht'])>=minimum_lines*13+20, 'Resumo multilinha nao cabe na altura salva'
    assert 'C/D ponderado' in summary and '66,67%' in summary and 'itens' in summary
    assert '4,123' in summary and '4.123456789' not in summary and '{' not in summary
    own=sheets['Grupos'][1]['G9'][0]
    assert 'nota escrita' in own and 'ausentes 2' in own and 'média 0' in own
    assert 'Suprimido' in sheets['Grupos'][1]['G10'][0]
    run=subprocess.run([node,str(root/'reports/build_workbook.mjs'),'--refine-layout',str(inp),str(source),str(tmp_path/'final')],
        cwd=root,capture_output=True,text=True,encoding='utf-8')
    assert run.returncode==0, 'Ajuste restrito de apresentacao ainda ausente'
    after,_=_ooxml(tmp_path/'final/intervencao-restrita.xlsx')
    for name,(_,before) in sheets.items():
        assert before==after[name][1], 'Ajuste de layout alterou valores/formulas'
