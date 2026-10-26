import sqlite3

conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')
cur = conn.cursor()

cur.execute('PRAGMA foreign_key_check;')
res = cur.fetchall()
print(f"Erros de Foreign Key: {len(res)}")

cur.execute('SELECT sequencia_bloco, tabela_afetada, tipo_operacao, hash_bloco_atual, timestamp_utc FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 3')
for r in cur.fetchall():
    print(r)
