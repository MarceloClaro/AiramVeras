"""Acrescenta correção de metadado, sem substituir recibo histórico."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    prior=ROOT/'evidencias/T10/previa-segura-03-resultado.json'
    snapshot=read(ROOT/'evidencias/T10/previa03-antes.json')
    payload=ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53/apresentacao01/previas-sinteticas/entrada-artificial.json'
    actual=read(payload)['fontes']['autoria/builder_js_sha256']
    assert actual==snapshot['hashes_codigo']['reports/build_workbook.mjs']
    assert read(prior)['json_sha256']==sha(payload)
    result=dict(escopo='Correcao aditiva da atribuicao do produtor no scan03, sem alterar teste/arquivo/recibo anterior',
        recibo_anterior_sha256=sha(prior),hash_anterior_era_codigo_do_verificador=read(prior)['builder_sha256'],
        builder_produtor_correto_sha256=actual,entrada_artificial_sha256=sha(payload),
        privacidade_regra_verificada_na_execucao03_inalterada=True,
        previa04_final_tem_produtor_e_verificador_separados=True)
    target=ROOT/'evidencias/T10/previa03-proveniencia-correcao.json'
    if target.exists():raise ValueError('Preservar recibo')
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
