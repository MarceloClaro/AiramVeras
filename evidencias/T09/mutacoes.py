"""Mutações concretas temporárias com recibos antes de cada execução e restauração."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    cases=[
        ('congelar_adequados','airam/cenarios.py',"future = a['adequados'] + entries - exits", "future = a['adequados'] + entries",'tests/test_cenarios.py','T41'),
        ('ignorar_perda_acertos','airam/cenarios.py',"delta = counts['ganho_acertos'] - counts['perda_acertos']", "delta = counts['ganho_acertos']",'tests/test_cenarios.py','aritmetica_individual'),
        ('exportacao_e_aplicacao','airam/predicao_gate.py',"application.get('tipo') != 'aplicacao'",'False','tests/test_predicao_gate.py','exportacao'),
        ('vazamento_alvo','airam/predicao_gate.py','elif set(inputs) & {target,*components}:','elif False:','tests/test_predicao_gate.py','T43'),
        ('aluno_em_ambos','airam/predicao_gate.py',"if members['treino'] & members['teste']:",'if False:','tests/test_predicao_gate.py','T44')]
    reports=[]
    for label,relative,old,new,test,selector in cases:
        path=ROOT/relative; raw=path.read_bytes(); source=raw.decode('utf-8')
        assert source.count(old)==1
        try:
            path.write_text(source.replace(old,new),encoding='utf-8')
            command=[sys.executable,str(ROOT/'evidencias/T09/executar.py'), 'mutacao-'+label,
                     'MUTACAO','-m','pytest',test,'-q','-k',selector]
            code=subprocess.run(command,cwd=ROOT,capture_output=True).returncode
            reports.append(dict(mutacao=label,codigo_saida=code,detectada=code==1,
                codigo_original_sha256=hashlib.sha256(raw).hexdigest()))
        finally:
            path.write_bytes(raw)
        assert code==1, 'Mutacao nao detectada ou erro de ambiente'
        assert path.read_bytes()==raw
    result=dict(mutacoes=reports,restauracao=True)
    (ROOT/'evidencias/T09/mutacoes-resultado.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':
    main()
