"""Contraprovas em cópias só de código/fixtures artificiais, sem tocar produto/fonte."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidencias/T10'
LABEL=sys.argv[1] if len(sys.argv)>1 else '01'
SCRATCH=ROOT/('.superpowers/sdd/implementation-plan/t10-mutacoes-'+LABEL)
PREFIX='' if LABEL=='01' else LABEL+'-'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    mutants=[
        ('necessidade_invertida','airam/relatorio.py',"(-1 if order=='necessidade' else 1)","(1 if order=='necessidade' else -1)",'test_t25_maior'),
        ('vazamento_agregado','airam/relatorio.py','    validar_agregado(resultados)\n','    pass  # mutacao deliberada\n','test_t52'),
        ('obrigacao_80_por_H','airam/relatorio.py',"        gap=result['lacuna']\n","        if hs and result['lacuna']==0: result['lacuna']=1\n        gap=result['lacuna']\n",'test_total80'),
        ('desempate_removido','reports/build_workbook.mjs',
            '1+AI${r}+AJ${r}+AK${r}',
            '1+AI${r}+AJ${r}',
            'test_t24_excel'),
        ('observacoes_reais_na_previa','reports/build_workbook.mjs',
            'sintetico:true,intervencao:rows,habilidades,maior_nome,',
            'sintetico:true,intervencao:data.intervencao,habilidades:data.habilidades,maior_nome,',
            'test_previa_substitui'),
    ]
    results=[]
    for name,relative,before,after,test in mutants:
        target=SCRATCH/name
        if target.exists():raise ValueError('Preservar tentativa anterior')
        target.mkdir(parents=True)
        files=[*ROOT.joinpath('airam').glob('*.py'),ROOT/'tests/test_intervencao.py',ROOT/'tests/test_relatorio.py',
            ROOT/'tests/fixtures/t10_workbook.json',ROOT/'reports/build_workbook.mjs',ROOT/'reports/templates/relatorio.html',ROOT/'pyproject.toml']
        for f in files:
            dest=target/f.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(f,dest)
        p=target/relative;text=p.read_text(encoding='utf-8')
        if before not in text:raise ValueError('Alvo de mutacao ausente')
        p.write_text(text.replace(before,after,1),encoding='utf-8')
        command=[sys.executable,'-m','pytest','tests/test_intervencao.py','tests/test_relatorio.py','-q','-k',test,'--tb=short']
        snapshot=dict(timestamp=datetime.now(timezone.utc).isoformat(),comando=command,
            hashes={f.relative_to(ROOT).as_posix():sha(target/f.relative_to(ROOT)) for f in files},
            runtime_bundle='26.1020.11127',artifact_tool='2.8.99',fixture_sha256=sha(target/'tests/fixtures/t10_workbook.json'))
        (OUT/(PREFIX+name+'-antes.json')).write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
        proc=subprocess.run(command,cwd=target,capture_output=True,text=True,encoding='utf-8',
            env={**os.environ,'AIRAM_ARTIFACT_RUNTIME':str(ROOT/'.superpowers/sdd/implementation-plan/runtime-probe')})
        log=OUT/(PREFIX+name+'.log');log.write_text(proc.stdout+proc.stderr,encoding='utf-8')
        if proc.returncode!=1 or ' failed' not in proc.stdout or 'ERROR collecting' in proc.stdout:
            raise AssertionError('Mutacao nao detectada funcionalmente: '+name)
        results.append(dict(mutacao=name,detectada=True,codigo_saida=proc.returncode,log_sha256=sha(log),
            snapshot_sha256=sha(OUT/(PREFIX+name+'-antes.json')),fim=datetime.now(timezone.utc).isoformat()))
    (OUT/('mutacoes'+LABEL+'-resultado.json')).write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'mutacoes_detectadas':len(results),'produto_original_alterado':False}))


if __name__=='__main__':main()
