# -*- coding: utf-8 -*-
"""
Gerador do Dossiê Pedagógico Integrado do 1º Ano (Ciclo III - 2026)
Escola de Cidadania Airam Veras • INEP 23084995 • Crateús - CE
Integração de:
- Consolidado Pedagógico Completo de Língua Portuguesa e Matemática (nos moldes do 5º Ano Corrigido)
- Caderno de Práticas Diárias Fônicas e Cumulativas Kumon (24 estudantes x 26 laudas = 624 laudas de práticas individuais)
- Total: 642 laudas em alta fidelidade vetorial A4
"""

import os
import sys
import subprocess
import pathlib
import pandas as pd
from pypdf import PdfReader, PdfWriter

sys.stdout.reconfigure(encoding='utf-8')

WORKSPACE_DIR = r"c:\Users\marce\Downloads\Airam veras"
DATA_DIR = os.path.join(WORKSPACE_DIR, "resultados-caed-ciclo-i-2026", "csv_originais")
F1_PATH = os.path.join(WORKSPACE_DIR, "Dossie_Integrado_1e2_Airam_Veras_2026_Fonico_Kumon_CAPA_PADRAO.pdf")
HTML_OUT = os.path.join(WORKSPACE_DIR, "datamining", "dossie_1ano_front_matter.html")
PDF_FRONT_OUT = os.path.join(WORKSPACE_DIR, "datamining", "dossie_1ano_front_matter.pdf")
PDF_FINAL_OUT = os.path.join(WORKSPACE_DIR, "DOSSIE_INTEGRADO_1ANO_AIRAM_VERAS_2026_FONICO_KUMON_MATEMATICA.pdf")

# Carregar dados
lp_csv = os.path.join(DATA_DIR, "1ANO_LEITURA_CICLO_I_2026", "HABILIDADES_DESEMPENHO_ESTUDANTE 22-10-2026 6-06-25.csv")
mat_csv = os.path.join(DATA_DIR, "1ANO_MATEMATICA_CICLO_I_2026", "HABILIDADES_DESEMPENHO_ESTUDANTE 22-10-2026 6-09-25.csv")

df_lp = pd.read_csv(lp_csv, sep=';', encoding='latin-1')
df_mat = pd.read_csv(mat_csv, sep=';', encoding='latin-1')

col_lp_niv = [c for c in df_lp.columns if 'vel de aprend' in c][0]
col_mat_niv = [c for c in df_mat.columns if 'vel de aprend' in c][0]

merged = pd.merge(df_lp, df_mat, on='Estudante', suffixes=('_LP', '_MAT'))
merged.sort_values(by='Estudante', inplace=True)

clusters_info = {
    "ANTONIO CALLEBY PEREIRA LIMA": ("1D", "Consolidação e Enriquecimento", "H04: 33%, H03: 67%", "Consolidado pleno"),
    "DANIEL CONCEICAO PIMENTEL": ("1A", "Base Alfabética e Decodificação", "H04: 0%, H07: 0%, H02: 50%", "H03: 50%"),
    "EMANUELLY DO NASCIMENTO BEZERRA": ("1D", "Consolidação e Enriquecimento", "H04: 33%, H05: 50%", "H02: 50%"),
    "FRANCISCO MIGUEL MARTINS DE SOUSA": ("1C", "Compreensão e Conversão", "H04: 33%, H07: 0%", "H03: 50%"),
    "GUSTAVO HENRIQUE MORENO DA SILVA": ("1A", "Base Alfabética e Decodificação", "H04: 0%, H05: 0%", "H03: 50%, H02: 50%"),
    "GUSTAVO SALES MACHADO": ("1C", "Compreensão e Conversão", "H04: 33%, H07: 50%", "Consolidado pleno"),
    "ISABELLA MARTINS FEITOSA": ("1A", "Base Alfabética e Decodificação", "H04: 0%, H07: 0%, H05: 50%", "H03: 50%"),
    "ISAC LUCCA FERNANDES MARTINS": ("1C", "Compreensão e Conversão", "H04: 67%, H07: 50%", "Consolidado pleno"),
    "ISIS GOMES MESQUITA": ("1B", "Segmentação e Leitura Funcional", "H04: 33%, H05: 50%", "H03: 50%"),
    "ISIS KETLEN SOUSA DA SILVA": ("1A", "Base Alfabética e Decodificação", "H04: 0%, H07: 0%", "H03: 50%, H04: 50%"),
    "JOSE YHUDY BENICIO FERREIRA DE ANDRADE": ("1C", "Compreensão e Conversão", "H04: 33%, H07: 50%", "Consolidado pleno"),
    "LIVYA MARIA ALVES MELO": ("1C", "Compreensão e Conversão", "H04: 67%, H05: 50%", "Consolidado pleno"),
    "LOUISE ALVES SANTIAGO": ("1C", "Compreensão e Conversão", "H04: 33%, H07: 50%", "Consolidado pleno"),
    "LUNNA DE SOUSA SILVA": ("1D", "Consolidação e Enriquecimento", "H04: 33%, H07: 50%", "H03: 50%"),
    "MARIA AGATHA DE SOUSA NEVES": ("1A", "Base Alfabética e Decodificação", "H04: 0%, H07: 0%, H02: 50%", "H03: 50%"),
    "MARIA ISIS DA CONCEICAO DE SOUSA": ("1D", "Consolidação e Enriquecimento", "H04: 67%, H05: 50%", "Consolidado pleno"),
    "MARIA ISIS PEREIRA GOMES": ("1A", "Base Alfabética e Decodificação", "H04: 0%, H07: 0%", "H03: 50%"),
    "MARIA JULIANA VIEIRA GOMES": ("1B", "Segmentação e Leitura Funcional", "H04: 33%, H05: 50%", "Consolidado pleno"),
    "MARIA LETICIA MARTINS DA SILVA": ("1B", "Segmentação e Leitura Funcional", "H04: 33%, H07: 50%", "H03: 50%"),
    "MARIA SOPHIA MARQUES SILVA": ("1A", "Base Alfabética e Decodificação", "H04: 0%, H07: 0%", "H03: 50%"),
    "MARIA YORRANA OLIVEIRA ARAUJO": ("1B", "Segmentação e Leitura Funcional", "H04: 33%, H07: 50%", "Consolidado pleno"),
    "MOISES TOLEDO DE SOUSA": ("1D", "Consolidação e Enriquecimento", "H04: 67%, H03: 67%", "Consolidado pleno"),
    "RUAN LUCAS DE SOUZA SALES": ("1D", "Consolidação e Enriquecimento", "H04: 67%, H07: 50%", "Consolidado pleno"),
    "SARAH ELOYSE LOPES VERISSIMO": ("1C", "Compreensão e Conversão", "H04: 33%, H07: 50%", "H03: 50%")
}

# Paginação calculada: 18 páginas de introdução + 26 páginas por aluno
student_pages = {}
curr = 19
for s in sorted(clusters_info.keys()):
    student_pages[s] = curr
    curr += 26

# Construção do HTML
css = """
@page {
    size: A4 portrait;
    margin: 0;
}
* {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
body {
    margin: 0;
    padding: 0;
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    font-size: 8.8pt;
    line-height: 1.35;
}
.page-block {
    width: 210mm;
    height: 297mm;
    max-height: 297mm;
    padding: 13mm 15mm 13mm 15mm;
    position: relative;
    page-break-after: always;
    overflow: hidden;
    background: #ffffff;
}
.header-bar {
    border-bottom: 2px solid #1e3a8a;
    padding-bottom: 5px;
    margin-bottom: 9px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}
.header-bar .inst-title {
    font-size: 8pt;
    font-weight: 800;
    color: #1e3a8a;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}
.header-bar .doc-subtitle {
    font-size: 7.5pt;
    color: #475569;
    font-weight: 600;
}
.header-bar .page-tag {
    background: #1e3a8a;
    color: #ffffff;
    padding: 2px 7px;
    border-radius: 3px;
    font-size: 7.5pt;
    font-weight: bold;
}
.footer-bar {
    position: absolute;
    bottom: 9mm;
    left: 15mm;
    right: 15mm;
    border-top: 1px solid #cbd5e1;
    padding-top: 4px;
    display: flex;
    justify-content: space-between;
    font-size: 6.8pt;
    color: #64748b;
}
h1.section-title {
    font-size: 13pt;
    color: #0f172a;
    margin: 0 0 7px 0;
    font-weight: 800;
    border-left: 4px solid #2563eb;
    padding-left: 8px;
    line-height: 1.2;
}
h2.sub-title {
    font-size: 9.8pt;
    color: #1e3a8a;
    margin: 8px 0 4px 0;
    font-weight: 700;
}
p {
    margin: 0 0 6px 0;
    text-align: justify;
}
.card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 4px;
    padding: 7px 9px;
    margin-bottom: 7px;
}
.card-highlight {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 4px;
    padding: 7px 9px;
    margin-bottom: 7px;
}
.card-warn {
    background: #fffbeb;
    border: 1px solid #fde68a;
    border-radius: 4px;
    padding: 7px 9px;
    margin-bottom: 7px;
}
.card-alert {
    background: #fff1f2;
    border: 1px solid #fecdd3;
    border-radius: 4px;
    padding: 7px 9px;
    margin-bottom: 7px;
}
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 7px;
}
.grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
    margin-bottom: 7px;
}
.grid-4 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr 1fr;
    gap: 6px;
    margin-bottom: 7px;
}
.kpi-box {
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
    padding: 8px;
    text-align: center;
}
.kpi-val {
    font-size: 15pt;
    font-weight: 800;
    color: #1e3a8a;
    line-height: 1;
}
.kpi-lbl {
    font-size: 7.2pt;
    color: #475569;
    font-weight: 600;
    margin-top: 3px;
    text-transform: uppercase;
}
table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 7px;
    font-size: 7.5pt;
}
table.data-table th {
    background: #1e3a8a;
    color: #ffffff;
    font-weight: 700;
    padding: 4px 6px;
    text-align: left;
    border: 1px solid #1e3a8a;
}
table.data-table td {
    padding: 3.5px 6px;
    border: 1px solid #cbd5e1;
}
table.data-table tr:nth-child(even) td {
    background: #f8fafc;
}
.badge {
    display: inline-block;
    padding: 1px 5px;
    border-radius: 3px;
    font-size: 6.8pt;
    font-weight: 700;
    text-transform: uppercase;
}
.badge-green { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.badge-yellow { background: #fef9c3; color: #854d0e; border: 1px solid #fde047; }
.badge-blue { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.badge-purple { background: #f3e8ff; color: #6b21a8; border: 1px solid #d8b4fe; }
.badge-red { background: #ffe4e6; color: #9f1239; border: 1px solid #fca5a5; }

/* Capa */
.cover-container {
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    border: 3px double #1e3a8a;
    padding: 28px 22px;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
}
.cover-top {
    text-align: center;
}
.cover-crest {
    font-size: 11pt;
    font-weight: 800;
    color: #1e3a8a;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.cover-subcrest {
    font-size: 8.5pt;
    color: #475569;
    font-weight: 600;
    margin-bottom: 25px;
}
.cover-center {
    text-align: center;
    padding: 20px 0;
}
.cover-badge-cycle {
    display: inline-block;
    background: #1e3a8a;
    color: #ffffff;
    font-size: 8.5pt;
    font-weight: 800;
    padding: 4px 14px;
    border-radius: 20px;
    letter-spacing: 1px;
    margin-bottom: 15px;
}
.cover-main-title {
    font-size: 24pt;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.15;
    margin-bottom: 12px;
    text-transform: uppercase;
}
.cover-main-subtitle {
    font-size: 11pt;
    font-weight: 700;
    color: #2563eb;
    margin-bottom: 22px;
    letter-spacing: 0.5px;
}
.cover-desc-box {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 12px 16px;
    font-size: 8.5pt;
    color: #334155;
    line-height: 1.45;
    text-align: center;
    max-width: 90%;
    margin: 0 auto;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}
.cover-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 10px;
    margin-top: 25px;
}
.cover-stat-card {
    background: #ffffff;
    border: 1.5px solid #1e3a8a;
    border-radius: 6px;
    padding: 10px 6px;
    text-align: center;
}
.cover-stat-num {
    font-size: 17pt;
    font-weight: 900;
    color: #1e3a8a;
}
.cover-stat-txt {
    font-size: 7.2pt;
    font-weight: 700;
    color: #475569;
    text-transform: uppercase;
    margin-top: 3px;
}
.cover-bottom {
    text-align: center;
    font-size: 7.5pt;
    color: #64748b;
    border-top: 1px solid #e2e8f0;
    padding-top: 12px;
    line-height: 1.35;
}
"""

