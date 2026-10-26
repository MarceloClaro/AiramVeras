# -*- coding: utf-8 -*-
import json

def main():
    with open('datamining/dados/estudantes_4ano_mapeados.json', 'r', encoding='utf-8') as f:
        alunos = json.load(f)

    turma_a = [a for a in alunos if a['turma_caed'].strip().endswith('A')]
    turma_b = [a for a in alunos if a['turma_caed'].strip().endswith('B')]
    
    print(f"Total Turma 4º Ano A: {len(turma_a)}")
    for i, a in enumerate(turma_a):
        print(f"  A{i+1:02d}: {a['nome']} | AEE: {a['laudo_aee']} | {a['cluster']}")

    print(f"\nTotal Turma 4º Ano B: {len(turma_b)}")
    for i, a in enumerate(turma_b):
        print(f"  B{i+1:02d}: {a['nome']} | AEE: {a['laudo_aee']} | {a['cluster']}")

    print(f"\nTotal Geral: {len(turma_a) + len(turma_b)}")

if __name__ == '__main__':
    main()
