"""Último gate de bytes staged e ausência de identificadores reais."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)


def main():
    paths=git('diff','--cached','--name-only','-z').decode().split('\0')
    paths=[p for p in paths if p]
    if not paths: raise ValueError('Nenhum arquivo staged')
    forbidden=('restrito/','.superpowers/','evidencias/bootstrap/','estatistica/t08/versoes/')
    if any(p.startswith(forbidden) for p in paths): raise ValueError('Caminho fora de escopo staged')
    tokens=set()
    def collect(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if k in ('aluno_local_id','avaliacao_local_id','nome','nome_normalizado') and isinstance(v,str) and len(v)>3:
                    tokens.add(v.encode())
                collect(v)
        elif isinstance(value,list):
            for v in value: collect(v)
    collect(json.loads((ROOT/'restrito/t05/checkpoint.json').read_text(encoding='utf-8')))
    hashes={}
    for p in paths:
        blob=git('show',':'+p)
        if any(t in blob for t in tokens): raise ValueError('Dado individual staged')
        if p not in ('.gitattributes','.gitignore') and blob!=(ROOT/p).read_bytes():
            raise ValueError('Bytes staged diferentes da evidencia local')
        hashes[p]=hashlib.sha256(blob).hexdigest()
    ignored=subprocess.run(['git','check-ignore','--quiet','restrito/t08/checkpoint.json'],cwd=ROOT).returncode==0
    if not ignored: raise ValueError('Checkpoint individual nao ignorado')
    diff=subprocess.run(['git','diff','--cached','--check'],cwd=ROOT,capture_output=True,text=True)
    if diff.returncode: raise ValueError('Whitespace staged divergente')
    report=dict(status='PASS',arquivos=len(paths),restrito_ignorado=ignored,hashes_staged=hashes,
        limite='Varredura por identificadores efetivos e igualdade de bytes; nao certifica ACL')
    (ROOT/'evidencias/T08/staging-resultado.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PASS',arquivos=len(paths),restrito_ignorado=ignored)))


if __name__=='__main__': main()
