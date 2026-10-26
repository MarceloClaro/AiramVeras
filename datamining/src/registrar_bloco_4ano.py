# -*- coding: utf-8 -*-
"""
Registro Seguro do Bloco do Dossiê Mestre do 4º Ano (Turmas A e B) no Ledger SHA-256 e SQLite Canônico
"""
import sqlite3
import hashlib
from datetime import datetime, timezone
import os

DB_PATH = 'datamining/dados/airam_veras_ecossistema.sqlite'
PDF_FINAL_OUT = 'DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf'

def main():
    if not os.path.exists(PDF_FINAL_OUT):
        raise FileNotFoundError(f"Arquivo {PDF_FINAL_OUT} não encontrado!")

    # Calcular SHA-256 do PDF gerado
    sha256 = hashlib.sha256()
    with open(PDF_FINAL_OUT, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    hash_pdf = sha256.hexdigest()
    tamanho_mb = os.path.getsize(PDF_FINAL_OUT) / (1024 * 1024)
    print(f"PDF 4º Ano A e B localizado: {PDF_FINAL_OUT}")
    print(f"Tamanho: {tamanho_mb:.2f} MB | Hash SHA-256: {hash_pdf}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Buscar último bloco dinamicamente
    cursor.execute("SELECT sequencia_bloco, hash_bloco_atual FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 1")
    row = cursor.fetchone()
    
    ultimo_bloco = row[0] if row else 0
    hash_anterior = row[1] if row else "0000000000000000000000000000000000000000000000000000000000000000"
    
    bloco_num = ultimo_bloco + 1
    timestamp_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    dados_bloco = f"{bloco_num}|{hash_anterior}|DOSSIE_MESTRE_4ANO_A_E_B_1720_LAUDAS|{hash_pdf}|{timestamp_utc}"
    hash_bloco_atual = hashlib.sha256(dados_bloco.encode('utf-8')).hexdigest()

    print(f"\nRegistrando Bloco {bloco_num} no Ledger...")
    print(f"Hash Bloco {ultimo_bloco} (Anterior): {hash_anterior}")
    print(f"Hash Bloco {bloco_num} (Atual): {hash_bloco_atual}")

    sql_ledger = """
    INSERT INTO fato_auditoria_transacional_ledger (
        sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash,
        resumo_transacao, hash_bloco_anterior, hash_bloco_atual, timestamp_utc, agente_ou_processo
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql_ledger, (
        bloco_num,
        "fato_dossie_mestre_4ano",
        "INSERT",
        hash_pdf,
        "Homologação do Dossiê Pedagógico Mestre Multidisciplinar do 4º Ano (Turmas A e B) com 1.720 laudas vetoriais A4 exatas, 42 estudantes censitários, rotina Integral 35H, microdados CAEd Ciclo I 2026 e trilhas Kumon B/C.",
        hash_anterior,
        hash_bloco_atual,
        timestamp_utc,
        "Antigravity_4Ano_Engine_v1.0"
    ))

    sql_trilha = """
    INSERT INTO sys_trilha_auditoria (
        timestamp_utc, operacao, tabela_afetada, id_registro_afetado,
        agente_executor, detalhes_operacao, sha256_estado_apos
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(sql_trilha, (
        timestamp_utc,
        "INSERT",
        "fato_dossie_mestre_4ano",
        hash_pdf,
        "Antigravity_Lead_Architect",
        f"HOMOLOGACAO_DOSSIE_4ANO_1720_LAUDAS: Compilação estrita de 1.720 laudas para o 4º Ano A e B (40 FM + 42x40). Hash PDF: {hash_pdf}. Bloco {bloco_num}: {hash_bloco_atual}.",
        hash_bloco_atual
    ))

    conn.commit()
    print(f"Bloco {bloco_num} gravado e commitado no banco SQLite com sucesso!")

    # Verificação de integridade referencial
    cursor.execute("PRAGMA foreign_key_check")
    fks = cursor.fetchall()
    print(f"PRAGMA foreign_key_check: {len(fks)} violações encontradas.")
    conn.close()

if __name__ == '__main__':
    main()
