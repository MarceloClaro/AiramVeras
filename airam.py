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
WHITE = "\033[97m"
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
    """Exibe o prontuário de AEE com os protocolos clínicos de manejo para TODOS os CIDs da escola."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT aluno_hash_id, nome_turma, codigo_cid10, codigo_cid11, grupo_diagnostico,
               nomenclatura_oficial, requer_manejo_tod_pbs, recurso_tempo_estendido_50pct,
               recurso_ledor_oficial, recurso_transcritor_oficial, recurso_pausas_ativas_fracionadas,
               protocolo_sala_aula, protocolo_avaliativo_caed, fundamentacao_legal
        FROM vw_relatorio_aee_inclusao
        ORDER BY requer_manejo_tod_pbs DESC, codigo_cid10;
    """)
    rows = cur.fetchall()

    print(f"\n{MAGENTA}{BOLD}================================================================================")
    print("  🧠 PRONTUÁRIO CLÍNICO DE AEE & MATRIZ DE MANEJOS PARA TODOS OS CIDs")
    print(f"================================================================================{RESET}")
    print(f"{'ID Seguro':<14} | {'Turma':<12} | {'CID-10':<7} | {'CID-11':<7} | {'Diagnóstico':<20} | {'Protocolo Clínico':<18}")
    print("-" * 88)
    
    for r in rows:
        aid, turma, c10, c11, grupo, nome_cid, tod, t_est, ledor, trans, pausas, p_sala, p_prova, legal = r
        if tod == 1:
            manejo_tag = f"{GREEN}PBS / Desescalada{RESET}"
        elif c10 == 'F90.0':
            manejo_tag = f"{YELLOW}Foco / Pausa 20m{RESET}"
        elif c10 == 'F84.0':
            manejo_tag = f"{CYAN}TEACCH / +50% Tempo{RESET}"
        elif c10 == 'R48':
            manejo_tag = f"{BLUE}Ledor / Transcritor{RESET}"
        elif c10 == 'G40':
            manejo_tag = f"{MAGENTA}Neuroprotetor{RESET}"
        elif c10 == 'G80':
            manejo_tag = f"{GREEN}TA / Prancha CAA{RESET}"
        elif c10 == 'F72':
            manejo_tag = f"{YELLOW}PDI / Art. 59 LDB{RESET}"
        elif c10 == 'E10':
            manejo_tag = f"{CYAN}Glicemia Livre{RESET}"
        else:
            manejo_tag = f"{WHITE}Fluência Adaptada{RESET}"
            
        print(f"{aid[:12]}... | {turma:<12} | {c10:<7} | {c11:<7} | {grupo:<20} | {manejo_tag}")

    # Consulta ao catálogo completo de protocolos
    cur.execute("""
        SELECT codigo_cid10, codigo_cid11, grupo_diagnostico, nomenclatura_oficial,
               protocolo_sala_aula, protocolo_avaliativo_caed, fundamentacao_legal
        FROM dim_cid_catalogo
        ORDER BY codigo_cid10;
    """)
    cids_cat = cur.fetchall()
    conn.close()

    print(f"\n{CYAN}{BOLD}================================================================================")
    print("  📋 PROTOCOLOS CLÍNICOS E REGRAS DE MANEJO POR CID (SALA DE AULA & PROVAS)")
    print(f"================================================================================{RESET}")
    
    for c in cids_cat:
        c10, c11, grupo, nome_cid, p_sala, p_prova, legal = c
        print(f"\n{YELLOW}{BOLD}▶ CID-10: {c10} | CID-11: {c11} — {nome_cid.upper()} ({grupo}){RESET}")
        print(f"  {BOLD}🏫 Manejo em Sala de Aula:{RESET} {p_sala}")
        print(f"  {BOLD}📝 Manejo em Provas CAEd/SPAECE:{RESET} {p_prova}")
        print(f"  {BOLD}⚖️ Fundamentação Legal:{RESET} {legal}")
        print("  " + "-" * 76)

    print(f"\n{GREEN}{BOLD}>>> SÍNTESE DE CONDUTA PARA A EQUIPE PEDAGÓGICA E PSICÓLOGOS <<<{RESET}")
    print("1. TOD (F91.3): Escolha controlada (2 opções) e proibição absoluta de confronto público.")
    print("2. TDAH (F90.0): Pausas ativas a cada 20 min e provas fracionadas em blocos menores (Lei 14.254/21).")
    print("3. TEA (F84.0): Previsibilidade visual, redução sensorial e tempo estendido +50% (Lei 12.764/12).")
    print("4. Dislexia/Discalculia (R48): Ledor oficial, transcritor e material concreto liberado.")
    print("5. Epilepsia (G40): Reagendamento sem penalidade em crises recentes e monitoramento de fadiga.")
    print("6. Paralisia Cerebral (G80): Tecnologia Assistiva (TA) e prancha de Comunicação Alternativa (CAA).")
    print("7. Deficiência Intelectual (F72): PDI funcional e critérios de Terminalidade Específica (Art. 59 LDB).")
    print("8. Diabetes (E10): Acesso livre a água/banheiro e kit glicêmico na mesa durante exames.")
    print("================================================================================")

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
        print("  3. 🧠 Prontuário AEE & Manejos Clínicos para TODOS os CIDs (TOD, TEA, TDAH, Dislexia, etc.)")
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
    parser.add_argument("--aee", action="store_true", help="Exibe prontuário e protocolos de manejo de TODOS os CIDs")
    parser.add_argument("--manejos", action="store_true", help="Exibe catálogo completo de diretrizes clínicas por CID")
    parser.add_argument("--longitudinal", action="store_true", help="Roda a análise longitudinal multi-ciclos")
    parser.add_argument("--web", action="store_true", help="Inicia o dashboard web no navegador")
    parser.add_argument("--contraprova", action="store_true", help="Executa a contraprova matemática")

    args = parser.parse_args()

    if args.metas:
        cmd_metas()
    elif args.aluno:
        cmd_estudante(args.aluno)
    elif args.tod or args.aee or args.manejos:
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
