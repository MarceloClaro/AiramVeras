"""Compara integralmente OOXML, sem importar autor/produto e sem expor linhas."""
from datetime import datetime, timezone
from decimal import Decimal
import hashlib
import json
import posixpath
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def structure(e):
    return (e.tag,tuple(sorted(e.attrib.items())),(e.text or '').strip(),tuple(structure(c) for c in e))
def load(p):
    result={}
    with zipfile.ZipFile(p) as z:
        assert not any('externalLink' in name for name in z.namelist()),'Referencia externa'
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(t.text or '' for t in item.iter('{'+NS['m']+'}t')) for item in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rels={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for e in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
            target=rels[e.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            target=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            tree=ET.fromstring(z.read(target));cells={}
            for c in tree.findall('.//m:sheetData/m:row/m:c',NS):
                kind=c.attrib.get('t');v=c.find('m:v',NS);f=c.find('m:f',NS)
                value=v.text if v is not None else None
                if kind=='s':value=strings[int(value)]
                elif kind=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//m:t',NS))
                elif value is not None and kind not in ('str','e'):value=Decimal(value)
                if value=='':value=None
                formula=f.text if f is not None else None
                assert kind!='e' and not (formula and '[' in formula),'Erro/referencia externa em celula'
                if value is not None or formula is not None:cells[c.attrib['r']]=(value,formula)
            dv=tree.find('m:dataValidations',NS)
            tables=tree.find('m:tableParts',NS)
            table_targets=[]
            if tables is not None:
                rel_path=posixpath.dirname(target)+'/_rels/'+posixpath.basename(target)+'.rels'
                sheet_rels={r.attrib['Id']:r.attrib['Target'] for r in ET.fromstring(z.read(rel_path))}
                for part in tables:
                    ref=sheet_rels[part.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
                    resolved=ref.lstrip('/') if ref.startswith('/') else posixpath.normpath(posixpath.join(posixpath.dirname(target),ref))
                    table_targets.append((resolved,structure(ET.fromstring(z.read(resolved)))))
            result[e.attrib['name']]=(cells,structure(dv) if dv is not None else None,tuple(table_targets))
        result['_tables']={name:structure(ET.fromstring(z.read(name))) for name in z.namelist() if name.startswith('xl/tables/') and name.endswith('.xml')}
    return result
def main():
    label=sys.argv[1] if len(sys.argv)>1 else '01'
    original=FOLDER/'intervencao-restrita.xlsx';updated=FOLDER/f'refinamento{label}/intervencao-restrita.xlsx'
    report=read(ROOT/'evidencias/T10/layout-resultado.json');old=read(ROOT/'evidencias/T10/workbook-resultado.json')
    assert sha(original)==old['xlsx_sha256']==report['origem_sha256']
    assert sha(updated)==report['xlsx_sha256']
    a,b=load(original),load(updated)
    assert a.keys()==b.keys() and a['_tables']==b['_tables'],'Abas/tabelas alteradas'
    groups=read(ROOT/'relatorios/t10/tabelas.json')['grupos']
    allowed={('Metas','A9'),('Intervenção nominal','Z7')}|{('Grupos',f'G{i}') for i in range(8,8+len(groups))}
    checked=formulas=changed=0
    for name in a.keys()-{'_tables'}:
        ac,ad,at=a[name];bc,bd,bt=b[name]
        assert ad==bd and at==bt,'Validacoes ou tabelas alteradas'
        for addr in ac.keys()|bc.keys():
            av=ac.get(addr,(None,None));bv=bc.get(addr,(None,None))
            assert av[1]==bv[1],'Formula alterada'
            formulas+=av[1] is not None
            if (name,addr) in allowed:
                assert av[1] is None and (isinstance(bv[0],str) or (name,addr)==('Intervenção nominal','Z7') and bv[0] is None),'Excecao deve ser texto'
                changed+=av!=bv
            else:assert av==bv,'Valor alterado fora das excecoes'
            checked+=1
    assert changed==len(allowed),'Resumo/legenda nao atualizado integralmente'
    cells=b['Grupos'][0]
    for i,g in enumerate(groups,8):
        text=cells[f'G{i}'][0]
        assert not text.startswith(('{','[')),'JSON bruto'
        if g.get('status_publicacao')=='suprimido_n_menor_5':assert 'N<5' in text and 'não publicadas' in text
        elif g.get('observado'):assert all(s in text for s in ['ponderado','individuais','itens','Ausências'])
        elif g.get('medidas_proprias'):assert all(s in text for s in ['disponíveis','ausentes','média'])
    result=dict(status='PASS',timestamp=datetime.now(timezone.utc).isoformat(),origem_sha256=sha(original),xlsx_sha256=sha(updated),
        celulas_conferidas=checked,formulas_identicas=formulas,textos_deliberados_alterados=changed,
        excecoes='Somente Grupos!G8:G140, Metas!A9 e rotulo tecnico Intervencao!Z7; estilos deliberadamente modificados',
        demais_valores_iguais=True,validacoes_tabelas_iguais=True,referencias_externas_ausentes=True,
        metodo='OOXML stdlib/Decimal independente, sem importar autor/produto')
    target=ROOT/f'evidencias/T10/refinamento{label}-invariancia-resultado.json'
    if target.exists():raise ValueError('Preservar recibo')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
