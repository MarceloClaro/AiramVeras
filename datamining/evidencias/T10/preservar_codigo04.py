"""Preserva fontes de04 confirmadas contra os hashes contemporâneos do snapshot."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    snap=json.loads((ROOT/'evidencias/T10/workbook04-antes.json').read_text(encoding='utf-8'))
    files={}
    for p in ['reports/build_workbook.mjs','reports/templates/relatorio.html','airam/relatorio.py',
              'tests/test_intervencao.py','tests/test_relatorio.py','tests/fixtures/t10_workbook.json',
              'tests/fixtures/t10_workbook_heterogeneo.json']:
        candidates=[ROOT/p,ROOT/'.superpowers/sdd/implementation-plan/t10-mutacoes-03/necessidade_invertida'/p]
        blob=next((c.read_bytes() for c in candidates if c.is_file() and sha(c.read_bytes())==snap['hashes_codigo'][p]),None)
        if blob is None:raise ValueError('Fonte historica nao recuperada: '+p)
        files[p]=dict(sha256=sha(blob),conteudo_utf8=blob.decode('utf-8'))
    target=ROOT/'evidencias/T10/codigo-autoria04-preservado.json'
    if target.exists():raise ValueError('Preservar copia anterior')
    target.write_text(json.dumps(dict(timestamp_preservacao=datetime.now(timezone.utc).isoformat(),
        criterio='Copia posterior confirmada pelo SHA do snapshot anterior a execucao04; nao e novo snapshot retrospectivo.',
        snapshot_sha256=sha((ROOT/'evidencias/T10/workbook04-antes.json').read_bytes()),fontes=files),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'fontes_preservadas':len(files),'hashes_contemporaneos_confirmados':True,'arquivo_sha256':sha(target.read_bytes())}))
if __name__=='__main__':main()
