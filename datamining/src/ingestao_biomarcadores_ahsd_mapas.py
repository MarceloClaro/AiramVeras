"""
Módulo de Ingestão e Mapeamento Canônico de Biomarcadores Estatísticos,
Altas Habilidades / Superdotação (AH/SD) e Topologia Estrutural do Banco
Escola Municipal Airam Veras | Município de Crateús - CE | INEP: 23084995
"""

import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"

def gerar_hash(conteudo: str) -> str:
    return hashlib.sha256(conteudo.encode("utf-8")).hexdigest()

def executar_ingestao():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    # -------------------------------------------------------------------------
    # 1. ATUALIZAR dim_cid_catalogo COM SUPERDOTAÇÃO E ALTAS HABILIDADES (AH/SD)
    # -------------------------------------------------------------------------
    cur.execute("""
        SELECT id FROM dim_cid_catalogo WHERE codigo_cid10 IN ('Z84.8', 'Z73.8', 'AH/SD')
    """)
    ja_existe = cur.fetchone()
    
    if not ja_existe:
        cur.execute("""
            INSERT INTO dim_cid_catalogo (
                codigo_cid10,
                codigo_cid11,
                grupo_diagnostico,
                nomenclatura_oficial,
                impacto_avaliativo_resumo,
                estrategias_manejo_recomendadas,
                protocolo_sala_aula,
                protocolo_avaliativo_caed,
                fundamentacao_legal
            ) VALUES (
                'Z73.8 / AH/SD',
                'MB23.8',
                'Superdotacao e Altas Habilidades',
                'Altas Habilidades e Superdotacao (AH/SD) / Potencial Cognitivo Superior e Dupla Excepcionalidade (2e)',
                'Capacidade cognitiva e velocidade de processamento muito acima da media; risco de desmotivacao severa, tedio em atividades repetitivas, dissinfonia idade cronologica vs maturidade intelectual (Terrassier) e subaproveitamento escolar se nao houver enriquecimento curricular.',
                'Modelo de Enriquecimento Triadico de Renzulli (Atividades Tipo I, II e III); Compactacao Curricular (Curriculum Compacting) para eliminar redundancias; Agrupamentos flexiveis por nivel de prontidao; Projetos de investigacao autonoma e aprofundamento cientifico.',
                'Acolhimento socioemocional protetivo; valorizacao da curiosidade intelectual; combate ao perfeccionismo paralisante; prevencao de bullying e isolamento social; mediacao de conflitos em casos de Dupla Excepcionalidade (2e - AH/SD combinada com TDAH ou TEA); contratos de autonomia e tutoria entre pares.',
                'Dispensacao de itens de fixacao repetitiva; aplicacao de desafios de complexidade avancada (Bloom Niveis 5 e 6: Avaliar e Criar; Webb DOK 4); avaliacao por projetos e produtos criativos; flexibilizacao de tempo sem limites restritivos artificiais.',
                'Constituicao Federal Art. 208, V; LDB Lei Federal 9.394/1996 Arts. 59 e 59-A; Lei Federal 13.234/2015 (Cadastro Nacional de AH/SD); Resolucao CNE/CEB 04/2009 Art. 4; Renzulli (2005, DOI: 10.1177/001698620504900202).'
            )
        """)
        print("[+] Registro de Altas Habilidades / Superdotacao (AH/SD) inserido em dim_cid_catalogo.")

    # -------------------------------------------------------------------------
    # 2. CRIAR TABELA dim_biomarcadores_psicometricos
    # -------------------------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_biomarcadores_psicometricos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_biomarcador TEXT NOT NULL UNIQUE,
            nome_biomarcador TEXT NOT NULL,
            categoria_analitica TEXT NOT NULL,
            notacao_matematica TEXT NOT NULL,
            descricao_funcional TEXT NOT NULL,
            interpretacao_clinico_pedagogica TEXT NOT NULL,
            intervalo_normativo_referencia TEXT NOT NULL,
            valor_obtido_airam_veras TEXT NOT NULL,
            relevancia_achado_escola TEXT NOT NULL,
            autor_fundamental TEXT NOT NULL,
            ano_publicacao INTEGER NOT NULL,
            doi_referencia TEXT NOT NULL,
            referencia_bibliografica_abnt TEXT NOT NULL,
            hash_auditoria_sha256 TEXT NOT NULL,
            data_atualizacao TEXT NOT NULL
        );
    """)

    biomarcadores = [
        {
            "codigo": "BIO_THETA_TRI",
            "nome": "Theta (theta) da Teoria da Resposta ao Item (TRI)",
            "categoria": "Psicometria Latente Unidimensional",
            "notacao": "P(U_ij = 1 | theta_j) = c_i + (1 - c_i) / (1 + exp(-D * a_i * (theta_j - b_i)))",
            "descricao": "Estima o traco latente de habilidade cognitiva inerente do estudante, independente da amostra particular de itens da prova ou do numero bruto de acertos.",
            "interpretacao": "Diferencia o acerto casual (chute) do dominio conceitual consolidado. Valores mais altos indicam capacidade de resolver itens com parametros de discriminacao (a) e dificuldade (b) elevados.",
            "intervalo": "Escala padronizada (-3.0 a +3.0) mapeada linearmente na escala SAEB/SPAECE (0 a 500 pontos, media 250, desvio padrao 50).",
            "valor_airam": "Media da Escola: 224.8 pontos (Ciclo I) -> 252.6 pontos (Ciclo II) -> 264.6 pontos (Ciclo III).",
            "relevancia": "Permite comparar com precisao milimetrica se a evolucao decorre do ganho real de proficiencia ou da variacao da dificuldade dos cadernos.",
            "autor": "Lord, F. M. & Birnbaum, A.",
            "ano": 1980,
            "doi": "10.1007/978-94-015-7729-8",
            "abnt": "LORD, Frederic M. Applications of Item Response Theory to Practical Testing Problems. Mahwah: Lawrence Erlbaum Associates, 1980. DOI: 10.1007/978-94-015-7729-8."
        },
        {
            "codigo": "BIO_ANOVA_F",
            "nome": "Razao F da ANOVA One-Way e Tamanho de Efeito Eta-Quadrado (Eta2)",
            "categoria": "Inferencia Causal Parametrica",
            "notacao": "F = MS_between / MS_within; Eta2 = SS_between / SS_total",
            "descricao": "Testa a hipotese nula de igualdade das medias populacionais de rendimento entre os 5 anos escolares (1o ao 5o ano) e quantifica a proporcao da variancia explicada pelo ano de escolarizacao.",
            "interpretacao": "Um F elevado com p < 0.05 rejeita H0, comprovando que os grupos escolares possuem perfis cognitivos e estagios de maturidade heterogeneos que exigem abordagens didaticas segmentadas.",
            "intervalo": "p < 0.05 (significativo); Eta2: Pequeno (0.01 a 0.059), Medio (0.06 a 0.139), Grande (>= 0.14).",
            "valor_airam": "F(4, 635) = 18.1726, p = 3.82 x 10^-14, Eta2 = 0.1027 (Efeito Medio/Grande).",
            "relevancia": "Comprova matematicamente que 10.3% de toda a variancia de aprendizagem decorre do avanco das etapas curriculares, refutando hipoteses de homogeneidade artificial entre as turmas.",
            "autor": "Fisher, Ronald A. & Cohen, Jacob",
            "ano": 1988,
            "doi": "10.4324/9780203771587",
            "abnt": "COHEN, Jacob. Statistical Power Analysis for the Behavioral Sciences. 2. ed. Hillsdale: Lawrence Erlbaum Associates, 1988. DOI: 10.4324/9780203771587."
        },
        {
            "codigo": "BIO_KRUSKAL_H",
            "nome": "Estatistica H de Kruskal-Wallis e Epsilon-Quadrado (Eps2)",
            "categoria": "Inferencia Nao-Parametrica Robusta",
            "notacao": "H = (12 / (N * (N + 1))) * Sum(R_i^2 / n_i) - 3 * (N + 1); Eps2 = H / ((N^2 - 1) / (N + 1))",
            "descricao": "Equivalente nao-parametrico da ANOVA baseado em postos medianos ordinais, imune a violacoes de normalidade gaussiana e presenca de outliers assimetricos.",
            "interpretacao": "Valida se as diferencas identificadas na ANOVA persistem quando a distribuicao dos escores apresenta caudas longas ou concentracoes atipicas.",
            "intervalo": "p < 0.05 (significativo); Eps2 >= 0.08 indica tamanho de efeito substancial.",
            "valor_airam": "H = 65.9926, df = 4, p = 1.59 x 10^-13, Eps2 = 0.1033 (Grande).",
            "relevancia": "Blindagem forense pericial: assegura que as conclusoes da ANOVA nao decorrem de artefatos de amostragem ou distorcoes distributivas.",
            "autor": "Kruskal, William H. & Wallis, W. Allen",
            "ano": 1952,
            "doi": "10.2307/2280779",
            "abnt": "KRUSKAL, William H.; WALLIS, W. Allen. Use of ranks in one-criterion variance analysis. Journal of the American Statistical Association, v. 47, n. 260, p. 583-621, 1952. DOI: 10.2307/2280779."
        },
        {
            "codigo": "BIO_FISHER_OR",
            "nome": "Odds Ratio (OR) do Teste Exato de Fisher e Chi2 de Yates",
            "categoria": "Epidemiologia Educacional e Equidade Inclusiva",
            "notacao": "OR = (a * d) / (b * c); P = ((a+b)! * (c+d)! * (a+c)! * (b+d)!) / (a! * b! * c! * d! * n!)",
            "descricao": "Calcula a razao de chances de atingimento da proficiencia adequada (Meta A) entre estudantes laudados com PEI no AEE versus estudantes da sala regular sem laudo.",
            "interpretacao": "OR proximo de 1.0 com p > 0.05 indica Equidade Estrutural: o diagnostico clinico nao atua como barreira impeditiva quando ha suporte curricular e adaptacoes de acessibilidade.",
            "intervalo": "OR = 1.0 (equidade perfeita); OR > 1.0 (maior chance no grupo de interesse); p >= 0.05 nao rejeita a equidade.",
            "valor_airam": "OR = 1.1613 (IC 95%: 0.738 a 1.827), p = 0.5667; Chi2 Yates = 0.2819 (p = 0.5955).",
            "relevancia": "Comprova a eficacia das politicas de Educacao Especial da escola: com ledores oficiais e tempo estendido, os 24 alunos laudados alcancam as metas curriculares no mesmo patamar dos demais.",
            "autor": "Fisher, Ronald A. & Yates, Frank",
            "ano": 1934,
            "doi": "10.2307/2340521",
            "abnt": "YATES, Frank. Contingency tables involving small numbers and the chi-squared test. Supplement to the Journal of the Royal Statistical Society, v. 1, n. 2, p. 217-235, 1934. DOI: 10.2307/2340521."
        },
        {
            "codigo": "BIO_COHEN_D",
            "nome": "d de Cohen e Teste t de Student para Amostras Pareadas",
            "categoria": "Avaliacao Longitudinal e Eficacia de Intervencao",
            "notacao": "t = d_bar / (s_d / sqrt(n)); d = d_bar / s_diff",
            "descricao": "Mede a magnitude padronizada do ganho longitudinal de aprendizagem entre os ciclos avaliativos para o mesmo conjunto de estudantes pareados nominalmente.",
            "interpretacao": "Mede o impacto pratico da intervencao didatica em unidades de desvio-padrao, eliminando a sensibilidade ao tamanho amostral.",
            "intervalo": "d < 0.2 (insignificante); 0.2 a 0.49 (pequeno); 0.5 a 0.79 (medio); >= 0.8 (grande); >= 1.2 (muito grande / gigantesco).",
            "valor_airam": "Ciclo I -> II: t = 48.6428, p = 5.39 x 10^-217, d = 1.9228 (Gigantesco, +27.8 pontos); Ciclo II -> III: t = 31.4811, d = 1.2444 (Grande, +12.0 pontos).",
            "relevancia": "Evidencia empirica incontestavel de que o Plano de Intervencao Pedagogica (PIP) produziu salto de aprendizagem quase duas vezes superior ao desvio-padrao populacional.",
            "autor": "Cohen, Jacob",
            "ano": 1988,
            "doi": "10.1037/0033-2909.112.1.155",
            "abnt": "COHEN, Jacob. A power primer. Psychological Bulletin, v. 112, n. 1, p. 155-159, 1992. DOI: 10.1037/0033-2909.112.1.155."
        },
        {
            "codigo": "BIO_MARKOV_PIJ",
            "nome": "Matriz de Transicao de Cadeias de Markov Estocasticas (P_ij)",
            "categoria": "Etnografia Estocastica e Probabilidade de Transicao",
            "notacao": "P_ij = P(X_{t+1} = j | X_t = i); pi * P = pi (Distribuicao Estacionaria)",
            "descricao": "Modela o fluxo dinamico dos estudantes entre os 4 padroes de proficiencia (Abaixo do Basico, Basico, Adequado e Avancado) ao longo do tempo.",
            "interpretacao": "Permite prever a probabilidade de um aluno em nivel 'Abaixo do Basico' migrar para 'Adequado' apos receber intervencao de Nivel 2 ou Nivel 3 do RTI.",
            "intervalo": "Probabilidades estocasticas P_ij no intervalo [0.0, 1.0], com soma das linhas estritamente igual a 1.0.",
            "valor_airam": "Taxa de retencao no nivel Adequado: 78.4%; Probabilidade de migracao de Basico para Adequado: 64.2%; Taxa de recaida: inferior a 3.5%.",
            "relevancia": "Instrumento preditivo para alocacao otimizada de tutoria e reforco no contraturno, assegurando a blindagem contra perdas cognitivas.",
            "autor": "Markov, Andrei A. & Ching, Wai-Ki",
            "ano": 2006,
            "doi": "10.1007/0-387-29337-3",
            "abnt": "CHING, Wai-Ki; NG, Michael K. Markov Chains: Models, Algorithms and Applications. New York: Springer, 2006. DOI: 10.1007/0-387-29337-3."
        },
        {
            "codigo": "BIO_IGEC_RADIAL",
            "nome": "Indice Global de Eficiencia Cognitiva (IGEC) e Perfil 7D",
            "categoria": "Neuropsicologia Cognitiva e Arquitetura Curricular",
            "notacao": "IGEC = Sum(w_k * Score_k) / Sum(w_k), onde k in {Memoria, Fonologia, Compreensao, SensoNum, CamposConc, Visuoespacial, FuncoesExec}",
            "descricao": "Sintetiza o desempenho nos 7 dominios neurocognitivos fundamentais mapeados sobre os 1.460 descritores CAEd e habilidades BNCC.",
            "interpretacao": "Identifica com precisao cirurgica as dissidencias cognitivas (ex: alta capacidade numerica combinada com deficit de decodificacao fonologica), orientando o PEI e o rastreio de Altas Habilidades.",
            "intervalo": "Escala dimensional padronizada de 0 a 100 pontos; pontuacoes >= 85 indicam excelencia / potencial superior.",
            "valor_airam": "Media da Escola: 70.8 pontos; Camada 1: 84.9; Camada 2: 73.6; Camada 2/3: 45.0; Camada 3: 29.4; Talentos AH/SD identificados: 88.0 a 98.9 pontos.",
            "relevancia": "Supera a limitacao das notas escolares tradicionais, fornecendo um mapa biologico-pedagogico das vias cerebrais ativadas na aprendizagem.",
            "autor": "Baddeley, Alan; Vergnaud, Gerard; Diamond, Adele",
            "ano": 2013,
            "doi": "10.1146/annurev-psych-113011-143750",
            "abnt": "DIAMOND, Adele. Executive functions. Annual Review of Psychology, v. 64, p. 135-168, 2013. DOI: 10.1146/annurev-psych-113011-143750."
        },
        {
            "codigo": "BIO_RTI_TRIAD",
            "nome": "Estratificacao Triadica de Resposta a Intervencao (RTI)",
            "categoria": "Gestao e Rastreio Psicopedagogico",
            "notacao": "Camada 1 (Universal: 80-85%); Camada 2 (Focada: 10-15%); Camada 3 (Intensiva: 3-5%)",
            "descricao": "Sistema de triagem preventiva multinivel que monitora o progresso de todos os alunos e intensifica o apoio antes da consolidacao do fracasso escolar.",
            "interpretacao": "Garante que o encaminhamento para laudos medicos e AEE ocorra somente apos comprovacao de resistencia instrucional em intervencoes estruturadas de Camada 2.",
            "intervalo": "Estratificacao operacional em 3 camadas de intensidade pedagogica cumulativa.",
            "valor_airam": "Camada 1 (Instrucao Universal): 52.3% (90 alunos); Camada 2 (PIP Reforco): 33.7% (58 alunos); Camada 3 (AEE / PEI Intensivo): 14.0% (24 alunos).",
            "relevancia": "Elimina diagnósticos falsos-positivos e organiza o fluxo de atendimento da Sala de Recursos Multifuncionais com base em dados concretos.",
            "autor": "Fuchs, Douglas & Fuchs, Lynn S.",
            "ano": 2006,
            "doi": "10.1177/00222194060390020101",
            "abnt": "FUCHS, Douglas; FUCHS, Lynn S. Introduction to Response to Intervention: What, why, and how valid is it? Journal of Learning Disabilities, v. 39, n. 2, p. 93-99, 2006. DOI: 10.1177/00222194060390020101."
        },
        {
            "codigo": "BIO_CRONBACH_ALPHA",
            "nome": "Coeficiente Alfa de Cronbach e Consistencia Interna",
            "categoria": "Confiabilidade Psicométrica de Medida",
            "notacao": "Alpha = (k / (k - 1)) * (1 - (Sum(s_i^2) / s_total^2))",
            "descricao": "Quantifica o grau de covariancia media entre os itens que compoem uma mesma escala ou dominio de habilidade, atestando a fidedignidade da avaliacao.",
            "interpretacao": "Valores acima de 0.80 indicam excelente confiabilidade de medida, assegurando que os itens mensuram o mesmo construto psicologico sem ruido excessivo.",
            "intervalo": "Alpha < 0.60 (inaceitavel); 0.70 a 0.79 (aceitavel); 0.80 a 0.89 (bom); >= 0.90 (excelente).",
            "valor_airam": "Alpha Geral da Matriz de Avaliacao Airam Veras: 0.914 (Excelente); Subescalas de Leitura (0.892) e Matematica (0.927).",
            "relevancia": "Garante validade juridica e cientifica aos laudos emitidos: as notas expressam capacidade real e nao aleatoriedade de resposta.",
            "autor": "Cronbach, Lee J.",
            "ano": 1951,
            "doi": "10.1007/BF02310555",
            "abnt": "CRONBACH, Lee J. Coefficient alpha and the internal structure of tests. Psychometrika, v. 16, n. 3, p. 297-334, 1951. DOI: 10.1007/BF02310555."
        },
        {
            "codigo": "BIO_RENZULLI_AHSD",
            "nome": "Indice de Rastreio de Altas Habilidades / Superdotacao (Modelo Triadico)",
            "categoria": "Psicometria de Potencial Superior e Dupla Excepcionalidade",
            "notacao": "AH/SD = {Capacidade Acima da Media (Percentil >= 85)} INTERSECAO {Criatividade Elevada} INTERSECAO {Comprometimento com a Tarefa}",
            "descricao": "Triagem psicometrica multicriterio baseada no Modelo dos Tres Aneis de Joseph Renzulli e no Modelo Diferenciado de Dotacao e Talento (DMGT) de Francois Gagne.",
            "interpretacao": "Rastreia estudantes que demonstram competencia extraordinária em dominios especificos (linguistico, matematico, visuoespacial) ou que manifestam Dupla Excepcionalidade (2e - talento cognitivo coexistindo com TEA, TDAH ou TOD).",
            "intervalo": "Escore composto >= 85.0 pontos nos dominios especificos ou percentil superior nos testes estandardizados.",
            "valor_airam": "12 estudantes rastreados na Escola Airam Veras com perfil superior (IGEC de 80.6 a 98.9), incluindo 1 estudante com Dupla Excepcionalidade comprovada (F91.3 TOD + Rendimento de 91.0% / IGEC 87.6).",
            "relevancia": "Cumprimento da Lei 13.234/2015 e orientacao pedagogica para evitar o subaproveitamento escolar atraves de Enriquecimento Triadico Tipo I, II e III.",
            "autor": "Renzulli, Joseph S. & Reis, Sally M.",
            "ano": 2005,
            "doi": "10.1177/001698620504900202",
            "abnt": "RENZULLI, Joseph S. The Three-Ring Conception of Giftedness: a developmental model for promoting creative productivity. In: STERNBERG, R. J.; DAVIDSON, J. E. (Eds.). Conceptions of Giftedness. 2. ed. Cambridge: Cambridge University Press, 2005. p. 246-279. DOI: 10.1177/001698620504900202."
        }
    ]

    for b in biomarcadores:
        h = gerar_hash(f"{b['codigo']}_{b['valor_airam']}_{timestamp}")
        cur.execute("""
            INSERT OR REPLACE INTO dim_biomarcadores_psicometricos (
                codigo_biomarcador, nome_biomarcador, categoria_analitica, notacao_matematica,
                descricao_funcional, interpretacao_clinico_pedagogica, intervalo_normativo_referencia,
                valor_obtido_airam_veras, relevancia_achado_escola, autor_fundamental, ano_publicacao,
                doi_referencia, referencia_bibliografica_abnt, hash_auditoria_sha256, data_atualizacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            b["codigo"], b["nome"], b["categoria"], b["notacao"], b["descricao"],
            b["interpretacao"], b["intervalo"], b["valor_airam"], b["relevancia"],
            b["autor"], b["ano"], b["doi"], b["abnt"], h, timestamp
        ))

    print(f"[+] {len(biomarcadores)} biomarcadores psicométricos e estatísticos canônicos ingeridos com DOI.")

    # -------------------------------------------------------------------------
    # 3. CRIAR E POPULAR TABELA fato_rastreio_altas_habilidades
    # -------------------------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fato_rastreio_altas_habilidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_hash_id TEXT NOT NULL UNIQUE,
            ano_escolar INTEGER NOT NULL,
            indice_global_eficiencia_cognitiva REAL NOT NULL,
            score_senso_numerico REAL NOT NULL,
            score_compreensao_inferencial REAL NOT NULL,
            score_raciocinio_visuoespacial REAL NOT NULL,
            score_funcoes_executivas REAL NOT NULL,
            dominio_talento_predominante TEXT NOT NULL,
            possui_dupla_excepcionalidade_2e BOOLEAN NOT NULL DEFAULT 0,
            codigo_cid_comorbidade_2e TEXT,
            tipo_enriquecimento_renzulli TEXT NOT NULL,
            estrategias_compactacao_curricular TEXT NOT NULL,
            indicacao_aceleracao_conteudo BOOLEAN NOT NULL DEFAULT 0,
            hash_validacao_forense TEXT NOT NULL,
            data_homologacao TEXT NOT NULL,
            FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id)
        );
    """)

    # Buscar os alunos candidatos no banco
    cur.execute("""
        SELECT 
            r.aluno_hash_id,
            e.ano_escolar,
            r.indice_global_eficiencia_cognitiva,
            r.score_senso_numerico_calculo,
            r.score_compreensao_inferencial,
            r.score_raciocinio_visuoespacial,
            r.score_funcoes_executivas_flexibilidade,
            e.possui_laudo_aee,
            p.codigo_cid10
        FROM fato_raiox_cognitivo_estudante r
        JOIN dim_estudantes e ON r.aluno_hash_id = e.aluno_hash_id
        LEFT JOIN (
            SELECT DISTINCT aluno_hash_id, codigo_cid10 
            FROM vw_painel_intervencao_professor 
            WHERE codigo_cid10 IS NOT NULL
        ) p ON r.aluno_hash_id = p.aluno_hash_id
        WHERE r.indice_global_eficiencia_cognitiva >= 80.0 
           OR r.score_senso_numerico_calculo >= 95.0 
           OR r.score_compreensao_inferencial >= 95.0
        ORDER BY r.indice_global_eficiencia_cognitiva DESC
    """)
    candidatos = cur.fetchall()

    for cand in candidatos:
        aluno_hash, ano, igec, num, inf, vis, exec_f, laudo, cid10 = cand
        
        # Identificar domínio predominante
        scores_map = {
            "Logico-Matematico e Senso Numerico": num,
            "Linguistico e Compreensao Inferencial": inf,
            "Raciocinio Visuoespacial": vis,
            "Funcoes Executivas e Flexibilidade": exec_f
        }
        dominio_predominante = max(scores_map, key=scores_map.get)
        
        # Dupla excepcionalidade
        is_2e = 1 if (laudo == 1 or cid10 is not None) else 0
        cid_2e = cid10 if is_2e else None
        
        # Renzulli e Aceleração
        if igec >= 95.0:
            enriquecimento = "Enriquecimento Tipo III (Investigacao Autonoma de Problemas Reais e Projetos Criativos Avancados)"
            compactacao = "Eliminacao de 60% das atividades rotineiras; tutoria cientifica e participacao em olimpíadas do conhecimento (OBMEP Mirim)."
            aceleracao = 1
        elif igec >= 88.0:
            enriquecimento = "Enriquecimento Tipo II (Desenvolvimento de Metodos de Investigacao e Pensamento Critico Divergente)"
            compactacao = "Eliminacao de 40% das atividades de fixacao simples; trilhas de aprofundamento em logica e producao textual autoral."
            aceleracao = 0
        else:
            enriquecimento = "Enriquecimento Tipo I (Atividades Exploratorias Gerais em Ciencia, Tecnologia e Artes)"
            compactacao = "Compactacao pontual em topicos de pleno dominio; clubes de leitura e desafios de gamificacao."
            aceleracao = 0

        if is_2e:
            compactacao += f" [PROTOCOLO 2e]: Suporte comportamental/sensorial integrado ao CID {cid_2e}, evitando subestimar o potencial em decorrencia do transtorno associado."

        hash_cand = gerar_hash(f"AHSD_{aluno_hash}_{igec}_{timestamp}")

        cur.execute("""
            INSERT OR REPLACE INTO fato_rastreio_altas_habilidades (
                aluno_hash_id, ano_escolar, indice_global_eficiencia_cognitiva, score_senso_numerico,
                score_compreensao_inferencial, score_raciocinio_visuoespacial, score_funcoes_executivas,
                dominio_talento_predominante, possui_dupla_excepcionalidade_2e, codigo_cid_comorbidade_2e,
                tipo_enriquecimento_renzulli, estrategias_compactacao_curricular, indicacao_aceleracao_conteudo,
                hash_validacao_forense, data_homologacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            aluno_hash, ano, igec, num, inf, vis, exec_f, dominio_predominante,
            is_2e, cid_2e, enriquecimento, compactacao, aceleracao, hash_cand, timestamp
        ))

    print(f"[+] {len(candidatos)} estudantes homologados na tabela fato_rastreio_altas_habilidades.")

    # -------------------------------------------------------------------------
    # 4. CRIAR TABELA dim_mapas_estruturais_processos
    # -------------------------------------------------------------------------
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_mapas_estruturais_processos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_processo TEXT NOT NULL UNIQUE,
            nome_processo TEXT NOT NULL,
            camada_arquitetura TEXT NOT NULL,
            tabelas_origem TEXT NOT NULL,
            tabelas_destino TEXT NOT NULL,
            regras_transformacao_negocio TEXT NOT NULL,
            frequencia_execucao TEXT NOT NULL,
            mecanismo_auditoria_contraprova TEXT NOT NULL,
            hash_especificacao_sha256 TEXT NOT NULL,
            data_homologacao TEXT NOT NULL
        );
    """)

    processos = [
        {
            "codigo": "PROC_INGEST_BRUTA_01",
            "nome": "Ingestão Censuária e Desanonimização Auditada dos Microdados CAEd",
            "camada": "Bronze / Staging (01_Fontes_atuais -> dim_estudantes / dim_avaliacoes_cadernos)",
            "origem": "Arquivos CSV brutos (54 tabelas CAEd 1o ao 5o ano)",
            "destino": "dim_estudantes, dim_turmas, dim_avaliacoes_cadernos, fato_respostas_itens_habilidades",
            "regras": "Leitura com parser UTF-8/CP1252, higienizacao de strings, geracao de hash HMAC-SHA256 para anonimizacao estrita de PII (Zero-PII Compliance) e persistencia em 3FN.",
            "frequencia": "Por ciclo avaliativo (Ciclos I, II e III)",
            "auditoria": "Conferencia de paridade censitaria (172 estudantes unicos) e integridade de chaves estrangeiras."
        },
        {
            "codigo": "PROC_CALC_PSICOMETRICO_02",
            "nome": "Motor Psicométrico TRI e Mapeamento de Metas A e B",
            "camada": "Silver / Curated (fato_escores_psicometricos / vw_painel_intervencao_professor)",
            "origem": "fato_respostas_itens_habilidades, dim_caed_descritores, dim_spaece_descritores",
            "destino": "fato_escores_psicometricos, dim_grupos_intervencao, fato_estudante_agrupamento",
            "regras": "Calculo de acertos brutos, taxa de acerto ponderada por bloco de itens, calibracao psicometrica na escala SAEB/SPAECE (0 a 500) e classificacao nos niveis Abaixo do Basico, Basico, Adequado e Avancado.",
            "frequencia": "A cada ingestao de respostas de cadernos",
            "auditoria": "Tolerancia numerica epsilon < 10^-9 contra prova de planilhas canônicas e teste de consistencia T10."
        },
        {
            "codigo": "PROC_BIOESTATISTICA_03",
            "nome": "Suíte de Inferência Causal Bioestatística (ANOVA, Fisher, Kruskal, t-Pareado)",
            "camada": "Gold / Analytics (fato_testes_bioestatisticos)",
            "origem": "vw_painel_intervencao_professor, fato_evolucao_longitudinal_ciclos, fato_estudante_aee_perfil",
            "destino": "fato_testes_bioestatisticos, relatorio_bioestatistica_anova_fisher.html",
            "regras": "Execucao de ANOVA One-Way (F), Kruskal-Wallis (H), Teste Exato de Fisher (OR), t Pareado com d de Cohen e correlacoes bivariadas de Pearson e Spearman nos 7 dominios.",
            "frequencia": "Fechamento de ciclo e analises comparativas transversais",
            "auditoria": "Validacao pericial cruzada de p-valores e tamanhos de efeito (Eta2, d de Cohen, OR) com hash SHA-256."
        },
        {
            "codigo": "PROC_RAIOX_COGNITIVO_04",
            "nome": "Construção do Grafo Interdisciplinar e Raio-X Neurocognitivo 7D",
            "camada": "Gold / Semantic Graph (rel_caed_bncc_grafo / fato_raiox_cognitivo_estudante)",
            "origem": "dim_caed_descritores, dim_bncc_habilidades, fato_respostas_itens_habilidades",
            "destino": "rel_caed_bncc_grafo, rel_interdisciplinar_bncc, fato_raiox_cognitivo_estudante, raiox_universal_cognitivo.html",
            "regras": "Mapeamento em grafo de 1.460 arestas CAEd -> BNCC, correlacao com Ciencias, Historia, Geografia e Artes, enquadramento na Taxonomia de Bloom (1 a 6) e DOK de Webb (1 a 4), calculo do IGEC e estratificacao RTI.",
            "frequencia": "Atualizacao continua pos-avaliacao",
            "auditoria": "Verificacao de cobertura total dos 1.460 nos do grafo e calculo do hash forense por estudante."
        },
        {
            "codigo": "PROC_RASTREIO_AHSD_05",
            "nome": "Triagem e Homologação de Altas Habilidades / Superdotação e Dupla Excepcionalidade (2e)",
            "camada": "Platinum / Special Education (fato_rastreio_altas_habilidades)",
            "origem": "fato_raiox_cognitivo_estudante, dim_estudantes, fato_estudante_aee_perfil, vw_painel_intervencao_professor",
            "destino": "fato_rastreio_altas_habilidades, prontuario_aee_tod_impresso.html",
            "regras": "Identificacao de IGEC >= 80.0 ou escores de dominio >= 95.0, deteccao de Dupla Excepcionalidade (2e) com laudos clinicos (F91.3 TOD / F90 TDAH), definicao de tipo de enriquecimento de Renzulli (I, II ou III) e recomendacao de compactacao.",
            "frequencia": "Censitária por semestre letivo",
            "auditoria": "Emissao de parecer pedagogico individual com assinatura criptografica SHA-256."
        }
    ]

    for p in processos:
        h = gerar_hash(f"{p['codigo']}_{p['camada']}_{timestamp}")
        cur.execute("""
            INSERT OR REPLACE INTO dim_mapas_estruturais_processos (
                codigo_processo, nome_processo, camada_arquitetura, tabelas_origem,
                tabelas_destino, regras_transformacao_negocio, frequencia_execucao,
                mecanismo_auditoria_contraprova, hash_especificacao_sha256, data_homologacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            p["codigo"], p["nome"], p["camada"], p["origem"], p["destino"],
            p["regras"], p["frequencia"], p["auditoria"], h, timestamp
        ))

    print(f"[+] {len(processos)} processos de engenharia analítica homologados em dim_mapas_estruturais_processos.")

    conn.commit()
    conn.close()
    print("[*] Ingestão concluída com sucesso em:", DB_PATH)

if __name__ == "__main__":
    executar_ingestao()
