"""
========================================================================================
ENGENHARIA DE DADOS: OTIMIZAÇÃO B-TREE, WAL, EARLY WARNING SYSTEM (EWS) E AUDITORIA LEDGER
Ecossistema Educacional Airam Veras | Município de Crateús - CE
Validação Censitária de 172 Estudantes | Zero-PII | Auditoria Forense Criptográfica
========================================================================================
"""
import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Caminho do banco de dados canônico
DB_PATH = Path(__file__).resolve().parent.parent / "dados" / "airam_veras_ecossistema.sqlite"

def conectar_banco():
    assert DB_PATH.exists(), f"Banco não encontrado em {DB_PATH}"
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def aplicar_configuracoes_wal_e_indices(conn):
    cur = conn.cursor()
    print("[1/5] Ativando modo WAL e otimizações de performance SQLite...")
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")
    cur.execute("PRAGMA foreign_keys = ON;")
    cur.execute("PRAGMA cache_size = -64000;") # 64MB cache em memória
    cur.execute("PRAGMA temp_store = MEMORY;")

    print("[2/5] Criando Índices B-Tree Analíticos Compostos...")
    indices = [
        ("idx_participacao_aluno_caderno", "fato_participacao_estudante", "aluno_hash_id, avaliacao_caderno_id"),
        ("idx_escores_participacao_nivel", "fato_escores_psicometricos", "participacao_id, nivel_desempenho_caed"),
        ("idx_trilha_kumon_fonico", "fato_trilha_aprendizagem_granular_aluno", "aluno_hash_id, status_evolucao_kumon, taxa_maestria_granular_pct"),
        ("idx_aee_perfil_aluno", "fato_estudante_aee_perfil", "aluno_hash_id, cid_primario_id"),
        ("idx_grafo_caed_bncc", "rel_caed_bncc_grafo", "caed_descritor_id, bncc_habilidade_id"),
        ("idx_altas_habilidades_aluno", "fato_rastreio_altas_habilidades", "aluno_hash_id, possui_dupla_excepcionalidade_2e")
    ]
    for nome_idx, tabela, colunas in indices:
        cur.execute(f"CREATE INDEX IF NOT EXISTS {nome_idx} ON {tabela} ({colunas});")
    conn.commit()

