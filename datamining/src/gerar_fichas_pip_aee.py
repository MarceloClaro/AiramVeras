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
            estrategias_manejo_recomendadas,
            protocolo_sala_aula,
            protocolo_avaliativo_caed,
            fundamentacao_legal,
            observacoes_clinico_pedagogicas
        FROM vw_relatorio_aee_inclusao
        ORDER BY requer_manejo_tod_pbs DESC, ano_escolar, codigo_cid10;
    """)
    casos = cur.fetchall()
    conn.close()

    html_casos = []
    for c in casos:
        (aid, turma, ano, c10, c11, grupo, nome_cid, pdi, t_est, ledor, trans, amb, 
         pausas, tod, estrat, p_sala, p_prova, legal, obs) = c
        is_tod = (tod == 1)

        # Determina o banner específico por CID
        if is_tod:
            banner_html = """<div class="cid-banner banner-tod">
                <strong>⚠️ PROTOCOLO DE MANEJO COMPORTAMENTAL POSITIVO (PBS) ATIVO (TOD / F91.3):</strong><br>
                Proibição absoluta de confronto público. Técnica da escolha controlada (2 opções válidas). Desescalada em tom de voz neutro.
            </div>"""
            border_cls = "tod-border"
        elif c10 == 'F90.0':
            banner_html = f"""<div class="cid-banner banner-tdah">
                <strong>⚡ PROTOCOLO NEUROEXECUTIVO & ATENÇÃO PLENA (TDAH / F90.0 — Lei 14.254/21):</strong><br>
                Pausas ativas a cada 20 min. Caderno de avaliação fracionado em blocos menores. Primeira carteira e redução de distratores.
            </div>"""
            border_cls = "tdah-border"
        elif c10 == 'F84.0':
            banner_html = f"""<div class="cid-banner banner-tea">
                <strong>🧩 PROTOCOLO ESTRUTURADO TEACCH & REGULAÇÃO SENSORIAL (TEA / F84.0 — Lei 12.764/12):</strong><br>
                Previsibilidade de rotina visual. Sala de baixo estímulo auditivo/visual. Tempo estendido (+50%) e mediador não-indutivo.
            </div>"""
            border_cls = "tea-border"
        elif c10 == 'R48':
            banner_html = f"""<div class="cid-banner banner-dislexia">
                <strong>📖 PROTOCOLO DE ACESSIBILIDADE TEXTUAL & SIMBÓLICA (DISLEXIA / R48 — Lei 14.254/21):</strong><br>
                Ledor e transcritor oficial mandatória. Tipografia OpenDyslexic (14pt+). Não penalização ortográfica. Material concreto e calculadora básica.
            </div>"""
            border_cls = "dislexia-border"
        elif c10 == 'G40':
            banner_html = f"""<div class="cid-banner banner-neuro">
                <strong>🧠 PROTOCOLO NEUROPROTETOR & SEGURANÇA (EPILEPSIA / G40 — Lei Lucas 13.722/18):</strong><br>
                Direito a reagendamento de provas se houver crise nas 48h anteriores. Tolerância à lentificação medicamentosa.
            </div>"""
            border_cls = "neuro-border"
        elif c10 == 'G80':
            banner_html = f"""<div class="cid-banner banner-ta">
                <strong>♿ PROTOCOLO DE TECNOLOGIA ASSISTIVA & CAA (PARALISIA CEREBRAL / G80 — LBI Art. 74):</strong><br>
                Prancha de Comunicação Alternativa (CAA). Transcritor oficial para respostas por apontamento ou voz. Mobiliário ergonômico.
            </div>"""
            border_cls = "ta-border"
        elif c10 == 'F72':
            banner_html = f"""<div class="cid-banner banner-di">
                <strong>🎯 PROTOCOLO DE ADEQUAÇÃO CURRICULAR & PDI (DEFICIÊNCIA INTELECTUAL / F72 — LDB Art. 59):</strong><br>
                Avaliação formativa adaptada às metas do PDI. Suporte concreto contínuo. Aplicação de critérios de Terminalidade Específica.
            </div>"""
            border_cls = "di-border"
        elif c10 == 'E10':
            banner_html = f"""<div class="cid-banner banner-diab">
                <strong>🩸 PROTOCOLO METABÓLICO ESCOLAR (DIABETES TIPO 1 / E10 — Lei 13.895/19):</strong><br>
                Livre acesso a água e sanitários sem restrição. Monitoramento glicêmico na mesa da prova e pausa imediata de tempo em hipoglicemia.
            </div>"""
            border_cls = "diab-border"
        else:
            banner_html = f"""<div class="cid-banner banner-malform">
                <strong>🌱 PROTOCOLO DE EQUIDADE FONOAUDIOLÓGICA (MALFORMAÇÃO / {c10}):</strong><br>
                Dispensa de penalidade na prova cronometrada de Fluência Oral CAEd. Valorização das habilidades receptivas e multissensoriais.
            </div>"""
            border_cls = "malform-border"

        card = f"""
        <div class="aee-card {border_cls}">
            <div class="aee-header">
                <div>
                    <span class="aee-badge badge-{grupo.lower().replace(' ', '-')}">
                        {grupo} — CID-10: {c10} | CID-11: {c11}
                    </span>
                    <h2 class="aluno-name">{nome_cid}</h2>
                    <div class="turma-info">Turma: {turma} ({ano}º Ano) | ID Seguro: <span class="mono">{aid}</span></div>
                </div>
                <div class="pdi-status">
                    <strong>PDI:</strong> {'ATIVO' if pdi else 'INATIVO'}<br>
                    <strong>Amparo:</strong> Conforme LBI Art. 28
                </div>
            </div>

            {banner_html}

            <div class="grid-acessibilidade">
                <div class="acess-item {'active' if t_est else ''}">⏱️ Tempo Estendido +50%</div>
                <div class="acess-item {'active' if ledor else ''}">📖 Ledor Oficial Designado</div>
                <div class="acess-item {'active' if trans else ''}">✍️ Transcritor Oficial</div>
                <div class="acess-item {'active' if amb else ''}">🔇 Ambiente Baixo Estímulo</div>
                <div class="acess-item {'active' if pausas else ''}">⏸️ Pausas Ativas Fracionadas</div>
                <div class="acess-item active">📐 Apoio Concreto & Visual</div>
            </div>

            <div class="estrat-box">
                <strong>🏫 Manejo Obrigatório em Sala de Aula Regular:</strong><br>
                {p_sala or estrat}
            </div>

            <div class="prova-box">
                <strong>📝 Protocolo para Aplicação de Avaliações (CAEd, SPAECE e SAEB):</strong><br>
                {p_prova or 'Aplicação com acessibilidade garantida e pausas fracionadas.'}
            </div>

            <div class="legal-box">
                <strong>⚖️ Fundamentação Legal e Jurídica:</strong><br>
                <em>{legal or 'Lei Brasileira de Inclusão (Lei 13.146/2015)'}</em>
            </div>

            <div class="obs-box">
                <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-top: 15px;">
                    <div>
                        <strong>Observações da Sala de Recursos:</strong> {obs or 'Seguir as metas individualizadas do PDI.'}
                    </div>
                    <div style="text-align: center; border-top: 1px solid #94a3b8; width: 280px; padding-top: 5px; font-size: 11px;">
                        Profissional Especialista de AEE / Coordenação
                    </div>
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
        .tod-border {{ border: 2px solid #7c3aed; box-shadow: 0 4px 12px rgba(124, 58, 237, 0.15); }}
        .tdah-border {{ border: 2px solid #d97706; box-shadow: 0 4px 12px rgba(217, 119, 6, 0.15); }}
        .tea-border {{ border: 2px solid #0284c7; box-shadow: 0 4px 12px rgba(2, 132, 199, 0.15); }}
        .dislexia-border {{ border: 2px solid #2563eb; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15); }}
        .neuro-border {{ border: 2px solid #9333ea; box-shadow: 0 4px 12px rgba(147, 51, 234, 0.15); }}
        .ta-border {{ border: 2px solid #059669; box-shadow: 0 4px 12px rgba(5, 150, 105, 0.15); }}
        .di-border {{ border: 2px solid #ea580c; box-shadow: 0 4px 12px rgba(234, 88, 12, 0.15); }}
        .diab-border {{ border: 2px solid #0891b2; box-shadow: 0 4px 12px rgba(8, 145, 178, 0.15); }}
        .malform-border {{ border: 2px solid #475569; box-shadow: 0 4px 12px rgba(71, 85, 105, 0.15); }}

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
            background: #2563eb;
            color: #ffffff;
        }}
        .badge-tod {{ background: #7c3aed; color: #ffffff; }}
        .badge-aee {{ background: #2563eb; color: #ffffff; }}
        .aluno-name {{ font-size: 16px; font-weight: bold; margin: 6px 0 2px 0; color: #0f172a; }}
        .turma-info {{ font-size: 12px; color: #64748b; }}
        .mono {{ font-family: monospace; }}
        .pdi-status {{ text-align: right; font-size: 11px; color: #047857; font-weight: bold; }}
        
        .cid-banner {{
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 12px;
            line-height: 1.45;
            margin-bottom: 15px;
        }}
        .banner-tod {{ background: #f5f3ff; border: 1px solid #c4b5fd; color: #5b21b6; }}
        .banner-tdah {{ background: #fffbeb; border: 1px solid #fde68a; color: #92400e; }}
        .banner-tea {{ background: #f0f9ff; border: 1px solid #bae6fd; color: #075985; }}
        .banner-dislexia {{ background: #eff6ff; border: 1px solid #bfdbfe; color: #1e40af; }}
        .banner-neuro {{ background: #faf5ff; border: 1px solid #e9d5ff; color: #6b21a8; }}
        .banner-ta {{ background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }}
        .banner-di {{ background: #fff7ed; border: 1px solid #fed7aa; color: #9a3412; }}
        .banner-diab {{ background: #ecfeff; border: 1px solid #a5f3fc; color: #155e75; }}
        .banner-malform {{ background: #f8fafc; border: 1px solid #cbd5e1; color: #334155; }}

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
            padding: 10px 12px;
            font-size: 12px;
            line-height: 1.5;
            margin-bottom: 8px;
        }}
        .prova-box {{
            background: #fefce8;
            border: 1px solid #fef08a;
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 12px;
            line-height: 1.5;
            color: #713f12;
            margin-bottom: 8px;
        }}
        .legal-box {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 11px;
            color: #166534;
            margin-bottom: 15px;
        }}
        .obs-box {{ font-size: 12px; margin-top: 15px; }}
        @media print {{
            body {{ background: transparent; padding: 0; }}
            .aee-card {{ margin: 0; box-shadow: none; border: 1px solid #000; page-break-after: always; }}
            .no-print {{ display: none; }}
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
