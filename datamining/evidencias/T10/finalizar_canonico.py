"""Move somente a saída derivada aprovada para seu nome canônico local."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    folder=ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53'
    source=(folder/'versoes/autoria04/intervencao-restrita.xlsx').resolve()
    target=(folder/'intervencao-restrita.xlsx').resolve()
    if not source.is_relative_to(folder.resolve()) or not target.is_relative_to(folder.resolve()):raise ValueError('Fora do destino autorizado')
    if not source.is_file() or target.exists():raise ValueError('Origem ausente ou destino existente: preservar')
    expected=json.loads((ROOT/'evidencias/T10/workbook-resultado.json').read_text(encoding='utf-8'))
    before=sha(source)
    if before!=expected['xlsx_sha256'] or expected['roundtrip_sem_erros'] is not True:raise ValueError('Autoria/reabertura nao conferida')
    source.rename(target)
    after=sha(target)
    if before!=after:raise ValueError('Bytes divergentes apos movimento')
    receipt=dict(timestamp=datetime.now(timezone.utc).isoformat(),origem=str(source),destino=str(target),
        sha256_antes=before,sha256_depois=after,mesmo_volume=True,originais_modificados=False,
        nominal_canonico_unico=not source.exists())
    (ROOT/'evidencias/T10/canonico-resultado.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt))
if __name__=='__main__':main()
