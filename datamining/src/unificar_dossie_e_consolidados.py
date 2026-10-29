# -*- coding: utf-8 -*-
"""
Script de Unificação Master: Consolidado Analítico CAEd & SAAP (16 Laudas) + Dossiê Mestre (1.000 Laudas)
Total da Edição Unificada: 1.016 Laudas Vetoriais A4 Estruturadas com Bookmarks Interativos
Escola de Cidadania Airam Veras • INEP 23084995 • Crateús - CE
"""

import os
import sys
import hashlib
import sqlite3
import pandas as pd
from datetime import datetime
from pypdf import PdfReader, PdfWriter

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r"c:\Users\marce\Downloads\Airam veras"
DATA_DIR = os.path.join(ROOT_DIR, "datamining", "dados")
DB_PATH = os.path.join(DATA_DIR, "airam_veras_ecossistema.sqlite")

PDF_CONSOLIDADO = os.path.join(ROOT_DIR, "CONSOLIDADO_ANALITICO_CAED_SAAP_1ANO_TURMA_E_ALUNOS.pdf")
PDF_DOSSIE_1000 = os.path.join(ROOT_DIR, "DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS_1000_LAUDAS.pdf")

PDF_UNIFICADO_OUT = os.path.join(ROOT_DIR, "DOSSIE_UNIFICADO_1ANO_MESTRE_CONSOLIDADOS_E_PRATICAS_DIARIAS.pdf")
PDF_MESTRE_FINAL = os.path.join(ROOT_DIR, "DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf")
PDF_DOCS_FINAL = os.path.join(ROOT_DIR, "docs", "DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf")

