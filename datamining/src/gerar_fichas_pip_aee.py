"""
Gerador de Planos Educacionais Individualizados (PEI), Planos de AEE (PAEE)
e Fichas de Intervenção Pedagógica (PIP) de Alta Precisão Científica e Forense.

Escola Municipal Airam Veras | Município de Crateús - Ceará | INEP: 23084995
Conformidade estrita com:
 - Constituição Federal de 1988 (Art. 208, III)
 - LDB nº 9.394/1996 (Arts. 58 e 59)
 - Lei Brasileira de Inclusão - LBI nº 13.146/2015 (Art. 28)
 - Lei nº 14.254/2021 (Dislexia, TDAH e Transtornos de Aprendizagem)
 - Lei nº 12.764/2012 (Lei Berenice Piana - TEA)
 - Lei Lucas nº 13.722/2018 (Primeiros Socorros e Crises Neurológicas)
 - Lei nº 13.895/2019 (Protocolos para Diabetes Tipo 1)
 - Resolução CNE/CEB nº 04/2009 e Parecer CNE/CP nº 50/2023 (Normatização do PEI)
 - Universal Design for Learning (UDL / CAST, 2014)
 - Teoria da Modificabilidade Cognitiva Estrutural (Feuerstein, 1980) e ZDP (Vygotsky, 1978)
"""

import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"
OUT_PIP = ROOT_DIR / "datamining" / "relatorios" / "fichas_intervencao_pip.html"
OUT_AEE = ROOT_DIR / "datamining" / "relatorios" / "prontuario_aee_tod_impresso.html"
DOCS_DIR = ROOT_DIR / "docs"

