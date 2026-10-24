"""Importação única de contratos históricos; não é coletor nem inferência nova.

Os hashes esperados provêm do Git aprovado, de snapshots anteriores e do recibo
de handoff do controlador. Nunca se aprende baseline a partir de catálogo novo.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess

ROOT=Path(__file__).resolve().parents[2]
BASE='28d88e356f3ce744f250331aa2f90a8de5bdc6be'
CENTRAL=ROOT.parent/'datamining/.superpowers/sdd/implementation-plan'


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')


def committed(relative):
    raw=subprocess.check_output(['git','show',BASE+':'+relative],cwd=ROOT)
    local=(ROOT/relative).read_bytes()
    if raw.replace(b'\r\n',b'\n') != local.replace(b'\r\n',b'\n'):
        raise ValueError('Referencia historica difere do Git aprovado')
    return json.loads(raw) if relative.endswith('.json') else raw


def main():
    historical=committed('evidencias/T01/fontes-hashes.json')
    selected={p:h for p,h in historical.items() if p.startswith((
        'resultados-caed-ciclo-i-2026/csv_originais/', 'resultados-caed-ciclo-i-2026/originais/'))}
    for p in ['resultados-caed-ciclo-i-2026/manifesto_coleta.json',
        'resultados-caed-ciclo-i-2026/conferencia/mapa_posicao_codigo_caed.csv',
        'MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf',
        'bncc-dados/dados/bncc-2018/ensino-fundamental.json']:
        selected[p]=historical[p]
    if len(selected)!=76: raise ValueError('Baseline historica incompleta')
    if any(sha(ROOT.parent/p)!=h for p,h in selected.items()):
        raise ValueError('Fonte fisica difere da baseline historica')
    baseline={'versao':1,'origem':{'commit':BASE,'arquivo':'evidencias/T01/fontes-hashes.json',
        'sha256':sha(ROOT/'evidencias/T01/fontes-hashes.json')},'fontes':selected}
    write(ROOT/'config/fontes-baseline.json',baseline)
    handoff=read(CENTRAL/'handoff-local-t11-resultado.json')
    outputs={r['relative_path']:r['sha_target'] for r in handoff['files']
        if r['relative_path'].startswith('restrito/')}
    public=['curriculo/t04/checkpoint.json','estatistica/t05/checkpoint.json',
        'estatistica/t06/entrega/checkpoint.json','estatistica/t06/entrega/associacoes.csv',
        'estatistica/t07/checkpoint.json','estatistica/t08/checkpoint.json','estatistica/t09/checkpoint.json']
    for p in public:
        committed(p); outputs[p]=sha(ROOT/p)
    if any(sha(ROOT/p)!=h for p,h in outputs.items()):
        raise ValueError('Checkpoint diverge do handoff')
    # Snapshot anterior a qualquer alteração T11; arquivos analíticos continuam no BASE.
    before=read(ROOT/'evidencias/T11/baseline-antes.json')
    modules={p:h for p,h in before['hashes_codigo'].items()
        if p.startswith('airam/') and p not in ('airam/catalogo.py','airam/recibos.py','airam/__init__.py')}
    for p,h in modules.items():
        committed(p)
        if sha(ROOT/p)!=h: raise ValueError('Produtor analitico divergente')
    params=['config/agrupamentos.json','config/correlacoes.json','config/cenarios.json','config/ressalvas_curriculares.json']
    for p in params: committed(p)
    # Verificar as versões herdadas contra snapshots realmente prévios de inferência.
    snapshots=['evidencias/T06/15-fix1-compatibilidade-antes.json',
        'evidencias/T08/fix1-atualizacao01-antes.json','evidencias/T09/analise02-antes.json']
    libs=('numpy','scipy','scikit-learn','threadpoolctl','pandas','pdfplumber','pypdf')
    versions={name:importlib.metadata.version(name) for name in libs}
    for p in snapshots:
        old=committed(p)
        if old['python']!=platform.python_version() or any(old['versoes'][n]!=v for n,v in versions.items()):
            raise ValueError('Runtime diverge dos snapshots historicos')
    from airam.cache import runtime
    old_config=json.loads(subprocess.check_output(['git','show',BASE+':config/analise.json'],cwd=ROOT))
    manifest={'versao_schema':'airam-cache-v1',
        'origem':{'tipo':'importacao_de_entregas_revisadas','commit':BASE,
            'handoff_sha256':sha(CENTRAL/'handoff-local-t11-resultado.json'),
            'snapshots_runtime':{p:sha(ROOT/p) for p in snapshots},
            'fronteira':'Compatibilidade autenticada agora; nenhum novo ajuste de modelo.',
            'codigo':'Produtores analiticos do BASE; catalogo/metadados CLI excluidos pois reingestao e comparada com T02.'},
        'entradas':{'config/fontes-baseline.json':sha(ROOT/'config/fontes-baseline.json')},
        'codigo':modules,'config':{p:sha(ROOT/p) for p in params},'saidas':outputs,'runtime':runtime(),
        'parametros':{k:old_config[k] for k in ('meta_a','meta_b','ausencia','identidade')}}
    write(ROOT/'config/cache-analise-aprovada.json',manifest)
    cfg=read(ROOT/'config/analise.json')
    cfg['baseline']={'caminho':'config/fontes-baseline.json','sha256':sha(ROOT/'config/fontes-baseline.json')}
    cfg['cache_analise']={'caminho':'config/cache-analise-aprovada.json','sha256':sha(ROOT/'config/cache-analise-aprovada.json')}
    cfg['checkpoint_ingestao']={'caminho':'restrito/t02/tabelas.json','sha256':outputs['restrito/t02/tabelas.json']}
    cfg['catalogo']['excluir_diretorios']+=['00_ORGANIZACAO','.airam-cenarios-t09','.airam-cli-t11']
    cfg['catalogo']['excluir_diretorios']=sorted(set(cfg['catalogo']['excluir_diretorios']))
    cfg['catalogo']['excluir_arquivos']=['COMECE_AQUI.lnk']
    write(ROOT/'config/analise.json',cfg)
    write(ROOT/'evidencias/T11/contratos-importados.json',{'tipo':'importacao_documental_operacional',
        'base':BASE,'fontes':len(selected),'checkpoints':len(outputs),'nova_inferencia':False,
        'baseline_sha256':sha(ROOT/'config/fontes-baseline.json'),'cache_sha256':sha(ROOT/'config/cache-analise-aprovada.json')})
    print(json.dumps({'fontes':len(selected),'checkpoints':len(outputs),'nova_inferencia':False}))


if __name__=='__main__':
    import sys
    sys.path.insert(0,str(ROOT))
    main()