def make_header(page_num, total_pages=18):
    return f"""
    <div class="header-bar">
        <div>
            <div class="inst-title">Escola de Cidadania Airam Veras • Crateús - CE</div>
            <div class="doc-subtitle">Dossiê Pedagógico Integrado 1º Ano • Ciclo III - 2026 • INEP 23084995</div>
        </div>
        <div class="page-tag">Página {page_num} de {total_pages}</div>
    </div>
    """

def make_footer(page_num, total_pages=18):
    return f"""
    <div class="footer-bar">
        <div>Documento Institucional Reservado • Uso Pedagógico Restrito • Gestão Escolar & AEE</div>
        <div>Língua Portuguesa & Matemática Integradas</div>
        <div>Página {page_num} de {total_pages}</div>
    </div>
    """

pages_html = []

# ================= PAGE 1: CAPA =================
p1 = f"""
<div class="page-block">
    <div class="cover-container">
        <div class="cover-top">
            <div class="cover-crest">Governo Municipal de Crateús • Secretaria de Educação</div>
            <div class="cover-subcrest">ESCOLA DE CIDADANIA AIRAM VERAS • INEP 23084995</div>
        </div>
        
        <div class="cover-center">
            <div class="cover-badge-cycle">CICLO III • GESTÃO BASEADA EM EVIDÊNCIAS • 2026</div>
            <div class="cover-main-title">Dossiê Pedagógico<br>Integrado • 1º Ano</div>
            <div class="cover-main-subtitle">Língua Portuguesa, Fluência Fônica & Raciocínio Lógico-Matemático</div>
            
            <div class="cover-desc-box">
                Instrumento operacional de diagnóstico, recomposição e aceleração da aprendizagem para a turma do 1º Ano do Ensino Fundamental. Consolida os microdados empíricos do CAEd (Ciclo I - 2026), matriz de habilidades H01-H09 (LP) e H01-H07 (Matemática), lógica cumulativa Kumon (regra 20-60-20), rotação por 4 estações pedagógicas e o caderno completo de intervenção individualizada contendo 40 dias de práticas diárias estruturadas por estudante.
            </div>
            
            <div class="cover-stats">
                <div class="cover-stat-card">
                    <div class="cover-stat-num">24</div>
                    <div class="cover-stat-txt">Estudantes (100%)</div>
                </div>
                <div class="cover-stat-card">
                    <div class="cover-stat-num">4</div>
                    <div class="cover-stat-txt">Clusters Ativos</div>
                </div>
                <div class="cover-stat-card">
                    <div class="cover-stat-num">8</div>
                    <div class="cover-stat-txt">Semanas de Prática</div>
                </div>
                <div class="cover-stat-card">
                    <div class="cover-stat-num">642</div>
                    <div class="cover-stat-txt">Laudas no Dossiê</div>
                </div>
            </div>
        </div>
        
        <div class="cover-bottom">
            <strong>ABORDAGEM METODOLÓGICA TRIÁDICA:</strong> Método Fônico Sistemático Explícito • Prática Deliberada Kumon • Matemática Manipulável Concreta<br>
            Crateús - Ceará • Ciclo III de 2026 • Documento Pedagógico de Alta Sensibilidade
        </div>
    </div>
</div>
"""
pages_html.append(p1)

# ================= PAGE 2: ARQUITETURA METODOLÓGICA =================
p2 = f"""
<div class="page-block">
    {make_header(2)}
    <h1 class="section-title">1. Arquitetura Metodológica do Dossiê Integrado</h1>
    
    <div class="card-highlight">
        <strong>Princípio Norteador:</strong> O Dossiê Integrado do 1º Ano articula a ciência cognitiva da leitura à didática do domínio cumulativo da matemática. Nenhuma criança avança sem consolidação prévia, e nenhuma intervenção ocorre sem evidência empírica individualizada.
    </div>
    
    <h2 class="sub-title">1.1 O Método Fônico Explícito e Sistemático no 1º Ano</h2>
    <p>O 1º ano constitui a janela crítica da alfabetização na idade certa (compromisso PAIC e Criança Alfabetizada). Adota-se o método fônico explícito em progressão rigorosa:</p>
    <div class="grid-2">
        <div class="card">
            <strong>Fase 1: Consciência Fonológica e Fonêmica</strong>
            <p style="font-size: 7.8pt; margin: 2px 0;">Treino auditivo intensivo de rimas, aliterações, isolamento de som inicial/final e manipulação fonêmica (fusão e segmentação oral), prevenindo adivinhações por imagem.</p>
        </div>
        <div class="card">
            <strong>Fase 2: Correspondência Grafofonêmica Estrita</strong>
            <p style="font-size: 7.8pt; margin: 2px 0;">Apresentação ordenada das relações letra-som: vogais, consoantes contínuas (/m/, /n/, /f/, /v/, /s/, /l/), oclusivas (/p/, /b/, /t/, /d/) e dígrafos. Leitura de palavras reais e pseudopalavras para atestar decodificação pura.</p>
        </div>
    </div>
    
    <h2 class="sub-title">1.2 Prática Cumulativa Inspirada na Lógica Kumon</h2>
    <p>A consolidação da memória de trabalho exige repetição espaçada com sobreaprendizagem controlada. A rotina adota o modelo Kumon adaptado:</p>
    <div class="grid-3">
        <div class="kpi-box">
            <div class="kpi-val">20%</div>
            <div class="kpi-lbl">Revisão Cumulativa</div>
            <p style="font-size: 7.2pt; color: #475569; margin-top: 3px;">Aquecimento diário com habilidades já dominadas para estabilidade neural.</p>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">60%</div>
            <div class="kpi-lbl">Foco Alvo do Dia</div>
            <p style="font-size: 7.2pt; color: #475569; margin-top: 3px;">Exercício guiado na habilidade diagnosticada com menor taxa de acerto.</p>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">20%</div>
            <div class="kpi-lbl">Transferência Autônoma</div>
            <p style="font-size: 7.2pt; color: #475569; margin-top: 3px;">Aplicação em frase inédita, situação-problema ou miniavaliação formativa.</p>
        </div>
    </div>
    
    <h2 class="sub-title">1.3 Integração com o Raciocínio Lógico-Matemático</h2>
    <p>A matemática no 1º ano não é tratada de forma estanque. O raciocínio numérico compartilha com a leitura a representação simbólica, o reconhecimento de padrões e a ordenação sequencial. As atividades integram contagem um a um, conservação de quantidade, representação posicional decimal e linguagem matemática clara, assegurando que dificuldades leitoras não bloqueiem a avaliação do cálculo.</p>
    
    <div class="card-warn">
        <strong>Critério de Avanço de Domínio:</strong> Taxa de acerto &lt; 85% exige reensino imediato com modelagem direta; entre 85% e 94% indica prática guiada cumulativa; &ge; 95% com compreensão atesta prontidão para a etapa subsequente.
    </div>
    {make_footer(2)}
</div>
"""
pages_html.append(p2)

