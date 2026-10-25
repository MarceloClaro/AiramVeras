import sqlite3

conn = sqlite3.connect(r'datamining/dados/airam_veras_ecossistema.sqlite')
cur = conn.cursor()

print("Schema of fato_auditoria_transacional_ledger:")
for col in cur.execute("PRAGMA table_info(fato_auditoria_transacional_ledger);").fetchall():
    print(col)

print("\nLast 5 blocks in fato_auditoria_transacional_ledger:")
for row in cur.execute("SELECT sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash, hash_bloco_atual, timestamp_utc FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 5;").fetchall():
    print(row)

conn.close()
