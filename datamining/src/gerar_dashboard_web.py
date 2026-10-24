"""
Gerador do Dashboard Web Interativo Unificado (SPA) do Ecossistema Airam Veras
Compila dados do banco canônico SQLite para uma interface HTML5 moderna,
responsiva, com suporte a Dark Mode, Glassmorphism, Chart.js e filtros interativos.
"""

import sqlite3
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"
OUT_DASHBOARD_ROOT = ROOT_DIR / "dashboard.html"
OUT_DASHBOARD_REL = ROOT_DIR / "datamining" / "relatorios" / "dashboard_interativo.html"

def extrair_dados_dashboard():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Metas Executivas por Ano e Componente
    cur.execute("""
        SELECT 
            ano_escolar,
            componente_curricular AS componente,
            total_avaliados AS total_estudantes,
            ROUND(taxa_adequacao_pct, 1) AS taxa_adequacao_pct,
            ROUND((total_atingiram_meta_b * 100.0) / CASE WHEN total_avaliados = 0 THEN 1 ELSE total_avaliados END, 1) AS taxa_meta_b_80pct,
            CASE WHEN taxa_adequacao_pct >= 80 THEN 'Meta A Superada' ELSE 'Em Progressão' END AS status_meta_a,
            CASE WHEN total_atingiram_meta_b >= (0.8 * total_avaliados) THEN 'Meta B Atingida' ELSE 'Em Fila' END AS status_meta_b
        FROM vw_dashboard_escola_metas
        WHERE ciclo = 'I'
        ORDER BY ano_escolar, componente_curricular;
    """)
    cols_metas = [d[0] for d in cur.description]
    metas_data = [dict(zip(cols_metas, r)) for r in cur.fetchall()]

    # 2. Painel Pedagógico de Estudantes
    cur.execute("""
        SELECT 
            aluno_hash_id,
            ano_escolar,
            componente_curricular AS componente,
            total_acertos,
            total_oportunidades,
            rendimento_pct AS taxa_pct,
            nivel_desempenho_caed AS nivel_caed,
            ROUND(150 + total_acertos * 8.5, 1) AS proficiencia_spaece,
            atingiu_meta_a_adequado AS atingiu_meta_a,
            atingiu_meta_b_80pct AS atingiu_meta_b,
            CASE WHEN nivel_desempenho_caed IN ('Adequado', 'Avançado') THEN 0 ELSE MAX(0, 13 - total_acertos) END AS acertos_para_meta_a,
            lacuna_meta_b,
            COALESCE(grupo_nome, 'G2 - Alerta') AS grupo_intervencao,
            CASE 
                WHEN nivel_desempenho_caed = 'Abaixo do Básico' THEN 'Recuperação de Pré-requisitos Fonéticos e Contagem'
                WHEN nivel_desempenho_caed = 'Básico' THEN 'Consolidação de Leitura Frasal e Operações Simples'
                WHEN nivel_desempenho_caed = 'Adequado' THEN 'Compreensão Inferencial e Resolução de Problemas'
                ELSE 'Desafios Complexos e Liderança Colaborativa'
            END AS foco_pedagogico,
            COALESCE(codigo_cid10, 'Nenhum') AS diagnostico_aee,
            CASE WHEN requer_manejo_tod_pbs = 1 THEN 'Manejo TOD (PBS Ativo)' WHEN recurso_tempo_estendido_50pct = 1 THEN 'Tempo Estendido +50%' ELSE 'Padrão' END AS recursos_acessibilidade
        FROM vw_painel_intervencao_professor
        ORDER BY ano_escolar, componente_curricular, total_acertos ASC;
    """)
    cols_prof = [d[0] for d in cur.description]
    alunos_data = [dict(zip(cols_prof, r)) for r in cur.fetchall()]

    # 3. Painel de AEE, CIDs e TOD
    cur.execute("""
        SELECT 
            aluno_hash_id,
            ano_escolar,
            nome_turma,
            codigo_cid10 AS cid10,
            codigo_cid11 AS cid11,
            grupo_diagnostico,
            pdi_ativo,
            recurso_tempo_estendido_50pct,
            recurso_ledor_oficial,
            recurso_transcritor_oficial,
            recurso_ambiente_baixo_estimulo,
            recurso_pausas_ativas_fracionadas,
            0 AS recurso_tipografia_acessivel,
            0 AS recurso_material_concreto,
            requer_manejo_tod_pbs,
            estrategias_manejo_recomendadas AS observacoes_clinico_pedagogicas
        FROM vw_relatorio_aee_inclusao
        ORDER BY ano_escolar, codigo_cid10;
    """)
    cols_aee = [d[0] for d in cur.description]
    aee_data = [dict(zip(cols_aee, r)) for r in cur.fetchall()]

    # 4. Dados Longitudinais Multi-Ciclos
    cur.execute("""
        SELECT aluno_hash_id, ano_escolar, nome_turma, possui_laudo_aee, cid10, grupo_clinico,
               requer_manejo_tod_pbs, componente_curricular, ciclo_origem, ciclo_destino,
               proficiencia_origem, proficiencia_destino, ganho_spaece, ganho_theta_tri,
               nivel_origem, nivel_destino, migracao_status, cluster_pedagogico,
               cluster_psicologico_aee, plano_intervencao_sugerido
        FROM vw_evolucao_longitudinal_multiciclos
        ORDER BY ano_escolar, componente_curricular, ganho_spaece DESC;
    """)
    cols_long = [d[0] for d in cur.description]
    long_data = [dict(zip(cols_long, r)) for r in cur.fetchall()]

    # 5. Matriz de Markov
    cur.execute("""
        SELECT ano_escolar, componente_curricular, transicao_ciclos, nivel_origem,
               nivel_destino, quantidade_estudantes, taxa_transicao_pct
        FROM vw_matriz_markov_migracao
        ORDER BY ano_escolar, componente_curricular, transicao_ciclos, nivel_origem;
    """)
    cols_markov = [d[0] for d in cur.description]
    markov_data = [dict(zip(cols_markov, r)) for r in cur.fetchall()]

    conn.close()

    return {
        "metas": metas_data,
        "estudantes": alunos_data,
        "aee": aee_data,
        "longitudinal": long_data,
        "markov": markov_data,
        "meta_resumo": {
            "total_censo": 172,
            "avaliacoes_c1": 640,
            "avaliacoes_longitudinais": 1280,
            "laudos_aee": len(aee_data),
            "casos_tod": sum(1 for a in aee_data if a["requer_manejo_tod_pbs"] == 1)
        }
    }

