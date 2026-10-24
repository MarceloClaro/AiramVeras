"""Handoff parcial minimizado; nenhuma promoção da T10 ou revisão independente."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    paths=[p for directory in ('airam','config','tests','hooks','agents') for p in (ROOT/directory).glob('*')
        if p.is_file() and p.suffix in ('.py','.json','.ps1','.mjs')]
    paths += [ROOT/'.gitattributes',ROOT/'docs/operacao-cli-t11.md']
    evidence=['suite02-antes.json','suite02-recibo.json','suite02.log','mutacoes-resultado.json',
        'contraprova-persistencia.json','publicacao-resultado.json','runtime01-recibo.json']
    payload={'estado':'NEEDS_CONTEXT','timestamp':datetime.now(timezone.utc).isoformat(),
        'spec':'SPEC-AIRAM-001','tarefa':'T11','base_commit':'28d88e356f3ce744f250331aa2f90a8de5bdc6be',
        'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
        't10_aprovado_recebido':False,'revisao_independente_t11':False,
        'codigo_contratos_testes':{p.relative_to(ROOT).as_posix():sha(p) for p in sorted(paths)},
        'evidencias':{f'evidencias/T11/{p}':sha(ROOT/'evidencias/T11'/p) for p in evidence},
        'resultado_sqlite_sha256':'b5ea25c7b47a95a8e085f67c5f13f809d84f6b981b5b72c6c57b6bcb115bc57b',
        'pendencias':['handoff T10 aprovado','relatar/executar e release final',
            'notas docentes por chave e reautoria autenticada','compatibilidade runtime com builder final',
            'revisao independente T11 apos gate T10'],
        'limites':['Reutilizacao autenticada T01-T09; nenhuma nova inferencia.',
            'Ressalvas de snapshots T11 iniciais e T02 preservadas no relatorio.',
            'Nenhum dado individual transmitido; banco/CSV individuais ignorados pelo Git.']}
    target=ROOT/'evidencias/T11/handoff-parcial.json'
    target.write_bytes((json.dumps(payload,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode())
    print(json.dumps({'estado':'NEEDS_CONTEXT','handoff_sha256':sha(target),'testes':371}))


if __name__=='__main__':main()
