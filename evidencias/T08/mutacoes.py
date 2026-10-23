"""Contraprovas funcionais em cópias temporárias com fixtures sintéticas."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[2]
MUTATIONS=[
    ('ausencia_zero','airam/clusters.py',
     "valid=np.isfinite(x).all(axis=1)&(coverage>=config['cobertura_minima'])",
     "x=np.nan_to_num(x); valid=np.ones(len(x),dtype=bool)",
     'tests/test_clusters.py::test_T47_ausencia_excluida_zero_obtido_e_constante_preservados'),
    ('ignora_estabilidade_grupo','airam/clusters.py',
     "failures.append('estabilidade_grupo')","pass",
     'tests/test_clusters.py::test_T46_filtro_grupo_reprova_mesmo_com_ari_alto'),
    ('minimo_ignorado','airam/clusters.py',
     "failures.append('tamanho_original')","pass",
     'tests/test_clusters.py::test_T46_um_perfil_e_grupo_pequeno_nao_sao_liberados'),
    ('fanout_perfil','airam/perfis_grupo.py',
     "n,d=_total(rows); totals=[_total(rs) for rs in by_student.values()]",
     "n,d=_total(rows); n=n*2 if n is not None else n; d=d*2 if d is not None else d; totals=[_total(rs) for rs in by_student.values()]",
     'tests/test_perfis_grupo.py::test_T48_fanout_nao_multiplica_contagens_e_contexto_nao_mistura')]


def main():
    receipts=[]
    for name,path,before,after,test in MUTATIONS:
        with tempfile.TemporaryDirectory(prefix='airam-t08-mutacao-') as temp:
            folder=Path(temp)
            for directory in ('airam','tests','config'):
                shutil.copytree(ROOT/directory,folder/directory,ignore=shutil.ignore_patterns('__pycache__'))
            source=folder/path; text=source.read_text(encoding='utf-8')
            assert text.count(before)==1,'Alvo de mutacao divergente'
            source.write_text(text.replace(before,after),encoding='utf-8')
            snapshot=dict(timestamp=datetime.now(timezone.utc).isoformat(),mutacao=name,teste=test,
                hashes={str(p.relative_to(folder)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                        for part in ('airam','tests','config') for p in (folder/part).rglob('*') if p.is_file()},
                original_sha256=hashlib.sha256((ROOT/path).read_bytes()).hexdigest())
            snap=ROOT/'evidencias/T08'/f'mutacao-{name}-antes.json'
            snap.write_text(json.dumps(snapshot,indent=2)+'\n',encoding='utf-8')
            proc=subprocess.run([sys.executable,'-m','pytest',test,'-q'],cwd=folder,capture_output=True,text=True,
                                encoding='utf-8',env={**os.environ,'PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'})
            log=ROOT/'evidencias/T08'/f'mutacao-{name}.log'
            log.write_text(proc.stdout+proc.stderr,encoding='utf-8')
            receipt=dict(mutacao=name,codigo_saida=proc.returncode,detectada=proc.returncode==1 and '1 failed' in proc.stdout,
                snapshot_sha256=hashlib.sha256(snap.read_bytes()).hexdigest(),log_sha256=hashlib.sha256(log.read_bytes()).hexdigest())
            receipts.append(receipt)
    (ROOT/'evidencias/T08/mutacoes-resultado.json').write_text(json.dumps(receipts,indent=2)+'\n',encoding='utf-8')
    assert all(r['detectada'] for r in receipts),'Mutacao nao detectada'
    print(json.dumps(dict(status='PASS',mutacoes=len(receipts),detectadas=sum(r['detectada'] for r in receipts))))


if __name__=='__main__': main()
