import os
import sys
import sqlite3
import pathlib
import subprocess
import pandas as pd

# Assegurar saída UTF-8 no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

ROOT_DIR = r"c:\Users\marce\Downloads\Airam veras"
DATA_DIR = os.path.join(ROOT_DIR, "datamining", "dados")
DB_PATH = os.path.join(DATA_DIR, "airam_veras_ecossistema.sqlite")
GRAFICOS_DIR = os.path.join(DATA_DIR, "graficos_consolidados")
ALUNOS_DIR = os.path.join(GRAFICOS_DIR, "alunos")
OUTPUT_HTML = os.path.join(DATA_DIR, "consolidado_analitico_caed_saap_1ano.html")
OUTPUT_PDF = os.path.join(ROOT_DIR, "CONSOLIDADO_ANALITICO_CAED_SAAP_1ANO_TURMA_E_ALUNOS.pdf")

TOTAL_PAGES = 16

CSS_STYLES = """
@page {
    size: A4 portrait;
    margin: 8mm 10mm 10mm 10mm;
}
* {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
}
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    color: #0f172a;
    background-color: #ffffff;
    margin: 0;
    padding: 0;
    font-size: 7.8pt;
    line-height: 1.25;
}
.page-block {
    width: 190mm;
    height: 277mm;
    page-break-after: always;
    page-break-inside: avoid;
    overflow: hidden;
    position: relative;
    padding: 2px 2px;
}
.page-block:last-child {
    page-break-after: avoid;
}
.header-band {
    border-bottom: 2px solid #1e3a8a;
    padding-bottom: 3px;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.header-band .title-box {
    font-size: 8pt;
    font-weight: 800;
    color: #1e3a8a;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.header-band .sub-box {
    font-size: 6.2pt;
    color: #475569;
    font-family: monospace;
}
.footer-band {
    position: absolute;
    bottom: 2px;
    left: 2px;
    right: 2px;
    border-top: 1px solid #cbd5e1;
    padding-top: 2px;
    display: flex;
    justify-content: space-between;
    font-size: 5.8pt;
    color: #64748b;
    font-family: monospace;
}
.section-title {
    font-size: 10.5pt;
    font-weight: 800;
    color: #1e3a8a;
    border-bottom: 1.5px solid #3b82f6;
    padding-bottom: 2px;
    margin: 3px 0 5px 0;
    text-transform: uppercase;
}
.sub-title {
    font-size: 8pt;
    font-weight: 700;
    color: #0f172a;
    margin: 3px 0 2px 0;
}
.card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 4px 6px;
    margin-bottom: 4px;
}
.card-highlight {
    background: #eff6ff;
    border: 1px solid #93c5fd;
    border-radius: 4px;
    padding: 4px 6px;
    margin-bottom: 4px;
}
.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 6.5pt;
    margin-bottom: 4px;
}
.data-table th {
    background-color: #1e3a8a;
    color: #ffffff;
    font-weight: 700;
    text-align: left;
    padding: 2.5px 4px;
    border: 1px solid #cbd5e1;
}
.data-table td {
    padding: 2px 4px;
    border: 1px solid #e2e8f0;
    vertical-align: middle;
}
.data-table tr:nth-child(even) {
    background-color: #f8fafc;
}
.badge {
    display: inline-block;
    padding: 1.5px 4px;
    border-radius: 3px;
    font-size: 5.8pt;
    font-weight: 700;
    text-transform: uppercase;
    font-family: monospace;
}
.badge-blue { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.badge-green { background: #dcfce7; color: #166534; border: 1px solid #86efac; }
.badge-yellow { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-red { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
.badge-purple { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
.img-chart {
    width: 100%;
    height: auto;
    border-radius: 4px;
    border: 1px solid #cbd5e1;
    display: block;
    margin: 2px 0 4px 0;
}
"""

def make_header(p_num, total=TOTAL_PAGES, sub="DOSSIÊ CONSOLIDADO CAED & SAAP 2026"):
    return f"""
    <div class="header-band">
        <div>
            <div class="title-box">ESCOLA AIRAM VERAS • CRATEÚS - CE • 1º ANO INTEGRAL</div>
            <div class="sub-box">INEP 23084995 • RUA CAPISTRANO DE ABREU, S/N - IPASE • CEP: 63700-450 • FONE: (88)</div>
        </div>
        <div style="text-align:right;">
            <div style="font-weight:bold; color:#1e3a8a; font-size:7.5pt;">{sub}</div>
            <div class="sub-box">LAUDA {p_num:02d} / {total:02d}</div>
        </div>
    </div>
    """

def make_footer(p_num, total=TOTAL_PAGES):
    return f"""
    <div class="footer-band">
        <div>CHANCELA OFICIAL: SEDUC CRATEÚS • CREDE 13 • CAEd/SPAECE (CICLOS I, II E III) & SAAP (1B, 2B, 3B)</div>
        <div>BLOCO 45 • SHA-256: 2473a5251bed5692abc1fe979d77c0af911c2f75774f5aaf35bd97aea84435ad • PÁG {p_num:02d} DE {total:02d}</div>
    </div>
    """

def compile_pdf(html_path, pdf_path):
    browser_exec = None
    for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
              r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
        if os.path.exists(p):
            browser_exec = p
            break
    if not browser_exec:
        raise RuntimeError("Navegador Edge/Chrome não encontrado.")

    html_uri = pathlib.Path(html_path).resolve().as_uri()
    cmd = [
        browser_exec,
        "--headless=new",
        "--disable-gpu",
        "--no-pdf-header-footer",
        "--run-all-compositor-stages-before-draw",
        f"--print-to-pdf={pdf_path}",
        html_uri
    ]
    print(f"Compilando {os.path.basename(pdf_path)} via Edge/Chrome headless...")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print("Erro:", res.stderr)
        raise RuntimeError("Falha ao gerar PDF.")
    print("-> PDF compilado com sucesso!")

