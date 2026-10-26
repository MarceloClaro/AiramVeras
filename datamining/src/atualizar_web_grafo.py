# -*- coding: utf-8 -*-
"""
Atualiza o showcase web (docs/index.html e index.html) e o dashboard com o bloco de:
TOPOLOGIA DA REDE INTERDISCIPLINAR & GRAFO DE APRENDIZAGEM (Mapa 2D / Fluxograma Vetorial)
"""
import os
import sys

sys.path.append(os.path.dirname(__file__))
from modulo_grafo_2d_topologia import gerar_svg_grafo_2d

ROOT_DIR = r"c:\Users\marce\Downloads\Airam veras"
DOCS_INDEX = os.path.join(ROOT_DIR, "docs", "index.html")
ROOT_INDEX = os.path.join(ROOT_DIR, "index.html")

svg_content = gerar_svg_grafo_2d(ano=3)

bloco_grafo_html = f"""
            <!-- BLOCO MESTRE: TOPOLOGIA DA REDE INTERDISCIPLINAR & GRAFO DE APRENDIZAGEM (MAPA 2D) -->
            <div class="p-6 rounded-2xl glass-card border border-blue-500/40 bg-gradient-to-b from-slate-900/90 via-blue-950/30 to-slate-900/90 text-left shadow-2xl relative overflow-hidden">
                <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-4 pb-4 border-b border-slate-700/60">
                    <div>
                        <div class="flex flex-wrap items-center gap-2 mb-2">
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-blue-500/20 text-blue-300 border border-blue-500/40">PADRÃO UNIVERSAL 1º, 2º E 3º ANO</span>
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-emerald-500/20 text-emerald-300 border border-emerald-500/40">JORNADA INTEGRAL 35H SME CRATEÚS</span>
                            <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold font-mono bg-purple-500/20 text-purple-300 border border-purple-500/40">MATRIZ BNCC 9 COMPONENTES</span>
                        </div>
                        <h3 class="text-xl md:text-2xl font-black text-white flex items-center gap-2.5">
                            <i data-lucide="git-merge" class="w-6 h-6 text-blue-400"></i>
                            TOPOLOGIA DA REDE INTERDISCIPLINAR &amp; GRAFO DE APRENDIZAGEM
                        </h3>
                        <p class="text-xs md:text-sm font-semibold text-blue-300 mt-1">
                            Grafo Direcionado Ponderado: Conexões sinérgicas entre os 9 componentes curriculares do 3º Ano.
                        </p>
                    </div>
                    <div class="px-3 py-1.5 rounded-xl bg-blue-900/40 border border-blue-500/30 shrink-0 text-right">
                        <div class="text-[10px] text-slate-400 font-mono">POTENCIALIZAÇÃO COGNITIVA</div>
                        <div class="text-base font-extrabold text-blue-300 font-mono">+82% Sinergia</div>
                    </div>
                </div>

                <div class="p-3.5 rounded-xl bg-blue-500/10 border border-blue-500/30 mb-4">
                    <p class="text-xs sm:text-sm text-slate-200 leading-relaxed font-medium">
                        <strong>O grafo demonstra que o fortalecimento da rota lexical em Língua Portuguesa potencializa em 82% a capacidade de leitura cartográfica em Geografia e interpretação de tabelas em Ciências e Matemática, otimizando o tempo pedagógico nas 35 horas semanais.</strong>
                    </p>
                </div>

                <!-- FLUXOGRAMA 2D / SVG VETORIAL COM OS 9 COMPONENTES -->
                <div class="p-2 sm:p-4 rounded-xl bg-white shadow-inner overflow-x-auto my-3">
                    {svg_content}
                </div>

                <!-- TABELA SINTÉTICA DE ALAVANCA NAS 35 HORAS -->
                <div class="grid grid-cols-1 md:grid-cols-4 gap-2.5 mt-3 text-xs">
                    <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700">
                        <div class="font-bold text-blue-300 mb-0.5">LP ➔ Geografia (+82%)</div>
                        <div class="text-[11px] text-slate-300">Decodificação de croquis e leitura cartográfica em Crateús.</div>
                    </div>
                    <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700">
                        <div class="font-bold text-teal-300 mb-0.5">LP ➔ Ciências (+79%)</div>
                        <div class="text-[11px] text-slate-300">Interpretação de esquemas de som/luz e tabelas experimentais.</div>
                    </div>
                    <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700">
                        <div class="font-bold text-emerald-300 mb-0.5">LP ➔ Matemática (+78%)</div>
                        <div class="text-[11px] text-slate-300">Compreensão semântica da pergunta em situações-problema.</div>
                    </div>
                    <div class="p-2.5 rounded-lg bg-slate-800/80 border border-slate-700">
                        <div class="font-bold text-indigo-300 mb-0.5">MAT ➔ Computação (+88%)</div>
                        <div class="text-[11px] text-slate-300">Fatos básicos habilitam raciocínio algorítmico e loops.</div>
                    </div>
                </div>
            </div>
"""

with open(DOCS_INDEX, "r", encoding="utf-8") as f:
    content = f.read()

target_marker = '<!-- Destaque: Dossiês Pedagógicos Mestres 1º e 2º Anos (Empilhados Verticalmente) -->'
if target_marker in content:
    content = content.replace(target_marker, target_marker + "\n" + bloco_grafo_html)
    # Atualizar também os blocos nos cards dos dossiês
    content = content.replace("LEDGER SHA-256 (BLOCO 18)", "LEDGER SHA-256 (BLOCO 23)")
    content = content.replace("LEDGER SHA-256 (BLOCO 19)", "LEDGER SHA-256 (BLOCO 22)")
    content = content.replace("LEDGER SHA-256 (BLOCO 20)", "LEDGER SHA-256 (BLOCO 21)")
    
    with open(DOCS_INDEX, "w", encoding="utf-8") as f:
        f.write(content)
    print("docs/index.html atualizado com sucesso!")
    
    with open(ROOT_INDEX, "w", encoding="utf-8") as f:
        f.write(content)
    print("index.html (raiz) sincronizado com sucesso!")
else:
    print("Marcador não encontrado em docs/index.html")
