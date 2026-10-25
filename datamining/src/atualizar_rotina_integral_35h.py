"""
Script de Criação e Atualização da Rotina Semanal de Tempo Integral (INTEGRAL 35H)
Secretaria de Educação - Governo Municipal de Crateús
Escola Municipal Airam Veras 2026
"""

import sqlite3
import hashlib
import json
from datetime import datetime

DB_PATH = "datamining/dados/airam_veras_ecossistema.sqlite"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Criar a tabela dim_rotina_semanal_integral_35h
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_rotina_semanal_integral_35h (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        turma_id INTEGER NOT NULL REFERENCES dim_turmas(id),
        horario_ordem INTEGER NOT NULL,
        horario_rotulo TEXT NOT NULL,
        tipo_registro TEXT NOT NULL,
        horario_inicio TEXT NOT NULL,
        horario_fim TEXT NOT NULL,
        duracao_minutos INTEGER NOT NULL,
        segunda_disciplina TEXT NOT NULL,
        segunda_detalhe TEXT NOT NULL,
        terca_disciplina TEXT NOT NULL,
        terca_detalhe TEXT NOT NULL,
        quarta_disciplina TEXT NOT NULL,
        quarta_detalhe TEXT NOT NULL,
        quinta_disciplina TEXT NOT NULL,
        quinta_detalhe TEXT NOT NULL,
        sexta_disciplina TEXT NOT NULL,
        sexta_detalhe TEXT NOT NULL,
        regime_jornada TEXT NOT NULL DEFAULT 'INTEGRAL 35H',
        orgao_emissor TEXT NOT NULL DEFAULT 'Secretaria de Educação - Governo de Crateús',
        cor_destaque_hex TEXT NOT NULL DEFAULT '#ffffff',
        hash_linha TEXT NOT NULL
    )
    """)

    # Limpar registros anteriores se houver para idempotência
    cur.execute("DELETE FROM dim_rotina_semanal_integral_35h")

    # Atualizar dim_turmas turno para Tempo Integral (35H)
    cur.execute("UPDATE dim_turmas SET turno = 'Tempo Integral (35H)' WHERE ano_letivo = 2026")

    # 9 períodos oficiais de acordo com a Secretaria de Educação de Crateús (INTEGRAL 35H)
    periodos = [
        (
            1, "1ª Aula", "AULA", "07:00", "07:50", 50,
            "Língua Portuguesa", "Consciência Fonêmica e Princípio Alfabético (Sons Contínuos: P, M, V) • Alinhamento CAEd H01",
            "Língua Portuguesa", "Decodificação Silábica Regular (C+V) e Formação Ativa de Palavras • Alinhamento CAEd H02",
            "Língua Portuguesa", "Segmentação Fonêmica, Reconhecimento de Rimas e Aliterações • Alinhamento CAEd H03",
            "Língua Portuguesa", "Fluência Leitora Inicial: Precisão Articulatória e Automatização • Alinhamento CAEd H04",
            "Língua Portuguesa", "Diagnóstico Formativo Semanal de Fluência (WCPM) e Leitura Guiada Individualizada",
            "#ffffff"
        ),
        (
            2, "2ª Aula", "AULA", "07:50", "08:40", 50,
            "Língua Portuguesa", "Prática Diária Fônica Ficha Semanal e Caligrafia Guiada de Letras de Imprensa",
            "Língua Portuguesa", "Ortografia Regular, Ditado Fônico Ilustrado e Produção de Legendas Curtas",
            "Língua Portuguesa", "Leitura Expressiva de Textos Curtos, Cantigas e Parlendas da Tradição Oral",
            "Língua Portuguesa", "Compreensão de Narrativas Ilustradas e Localização de Informação Explícita (CAEd H05)",
            "Matemática", "Kumon Adaptado 7A: Desafio de Contagem, Reta Numérica e Fixação Lúdica",
            "#ffffff"
        ),
        (
            3, "3ª Aula", "AULA", "08:40", "09:30", 50,
            "Matemática", "Kumon 7A: Sequência Numérica, Contagem e Cardinalidade até 20 • CAEd H01",
            "Matemática", "Kumon 6A: Composição e Decomposição de Quantidades em Dezenas e Unidades • CAEd H02",
            "Matemática", "Estruturas Aditivas Concretas: Ações Básicas de Juntar e Acrescentar • CAEd H03",
            "Matemática", "Geometria Espacial: Esfera, Cubo e Cilindro no Espaço Vivencial da Escola • CAEd H04",
            "Matemática", "Medidas de Tempo: Leitura do Calendário, Dias da Semana e Sequência Diária • CAEd H05",
            "#ffffff"
        ),
        (
            4, "Lanche", "INTERVALO", "09:30", "09:50", 20,
            "Intervalo / Merenda", "Lanche Escolar Nutritivo (20 min) • Higienização Bucal & Convivência Saudável",
            "Intervalo / Merenda", "Lanche Escolar Nutritivo (20 min) • Higienização Bucal & Convivência Saudável",
            "Intervalo / Merenda", "Lanche Escolar Nutritivo (20 min) • Higienização Bucal & Convivência Saudável",
            "Intervalo / Merenda", "Lanche Escolar Nutritivo (20 min) • Higienização Bucal & Convivência Saudável",
            "Intervalo / Merenda", "Lanche Escolar Nutritivo (20 min) • Higienização Bucal & Convivência Saudável",
            "#e8eedd"
        ),
        (
            5, "4ª Aula", "AULA", "09:50", "10:40", 50,
            "Matemática", "Resolução Concreta de Situações-Problema com Material Dourado e Cuisenaire",
            "BNCC Computacional", "Algoritmos Desplugados: Sequenciamento Passo a Passo de Rotinas e Tarefas Diárias",
            "Matemática", "Kumon 6A: Fatos Básicos da Adição e Raciocínio Dedutivo Cumulativo",
            "BNCC Computacional", "Reconhecimento de Padrões Visuais e Labirintos Lógicos Desplugados no Pátio",
            "BNCC Computacional", "Decomposição de Problemas e Criação de Instruções Lógicas Estruturadas",
            "#ffffff"
        ),
        (
            6, "5ª Aula", "AULA", "10:40", "11:30", 50,
            "Ciências da Natureza", "Corpo Humano, Órgãos dos Sentidos e Hábitos Saudáveis de Higiene (EF01CI02)",
            "Ciências da Natureza", "Ciclos Temporais da Terra: Dia e Noite e Efeitos nos Seres Vivos (EF01CI05)",
            "História", "Identidade Pessoal, Nome Próprio, Memória e Vínculos Familiares (EF01HI01)",
            "Geografia", "A Moradia e seus Compartimentos: Noções de Topologia e Convivência (EF01GE01)",
            "História", "A Escola e a Comunidade: Transformações e Permanências no Tempo (EF01HI04)",
            "#ffffff"
        ),
        (
            7, "Almoço", "INTERVALO", "11:30", "13:00", 90,
            "Almoço e Repouso", "Almoço Escolar Completo • Higiene Bucal • Repouso / Atividades Lúdicas Calmas (90 min)",
            "Almoço e Repouso", "Almoço Escolar Completo • Higiene Bucal • Repouso / Atividades Lúdicas Calmas (90 min)",
            "Almoço e Repouso", "Almoço Escolar Completo • Higiene Bucal • Repouso / Atividades Lúdicas Calmas (90 min)",
            "Almoço e Repouso", "Almoço Escolar Completo • Higiene Bucal • Repouso / Atividades Lúdicas Calmas (90 min)",
            "Almoço e Repouso", "Almoço Escolar Completo • Higiene Bucal • Repouso / Atividades Lúdicas Calmas (90 min)",
            "#dcd6e8"
        ),
        (
            8, "6ª Aula", "AULA", "13:00", "13:50", 50,
            "Arte", "Artes Visuais: Ponto, Linha, Cores Primárias e Autorretrato Lúdico (EF15AR01)",
            "Geografia", "O Espaço Escolar: Croquis da Sala de Aula e Lateralidade Corporal (EF01GE09)",
            "Arte", "Música e Expressão Corporal: Sons do Corpo e Paisagem Sonora Local (EF15AR14)",
            "Ciências da Natureza", "Materiais do Cotidiano e Práticas Sustentáveis de Reciclagem (EF01CI01)",
            "Educação Física", "Jogos Cooperativos, Coordenação Motora Fina/Ampla e Socialização",
            "#ffffff"
        ),
        (
            9, "7ª Aula", "AULA", "13:50", "14:40", 50,
            "Educação Física", "Esquema Corporal, Equilíbrio Vestibular e Regulação Sensorial DUA",
            "Ensino Religioso", "Círculo de Empatia, Alteridade e Validação Socioemocional PBS (EF01ER01)",
            "Educação Física", "Brincadeiras Tradicionais da Cultura Cearense e Cirandas de Roda",
            "Laboratório de Recomposição", "Prática Interdisciplinar DUA & Atendimento SRM/AEE Modular Especializado",
            "Círculo Formativo Semanal", "Assembleia de Turma, Autoavaliação de Metas & Portfólio de Evidências",
            "#ffffff"
        )
    ]

    for p in periodos:
        raw = f"{p[0]}|{p[1]}|{p[2]}|{p[3]}|{p[4]}|{p[5]}|{p[6]}|{p[8]}|{p[10]}|{p[12]}|{p[14]}"
        h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
        cur.execute("""
        INSERT INTO dim_rotina_semanal_integral_35h (
            turma_id, horario_ordem, horario_rotulo, tipo_registro,
            horario_inicio, horario_fim, duracao_minutos,
            segunda_disciplina, segunda_detalhe,
            terca_disciplina, terca_detalhe,
            quarta_disciplina, quarta_detalhe,
            quinta_disciplina, quinta_detalhe,
            sexta_disciplina, sexta_detalhe,
            regime_jornada, orgao_emissor, cor_destaque_hex, hash_linha
        ) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'INTEGRAL 35H', 'Secretaria de Educação - Governo de Crateús', ?, ?)
        """, (
            p[0], p[1], p[2], p[3], p[4], p[5],
            p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14], p[15],
            p[16], h
        ))

    # Verificar foreign keys
    cur.execute("PRAGMA foreign_key_check")
    fk_errors = cur.fetchall()
    assert len(fk_errors) == 0, f"Erros de FK detectados: {fk_errors}"

    # Registrar Bloco 17 no Ledger
    now_iso = datetime.now().isoformat()
    cur.execute("SELECT hash_bloco_atual FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 1")
    last_block = cur.fetchone()
    prev_hash = last_block[0] if last_block else "0" * 64

    bloco_17_raw = f"17|{prev_hash}|dim_rotina_semanal_integral_35h|INSERT_9_PERIODOS_INTEGRAL_35H_CRATEUS|{now_iso}"
    bloco_17_hash = hashlib.sha256(bloco_17_raw.encode("utf-8")).hexdigest()

    cur.execute("""
    INSERT INTO fato_auditoria_transacional_ledger (
        sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash,
        resumo_transacao, hash_bloco_anterior, hash_bloco_atual, timestamp_utc, agente_ou_processo
    ) VALUES (
        17, 'dim_rotina_semanal_integral_35h', 'SCHEMA_EXPANSION_AND_INSERT', 'dim_rotina_semanal_integral_35h:1..9',
        'Homologacao da Matriz e Rotina Semanal Oficial INTEGRAL 35H da Secretaria de Educacao de Crateus',
        ?, ?, ?, 'OpenCode Orchestrator & SME Crateus'
    )
    """, (prev_hash, bloco_17_hash, now_iso))

    cur.execute("""
    INSERT INTO sys_trilha_auditoria (
        timestamp_utc, operacao, tabela_afetada, id_registro_afetado,
        agente_executor, detalhes_operacao, sha256_estado_apos
    ) VALUES (
        ?, 'INSERT', 'dim_rotina_semanal_integral_35h', '1..9',
        'Antigravity Orchestrator', 'Criação e homologação dos 9 períodos oficiais de Tempo Integral (35H) de Crateús',
        ?
    )
    """, (now_iso, bloco_17_hash))

    conn.commit()

    # Contagem final de tabelas
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    total_tables = cur.fetchone()[0]

    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='view'")
    total_views = cur.fetchone()[0]

    print(f"Sucesso! Tabelas: {total_tables}, Views: {total_views}")
    print(f"Bloco 17 registrado no Ledger com hash: {bloco_17_hash}")

    conn.close()

if __name__ == "__main__":
    main()
