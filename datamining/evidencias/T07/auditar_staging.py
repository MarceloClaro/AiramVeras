"""Última barreira local: blobs selecionados, sigilo e entradas preservadas."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    paths=subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=ROOT).decode().split('\0')
    paths=[p for p in paths if p]
    assert paths and not any(p.startswith(('restrito/','.superpowers/','evidencias/bootstrap/')) for p in paths)
    tokens=set()
    def walk(obj):
        if isinstance(obj,dict):
            for k,v in obj.items():
                if k in ('aluno_local_id','avaliacao_local_id','nome','nome_normalizado') and isinstance(v,str) and len(v)>3:
                    tokens.add(v.encode())
                walk(v)
        elif isinstance(obj,list):
            for v in obj:
                walk(v)
    walk(json.loads((ROOT/'restrito/t05/checkpoint.json').read_text(encoding='utf-8')))
    hashes={}
    for path in paths:
        content=subprocess.check_output(['git','show',':'+path],cwd=ROOT)
        assert not any(t in content for t in tokens),'Identificador individual no staging'
        hashes[path]=hashlib.sha256(content).hexdigest()
        if path.startswith(('evidencias/T07/','estatistica/t07/')):
            assert content==(ROOT/path).read_bytes(),'Bytes de evidencia alterados no staging'
    first=json.loads((ROOT/'evidencias/T07/red01-antes.json').read_text(encoding='utf-8'))
    for path,expected in first['hashes_entradas'].items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,'Fonte alterada'
    assert subprocess.run(['git','check-ignore','-q','restrito/t07/checkpoint.json'],cwd=ROOT).returncode==0
    report=dict(status='PASS',arquivos=len(paths),hashes_blobs=hashes,entradas_preservadas=len(first['hashes_entradas']),
        limites='Verificacao de tokens reais e caminhos selecionados; nao certifica ACL')
    output=ROOT/'evidencias/T07'/(sys.argv[1] if len(sys.argv)>1 else 'staging-resultado.json')
    if output.exists():
        raise ValueError('Preservar auditoria anterior; fornecer nome novo')
    output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PASS',arquivos=len(paths),entradas_preservadas=len(first['hashes_entradas']))))


if __name__=='__main__':
    main()