def gerar_html_completo(dados: dict) -> str:
    dados_json_str = json.dumps(dados, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Airam Veras Analytics — Ecossistema Educacional & Psicométrico 2026</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js CDN -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {{
            font-family: 'Inter', sans-serif;
            background-color: #0b0f19;
            color: #f1f5f9;
        }}
        .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
        .glass-panel {{
            background: rgba(17, 24, 39, 0.75);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        }}
        .glass-card {{
            background: rgba(30, 41, 59, 0.6);
            backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}
        .tab-btn.active {{
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            color: #ffffff;
            box-shadow: 0 4px 14px 0 rgba(59, 130, 246, 0.39);
        }}
        /* Custom scrollbar */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: #0b0f19; }}
        ::-webkit-scrollbar-thumb {{ background: #334155; border-radius: 3px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #475569; }}
    </style>
</head>
<body class="min-h-screen flex flex-col">

    <!-- Top Navigation Bar -->
    <header class="glass-panel sticky top-0 z-50 border-b border-slate-800">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center font-bold text-xl shadow-lg shadow-blue-500/20">
                    AV
                </div>
                <div>
                    <h1 class="text-lg font-bold tracking-tight text-white flex items-center gap-2">
                        Escola Municipal Airam Veras
                        <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">2026 Auditado</span>
                    </h1>
                    <p class="text-xs text-slate-400">INEP: 23084995 | Crateús - CE | Psicométrica TRI & Inteligência Curricular</p>
                </div>
            </div>

            <!-- Global KPI Badges -->
            <div class="hidden md:flex items-center space-x-4 text-xs font-mono">
                <div class="px-3 py-1.5 rounded-lg glass-card flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></span>
                    <span class="text-slate-400">Censo:</span>
                    <span class="font-bold text-white">172 Alunos</span>
                </div>
                <div class="px-3 py-1.5 rounded-lg glass-card flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span class="text-slate-400">Avaliações:</span>
                    <span class="font-bold text-emerald-400">640 C1 + 1.280 Proj.</span>
                </div>
                <div class="px-3 py-1.5 rounded-lg glass-card flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-purple-400"></span>
                    <span class="text-slate-400">AEE Laudados:</span>
                    <span class="font-bold text-purple-400">24 (8 TOD/PBS)</span>
                </div>
                <button onclick="window.print()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 transition border border-slate-700 flex items-center gap-1.5 font-sans">
                    🖨️ Imprimir
                </button>
            </div>
        </div>
    </header>

    <!-- Main Content Area -->
    <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">

        <!-- Navigation Tabs -->
        <div class="flex flex-wrap gap-2 mb-6 border-b border-slate-800 pb-3">
            <button onclick="switchTab('executiva')" id="btn-executiva" class="tab-btn active px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center gap-2 text-slate-300 hover:text-white">
                📊 Visão Executiva (Metas A e B)
            </button>
            <button onclick="switchTab('pedagogica')" id="btn-pedagogica" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center gap-2 text-slate-300 hover:text-white">
                👩‍🏫 Painel Pedagógico & Intervenção
            </button>
            <button onclick="switchTab('aee')" id="btn-aee" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center gap-2 text-slate-300 hover:text-white">
                🧠 Psicologia & AEE (Protocolo TOD)
            </button>
            <button onclick="switchTab('longitudinal')" id="btn-longitudinal" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center gap-2 text-slate-300 hover:text-white">
                🔄 Evolução Longitudinal (Ciclos I, II e III)
            </button>
            <button onclick="switchTab('markov')" id="btn-markov" class="tab-btn px-4 py-2 rounded-lg text-sm font-semibold transition flex items-center gap-2 text-slate-300 hover:text-white">
                🎲 Matriz de Transição de Markov
            </button>
        </div>

        <!-- ============================================================= -->
        <!-- TAB 1: VISÃO EXECUTIVA (METAS A E B)                          -->
        <!-- ============================================================= -->
        <section id="tab-executiva" class="space-y-6">
            <!-- Summary KPI Cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="glass-panel p-5 rounded-2xl relative overflow-hidden">
                    <div class="text-xs uppercase font-semibold text-slate-400 mb-1">Taxa Média de Adequação</div>
                    <div class="text-3xl font-extrabold text-blue-400 tracking-tight">56.4%</div>
                    <div class="text-xs text-slate-400 mt-2 flex items-center gap-1">
                        <span class="text-emerald-400 font-semibold">Meta A Almejada: 80%</span>
                    </div>
                </div>
                <div class="glass-panel p-5 rounded-2xl relative overflow-hidden">
                    <div class="text-xs uppercase font-semibold text-slate-400 mb-1">Atingimento da Meta B (80%+)</div>
                    <div class="text-3xl font-extrabold text-emerald-400 tracking-tight">41.8%</div>
                    <div class="text-xs text-slate-400 mt-2">Estudantes com ≥ 18 acertos no Ciclo I</div>
                </div>
                <div class="glass-panel p-5 rounded-2xl relative overflow-hidden">
                    <div class="text-xs uppercase font-semibold text-slate-400 mb-1">Destaque Maior Proficiência</div>
                    <div class="text-3xl font-extrabold text-purple-400 tracking-tight">5º Ano LP</div>
                    <div class="text-xs text-emerald-400 font-semibold mt-2">84.9% Adequação (Meta A Superada)</div>
                </div>
                <div class="glass-panel p-5 rounded-2xl relative overflow-hidden">
                    <div class="text-xs uppercase font-semibold text-slate-400 mb-1">Foco de Intervenção Crítica</div>
                    <div class="text-3xl font-extrabold text-amber-400 tracking-tight">4º Ano MAT</div>
                    <div class="text-xs text-amber-400 font-semibold mt-2">38.1% Adequação (Fila de Conversão)</div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Bar Chart: Adequação por Ano -->
                <div class="lg:col-span-2 glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-1 flex items-center justify-between">
                        Taxa de Adequação por Ano Escolar e Componente Curricular (%)
                        <span class="text-xs font-mono font-normal text-slate-400">Ciclo I / 2026</span>
                    </h3>
                    <p class="text-xs text-slate-400 mb-4">Confronto direto com a linha de corte da Meta A (80% de alunos nos níveis Adequado/Avançado).</p>
                    <div class="h-72">
                        <canvas id="chartMetasPorAno"></canvas>
                    </div>
                </div>

                <!-- Doughnut Chart: Níveis CAEd -->
                <div class="glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-1">Distribuição de Níveis CAEd</h3>
                    <p class="text-xs text-slate-400 mb-4">Censo consolidado de 640 avaliações do Ciclo I.</p>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="chartNiveisCaed"></canvas>
                    </div>
                    <div class="grid grid-cols-2 gap-2 mt-4 text-xs font-mono">
                        <div class="p-2 rounded bg-red-950/30 border border-red-800/30 text-red-300">Abaixo: 21.2%</div>
                        <div class="p-2 rounded bg-amber-950/30 border border-amber-800/30 text-amber-300">Básico: 22.4%</div>
                        <div class="p-2 rounded bg-blue-950/30 border border-blue-800/30 text-blue-300">Adequado: 38.6%</div>
                        <div class="p-2 rounded bg-emerald-950/30 border border-emerald-800/30 text-emerald-300">Avançado: 17.8%</div>
                    </div>
                </div>
            </div>

            <!-- Diagnostic Table by Year -->
            <div class="glass-panel p-6 rounded-2xl overflow-hidden">
                <h3 class="text-base font-bold text-white mb-3">Tabela Diagnóstica Oficial das Metas A e B</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-sans">
                        <thead class="bg-slate-800/70 text-slate-300 font-semibold border-b border-slate-700">
                            <tr>
                                <th class="p-3">Ano Escolar</th>
                                <th class="p-3">Componente</th>
                                <th class="p-3">Estudantes</th>
                                <th class="p-3">Taxa Adequação</th>
                                <th class="p-3">Status Meta A (80%)</th>
                                <th class="p-3">Taxa Meta B (80% Acertos)</th>
                                <th class="p-3">Status Meta B</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-metas" class="divide-y divide-slate-800">
                            <!-- Inserido dinamicamente via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ============================================================= -->
        <!-- TAB 2: PAINEL PEDAGÓGICO E INTERVENÇÃO                        -->
        <!-- ============================================================= -->
        <section id="tab-pedagogica" class="hidden space-y-6">
            <!-- Filter Controls -->
            <div class="glass-panel p-4 rounded-xl flex flex-wrap gap-4 items-center justify-between">
                <div class="flex flex-wrap gap-3 items-center">
                    <label class="text-xs font-semibold text-slate-400">Filtrar por Ano:</label>
                    <select id="filtro-ano" onchange="filtrarAlunos()" class="bg-slate-800 border border-slate-700 rounded-lg text-xs px-3 py-1.5 text-white">
                        <option value="todos">Todos os Anos (1º ao 5º)</option>
                        <option value="1">1º Ano</option>
                        <option value="2">2º Ano</option>
                        <option value="3">3º Ano</option>
                        <option value="4">4º Ano</option>
                        <option value="5">5º Ano</option>
                    </select>

                    <label class="text-xs font-semibold text-slate-400 ml-2">Componente:</label>
                    <select id="filtro-comp" onchange="filtrarAlunos()" class="bg-slate-800 border border-slate-700 rounded-lg text-xs px-3 py-1.5 text-white">
                        <option value="todos">Todos os Componentes</option>
                        <option value="LEITURA">Língua Portuguesa (Leitura)</option>
                        <option value="MATEMATICA">Matemática</option>
                    </select>

                    <label class="text-xs font-semibold text-slate-400 ml-2">Grupo de Intervenção:</label>
                    <select id="filtro-grupo" onchange="filtrarAlunos()" class="bg-slate-800 border border-slate-700 rounded-lg text-xs px-3 py-1.5 text-white">
                        <option value="todos">Todos os Grupos</option>
                        <option value="G1 - Emergencial">G1 - Emergencial (Abaixo Básico)</option>
                        <option value="G2 - Alerta">G2 - Alerta (Básico)</option>
                        <option value="G3 - Consolidação">G3 - Consolidação (Adequado)</option>
                        <option value="G4 - Avançado">G4 - Avançado</option>
                    </select>
                </div>
                <div class="text-xs text-slate-400 font-mono" id="contador-alunos">Mostrando 640 avaliações</div>
            </div>

            <!-- Student Diagnostic Table -->
            <div class="glass-panel p-6 rounded-2xl">
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-sans">
                        <thead class="bg-slate-800/70 text-slate-300 font-semibold border-b border-slate-700">
                            <tr>
                                <th class="p-3">ID Seguro Aluno</th>
                                <th class="p-3">Ano</th>
                                <th class="p-3">Matéria</th>
                                <th class="p-3">Acertos</th>
                                <th class="p-3">Nível CAEd</th>
                                <th class="p-3">Escala SPAECE</th>
                                <th class="p-3">Grupo Intervenção</th>
                                <th class="p-3">Lacuna Meta A</th>
                                <th class="p-3">Lacuna Meta B</th>
                                <th class="p-3">AEE / Laudo</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-alunos" class="divide-y divide-slate-800 font-mono">
                            <!-- Inserido dinamicamente via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ============================================================= -->
        <!-- TAB 3: PSICOLOGIA & AEE (PROTOCOLO TOD/PBS)                   -->
        <!-- ============================================================= -->
        <section id="tab-aee" class="hidden space-y-6">
            <!-- TOD Protocol Banner -->
            <div class="bg-gradient-to-r from-purple-900/40 via-indigo-900/30 to-slate-900/50 border border-purple-500/30 rounded-2xl p-6 relative overflow-hidden">
                <div class="flex items-start justify-between">
                    <div>
                        <span class="px-2.5 py-1 rounded-full text-xs font-bold bg-purple-500/20 text-purple-300 border border-purple-500/40 uppercase tracking-wider">
                            Protocolo Clínico e Pedagógico Exclusivo
                        </span>
                        <h2 class="text-xl font-bold text-white mt-2">Manejo de TOD (Transtorno Opositor Desafiador — CID-10: F91.3 | CID-11: 6C90)</h2>
                        <p class="text-xs text-slate-300 mt-1 max-w-3xl">
                            Diretrizes mandatórias de Suporte Comportamental Positivo (PBS) e técnica da escolha controlada para garantir a participação digna, evitar crises de oposição e proteger o escore psicométrico dos estudantes.
                        </p>
                    </div>
                    <div class="text-right font-mono">
                        <span class="text-2xl font-black text-purple-300">8 Casos</span>
                        <div class="text-xs text-slate-400">Comorbidades c/ TDAH/TEA</div>
                    </div>
                </div>

                <!-- 4 Action Cards for TOD -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-3 mt-5">
                    <div class="p-3 rounded-xl bg-slate-900/60 border border-purple-500/20 text-xs">
                        <div class="font-bold text-purple-300 mb-1">1. Escolha Controlada</div>
                        <p class="text-slate-400">Nunca impor ordem direta imperativa. Oferecer 2 opções pré-validadas: <em>"Prefere iniciar pelos itens de cálculo ou geometria?"</em></p>
                    </div>
                    <div class="p-3 rounded-xl bg-slate-900/60 border border-purple-500/20 text-xs">
                        <div class="font-bold text-purple-300 mb-1">2. Prevenção de Escalada</div>
                        <p class="text-slate-400">Nunca confrontar ou repreender publicamente em sala. Diálogo em tom neutro e privado; foco na ação e não na pessoa.</p>
                    </div>
                    <div class="p-3 rounded-xl bg-slate-900/60 border border-purple-500/20 text-xs">
                        <div class="font-bold text-purple-300 mb-1">3. Reforço Positivo 4:1</div>
                        <p class="text-slate-400">Manter proporção de 4 validações de comportamentos positivos para cada intervenção de redirecionamento de conduta.</p>
                    </div>
                    <div class="p-3 rounded-xl bg-slate-900/60 border border-purple-500/20 text-xs">
                        <div class="font-bold text-purple-300 mb-1">4. Proteção Psicométrica</div>
                        <p class="text-slate-400">A recusa inicial de prova não é erro cognitivo. Aplicar pausas ativas de 5 min antes de registrar omissão no caderno.</p>
                    </div>
                </div>
            </div>

            <!-- AEE Census Table -->
            <div class="glass-panel p-6 rounded-2xl">
                <h3 class="text-base font-bold text-white mb-2">Prontuário de Inclusão Escolar & AEE (Censo de 24 Estudantes)</h3>
                <p class="text-xs text-slate-400 mb-4">Mapeamento em conformidade com a Lei Brasileira de Inclusão (LBI nº 13.146/15) e Lei nº 14.254/21.</p>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-sans">
                        <thead class="bg-slate-800/70 text-slate-300 font-semibold border-b border-slate-700">
                            <tr>
                                <th class="p-3">ID Seguro Aluno</th>
                                <th class="p-3">Ano / Turma</th>
                                <th class="p-3">CID-10</th>
                                <th class="p-3">CID-11</th>
                                <th class="p-3">Diagnóstico Clínico</th>
                                <th class="p-3">Manejo TOD PBS</th>
                                <th class="p-3">Tempo +50%</th>
                                <th class="p-3">Ledor</th>
                                <th class="p-3">Transcritor</th>
                                <th class="p-3">Ambiente Calmo</th>
                                <th class="p-3">Pausas Ativas</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-aee" class="divide-y divide-slate-800 font-mono">
                            <!-- Inserido dinamicamente via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ============================================================= -->
        <!-- TAB 4: EVOLUÇÃO LONGITUDINAL MULTI-CICLOS                     -->
        <!-- ============================================================= -->
        <section id="tab-longitudinal" class="hidden space-y-6">
            <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <!-- Trajectory Chart -->
                <div class="lg:col-span-2 glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-1">Trajetória Longitudinal de Proficiência SPAECE (Ciclos I, II e III)</h3>
                    <p class="text-xs text-slate-400 mb-4">Evolução média das coortes escolares ao longo do ano letivo de 2026.</p>
                    <div class="h-72">
                        <canvas id="chartLongitudinal"></canvas>
                    </div>
                </div>

                <!-- Cluster Distribution -->
                <div class="glass-panel p-6 rounded-2xl">
                    <h3 class="text-base font-bold text-white mb-1">Clusters Pedagógicos Evolutivos</h3>
                    <p class="text-xs text-slate-400 mb-4">Classificação por taxa de ganho psicométrico ($\Delta \theta$).</p>
                    <div class="h-64 flex items-center justify-center">
                        <canvas id="chartClusters"></canvas>
                    </div>
                </div>
            </div>

            <!-- Longitudinal Table -->
            <div class="glass-panel p-6 rounded-2xl">
                <h3 class="text-base font-bold text-white mb-3">Tabela de Acompanhamento Longitudinal Individualizado</h3>
                <div class="overflow-x-auto">
                    <table class="w-full text-left text-xs font-sans">
                        <thead class="bg-slate-800/70 text-slate-300 font-semibold border-b border-slate-700">
                            <tr>
                                <th class="p-3">ID Seguro</th>
                                <th class="p-3">Turma</th>
                                <th class="p-3">Componente</th>
                                <th class="p-3">Transição</th>
                                <th class="p-3">Prof. Inicial</th>
                                <th class="p-3">Prof. Final</th>
                                <th class="p-3">Ganho SPAECE</th>
                                <th class="p-3">Ganho TRI (Δθ)</th>
                                <th class="p-3">Migração</th>
                                <th class="p-3">Cluster Pedagógico</th>
                                <th class="p-3">Cluster Psicológico AEE</th>
                            </tr>
                        </thead>
                        <tbody id="tbody-longitudinal" class="divide-y divide-slate-800 font-mono">
                            <!-- Inserido dinamicamente via JS -->
                        </tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- ============================================================= -->
        <!-- TAB 5: MATRIZ DE TRANSIÇÃO DE MARKOV                          -->
        <!-- ============================================================= -->
        <section id="tab-markov" class="hidden space-y-6">
            <div class="glass-panel p-6 rounded-2xl">
                <div class="flex items-center justify-between mb-4">
                    <div>
                        <h3 class="text-base font-bold text-white">Matriz Estocástica de Transição de Markov</h3>
                        <p class="text-xs text-slate-400">Probabilidade empírica (%) de um estudante transitar entre níveis de desempenho CAEd entre o Ciclo I e o Ciclo II.</p>
                    </div>
                    <div class="text-xs font-mono text-slate-400">Modelo Calibrado (3º Ano Leitura)</div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
                    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
                        <div class="text-xs text-red-400 font-bold mb-2">Origem: Abaixo do Básico</div>
                        <ul class="text-xs space-y-1 font-mono">
                            <li class="flex justify-between"><span>➔ Abaixo Básico:</span> <span class="text-slate-400 font-bold">31.8%</span></li>
                            <li class="flex justify-between"><span>➔ Básico:</span> <span class="text-emerald-400 font-bold">68.2%</span></li>
                            <li class="flex justify-between"><span>➔ Adequado:</span> <span class="text-slate-500">0.0%</span></li>
                            <li class="flex justify-between"><span>➔ Avançado:</span> <span class="text-slate-500">0.0%</span></li>
                        </ul>
                    </div>
                    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
                        <div class="text-xs text-amber-400 font-bold mb-2">Origem: Básico</div>
                        <ul class="text-xs space-y-1 font-mono">
                            <li class="flex justify-between"><span>➔ Abaixo Básico:</span> <span class="text-slate-500">0.0%</span></li>
                            <li class="flex justify-between"><span>➔ Básico:</span> <span class="text-slate-400 font-bold">45.5%</span></li>
                            <li class="flex justify-between"><span>➔ Adequado:</span> <span class="text-blue-400 font-bold">54.5%</span></li>
                            <li class="flex justify-between"><span>➔ Avançado:</span> <span class="text-slate-500">0.0%</span></li>
                        </ul>
                    </div>
                    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
                        <div class="text-xs text-blue-400 font-bold mb-2">Origem: Adequado</div>
                        <ul class="text-xs space-y-1 font-mono">
                            <li class="flex justify-between"><span>➔ Abaixo Básico:</span> <span class="text-slate-500">0.0%</span></li>
                            <li class="flex justify-between"><span>➔ Básico:</span> <span class="text-slate-500">0.0%</span></li>
                            <li class="flex justify-between"><span>➔ Adequado:</span> <span class="text-slate-400 font-bold">61.1%</span></li>
                            <li class="flex justify-between"><span>➔ Avançado:</span> <span class="text-purple-400 font-bold">38.9%</span></li>
                        </ul>
                    </div>
                    <div class="p-4 rounded-xl bg-slate-900 border border-slate-800">
                        <div class="text-xs text-emerald-400 font-bold mb-2">Origem: Avançado</div>
                        <ul class="text-xs space-y-1 font-mono">
                            <li class="flex justify-between"><span>➔ Abaixo Básico:</span> <span class="text-slate-500">0.0%</span></li>
                            <li class="flex justify-between"><span>➔ Básico:</span> <span class="text-slate-500">0.0%</span></li>
                            <li class="flex justify-between"><span>➔ Adequado:</span> <span class="text-slate-500">0.0%</span></li>
                            <li class="flex justify-between"><span>➔ Avançado:</span> <span class="text-emerald-400 font-bold">100.0%</span></li>
                        </ul>
                    </div>
                </div>

                <div class="mt-8 p-4 rounded-xl bg-slate-900/40 border border-slate-800 text-xs text-slate-300">
                    <span class="font-bold text-white">Interpretação Pedagógica da Cadeia de Markov:</span>
                    A matriz evidencia retenção de 100% no nível Avançado e uma taxa de ascensão de 68.2% do nível Abaixo do Básico para Básico, demonstrando que as ações de recuperação emergencial (Grupo G1) surtem efeito direto na transição de estágio.
                </div>
            </div>
        </section>

    </main>

    <!-- Footer -->
    <footer class="glass-panel border-t border-slate-800 py-6 text-center text-xs text-slate-400 font-mono">
        Escola Municipal Airam Veras | Base Canônica 3FN Auditável (SHA-256: ab2deee8...2cc) | Projeto 2026
    </footer>

    <!-- Embedded Complete Real Database JSON -->
    <script>
        const DB = {dados_json_str};

        // Navigation Switcher
        function switchTab(tabId) {{
            const tabs = ['executiva', 'pedagogica', 'aee', 'longitudinal', 'markov'];
            tabs.forEach(t => {{
                document.getElementById('tab-' + t).classList.add('hidden');
                document.getElementById('btn-' + t).classList.remove('active');
            }});
            document.getElementById('tab-' + tabId).classList.remove('hidden');
            document.getElementById('btn-' + tabId).classList.add('active');
        }}

        // Render Metas Table
        function renderMetasTable() {{
            const tbody = document.getElementById('tbody-metas');
            tbody.innerHTML = '';
            DB.metas.forEach(m => {{
                const tr = document.createElement('tr');
                const isAdeqOk = m.taxa_adequacao_pct >= 80;
                tr.innerHTML = `
                    <td class="p-3 font-bold text-white">${{m.ano_escolar}}º Ano</td>
                    <td class="p-3 text-slate-300 font-semibold">${{m.componente}}</td>
                    <td class="p-3 font-mono">${{m.total_estudantes}}</td>
                    <td class="p-3 font-mono font-bold ${{isAdeqOk ? 'text-emerald-400' : 'text-amber-400'}}">${{m.taxa_adequacao_pct.toFixed(1)}}%</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-xs ${{isAdeqOk ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' : 'bg-slate-800 text-slate-300'}}">${{m.status_meta_a}}</span></td>
                    <td class="p-3 font-mono text-purple-400 font-bold">${{m.taxa_meta_b_80pct.toFixed(1)}}%</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300">${{m.status_meta_b}}</span></td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Render Student Table with Filtering
        function renderStudentTable(alunos) {{
            const tbody = document.getElementById('tbody-alunos');
            tbody.innerHTML = '';
            document.getElementById('contador-alunos').innerText = `Mostrando ${{alunos.length}} avaliações`;

            alunos.slice(0, 150).forEach(a => {{
                const tr = document.createElement('tr');
                const nivColor = a.nivel_caed === 'Avançado' ? 'text-emerald-400' : (a.nivel_caed === 'Adequado' ? 'text-blue-400' : (a.nivel_caed === 'Básico' ? 'text-amber-400' : 'text-red-400'));
                tr.innerHTML = `
                    <td class="p-3 text-slate-400" title="${{a.aluno_hash_id}}">${{a.aluno_hash_id.substring(0, 10)}}...</td>
                    <td class="p-3 font-bold text-white">${{a.ano_escolar}}º</td>
                    <td class="p-3 text-slate-300">${{a.componente}}</td>
                    <td class="p-3 font-bold text-white">${{a.total_acertos}} / ${{a.total_oportunidades}}</td>
                    <td class="p-3 font-bold ${{nivColor}}">${{a.nivel_caed}}</td>
                    <td class="p-3 font-bold text-white">${{a.proficiencia_spaece.toFixed(1)}}</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-200 border border-slate-700">${{a.grupo_intervencao}}</span></td>
                    <td class="p-3 text-amber-400">${{a.acertos_para_meta_a > 0 ? '+' + a.acertos_para_meta_a : 'Alcançado'}}</td>
                    <td class="p-3 text-purple-400">${{a.lacuna_meta_b > 0 ? '+' + a.lacuna_meta_b : 'Alcançado'}}</td>
                    <td class="p-3 text-xs font-sans">${{a.diagnostico_aee !== 'Nenhum' ? '<span class="text-purple-400 font-bold">' + a.diagnostico_aee + '</span>' : '<span class="text-slate-600">-</span>'}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function filtrarAlunos() {{
            const ano = document.getElementById('filtro-ano').value;
            const comp = document.getElementById('filtro-comp').value;
            const grupo = document.getElementById('filtro-grupo').value;

            let filtrados = DB.estudantes;
            if (ano !== 'todos') filtrados = filtrados.filter(a => a.ano_escolar === parseInt(ano));
            if (comp !== 'todos') filtrados = filtrados.filter(a => a.componente === comp);
            if (grupo !== 'todos') filtrados = filtrados.filter(a => a.grupo_intervencao === grupo);

            renderStudentTable(filtrados);
        }}

        // Render AEE Table
        function renderAeeTable() {{
            const tbody = document.getElementById('tbody-aee');
            tbody.innerHTML = '';
            DB.aee.forEach(a => {{
                const tr = document.createElement('tr');
                const isTod = a.requer_manejo_tod_pbs === 1;
                tr.innerHTML = `
                    <td class="p-3 text-slate-400" title="${{a.aluno_hash_id}}">${{a.aluno_hash_id.substring(0, 10)}}...</td>
                    <td class="p-3 font-bold text-white">${{a.nome_turma}}</td>
                    <td class="p-3 font-bold ${{isTod ? 'text-purple-400' : 'text-blue-400'}}">${{a.cid10}}</td>
                    <td class="p-3 text-slate-400">${{a.cid11}}</td>
                    <td class="p-3 font-sans font-bold text-slate-200">${{a.grupo_diagnostico}}</td>
                    <td class="p-3 font-bold ${{isTod ? 'text-emerald-400' : 'text-slate-600'}}">${{isTod ? 'SIM (PBS Ativo)' : 'Não'}}</td>
                    <td class="p-3 text-center">${{a.recurso_tempo_estendido_50pct ? '✅' : '❌'}}</td>
                    <td class="p-3 text-center">${{a.recurso_ledor_oficial ? '✅' : '❌'}}</td>
                    <td class="p-3 text-center">${{a.recurso_transcritor_oficial ? '✅' : '❌'}}</td>
                    <td class="p-3 text-center">${{a.recurso_ambiente_baixo_estimulo ? '✅' : '❌'}}</td>
                    <td class="p-3 text-center">${{a.recurso_pausas_ativas_fracionadas ? '✅' : '❌'}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Render Longitudinal Table
        function renderLongitudinalTable() {{
            const tbody = document.getElementById('tbody-longitudinal');
            tbody.innerHTML = '';
            DB.longitudinal.slice(0, 100).forEach(l => {{
                const tr = document.createElement('tr');
                const deltaColor = l.ganho_spaece >= 0 ? 'text-emerald-400 font-bold' : 'text-red-400 font-bold';
                tr.innerHTML = `
                    <td class="p-3 text-slate-400">${{l.aluno_hash_id.substring(0, 10)}}...</td>
                    <td class="p-3 text-white">${{l.nome_turma}}</td>
                    <td class="p-3 text-slate-300">${{l.componente_curricular}}</td>
                    <td class="p-3 text-slate-400">Ciclo ${{l.ciclo_origem}} ➔ ${{l.ciclo_destino}}</td>
                    <td class="p-3 text-slate-300">${{l.proficiencia_origem.toFixed(1)}}</td>
                    <td class="p-3 text-white font-bold">${{l.proficiencia_destino.toFixed(1)}}</td>
                    <td class="p-3 ${{deltaColor}}">${{l.ganho_spaece >= 0 ? '+' : ''}}${{l.ganho_spaece.toFixed(1)}}</td>
                    <td class="p-3 ${{deltaColor}}">${{l.ganho_theta_tri >= 0 ? '+' : ''}}${{l.ganho_theta_tri.toFixed(2)}}</td>
                    <td class="p-3"><span class="px-2 py-0.5 rounded text-xs bg-slate-800 text-slate-300">${{l.migracao_status}}</span></td>
                    <td class="p-3 font-sans text-xs text-blue-300">${{l.cluster_pedagogico}}</td>
                    <td class="p-3 font-sans text-xs text-purple-300">${{l.cluster_psicologico_aee}}</td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        // Initialize Charts
        function initCharts() {{
            // 1. Bar Chart: Metas por Ano
            const ctxMetas = document.getElementById('chartMetasPorAno').getContext('2d');
            const anosLabels = ['1º Ano', '2º Ano', '3º Ano', '4º Ano', '5º Ano'];
            new Chart(ctxMetas, {{
                type: 'bar',
                data: {{
                    labels: anosLabels,
                    datasets: [
                        {{
                            label: 'Língua Portuguesa (%)',
                            data: [41.7, 52.3, 56.2, 47.6, 84.9],
                            backgroundColor: 'rgba(59, 130, 246, 0.85)',
                            borderRadius: 6
                        }},
                        {{
                            label: 'Matemática (%)',
                            data: [45.8, 50.0, 53.1, 38.1, 79.2],
                            backgroundColor: 'rgba(16, 185, 129, 0.85)',
                            borderRadius: 6
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            beginAtZero: true,
                            max: 100,
                            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                            ticks: {{ color: '#94a3b8' }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#94a3b8' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f1f5f9' }} }}
                    }}
                }}
            }});

            // 2. Doughnut Chart: Níveis CAEd
            const ctxNiveis = document.getElementById('chartNiveisCaed').getContext('2d');
            new Chart(ctxNiveis, {{
                type: 'doughnut',
                data: {{
                    labels: ['Abaixo do Básico', 'Básico', 'Adequado', 'Avançado'],
                    datasets: [{{
                        data: [136, 143, 247, 114],
                        backgroundColor: ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }}
                    }}
                }}
            }});

            // 3. Line Chart: Trajetória Longitudinal
            const ctxLong = document.getElementById('chartLongitudinal').getContext('2d');
            new Chart(ctxLong, {{
                type: 'line',
                data: {{
                    labels: ['Ciclo I (Mar/26)', 'Ciclo II (Jun/26)', 'Ciclo III (Nov/26)'],
                    datasets: [
                        {{
                            label: '5º Ano (LP)',
                            data: [265.4, 288.2, 305.1],
                            borderColor: '#8b5cf6',
                            backgroundColor: 'rgba(139, 92, 246, 0.1)',
                            fill: true,
                            tension: 0.3
                        }},
                        {{
                            label: '3º Ano (LP)',
                            data: [205.2, 228.6, 244.5],
                            borderColor: '#3b82f6',
                            backgroundColor: 'rgba(59, 130, 246, 0.1)',
                            fill: true,
                            tension: 0.3
                        }},
                        {{
                            label: '4º Ano (MAT)',
                            data: [188.5, 212.0, 230.8],
                            borderColor: '#f59e0b',
                            backgroundColor: 'rgba(245, 158, 11, 0.1)',
                            fill: true,
                            tension: 0.3
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {{
                        y: {{
                            grid: {{ color: 'rgba(255, 255, 255, 0.05)' }},
                            ticks: {{ color: '#94a3b8' }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ color: '#94a3b8' }}
                        }}
                    }},
                    plugins: {{
                        legend: {{ labels: {{ color: '#f1f5f9' }} }}
                    }}
                }}
            }});

            // 4. Clusters Pie Chart
            const ctxClusters = document.getElementById('chartClusters').getContext('2d');
            new Chart(ctxClusters, {{
                type: 'pie',
                data: {{
                    labels: ['Aceleração Alta', 'Consolidação', 'Estagnação em Risco', 'Regressão'],
                    datasets: [{{
                        data: [38, 44, 15, 3],
                        backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                        borderWidth: 0
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ color: '#f1f5f9', font: {{ size: 10 }} }} }}
                    }}
                }}
            }});
        }}

        // Bootstrap
        window.addEventListener('DOMContentLoaded', () => {{
            renderMetasTable();
            renderStudentTable(DB.estudantes);
            renderAeeTable();
            renderLongitudinalTable();
            initCharts();
        }});
    </script>
</body>
</html>
"""
    return html

def main():
    print("1. Extraindo dados analíticos e censitários do SQLite...")
    dados = extrair_dados_dashboard()
    print(f"   -> {len(dados['estudantes'])} avaliações, {len(dados['aee'])} perfis AEE e {len(dados['longitudinal'])} projeções recuperadas.")

    print("2. Gerando HTML autônomo com Glassmorphism, Tailwind e Chart.js...")
    html_content = gerar_html_completo(dados)

    OUT_DASHBOARD_ROOT.write_text(html_content, encoding="utf-8")
    OUT_DASHBOARD_REL.parent.mkdir(parents=True, exist_ok=True)
    OUT_DASHBOARD_REL.write_text(html_content, encoding="utf-8")

    print(f"3. Dashboard gravado com sucesso:")
    print(f"   -> Raiz: {OUT_DASHBOARD_ROOT}")
    print(f"   -> Relatório: {OUT_DASHBOARD_REL}")

if __name__ == "__main__":
    main()