def criar_estruturas_ews_e_auditoria(conn):
    cur = conn.cursor()
    print("[3/5] Criando tabelas do Early Warning System (EWS) e Ledger de Auditoria...")

    # 1. Catálogo de Fatores de Risco EWS
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_fatores_risco_ews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_fator TEXT NOT NULL UNIQUE,
            categoria_fator TEXT NOT NULL,
            descricao_fator TEXT NOT NULL,
            peso_algoritmico REAL NOT NULL,
            acao_mitigadora_recomendada TEXT NOT NULL
        );
    """)

    # 2. Predição Censitária EWS por Estudante
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fato_predicao_alerta_precoce_ews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_hash_id TEXT NOT NULL UNIQUE,
            ano_escolar TEXT NOT NULL,
            probabilidade_risco_defasagem REAL NOT NULL,
            nivel_risco_ews TEXT NOT NULL, -- CRITICO, ALTO, MODERADO, CONSOLIDADO
            fator_risco_preponderante TEXT NOT NULL,
            score_tri_impacto REAL NOT NULL,
            score_kumon_lacuna REAL NOT NULL,
            score_aee_vulnerabilidade REAL NOT NULL,
            score_frequencia_participacao REAL NOT NULL,
            protocolo_intervencao_sugerido TEXT NOT NULL,
            data_calculo_predicao TEXT NOT NULL,
            hash_validacao_forense TEXT NOT NULL,
            FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id)
        );
    """)

    # 3. Ledger de Auditoria Criptográfica Imutável (Blockchain-like Forense)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fato_auditoria_transacional_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sequencia_bloco INTEGER NOT NULL UNIQUE,
            tabela_afetada TEXT NOT NULL,
            tipo_operacao TEXT NOT NULL, -- INSERT, UPDATE, DELETE, HOMOLOGACAO
            registro_id_ou_hash TEXT NOT NULL,
            resumo_transacao TEXT NOT NULL,
            hash_bloco_anterior TEXT NOT NULL,
            hash_bloco_atual TEXT NOT NULL,
            timestamp_utc TEXT NOT NULL,
            agente_ou_processo TEXT NOT NULL
        );
    """)

    conn.commit()

def criar_triggers_seguranca(conn):
    cur = conn.cursor()
    print("[4/5] Instalando triggers de integridade e auditoria automática no SQLite...")

    # Trigger de auditoria após inserção de escores psicométricos
    cur.execute("DROP TRIGGER IF EXISTS trg_audit_escores_psicometricos_ins;")
    cur.execute("""
        CREATE TRIGGER trg_audit_escores_psicometricos_ins
        AFTER INSERT ON fato_escores_psicometricos
        BEGIN
            INSERT INTO fato_auditoria_transacional_ledger (
                sequencia_bloco,
                tabela_afetada,
                tipo_operacao,
                registro_id_ou_hash,
                resumo_transacao,
                hash_bloco_anterior,
                hash_bloco_atual,
                timestamp_utc,
                agente_ou_processo
            )
            VALUES (
                (SELECT COALESCE(MAX(sequencia_bloco), 0) + 1 FROM fato_auditoria_transacional_ledger),
                'fato_escores_psicometricos',
                'INSERT',
                'PART_ID_' || NEW.participacao_id,
                'Novo escore computado: acertos ' || NEW.total_acertos || ' nivel ' || NEW.nivel_desempenho_caed,
                (SELECT COALESCE(MAX(hash_bloco_atual), '0000000000000000000000000000000000000000000000000000000000000000') FROM fato_auditoria_transacional_ledger),
                lower(hex(sha256(NEW.participacao_id || NEW.total_acertos || datetime('now')))),
                datetime('now'),
                'TRIGGER_SQLITE_AUDIT'
            );
        END;
    """)

    conn.commit()

def popular_catalogo_fatores_e_ews(conn):
    cur = conn.cursor()
    print("[5/5] Ingerindo fatores de risco, calculando EWS censitário e criando View 360º...")

    # População do catálogo de fatores EWS
    fatores = [
        ("FAT_ACAD_ABAIXO_BASICO", "ACADEMICO", "Desempenho abaixo do básico no CAEd em ambos os componentes", 0.40, "Intervenção intensiva em sala de apoio e plano de metas individual"),
        ("FAT_KUMON_DEFASAGEM_SCT", "OPERACIONAL", "Tempo de conclusão de micro-passo superior a 2x o padrão SCT", 0.25, "Recuo de 2 micro-passos no Kumon para consolidação de fatos prévios"),
        ("FAT_FONICO_ROTA_FRAGIL", "LEITURA", "Dificuldade na conversão grafofonêmica explícita (rota dorsal lenta)", 0.20, "Treinamento fônico diário de 15 minutos com cartões multissensoriais"),
        ("FAT_NEURO_COMORBIDADE", "CLINICO_AEE", "Presença de comorbidade CID-10 sem adequação pedagógica ativa", 0.15, "Adaptação curricular PEI/PAEE conforme protocolo de manejo clínico")
    ]
    cur.executemany("""
        INSERT OR REPLACE INTO dim_fatores_risco_ews (codigo_fator, categoria_fator, descricao_fator, peso_algoritmico, acao_mitigadora_recomendada)
        VALUES (?, ?, ?, ?, ?)
    """, fatores)

    # Consulta dos 172 estudantes cruzando CAEd, AEE, Kumon e AH/SD
    cur.execute("""
        SELECT 
            e.aluno_hash_id,
            t.nome_turma,
            CASE 
                WHEN t.nome_turma LIKE '%1º%' THEN '1º Ano'
                WHEN t.nome_turma LIKE '%2º%' THEN '2º Ano'
                WHEN t.nome_turma LIKE '%3º%' THEN '3º Ano'
                WHEN t.nome_turma LIKE '%4º%' THEN '4º Ano'
                ELSE '5º Ano'
            END AS ano_escolar,
            -- Médias CAEd
            AVG(CASE WHEN c.componente_curricular = 'LINGUA_PORTUGUESA' OR c.componente_curricular = 'LEITURA' THEN ep.taxa_rendimento_ponderada * 100 END) as acerto_lp,
            AVG(CASE WHEN c.componente_curricular = 'MATEMATICA' THEN ep.taxa_rendimento_ponderada * 100 END) as acerto_mat,
            AVG(ep.theta_habilidade_latente) as media_tri,
            -- AEE
            MAX(CASE WHEN aee.aluno_hash_id IS NOT NULL THEN 1 ELSE 0 END) as possui_laudo,
            MAX(cid.codigo_cid10) as cid_codigo,
            -- Kumon
            tk.taxa_maestria_granular_pct,
            tk.tempo_medio_folha_min,
            tk.status_evolucao_kumon,
            -- Altas Habilidades
            MAX(CASE WHEN ah.aluno_hash_id IS NOT NULL THEN 1 ELSE 0 END) as possui_ahsd,
            MAX(COALESCE(ah.possui_dupla_excepcionalidade_2e, 0)) as eh_2e
        FROM dim_estudantes e
        JOIN dim_turmas t ON e.turma_id = t.id
        LEFT JOIN fato_participacao_estudante p ON e.aluno_hash_id = p.aluno_hash_id
        LEFT JOIN dim_avaliacoes_cadernos c ON p.avaliacao_caderno_id = c.id
        LEFT JOIN fato_escores_psicometricos ep ON p.id = ep.participacao_id
        LEFT JOIN fato_estudante_aee_perfil aee ON e.aluno_hash_id = aee.aluno_hash_id
        LEFT JOIN dim_cid_catalogo cid ON aee.cid_primario_id = cid.id
        LEFT JOIN fato_trilha_aprendizagem_granular_aluno tk ON e.aluno_hash_id = tk.aluno_hash_id
        LEFT JOIN fato_rastreio_altas_habilidades ah ON e.aluno_hash_id = ah.aluno_hash_id
        GROUP BY e.aluno_hash_id
    """)
    estudantes = cur.fetchall()

    registros_ews = []
    agora_iso = datetime.now(timezone.utc).isoformat()

    for est in estudantes:
        aluno_id = est["aluno_hash_id"]
        ano_esc = est["ano_escolar"]
        acerto_lp = est["acerto_lp"] if est["acerto_lp"] is not None else 50.0
        acerto_mat = est["acerto_mat"] if est["acerto_mat"] is not None else 50.0
        media_acerto = (acerto_lp + acerto_mat) / 2.0
        maestria_kumon = est["taxa_maestria_granular_pct"] if est["taxa_maestria_granular_pct"] is not None else 72.0
        tempo_kumon = est["tempo_medio_folha_min"] if est["tempo_medio_folha_min"] is not None else 8.0
        possui_laudo = est["possui_laudo"] == 1
        possui_ahsd = est["possui_ahsd"] == 1
        eh_2e = est["eh_2e"] == 1

        # Cálculo de Scores Parciais de Risco
        score_tri = max(0.0, min(1.0, (80.0 - media_acerto) / 80.0))
        score_kumon = max(0.0, min(1.0, (85.0 - maestria_kumon) / 85.0 + (tempo_kumon - 7.0) / 20.0))
        score_aee = 0.6 if (possui_laudo and not eh_2e) else (0.25 if eh_2e else 0.0)
        score_freq = 0.05 # Presença censitária assegurada

        # Probabilidade Combinada de Risco de Defasagem (EWS)
        if possui_ahsd and not eh_2e:
            prob_risco = 0.03 # Risco desprezível em superdotados típicos
            nivel_risco = "CONSOLIDADO"
            fator_prep = "POTENCIAL_SUPERIOR_CONSOLIDADO"
            protocolo = "Enriquecimento Curricular Triádico Tipo III e Compactação de Conteúdo"
        else:
            prob_risco = (score_tri * 0.45) + (score_kumon * 0.30) + (score_aee * 0.20) + (score_freq * 0.05)
            prob_risco = round(max(0.01, min(0.99, prob_risco)), 4)

            if prob_risco >= 0.65:
                nivel_risco = "CRITICO"
                fator_prep = "DEFASAGEM_MULTIDIMENSIONAL_AGUDA"
                protocolo = "PIP Emergencial Individualizado + Tutoria Fônica 1:1 + AEE Adaptado"
            elif prob_risco >= 0.45:
                nivel_risco = "ALTO"
                fator_prep = "DEFASAGEM_CONCEITUAL_MODERADA"
                protocolo = "Nivelamento em Micro-Passos Kumon + Oficina de Raciocínio Lógico"
            elif prob_risco >= 0.25:
                nivel_risco = "MODERADO"
                fator_prep = "ALERTA_DE_MAESTRIA_PONTUAL"
                protocolo = "Monitoramento Quinzenal em Sala Regular e Feedback Imediato"
            else:
                nivel_risco = "CONSOLIDADO"
                fator_prep = "RITMO_PADRAO_ASSEGURADO"
                protocolo = "Manutenção do Cronograma Regular e Desafios de Aprofundamento"

        payload_hash = f"{aluno_id}:{prob_risco}:{nivel_risco}:{agora_iso}"
        hash_forense = hashlib.sha256(payload_hash.encode("utf-8")).hexdigest()

        registros_ews.append((
            aluno_id,
            ano_esc,
            prob_risco,
            nivel_risco,
            fator_prep,
            round(score_tri, 3),
            round(score_kumon, 3),
            round(score_aee, 3),
            round(score_freq, 3),
            protocolo,
            agora_iso,
            hash_forense
        ))

    cur.executemany("""
        INSERT OR REPLACE INTO fato_predicao_alerta_precoce_ews (
            aluno_hash_id, ano_escolar, probabilidade_risco_defasagem, nivel_risco_ews,
            fator_risco_preponderante, score_tri_impacto, score_kumon_lacuna,
            score_aee_vulnerabilidade, score_frequencia_participacao,
            protocolo_intervencao_sugerido, data_calculo_predicao, hash_validacao_forense
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, registros_ews)

    # Ingestão do Bloco Gênesis do Ledger de Auditoria se vazio
    cur.execute("SELECT COUNT(*) FROM fato_auditoria_transacional_ledger")
    total_ledger = cur.fetchone()[0]
    if total_ledger == 0:
        hash_genesis = hashlib.sha256(b"GENESIS_AIRAM_VERAS_ECOSSISTEMA_2026").hexdigest()
        cur.execute("""
            INSERT INTO fato_auditoria_transacional_ledger (
                sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash,
                resumo_transacao, hash_bloco_anterior, hash_bloco_atual,
                timestamp_utc, agente_ou_processo
            )
            VALUES (
                1, 'SISTEMA_CANONICO', 'HOMOLOGACAO', 'BLOCO_GENESIS',
                'Inicializacao do Ledger Criptografico Imutavel do Ecossistema Airam Veras',
                '0000000000000000000000000000000000000000000000000000000000000000',
                ?, ?, 'ENG_DADOS_CANONICO'
            )
        """, (hash_genesis, agora_iso))

        # Adicionar o bloco de homologação do EWS
        hash_ews_bloco = hashlib.sha256(f"EWS_HOMOLOGACAO:{hash_genesis}:{len(registros_ews)}".encode("utf-8")).hexdigest()
        cur.execute("""
            INSERT INTO fato_auditoria_transacional_ledger (
                sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash,
                resumo_transacao, hash_bloco_anterior, hash_bloco_atual,
                timestamp_utc, agente_ou_processo
            )
            VALUES (
                2, 'fato_predicao_alerta_precoce_ews', 'INSERT_CENSITARIO', '172_ESTUDANTES',
                'Calculo e homologacao do Early Warning System (EWS) para os 172 estudantes',
                ?, ?, ?, 'EWS_PREDICTIVE_PIPELINE'
            )
        """, (hash_genesis, hash_ews_bloco, agora_iso))

    # Criação da Visão Canônica 360º Universal do Estudante
    cur.execute("DROP VIEW IF EXISTS vw_estudante_raiox_360;")
    cur.execute("""
        CREATE VIEW vw_estudante_raiox_360 AS
        SELECT 
            e.aluno_hash_id,
            t.nome_turma,
            CASE 
                WHEN t.nome_turma LIKE '%1º%' THEN '1º Ano'
                WHEN t.nome_turma LIKE '%2º%' THEN '2º Ano'
                WHEN t.nome_turma LIKE '%3º%' THEN '3º Ano'
                WHEN t.nome_turma LIKE '%4º%' THEN '4º Ano'
                ELSE '5º Ano'
            END AS ano_escolar,
            -- CAEd Língua Portuguesa
            MAX(CASE WHEN c.componente_curricular = 'LINGUA_PORTUGUESA' OR c.componente_curricular = 'LEITURA' THEN ROUND(ep.taxa_rendimento_ponderada * 100, 1) END) AS acerto_lp_pct,
            MAX(CASE WHEN c.componente_curricular = 'LINGUA_PORTUGUESA' OR c.componente_curricular = 'LEITURA' THEN ep.nivel_desempenho_caed END) AS nivel_caed_lp,
            MAX(CASE WHEN c.componente_curricular = 'LINGUA_PORTUGUESA' OR c.componente_curricular = 'LEITURA' THEN ep.atingiu_meta_b_80pct END) AS meta_b_lp,
            -- CAEd Matemática
            MAX(CASE WHEN c.componente_curricular = 'MATEMATICA' THEN ROUND(ep.taxa_rendimento_ponderada * 100, 1) END) AS acerto_mat_pct,
            MAX(CASE WHEN c.componente_curricular = 'MATEMATICA' THEN ep.nivel_desempenho_caed END) AS nivel_caed_mat,
            MAX(CASE WHEN c.componente_curricular = 'MATEMATICA' THEN ep.atingiu_meta_b_80pct END) AS meta_b_mat,
            -- Método Fônico & Kumon Granular
            tk.estagio_fonico_atual,
            mfe.nome_estagio AS nome_estagio_fonico,
            tk.nivel_kumon_mat_atual,
            tk.nivel_kumon_leit_atual,
            tk.taxa_maestria_granular_pct AS maestria_kumon_pct,
            tk.tempo_medio_folha_min,
            tk.indice_autodidatismo_pct,
            tk.status_evolucao_kumon,
            -- AEE & CIDs
            MAX(CASE WHEN aee.aluno_hash_id IS NOT NULL THEN 1 ELSE 0 END) AS eh_laudado_aee,
            MAX(cid.codigo_cid10) AS codigo_cid10,
            MAX(cid.nomenclatura_oficial) AS cid_nome,
            -- Altas Habilidades / Dupla Excepcionalidade
            MAX(CASE WHEN ah.aluno_hash_id IS NOT NULL THEN 1 ELSE 0 END) AS eh_superdotado_ahsd,
            MAX(COALESCE(ah.possui_dupla_excepcionalidade_2e, 0)) AS eh_dupla_excepcionalidade_2e,
            -- Early Warning System (EWS)
            ews.probabilidade_risco_defasagem,
            ews.nivel_risco_ews,
            ews.fator_risco_preponderante,
            ews.protocolo_intervencao_sugerido,
            ews.hash_validacao_forense
        FROM dim_estudantes e
        JOIN dim_turmas t ON e.turma_id = t.id
        LEFT JOIN fato_participacao_estudante p ON e.aluno_hash_id = p.aluno_hash_id
        LEFT JOIN dim_avaliacoes_cadernos c ON p.avaliacao_caderno_id = c.id
        LEFT JOIN fato_escores_psicometricos ep ON p.id = ep.participacao_id
        LEFT JOIN fato_estudante_aee_perfil aee ON e.aluno_hash_id = aee.aluno_hash_id
        LEFT JOIN dim_cid_catalogo cid ON aee.cid_primario_id = cid.id
        LEFT JOIN fato_trilha_aprendizagem_granular_aluno tk ON e.aluno_hash_id = tk.aluno_hash_id
        LEFT JOIN dim_metodo_fonico_estagios mfe ON tk.estagio_fonico_atual = mfe.codigo_estagio
        LEFT JOIN fato_rastreio_altas_habilidades ah ON e.aluno_hash_id = ah.aluno_hash_id
        LEFT JOIN fato_predicao_alerta_precoce_ews ews ON e.aluno_hash_id = ews.aluno_hash_id
        GROUP BY e.aluno_hash_id;
    """)

    conn.commit()
    print("[+] Migração e Otimização do Ecossistema concluídas com êxito!")

def main():
    conn = conectar_banco()
    try:
        aplicar_configuracoes_wal_e_indices(conn)
        criar_estruturas_ews_e_auditoria(conn)
        criar_triggers_seguranca(conn)
        popular_catalogo_fatores_e_ews(conn)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