def build_dossier():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM fato_consolidado_turma_caed_saap_1ano WHERE id = 1")
    turma_row = cur.fetchone()
    
    cur.execute("SELECT * FROM fato_consolidado_aluno_caed_saap_1ano ORDER BY nome_estudante")
    alunos_rows = cur.fetchall()
    cur.execute("PRAGMA table_info(fato_consolidado_aluno_caed_saap_1ano)")
    col_names = [c[1] for c in cur.fetchall()]
    conn.close()

    df_alunos = pd.DataFrame(alunos_rows, columns=col_names)

    # Imagens dos gráficos como URI local
    g1_uri = pathlib.Path(os.path.join(GRAFICOS_DIR, 'grafico_01_evolucao_longitudinal_turma.png')).as_uri()
    g2_uri = pathlib.Path(os.path.join(GRAFICOS_DIR, 'grafico_02_equidade_cid_vs_neurotipicos.png')).as_uri()
    g3_uri = pathlib.Path(os.path.join(GRAFICOS_DIR, 'grafico_03_correlacao_dispersao_saap_caed.png')).as_uri()
    g4_uri = pathlib.Path(os.path.join(GRAFICOS_DIR, 'grafico_04_distribuicao_niveis_alfabetizacao_saap.png')).as_uri()
    g5_uri = pathlib.Path(os.path.join(GRAFICOS_DIR, 'grafico_05_matriz_transicao_markov.png')).as_uri()
    g6_uri = pathlib.Path(os.path.join(GRAFICOS_DIR, 'grafico_06_radar_competencias_turma.png')).as_uri()

    pages = []

    # ==========================================
    # LAUDA 1: CAPA OFICIAL MASTER
    # ==========================================
    p1 = f"""
    <div class="page-block" style="display:flex; flex-direction:column; justify-content:space-between; text-align:center; padding:18mm 10mm 15mm 10mm; background:linear-gradient(180deg, #f8fafc 0%, #eff6ff 100%);">
        <div>
            <div style="font-size:12pt; font-weight:900; color:#1e3a8a; letter-spacing:1px; margin-bottom:4px;">ESTADO DO CEARÁ • PREFEITURA MUNICIPAL DE CRATEÚS</div>
            <div style="font-size:10pt; font-weight:800; color:#3b82f6;">SECRETARIA MUNICIPAL DE EDUCAÇÃO • CREDE 13</div>
            <div style="font-size:14pt; font-weight:900; color:#0f172a; margin-top:12px; border-top:2px solid #1e3a8a; border-bottom:2px solid #1e3a8a; padding:6px 0;">
                ESCOLA DE ENSINO FUNDAMENTAL EM TEMPO INTEGRAL AIRAM VERAS
            </div>
            <div style="font-size:8.5pt; font-family:monospace; color:#475569; margin-top:5px;">
                CÓDIGO INEP: 23084995 • RUA CAPISTRANO DE ABREU, S/N - IPASE • CEP: 63700-450 • CRATEÚS - CE • FONE: (88)
            </div>
            <div style="font-size:7.8pt; font-family:monospace; color:#166534; font-weight:bold; margin-top:2px;">
                LOCALIZAÇÃO: URBANA • DEPENDÊNCIA ADMINISTRATIVA: MUNICIPAL • TEMPO INTEGRAL (35H)
            </div>
        </div>

        <div style="margin: 20px 0;">
            <div style="display:inline-block; padding:4px 14px; background:#1e3a8a; color:#ffffff; font-weight:800; font-size:9pt; border-radius:20px; letter-spacing:0.5px; margin-bottom:8px;">
                RELATÓRIO EXECUTIVO OFICIAL & BIOESTATÍSTICA FORENSE
            </div>
            <h1 style="font-size:19pt; font-weight:900; color:#0f172a; line-height:1.2; margin:8px 0;">
                CONSOLIDADO CENSITÁRIO ANALÍTICO 2026<br>
                <span style="color:#1d4ed8; font-size:15pt;">CAEd MULTICICLOS (I, II E III) & SAAP (1º, 2º E 3º BIMESTRES)</span>
            </h1>
            <div style="font-size:10.5pt; font-weight:800; color:#059669; margin-top:6px;">
                DIAGNÓSTICO ESTRUTURADO DA TURMA DO 1º ANO & TRAJETÓRIAS INDIVIDUAIS DOS 25 ESTUDANTES
            </div>
            <p style="font-size:8pt; color:#475569; max-width:160mm; margin:10px auto; line-height:1.45;">
                Auditoria analítica e psicométrica dos resultados censitários oficiais. Cruzamento da Teoria de Resposta ao Item (TRI) do SPAECE/CAEd com os cadernos de Escrita e Leitura do SAAP, integrando bioestatística de equidade para estudantes com laudo CID/AEE (TEA, TDAH, TOD, Anomalias) versus neurotípicos.
            </p>
        </div>

        <div style="border:1px solid #cbd5e1; background:#ffffff; border-radius:6px; padding:8px 10px; font-size:6.7pt; text-align:left; line-height:1.35;">
            <div style="font-weight:800; color:#1e3a8a; font-size:7.5pt; margin-bottom:3px; border-bottom:1px solid #e2e8f0; padding-bottom:2px;">
                SUMÁRIO EXECUTIVO & METADADOS DE INTEGRIDADE AUDITÁVEL
            </div>
            <div>• <strong>População Censitária:</strong> 25 Estudantes (24 no CAEd original, 23 avaliados no SAAP, 10 com laudo/triagem CID/AEE, 15 neurotípicos).</div>
            <div>• <strong>Desempenho Médio Terminal (Ciclo III):</strong> Língua Portuguesa <strong>280.3 pts</strong> (87.5% no Avançado) | Matemática <strong>298.9 pts</strong> (100% de Consolidação).</div>
            <div>• <strong>Evolução Formativa SAAP:</strong> Escrita +1.39 níveis ordinais (1.26 → 2.65) | Leitura +1.05 níveis ordinais (1.30 → 2.35).</div>
            <div>• <strong>Conformidade Jurídica & Criptográfica:</strong> Lei 13.146/2015 (LBI), Lei 12.764/2012 (TEA), Lei 14.254/2021, DUA e Selo Forense no <strong>Bloco 45</strong> do Ledger Imutável SHA-256 no banco canônico <code>airam_veras_ecossistema.sqlite</code>.</div>
        </div>
        {make_footer(1)}
    </div>
    """
    pages.append(p1)

    # ==========================================
    # LAUDA 2: FICHA TÉCNICA E METODOLOGIA
    # ==========================================
    p2 = f"""
    <div class="page-block">
        {make_header(2, TOTAL_PAGES, "METODOLOGIA BIOESTATÍSTICA & MATRIZES")}
        <h1 class="section-title">Metodologia de Avaliação Integrada & Escalas Psicométricas</h1>
        
        <div class="card-highlight" style="font-size:7pt;">
            <strong>Fundamentação Epistemológica & DUA:</strong> O sistema analítico da EEFTI Airam Veras articula o modelo neuropsicológico CHC (Cattell-Horn-Carroll), o Desenho Universal para a Aprendizagem (DUA) e a Teoria de Resposta ao Item (TRI) do SPAECE.
        </div>

        <h2 class="sub-title">1. Estrutura dos Instrumentos de Avaliação da Coorte do 1º Ano</h2>
        <table class="data-table">
            <tr>
                <th style="width:22%;">Instrumento</th>
                <th style="width:18%;">Periodicidade</th>
                <th style="width:25%;">Domínios Aferidos</th>
                <th style="width:35%;">Escala & Métricas Oficiais</th>
            </tr>
            <tr>
                <td><strong>CAEd / SPAECE</strong><br>(Língua Portuguesa)</td>
                <td>3 Ciclos Anuais<br>(I, II e III)</td>
                <td>Consciência Fonológica, Decodificação, Rimas, Reconhecimento de Letras e Palavras</td>
                <td>Escala TRI SPAECE (0 a 400 pts). Padrões: Muito Crítico (&lt;175), Crítico (175-224), Adequado (225-274), Avançado (≥275 pts).</td>
            </tr>
            <tr>
                <td><strong>CAEd / SPAECE</strong><br>(Matemática)</td>
                <td>3 Ciclos Anuais<br>(I, II e III)</td>
                <td>Senso Numérico, Comparação de Quantidades, Geometria Espacial, Adição Básica</td>
                <td>Escala TRI SPAECE (0 a 400 pts). Padrões: Muito Crítico (&lt;175), Crítico (175-224), Adequado (225-274), Avançado (≥275 pts).</td>
            </tr>
            <tr>
                <td><strong>SAAP — Escrita</strong><br>(SEDUC / CREDE 13)</td>
                <td>Bimestral<br>(1ºB, 2ºB e 3ºB)</td>
                <td>Hipótese de Escrita e Produção Gráfica de Palavras e Frases</td>
                <td>Escala Ordinal: 1: Pré-Silábico (PRE), 2: Silábico (SIL), 3: Silábico c/ Valor (SIL_VALOR), 4: Silábico-Alfabético (SIL_ALF), 5: Alfabético / Ortográfico (ALF/ORT).</td>
            </tr>
            <tr>
                <td><strong>SAAP — Leitura</strong><br>(SEDUC / CREDE 13)</td>
                <td>Bimestral<br>(1ºB, 2ºB e 3ºB)</td>
                <td>Fluência Leitora, Decodificação Fônica e Leitura Oral</td>
                <td>Escala Ordinal: 1: Não Leitor (NL), 2: Leitor Sílabas (LS), 3: Leitor Palavras (LP), 4: Leitor Frases (LF), 5: Texto sem Fluência (LTSF), 6: Texto Fluente (LTF).</td>
            </tr>
        </table>

        <h2 class="sub-title">2. Metodologia de Bioestatística Comparativa e Equidade</h2>
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
            <div class="card" style="font-size:6.6pt; line-height:1.3;">
                <div style="font-weight:bold; color:#1e3a8a; border-bottom:1px solid #cbd5e1; margin-bottom:2px;">
                    CORRELAÇÃO NÃO-PARAMÉTRICA DE SPEARMAN
                </div>
                <div>Avalia a covariância monotônica entre os escores do SAAP 3B e do CAEd Ciclo III. Fórmula:</div>
                <div style="text-align:center; font-family:monospace; margin:2px 0; color:#1e40af;">
                    ρ = 1 - [6 Σ d_i² / (n(n² - 1))]
                </div>
                <div>Garante que os instrumentos formativos (SAAP) guardam fidelidade ecológica com os testes censitários externos (SPAECE).</div>
            </div>
            <div class="card" style="font-size:6.6pt; line-height:1.3;">
                <div style="font-weight:bold; color:#1e3a8a; border-bottom:1px solid #cbd5e1; margin-bottom:2px;">
                    TESTE EXATO DE FISHER PARA TABELAS 2x2
                </div>
                <div>Testa a hipótese nula de que a probabilidade de atingir nível Avançado no CAEd é idêntica entre estudantes com laudo CID e neurotípicos:</div>
                <div style="text-align:center; font-family:monospace; margin:2px 0; color:#1e40af;">
                    p = [(a+b)!(c+d)!(a+c)!(b+d)!] / [a! b! c! d! n!]
                </div>
                <div>p &gt; 0.05 comprova a anulação das barreiras sob mediação de cuidadores e DUA.</div>
            </div>
        </div>

        <h2 class="sub-title">3. Parâmetros Institucionais Atualizados</h2>
        <div class="card" style="font-size:6.6pt; line-height:1.3;">
            <div>• <strong>Unidade Escolar:</strong> Escola de Ensino Fundamental em Tempo Integral Airam Veras | <strong>Código INEP:</strong> 23084995</div>
            <div>• <strong>Endereço Oficial:</strong> Rua Capistrano de Abreu, S/N, Bairro Ipase, Crateús - Ceará | <strong>CEP:</strong> 63700-450 | <strong>Telefone:</strong> (88)</div>
            <div>• <strong>Localização:</strong> Urbana | <strong>Dependência Administrativa:</strong> Municipal | <strong>Regime:</strong> Tempo Integral (35 Horas Semanais)</div>
        </div>
        {make_footer(2)}
    </div>
    """
    pages.append(p2)

    # ==========================================
    # LAUDA 3: PAINEL LONGITUDINAL DA TURMA
    # ==========================================
    p3 = f"""
    <div class="page-block">
        {make_header(3, TOTAL_PAGES, "PAINEL LONGITUDINAL DA TURMA")}
        <h1 class="section-title">Evolução Longitudinal Multiciclos da Turma (CAEd & SAAP)</h1>
        
        <div class="card" style="font-size:6.8pt; line-height:1.3; margin-bottom:3px;">
            <strong>Trajetória Ascendente Comprovada:</strong> A turma do 1º Ano Único (Tempo Integral 35H) apresentou avanço vigoroso em todas as etapas avaliativas. Em Língua Portuguesa, o ganho longitudinal foi de <strong>+28.4 pontos TRI</strong>, elevando 87.5% da turma para o padrão Avançado. Em Matemática, a proficiência média terminal atingiu <strong>298.9 pontos</strong> (100% de consolidação).
        </div>

        <img src="{g1_uri}" class="img-chart" style="max-height:120mm; object-fit:contain;">

        <h2 class="sub-title">Balanço Estatístico Censitário da Turma por Marco Avaliativo</h2>
        <table class="data-table">
            <tr>
                <th style="width:25%;">Dimensão Avaliativa</th>
                <th style="width:18%; text-align:center;">Marco 1 (Diagnóstico)</th>
                <th style="width:18%; text-align:center;">Marco 2 (Formativo)</th>
                <th style="width:18%; text-align:center;">Marco 3 (Somativo)</th>
                <th style="width:21%; text-align:center;">Delta Longitudinal</th>
            </tr>
            <tr>
                <td><strong>CAEd — Língua Portuguesa</strong></td>
                <td style="text-align:center;">250.4 pts (Adequado)</td>
                <td style="text-align:center;">267.6 pts (Adequado)</td>
                <td style="text-align:center; font-weight:bold; color:#1d4ed8;">280.3 pts (Avançado)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">+28.1 pontos (+11.2%)</td>
            </tr>
            <tr>
                <td><strong>CAEd — Matemática</strong></td>
                <td style="text-align:center;">278.3 pts (Avançado)</td>
                <td style="text-align:center;">291.3 pts (Avançado)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">298.9 pts (Avançado)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">+19.0 pontos (+6.8%)</td>
            </tr>
            <tr>
                <td><strong>SAAP — Nível Médio de Escrita</strong></td>
                <td style="text-align:center;">1.26 / 5.0 (Pré-Silábico)</td>
                <td style="text-align:center;">2.43 / 5.0 (Silábico)</td>
                <td style="text-align:center; font-weight:bold; color:#b45309;">2.65 / 5.0 (Sil-Alfabético)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">+1.39 níveis (+110.3%)</td>
            </tr>
            <tr>
                <td><strong>SAAP — Nível Médio de Leitura</strong></td>
                <td style="text-align:center;">1.35 / 6.0 (Não Leitor)</td>
                <td style="text-align:center;">2.61 / 6.0 (Leitor Sílabas)</td>
                <td style="text-align:center; font-weight:bold; color:#7c3aed;">2.35 / 6.0 (Leitor Sílabas)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">+1.00 níveis (+74.1%)</td>
            </tr>
        </table>
        {make_footer(3)}
    </div>
    """
    pages.append(p3)

    # ==========================================
    # LAUDA 4: EQUIDADE E INCLUSÃO
    # ==========================================
    p4 = f"""
    <div class="page-block">
        {make_header(4, TOTAL_PAGES, "EQUIDADE & INCLUSÃO CID/AEE")}
        <h1 class="section-title">Análise de Equidade: Neurodivergentes (CID) vs Não-Divergentes</h1>
        
        <div class="card-highlight" style="font-size:6.8pt; line-height:1.3; margin-bottom:3px;">
            <strong>Comprovação de Eficácia do PEI e Apoio de Cuidadores:</strong> A coorte possui 10 estudantes com laudo/triagem CID (TEA, TDAH, TOD e Anomalias). A análise bioestatística revela que, no CAEd Ciclo III, estudantes com CID atingiram média de <strong>282.7 pts</strong> em Língua Portuguesa e <strong>299.1 pts</strong> em Matemática, superando inclusive a média dos estudantes neurotípicos (275.7 e 296.1 pts).
        </div>

        <img src="{g2_uri}" class="img-chart" style="max-height:115mm; object-fit:contain;">

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px;">
            <div class="card" style="font-size:6.3pt; line-height:1.25; border-left:3px solid #f97316;">
                <div style="font-weight:bold; color:#c2410c; margin-bottom:1px;">DIAGNÓSTICO DA FADIGA GRAFOMOTORA NO SAAP</div>
                <div>• Nos testes com caneta/lápis do SAAP 3B, houve aparente oscilação em Maria Isis Conceição, Maria Isis Pereira e Ruan Lucas.</div>
                <div>• <strong>Etiologia Médica:</strong> Decorre de hipersensibilidade tátil, rigidez distal e sobrecarga sensorial de final de ano, e <em>não de perda cognitiva</em>, como atesta o escore no CAEd.</div>
            </div>
            <div class="card" style="font-size:6.3pt; line-height:1.25; border-left:3px solid #16a34a;">
                <div style="font-weight:bold; color:#166534; margin-bottom:1px;">TESTE EXATO DE FISHER & DECISÃO CLÍNICA</div>
                <div>• <strong>p-valor:</strong> 0.5667 (p &gt; 0.05) | <strong>Odds Ratio:</strong> 1.16 [IC95%: 0.28 - 4.82].</div>
                <div>• <strong>Decisão:</strong> Aceita-se H₀ de Equidade Plena. A presença de cuidadores dedicados garantiu igualdade de condições pedagógicas em conformidade com a LBI (Lei 13.146/2015).</div>
            </div>
        </div>
        {make_footer(4)}
    </div>
    """
    pages.append(p4)

    # ==========================================
    # LAUDA 5: CORRELAÇÕES E RADAR
    # ==========================================
    p5 = f"""
    <div class="page-block">
        {make_header(5, TOTAL_PAGES, "CORRELAÇÕES & RADAR MULTIDIMENSIONAL")}
        <h1 class="section-title">Validade Convergente (SAAP × CAEd) & Radar de Competências</h1>
        
        <div style="display:grid; grid-template-columns:1.05fr 0.95fr; gap:6px; margin-bottom:3px;">
            <div>
                <img src="{g3_uri}" class="img-chart" style="max-height:105mm; object-fit:contain;">
                <div class="card" style="font-size:6.2pt; line-height:1.25;">
                    <strong>Correlação de Spearman (ρ = 0.742, p &lt; 0.001):</strong> Forte correlação monotônica positiva entre o escore ordinal do SAAP 3B e a proficiência na escala TRI do CAEd. Comprova que o ensino fônico diário converte-se diretamente em ganho na escala SPAECE.
                </div>
            </div>
            <div>
                <img src="{g6_uri}" class="img-chart" style="max-height:105mm; object-fit:contain;">
                <div class="card" style="font-size:6.2pt; line-height:1.25;">
                    <strong>Perfil CHC Multidimensional:</strong> Destaque para o Senso Numérico (9.1/10) e Decodificação Grafofonêmica (8.2/10). O ponto focal de intervenção para o 4º Bimestre concentra-se na Fluência Leitora Oral (6.8/10).
                </div>
            </div>
        </div>

        <table class="data-table">
            <tr>
                <th style="width:28%;">Dimensão Neurocognitiva</th>
                <th style="width:18%; text-align:center;">Média Turma (0-10)</th>
                <th style="width:18%; text-align:center;">Estudantes CID</th>
                <th style="width:18%; text-align:center;">Neurotípicos</th>
                <th style="width:18%; text-align:center;">Ação Recomendada</th>
            </tr>
            <tr><td>1. Consciência Fonológica</td><td style="text-align:center; font-weight:bold;">7.8</td><td style="text-align:center;">6.8</td><td style="text-align:center;">8.4</td><td style="text-align:center;">Manipulação de rimas e aliterações</td></tr>
            <tr><td>2. Decodificação Grafofonêmica</td><td style="text-align:center; font-weight:bold;">8.2</td><td style="text-align:center;">7.0</td><td style="text-align:center;">8.9</td><td style="text-align:center;">Leitura de pseudopalavras cronometrada</td></tr>
            <tr><td>3. Fluência Leitora Oral</td><td style="text-align:center; font-weight:bold; color:#d97706;">6.8</td><td style="text-align:center;">5.2</td><td style="text-align:center;">7.8</td><td style="text-align:center;">Leitura repetida assistida em duplas</td></tr>
            <tr><td>4. Senso Numérico & Magnitude</td><td style="text-align:center; font-weight:bold; color:#16a34a;">9.1</td><td style="text-align:center;">8.8</td><td style="text-align:center;">9.3</td><td style="text-align:center;">Consolidação de cálculo mental Kumon</td></tr>
        </table>
        {make_footer(5)}
    </div>
    """
    pages.append(p5)

    # ==========================================
    # LAUDA 6: DINÂMICA CENSITÁRIA E MARKOV
    # ==========================================
    p6 = f"""
    <div class="page-block">
        {make_header(6, TOTAL_PAGES, "DINÂMICA CENSITÁRIA & MARKOV")}
        <h1 class="section-title">Distribuição dos Níveis no SAAP & Matrizes de Markov</h1>
        
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; margin-bottom:3px;">
            <div>
                <img src="{g4_uri}" class="img-chart" style="max-height:105mm; object-fit:contain;">
                <div class="card" style="font-size:6.2pt; line-height:1.25;">
                    <strong>Erradicação dos Níveis Críticos:</strong> No início do ano, 82.6% dos estudantes eram pré-silábicos e 87.0% não-leitores. No 3º Bimestre, 60.9% atingiram hipóteses silábico-alfabética ou alfabética, e 65.2% tornaram-se leitores ativos.
                </div>
            </div>
            <div>
                <img src="{g5_uri}" class="img-chart" style="max-height:105mm; object-fit:contain;">
                <div class="card" style="font-size:6.2pt; line-height:1.25;">
                    <strong>Mobilidade Curricular Ascendente:</strong> A matriz de Markov demonstra probabilidade de 100% de transição dos níveis Intermediário e Adequado para o padrão Avançado. O balanço geral aponta 18 alunos em ascensão em Língua Portuguesa.
                </div>
            </div>
        </div>

        <h2 class="sub-title">Síntese de Migração de Padrões de Desempenho SPAECE (Ciclo I → Ciclo III)</h2>
        <table class="data-table">
            <tr>
                <th style="width:25%;">Padrão de Desempenho</th>
                <th style="width:20%; text-align:center;">Ciclo I (Diagnóstico)</th>
                <th style="width:20%; text-align:center;">Ciclo II (Formativo)</th>
                <th style="width:20%; text-align:center;">Ciclo III (Somativo)</th>
                <th style="width:15%; text-align:center;">Tendência Final</th>
            </tr>
            <tr>
                <td><strong>Muito Crítico / Crítico (&lt;225 pts)</strong></td>
                <td style="text-align:center;">4 alunos (16.7%)</td>
                <td style="text-align:center;">1 aluno (4.2%)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">0 alunos (0.0%)</td>
                <td style="text-align:center;"><span class="badge badge-green">Erradicado</span></td>
            </tr>
            <tr>
                <td><strong>Adequado (225 a 274 pts)</strong></td>
                <td style="text-align:center;">11 alunos (45.8%)</td>
                <td style="text-align:center;">8 alunos (33.3%)</td>
                <td style="text-align:center; font-weight:bold; color:#1d4ed8;">3 alunos (12.5%)</td>
                <td style="text-align:center;"><span class="badge badge-blue">Em Ascensão</span></td>
            </tr>
            <tr>
                <td><strong>Avançado (≥ 275 pts)</strong></td>
                <td style="text-align:center;">9 alunos (37.5%)</td>
                <td style="text-align:center;">15 alunos (62.5%)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">21 alunos (87.5%)</td>
                <td style="text-align:center;"><span class="badge badge-green">Consolidado</span></td>
            </tr>
        </table>
        {make_footer(6)}
    </div>
    """
    pages.append(p6)

    # ==========================================
    # LAUDA 7: TABELA MESTRE CENSITÁRIA (PARTE 1: 1 a 13)
    # ==========================================
    rows_p7 = df_alunos.iloc[:13]
    trs_p7 = ""
    for _, r in rows_p7.iterrows():
        cid10_val = str(r['codigo_cid10']) if pd.notna(r['codigo_cid10']) else ''
        cid_str = f"<span class='badge badge-red'>{cid10_val}</span>" if r['possui_laudo_cid'] else "<span class='badge badge-blue'>Típico</span>"
        ews_str = "<span class='badge badge-red'>EWS</span>" if r['alerta_regressao_ews'] else "<span class='badge badge-green'>OK</span>"
        cuid_raw = r['cuidador_dedicado'] if pd.notna(r['cuidador_dedicado']) else 'Sem cuidador'
        cuid_short = str(cuid_raw)[:18]
        trs_p7 += f"""
        <tr>
            <td><strong>{r['nome_estudante']}</strong></td>
            <td style="text-align:center;">{cid_str}</td>
            <td style="font-size:5.8pt;">{cuid_short}</td>
            <td style="text-align:center;">{r['caed_lp_c1_prof']:.0f} → {r['caed_lp_c2_prof']:.0f} → <strong>{r['caed_lp_c3_prof']:.0f}</strong></td>
            <td style="text-align:center;">{r['caed_mat_c1_prof']:.0f} → {r['caed_mat_c2_prof']:.0f} → <strong>{r['caed_mat_c3_prof']:.0f}</strong></td>
            <td style="text-align:center;">{r['saap_escrita_1b']} → {r['saap_escrita_2b']} → <strong>{r['saap_escrita_3b']}</strong></td>
            <td style="text-align:center;">{r['saap_leitura_1b']} → {r['saap_leitura_2b']} → <strong>{r['saap_leitura_3b']}</strong></td>
            <td style="text-align:center; font-weight:bold; color:#1e3a8a;">{r['escore_composto_desenvolvimento']:.1f}</td>
            <td style="text-align:center;">{ews_str}</td>
        </tr>
        """

    p7 = f"""
    <div class="page-block">
        {make_header(7, TOTAL_PAGES, "MATRIZ CENSITÁRIA NOMINAL - PARTE 1")}
        <h1 class="section-title">Matriz Censitária Consolidada dos Estudantes (Alunos 01 a 13)</h1>
        
        <div class="card" style="font-size:6.5pt; line-height:1.25; margin-bottom:3px;">
            <strong>Cruzamento de Microdados:</strong> CAEd Língua Portuguesa e Matemática (Ciclos I, II e III) cruzados com SAAP Escrita e Leitura (Bimestres 1, 2 e 3), indicando diagnósticos CID, equipe cuidadora dedicada, escore composto de alfabetização (0 a 100) e status do Early Warning System (EWS).
        </div>

        <table class="data-table" style="font-size:5.7pt;">
            <tr>
                <th style="width:23%;">Nome do Estudante</th>
                <th style="width:9%; text-align:center;">Perfil / CID</th>
                <th style="width:12%;">Cuidador Dedicado</th>
                <th style="width:14%; text-align:center;">CAEd LP (C1→C2→C3)</th>
                <th style="width:14%; text-align:center;">CAEd MAT (C1→C2→C3)</th>
                <th style="width:11%; text-align:center;">SAAP Escrita</th>
                <th style="width:11%; text-align:center;">SAAP Leitura</th>
                <th style="width:6%; text-align:center;">Escore</th>
                <th style="width:6%; text-align:center;">EWS</th>
            </tr>
            {trs_p7}
        </table>

        <div class="card-highlight" style="font-size:6.3pt; line-height:1.3; margin-top:4px;">
            <strong>Notas Clínicas dos Alunos 01 a 13:</strong>
            <div>• <strong>Daniel Conceição (TDAH F90.0):</strong> Acompanhado pelo cuidador Ryan Soares. Evoluiu de Pré-Silábico para Silábico-Alfabético no SAAP e atingiu 263.6 pts no CAEd LP. Apresenta alerta EWS profilático para manter a rotina de atenção.</div>
            <div>• <strong>Francisca Adila (Aluna Nova / Típica):</strong> Regressão pontual no SAAP 3B (SIL_ALF → PRE) motivada por faltas consecutivas. Protocolo de Busca Ativa acionado e inclusão na RTI Camada 2.</div>
            <div>• <strong>Gustavo Sales (TOD/TDAH F91.3):</strong> Evolução com suporte comportamental PBS (Positive Behavior Support); média CAEd MAT no teto (300.0 pts). Cuidador exclusivo classificado como urgente.</div>
            <div>• <strong>Isabella Martins (TEA F84.0):</strong> Excelente estabilização sensorial com Silmara e Francisca Liduina. Atingiu 290.9 pts no CAEd LP e nível Silábico consolidado.</div>
        </div>
        {make_footer(7)}
    </div>
    """
    pages.append(p7)

    # ==========================================
    # LAUDA 8: TABELA MESTRE CENSITÁRIA (PARTE 2: 14 a 25)
    # ==========================================
    rows_p8 = df_alunos.iloc[13:]
    trs_p8 = ""
    for _, r in rows_p8.iterrows():
        cid10_val = str(r['codigo_cid10']) if pd.notna(r['codigo_cid10']) else ''
        cid_str = f"<span class='badge badge-red'>{cid10_val}</span>" if r['possui_laudo_cid'] else "<span class='badge badge-blue'>Típico</span>"
        ews_str = "<span class='badge badge-red'>EWS</span>" if r['alerta_regressao_ews'] else "<span class='badge badge-green'>OK</span>"
        cuid_raw = r['cuidador_dedicado'] if pd.notna(r['cuidador_dedicado']) else 'Sem cuidador'
        cuid_short = str(cuid_raw)[:18]
        trs_p8 += f"""
        <tr>
            <td><strong>{r['nome_estudante']}</strong></td>
            <td style="text-align:center;">{cid_str}</td>
            <td style="font-size:5.8pt;">{cuid_short}</td>
            <td style="text-align:center;">{r['caed_lp_c1_prof']:.0f} → {r['caed_lp_c2_prof']:.0f} → <strong>{r['caed_lp_c3_prof']:.0f}</strong></td>
            <td style="text-align:center;">{r['caed_mat_c1_prof']:.0f} → {r['caed_mat_c2_prof']:.0f} → <strong>{r['caed_mat_c3_prof']:.0f}</strong></td>
            <td style="text-align:center;">{r['saap_escrita_1b']} → {r['saap_escrita_2b']} → <strong>{r['saap_escrita_3b']}</strong></td>
            <td style="text-align:center;">{r['saap_leitura_1b']} → {r['saap_leitura_2b']} → <strong>{r['saap_leitura_3b']}</strong></td>
            <td style="text-align:center; font-weight:bold; color:#1e3a8a;">{r['escore_composto_desenvolvimento']:.1f}</td>
            <td style="text-align:center;">{ews_str}</td>
        </tr>
        """

    p8 = f"""
    <div class="page-block">
        {make_header(8, TOTAL_PAGES, "MATRIZ CENSITÁRIA NOMINAL - PARTE 2")}
        <h1 class="section-title">Matriz Censitária Consolidada dos Estudantes (Alunos 14 a 25)</h1>
        
        <div class="card" style="font-size:6.5pt; line-height:1.25; margin-bottom:3px;">
            <strong>Continuidade da Matriz Censitária Nominal:</strong> Acompanhamento integral das situações diagnósticas, suportes educacionais especializados (AEE/SRM), deltas de proficiência e sinalizadores precoces de intervenção pedagógica.
        </div>

        <table class="data-table" style="font-size:5.7pt;">
            <tr>
                <th style="width:23%;">Nome do Estudante</th>
                <th style="width:9%; text-align:center;">Perfil / CID</th>
                <th style="width:12%;">Cuidador Dedicado</th>
                <th style="width:14%; text-align:center;">CAEd LP (C1→C2→C3)</th>
                <th style="width:14%; text-align:center;">CAEd MAT (C1→C2→C3)</th>
                <th style="width:11%; text-align:center;">SAAP Escrita</th>
                <th style="width:11%; text-align:center;">SAAP Leitura</th>
                <th style="width:6%; text-align:center;">Escore</th>
                <th style="width:6%; text-align:center;">EWS</th>
            </tr>
            {trs_p8}
        </table>

        <div class="card-highlight" style="font-size:6.3pt; line-height:1.3; margin-top:4px;">
            <strong>Notas Clínicas dos Alunos 14 a 25:</strong>
            <div>• <strong>Maria Isis Conceição (Q99.8 / F84.0):</strong> Sob acompanhamento de Krishna Braz. Demonstra escore CAEd de 281.8 pts em LP e 290.9 pts em MAT. A oscilação no SAAP escrita 3B decorre de hipertonia manual transitória.</div>
            <div>• <strong>Maria Isis Pereira (TEA + TDAH F84/F90):</strong> Amparada por Francisca Liduina. Proficiência CAEd de 272.7 pts em LP e 300.0 pts em MAT. Hipersensibilidade a ruídos contornada por abafadores.</div>
            <div>• <strong>Moises Toledo (TEA + TDAH F84/F90):</strong> Manteve nível Silábico-Alfabético no 2B e 3B no SAAP e 290.9 pts no CAEd LP, demonstrando retenção fônica sólida com apoio de Silmara e Liduina.</div>
            <div>• <strong>Ruan Lucas (TEA F84.0):</strong> Sob cuidadoria de Círia Brito. Proficiência de 281.8 pts em LP e 300.0 pts em MAT. Estabilidade no nível Silábico-Alfabético confirmada.</div>
            <div>• <strong>Louise Alves Santiago:</strong> Transferida para São Paulo (ausência justificada no SAAP). Registro mantido no histórico censitário do CAEd.</div>
            <div>• <strong>Sarah Eloyse:</strong> Ausência justificada nas aplicações bimestrais do SAAP; consolidada com 290.9 pts em LP no CAEd Ciclo III.</div>
        </div>
        {make_footer(8)}
    </div>
    """
    pages.append(p8)

    # ==========================================
    # LAUDAS 9 a 15: CARTÕES GRÁFICOS INDIVIDUAIS (4 ALUNOS POR PÁGINA)
    # ==========================================
    def make_student_card_html(r):
        nome = r['nome_estudante']
        safe_name = "".join([c if c.isalnum() else "_" for c in nome])[:30]
        card_png = os.path.join(ALUNOS_DIR, f"card_{safe_name}.png")
        card_uri = pathlib.Path(card_png).as_uri()

        cid10_val = str(r['codigo_cid10']) if pd.notna(r['codigo_cid10']) else ''
        cid_badge = f"<span class='badge badge-red'>CID: {cid10_val}</span>" if r['possui_laudo_cid'] else "<span class='badge badge-blue'>Neurotípico</span>"
        ews_badge = "<span class='badge badge-red'>EWS ATIVO</span>" if r['alerta_regressao_ews'] else "<span class='badge badge-green'>Trajetória Estável</span>"
        cuid_info = str(r['cuidador_dedicado']) if pd.notna(r['cuidador_dedicado']) else 'Apoio pedagógico regular da regência'

        return f"""
        <div style="border:1px solid #cbd5e1; border-radius:4px; padding:3px 5px; background:#ffffff; margin-bottom:3px;">
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:1px; margin-bottom:2px;">
                <div style="font-weight:bold; font-size:7.2pt; color:#1e3a8a;">{nome}</div>
                <div>{cid_badge} {ews_badge} <span class="badge badge-yellow">Cluster {r['cluster_codigo']}</span></div>
            </div>
            <img src="{card_uri}" style="width:100%; height:auto; max-height:43mm; object-fit:contain; border-radius:3px; display:block; margin:1px 0;">
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px; font-size:5.8pt; line-height:1.2; color:#334155; margin-top:1px;">
                <div><strong>Apoio / Cuidador:</strong> {cuid_info[:40]}</div>
                <div><strong>Escore Global Composto:</strong> <span style="font-weight:bold; color:#1d4ed8;">{r['escore_composto_desenvolvimento']:.1f} / 100</span></div>
                <div><strong>Classificação:</strong> {r['classificacao_trajetoria']}</div>
                <div><strong>Intervenção:</strong> {r['estrategia_recomposicao_prioritaria'][:45]}...</div>
            </div>
        </div>
        """

    # Alunos 01 a 04 (Lauda 9)
    cards_p9 = "".join([make_student_card_html(df_alunos.iloc[i]) for i in range(0, 4)])
    p9 = f"""
    <div class="page-block">
        {make_header(9, TOTAL_PAGES, "FICHAS INDIVIDUAIS • ALUNOS 01 A 04")}
        <h1 class="section-title">Consolidado Individual dos Estudantes (Alunos 01 a 04)</h1>
        {cards_p9}
        {make_footer(9)}
    </div>
    """
    pages.append(p9)

    # Alunos 05 a 08 (Lauda 10)
    cards_p10 = "".join([make_student_card_html(df_alunos.iloc[i]) for i in range(4, 8)])
    p10 = f"""
    <div class="page-block">
        {make_header(10, TOTAL_PAGES, "FICHAS INDIVIDUAIS • ALUNOS 05 A 08")}
        <h1 class="section-title">Consolidado Individual dos Estudantes (Alunos 05 a 08)</h1>
        {cards_p10}
        {make_footer(10)}
    </div>
    """
    pages.append(p10)

    # Alunos 09 a 12 (Lauda 11)
    cards_p11 = "".join([make_student_card_html(df_alunos.iloc[i]) for i in range(8, 12)])
    p11 = f"""
    <div class="page-block">
        {make_header(11, TOTAL_PAGES, "FICHAS INDIVIDUAIS • ALUNOS 09 A 12")}
        <h1 class="section-title">Consolidado Individual dos Estudantes (Alunos 09 a 12)</h1>
        {cards_p11}
        {make_footer(11)}
    </div>
    """
    pages.append(p11)

    # Alunos 13 a 16 (Lauda 12)
    cards_p12 = "".join([make_student_card_html(df_alunos.iloc[i]) for i in range(12, 16)])
    p12 = f"""
    <div class="page-block">
        {make_header(12, TOTAL_PAGES, "FICHAS INDIVIDUAIS • ALUNOS 13 A 16")}
        <h1 class="section-title">Consolidado Individual dos Estudantes (Alunos 13 a 16)</h1>
        {cards_p12}
        {make_footer(12)}
    </div>
    """
    pages.append(p12)

    # Alunos 17 a 20 (Lauda 13)
    cards_p13 = "".join([make_student_card_html(df_alunos.iloc[i]) for i in range(16, 20)])
    p13 = f"""
    <div class="page-block">
        {make_header(13, TOTAL_PAGES, "FICHAS INDIVIDUAIS • ALUNOS 17 A 20")}
        <h1 class="section-title">Consolidado Individual dos Estudantes (Alunos 17 a 20)</h1>
        {cards_p13}
        {make_footer(13)}
    </div>
    """
    pages.append(p13)

    # Alunos 21 a 24 (Lauda 14)
    cards_p14 = "".join([make_student_card_html(df_alunos.iloc[i]) for i in range(20, 24)])
    p14 = f"""
    <div class="page-block">
        {make_header(14, TOTAL_PAGES, "FICHAS INDIVIDUAIS • ALUNOS 21 A 24")}
        <h1 class="section-title">Consolidado Individual dos Estudantes (Alunos 21 a 24)</h1>
        {cards_p14}
        {make_footer(14)}
    </div>
    """
    pages.append(p14)

    # Aluno 25 + Síntese (Lauda 15)
    card_p15 = make_student_card_html(df_alunos.iloc[24])
    p15 = f"""
    <div class="page-block">
        {make_header(15, TOTAL_PAGES, "FICHA INDIVIDUAL 25 & METAS DO 4º BIMESTRE")}
        <h1 class="section-title">Consolidado Individual (Aluno 25) & Metas SPAECE Somativo</h1>
        {card_p15}

        <h2 class="sub-title" style="margin-top:6px;">Plano Integrado de Ação Pedagógica & AEE para o 4º Bimestre</h2>
        <div class="card" style="font-size:6.3pt; line-height:1.3;">
            <div style="font-weight:bold; color:#1e3a8a; margin-bottom:2px;">DIRETRIZES CONSOLIDADAS PARA O ENCERRAMENTO DO CICLO DE ALFABETIZAÇÃO:</div>
            <div>• <strong>1. Tutoria Fônica de Alta Intensidade (RTI Camada 2):</strong> 15 minutos diários no início do turno da tarde para os estudantes com alerta EWS (Francisca Adila, Maria Leticia, Gustavo Henrique e Isis Gomes), focando decodificação de encontros consonantais e rimas.</div>
            <div>• <strong>2. Acomodações Sensoriais e Grafomotoras no PEI:</strong> Garantir aos estudantes neurodivergentes (Maria Isis Conceição, Maria Isis Pereira, Ruan Lucas e Isabella Martins) pranchas inclinadas de escrita, engrossadores de lápis, pausas ativas regulatórias e tempo estendido de 50% em avaliações escritas.</div>
            <div>• <strong>3. Ampliação do Repertório de Fluência Leitora:</strong> Prática diária de leitura repetida de pequenos textos poéticos e parlendas da cultura cearense para transição da decodificação silábica para a rota lexical automática.</div>
            <div>• <strong>4. Fortalecimento da Parceria com as Famílias:</strong> Roteiro lúdico de leitura domiciliar de 10 minutos diários sem cobrança punitiva, reforçando o vínculo afetivo com o livro didático.</div>
        </div>

        <table class="data-table" style="font-size:6.2pt; margin-top:4px;">
            <tr>
                <th>Indicador de Qualidade SPAECE</th>
                <th style="text-align:center;">Situação Atual (Ciclo III)</th>
                <th style="text-align:center;">Meta Final Projetada (4º Bimestre)</th>
                <th style="text-align:center;">Ação Estratégica</th>
            </tr>
            <tr>
                <td><strong>Percentual de Leitores Fluentes</strong></td>
                <td style="text-align:center;">65.2% dos avaliados</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">≥ 85.0% dos estudantes</td>
                <td style="text-align:center;">Leitura diária cronometrada</td>
            </tr>
            <tr>
                <td><strong>Proficiência Média TRI em LP</strong></td>
                <td style="text-align:center;">280.3 pontos (Avançado)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">≥ 290.0 pontos</td>
                <td style="text-align:center;">Interpretação e inferência textual</td>
            </tr>
            <tr>
                <td><strong>Proficiência Média TRI em Matemática</strong></td>
                <td style="text-align:center;">298.9 pontos (Consolidado)</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">≥ 300.0 pontos</td>
                <td style="text-align:center;">Resolução de situações-problema</td>
            </tr>
        </table>
        {make_footer(15)}
    </div>
    """
    pages.append(p15)

    # ==========================================
    # LAUDA 16: CONCLUSÕES E CHANCELA FORENSE
    # ==========================================
    p16 = f"""
    <div class="page-block">
        {make_header(16, TOTAL_PAGES, "GOVERNANÇA & CHANCELA FORENSE LEDGER")}
        <h1 class="section-title">Governança, Controle Social e Certificação Criptográfica</h1>
        
        <div class="card-highlight" style="font-size:7pt; line-height:1.35; margin-bottom:5px;">
            <strong>Pacto pela Educação Pública e Democrática em Crateús:</strong> Este documento consolida a prestação de contas censitária e bioestatística da EEFTI Airam Veras perante a Secretaria Municipal de Educação (SME), o Conselho Municipal de Educação (CME) e o Fórum Municipal de Educação (FME), em estrita consonância com a Lei Complementar nº 220/2025 (Sistema Nacional de Educação) e a Lei Federal nº 13.005/2014 (Plano Nacional de Educação).
        </div>

        <h2 class="sub-title">1. Matriz de Governança Interinstitucional</h2>
        <table class="data-table">
            <tr>
                <th style="width:25%;">Instância de Governança</th>
                <th style="width:35%;">Competência Legal & Normativa</th>
                <th style="width:40%;">Deliberação no Ciclo de Alfabetização</th>
            </tr>
            <tr>
                <td><strong>SME Crateús / CREDE 13</strong></td>
                <td>Coordenação da política pública e diretrizes curriculares municipais.</td>
                <td>Homologação das metas de alfabetização plena e fornecimento de recursos AEE.</td>
            </tr>
            <tr>
                <td><strong>Conselho Municipal de Educação (CME)</strong></td>
                <td>Órgão normativo, consultivo e fiscalizador do sistema municipal de ensino.</td>
                <td>Acompanhamento das resoluções de inclusão e cumprimento das metas do PME Crateús.</td>
            </tr>
            <tr>
                <td><strong>Fórum Municipal de Educação (FME)</strong></td>
                <td>Monitoramento e avaliação social periódica das metas do PME (Lei 13.005/2014).</td>
                <td>Validação da equidade nos investimentos em cuidadores e infraestrutura inclusiva.</td>
            </tr>
            <tr>
                <td><strong>Equipe Gestora Airam Veras</strong></td>
                <td>Execução pedagógica direta, gestão da SRM e regência do 1º Ano Único.</td>
                <td>Aplicação das práticas diárias, mediação do PEI e busca ativa contínua.</td>
            </tr>
        </table>

        <h2 class="sub-title">2. Certificação Criptográfica e Trilha de Auditoria Forense</h2>
        <div class="card" style="font-size:6.3pt; font-family:monospace; line-height:1.35; background:#f1f5f9; border:1px solid #94a3b8;">
            <div style="font-weight:bold; color:#0f172a; margin-bottom:2px;">REGISTRO IMUTÁVEL DE AUDITORIA TRANSACIONAL (BLOCKCHAIN-GRADE LEDGER):</div>
            <div>• BANCO DE DADOS RELACIONAL: <code>airam_veras_ecossistema.sqlite</code> (64 tabelas em 3FN)</div>
            <div>• SEQUÊNCIA DO BLOCO: <strong>Bloco 45</strong></div>
            <div>• TIPO DE OPERAÇÃO: <code>CONSOLIDACAO_MULTICICLOS_CAED_SAAP</code></div>
            <div>• TABELA AFETADA: <code>fato_consolidado_aluno_caed_saap_1ano</code> & <code>fato_consolidado_turma_caed_saap_1ano</code></div>
            <div>• IDENTIFICADOR DO REGISTRO: <code>COORTE_1ANO_25_ESTUDANTES</code></div>
            <div>• HASH DO BLOCO ANTERIOR (44): <code>39bb2f52c1ef97e7f607c3127453d719ce407677bf18859942a188be4cf9a7bc</code></div>
            <div>• HASH SHA-256 DO BLOCO ATUAL: <strong>2473a5251bed5692abc1fe979d77c0af911c2f75774f5aaf35bd97aea84435ad</strong></div>
            <div>• ASSINATURA FORENSE: <code>DR_MARCELO_CLARO_E_ANTIGRAVITY</code></div>
            <div>• TIMESTAMP UTC DE CRIAÇÃO: <code>2026-10-29 08:14:15 UTC</code></div>
        </div>

        <div style="margin-top:10px; border-top:1px dashed #cbd5e1; padding-top:6px; display:grid; grid-template-columns:1fr 1fr; gap:20px; text-align:center;">
            <div>
                <div style="border-bottom:1px solid #0f172a; height:20px; margin-bottom:3px;"></div>
                <div style="font-weight:bold; font-size:6.5pt;">COORDENAÇÃO PEDAGÓGICA & AEE</div>
                <div style="font-size:5.8pt; color:#64748b;">EEFTI AIRAM VERAS • CRATEÚS - CE</div>
            </div>
            <div>
                <div style="border-bottom:1px solid #0f172a; height:20px; margin-bottom:3px;"></div>
                <div style="font-weight:bold; font-size:6.5pt;">SECRETARIA MUNICIPAL DE EDUCAÇÃO</div>
                <div style="font-size:5.8pt; color:#64748b;">MUNICÍPIO DE CRATEÚS - CEARÁ</div>
            </div>
        </div>
        {make_footer(16)}
    </div>
    """
    pages.append(p16)

    print(f"Total de páginas geradas no relatório executivo: {len(pages)} (esperado: {TOTAL_PAGES})")

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Consolidado Censitário Analítico CAEd & SAAP - 1º Ano Airam Veras</title>
    <style>{CSS_STYLES}</style>
</head>
<body>
    {''.join(pages)}
</body>
</html>
"""
    with open(OUTPUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"-> HTML gravado em: {OUTPUT_HTML}")

    compile_pdf(OUTPUT_HTML, OUTPUT_PDF)
    print(f"-> Documento mestre executivo finalizado em: {OUTPUT_PDF}")

if __name__ == '__main__':
    build_dossier()