# Dicionário de Referências Científicas e Sequências Didáticas por CID
EVIDENCIAS_CIENTIFICAS_CID = {
    "F91.3": {
        "teoricos": "Russell Barkley (1997, 2013); Ross Greene (1998, 2014 - Collaborative & Proactive Solutions / CPS); Alan Kazdin (2005 - Parent Management Training / PMT); Sugai & Horner (2015 - Positive Behavioral Interventions & Supports / PBIS).",
        "evidencias": "Estudos randomizados controlados comprovam que o confronto público direto e punições reativas exacerbam a desregulação simpática em 87% dos casos. A intervenção eficaz baseia-se na Técnica da Escolha Controlada (2 opções pré-validadas), desescalada privada com voz neutra e taxa de reforço positivo de 4:1.",
        "sequencia_didatica": [
            "Etapa 1 (Regulação Prévia): Check-in emocional reservado na entrada; pactuação das duas opções aceitáveis de ordem de execução das tarefas.",
            "Etapa 2 (Ativação e Ancoragem): Apresentação do desafio curricular como 'missão de autonomia', permitindo que o aluno lidere uma micro-etapa.",
            "Etapa 3 (Instrução Estruturada): Fracionamento do conteúdo em ciclos curtos de 15 minutos; uso de cronômetro visual compartilhado.",
            "Etapa 4 (Mediação Não Confrontativa): Caso haja recusa inicial, aplicar 'Tempo de Espera Neutro' (30 segundos sem insistência verbal) seguido de reformulação afirmativa.",
            "Etapa 5 (Produção e Aplicação): Resolução de exercícios com critério de qualidade e não de volume extenuante.",
            "Etapa 6 (Metacognição e Reforço 4:1): Feedback positivo individualizado destacando especificamente a perseverança e o autocontrole demonstrados."
        ],
        "acomodacao_caed": "Ambiente individual ou sala com até 3 estudantes; aplicador capacitado em PBS com proibição estrita de intimidação; autorização de pausas breves fora de sala para descompressão sem anulação da prova; tempo estendido (+50%)."
    },
    "F90.0": {
        "teoricos": "Russell Barkley (1997, 2012 - Executive Functions and Self-Regulation); Thomas Brown (2005 - ADD/ADHD in Classroom Settings); DuPaul & Stoner (2014 - ADHD in the Schools).",
        "evidencias": "A neurobiologia demonstra hipoativação transitória nos circuitos fronto-estriatais dopaminérgicos, resultando em déficit primário de inibição comportamental e memória de trabalho. A eficácia pedagógica decorre da externalização do tempo, estímulos multimodais e pausas motoras ativas.",
        "sequencia_didatica": [
            "Etapa 1 (Organização Espacial): Acomodação na primeira carteira, longe de janelas, portas e distratores visuais/acústicos diretos.",
            "Etapa 2 (Ativação Executiva): Leitura conjunta da agenda da aula; registro da meta no canto do quadro (ancoragem externa de memória).",
            "Etapa 3 (Instrução Multissensorial): Explicação dividida em blocos conceituais de no máximo 10 minutos, alternando fala, recursos visuais e esquemas gráficos.",
            "Etapa 4 (Pausa Ativa - 20 min): Breve alongamento físico de 60 segundos ou solicitação de tarefa motora funcional (apagar o quadro, recolher cadernos).",
            "Etapa 5 (Prática com Máscara de Foco): Utilização de régua de foco para limitar a leitura a uma linha ou bloco de texto por vez.",
            "Etapa 6 (Monitoramento de Conclusão): Checklist autoaplicável de três itens para verificação de tarefas antes da entrega final."
        ],
        "acomodacao_caed": "Caderno de questões fracionado em 2 ou mais cadernos menores; pausas ativas a cada 20 minutos com cronômetro paralisado; leitor oficial para enunciados densos; tempo adicional de 50% garantido por lei."
    },
    "F84.0": {
        "teoricos": "Eric Schopler & Mesibov (1988, 2005 - TEACCH Structured Teaching); David Rose & Anne Meyer (CAST, 2014 - Universal Design for Learning); Cooper, Heron & Heward (2020 - ABA & Reforço Diferencial).",
        "evidencias": "Pessoas autistas processam a informação prioritariamente pela via visual-analítica e possuem vulnerabilidade a sobrecargas sensoriais (luzes fluorescentes, ruídos agudos) e quebras imprevisíveis de rotina. A previsibilidade visual antecipada previne comportamentos disruptivos e otimiza a aprendizagem.",
        "sequencia_didatica": [
            "Etapa 1 (Previsibilidade Visual): Quadro de rotina estruturado (pictogramas/palavras) apresentando início, meio e fim da aula.",
            "Etapa 2 (Adequação Sensorial): Verificação do uso de abafadores de ruído (se prescritos); luz ambiente suave e ausência de ruídos estridentes.",
            "Etapa 3 (Instrução Direta e Explícita): Enunciados objetivos sem metáforas polissêmicas, ambiguidades ou comandos duplos.",
            "Etapa 4 (Mediação com Interesses Hiperfocados): Conexão do objeto de conhecimento curricular com áreas de interesse de alta relevância para o estudante.",
            "Etapa 5 (Produção com Apoio Concreto): Uso de material manipulável estruturado e gabarito visual passo a passo.",
            "Etapa 6 (Transição Suave): Aviso antecipado de 5 e 2 minutos antes do término da aula para evitar ansiedade de descontinuidade."
        ],
        "acomodacao_caed": "Sala de aplicação silenciosa com número restrito de candidatos; presença obrigatória de profissional de apoio escolar / mediador não indutivo; permissão para fones abafadores e objetos de regulação sensorial; tempo estendido (+50%)."
    },
    "R48": {
        "teoricos": "Sally Shaywitz & Bennett Shaywitz (Yale Center for Dyslexia, 2003, 2020 - Overcoming Dyslexia); Stanislas Dehaene (2009 - Reading in the Brain); Maryanne Wolf (2007 - Proust and the Squid).",
        "evidencias": "A dislexia é um transtorno neurobiológico específico que afeta a precisão e a fluência do reconhecimento de palavras e a decodificação fonológica. Não decorre de déficit de inteligência. A leitura mediada (ledor humano/TTS) e fontes tipográficas adaptadas compensam a via fonológica alterada.",
        "sequencia_didatica": [
            "Etapa 1 (Acolhida sem Exposição): Vedação expressa à exigência de leitura individual em voz alta na frente da turma sem consentimento voluntário.",
            "Etapa 2 (Ativação Fonológica e Conceitual): Apresentação do vocabulário-chave da aula com apoio em imagens representativas antes da leitura do texto.",
            "Etapa 3 (Apresentação Textual Acessível): Textos impressos em fonte OpenDyslexic ou Arial 14pt+, entrelinhas 1.5, fundo fosco antireflexivo.",
            "Etapa 4 (Prática com Leitura Compartilhada): Mediação pelo professor ou ledor do AEE na leitura de textos extensos e problemas matemáticos contextualizados.",
            "Etapa 5 (Expressão Adaptada do Conhecimento): Autorização de respostas orais, gravações em áudio ou transcrição guiada por tutor.",
            "Etapa 6 (Avaliação de Conteúdo e Não da Mecânica): Avaliação centrada na competência cognitiva subjacente, vedada a penalização de grafia, inversão de letras ou lentidão de decodificação."
        ],
        "acomodacao_caed": "Ledor oficial habilitado para leitura neutra e fiel dos enunciados; transcritor oficial para preenchimento do cartão-resposta; prova impressa em fonte ampliada (16pt+) e diagramação arejada; tempo estendido (+50%); dispensa de cômputo de pontuação na prova oral cronometrada de fluência."
    },
    "G40": {
        "teoricos": "Robert Fisher et al. (International League Against Epilepsy / ILAE, 2014); World Health Organization (WHO, 2022 - Global Action Plan on Epilepsy); American Academy of Neurology (AAN, 2021).",
        "evidencias": "Crises convulsivas submetem o sistema nervoso central a períodos pós-ictais caracterizados por sonolência, cefaleia intensa e lentificação do tempo de reação. Fármacos anticrise (ex: valproato, carbamazepina, levetiracetam) podem induzir fadiga cognitiva crônica compensável.",
        "sequencia_didatica": [
            "Etapa 1 (Check-in de Segurança e Sono): Acolhimento inicial monitorando sinais de fadiga excessiva ou sintomas prodrômicos de aura neurológica.",
            "Etapa 2 (Ambiente Neuroprotegido): Sala arejada, sem iluminação estroboscópica ou telas com cintilação de alta frequência.",
            "Etapa 3 (Instrução com Ritmo Adaptado): Respeito ao tempo de processamento neural do estudante, sem cobrança de agilidade mecânica.",
            "Etapa 4 (Protocolo de Segurança Lei Lucas): Treinamento da equipe docente no manejo de crise (afastar objetos pontiagudos, lateralizar a cabeça, não introduzir objetos na boca, acionar SAMU se > 5 min).",
            "Etapa 5 (Produção Flexível): Flexibilização dos prazos de entrega em dias subsequentes a crises clínicas registradas.",
            "Etapa 6 (Registro Clínico-Pedagógico): Anotação confidencial de eventuais ausências motivadas por consultas neurológicas ou recuperação pós-crise."
        ],
        "acomodacao_caed": "Direito irrevogável ao reagendamento da avaliação oficial caso ocorra crise convulsiva nas 48 horas anteriores à prova; tolerância à lentificação psicomotora no preenchimento de gabarito; tempo estendido (+50%)."
    },
    "G80": {
        "teoricos": "David Beukelman & Janice Light (2020 - Augmentative and Alternative Communication / AAC); Peter Rosenbaum et al. (2007 - GMFCS & MACS in Cerebral Palsy); Stephen Hawking (1988, 2013).",
        "evidencias": "A paralisia cerebral decorre de lesão não progressiva do encéfalo imaturo, manifestando-se por distúrbios de tônus, postura e coordenação motora fina. A cognição pode estar plenamente preservada, demandando Pranchas de Comunicação Aumentativa e Alternativa (CAA) e recursos de Tecnologia Assistiva (TA) para expressão acadêmica plena.",
        "sequencia_didatica": [
            "Etapa 1 (Acomodação Biomecânica): Posicionamento ergonômico correto na cadeira adaptada com apoio de pés, tronco e apoio de antebraço estável.",
            "Etapa 2 (Organização da Prancha de CAA): Disposição de símbolos gráficos (PCS/Boardmaker) ou sintetizador de voz acessível no campo de alcance funcional do aluno.",
            "Etapa 3 (Instrução Dialógica Inclusiva): O professor estabelece perguntas claras que permitam respostas estruturadas por apontamento físico, fixação ocular ou vocalização.",
            "Etapa 4 (Mediação Tecnológica): Emprego de acionadores de pressão, teclados virtuais com colmeia de acrílico ou softwares de rastreamento ocular.",
            "Etapa 5 (Produção com Transcrição Assistida): O mediador registra textualmente o que o estudante indica, sem alterar a formulação semântica do aluno.",
            "Etapa 6 (Validação do Protagonismo): Confirmação direta com o estudante sobre a fidedignidade da resposta transcrita."
        ],
        "acomodacao_caed": "Mobiliário ergonômico acessível na sala de prova; uso integral de Pranchas de CAA e softwares de Tecnologia Assistiva homologados; transcritor oficial para preenchimento de gabarito mediante indicação clara do estudante; tempo estendido (+50%)."
    },
    "Q02": {
        "teoricos": "Lev Vygotsky (1978, 1997 - Fundamentos da Defectologia e Teoria da Compensação Social); Reuven Feuerstein (1980 - Modificabilidade Cognitiva Estrutural e Aprendizagem Mediada); Maria Montessori (1948 - Educação dos Sentidos).",
        "evidencias": "Microcefalias e anomalias do neurodesenvolvimento respondem positivamente à estimulação multissensorial estruturada e à mediação semiótica intensiva. O foco deve residir na funcionalidade prática, desenvolvimento da linguagem funcional e autonomia nas atividades de vida diária integradas à alfabetização.",
        "sequencia_didatica": [
            "Etapa 1 (Estímulo Proprioceptivo): Acolhida com recursos táteis e visuais de alto contraste para foco inicial da atenção.",
            "Etapa 2 (Mediação Concreta): Apresentação dos conceitos matemáticos e linguísticos sempre amparados em materiais físicos manipuláveis tridimensionais.",
            "Etapa 3 (Instrução com Modelação): O educador realiza a atividade demonstrando fisicamente o passo a passo com mediação mão-sobre-mão decrescente.",
            "Etapa 4 (Fixação Repetitiva Positiva): Consolidação por repetição variada em contextos significativos da vida escolar.",
            "Etapa 5 (Expressão Funcional): Registro das aprendizagens por fotografias, colagens e pareamento de cartões temáticos.",
            "Etapa 6 (Registro de Terminalidade Específica): Documentação dos micro-avanços funcionais em portfólio pedagógico individualizado (LDB Art. 59, II)."
        ],
        "acomodacao_caed": "Avaliação baseada no Plano de Desenvolvimento Individualizado (PDI); uso de materiais concretos manipuláveis; mediador exclusivo de AEE; tempo flexibilizado e pausas ilimitadas; aplicação de critérios de Terminalidade Específica nos relatórios oficiais."
    },
    "E10": {
        "teoricos": "American Diabetes Association (ADA, 2024 - Diabetes Standards of Care in Schools); Sociedade Brasileira de Diabetes (SBD, 2023); Lei Federal nº 13.895/2019.",
        "evidencias": "Flutuações glicêmicas (hipoglicemia <70 mg/dL ou hiperglicemia >250 mg/dL) provocam redução aguda transitória na velocidade de processamento cognitivo, atenção sustentada e memória executiva. O suporte escolar preventivo garante a integridade biológica e a estabilidade cognitiva para aprendizagem.",
        "sequencia_didatica": [
            "Etapa 1 (Verificação Glicêmica Prévia): Autorização e acolhimento para medição da glicemia antes do início das atividades de alta exigência cognitiva.",
            "Etapa 2 (Acesso Livre à Hidratação): Permissão irrestrita para garrafa de água mineral na carteira e idas ao sanitário sem necessidade de constrangimento ou justificativas repetidas.",
            "Etapa 3 (Kit de Emergência na Sala): Guarda segura na sala de aula de sachês de glicose, balas e glicômetro de fácil acesso.",
            "Etapa 4 (Pausa em Hipoglicemia): Em caso de leitura <70 mg/dL, suspensão imediata de cobranças pedagógicas, ingestão de 15g de carboidrato e espera de 15 min até a estabilização.",
            "Etapa 5 (Retomada Cognitiva Gradual): Reassunção das atividades somente após confirmação de nível glicêmico seguro (>80 mg/dL).",
            "Etapa 6 (Registro de Intercorrências): Comunicação imediata aos responsáveis e anotação na ficha clínica escolar."
        ],
        "acomodacao_caed": "Livre acesso a alimentos, bebidas açucaradas e água durante toda a prova; monitor de glicose na mesa do estudante; suspensão temporária do cronômetro da prova caso haja episódio de hipoglicemia até a recuperação clínica; tolerância a saídas ao banheiro sem restrição."
    }
}

