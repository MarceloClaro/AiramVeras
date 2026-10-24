#!/usr/bin/env python3
"""
AIRAM CLI — Interface Unificada do Ecossistema Airam Veras 2026
Escola Municipal Airam Veras | CRATEÚS - CEARÁ | INEP: 23084995

Comando central para pedagogos, gestores, psicólogos e desenvolvedores.
Permite consultas analíticas, prontuário AEE/TOD, execução do pipeline
longitudinal, inicialização do dashboard web e emissão de fichas PIP.
"""

import sys
import os
import sqlite3
import argparse
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import time

# Garantir UTF-8 no Windows Console para evitar UnicodeEncodeError
if sys.platform == "win32":
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

ROOT_DIR = Path(__file__).resolve().parent
DB_PATH = ROOT_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"
DASHBOARD_FILE = ROOT_DIR / "dashboard.html"

# Cores ANSI para Terminal
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"

def print_banner():
    print(f"""{CYAN}{BOLD}
================================================================================
  🏫 ECOSSISTEMA EDUCACIONAL AIRAM VERAS 2026 — CLI CENTRAL
  Escola Municipal Airam Veras | INEP: 23084995 | Crateús - CE
  Base Canônica 3FN Auditável | Psicométrica TRI | Matriz de Markov
================================================================================{RESET}""")

def get_connection():
    if not DB_PATH.exists():
        print(f"{RED}Erro: Banco de dados não encontrado em {DB_PATH}.{RESET}")
        print("Execute primeiro: python -m datamining.src.construir_banco_ecossistema")
        sys.exit(1)
    return sqlite3.connect(DB_PATH)

