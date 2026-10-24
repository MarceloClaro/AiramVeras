"""Auditoria independente: stdlib/Fraction/XML, sem importar airam ou o builder."""
from collections import defaultdict
from fractions import Fraction
import hashlib
import html
import json
from pathlib import Path
import re
import sqlite3
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[2]
XLSX=ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53/intervencao-restrita.xlsx'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
CHECKS=0


def check(condition,label):
    global CHECKS
    CHECKS+=1
    if not condition:raise AssertionError('Contraprova divergente: '+label)


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))


def xlsx_tables():
    with zipfile.ZipFile(XLSX) as z:
        shared=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            for item in ET.fromstring(z.read('xl/sharedStrings.xml')):shared.append(''.join(t.text or '' for t in item.iter('{'+NS['m']+'}t')))
        relationships={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        worksheets={}
        for e in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
            target=relationships[e.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            cells={}
            tree=ET.fromstring(z.read(target))
            for c in tree.findall('.//m:sheetData/m:row/m:c',NS):
                value=c.find('m:v',NS);f=c.find('m:f',NS);kind=c.attrib.get('t')
                v=value.text if value is not None else None
                if kind=='s':v=shared[int(v)]
                elif kind=='inlineStr':v=''.join(t.text or '' for t in c.findall('.//m:t',NS))
                elif kind not in ('str','e') and v is not None:
                    try:v=float(v);v=int(v) if v.is_integer() else v
                    except ValueError:pass
                cells[c.attrib['r']]=(v,f.text if f is not None else None,kind)
            worksheets[e.attrib['name']]=cells
        return worksheets


def val(sheet,address):return sheet.get(address,(None,None,None))[0]


def main():
    expected={
        'restrito/t05/checkpoint.json':'6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b',
        'restrito/t03/mapa-nominal.json':'5a4b62dab471de27b7a9b2fc510806f66fd205a65f28e5ab30c60e463d7ff3be',
        'curriculo/t04/checkpoint.json':'a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796'}
    for p,h in expected.items():check(sha(ROOT/p)==h,'fonte autenticada')
    raw=read('restrito/t05/checkpoint.json')['observado'];nominal=read('restrito/t03/mapa-nominal.json');catalog=read('curriculo/t04/checkpoint.json')
    prepared=read('restrito/t10/checkpoint.json');public=read('relatorios/t10/tabelas.json')
    sheets=xlsx_tables()
    check(list(sheets)==['Metas','Intervenção nominal','Habilidades','Grupos','Cálculos','Fontes e Auditoria'],'seis abas')
    base=sheets['Cálculos'];queue=sheets['Intervenção nominal'];hs=sheets['Habilidades'];metas=sheets['Metas'];sources=sheets['Fontes e Auditoria']
    errors=[1 for sheet in sheets.values() for v,f,t in sheet.values() if t=='e' or f and isinstance(v,str) and re.match(r'^#(?:REF!|DIV/0!|VALUE!|NAME\?|N/A|NUM!|NULL!|SPILL!|CALC!)',v)]
    check(not errors,'valores de erro no XLSX')
    names={r['aluno_local_id']:r['nome_bruto'] for r in nominal}
    source_measures=defaultdict(list)
    for table in ['habilidades','escrita','fluencia']:
        for m in raw[table]:source_measures[m['avaliacao_local_id']].append(m)
    context=['avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente','fonte_id','sha256','exportacao']
    keys={}
    for r in raw['avaliacoes']:
        k=hashlib.sha256(json.dumps([r[c] for c in context]+[r['aluno_local_id'],r['avaliacao_local_id']],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        keys[k]=r
    positions={val(base,f'A{n}'):n for n in range(8,648)}
    check(len(positions)==640 and set(positions)==set(keys),'bijeção de aplicações')
    priority=[]
    db=sqlite3.connect(':memory:')
    db.execute('CREATE TABLE obs (instrumento TEXT, turma TEXT, componente TEXT, participante INT, disponivel INT, adequado INT, lacuna INT)')
    for k,r in keys.items():
        n=positions[k];ms=source_measures[r['avaliacao_local_id']];lm=r['componente'] in ['LEITURA','MATEMATICA']
        available=bool(r['participacao'] and (r['acertos'] is not None if lm else any(m['disponibilidade'] for m in ms)))
        target= -(-(r['oportunidades']*4)//5) if lm and available else None
        gap=max(0,target-r['acertos']) if target is not None else None
        cls=0 if not available else 1 if lm and gap>0 else 2 if not lm else 3
        check(val(base,f'B{n}')==names[r['aluno_local_id']],'nome local por chave')
        for c,expected_v in [('C',r['ano_escolar']),('D',r['turma']),('E',r['componente']),('F',int(r['participacao'])),('G',r['categoria']),
                ('H',r['acertos']),('I',r['oportunidades']),('J',int(available)),('L',target if target is not None else 'n.a.'),
                ('M',gap if gap is not None else 'n.a.'),('N',cls),('AD',int(lm))]:
            actual=val(base,f'{c}{n}')
            check(actual==expected_v or actual in ('',None) and expected_v in ('',None),'medida/cálculo individual')
        check(val(base,f'Q{n}') in ('',None),'notas originais vazias restauradas')
        check(val(base,f'R{n}')=='pendente','revisão original restaurada')
        check(val(base,f'AH{n}')=='Revisão docente pendente','próxima ação pendente')
        priority.append((cls,-gap if cls==1 else 0,k))
        inst=hashlib.sha256(json.dumps([r[c] for c in context],sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()).hexdigest()
        db.execute('INSERT INTO obs VALUES (?,?,?,?,?,?,?)',(inst,r['turma'],r['componente'],int(r['participacao']),int(available),int(r['categoria']=='Adequado'),gap))
        valid=[m for m in ms if lm and m['disponibilidade'] and m['numerador']<m['denominador']]
        valid.sort(key=lambda m:(Fraction(m['numerador'],m['denominador']),m['posicao']))
        wanted='; '.join(f"{m['posicao']}: {m['numerador']}/{m['denominador']}" for m in valid[:3])
        check((val(base,f'U{n}') or '')==wanted,'prioridade usa H individual sem teto 80 por H')
    wanted_order=[t[2] for t in sorted(priority)]
    check([val(queue,f'B{n}') for n in range(8,648)]==wanted_order,'fila independente ordenada por necessidade')
    for n in [8,327,647]:
        k=val(queue,f'B{n}')
        check(val(queue,f'C{n}')==names[keys[k]['aluno_local_id']],'nome recuperado na fila')
        check('INDEX' in queue[f'B{n}'][1] and 'MATCH' in queue[f'Z{n}'][1],'fila contém consulta compartilhada executada')
    for i,scope in enumerate(prepared['componentes'],13):
        query='SELECT COUNT(*),SUM(participante),SUM(disponivel),SUM(CASE WHEN participante=1 THEN adequado ELSE 0 END),SUM(CASE WHEN lacuna=0 THEN 1 ELSE 0 END),SUM(lacuna) FROM obs WHERE instrumento=?'
        params=[scope['instrumento']]
        if scope['nivel']=='turma':query+=' AND turma=?';params.append(scope['turma'])
        cad,part,avail,adequate,reached,gaps=db.execute(query,params).fetchone()
        check(val(metas,f'F{i}')==cad and val(metas,f'G{i}')==part and val(metas,f'H{i}')==avail,'universos SQL')
        if scope['componente'] in ('LEITURA','MATEMATICA'):
            target=-(-(part*4)//5)
            for col,x in [('I',adequate),('J',target),('K',max(0,target-adequate)),('N',reached),('O',gaps or 0)]:check(val(metas,f'{col}{i}')==x,'Meta A/B SQL')
        else:
            check(all(val(metas,f'{c}{i}')=='n.a.' for c in ['I','J','K','L','M','N','O']),'E/F sem meta artificial')
    expected_measures=[]
    key_by_app={r['avaliacao_local_id']:k for k,r in keys.items()}
    for r in raw['avaliacoes']:
        for m in source_measures[r['avaliacao_local_id']]:
            expected_measures.append((key_by_app[r['avaliacao_local_id']],r['ano_escolar'],r['turma'],r['componente'],m['posicao'] or m['campo_original'],
                m['valor'] if m['valor'] is not None else m['numerador'],m['denominador'],m['unidade'],int(m['disponibilidade'])))
    for n,wanted in enumerate(expected_measures,8):
        actual=tuple(val(hs,f'{c}{n}') for c in 'ABCDEFGHI')
        check(all(a==e or a in ('',None) and e in ('',None) for a,e in zip(actual,wanted)),'medida original no XLSX sem fanout')
    check(len(expected_measures)==6074,'quantidade de medidas')
    # Todas as relações documentais estão no input curricular com seus textos/localizadores.
    source_rows={v:addr for addr,(v,f,t) in sources.items() if isinstance(v,str) and v.startswith('FONTES CURRICULARES')}
    check(len(source_rows)==1,'região de fontes curriculares')
    header=int(re.search(r'\d+',next(iter(source_rows.values()))).group())+1
    for i,v in enumerate(catalog['vinculos_posicoes'],header+1):
        for c,expected_v in [('A',v['ano_avaliado']),('B',v['componente']),('C',v['posicao']),('D',v['codigo_caed']),('E',v['texto_caed']),
                ('F',v['codigo_bncc']),('G',v['texto_bncc']),('H',v['pagina_matriz']),('J',v['status_contextual']),('K',v['status_semantico']),('M',v['sha256_pdf']),('N',v['ocorrencia_id']),('P',v['versao_posicao'])]:
            check(val(sources,f'{c}{i}')==expected_v,'fonte curricular preservada')
    restricted_terms={str(r[k]) for r in nominal for k in ['nome_bruto','nome_normalizado','aluno_local_id','matricula_local_id']}
    restricted_terms.update(r['avaliacao_local_id'] for r in raw['avaliacoes']);restricted_terms.update(keys)
    public_files=[p for p in (ROOT/'relatorios/t10').rglob('*') if p.is_file() and 'versoes' not in p.parts and p.suffix in {'.html','.json','.svg'}]
    public_files += [p for p in (ROOT/'evidencias/T10').rglob('*') if p.is_file() and p.suffix in {'.py','.mjs','.md','.json','.log'} and 'versoes' not in p.parts]
    for p in public_files:
        text=p.read_text(encoding='utf-8').casefold()
        check(not any(s.casefold() in text or html.escape(s).casefold() in text for s in restricted_terms if s),'termos individuais fora do restrito')
    check(len(public['associacoes'])==428,'universo completo de associações')
    check(len(public['grupos'])==133,'perfis públicos preservados')
    check(all('ressalvas' in p and any('L1' in s and 'L2' in s for s in p['ressalvas']) for p in public['grupos']),'M1 em todos os perfis')
    result=dict(status='PASS',verificacoes=CHECKS,aplicacoes_conferidas=640,medidas_conferidas=len(expected_measures),
        relacoes_curriculares_conferidas=len(catalog['vinculos_posicoes']),arquivos_publicos_sem_identificadores=len(public_files),
        metodo='stdlib + Fraction + SQL + leitura OOXML independente; sem importar airam/builder',
        xlsx_sha256=sha(XLSX),checkpoint_restrito_sha256=sha(ROOT/'restrito/t10/checkpoint.json'),
        limites='Caches e estruturas do XLSX conferidos; execução Excel nativo, eficácia e revisão docente não demonstradas.')
    label=sys.argv[1] if len(sys.argv)>1 else ''
    target=ROOT/f'evidencias/T10/contraprova{label}-resultado.json'
    if target.exists():raise ValueError('Preservar auditoria anterior')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