# ================= PAGE 3: ROTINA DIÁRIA E MATEMÁTICA =================
p3 = f"""
<div class="page-block">
    {make_header(3)}
    <h1 class="section-title">2. Rotina Diária Estruturada e Gestão de Tempo</h1>
    
    <p>A estrutura temporal do 1º ano organiza-se em blocos curtos, dinâmicos e previsíveis, reduzindo a fadiga atencional e maximizando o tempo efetivo de aprendizagem (Time on Task).</p>
    
    <div class="card">
        <h2 class="sub-title" style="margin-top:0;">Sessão Diária de Leitura e Fluência Fônica (20 Minutos)</h2>
        <table class="data-table">
            <tr>
                <th style="width: 18%;">Bloco</th>
                <th style="width: 14%;">Duração</th>
                <th>Objetivo Neurocognitivo</th>
                <th style="width: 32%;">Atividades-Chave</th>
            </tr>
            <tr>
                <td><strong>Bloco A</strong></td>
                <td><span class="badge badge-blue">5 min</span></td>
                <td>Consciência Fonêmica e Auditiva</td>
                <td>Isolar som inicial/final; segmentação de fonemas com palmas/fichas; rimas orais.</td>
            </tr>
            <tr>
                <td><strong>Bloco B</strong></td>
                <td><span class="badge badge-blue">7 min</span></td>
                <td>Decodificação Grafofonêmica</td>
                <td>Leitura guiada de sílabas canônicas e não canônicas; lista de palavras reais e pseudopalavras.</td>
            </tr>
            <tr>
                <td><strong>Bloco C</strong></td>
                <td><span class="badge badge-blue">5 min</span></td>
                <td>Leitura Conectada e Fluência</td>
                <td>Leitura repetida de frase ou parlenda; modelagem de prosódia e entonação; pergunta literal.</td>
            </tr>
            <tr>
                <td><strong>Bloco D</strong></td>
                <td><span class="badge badge-blue">3 min</span></td>
                <td>Registro Formativo Docente</td>
                <td>Anotação da precisão (%), hesitações, tipo de erro (troca/omissão) e decisão do dia seguinte.</td>
            </tr>
        </table>
    </div>

    <div class="card">
        <h2 class="sub-title" style="margin-top:0;">Sessão Diária de Raciocínio Lógico-Matemático (20 Minutos)</h2>
        <p style="font-size: 7.8pt;">Baseada no concreto-pictórico-abstrato (CPA) com regra cumulativa 20-60-20:</p>
        <table class="data-table">
            <tr>
                <th style="width: 18%;">Momento</th>
                <th style="width: 14%;">Duração</th>
                <th>Eixo Didático</th>
                <th style="width: 32%;">Metodologia e Recursos</th>
            </tr>
            <tr>
                <td><strong>1. Retomada</strong></td>
                <td><span class="badge badge-green">4 min (20%)</span></td>
                <td>Aquecimento de Contagem</td>
                <td>Contagem oral rítmica (frente/trás até 20); reconhecimento relâmpago de algarismos.</td>
            </tr>
            <tr>
                <td><strong>2. Prática Focal</strong></td>
                <td><span class="badge badge-yellow">12 min (60%)</span></td>
                <td>Habilidade-Alvo CAEd</td>
                <td>Manipulação com tampinhas/material dourado: adição/subtração, comparação de números até 50.</td>
            </tr>
            <tr>
                <td><strong>3. Desafio</strong></td>
                <td><span class="badge badge-purple">4 min (20%)</span></td>
                <td>Transferência e Registro</td>
                <td>Resolução de 1 situação-problema pictórica no caderno e checagem de raciocínio.</td>
            </tr>
        </table>
    </div>
    
    <div class="grid-2">
        <div class="card-highlight">
            <strong>Alinhamento com a Sexta-Feira Formativa (Dia 5):</strong>
            <p style="font-size: 7.5pt; margin: 3px 0;">Toda sexta-feira substitui os blocos C e D pela <strong>Miniavaliação Semanal de Fluência</strong> e pelo preenchimento obrigatório da Grade Docente (precisão de palavras lidas por minuto e acerto de compreensão).</p>
        </div>
        <div class="card-warn">
            <strong>Prevenção de Lacunas Cumulativas:</strong>
            <p style="font-size: 7.5pt; margin: 3px 0;">Estudantes com 2 dias consecutivos de precisão &lt;80% são imediatamente encaminhados ao atendimento focal da Coordenação/AEE no contraturno ou na estação de apoio.</p>
        </div>
    </div>
    {make_footer(3)}
</div>
"""
pages_html.append(p3)

# ================= PAGE 4: ACESSIBILIDADE E NEURODIVERSIDADE =================
p4 = f"""
<div class="page-block">
    {make_header(4)}
    <h1 class="section-title">3. Acessibilidade, Neurodiversidade e Diretrizes de AEE</h1>
    
    <p>A Escola de Cidadania Airam Veras opera sob a premissa de que a equidade pedagógica exige diferenciação curricular estruturada. As práticas diárias do 1º ano incorporam protocolos clínicos e pedagógicos para atendimento à diversidade neurológica da turma:</p>
    
    <div class="card">
        <h2 class="sub-title" style="margin-top:0;">Protocolos Específicos por Perfil Neurocognitivo</h2>
        <table class="data-table">
            <tr>
                <th style="width: 22%;">Condição / Perfil</th>
                <th style="width: 35%;">Manifestação no 1º Ano</th>
                <th>Adaptação Pedagógica Mandatória</th>
            </tr>
            <tr>
                <td><strong>Dislexia e Transtornos de Leitura</strong></td>
                <td>Dificuldade persistente na rota fonológica, lentidão na correspondência letra-som, trocas espelhadas (b/d, p/q).</td>
                <td>Uso de régua/janela de leitura; aumento de espaçamento gráfico; proibição de pedir que adivinhe pelo contexto; pistas táteis e auditivas simultâneas.</td>
            </tr>
            <tr>
                <td><strong>TDAH (CID F90.0)</strong></td>
                <td>Hiperatividade motora, impulsividade na resposta, perda de foco em tarefas que exigem esforço mental sustentado.</td>
                <td>Segmentação da folha em microetapas (2 itens por vez); pausas ativas a cada 7 minutos; reforço contingente imediato; tarefas com resposta motora ativa.</td>
            </tr>
            <tr>
                <td><strong>TOD (CID F91.3)</strong></td>
                <td>Resistência passiva ou ativa à instrução direta, baixa tolerância à frustração ao errar, recusa de atividades longas.</td>
                <td>Contrato pedagógico prévio ("Você prefere começar pela leitura ou pelo desenho?"); validação da autonomia; foco estrito no acerto sem confrontação verbal.</td>
            </tr>
            <tr>
                <td><strong>TEA (CID F84.0)</strong></td>
                <td>Sobrecarga sensorial, rigidez cognitiva, necessidade de previsibilidade estrita da rotina, linguagem literal.</td>
                <td>Quadro de rotina visual pictórico na carteira; eliminação de estímulos sonoros concorrentes; instruções de um comando por vez; reforçador de interesse restrito.</td>
            </tr>
            <tr>
                <td><strong>Altas Habilidades / Superdotação</strong></td>
                <td>Prontidão de leitura e raciocínio lógico muito antes dos pares; risco de desengajamento e comportamento dispersivo.</td>
                <td>Enriquecimento curricular Tipo I e II (Modelo de Renzulli): desafios de inferência textual complexa, tutoria entre pares e produção escrita criativa avançada.</td>
            </tr>
        </table>
    </div>
    
    <h2 class="sub-title">3.1 Acomodação Universal na Avaliação Matemática</h2>
    <div class="card-highlight">
        <strong>Desacoplamento Leitor:</strong> Quando o estudante apresenta fragilidade severa em decodificação (Cluster 1A), a avaliação de matemática <em>NUNCA</em> deve ser inviabilizada pela leitura. O professor aplicador é expressamente orientado a <strong>ler o enunciado do problema em voz alta</strong>, garantindo que o instrumento meça estritamente o raciocínio numérico e espacial da criança.
    </div>
    
    <h2 class="sub-title">3.2 Integração com a Sala de Recursos Multifuncionais (AEE)</h2>
    <p>Os estudantes laudados ou em processo de triagem diagnóstica têm suas folhas de prática integradas ao Plano de Atendimento Educacional Especializado (PAEE), assegurando que o professor de AEE trabalhe de forma espelhada as mesmas correspondências fônicas e conceitos numéricos da sala de aula comum.</p>
    {make_footer(4)}
</div>
"""
pages_html.append(p4)

# ================= PAGE 5: MATEMÁTICA CUMULATIVA E DESCRITORES =================
p5 = f"""
<div class="page-block">
    {make_header(5)}
    <h1 class="section-title">4. Matemática: Lógica Cumulativa e Matriz de Descritores</h1>
    
    <p>O ensino da matemática no 1º ano fundamenta-se na formação do conceito de número, contagem significativa e relações quantitativas e espaciais. A matriz do CAEd Ciclo I avaliou 7 habilidades empíricas centrais (H01 a H07), correlacionadas à BNCC e à Matriz PAIC/SPAECE:</p>
    
    <div class="card">
        <h2 class="sub-title" style="margin-top:0;">Matriz de Descritores e Foco Cognitivo no 1º Ano</h2>
        <table class="data-table">
            <tr>
                <th style="width: 10%;">Código</th>
                <th style="width: 15%;">BNCC</th>
                <th style="width: 35%;">Descritor / Objeto de Conhecimento</th>
                <th>Estratégia Didática de Domínio</th>
            </tr>
            <tr>
                <td><strong>H01 / D01</strong></td>
                <td>EF01MA04</td>
                <td>Contar elementos de uma coleção (até 10 objetos) e associar à escrita numérica.</td>
                <td>Contagem termo a termo com objetos concretos; correspondência biunívoca sem pular elementos.</td>
            </tr>
            <tr>
                <td><strong>H02 / D02</strong></td>
                <td>EF01MA03</td>
                <td>Comparar quantidades de objetos (mais, menos, mesma quantidade).</td>
                <td>Emparelhamento visual e sobreposição de grupos; uso de termos comparativos explícitos.</td>
            </tr>
            <tr>
                <td><strong>H03 / D03</strong></td>
                <td>EF01MA05</td>
                <td>Comparar e ordenar números naturais de até dois algarismos (ordem crescente/decrescente).</td>
                <td>Uso intensivo da reta numérica ilustrada, quadro de 1 a 50 e fichas sobrepostas (dezena/unidade).</td>
            </tr>
            <tr>
                <td><strong>H04 / D08</strong></td>
                <td>EF01MA08</td>
                <td>Resolver problemas aditivos (juntar e acrescentar) com suporte de imagens.</td>
                <td>Dramatização de situações-problema; agrupamento com blocos lógicos; registro pictórico antes do formal.</td>
            </tr>
            <tr>
                <td><strong>H05 / D08</strong></td>
                <td>EF01MA08</td>
                <td>Resolver problemas subtrativos (retirar e comparar) com suporte de imagens.</td>
                <td>Ação concreta de retirar elementos de uma coleção; técnica de riscar elementos no papel.</td>
            </tr>
            <tr>
                <td><strong>H06 / D09</strong></td>
                <td>EF01MA09</td>
                <td>Classificar objetos e figuras geométricas por atributos (forma, cor, tamanho).</td>
                <td>Classificação de figuras do cotidiano; agrupamento de blocos de acordo com 1 e 2 critérios.</td>
            </tr>
            <tr>
                <td><strong>H07 / D10</strong></td>
                <td>EF01MA10</td>
                <td>Identificar e completar regularidades em sequências e padrões geométricos.</td>
                <td>Sequenciamento de contas coloridas, formas geométricas alternadas (círculo, quadrado, círculo...).</td>
            </tr>
        </table>
    </div>
    
    <div class="grid-2">
        <div class="card-highlight">
            <strong>Prioridade de Recomposição na Turma:</strong>
            <p style="font-size: 7.5pt; margin: 3px 0;">O descritor <strong>H03 (Comparação de números naturais)</strong> obteve <strong>71% de acerto</strong>, sendo o menor percentual da avaliação de matemática. O plano de ação dedica 3 sessões semanais com jogos de batalha de cartas numéricas e trilhas de tabuleiro para consolidar o senso de grandeza numérica.</p>
        </div>
        <div class="card">
            <strong>Força Cognitiva Consolidada:</strong>
            <p style="font-size: 7.5pt; margin: 3px 0;">As habilidades <strong>H01, H05, H06 e H07</strong> atingiram <strong>100% de acerto escolar</strong>, evidenciando domínio sólido das noções de classificação, padrão e subtração inicial, servindo de alavanca para o avanço das demais habilidades.</p>
        </div>
    </div>
    {make_footer(5)}
</div>
"""
pages_html.append(p5)

