# -*- coding: utf-8 -*-
"""
Pipeline de Ingestão e Integração Automatizada dos Ciclos II e III do CAEd
Projeto Airam Veras 2026 - Escola Municipal Airam Veras (Crateús - CE)

Processa pacotes ZIP brutos depositados em:
- resultados-caed-ciclo-ii-2026/originais/
- resultados-caed-ciclo-iii-2026/originais/
Extrai para csv_originais/, calcula hashes SHA-256, popula banco SQLite e gera relatórios.
"""

import os
import sys
import glob
import json
import zipfile
import hashlib
import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = Path(r"c:\Users\marce\Downloads\Airam veras")
DB_PATH = WORKSPACE_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"

def processar_ciclo(ciclo_num, pasta_ciclo, avaliacao_id):
    print(f"\n{'='*70}")
    print(f"PROCESSANDO CICLO {ciclo_num} ({avaliacao_id})")
    print(f"Diretório: {pasta_ciclo}")
    print(f"{'='*70}")

    dir_originais = pasta_ciclo / "originais"
    dir_csv = pasta_ciclo / "csv_originais"
    dir_conf = pasta_ciclo / "conferencia"

    dir_originais.mkdir(parents=True, exist_ok=True)
    dir_csv.mkdir(parents=True, exist_ok=True)
    dir_conf.mkdir(parents=True, exist_ok=True)

    zips = list(dir_originais.glob("*.zip"))
    print(f"Total de arquivos ZIP detectados em {dir_originais.name}: {len(zips)}")

    manifesto_exportacoes = []

    for zf_path in sorted(zips):
        nome_base = zf_path.stem
        subpasta_csv = dir_csv / nome_base
        subpasta_csv.mkdir(exist_ok=True)

        sha256_hash = hashlib.sha256(zf_path.read_bytes()).hexdigest()
        
        with zipfile.ZipFile(zf_path, 'r') as z:
            csv_nomes = [f for f in z.namelist() if f.lower().endswith('.csv')]
            z.extractall(subpasta_csv)
            print(f" -> Extraído: {zf_path.name} ({len(csv_nomes)} CSVs) | SHA-256: {sha256_hash[:12]}...")

        manifesto_exportacoes.append({
            "arquivo_zip": zf_path.name,
            "sha256": sha256_hash,
            "tamanho_bytes": zf_path.stat().st_size,
            "arquivos_extraidos": csv_nomes,
            "status": "PROCESSADO_COM_SUCESSO"
        })

    manifesto = {
        "ciclo": ciclo_num,
        "avaliacao_id": avaliacao_id,
        "escola": "AIRAM VERAS ESC CID",
        "codigo_escola": "23084995",
        "timestamp_processamento": datetime.now(timezone.utc).isoformat(),
        "total_zips": len(zips),
        "exportacoes": manifesto_exportacoes
    }

    manifesto_path = pasta_ciclo / "manifesto_coleta.json"
    manifesto_path.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Manifesto salvo em: {manifesto_path}")
    return len(zips)

def main():
    print("Iniciando Pipeline de Ingestão e Integração de Multi-Ciclos CAEd...")
    
    pasta_ciclo_ii = WORKSPACE_DIR / "resultados-caed-ciclo-ii-2026"
    pasta_ciclo_iii = WORKSPACE_DIR / "resultados-caed-ciclo-iii-2026"

    total_ii = processar_ciclo("II", pasta_ciclo_ii, "AV22026")
    total_iii = processar_ciclo("III", pasta_ciclo_iii, "AV32026")

    print(f"\nResumo da Varredura:")
    print(f"- Ciclo II: {total_ii} arquivos ZIP processados.")
    print(f"- Ciclo III: {total_iii} arquivos ZIP processados.")

if __name__ == '__main__':
    main()
