"""Conferência independente dos bytes/valores SQL/CSV; imprime só contagens/hashes."""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
from contextlib import closing

ROOT=Path(__file__).resolve().parents[2]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def need(condition):
    if not condition:raise ValueError('Contraprova local de persistencia falhou; nenhum registro exposto')


def main():
    csv.field_size_limit(128*1024*1024)
    cfg=read(ROOT/'config/analise.json')
    cache=read(ROOT/cfg['cache_analise']['caminho'])
    need(all(sha(ROOT/p)==h for p,h in cache['saidas'].items()))
    original=read(ROOT/'restrito/t03/tabelas.json')
    for task,fields in {'t05':['metricas_alunos','metas_individuais'],'t07':['blocos','visoes_aluno'],
        't08':['instrumentos','unidades_proprias'],'t09':['cenarios_individuais','outros_instrumentos']}.items():
        data=read(ROOT/f'restrito/{task}/checkpoint.json')
        if task=='t08':
            # Todos os nomes nesta saída autenticada são títulos pedagógicos nos perfis;
            # substituição textual independente da navegação de caminhos do produto.
            data=json.loads(json.dumps(data,ensure_ascii=False).replace('"nome":','"titulo_perfil":'))
        for field in fields:original[task+'_'+field]=data[field]
    for relative,fields in {'curriculo/t04/checkpoint.json':['posicoes','vinculos_posicoes'],
        'estatistica/t05/checkpoint.json':['agregados','metas_A'],
        'estatistica/t06/entrega/checkpoint.json':['associacoes']}.items():
        data=read(ROOT/relative);task=relative.split('/')[1]
        for field in fields:original[task+'_'+field.lower()]=data[field]
    operations=[read(p) for p in (ROOT/'evidencias/operacionais').rglob('recibo.json')]
    operations=[r for r in operations if r['comando']=='analisar' and r['codigo_saida']==0]
    latest=max(operations,key=lambda r:r['fim'])
    dbpath=ROOT/latest['resultado']['sqlite']; directory=dbpath.parent
    counts={}
    with closing(sqlite3.connect(dbpath)) as db:
        need(db.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
        need(db.execute('PRAGMA user_version').fetchone()[0]==1)
        actual_tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        need(actual_tables==set(original)|{'proveniencia'})
        for table,expected in original.items():
            actual=[json.loads(r[0]) for r in db.execute(f'SELECT registro_json FROM "{table}" ORDER BY ordem')]
            need(actual==expected)
            with (directory/(table+'.csv')).open(encoding='utf-8-sig',newline='') as stream:
                csv_rows=list(csv.DictReader(stream))
            need(len(csv_rows)==len(expected))
            for saved,row in zip(csv_rows,expected):
                for key in saved:
                    value=row.get(key)
                    want=json.dumps(value,ensure_ascii=False,sort_keys=True) if isinstance(value,(dict,list)) else '' if value is None else str(value)
                    need(saved[key]==want)
            counts[table]=len(expected)
    mapping=read(ROOT/'restrito/t03/mapa-nominal.json')
    names={row[key] for row in mapping for key in ('nome_bruto','nome_normalizado') if row.get(key)}
    ids={row[key] for row in mapping for key in ('aluno_local_id','matricula_local_id') if row.get(key)}
    for table in original.values():
        text=json.dumps(table,ensure_ascii=False)
        need(not any(name in text for name in names))
    public=ROOT/'relatorios/agregados'
    checked=0
    for path in public.rglob('*'):
        if path.is_file():
            text=path.read_text(encoding='utf-8-sig')
            need(not any(term in text for term in names|ids));checked+=1
    baseline=read(ROOT/cfg['baseline']['caminho'])
    need(all(sha(ROOT.parent/p)==h for p,h in baseline['fontes'].items()))
    report={'estado':'PASS','codigo_saida':0,'tipo':'contraprova_independente_sqlite_csv',
        'contagens':counts,'tabelas':len(counts),'arquivos_publicos_verificados':checked,
        'sqlite_sha256':sha(dbpath),'manifesto_sha256':sha(directory/'manifesto.json'),
        'fontes_primarias_inalteradas':len(baseline['fontes']),
        'comparacao':'todos os valores, zero, ausencias, mascaras, contextos e proveniencia',
        'limites':['Armazenamento ignorado nao certifica ACL por papel nem criptografia.',
            'Sem inferencia Core nova; sem validacao pedagogica externa.']}
    path=ROOT/'evidencias/T11/contraprova-persistencia.json'
    path.write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))


if __name__=='__main__': main()