# ================= PAGE 6: SÍNTESE EXECUTIVA DO DIAGNÓSTICO =================
p6 = f"""
<div class="page-block">
    {make_header(6)}
    <h1 class="section-title">5. Síntese Executiva do Diagnóstico CAEd Ciclo I</h1>
    
    <p>A avaliação externa CAEd Ciclo I (2026) fornece a radiografia censitária da turma do 1º ano da Escola Airam Veras, atestando engajamento institucional pleno e estabelecendo a linha de base para as metas do Ciclo III:</p>
    
    <div class="grid-4">
        <div class="kpi-box">
            <div class="kpi-val">24/24</div>
            <div class="kpi-lbl">100% Avaliados</div>
            <p style="font-size: 7pt; color: #15803d; font-weight:bold; margin-top:2px;">Participação Plena</p>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">0%</div>
            <div class="kpi-lbl">Defasagem Severa</div>
            <p style="font-size: 7pt; color: #15803d; font-weight:bold; margin-top:2px;">Zero Crítico</p>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">42%</div>
            <div class="kpi-lbl">LP Adequado</div>
            <p style="font-size: 7pt; color: #2563eb; font-weight:bold; margin-top:2px;">10 Estudantes</p>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">46%</div>
            <div class="kpi-lbl">MAT Adequado</div>
            <p style="font-size: 7pt; color: #2563eb; font-weight:bold; margin-top:2px;">11 Estudantes</p>
        </div>
    </div>
    
    <h2 class="sub-title">5.1 Distribuição da Turma por Padrão de Desempenho</h2>
    <table class="data-table">
        <tr>
            <th>Componente Curricular</th>
            <th style="text-align:center;">Avaliados (%)</th>
            <th style="text-align:center;">Defasagem</th>
            <th style="text-align:center;">Intermediário</th>
            <th style="text-align:center;">Adequado</th>
            <th>Diagnóstico Institucional</th>
        </tr>
        <tr>
            <td><strong>Língua Portuguesa (Leitura)</strong></td>
            <td style="text-align:center;"><span class="badge badge-green">100% (24)</span></td>
            <td style="text-align:center;"><span class="badge badge-green">0% (0)</span></td>
            <td style="text-align:center;"><span class="badge badge-yellow">58% (14)</span></td>
            <td style="text-align:center;"><span class="badge badge-blue">42% (10)</span></td>
            <td>Zona de conversão direta: 14 alunos em nível intermediário prontos para transição.</td>
        </tr>
        <tr>
            <td><strong>Matemática</strong></td>
            <td style="text-align:center;"><span class="badge badge-green">100% (24)</span></td>
            <td style="text-align:center;"><span class="badge badge-green">0% (0)</span></td>
            <td style="text-align:center;"><span class="badge badge-yellow">54% (13)</span></td>
            <td style="text-align:center;"><span class="badge badge-blue">46% (11)</span></td>
            <td>Elevada base de adequação; 13 alunos necessitam reforço focal em H03 e H02.</td>
        </tr>
    </table>
    
    <h2 class="sub-title">5.2 A Trajetória de Recuperação: Evolução do SAAP para o CAEd</h2>
    <div class="card-highlight">
        <p>No diagnóstico de leitura inicial do município (SAAP), o 1º ano da Escola Airam Veras apresentou <strong>91,67% de Não Leitores (NL)</strong>, refletindo a defasagem pós-infantil compartilhada por escolas de contexto vulnerável. O resultado do CAEd revela uma <strong>transformação pedagógica expressiva</strong>:</p>
        <ul style="margin: 4px 0 4px 18px; padding: 0; font-size: 7.8pt;">
            <li><strong>Salto de Adequação:</strong> A adequação saltou de 8,33% para <strong>41,67% em Língua Portuguesa</strong> (+33,34 p.p. de ganho real).</li>
            <li><strong>Erradicação da Defasagem Crítica:</strong> Zero estudantes permanecem na faixa de defasagem do CAEd.</li>
            <li><strong>Potencial de Meta:</strong> A totalidade dos 14 estudantes do nível intermediário domina letras e sílabas simples, carecendo apenas de fluência e localização textual para ingressar no padrão adequado.</li>
        </ul>
    </div>
    
    <div class="card-warn">
        <strong>Conclusão da Gestão:</strong> A turma não possui barreiras intransponíveis de aprendizagem. Trata-se de um coletivo altamente responsivo ao ensino explícito, cuja meta de atingir <strong>80% de adequação no Ciclo III</strong> depende da conversão focal de apenas 9 a 10 estudantes do nível Intermediário.
    </div>
    {make_footer(6)}
</div>
"""
pages_html.append(p6)

# ================= PAGE 7: DIAGNÓSTICO CURRICULAR LP =================
p7 = f"""
<div class="page-block">
    {make_header(7)}
    <h1 class="section-title">6. Diagnóstico Curricular de Língua Portuguesa</h1>
    
    <p>A análise item a item das 9 habilidades avaliadas no CAEd permite identificar com precisão microcirúrgica onde residem as fortalezas e as vulnerabilidades leitoras da turma:</p>
    
    <table class="data-table">
        <tr>
            <th style="width: 10%;">Código</th>
            <th style="width: 48%;">Descrição da Habilidade Avaliada</th>
            <th style="width: 14%; text-align:center;">Acerto Turma</th>
            <th style="width: 14%; text-align:center;">Status</th>
            <th>Ação Pedagógica Focal</th>
        </tr>
        <tr>
            <td><strong>H01</strong></td>
            <td>Reconhecer letras do alfabeto grafadas em diferentes formatos.</td>
            <td style="text-align:center; font-weight:bold;">83%</td>
            <td style="text-align:center;"><span class="badge badge-green">Consolidado</span></td>
            <td>Manter em aquecimento diário (fichas relâmpago).</td>
        </tr>
        <tr>
            <td><strong>H02</strong></td>
            <td>Diferenciar letras de outros sinais gráficos (números, pontuação).</td>
            <td style="text-align:center; font-weight:bold;">75%</td>
            <td style="text-align:center;"><span class="badge badge-yellow">Recomposição</span></td>
            <td>Atividades contrastivas de classificação de caracteres.</td>
        </tr>
        <tr>
            <td><strong>H03</strong></td>
            <td>Identificar a ordem alfabética em listas e títulos curtos.</td>
            <td style="text-align:center; font-weight:bold;">85%</td>
            <td style="text-align:center;"><span class="badge badge-green">Consolidado</span></td>
            <td>Organização de agenda e lista de nomes da turma.</td>
        </tr>
        <tr style="background: #ffe4e6;">
            <td><strong>H04</strong></td>
            <td><strong>Localizar informação explícita em texto verbal curto.</strong></td>
            <td style="text-align:center; font-weight:bold; color: #be123c;">50%</td>
            <td style="text-align:center;"><span class="badge badge-red">CRÍTICO</span></td>
            <td><strong>Prioridade Máxima: releitura com marca-texto e perguntas literais.</strong></td>
        </tr>
        <tr>
            <td><strong>H05</strong></td>
            <td>Identificar o assunto principal de um texto com apoio figurativo.</td>
            <td style="text-align:center; font-weight:bold; color: #b45309;">63%</td>
            <td style="text-align:center;"><span class="badge badge-yellow">Atenção</span></td>
            <td>Modelagem docente do tema global ("Sobre o que fala o texto?").</td>
        </tr>
        <tr>
            <td><strong>H06</strong></td>
            <td>Ler palavras com estrutura silábica canônica consoante-vogal (CV).</td>
            <td style="text-align:center; font-weight:bold;">90%</td>
            <td style="text-align:center;"><span class="badge badge-green">Consolidado</span></td>
            <td>Avançar para sílabas complexas (CVC, CCV).</td>
        </tr>
        <tr style="background: #fffbeb;">
            <td><strong>H07</strong></td>
            <td>Reconhecer a finalidade de textos de circulação social cotidiana.</td>
            <td style="text-align:center; font-weight:bold; color: #b45309;">60%</td>
            <td style="text-align:center;"><span class="badge badge-yellow">Atenção</span></td>
            <td>Trabalho com bilhetes, convites, listas e receitas.</td>
        </tr>
        <tr>
            <td><strong>H08</strong></td>
            <td>Ler frases simples com autonomia e compreensão de sentido.</td>
            <td style="text-align:center; font-weight:bold;">85%</td>
            <td style="text-align:center;"><span class="badge badge-green">Consolidado</span></td>
            <td>Leitura diária em voz alta e prosódia dirigida.</td>
        </tr>
        <tr>
            <td><strong>H09</strong></td>
            <td>Reconhecer o significado de palavras a partir do contexto ilustrado.</td>
            <td style="text-align:center; font-weight:bold;">100%</td>
            <td style="text-align:center;"><span class="badge badge-green">Pleno</span></td>
            <td>Explorar expansão vocabular e campos semânticos.</td>
        </tr>
    </table>
    
    <div class="card-alert">
        <strong>Foco Estratégico em H04 (50% de acerto):</strong> A capacidade de responder "quem?", "onde?" e "o quê?" em frases curtas representa o nó crítico da turma. As práticas diárias de leitura inseridas no caderno dedicam o <strong>Dia 3 e Dia 4</strong> de cada semana à localização textual direta antes de inferências.
    </div>
    
    <div class="card-highlight">
        <strong>Síntese de Domínio Fônico:</strong> A habilidade H06 (90%) demonstra que o princípio alfabético e a fusão silábica simples estão assentados na quase totalidade dos alunos. O desafio é transferir a decodificação da palavra isolada para a unidade de sentido da frase (H04 e H07).
    </div>
    {make_footer(7)}
</div>
"""
pages_html.append(p7)

