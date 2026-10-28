# -*- coding: utf-8 -*-
"""
Script de Recompilação e Auditoria Universal dos Cadernos Customizados de Estudantes (1º ao 5º Ano)
Escola de Cidadania Airam Veras • Ano Letivo 2026
Garante que todos os arquivos HTML e PDFs das 5 turmas incorporem integralmente os dados de PAEE, PEI, CIDs e Estudos de Caso.
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

import gerar_dossie_1000_laudas_multidisciplinar as g1
import gerar_dossie_2ano_1160_laudas_multidisciplinar as g2
import gerar_dossie_3ano_1000_laudas_multidisciplinar as g3
import gerar_dossie_4ano_1720_laudas_multidisciplinar as g4
import gerar_dossie_5ano_2200_laudas_multidisciplinar as g5

def recompilar_tudo():
    print("=" * 70)
    print("RECOMPILAÇÃO DOS CADERNOS DE ESTUDANTES DE TODAS AS TURMAS (1º AO 5º ANO)")
    print("=" * 70)

    # 1º Ano
    t0 = time.time()
    print("\n[1/5] Compilando cadernos do 1º Ano (24 estudantes)...")
    g1.build_students_custom_pages()
    print(f"-> 1º Ano concluído em {time.time() - t0:.1f}s")

    # 2º Ano
    t0 = time.time()
    print("\n[2/5] Compilando cadernos do 2º Ano (28 estudantes - inclui Icaro Soares)...")
    g2.build_students_custom_pages()
    print(f"-> 2º Ano concluído em {time.time() - t0:.1f}s")

    # 3º Ano
    t0 = time.time()
    print("\n[3/5] Compilando cadernos do 3º Ano (24 estudantes - inclui Alice e Sofia Coelho)...")
    g3.build_students_custom_pages()
    print(f"-> 3º Ano concluído em {time.time() - t0:.1f}s")

    # 4º Ano
    t0 = time.time()
    print("\n[4/5] Compilando cadernos do 4º Ano (42 estudantes - Turmas 4º A e 4º B)...")
    g4.build_students_custom_pages()
    print(f"-> 4º Ano concluído em {time.time() - t0:.1f}s")

    # 5º Ano
    t0 = time.time()
    print("\n[5/5] Compilando cadernos do 5º Ano (54 estudantes - Turmas 5º A e 5º B)...")
    g5.build_students_custom_pages()
    print(f"-> 5º Ano concluído em {time.time() - t0:.1f}s")

    print("\n" + "=" * 70)
    print("TODAS AS 5 TURMAS FORAM RECOMPILADAS COM SUCESSO ABSOLUTO!")
    print("=" * 70)

if __name__ == "__main__":
    recompilar_tudo()