def cmd_metas():
    """Exibe o diagnóstico das Metas A e B no console."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            ano_escolar,
            componente_curricular,
            total_avaliados,
            ROUND(taxa_adequacao_pct, 1),
            CASE WHEN taxa_adequacao_pct >= 80 THEN 'SIM' ELSE 'NÃO' END,
            total_atingiram_meta_b,
            ROUND((total_atingiram_meta_b * 100.0) / total_avaliados, 1)
        FROM vw_dashboard_escola_metas
        WHERE ciclo = 'I'
        ORDER BY ano_escolar, componente_curricular;
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"\n{BOLD}{BLUE}--- DIAGNÓSTICO OFICIAL DAS METAS A E B (CICLO I / 2026) ---{RESET}\n")
    header = f"{'Ano':<6} | {'Componente':<18} | {'Alunos':<7} | {'Adequação (%)':<14} | {'Meta A (80%)':<12} | {'Meta B (Alunos)':<15} | {'Meta B (%)':<10}"
    print(header)
    print("-" * len(header))
    for r in rows:
        ano = f"{r[0]}º Ano"
        comp = r[1]
        tot = r[2]
        adeq = f"{r[3]}%"
        meta_a = f"{GREEN}SIM{RESET}" if r[4] == 'SIM' else f"{YELLOW}NÃO{RESET}"
        mb_qtd = f"{r[5]} alunos"
        mb_pct = f"{r[6]}%"
        print(f"{ano:<6} | {comp:<18} | {tot:<7} | {adeq:<14} | {meta_a:<21} | {mb_qtd:<15} | {mb_pct:<10}")
    print("\n" + "=" * 80)

def cmd_estudante(termo=None):
    """Consulta ficha detalhada de estudante por ID ou lista por turma."""
    conn = get_connection()
    cur = conn.cursor()

    if not termo:
        termo = input(f"{BOLD}Digite o ID Seguro do Aluno ou Ano Escolar (ex: 3): {RESET}").strip()

    if termo.isdigit():
        ano = int(termo)
        cur.execute("""
            SELECT aluno_hash_id, componente_curricular, total_acertos, rendimento_pct,
                   nivel_desempenho_caed, atingiu_meta_a_adequado, lacuna_meta_b, codigo_cid10
            FROM vw_painel_intervencao_professor
            WHERE ano_escolar = ?
            ORDER BY total_acertos ASC
            LIMIT 25;
        """, (ano,))
        rows = cur.fetchall()
        print(f"\n{BOLD}--- AMOSTRA DE ESTUDANTES DO {ano}º ANO (25 ALUNOS) ---{RESET}")
        print(f"{'ID Hash':<15} | {'Matéria':<12} | {'Acertos':<8} | {'Nível':<16} | {'Meta A':<8} | {'Lacuna B':<8} | {'CID':<8}")
        print("-" * 85)
        for r in rows:
            print(f"{r[0][:12]}... | {r[1]:<12} | {r[2]:<8} | {r[4]:<16} | {'OK' if r[5] else 'Falta':<8} | {r[6]:<8} | {r[7] or '-':<8}")
    else:
        cur.execute("""
            SELECT aluno_hash_id, nome_turma, ano_escolar, componente_curricular, total_acertos,
                   total_oportunidades, rendimento_pct, nivel_desempenho_caed, atingiu_meta_a_adequado,
                   atingiu_meta_b_80pct, lacuna_meta_b, grupo_nome, possui_laudo_aee, codigo_cid10,
                   requer_manejo_tod_pbs, recurso_tempo_estendido_50pct
            FROM vw_painel_intervencao_professor
            WHERE aluno_hash_id LIKE ?;
        """, (f"%{termo}%",))
        rows = cur.fetchall()
        if not rows:
            print(f"{RED}Estudante não encontrado com o termo '{termo}'.{RESET}")
        else:
            print(f"\n{GREEN}{BOLD}=== PRONTUÁRIO PEDAGÓGICO DO ESTUDANTE ==={RESET}")
            r0 = rows[0]
            print(f"ID Seguro: {r0[0]}")
            print(f"Turma    : {r0[1]} ({r0[2]}º Ano)")
            print(f"Laudo AEE: {'SIM (CID: ' + str(r0[13]) + ')' if r0[12] else 'Sem Laudo / Neurotípico'}")
            if r0[14] == 1:
                print(f"{MAGENTA}{BOLD}>>> PROTOCOLO TOD/PBS ATIVO: Acomodação comportamental mandatória <<<{RESET}")
            print("-" * 60)
            for r in rows:
                print(f"Disciplina : {r[3]}")
                print(f"Pontuação  : {r[4]} / {r[5]} ({r[6]}%) | Nível CAEd: {r[7]}")
                print(f"Grupo Inter: {r[11]}")
                print(f"Meta A (Adequado): {'Alcançado' if r[8] else 'Em Fila'}")
                print(f"Meta B (80%+ Acertos): {'Alcançado' if r[9] else 'Faltam ' + str(r[10]) + ' acertos'}")
                print("-" * 40)
    conn.close()

def cmd_tod_aee():
    """Exibe os casos de AEE com destaque para o Protocolo TOD (F91.3 / PBS)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT aluno_hash_id, nome_turma, codigo_cid10, codigo_cid11, grupo_diagnostico,
               requer_manejo_tod_pbs, recurso_tempo_estendido_50pct, recurso_pausas_ativas_fracionadas,
               estrategias_manejo_recomendadas
        FROM vw_relatorio_aee_inclusao
        ORDER BY requer_manejo_tod_pbs DESC, codigo_cid10;
    """)
    rows = cur.fetchall()
    conn.close()

    print(f"\n{MAGENTA}{BOLD}================================================================================")
    print("  🧠 PRONTUÁRIO CLÍNICO DE AEE & PROTOCOLO TOD (F91.3 / 6C90)")
    print(f"================================================================================{RESET}")
    print(f"{'ID Seguro':<14} | {'Turma':<12} | {'CID-10':<7} | {'CID-11':<7} | {'Diagnóstico':<20} | {'Manejo TOD':<10}")
    print("-" * 80)
    for r in rows:
        tod_badge = f"{GREEN}SIM (PBS){RESET}" if r[5] == 1 else "Padrão"
        print(f"{r[0][:12]}... | {r[1]:<12} | {r[2]:<7} | {r[3]:<7} | {r[4]:<20} | {tod_badge}")
    
    print(f"\n{YELLOW}{BOLD}REGRAS DE CONDUTA OBRIGATÓRIAS PARA TOD (F91.3 / PBS):{RESET}")
    print("1. Escolha Controlada: Apresente 2 a 3 alternativas legítimas para tarefas e avaliações.")
    print("2. Desescalada: Jamais repreenda ou discuta em público com o aluno.")
    print("3. Reforço Positivo: Elogie imediatamente comportamentos colaborativos (proporção 4:1).")
    print("4. Proteção Psicométrica: Não interprete recusa como ausência de saber; aplique pausas ativas.")
    print("=" * 80)

def cmd_longitudinal():
    """Executa e exibe o resumo da análise longitudinal multi-ciclos."""
    print(f"{CYAN}Executando pipeline analítico longitudinal multi-ciclos...{RESET}")
    script = ROOT_DIR / "datamining" / "src" / "analise_longitudinal_multiciclos.py"
    os.system(f'python "{script}"')

def cmd_dashboard_web():
    """Inicia um servidor web local e abre o dashboard interativo no navegador."""
    script_gen = ROOT_DIR / "datamining" / "src" / "gerar_dashboard_web.py"
    os.system(f'python "{script_gen}"')

    porta = 8080
    url = f"http://localhost:{porta}/dashboard.html"

    print(f"\n{GREEN}{BOLD}🚀 Iniciando Servidor Web do Dashboard Airam Veras...{RESET}")
    print(f"Endereço: {CYAN}{url}{RESET}")
    print("Pressione Ctrl+C para encerrar o servidor quando terminar.\n")

    os.chdir(ROOT_DIR)
    webbrowser.open(url)

    server = HTTPServer(('localhost', porta), SimpleHTTPRequestHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Servidor web encerrado com sucesso.{RESET}")

def cmd_contraprova():
    """Roda a contraprova matemática e testes unitários."""
    print(f"{CYAN}Iniciando contraprova de 19.474 verificações e suíte de testes pytest...{RESET}")
    contra_script = ROOT_DIR / "datamining" / "evidencias" / "T10" / "contraprova.py"
    if contra_script.exists():
        os.system(f'python "{contra_script}"')
    else:
        os.system('pytest "datamining/tests"')

def menu_interativo():
    """Menu interativo principal para uso no terminal."""
    while True:
        print_banner()
        print(f"{BOLD}Escolha uma operação:{RESET}\n")
        print("  1. 📊 Diagnóstico Executivo das Metas A e B")
        print("  2. 🔍 Consultar Estudante por ID Seguro ou Turma")
        print("  3. 🧠 Prontuário AEE & Diretrizes de TOD (F91.3 / PBS)")
        print("  4. 🔄 Executar Análise Longitudinal Multi-Ciclos (Ciclos I, II e III)")
        print("  5. 🌐 Iniciar Dashboard Web Interativo no Navegador")
        print("  6. 📑 Gerar Fichas de Intervenção Pedagógica (PIP) e AEE")
        print("  7. 🧪 Executar Contraprova Matemática e Auditoria de Testes")
        print("  0. 🚪 Sair\n")
        
        escolha = input(f"{BOLD}Opção [0-7]: {RESET}").strip()

        if escolha == '1':
            cmd_metas()
            input(f"\n{CYAN}Pressione Enter para continuar...{RESET}")
        elif escolha == '2':
            cmd_estudante()
            input(f"\n{CYAN}Pressione Enter para continuar...{RESET}")
        elif escolha == '3':
            cmd_tod_aee()
            input(f"\n{CYAN}Pressione Enter para continuar...{RESET}")
        elif escolha == '4':
            cmd_longitudinal()
            input(f"\n{CYAN}Pressione Enter para continuar...{RESET}")
        elif escolha == '5':
            cmd_dashboard_web()
            break
        elif escolha == '6':
            script_pip = ROOT_DIR / "datamining" / "src" / "gerar_fichas_pip_aee.py"
            if script_pip.exists():
                os.system(f'python "{script_pip}"')
            else:
                print(f"{YELLOW}Gerando fichas...{RESET}")
            input(f"\n{CYAN}Pressione Enter para continuar...{RESET}")
        elif escolha == '7':
            cmd_contraprova()
            input(f"\n{CYAN}Pressione Enter para continuar...{RESET}")
        elif escolha == '0':
            print(f"\n{GREEN}Encerrando Airam CLI. Até logo!{RESET}\n")
            break
        else:
            print(f"{RED}Opção inválida.{RESET}")
            time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description="Airam CLI — Ecossistema Educacional Airam Veras")
    parser.add_argument("--metas", action="store_true", help="Exibe diagnóstico das Metas A e B")
    parser.add_argument("--aluno", type=str, help="Consulta prontuário do aluno por ID Seguro")
    parser.add_argument("--tod", action="store_true", help="Exibe casos e protocolo de TOD (F91.3 / PBS)")
    parser.add_argument("--longitudinal", action="store_true", help="Roda a análise longitudinal multi-ciclos")
    parser.add_argument("--web", action="store_true", help="Inicia o dashboard web no navegador")
    parser.add_argument("--contraprova", action="store_true", help="Executa a contraprova matemática")

    args = parser.parse_args()

    if args.metas:
        cmd_metas()
    elif args.aluno:
        cmd_estudante(args.aluno)
    elif args.tod:
        cmd_tod_aee()
    elif args.longitudinal:
        cmd_longitudinal()
    elif args.web:
        cmd_dashboard_web()
    elif args.contraprova:
        cmd_contraprova()
    else:
        menu_interativo()

if __name__ == "__main__":
    main()
