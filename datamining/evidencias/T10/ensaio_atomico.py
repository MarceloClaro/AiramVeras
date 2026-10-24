"""Ensaio isolado em cópia de código e fixture 100% artificial; não altera produto."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[2]
NODE='C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sheets(path):
    with zipfile.ZipFile(path) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(t.text or '' for t in item.iter('{'+NS['m']+'}t')) for item in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        rel={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        result={}
        for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',NS):
            target=rel[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            tree=ET.fromstring(z.read(target.lstrip('/') if target.startswith('/') else 'xl/'+target));cells={}
            for c in tree.findall('.//m:sheetData/m:row/m:c',NS):
                v=c.find('m:v',NS);f=c.find('m:f',NS);value=v.text if v is not None else None
                if c.attrib.get('t')=='s':value=strings[int(value)]
                if c.attrib.get('t')=='inlineStr':value=''.join(t.text or '' for t in c.findall('.//m:t',NS))
                cells[c.attrib['r']]=(value,f.text if f is not None else None)
            result[s.attrib['name']]=(tree,cells)
        assert not any('externalLink' in n for n in z.namelist())
        assert not any('[' in (f or '') for _,cells in result.values() for v,f in cells.values())
        styles=ET.fromstring(z.read('xl/styles.xml'))
        return result,styles
def main():
    scratch=ROOT/'.superpowers/sdd/implementation-plan/t10-atomico01'
    if scratch.exists():raise ValueError('Preservar ensaio anterior')
    (scratch/'reports').mkdir(parents=True)
    original=ROOT/'reports/build_workbook.mjs';before=sha(original)
    source=original.read_text(encoding='utf-8')
    start=source.index('function writeBase(');end=source.index('\nfunction build(',start)
    replacement='''function writeBase(wb,rows,ties) {
  const calc=wb.worksheets.getItem('Cálculos'),last=START+rows.length-1;
  const staged=Workbook.create();const meta=staged.worksheets.add('Metas');
  const source=staged.worksheets.add('Cálculos');
  source.getRange(`A${START}:AK${last}`).copyFrom(calc.getRange(`A${START}:AK${last}`),'all');
  const matrix=baseMatrix(rows,ties).map(r=>r.map(safe));
  source.getRange(`A${START}:K${last}`).values=matrix.map(r=>r.slice(0,11));
  source.getRange(`Q${START}:AE${last}`).values=matrix.map(r=>r.slice(16,31));
  source.getRange(`AG${START}:AG${last}`).values=matrix.map(r=>r.slice(32,33));
  meta.getRange('B5:D8').copyFrom(wb.worksheets.getItem('Metas').getRange('B5:D8'),'all');
  staged.recalculate();
  calc.getRange(`A${START}:AK${last}`).copyFrom(source.getRange(`A${START}:AK${last}`),'all');
}
'''
    variant=scratch/'reports/build_workbook.mjs';variant.write_text(source[:start]+replacement+source[end:],encoding='utf-8')
    fixture=ROOT/'.superpowers/sdd/implementation-plan/t10-desempenho/fixture080.json'
    command=[NODE,str(variant),'--verify-fixture',str(fixture),str(scratch/'out')]
    snapshot=dict(timestamp=datetime.now(timezone.utc).isoformat(),comando=command,
        original_sha256=before,variante_sha256=sha(variant),fixture_sha256=sha(fixture),
        runtime_bundle='26.1020.11127',artifact_tool='2.8.99',somente_artificial=True)
    evidence=ROOT/'evidencias/T10'
    (evidence/'atomico01-antes.json').write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
    with (evidence/'atomico01.log').open('w',encoding='utf-8') as log:
        proc=subprocess.run(command,cwd=scratch,stdout=log,stderr=subprocess.STDOUT,
            env={**os.environ,'AIRAM_ARTIFACT_RUNTIME':str(ROOT/'.superpowers/sdd/implementation-plan/runtime-probe')})
    if proc.returncode:raise AssertionError('Ensaio artificial atomico falhou; preservar log')
    baseline,styles_before=sheets(ROOT/'.superpowers/sdd/implementation-plan/t10-desempenho/out080/fixture.xlsx')
    current,styles_after=sheets(scratch/'out/fixture.xlsx')
    for name in ['Metas','Cálculos','Intervenção nominal']:
        assert baseline[name][1]==current[name][1], 'Valores/formulas divergentes'
        for tag in ['dataValidations','cols','sheetFormatPr']:
            b=baseline[name][0].find('m:'+tag,NS);a=current[name][0].find('m:'+tag,NS)
            assert (ET.tostring(b) if b is not None else None)==(ET.tostring(a) if a is not None else None), 'Validacao/dimensoes alteradas'
    # Tabelas de estilos e seus ids de célula precisam permanecer exatamente iguais.
    assert ET.tostring(styles_before)==ET.tostring(styles_after),'Estilos/formatos alterados'
    for name in ['Metas','Cálculos','Intervenção nominal']:
        before_styles={c.attrib['r']:c.attrib.get('s') for c in baseline[name][0].findall('.//m:sheetData/m:row/m:c',NS)}
        after_styles={c.attrib['r']:c.attrib.get('s') for c in current[name][0].findall('.//m:sheetData/m:row/m:c',NS)}
        assert before_styles==after_styles,'Estilo por celula alterado'
    report=json.loads((scratch/'out/verificacao.json').read_text(encoding='utf-8'))
    assert report['nota_permanece_com_chave'] and report['controles_invalidos_expostos'] and report['roundtrip_sem_erros']
    assert report['ordem_inicial']==report['ordem_reversa']
    assert sha(original)==before,'Produto original alterado'
    result=dict(status='PASS',aplicacoes_artificiais=80,produto_inalterado=True,
        valores_formulas_invariantes=True,notas_validadas=True,validacoes_formatos_preservados=True,
        referencias_absolutas_relativas_preservadas=True,externalLinks_ausentes=True,
        xlsx_sha256=sha(scratch/'out/fixture.xlsx'),variante_sha256=sha(variant),
        log_sha256=sha(evidence/'atomico01.log'),fim=datetime.now(timezone.utc).isoformat())
    (evidence/'atomico01-resultado.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
