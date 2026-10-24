"""Gera somente fixtures artificiais para medir a cadeia de leitura da fila."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def main():
    original=json.loads((ROOT/'tests/fixtures/t10_workbook.json').read_text(encoding='utf-8'))
    out=ROOT/'.superpowers/sdd/implementation-plan/t10-desempenho'
    out.mkdir(exist_ok=True)
    results=[]
    for n in [40,80]:
        data=deepcopy(original);rows=[]
        for i in range(n):
            r=deepcopy(original['intervencao'][i%6]);r.update(chave=f'ARTIFICIAL-{i:04d}',
                aluno_local_id=f'PESSOA-{i}',avaliacao_local_id=f'APLICACAO-{i}',
                nome='PESSOA ARTIFICIAL '.ljust(70,'X'),notas_docentes=f'NOTA ARTIFICIAL {i}')
            if r['componente'] in ('LEITURA','MATEMATICA') and r['participacao']:
                r.update(acertos=(i*7)%23,oportunidades=22)
            rows.append(r)
        data['intervencao']=rows
        target=out/f'fixture{n:03d}.json'
        if target.exists():raise ValueError('Preservar fixture anterior')
        target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        results.append(dict(n=n,caminho=target.relative_to(ROOT).as_posix(),sha256=hashlib.sha256(target.read_bytes()).hexdigest()))
    (ROOT/'evidencias/T10/desempenho-fixtures.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'fixtures_artificiais':len(results),'sem_dados_reais':True}))
if __name__=='__main__':main()
