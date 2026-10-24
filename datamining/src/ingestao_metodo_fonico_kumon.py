"""
Módulo de Ingestão e Mapeamento da Rede Interdisciplinar:
Método Fônico Sistemático + Kumon Granular Autodidata + Neurociência Cognitiva Aplicada
Escola Municipal Airam Veras | Crateús - CE | INEP: 23084995
"""

import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"

def gerar_hash(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()

def executar_ingestao():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")
    
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    # 1. dim_metodologias_aprendizagem
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_metodologias_aprendizagem (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_metodologia TEXT NOT NULL UNIQUE,
            nome_metodologia TEXT NOT NULL,
            foco_pedagogico TEXT NOT NULL,
            fundamento_neurocientifico TEXT NOT NULL,
            mecanismo_autodidatismo TEXT NOT NULL,
            referencia_principal TEXT NOT NULL,
            doi_referencia TEXT NOT NULL
        );
    """)

    metodologias = [
        (
            "MET_FONICO_SISTEMATICO",
            "Método Fônico Sistemático e Explícito (Synthetic Phonics)",
            "Alfabetização, Precisão Decodificatória Fonema-Grafema, Ortografia e Fluência Leitora",
            "Ativação da Área da Forma Visual das Palavras (VWFA) no giro fusiforme esquerdo; reciclagem neuronal e automatização da via lexical.",
            "Listas graduadas de leitura autocorretiva, audição fonêmica com contraprova e leitura em pares.",
            "Dehaene, Stanislas. Os Neurônios da Leitura (2012); Ehri, Linnea (2005).",
            "10.1093/acprof:oso/9780199753871.001.0001"
        ),
        (
            "MET_KUMON_GRANULAR",
            "Método Kumon Granular de Micro-passos (Small-Step Mastery)",
            "Autodidatismo, Cálculo Mental Rápido, Resolução Autônoma e Fluência sem Lacunas",
            "Teoria da Carga Cognitiva de Sweller: redução da carga extrínseca para automação de esquemas na memória de longo prazo; potenciação de longa duração (LTP).",
            "Exemplos autoexplicativos no topo de cada folha, autocorreção imediata de erros e respeito ao ritmo intrínseco.",
            "Kumon, Toru (1958); Sweller, John (1988); Ericsson, K. Anders (1993).",
            "10.1207/s15516709cog1202_4"
        ),
        (
            "MET_NEUROCIENCIA_REDE",
            "Neurociência Cognitiva Aplicada em Rede Interdisciplinar",
            "Integração Multidisciplinar, Repetição Espaçada, Funções Executivas e Campos Conceituais",
            "Otimização do córtex pré-frontal dorsolateral (DLPFC), alça fonológica de Baddeley, campos conceituais aditivos e multiplicativos de Vergnaud.",
            "Projetos de investigação interdisciplinar guiados por desafios abertos com autoavaliação formativa.",
            "Baddeley, Alan (2000); Vergnaud, Gérard (2009); Diamond, Adele (2013).",
            "10.1146/annurev-psych-113011-143750"
        )
    ]

    for m in metodologias:
        cur.execute("""
            INSERT OR REPLACE INTO dim_metodologias_aprendizagem (
                codigo_metodologia, nome_metodologia, foco_pedagogico, fundamento_neurocientifico,
                mecanismo_autodidatismo, referencia_principal, doi_referencia
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, m)

    # 2. dim_kumon_niveis_granulares
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_kumon_niveis_granulares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_nivel TEXT NOT NULL UNIQUE,
            disciplina_eixo TEXT NOT NULL CHECK(disciplina_eixo IN ('MATEMATICA', 'LEITURA_LINGUAGEM')),
            nome_nivel TEXT NOT NULL,
            ano_escolar_sugerido INTEGER NOT NULL,
            foco_operacional_micro_passo TEXT NOT NULL,
            tempo_padrao_conclusao_min INTEGER NOT NULL,
            meta_maestria_pct REAL NOT NULL,
            descritores_caed_alvo TEXT NOT NULL,
            habilidades_bncc_alvo TEXT NOT NULL,
            prerequisito_nivel TEXT
        );
    """)

    niveis_kumon = [
        ("KUMON_MAT_7A_5A", "MATEMATICA", "Nível 7A a 5A: Coordenação Grafomotora e Traçado 1-10", 1, "Domínio do lápis, traçado numérico 1 a 10 e correspondência biunívoca.", 2, 100.0, "D01_M", "EF01MA01", None),
        ("KUMON_MAT_4A_3A", "MATEMATICA", "Nível 4A a 3A: Numerais até 50 e Subitização", 1, "Reconhecimento numérico até 50, contagem rápida de pontos e agrupamentos de 5 e 10.", 3, 100.0, "D02_M", "EF01MA02", "KUMON_MAT_7A_5A"),
        ("KUMON_MAT_2A_A", "MATEMATICA", "Nível 2A a A: Adição Básica (+1 a +10)", 1, "Fatos fundamentais da adição horizontal sem cálculo nos dedos; automação motora e mental.", 3, 95.0, "D03_M, D04_M", "EF01MA06, EF02MA05", "KUMON_MAT_4A_3A"),
        ("KUMON_MAT_B", "MATEMATICA", "Nível B: Adição e Subtração Vertical com Reagrupamento", 2, "Adição e subtração com 'vai um' e 'empresta' com 2 a 3 dígitos.", 4, 90.0, "D05_M, D06_M", "EF02MA06, EF03MA05", "KUMON_MAT_2A_A"),
        ("KUMON_MAT_C", "MATEMATICA", "Nível C: Tabuada Elementar e Multiplicação/Divisão", 3, "Automação da tabuada do 2 ao 9 e algoritmos de multiplicação e divisão com restos.", 5, 90.0, "D07_M, D08_M", "EF03MA07, EF04MA04", "KUMON_MAT_B"),
        ("KUMON_MAT_D", "MATEMATICA", "Nível D: Multiplicação/Divisão Multidígitos e Frações Iniciais", 4, "Algoritmos longos de multiplicação/divisão e noções de frações próprias e equivalência.", 6, 85.0, "D09_M, D10_M", "EF04MA05, EF05MA08", "KUMON_MAT_C"),
        ("KUMON_MAT_E_F", "MATEMATICA", "Nível E a F: Operações com Frações, Decimais e Proporção", 5, "Operações com frações heterogêneas, decimais, porcentagem e raciocínio proporcional.", 8, 85.0, "D11_M a D15_M", "EF05MA02, EF05MA07", "KUMON_MAT_D"),
        
        ("KUMON_LEIT_7A_4A", "LEITURA_LINGUAGEM", "Nível 7A a 4A: Pareamento Palavra-Imagem e Sons Iniciais", 1, "Discriminação visual de palavras simples, conexão com imagens e correspondência sonora.", 2, 100.0, "D01_LP", "EF01LP01", None),
        ("KUMON_LEIT_3A_2A", "LEITURA_LINGUAGEM", "Nível 3A a 2A: Rimas, Sílabas Simples e Frases Curtas", 1, "Leitura de palavras com padrão CV (consoante-vogal), frases curtas e ritmo cadenciado.", 3, 95.0, "D02_LP", "EF01LP02", "KUMON_LEIT_7A_4A"),
        ("KUMON_LEIT_A_B", "LEITURA_LINGUAGEM", "Nível A a B: Sílabas Complexas e Parágrafos Narrativos", 2, "Dígrafos, encontros consonantais, leitura de pequenos textos e identificação de personagens.", 4, 90.0, "D03_LP", "EF02LP04", "KUMON_LEIT_3A_2A"),
        ("KUMON_LEIT_C_D", "LEITURA_LINGUAGEM", "Nível C a D: Compreensão de Ideia Central e Vocabulário", 3, "Extração de tópicos frasais, ordenação temporal e identificação de relações de causa-efeito.", 5, 90.0, "D04_LP, D05_LP", "EF03LP01, EF04LP05", "KUMON_LEIT_A_B"),
        ("KUMON_LEIT_E_F", "LEITURA_LINGUAGEM", "Nível E a F: Inferência Crítica, Síntese e Intertextualidade", 5, "Análise de argumentos, teses textuais, ironia, pontos de vista e resumos autônomos.", 6, 85.0, "D06_LP a D15_LP", "EF05LP02, EF05LP15", "KUMON_LEIT_C_D")
    ]

    for k in niveis_kumon:
        cur.execute("""
            INSERT OR REPLACE INTO dim_kumon_niveis_granulares (
                codigo_nivel, disciplina_eixo, nome_nivel, ano_escolar_sugerido,
                foco_operacional_micro_passo, tempo_padrao_conclusao_min, meta_maestria_pct,
                descritores_caed_alvo, habilidades_bncc_alvo, prerequisito_nivel
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, k)

    # 3. dim_metodo_fonico_estagios
    cur.execute("""
        CREATE TABLE IF NOT EXISTS dim_metodo_fonico_estagios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_estagio TEXT NOT NULL UNIQUE,
            nome_estagio TEXT NOT NULL,
            fase_ehri_correspondente TEXT NOT NULL,
            processo_neurofuncional TEXT NOT NULL,
            estrategias_instrucionais TEXT NOT NULL,
            criterio_dominio_sucesso TEXT NOT NULL,
            descritores_caed TEXT NOT NULL,
            habilidades_bncc TEXT NOT NULL
        );
    """)

    estagios_fonico = [
        (
            "FON_E1_CONSCIENCIA",
            "Estágio 1: Consciência Fonológica e Fonêmica",
            "Fase Pré-Alfabética",
            "Discriminação auditiva no córtex auditivo primário; separação de rimas, aliterações e segmentação de fonemas.",
            "Jogos de rimas sonoras, contagem de palmas por sílaba, identificação do som inicial (/m/ de mamãe).",
            "Identificação correta de 10 em 10 rimas orais e segmentação de fonemas iniciais.",
            "D01_LP",
            "EF01LP06, EF01LP07"
        ),
        (
            "FON_E2_PRINCIPIO_ALFABETICO",
            "Estágio 2: Princípio Alfabético e Relação Fonema-Grafema",
            "Fase Alfabética Inicial",
            "Pareamento intermodal entre o giro temporal superior e o giro angular (conversão som-letra).",
            "Apresentação explícita de sons de vogais e consoantes contínuas (/v/, /m/, /s/, /f/); escrita tátil e multissensorial.",
            "Precisão de 100% na correspondência grafema-fonema dos 26 caracteres básicos.",
            "D02_LP",
            "EF01LP02, EF01LP03"
        ),
        (
            "FON_E3_DECODIFICACAO_SINTETICA",
            "Estágio 3: Decodificação Sintética e Blending",
            "Fase Alfabética Plena",
            "Ativação do fascículo arqueado e da via dorsal de leitura; fusão fonêmica sequencial.",
            "Síntese fonêmica (/s/ + /o/ + /l/ -> sol), leitura de pseudopalavras para garantir decodificação autêntica sem adivinhação.",
            "Leitura precisa de 30 pseudopalavras e palavras decodificáveis com acurácia >= 90%.",
            "D03_LP",
            "EF01LP08, EF02LP01"
        ),
        (
            "FON_E4_LEITURA_ORTOGRAFICA",
            "Estágio 4: Consolidação Ortográfica e Fluência Automática",
            "Fase Alfabética Consolidada",
            "Ativação plena da Área da Forma Visual das Palavras (VWFA); leitura por via lexical direta com prosódia.",
            "Leitura repetida de textos graduados, modelagem de entonação e pausas de pontuação, cronometragem de PPM (palavras por minuto).",
            "Fluência de leitura >= 80 PPM no 2º ano e >= 110 PPM no 5º ano, com compreensão de 100%.",
            "D04_LP, D05_LP, D15_LP",
            "EF02LP04, EF03LP01, EF05LP02"
        )
    ]

    for f in estagios_fonico:
        cur.execute("""
            INSERT OR REPLACE INTO dim_metodo_fonico_estagios (
                codigo_estagio, nome_estagio, fase_ehri_correspondente, processo_neurofuncional,
                estrategias_instrucionais, criterio_dominio_sucesso, descritores_caed, habilidades_bncc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, f)

    # 4. rel_kumon_fonico_rede_interdisciplinar
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rel_kumon_fonico_rede_interdisciplinar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            origem_tipo TEXT NOT NULL CHECK(origem_tipo IN ('KUMON', 'FONICO')),
            origem_codigo TEXT NOT NULL,
            componente_conectado TEXT NOT NULL, -- 'PORTUGUES', 'MATEMATICA', 'CIENCIAS', 'HISTORIA', 'GEOGRAFIA', 'ARTES'
            habilidade_bncc_conectada TEXT NOT NULL,
            descritor_caed_conectado TEXT NOT NULL,
            mecanismo_interdisciplinar TEXT NOT NULL,
            peso_conexao REAL NOT NULL DEFAULT 1.0,
            hash_conexao TEXT NOT NULL
        );
    """)

    conexoes = [
        # Conexões do Fônico com Ciências, História e Geografia
        ("FONICO", "FON_E3_DECODIFICACAO_SINTETICA", "CIENCIAS", "EF02CI01", "D03_LP", "Decodificação precisa de termos científicos (fotossíntese, habitat, matéria) sem sobrecarga da memória de trabalho.", 1.2),
        ("FONICO", "FON_E4_LEITURA_ORTOGRAFICA", "HISTORIA", "EF03HI01", "D04_LP", "Fluência na leitura autônoma de fontes documentais, certidões e relatos orais transcritos.", 1.1),
        ("FONICO", "FON_E4_LEITURA_ORTOGRAFICA", "GEOGRAFIA", "EF04GE01", "D05_LP", "Interpretação textual de legendas, mapas temáticos e fluxogramas socioeconômicos.", 1.1),
        ("FONICO", "FON_E2_PRINCIPIO_ALFABETICO", "ARTES", "EF15AR04", "D02_LP", "Expressão gráfica caligráfica, tipografia artística e valorização da forma visual das letras.", 0.9),

        # Conexões do Kumon com Ciências, História, Geografia e Artes
        ("KUMON", "KUMON_MAT_2A_A", "CIENCIAS", "EF01CI02", "D03_M", "Registro quantitativo de observações empíricas (contagem de plantas, dias de germinação, temperatura).", 1.2),
        ("KUMON", "KUMON_MAT_C", "GEOGRAFIA", "EF03GE06", "D07_M", "Cálculo de distâncias em escala linear simples, leitura de coordenadas em malhas quadriculadas.", 1.3),
        ("KUMON", "KUMON_MAT_D", "HISTORIA", "EF04HI02", "D09_M", "Contagem de tempo cronológico, séculos, linhas do tempo e conversão de algarismos romanos.", 1.1),
        ("KUMON", "KUMON_MAT_7A_5A", "ARTES", "EF15AR02", "D01_M", "Coordenação motora fina, simetria em desenhos geométricos, proporções áureas intuitivas.", 1.0),
        ("KUMON", "KUMON_MAT_E_F", "CIENCIAS", "EF05CI03", "D11_M", "Cálculo de frações e proporções em experimentos de mistura, densidade e reciclagem de água.", 1.4)
    ]

    for c in conexoes:
        h = gerar_hash(f"{c[0]}_{c[1]}_{c[2]}_{c[3]}")
        cur.execute("""
            INSERT OR REPLACE INTO rel_kumon_fonico_rede_interdisciplinar (
                origem_tipo, origem_codigo, componente_conectado, habilidade_bncc_conectada,
                descritor_caed_conectado, mecanismo_interdisciplinar, peso_conexao, hash_conexao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (c[0], c[1], c[2], c[3], c[4], c[5], c[6], h))

    # 5. fato_trilha_aprendizagem_granular_aluno
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fato_trilha_aprendizagem_granular_aluno (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_hash_id TEXT NOT NULL UNIQUE,
            ano_escolar INTEGER NOT NULL,
            estagio_fonico_atual TEXT NOT NULL,
            nivel_kumon_mat_atual TEXT NOT NULL,
            nivel_kumon_leit_atual TEXT NOT NULL,
            indice_autodidatismo_pct REAL NOT NULL,
            taxa_maestria_granular_pct REAL NOT NULL,
            tempo_medio_folha_min REAL NOT NULL,
            status_evolucao_kumon TEXT NOT NULL,
            estrategia_interdisciplinar_ativa TEXT NOT NULL,
            hash_validacao_forense TEXT NOT NULL,
            data_homologacao TEXT NOT NULL,
            FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id)
        );
    """)

    # Alocar trilha para os 172 alunos com base no desempenho real
    cur.execute("""
        SELECT 
            r.aluno_hash_id,
            e.ano_escolar,
            r.indice_global_eficiencia_cognitiva,
            r.score_senso_numerico_calculo,
            r.score_consciencia_fonologica_decod,
            e.possui_laudo_aee
        FROM fato_raiox_cognitivo_estudante r
        JOIN dim_estudantes e ON r.aluno_hash_id = e.aluno_hash_id
    """)
    alunos = cur.fetchall()

    for a in alunos:
        aluno_hash, ano, igec, num, fon, laudo = a

        # Enquadramento Fônico
        if fon >= 90.0:
            estagio_fon = "FON_E4_LEITURA_ORTOGRAFICA"
        elif fon >= 75.0:
            estagio_fon = "FON_E3_DECODIFICACAO_SINTETICA"
        elif fon >= 50.0:
            estagio_fon = "FON_E2_PRINCIPIO_ALFABETICO"
        else:
            estagio_fon = "FON_E1_CONSCIENCIA"

        # Enquadramento Kumon Matemática
        if num >= 95.0 and ano >= 4:
            nivel_k_mat = "KUMON_MAT_E_F"
            status_k = "Aceleração Autodidata"
        elif num >= 85.0 and ano >= 3:
            nivel_k_mat = "KUMON_MAT_D"
            status_k = "Avanço Granular Superior"
        elif num >= 70.0:
            nivel_k_mat = "KUMON_MAT_C" if ano >= 3 else "KUMON_MAT_B"
            status_k = "Ritmo Padrão Consolidado"
        elif num >= 50.0:
            nivel_k_mat = "KUMON_MAT_2A_A"
            status_k = "Reforço Granular em Micro-passos"
        else:
            nivel_k_mat = "KUMON_MAT_4A_3A"
            status_k = "Nivelamento Intensivo Fundamental"

        # Enquadramento Kumon Leitura
        if fon >= 85.0 and ano >= 3:
            nivel_k_leit = "KUMON_LEIT_E_F"
        elif fon >= 70.0:
            nivel_k_leit = "KUMON_LEIT_C_D"
        elif fon >= 50.0:
            nivel_k_leit = "KUMON_LEIT_A_B"
        else:
            nivel_k_leit = "KUMON_LEIT_3A_2A"

        # Autodidatismo estimado proporcional ao IGEC
        autodidatismo = round(min(100.0, max(20.0, igec * 0.95 + 5.0)), 1)
        maestria = round(min(100.0, max(30.0, (num + fon) / 2.0)), 1)
        tempo_folha = round(max(1.5, 8.0 - (igec / 20.0)), 1)

        interdisciplinar = "Conexão Fônico-Ciências e Kumon-Geografia com Prática Deliberada Espaçada."

        h_trilha = gerar_hash(f"{aluno_hash}_{estagio_fon}_{nivel_k_mat}_{timestamp}")

        cur.execute("""
            INSERT OR REPLACE INTO fato_trilha_aprendizagem_granular_aluno (
                aluno_hash_id, ano_escolar, estagio_fonico_atual, nivel_kumon_mat_atual,
                nivel_kumon_leit_atual, indice_autodidatismo_pct, taxa_maestria_granular_pct,
                tempo_medio_folha_min, status_evolucao_kumon, estrategia_interdisciplinar_ativa,
                hash_validacao_forense, data_homologacao
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            aluno_hash, ano, estagio_fon, nivel_k_mat, nivel_k_leit, autodidatismo,
            maestria, tempo_folha, status_k, interdisciplinar, h_trilha, timestamp
        ))

    conn.commit()
    conn.close()

    print(f"[+] Ingestão concluída com sucesso:")
    print(f"    - {len(metodologias)} metodologias canônicas cadastradas.")
    print(f"    - {len(niveis_kumon)} níveis granulares de Kumon mapeados.")
    print(f"    - {len(estagios_fonico)} estágios fônicos de Ehri/Dehaene cadastrados.")
    print(f"    - {len(conexoes)} arestas de rede interdisciplinar estabelecidas.")
    print(f"    - {len(alunos)} trilhas de aprendizagem granular homologadas para os 172 estudantes.")

if __name__ == "__main__":
    executar_ingestao()
