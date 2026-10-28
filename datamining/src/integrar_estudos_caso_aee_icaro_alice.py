# -*- coding: utf-8 -*-
"""
Script de Ingestão e Identificação Profunda dos Neurodivergentes, CIDs e PAEE
Atualiza Icaro Soares Leite de Sousa, Alice Coelho dos Santos Gemeo e todos os 59 alunos AEE.
Cria tabela fato_aee_estudo_caso_e_relatorios, atualiza fato_paee_plano_atendimento,
fato_pei_estudante_adaptacoes, fato_praticas_diarias_leitura_fluencia, dim_estudantes
e registra o Bloco 35 no Ledger SHA-256.
"""

import sqlite3
import unicodedata
import re
import hashlib
from datetime import datetime, timezone

DB_PATH = r"c:\Users\marce\Downloads\Airam veras\datamining\dados\airam_veras_ecossistema.sqlite"

def norm(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    text = re.sub(r'[^a-zA-Z0-9]', ' ', text).upper()
    return ' '.join(text.split())

def sha256_str(val):
    return hashlib.sha256(val.encode('utf-8')).hexdigest()

def run_integration():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("--- 1. Criando tabela fato_aee_estudo_caso_e_relatorios ---")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fato_aee_estudo_caso_e_relatorios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        aluno_hash_id TEXT NOT NULL,
        nome_estudante TEXT NOT NULL,
        ano_escolar INTEGER NOT NULL,
        turma_nome TEXT,
        data_nascimento TEXT,
        nome_mae TEXT,
        professor_avaliador_aee TEXT,
        periodo_avaliado TEXT,
        diagnostico_cid10 TEXT,
        diagnostico_cid11 TEXT,
        apresentacao_caso TEXT,
        esclarecimento_problema TEXT,
        natureza_problema TEXT,
        resolucao_problema TEXT,
        potencialidades_estudante TEXT,
        necessidades_apoio TEXT,
        recursos_acessibilidade TEXT,
        materiais_pedagogicos TEXT,
        objetivo_geral TEXT,
        objetivos_especificos TEXT,
        cronograma_atendimento TEXT,
        parcerias_necessarias TEXT,
        avaliacao_plano TEXT,
        fundamentacao_legal TEXT,
        relatorio_inicial_status TEXT,
        hash_forense_estudo TEXT NOT NULL,
        data_registro_utc TEXT NOT NULL,
        FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id)
    );
    """)

    # 2. Mapear todos os alunos das práticas e dim_estudantes
    cur.execute("SELECT aluno_hash_id, nome_estudante, ano_escolar FROM fato_praticas_diarias_leitura_fluencia;")
    prat_rows = cur.fetchall()
    prat_by_norm = {}
    for r in prat_rows:
        prat_by_norm[norm(r[1])] = r

    # 3. Carregar dim_aee_cuidadores_relacao_oficial_2026
    cur.execute("""
        SELECT id, numero_ordem, turma_docx, nome_estudante_docx, ano_escolar,
               apoiador_cuidador, necessidade_cuidador, turno_atendimento, telefones_contato,
               cid_10_codigo, cid_11_codigo, cid_descricao_sintese, status_laudo, em_triagem
        FROM dim_aee_cuidadores_relacao_oficial_2026;
    """)
    aee_rows = cur.fetchall()

    print(f"Total registros na tabela AEE oficial: {len(aee_rows)}")

    # 4. Atualizar cada aluno com seu diagnóstico real, is_paee=1, possui_pei=1
    matched_count = 0
    now_iso = datetime.now(timezone.utc).isoformat()

    for aee in aee_rows:
        n_docx = aee[3]
        ano_docx = aee[4]
        apoiador = aee[5]
        turno = aee[7]
        cid10 = aee[9]
        cid11 = aee[10]
        cid_desc = aee[11]
        status_laudo = aee[12]
        em_triagem = aee[13]

        norm_docx = norm(n_docx)
        match = None
        if norm_docx in prat_by_norm:
            match = prat_by_norm[norm_docx]
        else:
            first_w = norm_docx.split()[0] if norm_docx else ""
            # Match por substring, primeiro nome obrigatoriamente idêntico e ano escolar
            for k, p in prat_by_norm.items():
                p_first_w = k.split()[0] if k else ""
                if first_w == p_first_w and (norm_docx in k or k in norm_docx or (len(set(norm_docx.split()) & set(k.split())) >= 3 and (ano_docx is None or ano_docx == p[2]))):
                    match = p
                    break

        if match:
            matched_count += 1
            hid = match[0]
            nome_real = match[1]
            ano_real = match[2]

            # Definir descrição de laudo e CID refinado
            if em_triagem:
                rotulo_cid = "EM_INVESTIGACAO (Triagem AEE 27/10/2026)"
                estrategia = f"Protocolo Preventivo DUA: Acompanhamento pela equipe AEE ({apoiador}), tempo flexibilizado (+50%) e investigação de barreiras."
            else:
                rotulo_cid = f"{cid10} | CID-11: {cid11} ({cid_desc})"
                estrategia = f"Protocolo DUA/PBS Especializado: Mediação por cuidador ({apoiador}), tempo estendido (+50%), recursos visuais e SRM."

            # Atualizar fato_praticas_diarias_leitura_fluencia
            cur.execute("""
                UPDATE fato_praticas_diarias_leitura_fluencia
                SET is_paee = 1,
                    possui_pei = 1,
                    laudo_cid = ?,
                    estrategia_cluster_paee_pei = ?
                WHERE aluno_hash_id = ?;
            """, (rotulo_cid, estrategia, hid))

            # Atualizar dim_estudantes
            cur.execute("""
                UPDATE dim_estudantes
                SET possui_laudo_aee = 1
                WHERE aluno_hash_id = ?;
            """, (hid,))

            # Atualizar hash no registro AEE correspondente
            cur.execute("""
                UPDATE dim_aee_cuidadores_relacao_oficial_2026
                SET aluno_hash_id = ?
                WHERE id = ?;
            """, (hid, aee[0]))

    print(f"Total de alunos AEE sincronizados com fato_praticas_diarias: {matched_count}")

    # 5. Inserir Estudo de Caso de ICARO SOARES LEITE DE SOUSA
    cur.execute("SELECT aluno_hash_id FROM fato_praticas_diarias_leitura_fluencia WHERE nome_estudante LIKE '%ICARO SOARES%';")
    icaro_row = cur.fetchone()
    if icaro_row:
        icaro_hid = icaro_row[0]
        cur.execute("DELETE FROM fato_aee_estudo_caso_e_relatorios WHERE aluno_hash_id = ?;", (icaro_hid,))
        
        apres_icaro = """Icaro Soares demonstra um excelente desempenho em leitura global, sendo classificado como Leitor Iniciante (60 de 60 palavras lidas). Contudo, sua categoria de escrita é Baixa (nota 3.9), evidenciando uma desproporção entre a capacidade de decodificação e a produção gráfica manual. Ao chegar à escola o aluno apresentou dificuldades de adaptação, chorando e chamando pelos pais e pela Lalá (aluna de outra turma, que reside em sua rua). A princípio, manifestou agressividade com o apoio escolar, com os colegas, professores e consigo mesmo. Apresenta comportamentos específicos tais como: bater com a cabeça na parede, derrubar cadeiras, amassar, rasgar as atividades e colocá-las na boca após executá-las. Quando contrariado, chora e reage com agressividade. Comunica suas necessidades e desejos por meio da fala, tem oralidade bem desenvolvida."""
        
        esclarec_icaro = """O aluno compreende o que lhe é solicitado, presta atenção nas explicações dos professores. A escola conta com apoio escolar que precisa intervir para que o aluno não se machuque. Conta com atendimento na Sala de Recursos Multifuncionais (SRM) no AEE. Após acompanhamento realizado pela Psicóloga, as crises de agressividade em sala de aula e em outros ambientes foram superadas. Atualmente executa as atividades propostas e interage com os colegas, mas ainda não participou das apresentações, projetos e eventos da escola. Manifestou carinho com colegas, professores e afetividade com o apoio escolar (Gabriela Alves Costa). Família foi chamada no início devido ao choro pelos pais."""
        
        natureza_icaro = """Neurobiológica, afetando a coordenação motora, o planejamento executivo para a escrita e a integração sensorial. Natureza comportamental e emocional associada: dificuldade de adaptação, resistência em obedecer regras (compreende o não, mas não aceita), recusa em realizar atividades que não são de seu interesse, principalmente as que envolvem escrita com lápis."""
        
        resolucao_icaro = """Aproveitar a forte habilidade de observação e o perfil leitor para mediar a transição da letra de imprensa para a cursiva. Utilizar o reconhecimento visual de figuras geométricas em diferentes disposições para fortalecer a percepção espacial, aplicando esse ganho à organização do caderno. Acompanhamento psicológico que superou as crises de agressividade. Oferecimento de atividades de seu interesse (encaixe, pareamento, recorte e colagem, leitura sobre animais, números, músicas com gravuras) para criar vínculo. Apoio escolar com mediação constante e AEE trabalhando leitura com autonomia. Estratégia de partir do que ele gosta para depois inserir a escrita com suporte reduzido."""
        
        potenc_icaro = """Inteligente, consegue entender regras e explicações; já consegue ler palavras, frases e textos com autonomia (60/60 palavras lidas); escreve letras, sílabas iniciais e palavras com sílabas simples e complexas; boa coordenação motora fina e grossa; oralidade bem desenvolvida e interage bem; realiza pintura, recorte e colagem com pareamento de desenhos e palavras; identifica cores, formas, números, letras e tem noção de espaçamento; gosta de desenhar e brinquedos em miniaturas; tem predileção por leitura de textos com animais e atividades com números; aprecia atividades com músicas e gravuras, canta trechos de músicas; consegue sentar para lanchar e realizar atividades de seu interesse; sabe a funcionalidade dos materiais didáticos."""
        
        necess_icaro = """Minimizar comportamentos agressivos e autoagressivos (bater cabeça, derrubar cadeiras); desenvolver interesse e tolerância por atividades que envolvam escrita com lápis; trabalhar aceitação do 'não' e de regras; evitar amassar, rasgar e colocar atividades na boca; estimular participação em apresentações, projetos e eventos da escola; apoio emocional para adaptação escolar; continuar apoio para autorregulação quando contrariado."""
        
        recursos_icaro = """Atividades de encaixe, pareamento, jogos, recorte e colagem; textos com tema de animais e atividades com números; músicas com gravuras, brinquedos em miniaturas; reforço positivo e rotina visual com combinados; quadro de regras claras e antecipação de transições; cantinho da calma para autorregulação quando contrariado; atividades no computador ou lousa mágica como ponte para a escrita; na SRM/AEE: leitura com autonomia e escrita com suporte reduzido; apoio escolar (Gabriela Alves Costa) para mediação e prevenção de sobrecarga em escrita."""
        
        materiais_icaro = """Cadernos com pauta ampliada ou colorida (para demarcação de espaço); jogos de tangram; fichas de figuras geométricas em perspectivas variadas; guias de letra cursiva; linhas de orientação e espaçadores físicos (dedo ou palito para distanciamento entre palavras); caderno de caligrafia com modelos ampliados; lápis triangular ou com adaptador de preensão; borracha, apontador e lápis de diferentes espessuras; guias ou réguas de leitura e escrita."""
        
        obj_geral_icaro = """Consolidar a transição para a escrita cursiva e aprimorar a organização espacial, elevando o nível de escrita para 'Médio' ou 'Alto'."""
        
        obj_espec_icaro = """Ciclo II (Língua Portuguesa): Priorizar a legibilidade e a organização espacial no caderno, realizando a transição para a letra cursiva conforme a Unidade 1. Ciclo II (Matemática): Reconhecer, comparar e nomear figuras geométricas planas (círculo, quadrado, retângulo e triângulo) em desenhos apresentados em diferentes disposições ou tamanhos (EF02MA15 / 2EF12_M). Desenvolvimento Motor: Realizar atividades de caligrafia funcional integradas ao vocabulário que ele já domina como leitor."""
        
        crono_icaro = """Quinta-feira (Manhã) - Frequência: 1 vez na semana - Tempo: 08:00h às 08:30h (30 min) - Composição: Individual."""
        
        parcerias_icaro = """Família (pais e aluna Lalá como referência afetiva); Apoio escolar (Gabriela Alves Costa); Professores regentes do 2º Ano; Professora do AEE Luiza Bonfim Teixeira Lira; Psicóloga clínica/escolar; Equipe pedagógica e direção."""
        
        aval_icaro = """A avaliação será centrada na melhora da organização estética e espacial do caderno e na fluidez da escrita cursiva. O progresso será monitorado através da evolução da nota de escrita na Matriz de Referência 2026, visando superar a categoria Baixa atual (nota 3.9) e consolidar sua autonomia como escritor iniciante."""
        
        legal_icaro = """Constituição Federal de 1988 (Arts. 205, 206 e 208); LDB nº 9.394/96; Política Nacional de Educação Especial (2008); Decreto nº 7.611/2011; Lei Federal nº 13.146/2015 (LBI); Lei Federal nº 12.764/2012 (Lei Berenice Piana); Lei Federal nº 14.254/2021; ECA Lei nº 8.069/90; Resolução CNE/CEB nº 04/2009."""

        hash_estudo_icaro = sha256_str(f"ICARO_SOARES_{now_iso}")

        cur.execute("""
            INSERT INTO fato_aee_estudo_caso_e_relatorios (
                aluno_hash_id, nome_estudante, ano_escolar, turma_nome, data_nascimento,
                nome_mae, professor_avaliador_aee, periodo_avaliado, diagnostico_cid10,
                diagnostico_cid11, apresentacao_caso, esclarecimento_problema, natureza_problema,
                resolucao_problema, potencialidades_estudante, necessidades_apoio,
                recursos_acessibilidade, materiais_pedagogicos, objetivo_geral, objetivos_especificos,
                cronograma_atendimento, parcerias_necessarias, avaliacao_plano, fundamentacao_legal,
                relatorio_inicial_status, hash_forense_estudo, data_registro_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            icaro_hid, 'ICARO SOARES LEITE DE SOUSA', 2, '2º Ano Único (Tempo Integral 35H)',
            '02/03/2019', 'Família / Responsáveis Informados', 'LUIZA BONFIM TEIXEIRA LIRA',
            '03/08/2026 (Primeiro e Segundo Bimestres)', 'CID-10: F84.0 + F90', 'CID-11: 6A05.0',
            apres_icaro, esclarec_icaro, natureza_icaro, resolucao_icaro, potenc_icaro,
            necess_icaro, recursos_icaro, materiais_icaro, obj_geral_icaro, obj_espec_icaro,
            crono_icaro, parcerias_icaro, aval_icaro, legal_icaro, 'Estudo de Caso Completo Homologado',
            hash_estudo_icaro, now_iso
        ))

        # Atualizar PAEE de Icaro Soares com precisão milimétrica
        cur.execute("""
            UPDATE fato_paee_plano_atendimento
            SET modalidade_aee = 'Atendimento Individual na Sala de Recursos Multifuncionais (SRM)',
                frequencia_semanal_minutos = 30,
                area_foco_psiconeuropedagogica = 'Coordenação motora fina, escrita cursiva, organização espacial no caderno e figuras geométricas EF02MA15',
                tecnologias_assistivas_utilizadas = 'Pauta ampliada/colorida, tangram, lápis triangular, cantinho da calma, lousa mágica, espaçador físico',
                cronograma_atendimento_dia = 'Quinta-feira (08:00h às 08:30h - Individual) com Profª Luiza Bonfim Teixeira Lira',
                articulacao_sala_comum_estrategia = 'Mediação com cuidadora Gabriela Alves Costa; prevenção de crises de escrita com atividades de animais e números; reforço positivo',
                criterio_reavaliacao_quadrimestral = 'Superação da nota 3.9 de escrita na Matriz 2026 para categoria Média/Alta e consolidação da escrita cursiva'
            WHERE aluno_hash_id = ?;
        """, (icaro_hid,))

        # Atualizar PEI de Icaro Soares nos 4 bimestres
        cur.execute("""
            UPDATE fato_pei_estudante_adaptacoes
            SET diagnostico_clinico_resumo = 'TEA e TDAH (F84.0 + F90 / CID-11 6A05.0) - Desproporção entre Leitura Plena e Escrita Baixa',
                cid_codigo = 'F84.0 + F90 | 6A05.0',
                meta_fonica_adaptada = CASE 
                    WHEN bimestre = 1 THEN 'Transição orientada da letra de imprensa para cursiva com pauta ampliada e vocabulário dominado.'
                    WHEN bimestre = 2 THEN 'Ciclo II LP: Organização espacial no caderno, legibilidade da cursiva e espaçadores físicos entre palavras.'
                    WHEN bimestre = 3 THEN 'Produção de frases completas cursivas sem quebras, superando a nota 3.9 para patamar Médio.'
                    ELSE 'Escrita cursiva autônoma de pequenos textos narrativos com animais, atingindo nível Alto de escrita.'
                END,
                meta_matematica_kumon_adaptada = CASE 
                    WHEN bimestre = 1 THEN 'Reconhecimento visual e pareamento de figuras geométricas planas e números (Kumon 5A/4A).'
                    WHEN bimestre = 2 THEN 'Habilidade EF02MA15: Reconhecer, comparar e nomear figuras planas (círculo, quadrado, retângulo, triângulo) em diferentes posições.'
                    WHEN bimestre = 3 THEN 'Composição e decomposição espacial com Tangram e adição com figuras geométricas.'
                    ELSE 'Resolução de situações-problema com contagem concreta e geometria espacial consolidada.'
                END,
                adaptacao_espaco_fisico = 'Primeira fileira ao lado da cuidadora Gabriela Alves Costa; acesso ao cantinho da calma para autorregulação.',
                adaptacao_temporal_pausas = 'Tempo estendido (+50%); pausas ativas a cada 15 min; intercalar escrita com encaixe e leitura.',
                adaptacao_instrumentos_materiais = 'Caderno pauta ampliada colorida, tangram, lápis triangular ergonômico, réguas de alinhamento, lousa mágica.',
                protocolo_desescalada_comportamental = 'Prevenção de frustração com escolha controlada; evitar confronto verbal; acolhimento no cantinho da calma sem punição.',
                indicador_evolucao_esperado = 'Elevação da nota de escrita (de 3.9 para >= 6.0) e participação sem crises comportamentais.'
            WHERE aluno_hash_id = ?;
        """, (icaro_hid,))
        print("-> Estudo de caso, PAEE e PEI de ICARO SOARES LEITE DE SOUSA atualizados com sucesso!")

    # 6. Inserir Relatório Descritivo de ALICE COELHO DOS SANTOS GEMEO
    cur.execute("SELECT aluno_hash_id FROM fato_praticas_diarias_leitura_fluencia WHERE nome_estudante LIKE '%ALICE COELHO%';")
    alice_row = cur.fetchone()
    if alice_row:
        alice_hid = alice_row[0]
        cur.execute("DELETE FROM fato_aee_estudo_caso_e_relatorios WHERE aluno_hash_id = ?;", (alice_hid,))

        apres_alice = """Estudante matriculada no Ensino Especial / AEE - A - Manhã da Escola Airam Veras, avaliada pela professora Luiza Bonfim Teixeira Lira. Apresenta diagnóstico clínico de Deficiência Física associada a Epilepsia e Transtorno do Espectro Autista (CIDs G40 + F84 / CID-11 8A60 + 6A02)."""
        
        esclarec_alice = """A aluna conta com acompanhamento da cuidadora escolar dedicada Francisca Manuela Nascimento da Silva (manhã e tarde). Funcionalidade inserida no fim do ano, sem relatório inicial disponível no prontuário anterior. Necessita de acessibilidade arquitetônica, suporte na locomoção, adaptação de mobiliário e vigilância constante para prevenção de crises convulsivas em ambiente escolar."""
        
        natureza_alice = """Neuromotora e sensorial: limitação na coordenação motora ampla e fina decorrente da deficiência física, associada a labilidade neurológica por histórico de epilepsia e características do espectro autista."""
        
        resolucao_alice = """Desenvolvimento de plano de adaptação contínua na SRM e sala comum com apoio da cuidadora Francisca Manuela. Utilização de mobiliário com estabilização postural, atividades com materiais táteis adaptados, comunicação clara e tempo estendido oficial (+50%) nas avaliações."""
        
        potenc_alice = """Boa interação social quando acolhida em ambiente previsível e de baixo ruído; receptiva às orientações da professora Luiza Bonfim; interesse por atividades ilustradas e narrativas orais."""
        
        necess_alice = """Apoio para locomoção, uso do banheiro e alimentação; mobiliário escolar adaptado; monitoramento contínuo para suporte em crises convulsivas; plano de emergência articulado com a família (mãe Marina Coelho dos Santos)."""
        
        recursos_alice = """Apoio escolar dedicado integral (Francisca Manuela Nascimento da Silva); carteira com recorte acessível; prancha de comunicação e suporte para preensão; materiais pedagógicos com alto contraste visual e espessura adaptada."""
        
        materiais_alice = """Mobiliário ergonômico acessível; engrossadores de lápis; tesouras adaptadas; pranchas de apoio de leitura; jogos pedagógicos sensoriais."""
        
        obj_geral_alice = """Garantir acessibilidade física integral, participação ativa nas atividades pedagógicas do 3º Ano e promoção da autonomia funcional."""
        
        obj_espec_alice = """Ciclo II/III Língua Portuguesa: Acesso a textos com tipografia ampliada e aceitação de respostas orais ou assistidas. Matemática: Utilização de recursos manipuláveis concretos para fixação de operações básicas. Coordenação: Exercícios funcionais motores guiados pela SRM."""
        
        crono_alice = """Quarta-feira (Manhã) - SRM / AEE - Atendimento especializado com Profª Luiza Bonfim Teixeira Lira."""
        
        parcerias_alice = """Mãe Marina Coelho dos Santos; Cuidadora Francisca Manuela Nascimento da Silva; Professora AEE Luiza Bonfim; Equipe de saúde e neuropediatria; Professores do 3º Ano Único."""
        
        aval_alice = """Avaliação descritiva semestral de adaptação e desenvolvimento neurofuncional na Sala de Recursos Multifuncionais."""
        
        legal_alice = """Constituição Federal de 1988 (Art. 208, III); LBI nº 13.146/2015; Lei nº 14.254/2021; Decreto nº 7.611/2011; Resolução CNE/CEB nº 04/2009."""

        hash_estudo_alice = sha256_str(f"ALICE_COELHO_{now_iso}")

        cur.execute("""
            INSERT INTO fato_aee_estudo_caso_e_relatorios (
                aluno_hash_id, nome_estudante, ano_escolar, turma_nome, data_nascimento,
                nome_mae, professor_avaliador_aee, periodo_avaliado, diagnostico_cid10,
                diagnostico_cid11, apresentacao_caso, esclarecimento_problema, natureza_problema,
                resolucao_problema, potencialidades_estudante, necessidades_apoio,
                recursos_acessibilidade, materiais_pedagogicos, objetivo_geral, objetivos_especificos,
                cronograma_atendimento, parcerias_necessarias, avaliacao_plano, fundamentacao_legal,
                relatorio_inicial_status, hash_forense_estudo, data_registro_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            alice_hid, 'ALICE COELHO DOS SANTOS GEMEO', 3, '3º Ano Único (Tempo Integral 35H)',
            '08/02/2018', 'Marina Coelho Dos Santos', 'LUIZA BONFIM TEIXEIRA LIRA',
            'Final do Ano Letivo 2026', 'Deficiência Física / CID-10: G40 + F84', 'CID-11: 8A60 + 6A02',
            apres_alice, esclarec_alice, natureza_alice, resolucao_alice, potenc_alice,
            necess_alice, recursos_alice, materiais_alice, obj_geral_alice, obj_espec_alice,
            crono_alice, parcerias_alice, aval_alice, legal_alice, 'Funcionalidade inserida no fim do ano, sem relatório inicial disponível.',
            hash_estudo_alice, now_iso
        ))

        # Atualizar PAEE de Alice Coelho
        cur.execute("""
            UPDATE fato_paee_plano_atendimento
            SET modalidade_aee = 'Atendimento em SRM e Apoio de Cuidador em Sala Regular',
                frequencia_semanal_minutos = 50,
                area_foco_psiconeuropedagogica = 'Acessibilidade motora, suporte postural, adaptação de preensão e regulação em epilepsia/TEA',
                tecnologias_assistivas_utilizadas = 'Mobiliário com estabilização, engrossadores de lápis, tesoura adaptada, prancha de comunicação',
                cronograma_atendimento_dia = 'Quarta-feira (Manhã) na SRM com Profª Luiza Bonfim Teixeira Lira',
                articulacao_sala_comum_estrategia = 'Mediação integral por cuidadora Francisca Manuela; adaptação de formato de resposta; prevenção de crises',
                criterio_reavaliacao_quadrimestral = 'Relatório descritivo semestral de autonomia motora e participação nas atividades da turma'
            WHERE aluno_hash_id = ?;
        """, (alice_hid,))

        # Atualizar PEI de Alice Coelho
        cur.execute("""
            UPDATE fato_pei_estudante_adaptacoes
            SET diagnostico_clinico_resumo = 'Deficiência Física com Epilepsia e TEA (G40 + F84 / CID-11 8A60 + 6A02)',
                cid_codigo = 'Deficiência Física | G40 + F84',
                meta_fonica_adaptada = 'Leitura compartilhada com tipografia ampliada, aceitação de resposta oral e mediação motora da escrita.',
                meta_matematica_kumon_adaptada = 'Resolução com suporte de calculadora adaptada e material concreto (blocos e ábaco adaptado).',
                adaptacao_espaco_fisico = 'Mobiliário adaptado perto da porta para evacuação rápida; espaço livre de obstáculos.',
                adaptacao_temporal_pausas = 'Tempo estendido (+50%); repouso imediato em caso de sinais prodrômicos de crise convulsiva.',
                adaptacao_instrumentos_materiais = 'Prancha inclinada de leitura, engrossadores de borracha, livros com pauta demarcada.',
                protocolo_desescalada_comportamental = 'Ambiente acolhedor; acolhimento sensorial em caso de fadiga pós-crítica.',
                indicador_evolucao_esperado = 'Participação ativa nas atividades regulares e ausência de intercorrências graves.'
            WHERE aluno_hash_id = ?;
        """, (alice_hid,))
        print("-> Relatório descritivo, PAEE e PEI de ALICE COELHO DOS SANTOS GEMEO atualizados com sucesso!")

    # 7. Popular fato_aee_estudo_caso_e_relatorios para os demais alunos neurodivergentes
    print("--- 7. Populando estudos de caso padronizados para todos os alunos AEE ---")
    cur.execute("""
        SELECT a.aluno_hash_id, p.nome_estudante, p.ano_escolar, a.cid_10_codigo, a.cid_11_codigo,
               a.cid_descricao_sintese, a.apoiador_cuidador, a.turno_atendimento, a.em_triagem
        FROM dim_aee_cuidadores_relacao_oficial_2026 a
        JOIN fato_praticas_diarias_leitura_fluencia p ON a.aluno_hash_id = p.aluno_hash_id
        WHERE a.aluno_hash_id NOT IN (?, ?);
    """, (icaro_hid if icaro_row else '', alice_hid if alice_row else ''))
    
    outros_aee = cur.fetchall()
    for row in outros_aee:
        o_hid, o_nome, o_ano, o_cid10, o_cid11, o_desc, o_apoiador, o_turno, o_triagem = row
        cur.execute("DELETE FROM fato_aee_estudo_caso_e_relatorios WHERE aluno_hash_id = ?;", (o_hid,))
        
        status_tri = "Em Triagem Ativa de Investigação" if o_triagem else "Laudado Oficial AEE"
        apres = f"Estudante {o_nome}, matriculado no {o_ano}º Ano da Escola Airam Veras. Enquadramento: {status_tri}. Diagnóstico clínico/neurológico: {o_desc} (CID-10: {o_cid10} | CID-11: {o_cid11}). Acompanhado pelo apoio escolar {o_apoiador} no turno {o_turno}."
        esclar = f"Apresenta necessidades de mediação pedagógica individualizada em sala comum e na Sala de Recursos Multifuncionais (SRM). O plano articula suporte comportamental positivo (PBS), Desenho Universal para a Aprendizagem (DUA) e adaptação de materiais."
        natureza = f"Condição neurobiológica associada a {o_desc}, demandando estratégias de flexibilização de tempo (+50%), recursos visuais e redução de sobrecarga cognitiva."
        resol = f"Instrução explícita em micro-passos, reforço positivo contingente (4:1), antecipação de transições com rotina visual e atividades de interesse."
        potenc = "Potencial cognitivo em desenvolvimento com apoio estruturado; capacidade de evolução na fluência e no raciocínio lógico sob mediação."
        necess = f"Suporte continuado do cuidador/apoiador {o_apoiador}; pausas ativas regulares; adequação de avaliações e ambiente com baixo nível de ruído."
        recursos = "Tempo adicional (+50%); ledores quando necessário; cadernos adaptados; reforço positivo; rotina estruturada TEACCH."
        materiais = "Fichas fônicas visuais, material concreto Kumon (blocos lógicos, ábaco), jogos de pareamento e recursos de tecnologia assistiva."
        obj_geral = f"Garantir a permanência, o avanço curricular e a alfabetização/consolidação das competências da BNCC no {o_ano}º Ano."
        obj_espec = f"Atingir as metas de fluência leitora e de resolução matemática pactuadas no PEI nos 4 bimestres de 2026."
        crono = f"Atendimento semanal na SRM de acordo com grade do contraturno (Profª Luiza Bonfim Teixeira Lira e Equipe AEE)."
        parcerias = f"Família; Apoio Escolar ({o_apoiador}); Professores regentes; Equipe pedagógica e SRM."
        aval = "Avaliação formativa bimestral com registro de metas atingidas no PEI e parecer descritivo semestral."
        legal = "Constituição Federal de 1988; LBI nº 13.146/2015; Lei nº 14.254/2021; Decreto nº 7.611/2011; Resolução CNE/CEB nº 04/2009."
        
        h_estudo = sha256_str(f"ESTUDO_{o_hid}_{now_iso}")
        
        cur.execute("""
            INSERT INTO fato_aee_estudo_caso_e_relatorios (
                aluno_hash_id, nome_estudante, ano_escolar, turma_nome, data_nascimento,
                nome_mae, professor_avaliador_aee, periodo_avaliado, diagnostico_cid10,
                diagnostico_cid11, apresentacao_caso, esclarecimento_problema, natureza_problema,
                resolucao_problema, potencialidades_estudante, necessidades_apoio,
                recursos_acessibilidade, materiais_pedagogicos, objetivo_geral, objetivos_especificos,
                cronograma_atendimento, parcerias_necessarias, avaliacao_plano, fundamentacao_legal,
                relatorio_inicial_status, hash_forense_estudo, data_registro_utc
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            o_hid, o_nome, o_ano, f"{o_ano}º Ano (Tempo Integral 35H)", 'Registrado em Prontuário Escolar',
            'Responsável Legal Cadastrado', 'LUIZA BONFIM TEIXEIRA LIRA / EQUIPE AEE',
            'Ano Letivo 2026 (Ciclos I, II e III)', o_cid10, o_cid11,
            apres, esclar, natureza, resol, potenc, necess, recursos, materiais,
            obj_geral, obj_espec, crono, parcerias, aval, legal, status_tri,
            h_estudo, now_iso
        ))

    print(f"Total de estudos de caso adicionados: {len(outros_aee) + 2}")

    # 8. Atualizar fato_estudante_aee_perfil para todos os alunos AEE laudados e em triagem
    print("--- 8. Atualizando fato_estudante_aee_perfil ---")
    cur.execute("SELECT aluno_hash_id, diagnostico_cid10, apresentacao_caso FROM fato_aee_estudo_caso_e_relatorios;")
    estudos_rows = cur.fetchall()
    
    for er in estudos_rows:
        ehid = er[0]
        ecid = er[1]
        eobs = er[2][:200]
        
        cur.execute("SELECT id FROM fato_estudante_aee_perfil WHERE aluno_hash_id = ?;", (ehid,))
        p_row = cur.fetchone()
        
        # Mapear CID para dim_cid_catalogo
        cid_id = 3 # Default TEA
        if 'F90' in ecid or '6A05' in ecid:
            cid_id = 1 # TDAH
        elif 'F91' in ecid:
            cid_id = 2 # TOD
        elif 'F84' in ecid:
            cid_id = 3 # TEA
        elif 'G40' in ecid:
            cid_id = 6 # Epilepsia
        elif 'G80' in ecid or 'Deficiência' in ecid:
            cid_id = 7 # Paralisia / Fisico
        elif 'Q02' in ecid:
            cid_id = 9 # Microcefalia
        elif 'Q37' in ecid:
            cid_id = 10 # Fenda
        elif 'E10' in ecid:
            cid_id = 11 # Diabetes
        
        req_tod = 1 if ('F91' in ecid or 'TOD' in ecid or 'agressividade' in eobs.lower()) else 0
        
        if p_row:
            cur.execute("""
                UPDATE fato_estudante_aee_perfil
                SET cid_primario_id = ?,
                    pdi_ativo = 1,
                    recurso_tempo_estendido_50pct = 1,
                    recurso_ledor_oficial = 1,
                    recurso_ambiente_baixo_estimulo = 1,
                    recurso_pausas_ativas_fracionadas = 1,
                    recurso_material_concreto = 1,
                    requer_manejo_tod_pbs = ?,
                    observacoes_clinico_pedagogicas = ?
                WHERE aluno_hash_id = ?;
            """, (cid_id, req_tod, eobs, ehid))
        else:
            cur.execute("""
                INSERT INTO fato_estudante_aee_perfil (
                    aluno_hash_id, cid_primario_id, pdi_ativo, recurso_tempo_estendido_50pct,
                    recurso_ledor_oficial, recurso_transcritor_oficial, recurso_ambiente_baixo_estimulo,
                    recurso_pausas_ativas_fracionadas, recurso_tipografia_acessivel,
                    recurso_material_concreto, recurso_prancha_comunicacao_caa, requer_manejo_tod_pbs,
                    observacoes_clinico_pedagogicas
                ) VALUES (?, ?, 1, 1, 1, 0, 1, 1, 1, 1, 0, ?, ?);
            """, (ehid, cid_id, req_tod, eobs))

    # 9. Inserir Bloco 35 no Ledger
    print("--- 9. Registrando Bloco 35 no Ledger SHA-256 ---")
    cur.execute("SELECT id, hash_bloco_atual FROM fato_auditoria_transacional_ledger ORDER BY id DESC LIMIT 1;")
    last_block = cur.fetchone()
    last_seq = last_block[0]
    last_hash = last_block[1]
    
    seq_35 = last_seq + 1
    detalhes_35 = f"BLOCO_35: Ingestao Profunda dos Estudos de Caso e Relatorios AEE (Icaro Soares Leite de Sousa, Alice Coelho dos Santos Gemeo e Coorte AEE 2026). Atualizacao censitaria de CIDs 10 e 11, PAEE, PEI e fato_praticas_diarias_leitura_fluencia. Hash Anterior: {last_hash}"
    hash_35 = sha256_str(f"{seq_35}_{detalhes_35}_{last_hash}")

    cur.execute("""
        INSERT INTO fato_auditoria_transacional_ledger (
            sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash,
            resumo_transacao, hash_bloco_anterior, hash_bloco_atual,
            timestamp_utc, agente_ou_processo
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        seq_35,
        'fato_aee_estudo_caso_e_relatorios',
        'INSERT_ESTUDOS_CASO_E_RELATORIOS_AEE_2026',
        hash_35,
        'Ingestão pericial do Estudo de Caso de Icaro Soares (TEA/TDAH F84.0+F90), Relatório Descritivo de Alice Coelho (Deficiência Física G40+F84) e atualização censitária dos 59 alunos AEE no ecossistema.',
        last_hash,
        hash_35,
        now_iso,
        'Antigravity / Luiza Bonfim Teixeira Lira (AEE Oficial)'
    ))

    conn.commit()
    conn.close()

    print(f"=== Integração Concluída com Sucesso! ===")
    print(f"Bloco {seq_35} no Ledger SHA-256: {hash_35}")

if __name__ == "__main__":
    run_integration()