# ================= PAGE 8: DIAGNÓSTICO CURRICULAR MATEMÁTICA =================
p8 = f"""
<div class="page-block">
    {make_header(8)}
    <h1 class="section-title">7. Diagnóstico Curricular de Matemática</h1>
    
    <p>Em Matemática, o 1º ano demonstra proficiência estruturada e equilíbrio dimensional superior à média regional, mas com pontos específicos de refinamento no sistema decimal:</p>
    
    <table class="data-table">
        <tr>
            <th style="width: 10%;">Código</th>
            <th style="width: 48%;">Habilidade Empírica CAEd</th>
            <th style="width: 14%; text-align:center;">Acerto Turma</th>
            <th style="width: 14%; text-align:center;">Status</th>
            <th>Diretriz de Intervenção Pedagógica</th>
        </tr>
        <tr>
            <td><strong>H01</strong></td>
            <td>Contar coleções de objetos até 10 unidades.</td>
            <td style="text-align:center; font-weight:bold;">100%</td>
            <td style="text-align:center;"><span class="badge badge-green">Pleno</span></td>
            <td>Ampliar contagem até 50 e contagem regressiva.</td>
        </tr>
        <tr>
            <td><strong>H02</strong></td>
            <td>Comparar quantidades de coleções de objetos.</td>
            <td style="text-align:center; font-weight:bold;">78%</td>
            <td style="text-align:center;"><span class="badge badge-yellow">Atenção</span></td>
            <td>Pareamento visual concreto e quantificadores relativos.</td>
        </tr>
        <tr style="background: #ffe4e6;">
            <td><strong>H03</strong></td>
            <td><strong>Comparar números naturais de até dois algarismos.</strong></td>
            <td style="text-align:center; font-weight:bold; color: #be123c;">71%</td>
            <td style="text-align:center;"><span class="badge badge-red">CRÍTICO</span></td>
            <td><strong>Foco Focal: valor posicional decimal, reta numérica e jogos.</strong></td>
        </tr>
        <tr>
            <td><strong>H04</strong></td>
            <td>Resolver problemas aditivos com imagens (juntar/acrescentar).</td>
            <td style="text-align:center; font-weight:bold;">79%</td>
            <td style="text-align:center;"><span class="badge badge-yellow">Atenção</span></td>
            <td>Prática diária de adições com apoio de material manipulável.</td>
        </tr>
        <tr>
            <td><strong>H05</strong></td>
            <td>Resolver problemas subtrativos com imagens (retirar).</td>
            <td style="text-align:center; font-weight:bold;">100%</td>
            <td style="text-align:center;"><span class="badge badge-green">Pleno</span></td>
            <td>Transição da representação pictórica para sentença numérica.</td>
        </tr>
        <tr>
            <td><strong>H06</strong></td>
            <td>Classificar objetos por atributos múltiplos (forma, cor, tamanho).</td>
            <td style="text-align:center; font-weight:bold;">100%</td>
            <td style="text-align:center;"><span class="badge badge-green">Pleno</span></td>
            <td>Introdução a diagramas de classificação e tabelas simples.</td>
        </tr>
        <tr>
            <td><strong>H07</strong></td>
            <td>Identificar regularidades e padrões em sequências figurais.</td>
            <td style="text-align:center; font-weight:bold;">100%</td>
            <td style="text-align:center;"><span class="badge badge-green">Pleno</span></td>
            <td>Sequências numéricas com saltos de 2 em 2 e 5 em 5.</td>
        </tr>
    </table>
    
    <div class="card-warn">
        <strong>Análise Didática da Vulnerabilidade em H03 (71%):</strong>
        <p style="font-size: 7.8pt; margin: 3px 0;">O erro mais comum dos estudantes do 1º ano na comparação de dois algarismos (ex: comparar 21 e 19) decorre da fixação no último dígito ou da falta de compreensão do valor da dezena. O plano de ação adota a decomposição com <strong>fichas sobrepostas e material dourado</strong>, ensinando a comparar primeiro a ordem de maior grandeza.</p>
    </div>
    
    <div class="grid-2">
        <div class="card">
            <strong>Desempenho por Eixo Matemático:</strong>
            <p style="font-size: 7.5pt; margin: 2px 0;">• Geometria e Padrões: <strong>100%</strong> de aproveitamento.<br>
            • Operações Básicas: <strong>89,5%</strong> de aproveitamento médio.<br>
            • Números e Sistema Decimal: <strong>83,0%</strong> de aproveitamento médio.</p>
        </div>
        <div class="card-highlight">
            <strong>Integração com a Rotina 20-60-20:</strong>
            <p style="font-size: 7.5pt; margin: 2px 0;">Os 12 minutos centrais da prática matemática diária são dedicados à rotação entre <strong>H03 (comparação numérica)</strong> e <strong>H04 (adição com suporte visual)</strong>, garantindo domínio estável até o Ciclo III.</p>
        </div>
    </div>
    {make_footer(8)}
</div>
"""
pages_html.append(p8)

# ================= PAGE 9: HABILIDADES PRIORITÁRIAS =================
p9 = f"""
<div class="page-block">
    {make_header(9)}
    <h1 class="section-title">8. Habilidades Prioritárias e Conteúdos do Ciclo III</h1>
    
    <p>A preparação para o Ciclo III exige concentrar esforços na interseção entre: (a) menor acerto no CAEd; (b) peso na matriz do SPAECE/PAIC; e (c) pré-requisito formativo para o 2º ano escolar:</p>
    
    <div class="card">
        <h2 class="sub-title" style="margin-top:0;">Matriz de Prioridade Empírica e Plano de Fortalecimento</h2>
        <table class="data-table">
            <tr>
                <th style="width: 14%;">Componente</th>
                <th style="width: 10%;">Código</th>
                <th style="width: 32%;">Conteúdo a Fortalecer</th>
                <th style="width: 14%; text-align:center;">Acerto Atual</th>
                <th>Estratégia de Ensino Direto</th>
            </tr>
            <tr>
                <td><strong>Língua Portuguesa</strong></td>
                <td><strong>H04</strong></td>
                <td>Localização de dados explícitos em frases e bilhetes curtos.</td>
                <td style="text-align:center; font-weight:bold; color:#be123c;">50%</td>
                <td>Técnica "Procurar e Sublinhar": o professor dita uma pergunta e guia a criança para achar e grifar a palavra-chave no texto.</td>
            </tr>
            <tr>
                <td><strong>Língua Portuguesa</strong></td>
                <td><strong>H07</strong></td>
                <td>Finalidade e suporte de gêneros textuais do cotidiano.</td>
                <td style="text-align:center; font-weight:bold; color:#b45309;">60%</td>
                <td>Varal de gêneros na sala de aula: comparação de função entre convite de aniversário, bilhete de aviso e rótulo de embalagem.</td>
            </tr>
            <tr>
                <td><strong>Língua Portuguesa</strong></td>
                <td><strong>H05</strong></td>
                <td>Identificação do assunto principal e ideia central.</td>
                <td style="text-align:center; font-weight:bold; color:#b45309;">63%</td>
                <td>Leitura compartilhada com fechamento de síntese oral ("Quem é o personagem e o que ele fez de mais importante?").</td>
            </tr>
            <tr>
                <td><strong>Matemática</strong></td>
                <td><strong>H03</strong></td>
                <td>Comparação e ordenação de números até 2 algarismos (0 a 50).</td>
                <td style="text-align:center; font-weight:bold; color:#be123c;">71%</td>
                <td>Jogo "Quem tem mais?": cartas com números de 2 dígitos, representação com canudos em feixes de dez e comparação visual.</td>
            </tr>
            <tr>
                <td><strong>Matemática</strong></td>
                <td><strong>H02</strong></td>
                <td>Comparação de quantidades em coleções heterogêneas.</td>
                <td style="text-align:center; font-weight:bold; color:#b45309;">78%</td>
                <td>Atividades com pares de calçados, botões e formas; uso de termos matemáticos precisos (maior que, menor que, igual).</td>
            </tr>
            <tr>
                <td><strong>Matemática</strong></td>
                <td><strong>H04</strong></td>
                <td>Resolução e elaboração de problemas aditivos simples.</td>
                <td style="text-align:center; font-weight:bold; color:#b45309;">79%</td>
                <td>Uso de caixas organizadoras de somar (juntar objetos de duas caixas menores em uma caixa maior com contagem final).</td>
            </tr>
        </table>
    </div>
    
    <div class="card-highlight">
        <h2 class="sub-title" style="margin-top:0;">Regra de Intervenção Pedagógica Individualizada</h2>
        <p>A turma do 1º ano não deve ser tratada como bloco homogêneo. A intervenção organiza-se rigorosamente pela correspondência nominal:</p>
        <p style="font-size: 7.8pt; margin: 2px 0;">• Estudantes do <strong>Cluster 1A</strong> recebem reforço nas correspondências som-letra (H01, H02 e H06) antes da exigência de localização textual.<br>
        • Estudantes do <strong>Cluster 1C</strong> focam diretamente em H04 e H07, pois já possuem decodificação consolidada.<br>
        • Em matemática, os estudantes com erro em H03 praticam com a reta numérica móvel em sua carteira durante todas as sessões.</p>
    </div>
    {make_footer(9)}
</div>
"""
pages_html.append(p9)

# ================= PAGE 10: ESTATÍSTICA E META DE 80% =================
p10 = f"""
<div class="page-block">
    {make_header(10)}
    <h1 class="section-title">9. Análise Estatística, Contraprova e Meta de 80%</h1>
    
    <p>A gestão baseada em evidências exige rigor biométrico e modelagem probabilística de conversão. A turma de 24 estudantes possui características estatísticas de alta sensibilidade:</p>
    
    <div class="grid-3">
        <div class="kpi-box">
            <div class="kpi-val">4,17 p.p.</div>
            <div class="kpi-lbl">Peso de Cada Aluno</div>
            <p style="font-size: 7pt; color: #475569; margin-top: 2px;">1 aluno = 1/24 = 4,1667% de impacto direto no resultado escolar.</p>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">10 Alunos</div>
            <div class="kpi-lbl">Conversão Necessária LP</div>
            <p style="font-size: 7pt; color: #2563eb; margin-top: 2px;">Para elevar de 41,7% para 83,3% de adequação (+41,6 p.p.).</p>
        </div>
        <div class="kpi-box">
            <div class="kpi-val">9 Alunos</div>
            <div class="kpi-lbl">Conversão Necessária MAT</div>
            <p style="font-size: 7pt; color: #2563eb; margin-top: 2px;">Para elevar de 45,8% para 83,3% de adequação (+37,5 p.p.).</p>
        </div>
    </div>
    
    <h2 class="sub-title">9.1 Análise de Correlação e Discriminância dos Itens</h2>
    <table class="data-table">
        <tr>
            <th>Habilidade</th>
            <th style="text-align:center;">Domínio</th>
            <th style="text-align:center;">Correlação (r) com Adequação</th>
            <th style="text-align:center;">Correlação Item-Total</th>
            <th>Poder Discriminatório e Decisão</th>
        </tr>
        <tr>
            <td><strong>LP - H04</strong></td>
            <td style="text-align:center; font-weight:bold; color:#be123c;">50,0%</td>
            <td style="text-align:center; font-weight:bold;">0,65 (Moderada/Alta)</td>
            <td style="text-align:center;">0,50 (Moderada)</td>
            <td><span class="badge badge-red">Prioridade Crítica</span> - Principal item divisor entre Intermediário e Adequado.</td>
        </tr>
        <tr>
            <td><strong>LP - H07</strong></td>
            <td style="text-align:center; font-weight:bold; color:#b45309;">60,0%</td>
            <td style="text-align:center;">0,58 (Moderada)</td>
            <td style="text-align:center;">0,48 (Moderada)</td>
            <td><span class="badge badge-yellow">Alta Relevância</span> - Sinaliza autonomia leitora além da mera decodificação.</td>
        </tr>
        <tr>
            <td><strong>MAT - H03</strong></td>
            <td style="text-align:center; font-weight:bold; color:#be123c;">71,0%</td>
            <td style="text-align:center; font-weight:bold;">0,61 (Moderada/Alta)</td>
            <td style="text-align:center;">0,54 (Moderada)</td>
            <td><span class="badge badge-red">Prioridade Crítica</span> - Chave para o avanço matemático de 9 estudantes limítrofes.</td>
        </tr>
        <tr>
            <td><strong>MAT - H02</strong></td>
            <td style="text-align:center; font-weight:bold; color:#b45309;">78,0%</td>
            <td style="text-align:center;">0,52 (Moderada)</td>
            <td style="text-align:center;">0,46 (Moderada)</td>
            <td><span class="badge badge-yellow">Média Relevância</span> - Recomposição rápida com material manipulável.</td>
        </tr>
    </table>
    
    <h2 class="sub-title">9.2 Simulação de Cenário What-If para a Meta de 80%</h2>
    <div class="card-highlight">
        <p>A meta municipal de excelência fixa o patamar de <strong>80% de estudantes no padrão Adequado</strong>. A análise nominal identifica o grupo de alta responsividade (estudantes que já acertaram mais de 60% da prova e necessitam apenas de 1 ou 2 itens para atingir a nota de corte):</p>
        <p style="font-size: 7.8pt; margin: 3px 0;">• Em Língua Portuguesa, <strong>7 estudantes do Cluster 1C</strong> (Francisco Miguel, Gustavo Sales, Isac Lucca, Jose Yhudy, Livya Maria, Louise Alves e Sarah Eloyse) somados a <strong>3 estudantes do Cluster 1B</strong> totalizam exatamente os 10 estudantes necessários para alcançar <strong>83,3% de adequação</strong>.<br>
        • Em Matemática, a conversão de 9 estudantes que erraram apenas a comparação de 2 dígitos (H03) eleva a adequação imediata para <strong>83,3%</strong>.</p>
    </div>
    
    <div class="card-warn">
        <strong>Vigilância contra a Ilusão Percentual:</strong> Em uma turma de 24 alunos, a falta ou distração de apenas 2 crianças em dia de avaliação derruba o índice em quase 9 pontos percentuais. Por isso, o plano de monitoramento prevê <strong>contraprovas quinzenais e controle rígido de infrequência</strong>.
    </div>
    {make_footer(10)}
</div>
"""
pages_html.append(p10)

