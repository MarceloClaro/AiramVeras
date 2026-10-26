# -*- coding: utf-8 -*-
"""
Atualização do README.md com a inclusão completa do Dossiê Mestre do 4º Ano A e B (1.720 Laudas, Bloco 24)
"""
import re

README_PATH = 'README.md'

def main():
    with open(README_PATH, 'r', encoding='utf-8') as f:
        text = f.read()

    # 1. Atualizar a tabela de Dossiês Mestres
    padrao = r"(\|\s*\*\*Dossi.*?Mestre 3.*?Ano\*\*.*?\*\*Bloco 21\*\*\s*\|)"
    m = re.search(padrao, text)
    if m:
        antiga = m.group(1)
        nova = antiga + "\n| **Dossiê Mestre 4º Ano (A e B)** | 42 estudantes (22 no 4º A + 20 no 4º B) | **1.720 laudas** | 40 laudas (INTEGRAL 35H, Matriz BNCC 4º Ano, Grafo 2D, DOIs, Diagnóstico A vs B) | 42 cadernos $\\times$ 40 laudas (4 custom + 26 LP Vol. 4 + 4 MAT Kumon + 6 custom) | `b4ef92b9744ce5f9314371f18e3ef2e6a362035ee38b369bb8c1908d68ae6811` | **Bloco 24** |"
        text = text.replace(antiga, nova)
        print("Tabela comparativa atualizada com 4º Ano A e B (1.720 laudas).")
    else:
        print("AVISO: Linha do 3º ano na tabela não encontrada.")

    # 2. Atualizar menção do padrão universal de lauda 27
    antiga_lauda27 = "(1º, 2º e 3º Anos)"
    nova_lauda27 = "(1º, 2º, 3º e 4º Anos)"
    if antiga_lauda27 in text:
        text = text.replace(antiga_lauda27, nova_lauda27)
        print("Menção da Lauda 27 atualizada para 1º a 4º Anos.")

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(text)
    print("README.md gravado com sucesso.")

if __name__ == '__main__':
    main()