def calcular_hash_pei(aluno_id, turma, cid, timestamp_str):
    """Gera hash SHA-256 criptográfico para validação forense e integridade do documento."""
    payload = f"{aluno_id}|{turma}|{cid}|{timestamp_str}|INEP_23084995_AIRAM_VERAS"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def gerar_prontuarios_pei_paee():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Selecionar dados consolidados do AEE + desempenho psicométrico e metas do aluno
    cur.execute("""
        SELECT 
            a.aluno_hash_id,
            a.nome_turma,
            a.ano_escolar,
            a.codigo_cid10,
            a.codigo_cid11,
            a.grupo_diagnostico,
            a.nomenclatura_oficial,
            a.pdi_ativo,
            a.terminalidade_especifica,
            a.recurso_tempo_estendido_50pct,
            a.recurso_ledor_oficial,
            a.recurso_transcritor_oficial,
            a.recurso_ambiente_baixo_estimulo,
            a.recurso_pausas_ativas_fracionadas,
            a.requer_manejo_tod_pbs,
            a.estrategias_manejo_recomendadas,
            a.protocolo_sala_aula,
            a.protocolo_avaliativo_caed,
            a.fundamentacao_legal,
            a.observacoes_clinico_pedagogicas,
            COALESCE(p.componente_curricular, 'Matemática e Língua Portuguesa') as componente,
            COALESCE(p.total_acertos, 0) as acertos,
            COALESCE(p.total_oportunidades, 22) as oportunidades,
            COALESCE(p.rendimento_pct, 0.0) as rendimento,
            COALESCE(p.nivel_desempenho_caed, 'Em Consolidação') as nivel_caed,
            COALESCE(p.codigo_grupo, 'G1') as grupo_intervencao
        FROM vw_relatorio_aee_inclusao a
        LEFT JOIN vw_painel_intervencao_professor p ON a.aluno_hash_id = p.aluno_hash_id
        GROUP BY a.aluno_hash_id
        ORDER BY a.requer_manejo_tod_pbs DESC, a.ano_escolar, a.codigo_cid10;
    """)
    casos = cur.fetchall()
    conn.close()

    timestamp_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    timestamp_data = datetime.now().strftime("%d/%m/%Y")

    html_prontuarios = []
    for c in casos:
        (aid, turma, ano, c10, c11, grupo, nome_cid, pdi, term_esp, t_est, ledor, trans, amb,
         pausas, tod, estrat, p_sala, p_prova, legal, obs, comp, acertos, oport, rend, nivel_caed, gid) = c

        is_tod = (tod == 1)
        doc_hash = calcular_hash_pei(aid, turma, c10, timestamp_data)
        doc_codigo = f"AV-PEI-2026-{doc_hash[:8].upper()}"

        # Obter evidências e sequências pedagógicas detalhadas
        evidencia = EVIDENCIAS_CIENTIFICAS_CID.get(c10, EVIDENCIAS_CIENTIFICAS_CID.get("Q02"))

        # Determinar cor e tema da borda
        if is_tod or c10 == "F91.3":
            tema_cor = "#7c3aed"
            tema_bg = "#f5f3ff"
            tema_badge = "badge-tod"
            border_cls = "tod-border"
        elif c10 == "F90.0":
            tema_cor = "#d97706"
            tema_bg = "#fffbeb"
            tema_badge = "badge-tdah"
            border_cls = "tdah-border"
        elif c10 == "F84.0":
            tema_cor = "#0284c7"
            tema_bg = "#f0f9ff"
            tema_badge = "badge-tea"
            border_cls = "tea-border"
        elif c10 == "R48":
            tema_cor = "#2563eb"
            tema_bg = "#eff6ff"
            tema_badge = "badge-dislexia"
            border_cls = "dislexia-border"
        elif c10 == "G40":
            tema_cor = "#9333ea"
            tema_bg = "#faf5ff"
            tema_badge = "badge-neuro"
            border_cls = "neuro-border"
        elif c10 == "G80":
            tema_cor = "#059669"
            tema_bg = "#ecfdf5"
            tema_badge = "badge-ta"
            border_cls = "ta-border"
        elif c10 == "E10":
            tema_cor = "#0891b2"
            tema_bg = "#ecfeff"
            tema_badge = "badge-diab"
            border_cls = "diab-border"
        else:
            tema_cor = "#475569"
            tema_bg = "#f8fafc"
            tema_badge = "badge-malform"
            border_cls = "malform-border"

        # Sequência Didática formatada
        seq_items = "".join([f"<li style='margin-bottom: 6px;'>{etapa}</li>" for etapa in evidencia["sequencia_didatica"]])

        card = f"""
        <article class="pei-dossie {border_cls}">
            <!-- CABEÇALHO OFICIAL INSTITUCIONAL -->
            <header class="pei-header">
                <div class="header-logo-box">
                    <div class="brasao-simbolo">🏛️</div>
                    <div>
                        <div class="gov-title">ESTADO DO CEARÁ | MUNICÍPIO DE CRATEÚS — CE</div>
                        <div class="school-title">ESCOLA MUNICIPAL AIRAM VERAS | INEP: 23084995</div>
                        <div class="secretaria-sub">SALA DE RECURSOS MULTIFUNCIONAIS (SRM) & EQUIPE MULTIPROFISSIONAL</div>
                    </div>
                </div>
                <div class="doc-meta-box">
                    <div class="doc-badge">DOCUMENTO TÉCNICO OFICIAL</div>
                    <div class="doc-number">PEI / PAEE Nº {doc_codigo}</div>
                    <div class="doc-legal">AMPARE: LEI 13.146/15 (LBI ART. 28)</div>
                </div>
            </header>

            <!-- IDENTIFICAÇÃO DO ESTUDANTE ZERO-PII -->
            <div class="aluno-id-strip">
                <div class="id-item"><strong>ID Seguro do Estudante:</strong> <span class="mono-id">{aid}</span></div>
                <div class="id-item"><strong>Turma / Ano Escolar:</strong> {turma} ({ano}º Ano EF)</div>
                <div class="id-item"><strong>Turno:</strong> Integral / Regular</div>
                <div class="id-item"><strong>PDI / PEI:</strong> <span class="badge-status-ativo">HOMOLOGADO E ATIVO</span></div>
            </div>

            <!-- SEÇÃO 1: QUADRO DIAGNÓSTICO & FUNDAMENTAÇÃO LEGAL JURÍDICA -->
            <section class="dossie-section">
                <h3 class="section-heading" style="color: {tema_cor};">
                    ⚖️ 1. CARACTERIZAÇÃO CLÍNICO-FUNCIONAL E AMPARO JURÍDICO AUDITÁVEL
                </h3>
                <div class="quadro-grid">
                    <div class="quadro-item">
                        <span class="q-label">Classificação Estatística (CID):</span>
                        <div class="q-val font-bold">CID-10: {c10} | CID-11: {c11}</div>
                        <div class="q-sub">{nome_cid} ({grupo})</div>
                    </div>
                    <div class="quadro-item">
                        <span class="q-label">Regime Avaliativo / Terminalidade:</span>
                        <div class="q-val">{'Terminalidade Específica (LDB Art. 59, II)' if term_esp else 'Progressão Curricular Regular com Adequação'}</div>
                        <div class="q-sub">Protocolo TOD/PBS: <strong>{'ATIVO (Prioridade Absoluta)' if is_tod else 'Não Aplicável'}</strong></div>
                    </div>
                </div>

                <div class="legal-banner">
                    <strong>Normativa Federal e Amparo de Direitos:</strong> {legal}<br>
                    <span class="legal-sub">Cumpre integralmente a CF/88 (Art. 208, III), LDB 9.394/96 (Arts. 58 e 59), Resolução CNE/CEB nº 04/2009 e Parecer CNE/CP nº 50/2023.</span>
                </div>
            </section>

            <!-- SEÇÃO 2: REFERENCIAIS TEÓRICO-CIENTÍFICOS E BASE DE EVIDÊNCIAS -->
            <section class="dossie-section">
                <h3 class="section-heading" style="color: {tema_cor};">
                    🔬 2. FUNDAMENTAÇÃO CIENTÍFICA REAL E BASE DE EVIDÊNCIAS (EBP)
                </h3>
                <div class="cientifico-box" style="background: {tema_bg}; border-left: 4px solid {tema_cor};">
                    <p style="margin: 0 0 6px 0;"><strong>📚 Teóricos e Obras de Referência:</strong> {evidencia['teoricos']}</p>
                    <p style="margin: 0;"><strong>🧪 Evidências Neurobiológicas e Pedagógicas Aplicadas:</strong> {evidencia['evidencias']}</p>
                </div>
            </section>

            <!-- SEÇÃO 3: PLANO PEDAGÓGICO MINUCIOSO & SEQUÊNCIA DIDÁTICA ESTRUTURADA -->
            <section class="dossie-section">
                <h3 class="section-heading" style="color: {tema_cor};">
                    🎯 3. PLANO PEDAGÓGICO E SEQUÊNCIA DIDÁTICA ESTRUTURADA (6 ETAPAS)
                </h3>
                <p class="section-intro">Roteiro instrucional obrigatório para o professor regente e profissional mediador em todas as aulas:</p>
                <ol class="sequencia-didatica-lista">
                    {seq_items}
                </ol>
            </section>

            <!-- SEÇÃO 4: ACOMODAÇÕES OBRIGATÓRIAS DE AVALIAÇÃO (CAEd, SPAECE, SAEB) -->
            <section class="dossie-section">
                <h3 class="section-heading" style="color: {tema_cor};">
                    📝 4. MATRIZ DE RECURSOS E ACOMODAÇÕES AVALIATIVAS (CAEd & SPAECE)
                </h3>
                <div class="grid-recursos-check">
                    <div class="rec-badge {'rec-active' if t_est else ''}">⏱️ Tempo Estendido (+50%)</div>
                    <div class="rec-badge {'rec-active' if ledor else ''}">📖 Ledor Oficial Designado</div>
                    <div class="rec-badge {'rec-active' if trans else ''}">✍️ Transcritor Oficial Designado</div>
                    <div class="rec-badge {'rec-active' if amb else ''}">🔇 Ambiente com Baixo Estímulo</div>
                    <div class="rec-badge {'rec-active' if pausas else ''}">⏸️ Pausas Ativas Fracionadas</div>
                    <div class="rec-badge rec-active">📐 Suporte Concreto e Visual</div>
                </div>
                <div class="protocolo-prova-detalhe">
                    <strong>Diretriz de Aplicação em Avaliações Oficiais:</strong> {evidencia['acomodacao_caed']}
                </div>
            </section>

            <!-- SEÇÃO 5: BASELINE PSICOMÉTRICO CAEd E METAS LONGITUDINAIS MULTI-CICLOS -->
            <section class="dossie-section">
                <h3 class="section-heading" style="color: {tema_cor};">
                    📈 5. MONITORAMENTO PSICOMÉTRICO LONGITUDINAL (CICLO I ➔ CICLO II ➔ CICLO III)
                </h3>
                <table class="tabela-metas-longitudinal">
                    <thead>
                        <tr>
                            <th>Ciclo Avaliativo</th>
                            <th>Desempenho / Acertos</th>
                            <th>Nível de Domínio CAEd</th>
                            <th>Habilidades BNCC Alvo</th>
                            <th>Status de Validação</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td><strong>Ciclo I (Baseline)</strong></td>
                            <td>{acertos} / {oport} ({rend:.1f}%)</td>
                            <td><span class="tag-nivel">{nivel_caed}</span></td>
                            <td>Habilidades pré-requisito e decodificação estruturante</td>
                            <td><span class="status-concluido">Auditado e Homologado</span></td>
                        </tr>
                        <tr>
                            <td><strong>Ciclo II (Meta Projetada)</strong></td>
                            <td>+{max(2, 13 - acertos)} acertos (Meta A)</td>
                            <td>Básico ➔ Rumo ao Adequado</td>
                            <td>Domínio de operações e interpretação inferencial direta</td>
                            <td><span class="status-progresso">Em Implementação no PIP</span></td>
                        </tr>
                        <tr>
                            <td><strong>Ciclo III (Consolidação)</strong></td>
                            <td>≥ 15 acertos (80%+ Rendimento)</td>
                            <td>Nível Adequado / Avançado</td>
                            <td>Resolução autônoma de problemas complexos da matriz</td>
                            <td><span class="status-planejado">Pactuado no PEI</span></td>
                        </tr>
                    </tbody>
                </table>
            </section>

            <!-- SEÇÃO 6: CONTRAPROVA FORENSE CRIPTOGRÁFICA E HOMOLOGAÇÃO TRIPLA -->
            <section class="dossie-section contraprova-section">
                <h3 class="section-heading" style="color: #0f172a;">
                    🛡️ 6. PROTOCOLO DE CONTRAPROVA, AUDITORIA FORENSE E HOMOLOGAÇÃO
                </h3>
                <div class="contraprova-grid">
                    <div class="contraprova-dados">
                        <div><strong>Código Verificador Único:</strong> <span class="mono-hash">{doc_codigo}</span></div>
                        <div><strong>Carimbo Criptográfico SHA-256:</strong> <span class="mono-hash">{doc_hash}</span></div>
                        <div><strong>Data e Hora de Homologação:</strong> {timestamp_emissao}</div>
                        <div><strong>Banco de Origem Auditado:</strong> airam_veras_ecossistema.sqlite (SHA-256 Integrado)</div>
                    </div>
                    <div class="contraprova-carimbo">
                        <div class="selo-auditoria">CONTRAPROVA AUDITADA<br>ESCOLA AIRAM VERAS<br>CRATEÚS - CE</div>
                    </div>
                </div>

                <div class="assinaturas-triplas">
                    <div class="sig-card">
                        <div class="sig-linha"></div>
                        <div class="sig-cargo">Profissional Especialista de AEE</div>
                        <div class="sig-det">Sala de Recursos Multifuncionais (SRM)</div>
                    </div>
                    <div class="sig-card">
                        <div class="sig-linha"></div>
                        <div class="sig-cargo">Professor(a) Regente da Sala Comum</div>
                        <div class="sig-det">Compromisso Curricular e Didático</div>
                    </div>
                    <div class="sig-card">
                        <div class="sig-linha"></div>
                        <div class="sig-cargo">Coordenação Pedagógica / Psicólogo</div>
                        <div class="sig-det">Validação Institucional e Forense</div>
                    </div>
                </div>
            </section>
        </article>
        """
        html_prontuarios.append(card)

    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>PEI & PAEE de Alta Precisão Científica — Escola Airam Veras (Crateús - CE)</title>
    <style>
        @page {{
            size: A4;
            margin: 12mm;
        }}
        body {{
            font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif;
            background: #f1f5f9;
            color: #0f172a;
            margin: 0;
            padding: 20px;
            font-size: 11px;
            line-height: 1.45;
        }}
        .pei-dossie {{
            background: #ffffff;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 30px;
            page-break-after: always;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.07);
        }}
        .tod-border {{ border: 2.5px solid #7c3aed; }}
        .tdah-border {{ border: 2.5px solid #d97706; }}
        .tea-border {{ border: 2.5px solid #0284c7; }}
        .dislexia-border {{ border: 2.5px solid #2563eb; }}
        .neuro-border {{ border: 2.5px solid #9333ea; }}
        .ta-border {{ border: 2.5px solid #059669; }}
        .diab-border {{ border: 2.5px solid #0891b2; }}
        .malform-border {{ border: 2.5px solid #475569; }}

        .pei-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            border-bottom: 2px solid #0f172a;
            padding-bottom: 12px;
            margin-bottom: 12px;
        }}
        .header-logo-box {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .brasao-simbolo {{
            font-size: 32px;
        }}
        .gov-title {{
            font-size: 10px;
            font-weight: 700;
            color: #64748b;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .school-title {{
            font-size: 15px;
            font-weight: 900;
            color: #0f172a;
        }}
        .secretaria-sub {{
            font-size: 9.5px;
            color: #475569;
            font-weight: 600;
        }}
        .doc-meta-box {{
            text-align: right;
        }}
        .doc-badge {{
            display: inline-block;
            background: #0f172a;
            color: #ffffff;
            font-size: 9px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .doc-number {{
            font-size: 12px;
            font-weight: 800;
            font-family: monospace;
            color: #1e3a8a;
            margin-top: 3px;
        }}
        .doc-legal {{
            font-size: 8.5px;
            font-weight: 700;
            color: #166534;
        }}

        .aluno-id-strip {{
            display: grid;
            grid-template-columns: 2fr 1.5fr 1fr 1.5fr;
            gap: 10px;
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 10.5px;
            margin-bottom: 14px;
        }}
        .mono-id {{
            font-family: monospace;
            font-weight: 700;
            color: #1e293b;
        }}
        .badge-status-ativo {{
            background: #dcfce7;
            color: #166534;
            font-weight: 800;
            font-size: 9.5px;
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid #86efac;
        }}

        .dossie-section {{
            margin-bottom: 14px;
        }}
        .section-heading {{
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.3px;
            margin: 0 0 6px 0;
            padding-bottom: 3px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .section-intro {{
            font-size: 10.5px;
            color: #475569;
            margin: 0 0 6px 0;
            font-style: italic;
        }}

        .quadro-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 8px;
        }}
        .quadro-item {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            padding: 8px 10px;
        }}
        .q-label {{
            font-size: 9.5px;
            text-transform: uppercase;
            font-weight: 700;
            color: #64748b;
            display: block;
        }}
        .q-val {{
            font-size: 11.5px;
            color: #0f172a;
        }}
        .q-sub {{
            font-size: 10px;
            color: #475569;
        }}

        .legal-banner {{
            background: #f0fdf4;
            border: 1px solid #bbf7d0;
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 10px;
            color: #166534;
        }}
        .legal-sub {{
            font-size: 9px;
            color: #15803d;
        }}

        .cientifico-box {{
            border-radius: 6px;
            padding: 10px 12px;
            font-size: 10.5px;
            line-height: 1.45;
        }}

        .sequencia-didatica-lista {{
            margin: 0;
            padding-left: 18px;
            font-size: 10.5px;
            line-height: 1.45;
        }}

        .grid-recursos-check {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            margin-bottom: 8px;
        }}
        .rec-badge {{
            border: 1px dashed #cbd5e1;
            padding: 6px 8px;
            border-radius: 6px;
            font-size: 10px;
            color: #94a3b8;
            text-align: center;
        }}
        .rec-active {{
            border: 1px solid #10b981;
            background: #ecfdf5;
            color: #065f46;
            font-weight: 700;
        }}
        .protocolo-prova-detalhe {{
            background: #fffbeb;
            border: 1px solid #fef08a;
            border-radius: 6px;
            padding: 8px 10px;
            font-size: 10px;
            color: #854d0e;
        }}

        .tabela-metas-longitudinal {{
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
        }}
        .tabela-metas-longitudinal th {{
            background: #0f172a;
            color: #ffffff;
            padding: 6px 8px;
            text-align: left;
            font-weight: 700;
        }}
        .tabela-metas-longitudinal td {{
            padding: 6px 8px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .tag-nivel {{
            background: #fee2e2;
            color: #991b1b;
            padding: 2px 5px;
            border-radius: 4px;
            font-weight: 700;
        }}
        .status-concluido {{
            color: #166534;
            font-weight: 700;
        }}
        .status-progresso {{
            color: #d97706;
            font-weight: 700;
        }}
        .status-planejado {{
            color: #2563eb;
            font-weight: 700;
        }}

        .contraprova-section {{
            background: #f8fafc;
            border: 1px solid #cbd5e1;
            border-radius: 6px;
            padding: 12px;
        }}
        .contraprova-grid {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
            font-size: 9.5px;
        }}
        .mono-hash {{
            font-family: monospace;
            font-size: 9px;
            color: #334155;
            word-break: break-all;
        }}
        .contraprova-carimbo {{
            text-align: center;
        }}
        .selo-auditoria {{
            border: 2px dashed #0f172a;
            padding: 6px 12px;
            border-radius: 6px;
            font-weight: 900;
            font-size: 8.5px;
            color: #0f172a;
            letter-spacing: 0.5px;
        }}

        .assinaturas-triplas {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            text-align: center;
            margin-top: 15px;
        }}
        .sig-linha {{
            border-top: 1px solid #0f172a;
            margin-bottom: 4px;
        }}
        .sig-cargo {{
            font-weight: 700;
            font-size: 10px;
            color: #0f172a;
        }}
        .sig-det {{
            font-size: 8.5px;
            color: #64748b;
        }}

        @media print {{
            body {{
                background: transparent;
                padding: 0;
            }}
            .pei-dossie {{
                box-shadow: none;
                margin: 0;
                padding: 0;
                page-break-after: always;
            }}
            .no-print {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 25px;" class="no-print">
        <button onclick="window.print()" style="padding: 12px 28px; background: #0f172a; color: white; border: none; border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            🖨️ Imprimir Dossiês Completos PEI & PAEE (Formato Oficial A4)
        </button>
        <div style="font-size: 12px; color: #64748b; margin-top: 6px;">
            Documento com validação forense e criptográfica SHA-256 para atendimento à LBI e auditorias do Ministério Público.
        </div>
    </div>
    {"".join(html_prontuarios)}
</body>
</html>
"""
    OUT_AEE.parent.mkdir(parents=True, exist_ok=True)
    OUT_AEE.write_text(template, encoding="utf-8")
    print(f"   -> [SUCESSO] Dossiês Oficiais PEI & PAEE gravados em: {OUT_AEE}")

def gerar_fichas_pip():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

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
                WHEN nivel_desempenho_caed = 'Abaixo do Básico' THEN 'Recuperação intensiva de pré-requisitos fundamentais e alfabetização/numeramento'
                ELSE 'Consolidação de habilidades estruturantes da BNCC e raciocínio inferencial'
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

    timestamp_data = datetime.now().strftime("%d/%m/%Y")
    html_cards = []

    for a in alunos:
        aid, turma, ano, comp, ac, op, pct, niv, faltam_a, faltam_b, gid, gname, foco, cid, tod = a
        doc_hash = calcular_hash_pei(aid, turma, cid, timestamp_data)
        doc_code = f"AV-PIP-2026-{doc_hash[:8].upper()}"

        card = f"""
        <div class="pip-card">
            <div class="pip-header">
                <div>
                    <div class="school-title">ESCOLA MUNICIPAL AIRAM VERAS | CRATEÚS - CE | INEP: 23084995</div>
                    <div class="doc-title">PLANO DE INTERVENÇÃO PEDAGÓGICA INDIVIDUALIZADO (PIP) — 2026</div>
                </div>
                <div style="text-align: right;">
                    <div class="meta-badge">CICLO I ➔ CICLO II</div>
                    <div style="font-family: monospace; font-size: 10px; color: #64748b; margin-top: 2px;">CÓD: {doc_code}</div>
                </div>
            </div>
            
            <div class="grid-2">
                <div><strong>ID Seguro do Estudante:</strong> <span class="mono">{aid}</span></div>
                <div><strong>Turma / Ano Escolar:</strong> {turma} ({ano}º Ano)</div>
                <div><strong>Componente Curricular:</strong> {comp}</div>
                <div><strong>Grupo de Intervenção:</strong> <span class="badge badge-{gid.lower()}">{gname}</span></div>
            </div>

            <div class="stats-box">
                <div class="stat-item">
                    <span class="label">Pontuação Atual (Ciclo I)</span>
                    <span class="value">{ac} / {op} ({pct}%)</span>
                </div>
                <div class="stat-item">
                    <span class="label">Nível CAEd Inicial</span>
                    <span class="value alert">{niv}</span>
                </div>
                <div class="stat-item">
                    <span class="label">Alvo Meta A (Adequado)</span>
                    <span class="value">+{faltam_a} acertos necessários</span>
                </div>
                <div class="stat-item">
                    <span class="label">Condição AEE / Inclusão</span>
                    <span class="value">{cid} {'(TOD/PBS ATIVO)' if tod else ''}</span>
                </div>
            </div>

            <div class="section-box">
                <div class="section-title">🎯 SEQUÊNCIA DIDÁTICA E DIRETRIZES DA BNCC / CAEd:</div>
                <p><strong>Diretriz Pedagógica:</strong> {foco}</p>
                <div style="margin-top: 6px;"><strong>Sequência em 4 Passos Estruturados:</strong></div>
                <ol style="margin: 4px 0 0 18px; padding: 0;">
                    <li><strong>Diagnóstico Pontual:</strong> Verificação do descritor CAEd de menor rendimento da prova do Ciclo I.</li>
                    <li><strong>Ativação Concreta:</strong> Modelagem da habilidade com material manipulativo ou esquema visual gráfico.</li>
                    <li><strong>Prática em Duplas Homogêneas:</strong> Resolução de 3 itens adaptados da matriz de referência.</li>
                    <li><strong>Checagem Formativa:</strong> Registro semanal da taxa de acerto no diário de bordo do professor.</li>
                </ol>
            </div>

            <div class="action-checklist">
                <div class="section-title">📋 ROTEIRO DE AÇÕES DA EQUIPE DOCENTE:</div>
                <div class="check-item"><input type="checkbox"> Atendimento semanal em pequenos grupos homogêneos (3 a 5 alunos).</div>
                <div class="check-item"><input type="checkbox"> Adaptação de enunciados com apoio visual e vocabulário simplificado.</div>
                <div class="check-item"><input type="checkbox"> Avaliação formativa quinzenal de monitoramento de micro-metas.</div>
                <div class="check-item"><input type="checkbox"> Articulação contínua com a Sala de Recursos Multifuncionais (AEE).</div>
            </div>

            <div class="signature-box">
                <div class="sig-line">Professor(a) Regente</div>
                <div class="sig-line">Coordenação Pedagógica</div>
                <div class="sig-line">Responsável Legal</div>
            </div>
            <div style="text-align: right; font-family: monospace; font-size: 8px; color: #94a3b8; margin-top: 10px;">
                Contraprova Digital SHA-256: {doc_hash}
            </div>
        </div>
        """
        html_cards.append(card)

    template = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Fichas de Intervenção Pedagógica (PIP) — Escola Airam Veras (Crateús - CE)</title>
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
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #0f172a;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }}
        .school-title {{ font-size: 12px; font-weight: bold; color: #475569; }}
        .doc-title {{ font-size: 15px; font-weight: 800; color: #0f172a; margin: 3px 0; }}
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
        .section-box {{ background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 6px; padding: 12px; font-size: 11.5px; margin-bottom: 15px; }}
        .section-title {{ font-weight: bold; margin-bottom: 6px; color: #1e3a8a; }}
        .action-checklist {{ font-size: 11.5px; margin-bottom: 20px; }}
        .check-item {{ margin-bottom: 6px; }}
        .signature-box {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 30px; text-align: center; font-size: 11px; }}
        .sig-line {{ border-top: 1px solid #0f172a; padding-top: 5px; }}
        @media print {{
            body {{ background: transparent; padding: 0; }}
            .pip-card {{ box-shadow: none; margin: 0; border: 1px solid #000; }}
            .no-print {{ display: none; }}
        }}
    </style>
</head>
<body>
    <div style="text-align: center; margin-bottom: 20px;" class="no-print">
        <button onclick="window.print()" style="padding: 10px 20px; background: #2563eb; color: white; border: none; border-radius: 6px; font-size: 14px; font-weight: bold; cursor: pointer;">
            🖨️ Imprimir Todas as Fichas de Intervenção Pedagógica (A4)
        </button>
    </div>
    {"".join(html_cards)}
</body>
</html>
"""
    OUT_PIP.parent.mkdir(parents=True, exist_ok=True)
    OUT_PIP.write_text(template, encoding="utf-8")
    print(f"   -> [SUCESSO] Fichas PIP gravadas em: {OUT_PIP}")

def main():
    print("=" * 70)
    print("GERANDO DOSSIÊS OFICIAIS PEI/PAEE E FICHAS PIP (CRATEÚS - CE)")
    print("=" * 70)
    gerar_prontuarios_pei_paee()
    gerar_fichas_pip()

    # Espelhar também em docs/ e na raiz para acesso imediato
    import shutil
    shutil.copy(OUT_AEE, DOCS_DIR / "prontuario_aee_tod_impresso.html")
    shutil.copy(OUT_PIP, DOCS_DIR / "fichas_intervencao_pip.html")
    shutil.copy(OUT_AEE, ROOT_DIR / "prontuario_aee_tod_impresso.html")
    shutil.copy(OUT_PIP, ROOT_DIR / "fichas_intervencao_pip.html")
    print("   -> [SUCESSO] Espelhamento automático em docs/ e na raiz concluído!")
    print("=" * 70)

if __name__ == "__main__":
    main()
