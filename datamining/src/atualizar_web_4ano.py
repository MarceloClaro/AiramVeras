# -*- coding: utf-8 -*-
"""
Atualização Cirúrgica de docs/index.html e index.html para Incluir o Dossiê Mestre do 4º Ano A e B (1.720 Laudas)
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

    # Ocorrência 1: Header
    btn_3ano_header = """            <a href="DOSSIE_MESTRE_3ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2 py-1.5 rounded-lg bg-blue-900/60 hover:bg-blue-800 text-blue-200 border border-blue-700/70 transition flex items-center gap-1 font-semibold text-[11px]"
                title="Dossiê Pedagógico Mestre 3º Ano (1.000 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-blue-400"></i> 3º Ano (1000p)
            </a>"""

    btn_4ano_header = btn_3ano_header + """\n            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2 py-1.5 rounded-lg bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/70 transition flex items-center gap-1 font-semibold text-[11px]"
                title="Dossiê Pedagógico Mestre 4º Ano A e B (1.720 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-indigo-400"></i> 4º Ano A e B (1720p)
            </a>"""

    # Ocorrência 2: Hero Badges (Pills)
    pill_3ano = """                    <a href="DOSSIE_MESTRE_3ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="attribute-pill font-mono text-blue-300 border-blue-500/40 hover:bg-blue-500/20 transition flex items-center gap-1">
                        <i data-lucide="file-spreadsheet" class="w-3 h-3"></i> 3º Ano (1.000p)
                    </a>"""

    pill_4ano = pill_3ano + """\n                    <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="attribute-pill font-mono text-indigo-300 border-indigo-500/40 hover:bg-indigo-500/20 transition flex items-center gap-1">
                        <i data-lucide="file-spreadsheet" class="w-3 h-3"></i> 4º Ano A e B (1.720p)
                    </a>"""

    # Ocorrência 3: Hero CTA
    cta_3ano = """                    <a href="DOSSIE_MESTRE_3ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="px-3 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold transition flex items-center gap-1.5 shadow-lg shadow-blue-600/30 text-xs">
                        <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i> 3º Ano (1000p)
                    </a>"""

    cta_4ano = cta_3ano + """\n                    <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                        class="px-3 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold transition flex items-center gap-1.5 shadow-lg shadow-indigo-600/30 text-xs">
                        <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5"></i> 4º Ano A e B (1720p)
                    </a>"""

    # Ocorrência 4 e 5: Slide 7 Card
    card_3ano_full_end = """                            <a href="DOSSIE_MESTRE_3ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" download class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1.5 transition">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i> Baixar (5.90 MB)
                            </a>
                        </div>
                    </div>
                </div>"""

    card_4ano_full = card_3ano_full_end + """\n\n                <!-- Card 4º Ano A e B: 1.720 Laudas (POSICIONADO ABAIXO DO 3º ANO) -->
                <div class="p-6 rounded-2xl glass-card border border-indigo-500/40 bg-gradient-to-r from-indigo-950/40 via-slate-900/80 to-purple-950/40 text-left shadow-2xl relative overflow-hidden">
                    <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                        <div class="space-y-2">
                            <div class="flex flex-wrap items-center gap-2">
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-indigo-500/20 text-indigo-300 border border-indigo-500/40">4º ANO A e B • COORTE 42 ESTUDANTES</span>
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40">1.720 LAUDAS VETORIAIS A4</span>
                                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">LEDGER SHA-256 (BLOCO 24)</span>
                            </div>
                            <h3 class="text-lg md:text-xl font-black text-white flex items-center gap-2">
                                <i data-lucide="file-spreadsheet" class="w-5 h-5 text-indigo-400"></i>
                                Dossiê Pedagógico Mestre 4º Ano (Turmas A e B) — BNCC, PEI/PAEE & Práticas Diárias Ampliadas
                            </h3>
                            <p class="text-xs text-slate-300 max-w-4xl leading-relaxed">
                                Total de exatamente <strong>1.720 laudas vetoriais A4</strong>: 40 laudas de Front Matter Master (Matriz Oficial <strong>INTEGRAL 35H SME Crateús</strong> com 7 aulas diárias de 50 min, bioestatística com guia leigo, modelagem de Markov, EWS, trilha Kumon Níveis B e C de multiplicação/divisão e índice remissivo nominal com início de página exato por turma) + <strong>42 Cadernos Individuais de 40 laudas cada</strong> (22 alunos da Turma 4º Ano A + 20 alunos da Turma 4º Ano B), integrando 26 laudas de Língua Portuguesa/Fônico do Volume 4, 4 laudas de Matemática Kumon (operações verticais de múltiplos dígitos, frações e problemas SPAECE D01-D28) e 6 laudas multidisciplinares (Ciências, Geografia, História, Arte, Educação Física, BNCC Computação e Termo Forense com fé pública).
                            </p>
                        </div>
                        <div class="flex flex-row md:flex-col gap-2 shrink-0">
                            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank" class="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 flex items-center justify-center gap-2 transition">
                                <i data-lucide="external-link" class="w-4 h-4"></i> Abrir Dossiê (PDF)
                            </a>
                            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" download class="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1.5 transition">
                                <i data-lucide="download" class="w-3.5 h-3.5"></i> Baixar (7.58 MB)
                            </a>
                        </div>
                    </div>
                </div>"""

    # Normalizar quebras de linha para garantir match 100%
    html_norm = html.replace('\r\n', '\n')

    if btn_3ano_header in html_norm:
        html_norm = html_norm.replace(btn_3ano_header, btn_4ano_header)
        print("Header atualizado com sucesso.")
    else:
        print("Aviso: Header não casou.")

    if pill_3ano in html_norm:
        html_norm = html_norm.replace(pill_3ano, pill_4ano)
        print("Hero Pills atualizados com sucesso.")
    else:
        print("Aviso: Hero Pills não casou.")

    if cta_3ano in html_norm:
        html_norm = html_norm.replace(cta_3ano, cta_4ano)
        print("Hero CTA atualizado com sucesso.")
    else:
        print("Aviso: Hero CTA não casou.")

    if card_3ano_full_end in html_norm:
        html_norm = html_norm.replace(card_3ano_full_end, card_4ano_full)
        print("Slide 7 Card empilhado com sucesso.")
    else:
        print("Aviso: Card 3º ano não casou.")

    # Restaurar CRLF
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

    btn_3ano_dash = """            <a href="DOSSIE_MESTRE_3ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2.5 py-1.5 rounded-lg bg-blue-900/60 hover:bg-blue-800 text-blue-200 border border-blue-700/70 transition flex items-center gap-1.5 font-semibold text-xs"
                title="Dossiê Pedagógico Mestre 3º Ano (1.000 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-blue-400"></i> Dossiê 3º Ano (1000p)
            </a>"""

    btn_4ano_dash = btn_3ano_dash + """\n            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2.5 py-1.5 rounded-lg bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/70 transition flex items-center gap-1.5 font-semibold text-xs"
                title="Dossiê Pedagógico Mestre 4º Ano A e B (1.720 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-indigo-400"></i> Dossiê 4º Ano A e B (1720p)
            </a>"""

    html_norm = html.replace('\r\n', '\n')
    if btn_3ano_dash in html_norm:
        html_norm = html_norm.replace(btn_3ano_dash, btn_4ano_dash)
        print("Dashboard atualizado com botão do 4º Ano A e B.")
    else:
        # tentar replace genérico de 3ANO
        idx = html_norm.find('DOSSIE_MESTRE_3ANO')
        if idx != -1:
            end_a = html_norm.find('</a>', idx) + 4
            bloco_3 = html_norm[idx-60:end_a]
            novo_b = bloco_3 + """\n            <a href="DOSSIE_MESTRE_4ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf" target="_blank"
                class="px-2.5 py-1.5 rounded-lg bg-indigo-900/60 hover:bg-indigo-800 text-indigo-200 border border-indigo-700/70 transition flex items-center gap-1.5 font-semibold text-xs"
                title="Dossiê Pedagógico Mestre 4º Ano A e B (1.720 Laudas Vetoriais A4)">
                <i data-lucide="file-spreadsheet" class="w-3.5 h-3.5 text-indigo-400"></i> Dossiê 4º Ano A e B (1720p)
            </a>"""
            html_norm = html_norm[:idx-60] + novo_b + html_norm[end_a:]
            print("Dashboard atualizado via busca de bloco.")

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
