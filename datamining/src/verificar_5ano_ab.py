# -*- coding: utf-8 -*-
import json

def main():
    with open('datamining/dados/estudantes_5ano_mapeados.json', 'r', encoding='utf-8') as f:
        alunos = json.load(f)

    turma_a = [a for a in alunos if a['turma_caed'].strip().endswith('A')]
    turma_b = [a for a in alunos if a['turma_caed'].strip().endswith('B')]

    print(f"=== TURMA 5º ANO A ({len(turma_a)} alunos) ===")
    for i, a in enumerate(turma_a):
        print(f"  A{i+1:02d}: {a['nome']} | AEE: {a['laudo_aee']} | {a['cluster']}")

    print(f"\n=== TURMA 5º ANO B ({len(turma_b)} alunos) ===")
    for i, a in enumerate(turma_b):
        print(f"  B{i+1:02d}: {a['nome']} | AEE: {a['laudo_aee']} | {a['cluster']}")

if __name__ == '__main__':
    main()
