"""Mutações isoladas de produto com restauração byte-a-byte e snapshots prévios."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
MUTANTS=[
    ('baseline_ignorada','airam/gates.py',
        "for p,h in baseline['fontes'].items(): validar_fonte(dentro(root,p),h,root)",
        "for p,h in baseline['fontes'].items(): pass",
        'tests/test_hooks.py::test_preflight_real_falha_interrompe_cli_antes_catalogo'),
    ('hook_ignorado','airam/cli.py',"if hook['codigo_saida']:","if False:",
        'tests/test_hooks.py::test_preflight_real_falha_interrompe_cli_antes_catalogo'),
    ('runtime_ignorado','airam/cache.py',"if manifest.get('runtime') != versoes:","if False:",
        'tests/test_cli.py::test_cache_invalida_cada_dependencia_sem_promover_nova_inferencia[runtime]'),
    ('nominal_liberado','airam/gates.py',"if any(word in normalized for word in", "if False and any(word in normalized for word in",
        'tests/test_cli.py::test_t53_t58_release_rejeita_evidencia_incompleta_ou_vazada[nominal]'),
    ('evento_promovido','airam/operacao.py',"'ativo_verificado':verified,", "'ativo_verificado':True,",
        'tests/test_agent_receipts.py::test_evento_configurado_sem_disparo_real_nao_e_ativo')]


def main():
    results=[]
    for name,relative,before,after,test in MUTANTS:
        path=ROOT/relative; original=path.read_bytes(); digest=hashlib.sha256(original).hexdigest()
        text=original.decode('utf-8');
        if text.count(before)!=1:raise ValueError('Mutacao nao localizada unicamente')
        try:
            path.write_bytes(text.replace(before,after).encode('utf-8'))
            run=subprocess.run([sys.executable,'evidencias/T11/executar.py','mutacao-'+name,'MUTACAO',
                '-m','pytest',test,'-q'],cwd=ROOT,capture_output=True)
            receipt=json.loads((ROOT/f'evidencias/T11/mutacao-{name}-recibo.json').read_text())
            log=(ROOT/f'evidencias/T11/mutacao-{name}.log').read_text(encoding='utf-8')
            killed=run.returncode==1 and '1 failed' in log and 'ERROR collecting' not in log
            results.append({'mutacao':name,'codigo_saida':run.returncode,'morta_por_falha_funcional':killed,
                'snapshot_sha256':receipt['snapshot_sha256'],'original_sha256':digest})
        finally:
            path.write_bytes(original)
        if hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Restauracao divergiu')
    out={'estado':'PASS' if all(r['morta_por_falha_funcional'] for r in results) else 'FAIL',
        'resultados':results,'restauracao_bytes_verificada':True}
    (ROOT/'evidencias/T11/mutacoes-resultado.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(out))
    return 0 if out['estado']=='PASS' else 1


if __name__=='__main__':raise SystemExit(main())
