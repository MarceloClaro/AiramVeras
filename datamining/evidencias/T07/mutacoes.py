"""Mutações em cópia temporária; não altera produto ou dados reais."""
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
CASES=[('fanout','grafo.py','np.divide(b,total,out=b,where=total>0)','b = b',
        'tests/test_grafo.py::test_t32_many_edges_and_duplicates_do_not_multiply_mass'),
       ('dois_passos','grafo.py','else a @ a','else a.copy()',
        'tests/test_grafo.py::test_t34_two_steps_use_original_mask_and_expose_return'),
       ('ausencia_zero','grafo.py','out=np.full_like(p,np.nan)','out=np.zeros_like(p)',
        'tests/test_grafo.py::test_t33_manual_weighted_mask_zero_is_observed_and_isolated_absent'),
       ('media_taxas','agregacoes.py','taxa_observada=n/d if d else None',
        "taxa_observada=sum(r['numerador']/r['denominador'] for r in valid)/len(valid) if valid else None",
        'tests/test_agregacoes.py::test_t35_overlapping_groups_school_deduplicates_and_uses_ratio_of_sums')]


def main():
    results=[]
    for name,file,old,new,test in CASES:
        with tempfile.TemporaryDirectory(prefix='airam_t07_mutacao_') as tmp:
            root=Path(tmp)
            shutil.copytree(ROOT/'airam',root/'airam',ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copytree(ROOT/'tests',root/'tests',ignore=shutil.ignore_patterns('__pycache__'))
            shutil.copy(ROOT/'pyproject.toml',root/'pyproject.toml')
            target=root/'airam'/file
            content=target.read_text(encoding='utf-8')
            assert old in content
            target.write_text(content.replace(old,new),encoding='utf-8')
            before=dict(timestamp=datetime.now(timezone.utc).isoformat(),mutacao=name,
                comando=[sys.executable,'-m','pytest',test,'-q'],
                hashes={str(p.relative_to(root)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in root.rglob('*') if p.is_file()})
            prefix=ROOT/'evidencias/T07'/('mutacao-'+name)
            before_path=prefix.with_suffix('.antes.json')
            if before_path.exists():
                raise ValueError('Mutacao ja registrada')
            before_path.write_text(json.dumps(before,indent=2)+'\n',encoding='utf-8')
            process=subprocess.run(before['comando'],cwd=root,capture_output=True,text=True,
                encoding='utf-8',env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONUTF8':'1'})
            log=prefix.with_suffix('.log')
            log.write_text(process.stdout+process.stderr,encoding='utf-8')
            results.append(dict(mutacao=name,codigo_saida=process.returncode,
                antes_sha256=hashlib.sha256(before_path.read_bytes()).hexdigest(),
                log_sha256=hashlib.sha256(log.read_bytes()).hexdigest(),
                detectada=process.returncode==1 and '1 failed' in process.stdout and 'ERROR' not in process.stdout))
    (ROOT/'evidencias/T07/mutacoes-resultado.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
    assert all(r['detectada'] for r in results),'Mutacao nao detectada funcionalmente'
    print(json.dumps(dict(mutacoes_detectadas=len(results))))


if __name__=='__main__':
    main()
