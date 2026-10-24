"""
Gerador de Fichas de Intervenção Pedagógica (PIP) e Prontuários AEE/TOD
Compila folhas de trabalho e protocolos clínicos formatados para impressão em folha A4.
Em conformidade com a LBI (Lei nº 13.146/15), Lei nº 14.254/21 e BNCC.
"""

import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"
OUT_PIP = ROOT_DIR / "datamining" / "relatorios" / "fichas_intervencao_pip.html"
OUT_AEE = ROOT_DIR / "datamining" / "relatorios" / "prontuario_aee_tod_impresso.html"

def gerar_fichas_pip():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Selecionar alunos em situação de alerta ou emergencial (Grupos G1 e G2)
    cur.execute("""
        SELECT 
            aluno_hash_id,
            nome_turma,
            ano_escolar,
            componente_curricular,
            total_acertos,
            total_oportunidades,
            rendimento_pct,
            nivel_desempenho_caed,
            CASE WHEN nivel_desempenho_caed IN ('Adequado', 'Avançado') THEN 0 ELSE MAX(0, 13 - total_acertos) END AS acertos_adicionais_para_meta_a,
            lacuna_meta_b,
            codigo_grupo,
            grupo_nome,
            CASE 
                WHEN nivel_desempenho_caed = 'Abaixo do Básico' THEN 'Recuperação intensiva de pré-requisitos fundamentais'
                ELSE 'Consolidação de habilidades estruturantes da BNCC'
            END AS foco_pedagogico,
            COALESCE(codigo_cid10, 'Sem Laudo') AS cid10,
            requer_manejo_tod_pbs
        FROM vw_painel_intervencao_professor
        WHERE codigo_grupo IN ('G1', 'G2')
        ORDER BY ano_escolar, componente_curricular, total_acertos ASC
        LIMIT 60;
    """)
    alunos = cur.fetchall()
    conn.close()

    html_cards = []
    for a in alunos:
        aid, turma, ano, comp, ac, op, pct, niv, faltam_a, faltam_b, gid, gname, foco, cid, tod = a
        card = f"""
        <div class="pip-card">
            <div class="pip-header">
                <div class="school-title">ESCOLA MUNICIPAL AIRAM VERAS | INEP: 23084995</div>
                <div class="doc-title">PLANO DE INTERVENÇÃO PEDAGÓGICA INDIVIDUALIZADO (PIP) — 2026</div>
                <div class="meta-badge">CICLO I ➔ CICLO II</div>
            </div>
            
            <div class="grid-2">
                <div><strong>ID Seguro Aluno:</strong> <span class="mono">{aid}</span></div>
                <div><strong>Turma / Ano:</strong> {turma} ({ano}º Ano)</div>
                <div><strong>Componente:</strong> {comp}</div>
                <div><strong>Grupo de Intervenção:</strong> <span class="badge badge-{gid.lower()}">{gname}</span></div>
            </div>

            <div class="stats-box">
                <div class="stat-item">
                    <span class="label">Pontuação Atual</span>
                    <span class="value">{ac} / {op} ({pct}%)</span>
                </div>
                <div class="stat-item">
                    <span class="label">Nível CAEd</span>
                    <span class="value alert">{niv}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Alvo Meta A (Adequado)</span>
                    <span class="value">+{faltam_a} acertos necessários</span>
                </div>
                <div class="stat-item">
                    <span class="label">Condição AEE</span>
                    <span class="value">{cid} {'(TOD/PBS ATIVO)' if tod else ''}</span>
                </div>
            </div>

            <div class="section-box">
                <div class="section-title">🎯 FOCO DIDÁTICO E PRIORIDADES CURRICULARES (BNCC & CAEd):</div>
                <p><strong>Diretriz Pedagógica:</strong> {foco}</p>
                <p><strong>Habilidades BNCC Críticas a Desenvolver:</strong></p>
                <ul class="skills-list">
                    <li><strong>Língua Portuguesa:</strong> EF0{ano}LP01 / EF0{ano}LP04 — Decodificação e fluência de leitura frasal com autonomia.</li>
                    <li><strong>Matemática:</strong> EF0{ano}MA02 / EF0{ano}MA06 — Significado das operações básicas e cálculo mental aplicado.</li>
                </ul>
            </div>

            <div class="action-checklist">
                <div class="section-title">📋 ROTEIRO DE AÇÕES DA EQUIPE DOCENTE:</div>
                <div class="check-item"><input type="checkbox"> Atendimento semanal em pequenos grupos homogêneos (3 a 5 alunos).</div>
                <div class="check-item"><input type="checkbox"> Adaptação de enunciados com apoio visual e vocabulário simplificado.</div>
                <div class="check-item"><input type="checkbox"> Avaliação formativa quinzenal de monitoramento de micro-metas.</div>
                <div class="check-item"><input type="checkbox"> Articulação com a Sala de Recursos Multifuncionais (AEE).</div>
            </div>

            <div class="signature-box">
                <div class="sig-line">Professor(a) Regente</div>
                <div class="sig-line">Coordenação Pedagógica</div>
                <div class="sig-line">Responsável Legal</div>
            </div>
        </div>
        """
        html_cards.append(card)

    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Fichas de Intervenção Pedagógica (PIP) — Escola Airam Veras</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f1f5f9;
            margin: 0;
            padding: 20px;
            color: #0f172a;
        }}
        .pip-card {{
            background: #ffffff;
            border: 2px solid #0f172a;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            page-break-after: always;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        }}
        .pip-header {{
            text-align: center;
            border-bottom: 2px solid #0f172a;
            padding-bottom: 10px;
            margin-bottom: 15px;
            position: relative;
        }}
        .school-title {{ font-size: 13px; font-weight: bold; color: #475569; }}
        .doc-title {{ font-size: 16px; font-weight: 800; color: #0f172a; margin: 4px 0; }}
        .meta-badge {{ display: inline-block; background: #0f172a; color: white; font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: bold; }}
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 12px; margin-bottom: 15px; }}
        .mono {{ font-family: monospace; font-size: 11px; }}
        .badge {{ padding: 2px 6px; border-radius: 4px; font-weight: bold; font-size: 11px; }}
        .badge-g1 {{ background: #fee2e2; color: #991b1b; border: 1px solid #f87171; }}
        .badge-g2 {{ background: #fef3c7; color: #92400e; border: 1px solid #fbbf24; }}
        .stats-box {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 6px; padding: 10px; margin-bottom: 15px; text-align: center; }}
        .stat-item .label {{ display: block; font-size: 10px; color: #64748b; text-transform: uppercase; font-weight: 600; }}
        .stat-item .value {{ font-size: 14px; font-weight: bold; color: #0f172a; }}
        .stat-item .alert {{ color: #dc2626; }}
        .section-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 12px; font-size: 12px; margin-bottom: 15px; }}
        .section-title {{ font-weight: bold; margin-bottom: 6px; color: #1e3a8a; }}
        .skills-list {{ margin: 5px 0 0 15px; padding: 0; }}
        .skills-list li {{ margin-bottom: 4px; }}
        .action-checklist {{ font-size: 12px; margin-bottom: 20px; }}
        .check-item {{ margin-bottom: 6px; }}
        .signature-box {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px; text-align: center; font-size: 11px; }}
        .sig-line {{ border-top: 1px solid #0f172a; padding-top: 5px; }}
        @media print {{
            body {{ background: transparent; padding: 0; }}
            .pip-card {{ box-shadow: none; margin: 0; border: 1px solid #000; }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 20px;" class="no-print">
        <button onclick="window.print()" style="padding: 10px 20px; background: #2563eb; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer;">
            🖨️ Imprimir Todas as Fichas de Intervenção (A4)
        </button>
    </div>
    {"".join(html_cards)}
</body>
</html>
"""
    OUT_PIP.parent.mkdir(parents=True, exist_ok=True)
    OUT_PIP.write_text(template, encoding="utf-8")
    print(f"   -> Fichas PIP gravadas em: {OUT_PIP}")

def gerar_prontuario_aee():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            aluno_hash_id,
            nome_turma,
            ano_escolar,
            codigo_cid10,
            codigo_cid11,
            grupo_diagnostico,
            nomenclatura_oficial,
            pdi_ativo,
            recurso_tempo_estendido_50pct,
            recurso_ledor_oficial,
            recurso_transcritor_oficial,
            recurso_ambiente_baixo_estimulo,
            recurso_pausas_ativas_fracionadas,
            requer_manejo_tod_pbs,
            estrategias_manejo_recomendadas
        FROM vw_relatorio_aee_inclusao
        ORDER BY requer_manejo_tod_pbs DESC, ano_escolar, codigo_cid10;
    """)
    casos = cur.fetchall()
    conn.close()

    html_casos = []
    for c in casos:
        aid, turma, ano, c10, c11, grupo, nome_cid, pdi, t_est, ledor, trans, amb, pausas, tod, estrat = c
        is_tod = (tod == 1)

        card = f"""
        <div class="aee-card {'tod-border' if is_tod else ''}">
            <div class="aee-header">
                <div>
                    <span class="aee-badge {'badge-tod' if is_tod else 'badge-aee'}">
                        {grupo} — CID-10: {c10} | CID-11: {c11}
                    </span>
                    <h2 class="aluno-name">{nome_cid}</h2>
                    <div class="turma-info">Turma: {turma} ({ano}º Ano) | ID Seguro: <span class="mono">{aid}</span></div>
                </div>
                <div class="pdi-status">
                    <strong>PDI:</strong> {'ATIVO' if pdi else 'INATIVO'}<br>
                    <strong>LBI:</strong> Conforme Art. 28
                </div>
            </div>

            {'<div class="tod-banner">⚠️ PROTOCOLO DE MANEJO COMPORTAMENTAL POSITIVO (PBS) ATIVO: Aluno com Transtorno Opositor Desafiador. Proibido confronto público. Usar técnica de escolha controlada.</div>' if is_tod else ''}

            <div class="grid-acessibilidade">
                <div class="acess-item {'active' if t_est else ''}">⏱️ Tempo Estendido +50%</div>
                <div class="acess-item {'active' if ledor else ''}">📖 Ledor Oficial Designado</div>
                <div class="acess-item {'active' if trans else ''}">✍️ Transcritor Oficial</div>
                <div class="acess-item {'active' if amb else ''}">🔇 Ambiente Baixo Estímulo</div>
                <div class="acess-item {'active' if pausas else ''}">⏸️ Pausas Ativas Fracionadas</div>
                <div class="acess-item active">📐 Materiais Concretos / Visuais</div>
            </div>

            <div class="estrat-box">
                <strong>Orientações Clínico-Pedagógicas para Sala de Aula:</strong><br>
                {estrat}
            </div>

            <div class="obs-box">
                <strong>Assinatura do Profissional do AEE / Sala de Recursos:</strong>
                <div style="margin-top: 25px; border-top: 1px solid #94a3b8; width: 300px; padding-top: 5px; font-size: 11px;">
                    Especialista em Educação Especial e Inclusiva
                </div>
            </div>
        </div>
        """
        html_casos.append(card)

    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Prontuário Clínico AEE & Protocolo TOD — Escola Airam Veras</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8fafc;
            padding: 20px;
            color: #0f172a;
        }}
        .aee-card {{
            background: #ffffff;
            border: 1px solid #cbd5e1;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 25px;
            page-break-after: always;
        }}
        .tod-border {{
            border: 2px solid #7c3aed;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15);
        }}
        .aee-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 12px;
            margin-bottom: 15px;
        }}
        .aee-badge {{
            display: inline-block;
            font-size: 11px;
            font-weight: bold;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
        }}
        .badge-tod {{ background: #7c3aed; color: #ffffff; }}
        .badge-aee {{ background: #2563eb; color: #ffffff; }}
        .aluno-name {{ font-size: 16px; font-weight: bold; margin: 6px 0 2px 0; color: #0f172a; }}
        .turma-info {{ font-size: 12px; color: #64748b; }}
        .mono {{ font-family: monospace; }}
        .pdi-status {{ text-align: right; font-size: 11px; color: #047857; font-weight: bold; }}
        .tod-banner {{
            background: #f5f3ff;
            border: 1px solid #c4b5fd;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            color: #5b21b6;
            font-weight: 600;
            margin-bottom: 15px;
        }}
        .grid-acessibilidade {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 15px;
        }}
        .acess-item {{
            border: 1px dashed #cbd5e1;
            padding: 8px;
            border-radius: 6px;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
        }}
        .acess-item.active {{
            border: 1px solid #10b981;
            background: #ecfdf5;
            color: #065f46;
            font-weight: bold;
        }}
        .estrat-box {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 12px;
            font-size: 12px;
            line-height: 1.5;
            margin-bottom: 15px;
        }}
        .obs-box {{ font-size: 12px; margin-top: 20px; }}
        @media print {{
            body {{ background: transparent; padding: 0; }}
            .aee-card {{ margin: 0; box-shadow: none; border: 1px solid #000; }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 20px;" class="no-print">
        <button onclick="window.print()" style="padding: 10px 20px; background: #7c3aed; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer;">
            🖨️ Imprimir Todos os Prontuários AEE & Protocolos TOD
        </button>
    </div>
    {"".join(html_casos)}
</body>
</html>
"""
    OUT_AEE.parent.mkdir(parents=True, exist_ok=True)
    OUT_AEE.write_text(template, encoding="utf-8")
    print(f"   -> Prontuários AEE/TOD gravados em: {OUT_AEE}")

def main():
    print("1. Gerando Fichas de Intervenção Pedagógica (PIP) prontas para imprimir...")
    gerar_fichas_pip()

    print("2. Gerando Prontuários Clínicos de AEE e Protocolo TOD...")
    gerar_prontuario_aee()

    print("\nFichas e Prontuários gerados com sucesso total!")

if __name__ == "__main__":
    main()
