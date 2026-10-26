# -*- coding: utf-8 -*-
"""
Atualização Robusta dos Showcases Web para o 5º Ano A e B (2.200 Laudas)
Corrige espaçamento e insere o 5º Ano no Header, Hero Pills, Hero CTA e Slide 7.
"""
import os
import re
import shutil

WORKSPACE_DIR = r"c:\Users\marce\Downloads\Airam veras"
DOCS_INDEX = os.path.join(WORKSPACE_DIR, "docs", "index.html")
ROOT_INDEX = os.path.join(WORKSPACE_DIR, "index.html")
DOCS_DASH = os.path.join(WORKSPACE_DIR, "docs", "dashboard.html")
ROOT_DASH = os.path.join(WORKSPACE_DIR, "dashboard.html")

def atualizar_index():
    with open(DOCS_INDEX, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Header: Adicionar 5º Ano A e B se não presente
    if 'DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf' not in html[:1500]:
        pattern_header = r'(<a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS\.pdf"[^>]*>[\s\S]*?4º Ano A e B \(1720p\)[\s\S]*?</a>)'
        header_5ano = r'''\1
            <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2 py-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 border border-emerald-700/70 transition flex items-center gap-1 font-semibold text-[11px]"
                title="Dossiê Pedagógico Mestre 5º Ano A e B (2.200 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3 h-3 text-emerald-400"></i> 5º Ano A e B (2200p)
            </a>'''
        html = re.sub(pattern_header, header_5ano, html, count=1)
        print("Header atualizado com 5º Ano.")

    # 2. Hero Pills: Adicionar 5º Ano A e B
    pattern_pill = r'(<a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS\.pdf"[^>]*class="attribute-pill[^>]*>[\s\S]*?4º Ano A e B \(1\.720p\)[\s\S]*?</a>)'
    pill_5ano = r'''\1
                    <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="attribute-pill font-mono text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/20 transition flex items-center gap-1">
                        <i data-lucide="file-spreadsheet" class="w-3 h-3"></i> 5º Ano A e B (2.200p)
                    </a>'''
    if '5º Ano A e B (2.200p)' not in html:
        html = re.sub(pattern_pill, pill_5ano, html, count=1)
        print("Hero Pills atualizadas com 5º Ano.")

    # 3. Hero CTA: Adicionar 5º Ano A e B
    pattern_cta = r'(<a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS\.pdf"[^>]*class="px-3 py-2 rounded-xl bg-indigo-600[^>]*>[\s\S]*?4º Ano A e B \(1720p\)[\s\S]*?</a>)'
    cta_5ano = r'''\1
                    <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/30 text-xs">
                        <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i> 5º Ano A e B (2200p)
                    </a>'''
    if 'bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/30 text-xs' not in html:
        html = re.sub(pattern_cta, cta_5ano, html, count=1)
        print("Hero CTA atualizado com 5º Ano.")

    # 4. Slide 7: Card do 5º Ano A e B
    if 'Card 5º Ano A e B: 2.200 Laudas' not in html:
        card_5ano_markup = '''

                <!-- Card 5º Ano A e B: 2.200 Laudas (POSICIONADO ABAIXO DO 4º ANO) -->
                <div class="p-6 rounded-2xl glass-card border border-emerald-500/40 bg-gradient-to-r from-emerald-950/40 via-slate-900/80 to-teal-950/40 text-left shadow-2xl relative overflow-hidden">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div class="space-y-2">
                            <div class="flex flex-wrap items-center gap-2">
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">5º ANO A e B • COORTE 54 ESTUDANTES</span>
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-teal-500/20 text-teal-300 border border-teal-500/40">2.200 LAUDAS VETORIAIS A4</span>
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">LEDGER SHA-256 (BLOCO 25)</span>
                            </div>
                            <h3 class="text-lg md:text-xl font-black text-white flex items-center gap-2">
                                <i data-lucide="file-spreadsheet" class="w-5 h-5 text-emerald-400"></i>
                                Dossiê Pedagógico Mestre 5º Ano (Turmas A e B) — BNCC, PEI/PAEE & Terminalidade Anos Iniciais
                            </h3>
                            <p class="text-xs text-slate-300 max-w-4xl leading-relaxed">
                                Total de exatamente <strong>2.200 laudas vetoriais A4</strong>: 40 laudas de Front Matter Master (Matriz Oficial <strong>INTEGRAL 35H SME Crateús</strong> com 7 aulas diárias de 50 min, bioestatística com guia leigo, modelagem de Markov, EWS, trilha Kumon Níveis C e D de frações, números decimais e porcentagem, e índice remissivo nominal com início de página exato por turma) + <strong>54 Cadernos Individuais de 40 laudas cada</strong> (27 alunos da Turma 5º Ano A + 27 alunos da Turma 5º Ano B), integrando 26 laudas de Língua Portuguesa/Fônico do Volume 5, 4 laudas de Matemática Kumon (operações formais com decimais, frações equivalentes, porcentagem e situações-problema SPAECE D01-D28) e 6 laudas multidisciplinares (Ciências da Natureza, Geografia, História, Arte, Educação Física, BNCC Computação e Termo Forense com fé pública).
                            </p>
                        </div>
                        <div class="flex flex-row md:flex-col gap-2 shrink-0">
                            <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank" class="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 flex items-center justify-center gap-2 transition">
                                <i data-lucide="external-link" class="w-4 h-4"></i> Abrir Dossiê (PDF)
                            </a>
                            <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" download class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1.5 transition">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i> Baixar (9.60 MB)
                            </a>
                        </div>
                    </div>
                </div>'''

        # Localizar o fechamento do card do 4º ano no Slide 7
        pattern_card_4ano = r'(<a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS\.pdf" download[\s\S]*?Baixar \(7\.58 MB\)[\s\S]*?</a>[\s\S]*?</div>[\s\S]*?</div>[\s\S]*?</div>)'
        match = re.search(pattern_card_4ano, html)
        if match:
            html = html[:match.end()] + card_5ano_markup + html[match.end():]
            print("Slide 7: Card do 5º Ano inserido após o 4º Ano.")
        else:
            print("AVISO: Regex do Card do 4º Ano não casou.")

    with open(DOCS_INDEX, 'w', encoding='utf-8') as f:
        f.write(html)
    shutil.copy(DOCS_INDEX, ROOT_INDEX)
    print("Salvos docs/index.html e index.html.")

def atualizar_dashboard():
    if not os.path.exists(DOCS_DASH):
        return
    with open(DOCS_DASH, 'r', encoding='utf-8') as f:
        html = f.read()

    if 'DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf' not in html:
        pattern_btn = r'(<a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS\.pdf"[^>]*>[\s\S]*?Dossiê 4º Ano A e B \(1720p\)[\s\S]*?</a>)'
        btn_5ano = r'''\1
            <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2.5 py-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 border border-emerald-700/70 transition flex items-center gap-1.5 font-semibold text-xs"
                title="Dossiê Pedagógico Mestre 5º Ano A e B (2.200 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-emerald-400"></i> Dossiê 5º Ano A e B (2200p)
            </a>'''
        html = re.sub(pattern_btn, btn_5ano, html, count=1)
        print("Dashboard atualizado com botão do 5º Ano A e B.")

    with open(DOCS_DASH, 'w', encoding='utf-8') as f:
        f.write(html)
    shutil.copy(DOCS_DASH, ROOT_DASH)
    print("Salvos docs/dashboard.html e dashboard.html.")

if __name__ == '__main__':
    atualizar_index()
    atualizar_dashboard()
