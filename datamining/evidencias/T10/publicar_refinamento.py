"""Substitui somente derivado canonico, preservando versao e recibos anteriores."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    folder=(ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53').resolve()
    canonical=folder/'intervencao-restrita.xlsx';previous=folder/'versoes/autoria04/intervencao-restrita.xlsx'
    update=folder/'refinamento02/intervencao-restrita.xlsx'
    evidence=ROOT/'evidencias/T10/refinamento-canonico-resultado.json'
    receipt=json.loads((ROOT/'evidencias/T10/refinamento02-invariancia-resultado.json').read_text(encoding='utf-8'))
    assert all(p.resolve().is_relative_to(folder) for p in [canonical,previous,update])
    assert receipt['status']=='PASS' and sha(canonical)==receipt['origem_sha256'] and sha(update)==receipt['xlsx_sha256']
    assert not previous.exists() and not evidence.exists(),'Preservar destino anterior'
    canonical.rename(previous)
    try:update.rename(canonical)
    except BaseException:
        previous.rename(canonical);raise
    assert sha(canonical)==receipt['xlsx_sha256'] and sha(previous)==receipt['origem_sha256']
    result=dict(timestamp=datetime.now(timezone.utc).isoformat(),canonico=str(canonical),versao04=str(previous),
        sha256_final=sha(canonical),sha256_versao04=sha(previous),mesmo_volume=True,originais_modificados=False)
    evidence.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__':main()
