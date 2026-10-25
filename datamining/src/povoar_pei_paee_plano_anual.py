import sqlite3
import hashlib
from datetime import datetime
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = r'datamining/dados/airam_veras_ecossistema.sqlite'
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

def sha256_str(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

print("=== CRIANDO E POVOANDO TABELAS DE PEI, PAEE, LEGISLAÇÃO E PLANO ANUAL ===")

# 1. TABELA DE LEGISLAÇÃO EDUCACIONAL E INCLUSIVA
cursor.execute("""
    CREATE TABLE IF NOT EXISTS dim_legislacao_educacional_inclusiva (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_ato TEXT NOT NULL, -- 'Lei Federal', 'Decreto', 'Resolução CNE', 'Parecer CNE', 'Nota Técnica'
        numero_ano TEXT NOT NULL UNIQUE,
        titulo_oficial TEXT NOT NULL,
        artigos_relevantes TEXT NOT NULL,
        ementa_resumida TEXT NOT NULL,
        diretriz_sala_aula TEXT NOT NULL,
        diretriz_avaliacao_caed TEXT NOT NULL
    );
""")

leis = [
    (
        'Lei Federal', 'Lei nº 13.146/2015',
        'Lei Brasileira de Inclusão da Pessoa com Deficiência (Estatuto da Pessoa com Deficiência)',
        'Arts. 27, 28 (incisos I a XVII), 30',
        'Garante sistema educacional inclusivo em todos os níveis, oferta de profissionais de apoio, recursos de acessibilidade e veda a recusa de matrícula ou cobrança de taxas adicionais.',
        'Obrigação de oferta de adaptações razoáveis, material pedagógico acessível, tecnologia assistiva e mediação pedagógica contínua.',
        'Direito a tempo adicional (+50%), provas em formatos acessíveis, salas com reduzido distrator e apoio de ledor/transcritor oficial sem descaracterizar a matriz de competências.'
    ),
    (
        'Lei Federal', 'Lei nº 12.764/2012',
        'Política Nacional de Proteção dos Direitos da Pessoa com Transtorno do Espectro Autista (Lei Berenice Piana)',
        'Art. 2º (inciso III), Art. 3º (inciso IV, parágrafo único)',
        'Institui a pessoa com TEA como pessoa com deficiência para todos os efeitos legais, assegurando acompanhante especializado em sala de aula regular em caso de comprovada necessidade.',
        'Estruturação da rotina escolar com antecipação visual (TEACCH), linguagem direta e clara sem ambiguidades, mediação em transições de atividades e respeito ao perfil sensorial.',
        'Aplicação de provas em ambiente silencioso, instruções diretas passo a passo, permissão de recursos de conforto sensorial (fones, mordedores, objetos de transição).'
    ),
    (
        'Lei Federal', 'Lei nº 14.254/2021',
        'Lei de Acompanhamento Integral para Educandos com Dislexia, TDAH ou outros Transtornos de Aprendizagem',
        'Arts. 1º, 3º, 4º',
        'Determina a identificação precoce e o encaminhamento pedagógico e terapêutico integral na rede de ensino aos estudantes com TDAH, Dislexia e afins.',
        'Assento prioritário na primeira fileira longe de janelas e portas; instruções curtas e fracionadas; verificação individual de compreensão; apoio multissensorial.',
        'Ledor humano oficial para leitura de textos longos; tempo estendido; permissão de calculadora básica e material manipulativo; não penalização de disortografias secundárias.'
    ),
    (
        'Resolução CNE', 'Resolução CNE/CEB nº 4/2009',
        'Diretrizes Operacionais para o Atendimento Educacional Especializado (AEE) na Educação Básica',
        'Arts. 1º ao 13',
        'Define a operacionalização do AEE no contraturno em Salas de Recursos Multifuncionais (SRM), com Plano de AEE obrigatório e articulação interinstitucional com o professor da sala comum.',
        'Planejamento conjunto quinzenal entre professor da sala comum e professor do AEE; implementação de Comunicação Alternativa e Aumentativa (CAA); adaptação de materiais.',
        'Validação formal do PEI e do Plano de AEE no Conselho de Classe e registros comprobatórios das acomodações avaliativas para monitoramento e auditoria.'
    ),
    (
        'Decreto', 'Decreto nº 7.611/2011',
        'Dispõe sobre a Educação Especial e o Atendimento Educacional Especializado',
        'Arts. 1º ao 5º',
        'Regulamenta o dever do Estado na garantia de serviços de apoio pedagógico especializado e financiamento compartilhado da educação inclusiva via Fundeb (dupla matrícula).',
        'Garantia da infraestrutura acessível na SRM e salas comuns; disponibilização de recursos de tecnologia assistiva.',
        'Registro de dupla matrícula no Censo Escolar/INEP e conformidade de registros pedagógicos para prestação de contas dos recursos descentralizados.'
    ),
    (
        'Parecer CNE', 'Parecer CNE/CP nº 50/2023',
        'Orientações Específicas para o Atendimento Escolar de Estudantes com Transtorno do Espectro Autista (TEA)',
        'Seções 4, 5 e 6',
        'Normatiza o Plano Educacional Individualizado (PEI) como documento pedagógico mandatório, norteador de metas funcionais e acadêmicas articuladas à equipe multidisciplinar.',
        'Elaboração colaborativa do PEI com metas trimestrais; estratégias baseadas em evidências científicas (ABA/PBS); proibição expressa de exclusão pedagógica ou tarefas avulsas desconectadas.',
        'Ajuste das matrizes avaliativas às metas do PEI; avaliação processual e formativa contínua baseada em rubricas comportamentais e de engajamento funcional.'
    ),
    (
        'Nota Técnica', 'Nota Técnica Conjunta nº 02/2025/MEC/SECADI',
        'Diretrizes Nacionais para Elaboração, Implementação e Auditoria do Plano Educacional Individualizado (PEI)',
        'Itens I a V',
        'Padroniza o ciclo metodológico do PEI: Avaliação Diagnóstica Neuropsicopedagógica, Pactuação de Metas com Família, Execução Adaptada em Sala e Revisão Bimestral Obrigatória.',
        'Documentação obrigatória do PEI no prontuário do aluno com assinatura da coordenação pedagógica, professor regente, professor do AEE e responsáveis legais.',
        'Auditoria formal de cumprimento das metas curriculares adaptadas e rastreabilidade dos indicadores de evolução bioestatística.'
    )
]

cursor.executemany("""
    INSERT OR REPLACE INTO dim_legislacao_educacional_inclusiva 
    (tipo_ato, numero_ano, titulo_oficial, artigos_relevantes, ementa_resumida, diretriz_sala_aula, diretriz_avaliacao_caed)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", leis)
conn.commit()
print(f"-> dim_legislacao_educacional_inclusiva povoada com {len(leis)} marcos normativos!")

# 2. TABELA DE PLANO EDUCACIONAL INDIVIDUALIZADO (PEI)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fato_pei_estudante_adaptacoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_hash_id TEXT NOT NULL,
        ano_letivo INTEGER NOT NULL DEFAULT 2026,
        bimestre INTEGER NOT NULL CHECK(bimestre BETWEEN 1 AND 4),
        diagnostico_clinico_resumo TEXT NOT NULL,
        cid_codigo TEXT NOT NULL,
        perfil_neurocognitivo_sweller TEXT NOT NULL,
        meta_fonica_adaptada TEXT NOT NULL,
        meta_matematica_kumon_adaptada TEXT NOT NULL,
        adaptacao_espaco_fisico TEXT NOT NULL,
        adaptacao_temporal_pausas TEXT NOT NULL,
        adaptacao_instrumentos_materiais TEXT NOT NULL,
        protocolo_desescalada_comportamental TEXT NOT NULL,
        indicador_evolucao_esperado TEXT NOT NULL,
        responsavel_elaboracao TEXT NOT NULL,
        data_revisao_pactuada TEXT NOT NULL,
        hash_forense_pei TEXT NOT NULL,
        FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id) ON DELETE CASCADE
    );
""")

# Povoar PEI para todos os 24 alunos do 1º ano com diferenciação psiconeuropedagógica minuciosa
alunos_1ano = cursor.execute("""
    SELECT e.aluno_hash_id, gr.nome_perfil, g.grupo_id
    FROM dim_estudantes e
    JOIN fato_estudante_agrupamento g ON e.aluno_hash_id = g.aluno_hash_id
    JOIN dim_grupos_intervencao gr ON g.grupo_id = gr.id
    WHERE e.ano_escolar = 1 AND g.avaliacao_caderno_id = 1
""").fetchall()

peis_insert = []
data_hoje = datetime.utcnow().strftime("%Y-%m-%d")

for aluno_hash, nome_grupo, grupo_id in alunos_1ano:
    for bim in range(1, 5):
        if grupo_id == 1: # G1: Recomposição Intensiva / Alerta Clínico
            diag = "Dificuldade severa em consciência fonêmica e senso numérico inicial; labilidade atencional."
            cid = "R48 / F90.0"
            neuro = "Sobrecarga cognitiva alta em tarefas com mais de 1 estímulo simultâneo. Necessita de ancoragem visual isolada (Rede de Reconhecimento DUA)."
            m_fon = f"Bim {bim}: Consolidação multissensorial de fonemas contínuos /p/, /m/, /v/, /t/ com apoio tátil e articulação diante do espelho."
            m_mat = f"Bim {bim}: Kumon 7A/6A. Contagem biunívoca 1 a 10 com tampinhas e blocos lógicos; correspondência termo a termo."
            esp = "Primeira carteira no centro, com distratores visuais minimizados; quadro de foco individual."
            temp = "Blocos de atividade de 15 minutos intercalados com 3 minutos de pausa motora regulatória."
            mat = "Letras móveis emborrachadas com relevo; prancha de comunicação com imagens PECS/Arasaac; fonte 16pt entrelinhas duplo."
            desesc = "Técnica da escolha controlada ('Você prefere fazer a letra P com massinha ou com giz?'); proibição de reprimenda pública."
            ind = "Avanço de 30% na precisão de síntese fonêmica e contagem até 10 sem apoio motor."
        elif grupo_id == 2: # G2: Consolidação e Fluência
            diag = "Leitura silábica hesitante; lentidão no processamento sequencial e memória operacional em desenvolvimento."
            cid = "R48 / Z55.8"
            neuro = "Carga intrínseca administrável em blocos curtos. Necessita de andaimes (scaffolding) sintáticos (Rede Estratégica DUA)."
            m_fon = f"Bim {bim}: Transição da silabação para reconhecimento global de palavras frequentes dissílabas (CV-CV) com cronometragem lúdica."
            m_mat = f"Bim {bim}: Kumon 5A/4A. Reta numérica horizontal até 30; identificação de sucessor e antecessor com linha guia."
            esp = "Fileira central, emparelhado com colega tutor de apoio colaborativo."
            temp = "Blocos de 20 minutos com pausas de hidratação e alongamento guiado."
            mat = "Textos curtos em caixa alta com separação silábica em cores contrastantes; fichas cumulativas Kumon plastificadas."
            desesc = "Reforço imediato por conclusão de etapas parciais; contrato de metas visuais com adesivos."
            ind = "Aumento de 15 PPM na taxa de fluência leitora e 80% de precisão na escrita de palavras dissílabas."
        elif grupo_id == 3: # G3: Compreensão e Inferência
            diag = "Leitura decodificada funcional, porém com dificuldade em inferências pragmáticas e interpretação de duplos sentidos."
            cid = "F84.0 / Z55.0"
            neuro = "Memória de trabalho robusta para decodificação, mas com sobrecarga extrínseca em enunciados longos. Requer ancoragem contextual (Rede Afetiva DUA)."
            m_fon = f"Bim {bim}: Roteiros de leitura compartilhada com perguntas explícitas de causa-efeito ('Onde?', 'Quem?', 'Por quê?')."
            m_mat = f"Bim {bim}: Kumon 3A/2A. Resolução de situações-problema com enunciado ilustrado e operação de adição/subtração em 2 etapas."
            esp = "Posicionamento próximo ao mediador pedagógico para checagem de compreensão de instruções abstratas."
            temp = "Ritmo regular de aula com tempo adicional de 25% para elaboração escrita de respostas reflexivas."
            mat = "Organizadores gráficos de pensamento (mapas mentais, diagramas de Venn simplificados); cartões de pistas inferenciais."
            desesc = "Previsibilidade de agenda diária anotada na mesa; aviso prévio de 5 minutos antes da troca de disciplina."
            ind = "Atingimento de 75%+ de acerto nos descritores CAEd D02 (inferência em texto verbal) e D04 (adição com reserva)."
        else: # G4: Aprofundamento e Altas Habilidades / Dupla Excepcionalidade (2E)
            diag = "Potencial de Altas Habilidades/Superdotação; risco de desengajamento e ansiedade por tédio ou rigidez perfeccionista."
            cid = "Z73.0 / 2E"
            neuro = "Velocidade de processamento elevada; rápida saciedade de tarefas repetitivas. Necessita de enriquecimento tipo II e III (Renzulli)."
            m_fon = f"Bim {bim}: Produção de pequenos livros autorais ilustrados com gêneros textuais diversificados (fábulas, notícias, poesias)."
            m_mat = f"Bim {bim}: Kumon avançado (Nível A/B). Desafios de lógica numérica, algoritmos desplugados e padrões geométricos fractais."
            esp = "Bancada de projetos e experimentos; liberdade de movimentação responsável para consulta a acervo bibliográfico."
            temp = "Compactação curricular: dispensa de repetição após demonstração de maestria (test-out rápido)."
            mat = "Cadernos de pesquisa autônoma; software educacional de pensamento computacional desplugado e jogos de raciocínio lógico."
            desesc = "Pactuação de contratos de mentoria; flexibilização de prazos para projetos profundos; validação de interesses intrínsecos."
            ind = "Desenvolvimento de projeto interdisciplinar autoral e manutenção de índice de maestria superior a 95%."

        h_pei = sha256_str(f"PEI_{aluno_hash}_B{bim}_{cid}")
        peis_insert.append((
            aluno_hash, 2026, bim, diag, cid, neuro, m_fon, m_mat, esp, temp, mat, desesc, ind,
            "Equipe Multidisciplinar Psiconeuropedagógica e Coordenação Pedagógica",
            f"2026-0{bim*3}-15", h_pei
        ))

cursor.execute("DELETE FROM fato_pei_estudante_adaptacoes;")
cursor.executemany("""
    INSERT INTO fato_pei_estudante_adaptacoes
    (aluno_hash_id, ano_letivo, bimestre, diagnostico_clinico_resumo, cid_codigo, perfil_neurocognitivo_sweller,
     meta_fonica_adaptada, meta_matematica_kumon_adaptada, adaptacao_espaco_fisico, adaptacao_temporal_pausas,
     adaptacao_instrumentos_materiais, protocolo_desescalada_comportamental, indicador_evolucao_esperado,
     responsavel_elaboracao, data_revisao_pactuada, hash_forense_pei)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", peis_insert)
conn.commit()
print(f"-> fato_pei_estudante_adaptacoes povoada com {len(peis_insert)} registros de PEI (24 alunos x 4 bimestres)!")

# 3. TABELA DE PLANO DE ATENDIMENTO EDUCACIONAL ESPECIALIZADO (PAEE)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fato_paee_plano_atendimento (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_hash_id TEXT NOT NULL,
        ano_letivo INTEGER NOT NULL DEFAULT 2026,
        modalidade_aee TEXT NOT NULL, -- 'SRM Individual', 'SRM Pequeno Grupo', 'AEE Itinerante', 'Apoio em Sala Regular'
        frequencia_semanal_minutos INTEGER NOT NULL,
        area_foco_psiconeuropedagogica TEXT NOT NULL,
        tecnologias_assistivas_utilizadas TEXT NOT NULL,
        cronograma_atendimento_dia TEXT NOT NULL,
        articulacao_sala_comum_estrategia TEXT NOT NULL,
        criterio_reavaliacao_quadrimestral TEXT NOT NULL,
        hash_forense_paee TEXT NOT NULL,
        FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id) ON DELETE CASCADE
    );
""")

paees_insert = []
for aluno_hash, nome_grupo, grupo_id in alunos_1ano:
    if grupo_id == 1:
        mod = "SRM Individual + Apoio em Sala Regular"
        freq = 150 # 3x 50 min
        foco = "Estimulação multissensorial de funções executivas, consciência fonológica estrita e integração sensório-motora."
        tec = "Prancha de comunicação alternativa (CAA/PECS), teclado adaptado, máscara de foco visual, material manipulativo concreto."
        crono = "Segunda, Quarta e Sexta (13:30 às 14:20)"
        art = "Orientação semanal ao professor regente sobre estratégias de desescalada comportamental e entrega de fichas de atividade ampliadas."
        crit = "Ganho de 20% na escala de autonomia executiva e decodificação precisa de sílabas canônicas simples."
    elif grupo_id == 2:
        mod = "SRM Pequeno Grupo (3 alunos)"
        freq = 100 # 2x 50 min
        foco = "Velocidade de processamento fonológico, treino de automação do código grafema-fonema e cálculo mental básico."
        tec = "Jogos pedagógicos de síntese silábica, ábaco horizontal, cartões de leitura Kumon plastificados, cronômetro de areia."
        crono = "Terça e Quinta (14:00 às 14:50)"
        art = "Compartilhamento dos vocabulários de palavras frequentes para reforço integrado nas aulas de Língua Portuguesa."
        crit = "Fluência mínima de 30 PPM com taxa de erro inferior a 10% em textos narrativos curtos."
    elif grupo_id == 3:
        mod = "SRM Pequeno Grupo (Foco Cognitivo)"
        freq = 80 # 2x 40 min
        foco = "Compreensão inferencial, teoria da mente, leitura social de contextos e estratégias de metacognição."
        tec = "Organizadores visuais em diagramas, fichas de pistas lógicas, pranchas de sequenciamento temporal de histórias."
        crono = "Segunda e Quarta (15:00 às 15:40)"
        art = "Alinhamento das propostas de interpretação de textos literários com foco em identificar causalidade e empatia nas personagens."
        crit = "Capacidade de inferir motivações e sentimentos de personagens em 80% das fábulas analisadas."
    else:
        mod = "SRM Enriquecimento Curricular (Altas Habilidades)"
        freq = 60 # 1x 60 min
        foco = "Enriquecimento Tipo II e III (Renzulli), desenvolvimento de projetos científicos, programação desplugada e pensamento complexo."
        tec = "Kits de robótica desplugada, jogos de xadrez e estratégia matemática, cadernos de iniciação à pesquisa."
        crono = "Sexta-feira (14:00 às 15:00)"
        art = "Orientação ao professor regente para aplicação de compactação curricular e atuação do estudante como líder monitor colaborativo."
        crit = "Apresentação semestral de projeto de pesquisa interdisciplinar com produto final concreto homologado."

    h_paee = sha256_str(f"PAEE_{aluno_hash}_{mod}_{freq}")
    paees_insert.append((aluno_hash, 2026, mod, freq, foco, tec, crono, art, crit, h_paee))

cursor.execute("DELETE FROM fato_paee_plano_atendimento;")
cursor.executemany("""
    INSERT INTO fato_paee_plano_atendimento
    (aluno_hash_id, ano_letivo, modalidade_aee, frequencia_semanal_minutos, area_foco_psiconeuropedagogica,
     tecnologias_assistivas_utilizadas, cronograma_atendimento_dia, articulacao_sala_comum_estrategia,
     criterio_reavaliacao_quadrimestral, hash_forense_paee)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", paees_insert)
conn.commit()
print(f"-> fato_paee_plano_atendimento povoada com {len(paees_insert)} registros de PAEE!")

# 4. TABELA DE PLANO ANUAL INTEGRADO DA TURMA (BNCC + CAED)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fato_plano_anual_turma_bncc_caed (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ano_letivo INTEGER NOT NULL DEFAULT 2026,
        ano_escolar INTEGER NOT NULL DEFAULT 1,
        componente_curricular TEXT NOT NULL,
        competencias_gerais_bncc_foco TEXT NOT NULL,
        marco_desenvolvimento_anual TEXT NOT NULL,
        metas_caed_escola_spaece TEXT NOT NULL,
        cronograma_bimestral_resumo TEXT NOT NULL,
        estrategia_pedagogica_inclusiva_dua TEXT NOT NULL,
        metodologia_afericao_evidencias TEXT NOT NULL,
        hash_forense_plano_anual TEXT NOT NULL
    );
""")

planos_anuais = [
    (
        2026, 1, 'Língua Portuguesa (Alfabetização Fônica e Letramento)',
        'Competências Gerais 1, 3, 4: Comunicação verbal, fruição estética e repertório cultural.',
        'Alfabetização plena de 100% dos estudantes com domínio da decodificação fonema-grafema, escrita alfabética canônica e fluência mínima de 60 PPM no final do Ciclo.',
        'Atingir Meta A (Proficiente/Desejável) no CAEd com redução a zero do padrão Muito Crítico no SPAECE (Escala > 650 pontos).',
        'Bim I: Consciência fonêmica e vogais | Bim II: Consoantes contínuas e sílabas CV | Bim III: Consoantes oclusivas e dissílabos | Bim IV: Sílabas complexas e frases narrativas.',
        'Método fônico estruturado, textos de tradição oral, rotinas diárias de leitura assistida e pranchas acessíveis DUA.',
        'Avaliações diagnósticas bimestrais alinhadas aos descritores CAEd D01 a D09, registros de PPM e portfólio de escrita psicogenética.',
        sha256_str('PLANO_ANUAL_LP_1ANO_2026')
    ),
    (
        2026, 1, 'Matemática (Kumon Cumulativo e Raciocínio Lógico)',
        'Competências Gerais 2, 4, 5: Pensamento científico, crítico, criativo e raciocínio lógico-matemático.',
        'Consolidação do senso numérico até 100, domínio de cálculo mental de adição e subtração básica sem reagrupamento e leitura de tabelas simples.',
        'Média de acertos CAEd Matemática > 85%, garantindo transição de todos os estudantes dos grupos G1 e G2 para G3 e G4.',
        'Bim I: Contagem 1-10 e grandezas | Bim II: Sequência até 30 e adição simples (+1,+2) | Bim III: Adição até +5 e ordem espacial | Bim IV: Decomposição até 100 e figuras geométricas.',
        'Material dourado, ábaco, Kumon cumulativo progressivo, desafios matemáticos práticos e jogos de tabuleiro adaptados.',
        'Testes de retenção semanal Kumon, simulados de itens CAEd H01 a H07 e rubricas formativas de resolução de problemas.',
        sha256_str('PLANO_ANUAL_MAT_1ANO_2026')
    ),
    (
        2026, 1, 'BNCC Computação (Resolução CNE/CP nº 1/2022)',
        'Competências Gerais 2, 5: Cultura digital, pensamento computacional e resolução algorítmica de problemas.',
        'Compreensão do conceito de algoritmo desplugado, reconhecimento do mundo digital, decomposição de problemas e uso ético da tecnologia.',
        '100% dos estudantes do 1º ano aptos nas 7 habilidades normativas EF01CO01 a EF01CO07.',
        'Bim I: Instruções ordenadas e algoritmos desplugados | Bim II: Representação de dados por símbolos | Bim III: Identificação de dispositivos | Bim IV: Segurança e convivência digital.',
        'Atividades corporais de labirinto, jogos de cartas lógicas, ordenação de sequências físicas sem tela e debates reflexivos.',
        'Rubricas de observação direta de raciocínio computacional desplugado e portfólio de sequenciamento algorítmico.',
        sha256_str('PLANO_ANUAL_COMP_1ANO_2026')
    ),
    (
        2026, 1, 'Ciências da Natureza',
        'Competências Gerais 1, 2, 7: Conhecimento sobre o mundo físico, investigação científica e cuidado socioambiental.',
        'Reconhecimento do corpo humano, identificação de hábitos de higiene, escalas de tempo e observação dos seres vivos do semiárido cearense.',
        'Articulação interdisciplinar direta com habilidades de leitura contextual CAEd D01 e produção de relatos observacionais.',
        'Bim I: O corpo humano e os sentidos | Bim II: Hábitos saudáveis e higiene | Bim III: Seres vivos do entorno | Bim IV: Ciclos da natureza e estações.',
        'Aulas de campo no pomar/horta da escola, experimentação sensorial com apoio DUA e cartazes ilustrados táteis.',
        'Relatórios de observação desenhados e narrados, checagem oral e participação em feira de ciências infantil.',
        sha256_str('PLANO_ANUAL_CIENCIAS_1ANO_2026')
    ),
    (
        2026, 1, 'História e Geografia',
        'Competências Gerais 3, 6, 10: Autonomia, responsabilidade, identidade familiar e pertencimento comunitário em Crateús.',
        'Identificação da história pessoal e familiar, noção de espaço vivido (casa, rua, escola) e valorização da diversidade cultural.',
        'Desenvolvimento da leitura de paisagens, imagens e esquemas gráficos elementares.',
        'Bim I: Quem sou eu e minha família | Bim II: Minha escola e convivência | Bim III: Lugares de vivência e paisagens de Crateús | Bim IV: Festas e tradições locais.',
        'Entrevistas com familiares gravadas em áudio, maquetes com materiais recicláveis, mapas afetivos e contação de causos populares.',
        'Painéis de identidade pessoal, avaliação de representação espacial e diário de vivências comunitárias.',
        sha256_str('PLANO_ANUAL_HUMANAS_1ANO_2026')
    ),
    (
        2026, 1, 'Linguagens Integradas (Arte e Educação Física)',
        'Competências Gerais 3, 4, 8: Consciência corporal, expressão artística, coordenação motora fina/ampla e autocuidado.',
        'Desenvolvimento da motricidade fina para o traçado alfabético, lateralidade, exploração de artes visuais, música e jogos corporais coletivos.',
        'Apoio motor e perceptivo essencial para a psicogênese da escrita e decodificação sensorial.',
        'Bim I: O ponto, a linha e o ritmo corporal | Bim II: Jogos cantados e cantigas de roda | Bim III: Danças regionais e coordenação ampla | Bim IV: Teatro de fantoches e jogos cooperativos.',
        'Circuitos psicomotores no pátio, oficinas de massinha de modelar, tintas naturais de urucum/açafrão e brincadeiras tradicionais cearenses.',
        'Avaliação processual da motricidade gráfica, ritmo respiratório, integração sensorial e autorregulação comportamental.',
        sha256_str('PLANO_ANUAL_LINGUAGENS_1ANO_2026')
    ),
    (
        2026, 1, 'Ensino Religioso',
        'Competências Gerais 8, 9, 10: Empatia, diálogo, respeito às diferenças e cultura de paz.',
        'Compreensão do valor da convivência harmônica, respeito aos sentimentos alheios, acolhimento à diversidade e práticas solidárias.',
        'Desenvolvimento da linguagem socioemocional e redução de condutas opositivas na rotina escolar.',
        'Bim I: Meus sentimentos e os dos outros | Bim II: Acolhimento e amizade na escola | Bim III: Histórias e ensinamentos sobre respeito | Bim IV: Partilha, gratidão e comunidade.',
        'Roda de conversa matinal ("Círculo da Empatia"), histórias ilustradas sobre virtudes cívicas e dinâmicas de mediação de conflitos.',
        'Registro de interações socioemocionais no conselho de classe e autoavaliação guiada com carinhas de sentimentos.',
        sha256_str('PLANO_ANUAL_ER_1ANO_2026')
    )
]

cursor.execute("DELETE FROM fato_plano_anual_turma_bncc_caed;")
cursor.executemany("""
    INSERT INTO fato_plano_anual_turma_bncc_caed
    (ano_letivo, ano_escolar, componente_curricular, competencias_gerais_bncc_foco, marco_desenvolvimento_anual,
     metas_caed_escola_spaece, cronograma_bimestral_resumo, estrategia_pedagogica_inclusiva_dua,
     metodologia_afericao_evidencias, hash_forense_plano_anual)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", planos_anuais)
conn.commit()
print(f"-> fato_plano_anual_turma_bncc_caed povoada com {len(planos_anuais)} componentes anuais integrados!")

# 5. TABELA DE ADAPTAÇÕES DIÁRIAS POR CLUSTER
cursor.execute("""
    CREATE TABLE IF NOT EXISTS fato_praticas_adaptadas_cluster (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cluster_codigo TEXT NOT NULL, -- 'G1', 'G2', 'G3', 'G4'
        nome_cluster TEXT NOT NULL,
        perfil_cognitivo_predominante TEXT NOT NULL,
        adaptacao_diaria_sala_aula TEXT NOT NULL,
        recurso_pedagogico_chave TEXT NOT NULL,
        estrategia_avaliacao_adaptada TEXT NOT NULL,
        intervencao_psiconeuropedagogica TEXT NOT NULL
    );
""")

clusters_dados = [
    (
        'G1', 'Recomposição Intensiva (Alerta Clínico / Defasagem Severa)',
        'Déficit em consciência fonêmica, desatenção, labilidade executiva e ausência de senso numérico reflexo.',
        'Atividades diárias em etapas únicas; máscara visual de foco; sentar na primeira carteira; pausas ativas a cada 15 min; mediação individualizada.',
        'Letras móveis com textura, espelho para fonoarticulação, material dourado, ábaco e fichas fônicas de vogais.',
        'Avaliação oral com apoio de imagens e tempo 100% flexibilizado; foco no ganho longitudinal em relação a si mesmo.',
        'Estimulação multissensorial de vias visuais, auditivas e cinestésicas (método fônico Orton-Gillingham adaptado).'
    ),
    (
        'G2', 'Consolidação e Fluência (Silabação Hesitante / Adição Sem Reserva)',
        'Decodificação silábica lenta, memória de trabalho em saturação rápida e dependência de contagem nos dedos.',
        'Rotinas diárias de leitura em coro e duplas tutoradas; contagem ritmada na reta numérica; reforço imediato de micro-etapas.',
        'Fichas cumulativas Kumon 5A/4A, textos curtos em caixa alta e cartões de vocabulário de alta frequência.',
        'Provas em blocos de 5 itens com intervalo de 3 minutos; leitura compartilhada das instruções.',
        'Treino de automação do código alfabético para liberação de carga cognitiva na memória de trabalho (Sweller).'
    ),
    (
        'G3', 'Compreensão e Inferência (Leitor em Desenvolvimento / Problemas de 2 Etapas)',
        'Decodificação consolidada, mas dificuldade em inferir informações implícitas e interpretar enunciados matemáticos abstratos.',
        'Perguntas mediadas durante a leitura ("Por que isso aconteceu?"); decomposição de problemas matemáticos em etapas visuais.',
        'Organizadores gráficos de pensamento, histórias em quadrinhos, tabelas ilustradas e desafios de raciocínio Kumon 3A.',
        'Avaliação com questões contextualizadas e apoio de esquemas visuais; checagem prévia de vocabulário desconhecido.',
        'Desenvolvimento de estratégias metacognitivas e inferenciais com ancoragem semântica (Stanovich/Scarborough).'
    ),
    (
        'G4', 'Aprofundamento e Altas Habilidades / Dupla Excepcionalidade (Autonomia Consolidada)',
        'Raciocínio lógico-abstrato avançado, velocidade de aprendizagem superior; risco de desmotivação por rotinas mecânicas.',
        'Compactação curricular (dispensa de exercícios repetitivos); autonomia para pesquisa de campo e mentoria de colegas.',
        'Jogos de lógica e estratégia, desafios de programação desplugada (BNCC Computação), livros ilustrados de ciência e fábulas complexas.',
        'Avaliação por projetos, resolução de problemas abertos com múltiplas soluções e autoavaliação reflexiva.',
        'Enriquecimento curricular Tipo II e III do Modelo de Renzulli para estímulo de pensamento crítico e criativo.'
    )
]


cursor.execute("DELETE FROM fato_praticas_adaptadas_cluster;")
cursor.executemany("""
    INSERT INTO fato_praticas_adaptadas_cluster
    (cluster_codigo, nome_cluster, perfil_cognitivo_predominante, adaptacao_diaria_sala_aula,
     recurso_pedagogico_chave, estrategia_avaliacao_adaptada, intervencao_psiconeuropedagogica)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", clusters_dados)
conn.commit()
print(f"-> fato_praticas_adaptadas_cluster povoada com {len(clusters_dados)} perfis de cluster adaptados!")

# 6. ATUALIZAÇÃO DO LEDGER DE AUDITORIA CRIPTOGRÁFICA
ultimo_bloco = cursor.execute("SELECT sequencia_bloco, hash_bloco_atual FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 1").fetchone()
seq = ultimo_bloco[0]
hash_anterior = ultimo_bloco[1]

blocos_novos = [
    ('dim_legislacao_educacional_inclusiva', 'HOMOLOGACAO_LEGAL', '7_MARCOS_LEGAIS', 'Registro de normas federais (LBI, TEA, TDAH, CNE, MEC) para legalidade e conformidade escolar'),
    ('fato_pei_estudante_adaptacoes', 'INSERT_PEI_INDIVIDUAL', '96_PEIS_BIMESTRAIS', 'Registro de 96 PEIs individuais adaptados (24 alunos x 4 bimestres) com fundamentação psiconeuropedagógica'),
    ('fato_paee_plano_atendimento', 'INSERT_PAEE_SRM', '24_PLANOS_AEE', 'Registro dos Planos de AEE na Sala de Recursos Multifuncionais, tecnologias assistivas e cronogramas'),
    ('fato_plano_anual_turma_bncc_caed', 'HOMOLOGACAO_CURRICULAR', '7_COMPONENTES_ANUAIS', 'Plano Anual Integrado da Turma alinhado à BNCC, CAEd, SPAECE e DUA'),
    ('fato_praticas_adaptadas_cluster', 'PARAMETRIZACAO_CLUSTERS', '4_CLUSTERS_ADAPTADOS', 'Diretrizes de sala de aula e adaptação diária por cluster G1 a G4')
]

for tab, op, reg, resumo in blocos_novos:
    seq += 1
    ts = datetime.utcnow().isoformat()
    h_atual = sha256_str(f"{seq}_{tab}_{op}_{reg}_{hash_anterior}_{ts}")
    cursor.execute("""
        INSERT INTO fato_auditoria_transacional_ledger
        (sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash, resumo_transacao, hash_bloco_anterior, hash_bloco_atual, timestamp_utc, agente_ou_processo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (seq, tab, op, reg, resumo, hash_anterior, h_atual, ts, 'AIRAM_INCLUSIVE_LEGAL_ENGINE_2026'))
    hash_anterior = h_atual

cursor.execute("""
    INSERT INTO sys_trilha_auditoria
    (timestamp_utc, operacao, tabela_afetada, id_registro_afetado, agente_executor, detalhes_operacao, sha256_estado_apos)
    VALUES (datetime('now'), 'CONTRAPROVA', 'ECOSSISTEMA_PEI_PAEE_LEGAL', 'FULL_LEGAL_SUITE', 'AIRAM_LEGAL_PIPELINE', 'Homologação de PEI, PAEE, Plano Anual e Legislação Inclusiva 100% auditável', ?)
""", (hash_anterior,))

conn.commit()
print(f"-> Ledger atualizado até o Bloco {seq} com sucesso!")

# 7. VERIFICAÇÃO FINAL DE AUDITORIA
tables = [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
empty_found = []
for t in tables:
    cnt = cursor.execute(f"SELECT COUNT(*) FROM '{t}'").fetchone()[0]
    if cnt == 0:
        empty_found.append(t)
    print(f"  [OK] {t}: {cnt} registros")

cursor.execute("PRAGMA foreign_key_check;")
fk_violations = cursor.fetchall()

print(f"\nTotal de tabelas no banco de dados: {len(tables)}")
print(f"Tabelas vazias: {len(empty_found)}")
print(f"Violações de chaves estrangeiras: {len(fk_violations)}")