# ================= PAGE 11: CLUSTERS OPERACIONAIS =================
p11 = f"""
<div class="page-block">
    {make_header(11)}
    <h1 class="section-title">10. Clusters Pedagógicos Operacionais do 1º Ano</h1>
    
    <p>Para operacionalizar a intervenção sem sobrecarregar a rotina docente, os 24 estudantes foram organizados em 4 clusters pedagógicos baseados em suas necessidades formativas prioritárias:</p>
    
    <div class="card" style="border-left: 4px solid #be123c;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>Cluster 1A — Base Alfabética e Decodificação Fônica (7 Estudantes)</strong>
            <span class="badge badge-red">Intervenção Intensiva</span>
        </div>
        <p style="font-size: 7.6pt; margin: 2px 0;"><strong>Estudantes:</strong> Daniel Conceição, Gustavo Henrique, Isabella Martins, Isis Ketlen, Maria Agatha, Maria Isis Pereira, Maria Sophia.</p>
        <p style="font-size: 7.4pt; margin: 2px 0; color: #475569;"><strong>Foco Pedagógico:</strong> Consciência fonêmica, isolamento de som, correspondência grafema-fonema, leitura de sílabas canônicas e palavras simples. Dosagem: 5 encontros/semana de 20 min com o professor aplicador.</p>
    </div>
    
    <div class="card" style="border-left: 4px solid #b45309;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>Cluster 1B — Segmentação e Leitura Funcional (4 Estudantes)</strong>
            <span class="badge badge-yellow">Recomposição Focal</span>
        </div>
        <p style="font-size: 7.6pt; margin: 2px 0;"><strong>Estudantes:</strong> Isis Gomes, Maria Juliana, Maria Letícia, Maria Yorrana.</p>
        <p style="font-size: 7.4pt; margin: 2px 0; color: #475569;"><strong>Foco Pedagógico:</strong> Fluência emergente, transição para frases simples, superação de hesitações e correspondências complexas. Dosagem: 4 encontros/semana de 20 min com monitoramento de ritmo.</p>
    </div>
    
    <div class="card" style="border-left: 4px solid #2563eb;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>Cluster 1C — Compreensão e Conversão para a Meta (7 Estudantes)</strong>
            <span class="badge badge-blue">Prática Guiada</span>
        </div>
        <p style="font-size: 7.6pt; margin: 2px 0;"><strong>Estudantes:</strong> Francisco Miguel, Gustavo Sales, Isac Lucca, José Yhudy, Livya Maria, Louise Alves, Sarah Eloyse.</p>
        <p style="font-size: 7.4pt; margin: 2px 0; color: #475569;"><strong>Foco Pedagógico:</strong> Localização textual (H04), inferência direta, leitura expressiva com pontuação e resolução de problemas matemáticos. Dosagem: 3 encontros/semana de 20 min com foco em autonomia.</p>
    </div>
    
    <div class="card" style="border-left: 4px solid #15803d;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <strong>Cluster 1D — Consolidação e Enriquecimento (6 Estudantes)</strong>
            <span class="badge badge-green">Aprofundamento</span>
        </div>
        <p style="font-size: 7.6pt; margin: 2px 0;"><strong>Estudantes:</strong> Antonio Calleby, Emanuelly, Lunna, Maria Isis da Conceição, Moisés, Ruan Lucas.</p>
        <p style="font-size: 7.4pt; margin: 2px 0; color: #475569;"><strong>Foco Pedagógico:</strong> Fluência expressiva (&gt;60 palavras/min), produção escrita de pequenas histórias, desafios de raciocínio lógico e tutoria colaborativa. Dosagem: 2 encontros/semana e tarefas enriquecidas.</p>
    </div>
    
    <div class="card-highlight">
        <strong>Flexibilidade e Mobilidade dos Clusters:</strong> Os agrupamentos são provisórios. A cada 15 dias, a coordenação pedagógica analisa os registros do caderno de práticas e reclassifica os estudantes que atingirem precisão &ge;95% com estabilidade comprovada.
    </div>
    {make_footer(11)}
</div>
"""
pages_html.append(p11)

# ================= PAGE 12: PLANO DE AÇÃO 5 EIXOS =================
p12 = f"""
<div class="page-block">
    {make_header(12)}
    <h1 class="section-title">11. Plano de Ação Pedagógica — 5 Eixos Estratégicos</h1>
    
    <p>O plano de ação do Ciclo III articula intervenções curriculares, didáticas e comunitárias para garantir o salto de qualidade do 1º ano:</p>
    
    <table class="data-table">
        <tr>
            <th style="width: 18%;">Eixo Estratégico</th>
            <th style="width: 35%;">Ações Operacionais Obrigatórias</th>
            <th style="width: 25%;">Indicador de Eficácia</th>
            <th style="width: 14%;">Frequência</th>
        </tr>
        <tr>
            <td><strong>Eixo 1: Consciência Fonológica e Fonêmica</strong></td>
            <td>Treino diário sistemático de 5 minutos com isolamento de sons, rimas e manipulação de fonemas com apoio de fichas táteis e palmas.</td>
            <td>Taxa de acerto em tarefas orais de segmentação (&ge;90%).</td>
            <td><span class="badge badge-blue">Diária</span></td>
        </tr>
        <tr>
            <td><strong>Eixo 2: Fluência e Decodificação Fônica</strong></td>
            <td>Leitura diária do bloco de palavras e frases do caderno; modelagem de entonação pelo professor; leitura assistida e repetida.</td>
            <td>Contagem de palavras lidas por minuto (PPM) e precisão percentual.</td>
            <td><span class="badge badge-blue">Diária</span></td>
        </tr>
        <tr>
            <td><strong>Eixo 3: Escrita e Grafofonêmica</strong></td>
            <td>Ditado fônico curto diário (4 palavras + 1 frase curta); formação de palavras com alfabeto móvel; registro no caderno.</td>
            <td>Percentual de escrita alfabética canônica sem omissão de letras.</td>
            <td><span class="badge badge-blue">Diária</span></td>
        </tr>
        <tr>
            <td><strong>Eixo 4: Raciocínio Lógico-Matemático Kumon</strong></td>
            <td>Sessão estruturada de 20 minutos (20-60-20): contagem, comparação de números até 50 (H03) e cálculo com material concreto.</td>
            <td>Taxa de acerto nas situações-problema semanais (&ge;85%).</td>
            <td><span class="badge badge-blue">Diária</span></td>
        </tr>
        <tr>
            <td><strong>Eixo 5: Gestão, AEE e Engajamento Familiar</strong></td>
            <td>Envio da folha semanal de leitura com assinatura dos pais; reuniões formativas de devolutiva; atendimento articulado na SRM/AEE.</td>
            <td>Devolutiva das folhas assinadas (&ge;90%) e assiduidade dos alunos.</td>
            <td><span class="badge badge-green">Semanal</span></td>
        </tr>
    </table>
    
    <div class="grid-2">
        <div class="card">
            <strong>Compromisso de Monitoramento Semanal:</strong>
            <p style="font-size: 7.5pt; margin: 2px 0;">Toda sexta-feira o professor preenche a <strong>Grade de Registro Docente</strong> presente no caderno individual de cada estudante, anotando a precisão percentual e rubricando as decisões tomadas.</p>
        </div>
        <div class="card-warn">
            <strong>Protocolo de Busca Ativa Pedagógica:</strong>
            <p style="font-size: 7.5pt; margin: 2px 0;">Estudante que faltar a 2 dias de prática na mesma semana recebe reposição imediata de fichas cumulativas na segunda-feira subsequente na Estação de Apoio.</p>
        </div>
    </div>
    {make_footer(12)}
</div>
"""
pages_html.append(p12)

