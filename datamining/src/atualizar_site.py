import os

def main():
    print("Iniciando atualização de docs/index.html e docs/dashboard.html...")

    # --- 1. Atualizar docs/index.html ---
    with open("docs/index.html", "r", encoding="utf-8") as f:
        idx_content = f.read()

    # Atualização no Slide 1 Hero pills
    target_pill = '<span class="attribute-pill font-mono text-emerald-400 border-emerald-500/30">Base 3FN\n                        Auditável</span>'
    repl_pill = '<span class="attribute-pill font-mono text-emerald-400 border-emerald-500/30">Banco 3FN • 51 Tabelas (0 Ilhas)</span>\n                    <span class="attribute-pill font-mono text-purple-400 border-purple-500/30">Dossiê Mestre 670 Laudas</span>'
    
    if target_pill in idx_content:
        idx_content = idx_content.replace(target_pill, repl_pill)
        print("-> Slide 1 Hero pills atualizado!")
    else:
        # Fallback check
        target_pill_alt = '<span class="attribute-pill font-mono text-emerald-400 border-emerald-500/30">Base 3FN Auditável</span>'
        if target_pill_alt in idx_content:
            idx_content = idx_content.replace(target_pill_alt, repl_pill)
            print("-> Slide 1 Hero pills alt atualizado!")

    # Atualização no Slide 4: Educação Especial Inclusiva
    old_s4 = '''                    <div>
                        <span class="text-xs uppercase font-mono font-bold text-purple-400">Educação Especial Inclusiva
                            (LBI & Lei 14.254)</span>
                        <h2 class="text-2xl sm:text-3xl font-extrabold text-white">Matriz de Manejos por CID</h2>
                    </div>'''

    new_s4 = '''                    <div>
                        <span class="text-xs uppercase font-mono font-bold text-purple-400">Educação Especial Inclusiva (LBI 13.146, Berenice Piana 12.764, Lei 14.254, Res. CNE 04/2009 & Nota Técnica 02/2025/MEC)</span>
                        <h2 class="text-2xl sm:text-3xl font-extrabold text-white">Matriz de Manejos, PEI & PAEE por CID</h2>
                    </div>'''

    if old_s4 in idx_content:
        idx_content = idx_content.replace(old_s4, new_s4)
        print("-> Slide 4 título e cabeçalho atualizado!")

    old_s4_p = '''                <p class="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
                    Protocolos clínicos parametrizados para os <strong>24 estudantes laudados</strong> da escola,
                    garantindo acomodação de provas e sala de aula regular:
                </p>'''

    new_s4_p = '''                <p class="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
                    Protocolos clínicos e psiconeuropedagógicos baseados no <strong>Desenho Universal para a Aprendizagem (DUA)</strong>, Funções Executivas e Suporte Comportamental Positivo (PBS). Contempla <strong>96 PEIs bimestrais</strong> e <strong>24 Planos de AEE (SRM)</strong> registrados de forma auditável e sem ilhas no banco relacional de 51 tabelas:
                </p>'''

    if old_s4_p in idx_content:
        idx_content = idx_content.replace(old_s4_p, new_s4_p)
        print("-> Slide 4 descrição PEI/PAEE/DUA atualizada!")

    # Atualização no Slide 7: Hub Central do Ecossistema
    old_s7_hub = '''            <p class="text-sm sm:text-base text-slate-400 max-w-2xl mx-auto">
                Todos os artefatos estão integrados, auditados e disponíveis para pedagogos, psicólogos, auditores
                jurídicos e desenvolvedores.
            </p>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-left">'''

    new_s7_hub = '''            <p class="text-sm sm:text-base text-slate-400 max-w-3xl mx-auto">
                Todos os artefatos estão integrados, auditados e disponíveis para pedagogos, psicólogos, auditores
                jurídicos e desenvolvedores. Modelo canônico unificado para todas as turmas (1º ao 5º Ano).
            </p>

            <!-- Card Destaque: Dossiê Pedagógico Mestre 670 Laudas -->
            <div class="p-6 rounded-2xl glass-card border border-purple-500/40 bg-gradient-to-r from-purple-950/40 via-slate-900/80 to-blue-950/40 text-left shadow-2xl relative overflow-hidden">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div class="space-y-2">
                        <div class="flex flex-wrap items-center gap-2">
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40">NOVO • PADRÃO MESTRE 2026</span>
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-blue-500/20 text-blue-300 border border-blue-500/40">670 LAUDAS VETORIAIS A4</span>
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">LEDGER SHA-256 (BLOCO 13)</span>
                        </div>
                        <h3 class="text-lg md:text-xl font-black text-white flex items-center gap-2">
                            <i data-lucide="file-text" class="w-5 h-5 text-purple-400"></i>
                            Dossiê Pedagógico Mestre 1º Ano — BNCC, PEI/PAEE & Práticas Diárias Ampliadas
                        </h3>
                        <p class="text-xs text-slate-300 max-w-4xl leading-relaxed">
                            Modelo canônico referencial para todas as turmas (1º ao 5º Ano). Incorpora sequência lógica com citação real (DOI), estatísticas por estudante com gráficos D3/SVG, cruzamento longitudinal CAEd, Plano Anual e Bimestrais (I a IV) integrando todos os componentes da BNCC + <strong>BNCC Computacional</strong>, PEI/PAEE sob normas federais (LBI, Berenice Piana, Lei 14.254, DUA, Funções Executivas) e caderno completo de <strong>40 Folhas de Práticas Diárias Estruturadas</strong> (Método Fônico e Kumon).
                        </p>
                    </div>
                    <div class="flex flex-row md:flex-col gap-2 shrink-0">
                        <a href="DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank" class="px-4 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-500 text-white font-bold text-xs shadow-lg shadow-purple-600/30 flex items-center justify-center gap-2 transition">
                            <i data-lucide="external-link" class="w-4 h-4"></i> Abrir Dossiê (PDF)
                        </a>
                        <a href="DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" download class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1.5 transition">
                            <i data-lucide="download" class="w-3.5 h-3.5"></i> Baixar (2.98 MB)
                        </a>
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 text-left">'''

    if old_s7_hub in idx_content:
        idx_content = idx_content.replace(old_s7_hub, new_s7_hub)
        print("-> Slide 7 Banner do Dossiê Mestre 670 Laudas adicionado com sucesso!")

    # Atualizar card Banco SQLite no Slide 7
    old_card_banco = '''                <a href="https://github.com/MarceloClaro/AiramVeras" target="_blank"
                    class="p-4 rounded-xl glass-card hover:border-rose-500 transition group">
                    <div
                        class="w-9 h-9 rounded-lg bg-rose-500/10 border border-rose-500/30 flex items-center justify-center text-rose-400 mb-2 group-hover:scale-110 transition">
                        <i data-lucide="shield-check" class="w-4 h-4"></i>
                    </div>
                    <h3 class="text-xs font-bold text-white mb-1">Banco 3FN SQLite</h3>
                    <p class="text-[11px] text-slate-400">1.460 arestas e hash SHA-256.</p>
                </a>'''

    new_card_banco = '''                <a href="https://github.com/MarceloClaro/AiramVeras" target="_blank"
                    class="p-4 rounded-xl glass-card hover:border-emerald-500 transition group">
                    <div
                        class="w-9 h-9 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mb-2 group-hover:scale-110 transition">
                        <i data-lucide="database" class="w-4 h-4"></i>
                    </div>
                    <h3 class="text-xs font-bold text-white mb-1">Banco 3FN (51 Tabelas)</h3>
                    <p class="text-[11px] text-slate-400">100% sem ilhas, 13 blocos no Ledger e 96 PEIs.</p>
                </a>'''

    if old_card_banco in idx_content:
        idx_content = idx_content.replace(old_card_banco, new_card_banco)
        print("-> Slide 7 Card do Banco 3FN (51 Tabelas) atualizado!")

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(idx_content)
    print("-> docs/index.html gravado com sucesso!")

    # --- 2. Atualizar docs/dashboard.html ---
    with open("docs/dashboard.html", "r", encoding="utf-8") as f:
        dash_content = f.read()

    # Adicionar link do Dossiê Mestre no Header do dashboard
    old_dash_header = '''                <a href="relatorio_bioestatistica_anova_fisher.html" class="px-3 py-1.5 rounded-lg bg-emerald-900/50 hover:bg-emerald-800 text-emerald-200 border border-emerald-700/60 flex items-center gap-1.5 transition font-sans font-semibold">
                    📈 Bioestatística
                </a>'''

    new_dash_header = '''                <a href="relatorio_bioestatistica_anova_fisher.html" class="px-3 py-1.5 rounded-lg bg-emerald-900/50 hover:bg-emerald-800 text-emerald-200 border border-emerald-700/60 flex items-center gap-1.5 transition font-sans font-semibold">
                    📈 Bioestatística
                </a>
                <a href="DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank" class="px-3 py-1.5 rounded-lg bg-purple-900/60 hover:bg-purple-800 text-purple-200 border border-purple-700/70 flex items-center gap-1.5 transition font-sans font-semibold" title="Dossiê Pedagógico Mestre 1º Ano (670 Laudas Vetoriais A4)">
                    📑 Dossiê Mestre (670p)
                </a>'''

    if old_dash_header in dash_content:
        dash_content = dash_content.replace(old_dash_header, new_dash_header, 1)
        print("-> Header do dashboard atualizado com link do Dossiê!")

    # Atualizar KPI badges do dashboard
    old_dash_kpi = '''                <div class="px-3 py-1.5 rounded-lg glass-card flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span class="text-slate-400">Avaliações:</span>
                    <span class="font-bold text-emerald-400">640 C1 + 1.280 Proj.</span>
                </div>'''

    new_dash_kpi = '''                <div class="px-3 py-1.5 rounded-lg glass-card flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-emerald-400"></span>
                    <span class="text-slate-400">Avaliações:</span>
                    <span class="font-bold text-emerald-400">640 C1 + 1.280 Proj.</span>
                </div>
                <div class="px-3 py-1.5 rounded-lg glass-card flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-purple-400"></span>
                    <span class="text-slate-400">Banco:</span>
                    <span class="font-bold text-purple-300">51 Tabelas (0 Ilhas)</span>
                </div>'''

    if old_dash_kpi in dash_content:
        dash_content = dash_content.replace(old_dash_kpi, new_dash_kpi, 1)
        print("-> KPI Badges do dashboard atualizados!")

    # Adicionar botão na barra de abas
    old_dash_tabs = '''                <a href="relatorio_bioestatistica_anova_fisher.html" class="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-semibold shadow-md flex items-center gap-1.5 transition">
                    📊 ANOVA & Fisher
                </a>'''

    new_dash_tabs = '''                <a href="relatorio_bioestatistica_anova_fisher.html" class="px-3 py-1.5 rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white text-xs font-semibold shadow-md flex items-center gap-1.5 transition">
                    📊 ANOVA & Fisher
                </a>
                <a href="DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank" class="px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-semibold shadow-md flex items-center gap-1.5 transition" title="Dossiê Pedagógico Mestre 1º Ano (670 Laudas Vetoriais A4)">
                    📑 Dossiê Mestre 1º Ano (670p)
                </a>'''

    if old_dash_tabs in dash_content:
        dash_content = dash_content.replace(old_dash_tabs, new_dash_tabs, 1)
        print("-> Barra de abas do dashboard atualizada!")

    with open("docs/dashboard.html", "w", encoding="utf-8") as f:
        f.write(dash_content)
    print("-> docs/dashboard.html gravado com sucesso!")

if __name__ == "__main__":
    main()
