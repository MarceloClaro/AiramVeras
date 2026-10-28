# -*- coding: utf-8 -*-
"""
Módulo Canônico de Geração da Lauda 3: PEI e PAEE Dinâmico Universal
Escola de Cidadania Airam Veras • Crateús - CE • Ano Letivo 2026
Atende integralmente a alunos neurodivergentes (AEE/Cuidadores) e não-divergentes (DUA Universal).
"""

import sqlite3
import unicodedata
import re

def norm(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^A-Z0-9\s]', '', text.upper()).strip()

def carregar_mapa_pei_paee(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # 1. Carregar AEE e Cuidadores
    cur.execute("""
        SELECT aluno_hash_id, nome_estudante_docx, apoiador_cuidador, necessidade_cuidador,
               turno_atendimento, cid_10_codigo, cid_11_codigo, cid_descricao_sintese,
               status_laudo, em_triagem
        FROM dim_aee_cuidadores_relacao_oficial_2026;
    """)
    aee_map_hash = {}
    aee_map_nome = {}
    for r in cur.fetchall():
        d = {
            'hash_id': r[0],
            'nome_docx': r[1],
            'apoiador': r[2],
            'nec_cuidador': r[3],
            'turno': r[4],
            'cid10': r[5],
            'cid11': r[6],
            'cid_desc': r[7],
            'status_laudo': r[8],
            'em_triagem': r[9]
        }
        if r[0]:
            aee_map_hash[r[0]] = d
        if r[1]:
            aee_map_nome[norm(r[1])] = d

    # 2. Carregar PAEE
    cur.execute("""
        SELECT aluno_hash_id, modalidade_aee, frequencia_semanal_minutos,
               area_foco_psiconeuropedagogica, tecnologias_assistivas_utilizadas,
               cronograma_atendimento_dia, articulacao_sala_comum_estrategia, hash_forense_paee
        FROM fato_paee_plano_atendimento;
    """)
    paee_map = {}
    for r in cur.fetchall():
        paee_map[r[0]] = {
            'modalidade': r[1],
            'freq_min': r[2],
            'area_foco': r[3],
            'tec_assist': r[4],
            'cronograma': r[5],
            'articulacao': r[6],
            'hash_paee': r[7]
        }

    # 3. Carregar PEI nos 4 Bimestres
    cur.execute("""
        SELECT p.aluno_hash_id, p.bimestre, p.diagnostico_clinico_resumo, p.cid_codigo,
               p.perfil_neurocognitivo_sweller, p.meta_fonica_adaptada, p.meta_matematica_kumon_adaptada,
               p.adaptacao_espaco_fisico, p.adaptacao_temporal_pausas, p.adaptacao_instrumentos_materiais,
               p.protocolo_desescalada_comportamental, p.indicador_evolucao_esperado, p.hash_forense_pei,
               e.nome_estudante
        FROM fato_pei_estudante_adaptacoes p
        JOIN fato_praticas_diarias_leitura_fluencia e ON p.aluno_hash_id = e.aluno_hash_id
        ORDER BY p.aluno_hash_id, p.bimestre;
    """)
    pei_map = {}
    for r in cur.fetchall():
        h = r[0]
        b = r[1]
        nome = r[13]
        if h not in pei_map:
            pei_map[h] = {
                'nome': nome,
                'diag': r[2],
                'cid': r[3],
                'sweller': r[4],
                'bimestres': {}
            }
        pei_map[h]['bimestres'][b] = {
            'meta_fonica': r[5],
            'meta_mat': r[6],
            'espaco': r[7],
            'pausas': r[8],
            'materiais': r[9],
            'pbs': r[10],
            'evolucao': r[11],
            'hash_pei': r[12]
        }

    conn.close()
    return aee_map_hash, aee_map_nome, paee_map, pei_map

def gerar_html_lauda_3_pei(aluno_hash_id, nome_aluno, ano_escolar, turma_nome, cluster_cod,
                           p_num, total_pages, make_header, make_footer,
                           aee_map_hash, aee_map_nome, paee_map, pei_map):
    """
    Gera exatamente 1 lauda A4 vetorial contendo o PEI e PAEE parametrizado.
    """
    norm_n = norm(nome_aluno)
    aee_info = aee_map_hash.get(aluno_hash_id, aee_map_nome.get(norm_n, None))
    
    # Se não achou por nome exato, tentar substring
    if not aee_info:
        for k, v in aee_map_nome.items():
            if k in norm_n or norm_n in k:
                aee_info = v
                break

    paee_info = paee_map.get(aluno_hash_id, {})
    pei_aluno = pei_map.get(aluno_hash_id, {})
    bimestres = pei_aluno.get('bimestres', {})

    eh_laudado = False
    eh_triagem = False

    if aee_info:
        if aee_info.get('em_triagem') == 1:
            eh_triagem = True
        elif aee_info.get('status_laudo') == 'LAUDADO_OFICIAL':
            eh_laudado = True

    # Badges e Rótulos
    if eh_laudado:
        badge_cls = "badge-blue"
        tipo_pei = "PEI CLÍNICO-PEDAGÓGICO AEE (LEI 13.146/2015 & PARECER CNE 50/2023)"
        rotulo_status = f"LAUDADO AEE • {aee_info.get('cid_desc', 'Educação Especial')}"
        cuidador_txt = f"<strong>Apoiador/Cuidador Designado:</strong> {aee_info.get('apoiador', 'Equipe AEE')} ({aee_info.get('turno', 'Turno Escolar')}) | <strong>CIDs:</strong> {aee_info.get('cid10', '')} {aee_info.get('cid11', '')}"
    elif eh_triagem:
        badge_cls = "badge-amber"
        tipo_pei = "PEI DE TRIAGEM & ACOLHIMENTO NEUROPSICOPEDAGÓGICO (DOCX 27/10/2026)"
        rotulo_status = "EM TRIAGEM ATIVA OFICIAL • Investigação Diagnóstica de Barreiras"
        cuidador_txt = "<strong>Status AEE:</strong> Em Triagem Multidisciplinar (Equipe Escolar e AEE) | <strong>Acomodações:</strong> Preventivas em Sala Regular"
    else:
        badge_cls = "badge-green"
        tipo_pei = "PEI FORMATIVO UNIVERSAL DUA (DESENHO UNIVERSAL PARA A APRENDIZAGEM)"
        rotulo_status = f"DESENVOLVIMENTO REGULAR / NEUROTÍPICO • CLUSTER {cluster_cod}"
        cuidador_txt = f"<strong>Modalidade:</strong> Tutoria e Mediação Pedagógica Universal DUA em Sala Regular (35H) | <strong>Cluster:</strong> {cluster_cod}"

    modalidade_paee = paee_info.get('modalidade', 'Acompanhamento Universal DUA em Sala Regular')
    tec_assist_paee = paee_info.get('tec_assist', 'Materiais pedagógicos estruturados e apoio visual')

    # Obter dados dos 4 bimestres
    b1 = bimestres.get(1, {})
    b2 = bimestres.get(2, {})
    b3 = bimestres.get(3, {})
    b4 = bimestres.get(4, {})

    pbs_geral = b1.get('pbs', 'Reforço diferencial positivo (4:1), rotina visual TEACCH e previsibilidade de transições.')
    hash_pei_display = b4.get('hash_pei', b1.get('hash_pei', 'SHA256-PENDING'))

    html = f"""
    <div class="page-block">
        {make_header(p_num, total_pages, f"PLANO PEI / PAEE • {nome_aluno}")}
        <h1 class="section-title">Plano Educacional Individualizado (PEI) & Diretrizes PAEE</h1>
        
        <div class="card-highlight" style="font-size:6.4pt; padding:3px 7px; margin-bottom:3px; line-height:1.25;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div><strong>Estudante:</strong> {nome_aluno} | <strong>Turma:</strong> {turma_nome}</div>
                <div><span class="badge {badge_cls}">{rotulo_status}</span></div>
            </div>
            <div style="margin-top:2px;">{cuidador_txt}</div>
            <div style="margin-top:1px;"><strong>Modalidade PAEE:</strong> {modalidade_paee} | <strong>Recursos:</strong> {tec_assist_paee}</div>
        </div>

        <h2 class="sub-title" style="margin-top:2px; margin-bottom:2px;">1. Metas Bimestrais Estruturadas de Aprendizagem & Adaptações DUA (1º ao 4º Bimestre)</h2>
        <table class="data-table" style="font-size:5.5pt; line-height:1.15; margin-bottom:3px;">
            <tr>
                <th style="width:12%;">Bimestre</th>
                <th style="width:28%;">Meta Fônica e Linguística</th>
                <th style="width:26%;">Meta Matemática (Kumon Adaptado)</th>
                <th style="width:20%;">Acomodações de Prova & DUA</th>
                <th style="width:14%; text-align:center;">Indicador de Sucesso</th>
            </tr>
            <tr>
                <td><strong>1º Bimestre</strong><br><span style="font-size:4.8pt; color:#64748b;">Diagnóstico & Acolhimento</span></td>
                <td>{b1.get('meta_fonica', 'Reconhecimento de sons das vogais e consoantes contínuas com apoio visual.')}</td>
                <td>{b1.get('meta_mat', 'Contagem concreta e associação número-quantidade (Kumon 7A).')}</td>
                <td>{b1.get('materiais', 'Provas ampliadas e pausas ativas.')}</td>
                <td style="text-align:center; font-weight:bold; color:#1e40af;">{b1.get('evolucao', 'Tolerância e engajamento')}</td>
            </tr>
            <tr>
                <td><strong>2º Bimestre</strong><br><span style="font-size:4.8pt; color:#64748b;">Decodificação & Automação</span></td>
                <td>{b2.get('meta_fonica', 'Leitura de sílabas canônicas e vocabulário funcional de alta frequência.')}</td>
                <td>{b2.get('meta_mat', 'Adições concretas até 10/20 e reconhecimento de padrões espaciais.')}</td>
                <td>{b2.get('materiais', 'Cartelas de apoio e rotina estruturada.')}</td>
                <td style="text-align:center; font-weight:bold; color:#1e40af;">{b2.get('evolucao', 'Autonomia crescente')}</td>
            </tr>
            <tr>
                <td><strong>3º Bimestre</strong><br><span style="font-size:4.8pt; color:#64748b;">Fluência & Resolução</span></td>
                <td>{b3.get('meta_fonica', 'Leitura guiada de frases e identificação de informações explícitas.')}</td>
                <td>{b3.get('meta_mat', 'Resolução de problemas cotidianos aditivos com suporte manipulável.')}</td>
                <td>{b3.get('materiais', 'Ledor credenciado e sala silenciosa.')}</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">{b3.get('evolucao', 'Evolução leitora')}</td>
            </tr>
            <tr>
                <td><strong>4º Bimestre</strong><br><span style="font-size:4.8pt; color:#64748b;">Consolidação & SPAECE</span></td>
                <td>{b4.get('meta_fonica', 'Autonomia na leitura de pequenos textos e alcance da meta de fluência.')}</td>
                <td>{b4.get('meta_mat', 'Operações fundamentais consolidadas no nível Kumon correspondente.')}</td>
                <td>{b4.get('materiais', 'Auditoria pericial de metas atingidas.')}</td>
                <td style="text-align:center; font-weight:bold; color:#16a34a;">{b4.get('evolucao', 'Meta Plena Atingida')}</td>
            </tr>
        </table>

        <div style="display:grid; grid-template-columns:1fr 1fr; gap:4px; margin-top:2px;">
            <div class="card" style="font-size:5.7pt; line-height:1.2; padding:3px 6px;">
                <div style="font-weight:bold; color:#1e3a8a; margin-bottom:1px;">PROTOCOLO DE CONDUTA & APOIO COMPORTAMENTAL POSITIVO (PBS):</div>
                {pbs_geral}
            </div>
            <div class="card-highlight" style="font-size:5.7pt; line-height:1.2; padding:3px 6px;">
                <div style="font-weight:bold; color:#065f46; margin-bottom:1px;">DIRETRIZ AVALIATIVA SPAECE / CAEd & AUDITORIA FORENSE:</div>
                Tempo estendido oficial (+50%), não penalização de trocas fonéticas, presença de profissional de apoio escolar credenciado e guarda ética documental.
                <div style="margin-top:2px; font-family:monospace; font-size:4.8pt; color:#475569;">
                    Assinatura Criptográfica PEI: <code>{hash_pei_display[:32]}...</code> (Bloco 34 no Ledger)
                </div>
            </div>
        </div>
        {make_footer(p_num)}
    </div>
    """
    return html
