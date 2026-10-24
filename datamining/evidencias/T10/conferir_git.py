"""Confere escopo, bytes e privacidade do staging sem mostrar termos reais."""
import hashlib
import html
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
SINGLE={'.gitattributes','airam/relatorio.py','reports/build_workbook.mjs','reports/templates/relatorio.html',
    'tests/test_relatorio.py','tests/test_intervencao.py','tests/fixtures/t10_workbook.json',
    'tests/fixtures/t10_workbook_heterogeneo.json','docs/dicionario-t10.md'}
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def main():
    paths=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode('utf-8').strip('\0').split('\0')
    assert paths and all(p in SINGLE or p.startswith('evidencias/T10/') for p in paths),'Staging fora do escopo'
    nominal=read('restrito/t03/mapa-nominal.json');raw=read('restrito/t05/checkpoint.json')['observado']
    prepared=read('restrito/t10/checkpoint.json')
    terms={str(r[k]).casefold() for r in nominal for k in ['nome_bruto','nome_normalizado','aluno_local_id','matricula_local_id'] if r.get(k)}
    terms.update(r['avaliacao_local_id'].casefold() for r in raw['avaliacoes'])
    terms.update(r['chave'].casefold() for r in prepared['intervencao'])
    hashes={}
    for p in paths:
        assert Path(p).suffix.lower() not in {'.xlsx','.png','.pdf','.docx','.gdoc'},'Artefato restrito/externo no staging'
        blob=subprocess.check_output(['git','show',':'+p],cwd=ROOT)
        assert blob==(ROOT/p).read_bytes(),'Git normalizou bytes com hashes historicos'
        folded=blob.decode('utf-8').casefold()
        assert not any(t in folded or html.escape(t) in folded for t in terms),'Termo individual no staging'
        hashes[p]=hashlib.sha256(blob).hexdigest()
    result=dict(status='PASS',arquivos=len(paths),escopo_exclusivamente_T10=True,bytes_git_iguais_aos_recibos=True,
        nomes_ids_chaves_reais_ausentes=True,nominais_derivados_fora_git=True,hashes=hashes)
    # O recibo não contém conteúdo individual; é adicionado depois da conferência.
    (ROOT/'evidencias/T10/staging-resultado.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='hashes'}))
if __name__=='__main__':main()
