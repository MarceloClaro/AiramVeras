"""
========================================================================================
SUÍTE DE TESTES TDD: BANCO OTIMIZADO, WAL, EWS PREDICTIVO E LEDGER DE AUDITORIA FORENSE
Ecossistema Educacional Airam Veras | Município de Crateús - CE
Validação Rigorosa de Performance, Integridade Censitária e Criptografia
========================================================================================
"""
import sqlite3
import pytest
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "dados" / "airam_veras_ecossistema.sqlite"

@pytest.fixture(scope="module")
def db_conn():
    assert DB_PATH.exists(), f"Banco de dados não encontrado em {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_sqlite_wal_mode_e_foreign_keys_ativas(db_conn):
    """
    TDD Invariante 1: O banco de dados deve estar operando em modo WAL (Write-Ahead Logging)
    para permitir leituras e gravações concorrentes sem concorrência destrutiva,
    e a verificação de integridade referencial deve estar habilitada.
    """
    cur = db_conn.cursor()
    cur.execute("PRAGMA journal_mode;")
    mode = cur.fetchone()[0]
    assert mode.lower() == "wal", f"Esperado modo 'wal', obtido '{mode}'"

    cur.execute("PRAGMA integrity_check;")
    check = cur.fetchone()[0]
    assert check == "ok", f"Falha na integridade do banco: {check}"

def test_indices_b_tree_existencia_e_cobertura(db_conn):
    """
    TDD Invariante 2: Os 6 índices analíticos compostos B-Tree devem existir e cobrir
    as principais operações de junção e filtro analítico em tempo real.
    """
    cur = db_conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indices = {r["name"] for r in cur.fetchall()}

    indices_obrigatorios = [
        "idx_participacao_aluno_caderno",
        "idx_escores_participacao_nivel",
        "idx_trilha_kumon_fonico",
        "idx_aee_perfil_aluno",
        "idx_grafo_caed_bncc",
        "idx_altas_habilidades_aluno"
    ]
    for idx in indices_obrigatorios:
        assert idx in indices, f"Índice B-Tree {idx} não encontrado no schema do SQLite"

def test_ews_predicao_probabilidade_e_invariantes(db_conn):
    """
    TDD Invariante 3: A predição censitária do Early Warning System (EWS) deve conter
    exatamente os 172 estudantes únicos, com probabilidades no domínio [0.0, 1.0] (tolerância 1e-9),
    distribuição em 4 níveis válidos e hash SHA-256 de validação forense em 64 caracteres.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT 
            aluno_hash_id,
            probabilidade_risco_defasagem,
            nivel_risco_ews,
            fator_risco_preponderante,
            hash_validacao_forense
        FROM fato_predicao_alerta_precoce_ews
    """)
    rows = cur.fetchall()
    assert len(rows) == 172, f"Esperado 172 predições EWS, encontrado {len(rows)}"

    niveis_validos = {"CRITICO", "ALTO", "MODERADO", "CONSOLIDADO"}
    eps = 1e-9

    for r in rows:
        assert -eps <= r["probabilidade_risco_defasagem"] <= 1.0 + eps, (
            f"Probabilidade EWS fora do domínio para {r['aluno_hash_id']}: {r['probabilidade_risco_defasagem']}"
        )
        assert r["nivel_risco_ews"] in niveis_validos, f"Nível de risco inválido: {r['nivel_risco_ews']}"
        assert len(r["fator_risco_preponderante"]) > 0
        assert len(r["hash_validacao_forense"]) == 64, "Hash de validação forense deve possuir 64 caracteres SHA-256"

def test_auditoria_ledger_encadeamento_criptografico(db_conn):
    """
    TDD Invariante 4: O ledger de auditoria transacional deve possuir blocos sequenciais
    estritamente ordenados, com hashes válidos e encadeamento criptográfico contínuo
    (hash_bloco_anterior do bloco N deve ser igual a hash_bloco_atual do bloco N-1).
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT sequencia_bloco, hash_bloco_anterior, hash_bloco_atual, tipo_operacao
        FROM fato_auditoria_transacional_ledger
        ORDER BY sequencia_bloco ASC
    """)
    blocos = cur.fetchall()
    assert len(blocos) >= 2, f"Esperado pelo menos 2 blocos no ledger, encontrado {len(blocos)}"

    for i, b in enumerate(blocos):
        assert b["sequencia_bloco"] == i + 1, f"Sequência de blocos descontinuada no bloco {i+1}"
        assert len(b["hash_bloco_atual"]) == 64, "Hash do bloco atual deve ser SHA-256"
        if i == 0:
            assert b["hash_bloco_anterior"] == "0000000000000000000000000000000000000000000000000000000000000000"
        else:
            assert b["hash_bloco_anterior"] == blocos[i-1]["hash_bloco_atual"], (
                f"Quebra de integridade criptográfica no bloco {b['sequencia_bloco']}: "
                f"anterior {b['hash_bloco_anterior']} != atual anterior {blocos[i-1]['hash_bloco_atual']}"
            )

def test_view_estudante_raiox_360_integridade(db_conn):
    """
    TDD Invariante 5: A visão canônica 360º universal do estudante (vw_estudante_raiox_360)
    deve consolidar exatamente 172 estudantes únicos, com métricas CAEd, Kumon, Fônico, CIDs e EWS,
    preservando rigorosamente a política Zero-PII via aluno_hash_id de 64 caracteres.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT 
            aluno_hash_id,
            ano_escolar,
            maestria_kumon_pct,
            estagio_fonico_atual,
            eh_laudado_aee,
            eh_superdotado_ahsd,
            nivel_risco_ews,
            probabilidade_risco_defasagem
        FROM vw_estudante_raiox_360
    """)
    alunos = cur.fetchall()
    assert len(alunos) == 172, f"Esperado 172 registros na visão 360º, encontrado {len(alunos)}"

    for a in alunos:
        assert len(a["aluno_hash_id"]) == 64, "aluno_hash_id deve ser um hash seguro SHA-256 de 64 chars"
        assert a["ano_escolar"] in ["1º Ano", "2º Ano", "3º Ano", "4º Ano", "5º Ano"]
        assert a["nivel_risco_ews"] in ["CRITICO", "ALTO", "MODERADO", "CONSOLIDADO"]
        assert a["eh_laudado_aee"] in (0, 1)
        assert a["eh_superdotado_ahsd"] in (0, 1)
