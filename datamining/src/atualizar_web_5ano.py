# -*- coding: utf-8 -*-
"""
Atualização das Interfaces Web para Incorporar o Dossiê Mestre do 5º Ano A e B (2.200 Laudas)
Atualiza docs/index.html, index.html, docs/dashboard.html e dashboard.html
"""
import os
import shutil

DOCS_INDEX = 'docs/index.html'
ROOT_INDEX = 'index.html'
DOCS_DASH = 'docs/dashboard.html'
ROOT_DASH = 'dashboard.html'

def atualizar_index():
    with open(DOCS_INDEX, 'r', encoding='utf-8') as f:
        html = f.read()

    html_norm = html.replace('\r\n', '\n')

    # 1. Header fixo superior
    btn_4ano_header = """            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2 py-1.5 rounded-lg bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/70 transition flex items-center gap-1 font-semibold text-[11px]"
                title="Dossiê Pedagógico Mestre 4º Ano A e B (1.720 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3 h-3 text-indigo-400"></i> 4º Ano A e B (1720p)
            </a>"""

    btn_5ano_header = btn_4ano_header + """\n            <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2 py-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 border border-emerald-700/70 transition flex items-center gap-1 font-semibold text-[11px]"
                title="Dossiê Pedagógico Mestre 5º Ano A e B (2.200 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3 h-3 text-emerald-400"></i> 5º Ano A e B (2200p)
            </a>"""

    if btn_4ano_header in html_norm:
        html_norm = html_norm.replace(btn_4ano_header, btn_5ano_header)
        print("Header fixo atualizado com 5º Ano A e B.")
    else:
        print("AVISO: Trecho do header do 4º ano não encontrado.")

    # 2. Hero Badges (Pills)
    pill_4ano = """                    <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="attribute-pill font-mono text-indigo-300 border-indigo-500/40 hover:bg-indigo-500/20 transition flex items-center gap-1">
                        <i data-lucide="file-spreadsheet" class="w-3 h-3"></i> 4º Ano A e B (1.720p)
                    </a>"""

    pill_5ano = pill_4ano + """\n                    <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="attribute-pill font-mono text-emerald-300 border-emerald-500/40 hover:bg-emerald-500/20 transition flex items-center gap-1">
                        <i data-lucide="file-spreadsheet" class="w-3 h-3"></i> 5º Ano A e B (2.200p)
                    </a>"""

    if pill_4ano in html_norm:
        html_norm = html_norm.replace(pill_4ano, pill_5ano)
        print("Hero Pills atualizados com 5º Ano A e B.")

    # 3. Hero CTA
    cta_4ano = """                    <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="px-3 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition flex items-center gap-1.5 shadow-lg shadow-indigo-600/30 text-xs">
                        <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i> 4º Ano A e B (1720p)
                    </a>"""

    cta_5ano = cta_4ano + """\n                    <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold transition flex items-center gap-1.5 shadow-lg shadow-emerald-600/30 text-xs">
                        <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i> 5º Ano A e B (2200p)
                    </a>"""

    if cta_4ano in html_norm:
        html_norm = html_norm.replace(cta_4ano, cta_5ano)
        print("Hero CTA atualizado com 5º Ano A e B.")

    # 4. Slide 7: Card do 5º Ano A e B empilhado abaixo do 4º Ano
    card_4ano_end = """                            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" download class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1.5 transition">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i> Baixar (7.58 MB)
                            </a>
                        </div>
                    </div>
                </div>"""

    card_5ano_html = card_4ano_end + """\n\n                <!-- Card 5º Ano A e B: 2.200 Laudas (POSICIONADO ABAIXO DO 4º ANO) -->
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
                </div>"""

    if card_4ano_end in html_norm:
        html_norm = html_norm.replace(card_4ano_end, card_5ano_html)
        print("Slide 7 Card do 5º Ano A e B empilhado com sucesso.")
    else:
        print("AVISO: Trecho do card do 4º ano não encontrado para empilhar.")

    final_html = html_norm.replace('\n', '\r\n')
    with open(DOCS_INDEX, 'w', encoding='utf-8') as f:
        f.write(final_html)
    shutil.copy(DOCS_INDEX, ROOT_INDEX)
    print(f"Salvo {DOCS_INDEX} e {ROOT_INDEX}.")

def atualizar_dashboard():
    if not os.path.exists(DOCS_DASH):
        return
    with open(DOCS_DASH, 'r', encoding='utf-8') as f:
        html = f.read()

    html_norm = html.replace('\r\n', '\n')

    btn_4ano_dash = """            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2.5 py-1.5 rounded-lg bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/70 transition flex items-center gap-1.5 font-semibold text-xs"
                title="Dossiê Pedagógico Mestre 4º Ano A e B (1.720 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-indigo-400"></i> Dossiê 4º Ano A e B (1720p)
            </a>"""

    btn_5ano_dash = btn_4ano_dash + """\n            <a href="DOSSIE_MESTRE_5ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2.5 py-1.5 rounded-lg bg-emerald-900/60 hover:bg-emerald-800 text-emerald-200 border border-emerald-700/70 transition flex items-center gap-1.5 font-semibold text-xs"
                title="Dossiê Pedagógico Mestre 5º Ano A e B (2.200 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-emerald-400"></i> Dossiê 5º Ano A e B (2200p)
            </a>"""

    if btn_4ano_dash in html_norm:
        html_norm = html_norm.replace(btn_4ano_dash, btn_5ano_dash)
        print("Dashboard atualizado com botão do 5º Ano A e B.")

    final_html = html_norm.replace('\n', '\r\n')
    with open(DOCS_DASH, 'w', encoding='utf-8') as f:
        f.write(final_html)
    shutil.copy(DOCS_DASH, ROOT_DASH)
    print(f"Salvo {DOCS_DASH} e {ROOT_DASH}.")

def main():
    atualizar_index()
    atualizar_dashboard()

if __name__ == '__main__':
    main()