# ================= PAGE 13: ROTAÇÃO POR ESTAÇÕES =================
p13 = f"""
<div class="page-block">
    {make_header(13)}
    <h1 class="section-title">12. Arquitetura de Rotação por Estações Pedagógicas</h1>
    
    <p>Para conciliar o ensino intensivo dos clusters mais defasados sem estagnar os estudantes avançados, a sala de aula do 1º ano adota o modelo de <strong>Rotação por 4 Estações de Aprendizagem Ativa</strong> (sessões de 20 minutos por estação, com circulação rotativa):</p>
    
    <div class="grid-2">
        <div class="card-highlight" style="border-top: 3px solid #be123c;">
            <div style="display:flex; justify-content:space-between;">
                <strong>Estação 1: Ensino Direto com o Professor</strong>
                <span class="badge badge-red">Mediação Fônica</span>
            </div>
            <p style="font-size: 7.5pt; margin: 4px 0;"><strong>Público Prioritário:</strong> Clusters 1A e 1B (atendimento direto em mesa redonda).</p>
            <p style="font-size: 7.3pt; margin: 2px 0; color: #334155;"><strong>Dinâmica:</strong> O professor modela o som da letra, guia a fusão fonêmica, faz o espelhamento articulatório na boca e monitora a leitura em voz alta palavra por palavra. Reensino explícito com correção imediata.</p>
        </div>
        
        <div class="card-highlight" style="border-top: 3px solid #2563eb;">
            <div style="display:flex; justify-content:space-between;">
                <strong>Estação 2: Prática Deliberada Kumon</strong>
                <span class="badge badge-blue">Caderno de Práticas</span>
            </div>
            <p style="font-size: 7.5pt; margin: 4px 0;"><strong>Público:</strong> Todos os clusters em turnos alternados.</p>
            <p style="font-size: 7.3pt; margin: 2px 0; color: #334155;"><strong>Dinâmica:</strong> Resolução autônoma das folhas diárias do Dossiê Integrado (Dias 1 a 4). Aplicação da regra 20-60-20: revisão, treino da habilidade do dia e desafio final. Checagem por gabarito e autocorreção assistida.</p>
        </div>
        
        <div class="card-highlight" style="border-top: 3px solid #b45309;">
            <div style="display:flex; justify-content:space-between;">
                <strong>Estação 3: Jogos Matemáticos & Manipuláveis</strong>
                <span class="badge badge-yellow">Laboratório Concreto</span>
            </div>
            <p style="font-size: 7.5pt; margin: 4px 0;"><strong>Recursos:</strong> Material dourado, tampinhas, reta numérica e ábaco.</p>
            <p style="font-size: 7.3pt; margin: 2px 0; color: #334155;"><strong>Dinâmica:</strong> Jogos de comparação numérica (H03), batalha das dezenas, agrupamentos de 10 em 10 e resolução de desafios aditivos/subtrativos concretos em pequenos grupos colaborativos.</p>
        </div>
        
        <div class="card-highlight" style="border-top: 3px solid #15803d;">
            <div style="display:flex; justify-content:space-between;">
                <strong>Estação 4: Produção Guiada & Registro Autônomo</strong>
                <span class="badge badge-green">Escrita & Expressão</span>
            </div>
            <p style="font-size: 7.5pt; margin: 4px 0;"><strong>Recursos:</strong> Letras móveis, pranchas ilustradas e caderno de escrita.</p>
            <p style="font-size: 7.3pt; margin: 2px 0; color: #334155;"><strong>Dinâmica:</strong> Montagem de palavras reais ditadas pelo colega tutor, cópia com sentido de pequenas frases, desenho representativo do texto lido e escrita de bilhetes funcionais do cotidiano escolar.</p>
        </div>
    </div>
    
    <h2 class="sub-title">12.1 Fluxo de Circulação e Gestão da Sala</h2>
    <div class="card">
        <p style="font-size: 7.8pt; margin: 2px 0;">• A cada 20 minutos, um sinal sonoro suave indica a rotação de estação.<br>
        • Os estudantes do <strong>Cluster 1A</strong> passam obrigatoriamente 2 tempos na Estação 1 (Ensino Direto) e 1 tempo na Estação 2 (Prática Kumon).<br>
        • Os estudantes do <strong>Cluster 1D</strong> atuam como monitores solidários na Estação 3 e 4, aprofundando o próprio domínio ao ensinar os colegas (Efeito Protegido de Tutoria).</p>
    </div>
    {make_footer(13)}
</div>
"""
pages_html.append(p13)

# ================= PAGE 14: GESTÃO POR EVIDÊNCIAS =================
p14 = f"""
<div class="page-block">
    {make_header(14)}
    <h1 class="section-title">13. Gestão por Evidências, Monitoramento e Cadência</h1>
    
    <p>O sucesso da metodologia assenta-se na cadência regular de registro e tomada de decisão fundamentada em dados empíricos:</p>
    
    <table class="data-table">
        <tr>
            <th style="width: 14%;">Cadência</th>
            <th style="width: 28%;">Instrumento de Coleta</th>
            <th style="width: 38%;">Evidência Analisada</th>
            <th style="width: 20%;">Responsável</th>
        </tr>
        <tr>
            <td><strong>Diária</strong></td>
            <td>Folha de Prática do Dossiê</td>
            <td>Precisão percentual do dia, tempo gasto na tarefa, tipo de erro fonético (omissão/troca) e nível de ajuda exigido.</td>
            <td>Professor Aplicador</td>
        </tr>
        <tr>
            <td><strong>Semanal</strong></td>
            <td>Miniavaliação de Fluência (Dia 5)</td>
            <td>Palavras lidas por minuto (PPM), escala de prosódia (1 a 4) e acerto na pergunta de compreensão literal (H04).</td>
            <td>Professor + Coordenador</td>
        </tr>
        <tr>
            <td><strong>Quinzenal</strong></td>
            <td>Matriz de Reclassificação</td>
            <td>Análise nominal de estabilidade (&ge;95% de precisão) para promoção de cluster e ajuste de rotação das estações.</td>
            <td>Coordenação Pedagógica</td>
        </tr>
        <tr>
            <td><strong>Mensal</strong></td>
            <td>Painel Censitário Escolar</td>
            <td>Indicadores globais de frequência, índice de conversão de leitores, evolução matemática e alinhamento com a meta de 80%.</td>
            <td>Núcleo Gestor e Secretaria</td>
        </tr>
    </table>
    
    <h2 class="sub-title">13.1 Régua Operacional de Decisão Formativa</h2>
    <div class="grid-3">
        <div class="card-alert" style="text-align:center;">
            <div style="font-size:11pt; font-weight:900; color:#9f1239;">&lt; 85% Precisão</div>
            <div style="font-weight:700; margin: 3px 0; color:#be123c;">Reensino Explícito</div>
            <p style="font-size:7.2pt; color:#475569;">O estudante repete o padrão fonêmico com mediação direta do professor na Estação 1; proibido avançar conteúdo.</p>
        </div>
        <div class="card-warn" style="text-align:center;">
            <div style="font-size:11pt; font-weight:900; color:#854d0e;">85% a 94% Precisão</div>
            <div style="font-weight:700; margin: 3px 0; color:#b45309;">Prática Guiada</div>
            <p style="font-size:7.2pt; color:#475569;">O estudante mantém o bloco de tarefas cumulativas com checagem de erros pelo gabarito e apoio de tutor.</p>
        </div>
        <div class="card-highlight" style="text-align:center;">
            <div style="font-size:11pt; font-weight:900; color:#15803d;">&ge; 95% Precisão</div>
            <div style="font-weight:700; margin: 3px 0; color:#16a34a;">Consolidação e Avanço</div>
            <p style="font-size:7.2pt; color:#475569;">Após 2 semanas consecutivas neste patamar com compreensão &ge;80%, o estudante é promovido ao próximo cluster.</p>
        </div>
    </div>
    
    <div class="card">
        <strong>Auditoria de Integridade dos Dados:</strong> Não se admite preenchimento retrospectivo ou estimativo das grades de registro. Toda anotação deve ser contemporânea à aplicação da atividade, assegurando validade jurídica e técnica ao dossiê escolar.
    </div>
    {make_footer(14)}
</div>
"""
pages_html.append(p14)

# ================= PAGE 15: ANEXO NOMINAL PARTE 1 =================
p15_rows = ""
for i, r in merged.iloc[:12].iterrows():
    std_name = r['Estudante']
    lp_lvl = r[col_lp_niv + '_LP']
    mat_lvl = r[col_mat_niv + '_MAT']
    c_code, c_desc, frag_lp, frag_mat = clusters_info.get(std_name, ("1C", "Compreensão", "-", "-"))
    
    badge_lp = "badge-blue" if lp_lvl == "Adequado" else "badge-yellow"
    badge_mat = "badge-blue" if mat_lvl == "Adequado" else "badge-yellow"
    badge_cl = "badge-red" if c_code == "1A" else ("badge-yellow" if c_code == "1B" else ("badge-blue" if c_code == "1C" else "badge-green"))
    
    p15_rows += f"""
    <tr>
        <td style="font-weight:700;">{std_name}</td>
        <td><span class="badge {badge_lp}">{lp_lvl}</span></td>
        <td><span class="badge {badge_mat}">{mat_lvl}</span></td>
        <td style="font-size:7pt; color:#be123c;">{frag_lp}</td>
        <td style="font-size:7pt; color:#b45309;">{frag_mat}</td>
        <td><span class="badge {badge_cl}">{c_code}</span></td>
    </tr>
    """

p15 = f"""
<div class="page-block">
    {make_header(15)}
    <h1 class="section-title">14. Anexo Nominal Operacional — Perfil Integrado (Parte 1)</h1>
    
    <p>Quadro analítico individualizado integrando os resultados oficiais CAEd (Língua Portuguesa e Matemática), mapeamento de fragilidades diagnósticas e alocação no cluster de intervenção (Estudantes 1 a 12):</p>
    
    <table class="data-table">
        <tr>
            <th style="width: 32%;">Estudante</th>
            <th style="width: 13%;">Nível LP</th>
            <th style="width: 13%;">Nível MAT</th>
            <th style="width: 18%;">Fragilidades LP</th>
            <th style="width: 14%;">Fragilidades MAT</th>
            <th style="width: 10%;">Cluster</th>
        </tr>
        {p15_rows}
    </table>
    
    <div class="card-highlight">
        <strong>Orientações de Atendimento (Estudantes 1 a 12):</strong>
        <p style="font-size:7.5pt; margin: 2px 0;">• <strong>Daniel Conceição, Gustavo Henrique e Isabella Martins (Cluster 1A):</strong> Apresentam zeramento em H04 e necessitam de reensino sistemático de correspondências grafofonêmicas básicas antes da exigência de leitura de frases longas.<br>
        • <strong>Antonio Calleby e Emanuelly (Cluster 1D):</strong> Desempenho pleno na decodificação; foco estrito em inferência de finalidade e problemas de adição sem suporte de imagem.</p>
    </div>
    {make_footer(15)}
</div>
"""
pages_html.append(p15)

