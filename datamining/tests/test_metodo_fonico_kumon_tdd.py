"""
========================================================================================
SUÍTE DE TESTES TDD: MÉTODO FÔNICO SISTEMÁTICO & KUMON GRANULAR EM REDE INTERDISCIPLINAR
Ecossistema Educacional Airam Veras | Município de Crateús - CE
Validação Rigorosa baseada em SDD (Software Design Document) e Neurociência Cognitiva
========================================================================================
"""
import sqlite3
import pytest
from pathlib import Path

# Localização do banco SQLite auditável
DB_PATH = Path(__file__).resolve().parent.parent / "dados" / "airam_veras_ecossistema.sqlite"

@pytest.fixture(scope="module")
def db_conn():
    assert DB_PATH.exists(), f"Banco de dados não encontrado em {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()

def test_metodologias_canonicas_existencia(db_conn):
    """
    Verifica a existência das 3 metodologias canônicas estruturadas com respaldo em neurociência.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT codigo_metodologia, nome_metodologia, referencia_principal, doi_referencia 
        FROM dim_metodologias_aprendizagem
    """)
    rows = cur.fetchall()
    assert len(rows) == 3, f"Esperado 3 metodologias, encontrado {len(rows)}"
    metods = {r["codigo_metodologia"]: r for r in rows}
    
    assert "MET_FONICO_SISTEMATICO" in metods
    assert "MET_KUMON_GRANULAR" in metods
    assert "MET_NEUROCIENCIA_REDE" in metods

    # Validar presença de DOIs auditáveis
    for m_id, row in metods.items():
        assert row["doi_referencia"] is not None and row["doi_referencia"].startswith("10."), f"DOI inválido para {m_id}"

def test_kumon_granular_progression_invariants(db_conn):
    """
    TDD Invariante 1: O grafo de níveis granulares do Kumon deve ser estritamente sequencial,
    com pré-requisitos bem encadeados, tempo padrão SCT entre 1 e 20 minutos por folha e meta de maestria >= 85%.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT codigo_nivel, disciplina_eixo, tempo_padrao_conclusao_min, meta_maestria_pct, prerequisito_nivel
        FROM dim_kumon_niveis_granulares
        ORDER BY disciplina_eixo, id
    """)
    niveis = cur.fetchall()
    assert len(niveis) == 12, f"Esperado 12 níveis de Kumon, encontrado {len(niveis)}"

    mat_niveis = [n for n in niveis if n["disciplina_eixo"] == "MATEMATICA"]
    leit_niveis = [n for n in niveis if n["disciplina_eixo"] == "LEITURA_LINGUAGEM"]

    assert len(mat_niveis) == 7, "Matemática deve cobrir 7 micro-níveis (7A até B)"
    assert len(leit_niveis) == 5, "Leitura/Linguagem deve cobrir 5 micro-níveis (7A até BII)"

    for disc_niveis in [mat_niveis, leit_niveis]:
        for i, n in enumerate(disc_niveis):
            assert n["meta_maestria_pct"] >= 85.0, f"Meta de maestria mínima deve ser >= 85% para {n['codigo_nivel']}"
            assert 1 <= n["tempo_padrao_conclusao_min"] <= 20, f"SCT fora dos limites (1-20 min) para {n['codigo_nivel']}"
            if i == 0:
                assert n["prerequisito_nivel"] is None
            else:
                assert n["prerequisito_nivel"] == disc_niveis[i-1]["codigo_nivel"]

def test_metodo_fonico_decodificacao_automatizacao(db_conn):
    """
    TDD Invariante 2: Os estágios de Ehri e Dehaene devem cobrir os 4 marcos do desenvolvimento
    da leitura (Pré-Alfabético a Consolidado/Lexical) com áreas corticais e fases específicas.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT codigo_estagio, nome_estagio, fase_ehri_correspondente, processo_neurofuncional
        FROM dim_metodo_fonico_estagios
        ORDER BY id
    """)
    estagios = cur.fetchall()
    assert len(estagios) == 4, f"Esperado 4 estágios fônicos, encontrado {len(estagios)}"

    fases = [e["fase_ehri_correspondente"] for e in estagios]
    assert "Fase Pré-Alfabética" in fases[0]
    assert "Fase Alfabética Inicial" in fases[1]
    assert "Fase Alfabética Plena" in fases[2]
    assert "Fase Alfabética Consolidada" in fases[3]
    
    # Validações neurofuncionais (Dehaene / Rota Lexical e VWFA)
    assert "VWFA" in estagios[3]["processo_neurofuncional"]
    assert "lexical" in estagios[3]["processo_neurofuncional"].lower()