def unificar_dossie_e_consolidados():
    print("================================================================================")
    print("INICIANDO UNIFICAÇÃO OFICIAL DO DOSSIÊ E CONSOLIDADOS (1º ANO EF)")
    print("================================================================================")
    
    if not os.path.exists(PDF_CONSOLIDADO):
        raise FileNotFoundError(f"Arquivo não encontrado: {PDF_CONSOLIDADO}")
    if not os.path.exists(PDF_DOSSIE_1000):
        raise FileNotFoundError(f"Arquivo não encontrado: {PDF_DOSSIE_1000}")
        
    reader_cons = PdfReader(PDF_CONSOLIDADO)
    reader_dossie = PdfReader(PDF_DOSSIE_1000)
    
    n_cons = len(reader_cons.pages)
    n_dossie = len(reader_dossie.pages)
    total_esperado = n_cons + n_dossie
    
    print(f"-> Consolidado Analítico: {n_cons} páginas (esperado: 16)")
    print(f"-> Dossiê Mestre: {n_dossie} páginas (esperado: 1000)")
    print(f"-> Total unificado esperado: {total_esperado} páginas (1016 laudas)")
    
    if n_cons != 16:
        print(f"AVISO: Consolidado possui {n_cons} páginas (esperado 16).")
    if n_dossie != 1000:
        print(f"AVISO: Dossiê possui {n_dossie} páginas (esperado 1000).")
        
    writer = PdfWriter()
    
    # 1. Copiar páginas do Consolidado (Volume I)
    print("\n[1/3] Inserindo Volume I: Consolidado Analítico CAEd & SAAP...")
    for idx, page in enumerate(reader_cons.pages):
        writer.add_page(page)
        
    # 2. Copiar páginas do Dossiê Mestre (Volume II)
    print("[2/3] Inserindo Volume II: Dossiê Pedagógico Mestre e Cadernos Individuais...")
    for idx, page in enumerate(reader_dossie.pages):
        writer.add_page(page)
        
    print(f"-> Total de páginas no writer: {len(writer.pages)}")
    
    # 3. Adicionar Estrutura Completa de Bookmarks (Outlines)
    print("\n[3/3] Criando Árvore Hierárquica de Bookmarks (Outlines)...")
    
    # --- VOLUME I OUTLINE ---
    bm_vol1 = writer.add_outline_item("📑 VOLUME I: CONSOLIDADO ANALÍTICO CENSITÁRIO CAEd & SAAP (16 Laudas)", 0)
    writer.add_outline_item("🏛️ Lauda 01: Capa Oficial Master do Consolidado Executivo & Metadados", 0, parent=bm_vol1)
    writer.add_outline_item("📐 Lauda 02: Metodologia Psicométrica & Escalas de Avaliação Integradas", 1, parent=bm_vol1)
    writer.add_outline_item("📈 Lauda 03: Painel Longitudinal Censitário da Turma (CAEd & SAAP) [Gráfico 1]", 2, parent=bm_vol1)
    writer.add_outline_item("⚖️ Lauda 04: Análise de Equidade: Neurodivergentes (CID) vs Típicos [Gráfico 2 & Fisher]", 3, parent=bm_vol1)
    writer.add_outline_item("🎯 Lauda 05: Validade Convergente (Spearman ρ=0.742) & Radar CHC [Gráficos 3 e 6]", 4, parent=bm_vol1)
    writer.add_outline_item("📊 Lauda 06: Distribuição dos Níveis no SAAP & Matrizes de Markov [Gráficos 4 e 5]", 5, parent=bm_vol1)
    writer.add_outline_item("📋 Lauda 07: Matriz Censitária Consolidada dos Estudantes (Alunos 01 a 13)", 6, parent=bm_vol1)
    writer.add_outline_item("📋 Lauda 08: Matriz Censitária Consolidada dos Estudantes (Alunos 14 a 25)", 7, parent=bm_vol1)
    
    bm_cards = writer.add_outline_item("👤 Fichas Gráficas Individuais dos Estudantes (Alunos 01 a 25)", 8, parent=bm_vol1)
    writer.add_outline_item("Alunos 01 a 04: Antonio Calleby, Daniel Conceição, Emanuelly, Francisco Miguel", 8, parent=bm_cards)
    writer.add_outline_item("Alunos 05 a 08: Gustavo Henrique, Gustavo Sales, Isabella Martins, Isac Lucca", 9, parent=bm_cards)
    writer.add_outline_item("Alunos 09 a 12: Isis Gomes, Isis Ketlen, José Yhudy, Livya Maria", 10, parent=bm_cards)
    writer.add_outline_item("Alunos 13 a 16: Louise Alves, Lunna Silva, Maria Agatha, Maria Isis Conceição", 11, parent=bm_cards)
    writer.add_outline_item("Alunos 17 a 20: Maria Isis Pereira, Maria Juliana, Maria Leticia, Maria Sophia", 12, parent=bm_cards)
    writer.add_outline_item("Alunos 21 a 24: Maria Yorrana, Moises Toledo, Ruan Lucas, Sarah Eloyse", 13, parent=bm_cards)
    writer.add_outline_item("Aluno 25 & Metas SPAECE: Francisca Adila Caxias de Almeida", 14, parent=bm_cards)
    
    writer.add_outline_item("🛡️ Lauda 16: Governança, Controle Social e Certificação Forense [Bloco 45]", 15, parent=bm_vol1)
    
    # --- VOLUME II OUTLINE ---
    bm_vol2 = writer.add_outline_item("📑 VOLUME II: DOSSIÊ PEDAGÓGICO MESTRE & PRÁTICAS DIÁRIAS (1.000 Laudas)", 16)
    
    # Subseção 1: Front Matter Mestre (Laudas 1 a 40 do Dossiê -> Páginas 17 a 56 do Unificado)
    bm_fm = writer.add_outline_item("🏛️ Seção 1: Front Matter Mestre Multidisciplinar (40 Laudas)", 16, parent=bm_vol2)
    writer.add_outline_item("Lauda 01: Capa Oficial Master do Dossiê Mestre 1000 Laudas", 16, parent=bm_fm)
    writer.add_outline_item("Lauda 02: Ficha Catalográfica e Metadados Forenses", 17, parent=bm_fm)
    writer.add_outline_item("Laudas 03 a 07: Governança Institucional, Equipe e Matriz Curricular 35H", 18, parent=bm_fm)
    writer.add_outline_item("Laudas 08 a 25: Matrizes Curriculares dos 9 Componentes BNCC (Bimestres I a IV)", 23, parent=bm_fm)
    writer.add_outline_item("Lauda 26: Suíte de Bioestatística Multidisciplinar: ANOVA, Kruskal-Wallis e Fisher", 41, parent=bm_fm)
    writer.add_outline_item("Lauda 27: Topologia da Rede Interdisciplinar (Fluxograma 2D SVG Vetorial)", 42, parent=bm_fm)
    writer.add_outline_item("Lauda 28: Modelagem de Markov & Projeção Longitudinal de Transição de Níveis", 43, parent=bm_fm)
    writer.add_outline_item("Lauda 29: Early Warning System (EWS) & Gatilhos Preditivos de Risco Escolar", 44, parent=bm_fm)
    writer.add_outline_item("Lauda 30: Censo Coletivo dos 172 Estudantes e Diagnóstico CAEd Ciclo I", 45, parent=bm_fm)
    writer.add_outline_item("Lauda 31: Análise dos Clusters Pedagógicos do 1º Ano (1A, 1B, 1C e 1D)", 46, parent=bm_fm)
    writer.add_outline_item("Lauda 32: Matriz Diagnóstica de Habilidades CAEd (H01 a H08)", 47, parent=bm_fm)
    writer.add_outline_item("Lauda 33: Comparativo Longitudinal dos Ciclos I, II e III CAEd (1º Ano Único)", 48, parent=bm_fm)
    writer.add_outline_item("Lauda 34: Diretrizes Integradas Clusters 1A & 1B (Base Alfabética e DUA)", 49, parent=bm_fm)
    writer.add_outline_item("Lauda 35: Diretrizes Integradas Clusters 1C & 1D (Compreensão e Enriquecimento)", 50, parent=bm_fm)
    writer.add_outline_item("Lauda 36: Reavaliação Censitária Longitudinal: SAAP & Multiciclos CAEd", 51, parent=bm_fm)
    writer.add_outline_item("Lauda 37: Microdados Oficiais SAAP (23 Alunos) & Rastreamento EWS Diferenciado", 52, parent=bm_fm)
    writer.add_outline_item("Lauda 38: Guia Metodológico de Aplicação das 40 Fichas Diárias", 53, parent=bm_fm)
    writer.add_outline_item("Lauda 39: Orientações para a Família e Protocolo de Leitura Domiciliar", 54, parent=bm_fm)
    writer.add_outline_item("Lauda 40: Índice Remissivo Nominal Geral dos 24 Cadernos Estruturados", 55, parent=bm_fm)
    
    # Subseção 2: Cadernos Individuais de Práticas Diárias (24 Estudantes x 40 laudas = 960 laudas)
    bm_cad = writer.add_outline_item("📚 Seção 2: Cadernos Individuais de Práticas Diárias (24 Estudantes • 960 Laudas)", 56, parent=bm_vol2)
    
    # Mapear os 24 estudantes da coorte
    data_dir_caed = os.path.join(ROOT_DIR, "resultados-caed-ciclo-i-2026", "csv_originais")
    lp_csv = os.path.join(data_dir_caed, "1ANO_LEITURA_CICLO_I_2026", "HABILIDADES_DESEMPENHO_ESTUDANTE 22-10-2026 6-06-25.csv")
    df_lp = pd.read_csv(lp_csv, sep=';', encoding='latin-1')
    std_names = sorted(df_lp['Estudante'].unique())
    
    # Carregar CIDs e Clusters do banco de dados
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT nome_estudante, cluster_codigo, possui_laudo_cid, codigo_cid10, diagnostico_resumo
        FROM fato_consolidado_aluno_caed_saap_1ano
    """)
    db_info = {r[0]: (r[1], r[2], r[3], r[4]) for r in cur.fetchall()}
    conn.close()
    
    for idx, std_name in enumerate(std_names):
        p_unif_ini = 16 + 40 + idx * 40  # 0-indexed: 56 + idx*40
        p_num_display = p_unif_ini + 1   # 1-indexed: 57 + idx*40
        p_fim_display = p_num_display + 39
        
        c_code, has_cid, cid_cod, diag = db_info.get(std_name, ("1C", 0, None, None))
        cid_tag = f" [{cid_cod}]" if (has_cid and cid_cod) else ""
        
        label = f"Caderno {idx+1:02d}: {std_name}{cid_tag} (Cluster {c_code}) • Págs. {p_num_display:04d} a {p_fim_display:04d}"
        writer.add_outline_item(label, p_unif_ini, parent=bm_cad)
        
    # Gravar o PDF Unificado
    print(f"\nGravando arquivo unificado: {PDF_UNIFICADO_OUT}...")
    with open(PDF_UNIFICADO_OUT, 'wb') as f:
        writer.write(f)
    print("-> Gravação concluída com sucesso!")
    
    # Atualizar cópias mestras oficiais
    print(f"Atualizando cópia mestre primária: {PDF_MESTRE_FINAL}...")
    with open(PDF_MESTRE_FINAL, 'wb') as f:
        with open(PDF_UNIFICADO_OUT, 'rb') as f_src:
            f.write(f_src.read())
            
    print(f"Atualizando cópia em docs/: {PDF_DOCS_FINAL}...")
    with open(PDF_DOCS_FINAL, 'wb') as f:
        with open(PDF_UNIFICADO_OUT, 'rb') as f_src:
            f.write(f_src.read())
            
    # Calcular Hashes SHA-256
    with open(PDF_UNIFICADO_OUT, 'rb') as f:
        pdf_bytes = f.read()
        sha256_unificado = hashlib.sha256(pdf_bytes).hexdigest()
        
    tamanho_mb = len(pdf_bytes) / (1024 * 1024)
    print(f"\n================================================================================")
    print(f"RELATÓRIO DE INTEGRIDADE FORENSE & CERTIFICAÇÃO:")
    print(f"• Arquivo Unificado: {os.path.basename(PDF_UNIFICADO_OUT)}")
    print(f"• Total de Páginas: {len(writer.pages)} laudas vetoriais A4")
    print(f"• Tamanho do Arquivo: {tamanho_mb:.2f} MB")
    print(f"• Hash Criptográfico SHA-256: {sha256_unificado}")
    print(f"================================================================================")
    
    # Inserir no Ledger Transacional (Bloco 47)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Obter hash do bloco anterior
    cur.execute("SELECT sequencia_bloco, hash_bloco_atual FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 1")
    ultimo_bloco = cur.fetchone()
    seq_anterior = ultimo_bloco[0] if ultimo_bloco else 46
    hash_anterior = ultimo_bloco[1] if ultimo_bloco else "bf4ca1784fb166fcd1fbef2c752f719ee782b87840e576304d38082d518e1c59"
    
    novo_bloco = seq_anterior + 1
    timestamp_utc = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    
    # Criar hash do bloco atual do ledger
    bloco_content = f"{novo_bloco}|UNIFICACAO_DOSSIE_E_CONSOLIDADOS_1016_LAUDAS|{hash_anterior}|{sha256_unificado}|{timestamp_utc}"
    hash_bloco_atual = hashlib.sha256(bloco_content.encode('utf-8')).hexdigest()
    
    cur.execute("""
        INSERT INTO fato_auditoria_transacional_ledger (
            sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash,
            resumo_transacao, hash_bloco_anterior, hash_bloco_atual, timestamp_utc, agente_ou_processo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        novo_bloco,
        "fato_consolidado_aluno_caed_saap_1ano, fato_consolidado_turma_caed_saap_1ano, dossie_unificado_1016_laudas",
        "UNIFICACAO_DOSSIE_E_CONSOLIDADOS_1016_LAUDAS",
        f"DOSSIE_UNIFICADO_SHA256_{sha256_unificado[:16]}",
        f"Unificação oficial do Consolidado Analítico CAEd & SAAP (16 laudas) com o Dossiê Mestre de Práticas Diárias (1.000 laudas) em publicação unificada de 1.016 laudas A4 com árvore completa de bookmarks interativos.",
        hash_anterior,
        hash_bloco_atual,
        timestamp_utc,
        "MARCELO_CLARO_E_ANTIGRAVITY"
    ))
    conn.commit()
    conn.close()
    
    print(f"\n[LEDGER] Bloco {novo_bloco} registrado com sucesso no ecossistema!")
    print(f"• Hash do Bloco {novo_bloco}: {hash_bloco_atual}")
    print(f"• Timestamp UTC: {timestamp_utc}")
    print("================================================================================")
    
if __name__ == '__main__':
    unificar_dossie_e_consolidados()