# ================= PAGE 16: ANEXO NOMINAL PARTE 2 =================
p16_rows = ""
for i, r in merged.iloc[12:].iterrows():
    std_name = r['Estudante']
    lp_lvl = r[col_lp_niv + '_LP']
    mat_lvl = r[col_mat_niv + '_MAT']
    c_code, c_desc, frag_lp, frag_mat = clusters_info.get(std_name, ("1C", "Compreensão", "-", "-"))
    
    badge_lp = "badge-blue" if lp_lvl == "Adequado" else "badge-yellow"
    badge_mat = "badge-blue" if mat_lvl == "Adequado" else "badge-yellow"
    badge_cl = "badge-red" if c_code == "1A" else ("badge-yellow" if c_code == "1B" else ("badge-blue" if c_code == "1C" else "badge-green"))
    
    p16_rows += f"""
    <tr>
        <td style="font-weight:700;">{std_name}</td>
        <td><span class="badge {badge_lp}">{lp_lvl}</span></td>
        <td><span class="badge {badge_mat}">{mat_lvl}</span></td>
        <td style="font-size:7pt; color:#be123c;">{frag_lp}</td>
        <td style="font-size:7pt; color:#b45309;">{frag_mat}</td>
        <td><span class="badge {badge_cl}">{c_code}</span></td>
    </tr>
    """

p16 = f"""
<div class="page-block">
    {make_header(16)}
    <h1 class="section-title">14. Anexo Nominal Operacional — Perfil Integrado (Parte 2)</h1>
    
    <p>Quadro analítico individualizado integrando os resultados oficiais CAEd (Língua Portuguesa e Matemática), mapeamento de fragilidades diagnósticas e alocação no cluster de intervenção (Estudantes 13 a 24):</p>
    
    <table class="data-table">
        <tr>
            <th style="width: 32%;">Estudante</th>
            <th style="width: 13%;">Nível LP</th>
            <th style="width: 13%;">Nível MAT</th>
            <th style="width: 18%;">Fragilidades LP</th>
            <th style="width: 14%;">Fragilidades MAT</th>
            <th style="width: 10%;">Cluster</th>
        </tr>
        {p16_rows}
    </table>
    
    <div class="card-highlight">
        <strong>Orientações de Atendimento (Estudantes 13 a 24):</strong>
        <p style="font-size:7.5pt; margin: 2px 0;">• <strong>Maria Agatha, Maria Isis Pereira e Maria Sophia (Cluster 1A):</strong> Fragilidade severa na rota de decodificação; prioridade absoluta no treino auditivo e formação de palavras simples com letras móveis.<br>
        • <strong>Moisés Toledo e Ruan Lucas (Cluster 1D):</strong> Adequação simultânea em Língua Portuguesa e Matemática; recebem atividades de enriquecimento com textos informativos e desafios de raciocínio lógico multiplicativo inicial.</p>
    </div>
    {make_footer(16)}
</div>
"""
pages_html.append(p16)

# ================= PAGE 17: NOTAS METODOLÓGICAS =================
p17 = f"""
<div class="page-block">
    {make_header(17)}
    <h1 class="section-title">15. Notas Metodológicas, Fontes e Fundamentação</h1>
    
    <p>Este Dossiê Pedagógico Integrado constitui um instrumento técnico de gestão escolar e intervenção clínica-educacional fundamentado nas seguintes bases normativas e teóricas:</p>
    
    <div class="card">
        <h2 class="sub-title" style="margin-top:0;">Fontes de Dados e Instrumentos Diagnósticos Oficiais</h2>
        <ul style="margin: 3px 0 3px 18px; padding: 0; font-size: 7.8pt;">
            <li><strong>CAEd Ciclo I (2026):</strong> Microdados oficiais exportados em 22/10/2026 contendo resultados censitários de desempenho por estudante, turma e escola em Língua Portuguesa e Matemática da Escola Municipal de Cidadania Airam Veras (INEP 23084995).</li>
            <li><strong>SAAP / Diagnóstico de Leitura Municipal:</strong> Linha de base da proficiência leitora do município de Crateús/CE, atestando a classificação inicial em Não Leitores (NL), Leitores de Sílabas (LS), Leitores de Palavras (LP) e Leitores de Frases/Textos.</li>
            <li><strong>Censo Escolar e Sistema de Matrícula:</strong> Validação cadastral da turma de 1º ano com exatamente 24 estudantes matriculados e efetivamente frequentes.</li>
        </ul>
    </div>
    
    <div class="card">
        <h2 class="sub-title" style="margin-top:0;">Fundamentação Científica e Cognitiva</h2>
        <ul style="margin: 3px 0 3px 18px; padding: 0; font-size: 7.8pt;">
            <li><strong>Ciência da Leitura e Modelo da Corda de Scarborough (2001):</strong> A alfabetização resulta do entrelaçamento entre o reconhecimento automatizado de palavras (consciência fonêmica, decodificação, ortografia) e a compreensão da linguagem (vocabulário, sintaxe, inferência).</li>
            <li><strong>Teoria da Carga Cognitiva de John Sweller:</strong> A memória de trabalho infantil é limitada. Práticas diárias curtas, estruturadas e com mínima distração visual garantem a transferência de padrões para a memória de longo prazo.</li>
            <li><strong>Prática Deliberada e Regra Kumon de Sobreaprendizagem:</strong> A repetição cumulativa e a autocorreção imediata impedem a fossilização de erros ortográficos e conceituais na infância.</li>
            <li><strong>Modelo dos Três Anéis de Joseph Renzulli:</strong> Identificação e enriquecimento curricular para potenciais em altas habilidades, prevenindo desinteresse escolar.</li>
        </ul>
    </div>
    
    <div class="card-warn">
        <strong>Termo de Confidencialidade e Guarda Ética (LGPD / Marco Legal da Primeira Infância):</strong>
        <p style="font-size: 7.3pt; margin: 2px 0;">Este dossiê contém dados nominativos e indicadores individuais de desempenho infantil. É vedada sua veiculação pública, compartilhamento em redes abertas ou reprodução externa desautorizada. O acesso restringe-se aos educadores responsáveis pela turma, equipe multiprofissional do AEE e órgãos de supervisão pedagógica municipal.</p>
    </div>
    {make_footer(17)}
</div>
"""
pages_html.append(p17)

# ================= PAGE 18: ÍNDICE NOMINAL REMISSIVO =================
p18_table = ""
for std in sorted(clusters_info.keys()):
    c_code, c_desc, _, _ = clusters_info[std]
    p_start = student_pages[std]
    p_end = p_start + 25
    badge_cl = "badge-red" if c_code == "1A" else ("badge-yellow" if c_code == "1B" else ("badge-blue" if c_code == "1C" else "badge-green"))
    
    p18_table += f"""
    <tr>
        <td style="font-weight:700;">{std}</td>
        <td style="text-align:center;"><span class="badge {badge_cl}">{c_code}</span></td>
        <td style="font-size:7.2pt; color:#475569;">{c_desc}</td>
        <td style="text-align:center; font-weight:bold; color:#1e3a8a;">Página {p_start}</td>
        <td style="text-align:center; font-size:7.2pt; color:#64748b;">Páginas {p_start} a {p_end} (26 laudas)</td>
    </tr>
    """

p18 = f"""
<div class="page-block">
    {make_header(18)}
    <h1 class="section-title">16. Índice Remissivo Nominal das Fichas Individuais</h1>
    
    <p>Localizador oficial de cada estudante no <strong>Caderno de Práticas Diárias Individualizadas</strong>. Cada estudante possui exatamente <strong>26 laudas dedicadas</strong> (Capa individual, perfil diagnóstico/modo de aplicação e 8 semanas completas de atividades estruturadas):</p>
    
    <table class="data-table">
        <tr>
            <th style="width: 34%;">Nome Completo do Estudante</th>
            <th style="width: 10%; text-align:center;">Cluster</th>
            <th style="width: 24%;">Perfil Pedagógico</th>
            <th style="width: 14%; text-align:center;">Início Ficha</th>
            <th style="width: 18%; text-align:center;">Bloco Individual</th>
        </tr>
        {p18_table}
    </table>
    
    <div class="card-highlight" style="margin-top: 5px;">
        <strong>Estrutura Interna de Cada Caderno Individual (26 Laudas por Aluno):</strong>
        <p style="font-size: 7.3pt; margin: 2px 0;">• <strong>Lauda 1:</strong> Capa de Práticas Diárias com cluster, dosagem e matriz individual de habilidades.<br>
        • <strong>Lauda 2:</strong> Perfil individual, fragilidades diagnósticas CAEd, critérios de saída e orientações clínicas.<br>
        • <strong>Laudas 3 a 26:</strong> 8 Semanas estruturadas (3 laudas por semana: Dias 1 e 2 na lauda 1; Dias 3 e 4 na lauda 2; Dia 5 com Miniavaliação de Fluência e Grade de Registro Docente na lauda 3).</p>
    </div>
    {make_footer(18)}
</div>
"""
pages_html.append(p18)

# Gerar arquivo HTML completo
full_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Dossiê Pedagógico Integrado 1º Ano - Escola Airam Veras</title>
    <style>
        {css}
    </style>
</head>
<body>
    {''.join(pages_html)}
</body>
</html>
"""

with open(HTML_OUT, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f"HTML do Front Matter gerado em: {HTML_OUT}")

# Compilação para PDF via Headless Edge / Chrome
browser_exec = None
for p in [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
          r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
          r"C:\Program Files\Google\Chrome\Application\chrome.exe"]:
    if os.path.exists(p):
        browser_exec = p
        break

if not browser_exec:
    raise RuntimeError("Nenhum navegador Chromium/Edge encontrado para renderização.")

html_uri = pathlib.Path(HTML_OUT).resolve().as_uri()
cmd = [
    browser_exec,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={PDF_FRONT_OUT}",
    html_uri
]

print("Compilando Front Matter via Edge/Chrome headless...")
res = subprocess.run(cmd, capture_output=True, text=True)
if res.returncode != 0:
    print("Erro na compilação:", res.stderr)
    sys.exit(1)

print(f"Front Matter compilado com sucesso em: {PDF_FRONT_OUT}")

# Verificar páginas do Front Matter
r_front = PdfReader(PDF_FRONT_OUT)
print(f"Total de páginas no Front Matter compilado: {len(r_front.pages)}")

# Extrair páginas dos estudantes do F1 (páginas 53 a 676 inclusive, 0-indexadas)
print("Extraindo 624 páginas dos 24 estudantes do 1º Ano de F1...")
r_f1 = PdfReader(F1_PATH)

writer = PdfWriter()

# 1. Adicionar as 18 páginas do Front Matter
for p in r_front.pages:
    writer.add_page(p)

# 2. Adicionar as 624 páginas dos alunos
for idx in range(53, 677):
    writer.add_page(r_f1.pages[idx])

total_final = len(writer.pages)
print(f"Total de páginas a serem gravadas no PDF Integrado: {total_final}")

with open(PDF_FINAL_OUT, "wb") as f_out:
    writer.write(f_out)

print(f"PDF FINAL INTEGRADO CONCLUÍDO COM SUCESSO:")
print(f"-> {PDF_FINAL_OUT}")
print(f"-> Tamanho do arquivo: {os.path.getsize(PDF_FINAL_OUT) / (1024*1024):.2f} MB")