def test_rede_interdisciplinar_correlacao_grafo(db_conn):
    """
    TDD Invariante 3: A rede interdisciplinar deve conectar os níveis granulares do Kumon e estágios fônicos
    às habilidades BNCC com pesos sinérgicos válidos (0.0 < peso <= 2.0) e hashes de integridade.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT id, origem_tipo, origem_codigo, componente_conectado, habilidade_bncc_conectada, peso_conexao, hash_conexao
        FROM rel_kumon_fonico_rede_interdisciplinar
    """)
    arestas = cur.fetchall()
    assert len(arestas) >= 9, f"Esperado pelo menos 9 arestas interdisciplinares, encontrado {len(arestas)}"

    for a in arestas:
        assert 0.0 < a["peso_conexao"] <= 2.0, f"Peso de conexão fora do intervalo permitido: {a['peso_conexao']}"
        assert a["origem_tipo"] in ["KUMON", "FONICO"]
        assert len(a["habilidade_bncc_conectada"]) > 0
        assert len(a["hash_conexao"]) == 64, "Hash de integridade da conexão deve ter 64 caracteres (SHA-256)"

def test_validacao_maestria_tempo_padrao_sct(db_conn):
    """
    TDD Invariante 4: Regra de progressão censitária: Alunos com status 'Ritmo Padrão Consolidado'
    devem possuir taxa de maestria granular >= 70.0% e tempo médio por folha <= 20 minutos.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT 
            aluno_hash_id,
            nivel_kumon_mat_atual,
            nivel_kumon_leit_atual,
            taxa_maestria_granular_pct,
            tempo_medio_folha_min,
            status_evolucao_kumon
        FROM fato_trilha_aprendizagem_granular_aluno
        WHERE status_evolucao_kumon = 'Ritmo Padrão Consolidado'
    """)
    consolidados = cur.fetchall()
    assert len(consolidados) == 24, "Esperado exatamente 24 alunos consolidados no ritmo padrão censitário"
    
    for row in consolidados:
        assert row["taxa_maestria_granular_pct"] >= 70.0, (
            f"Violação de maestria no aluno {row['aluno_hash_id']}: taxa {row['taxa_maestria_granular_pct']}% < 70%"
        )
        assert row["tempo_medio_folha_min"] <= 20.0, (
            f"Violação de SCT no aluno {row['aluno_hash_id']}: tempo {row['tempo_medio_folha_min']} min > 20 min"
        )

def test_integridade_censitaria_hash_sha256(db_conn):
    """
    TDD Invariante 5: Garantir que todos os 172 estudantes da Escola Airam Veras
    possuam exatamente uma trilha ativa na fato_trilha_aprendizagem_granular_aluno,
    preservando estritamente a política Zero-PII via hash SHA-256 e hash forense.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT aluno_hash_id, hash_validacao_forense, indice_autodidatismo_pct
        FROM fato_trilha_aprendizagem_granular_aluno
    """)
    alunos = cur.fetchall()
    assert len(alunos) == 172, f"Esperado 172 alunos censitários, encontrado {len(alunos)}"

    for a in alunos:
        # Validar hash SHA-256 hexadecimal com 64 caracteres
        assert len(a["aluno_hash_id"]) == 64
        assert int(a["aluno_hash_id"], 16) >= 0
        assert len(a["hash_validacao_forense"]) == 64
        assert 0.0 <= a["indice_autodidatismo_pct"] <= 100.0

def test_resistencia_estatistica_tolerancia_epsilon(db_conn):
    """
    TDD Invariante 6: Todas as métricas de proficiência e acurácia devem estar estritamente
    no domínio percentual [0.0, 100.0] com tolerância numérica epsilon < 1e-9.
    """
    cur = db_conn.cursor()
    cur.execute("""
        SELECT taxa_maestria_granular_pct, indice_autodidatismo_pct, tempo_medio_folha_min 
        FROM fato_trilha_aprendizagem_granular_aluno
    """)
    rows = cur.fetchall()
    eps = 1e-9
    for r in rows:
        assert -eps <= r["taxa_maestria_granular_pct"] <= 100.0 + eps
        assert -eps <= r["indice_autodidatismo_pct"] <= 100.0 + eps
        assert r["tempo_medio_folha_min"] > 0.0
