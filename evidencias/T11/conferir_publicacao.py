"""Varredura local de candidatos Git; nenhum termo individual é emitido."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]


def main():
    changed=subprocess.check_output(['git','diff','--name-only','HEAD','-z'],cwd=ROOT)
    others=subprocess.check_output(['git','ls-files','--others','--exclude-standard','-z'],cwd=ROOT)
    paths=sorted(set(p.decode('utf-8') for p in (changed+others).split(b'\0') if p))
    mapping=json.loads((ROOT/'restrito/t03/mapa-nominal.json').read_text(encoding='utf-8'))
    terms={row[key].encode('utf-8') for row in mapping for key in
        ('nome_bruto','nome_normalizado','aluno_local_id','matricula_local_id') if row.get(key)}
    examined=0;failures=0
    for relative in paths:
        p=ROOT/relative
        if not p.is_file():continue
        if relative.startswith(('restrito/','secrets/')):failures+=1
        raw=p.read_bytes();failures+=int(any(term in raw for term in terms));examined+=1
    report={'estado':'PASS' if failures==0 else 'FAIL','codigo_saida':0 if failures==0 else 1,
        'arquivos_candidatos_verificados':examined,'arquivos_com_falha':failures,
        'termos_nominais_ou_identificadores_emitidos':False,
        'limite':'Varredura literal complementar; nao substitui revisao independente nem ACL.'}
    p=ROOT/'evidencias/T11/publicacao-resultado.json'
    p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False))
    return report['codigo_saida']


if __name__=='__main__':raise SystemExit(main())
