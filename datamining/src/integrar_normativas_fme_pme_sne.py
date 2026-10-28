import sqlite3
import hashlib
from datetime import datetime, timezone

def integrar_normativas():
    conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')
    cur = conn.cursor()

    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

    print("=== 1. INSERINDO LEIS DO FÓRUM MUNICIPAL DE EDUCAÇÃO E SNE EM dim_legislacao_educacional_inclusiva ===")
    
    leis_novas = [
        (
            'Constituição Federal',
            'CF/1988 (Art. 206, VI)',
            'Constituição da República Federativa do Brasil de 1988',
            'Art. 206, inciso VI',
            'Princípio Constitucional da Gestão Democrática do Ensino Público, garantindo a participação da comunidade escolar e da sociedade civil na definição e fiscalização dos rumos educacionais.',
            'Criação de colegiados participativos, conselho escolar atuante e planejamento pedagógico construído coletivamente com famílias e docentes.',
            'Publicização transparente dos resultados do CAEd/SPAECE à comunidade e fundamentação democrática dos planos de intervenção.'
        ),
        (
            'Lei Federal',
            'Lei nº 13.005/2014',
            'Plano Nacional de Educação (PNE)',
            'Art. 5º, §§ 1º e 2º; Metas 1, 2, 4, 5, 6, 7 e 19',
            'Aprova o Plano Nacional de Educação e determina a obrigatoriedade do monitoramento contínuo e avaliações periódicas dos Planos Municipais de Educação (PME) com participação social através de Fóruns Permanentes.',
            'Alinhamento do projeto pedagógico da Escola Airam Veras às metas estruturantes do PME de Crateús (Alfabetização na idade certa, tempo integral 35H e inclusão).',
            'Utilização dos microdados censitários como indicador oficial de cumprimento das metas de proficiência e equidade do PME.'
        ),
        (
            'Lei Complementar',
            'Lei Complementar nº 220/2025',
            'Institui o Sistema Nacional de Educação (SNE)',
            'Artigos 16 a 21',
            'Institui o Sistema Nacional de Educação (SNE) para articular o regime de colaboração federativo. Exige a criação obrigatória de Fóruns Municipais de Educação (FME) por ato do Poder Executivo para acompanhamento e deliberação participativa do PME, com natureza não remunerada e de relevante interesse público.',
            'Submissão dos relatórios de eficácia das práticas pedagógicas ao Fórum Municipal de Educação e garantia de coautoria da comunidade no projeto educacional municipal.',
            'Adopção do painel de monitoramento do PNE/Inep, relatórios analíticos territoriais e dados oficiais do SPAECE como lastro probatório indiscutível.'
        )
    ]

    for tipo, num, tit, arts, ementa, dir_sala, dir_caed in leis_novas:
        # Verificar se já existe
        cur.execute("SELECT id FROM dim_legislacao_educacional_inclusiva WHERE numero_ano = ?", (num,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO dim_legislacao_educacional_inclusiva
                (tipo_ato, numero_ano, titulo_oficial, artigos_relevantes, ementa_resumida, diretriz_sala_aula, diretriz_avaliacao_caed)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tipo, num, tit, arts, ementa, dir_sala, dir_caed))
            print(f" -> Inserida: {num} - {tit}")
        else:
            print(f" -> Já existe: {num}")

    print("\n=== 2. CRIANDO TABELA dim_governanca_fme_pme_crateus ===")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS dim_governanca_fme_pme_crateus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        instancia_sigla TEXT NOT NULL UNIQUE,
        instancia_nome TEXT NOT NULL,
        natureza_juridica TEXT NOT NULL,
        funcao_principal TEXT NOT NULL,
        base_legal TEXT NOT NULL,
        instrumentos_dados TEXT NOT NULL,
        composicao_representativa TEXT NOT NULL,
        articulacao_escola_airam_veras TEXT NOT NULL
    );
    """)

    instancias = [
        (
            'FME',
            'Fórum Municipal de Educação de Crateús',
            'Articuladora e Propositiva (Instância Permanente de Participação Social)',
            'Coordenar as Conferências Municipais de Educação, acompanhar e avaliar a execução das metas do Plano Municipal de Educação (PME) e propor medidas para garantir o direito à educação com decisões baseadas em dados.',
            'Constituição Federal (Art. 206, VI), PNE (Lei 13.005/2014, Art. 5º) e Lei Complementar nº 220/2025 (SNE, Arts. 16-21).',
            'Painel de Monitoramento do PNE (Inep), Relatórios Analíticos do Inep, Indicadores Educacionais (Ideb), SPAECE Censitário e Dossiê Mestre Airam Veras.',
            'Instituições e Órgãos do Poder Público (SME, etc.), Profissionais e Gestores da Educação, Movimentos Sociais e Sindicatos, Estudantes e Famílias, Universidades e Pesquisadores.',
            'Espaço de diálogo institucional onde as evidências psicométricas e as necessidades de recursos (AEE, infraestrutura de tempo integral) da Escola Airam Veras são transformadas em políticas de longo prazo.'
        ),
        (
            'CME',
            'Conselho Municipal de Educação de Crateús',
            'Normativa, Consultiva, Deliberativa e Fiscalizadora',
            'Exercer o controle normativo do Sistema Municipal de Ensino, credenciar escolas, autorizar cursos, normatizar o calendário letivo e fiscalizar a conformidade legal.',
            'LDB (Lei 9.394/1996, Art. 11), Leis Municipais de Crateús e Diretrizes do CNE.',
            'Processos de credenciamento, termos de homologação curricular e auditorias pedagógicas.',
            'Conselheiros homologados por decreto municipal representando os poderes públicos e segmentos educacionais.',
            'Validação regulatória da matriz curricular de 9 componentes + BNCC Computacional e homologação dos critérios de terminalidade específica para estudantes PAEE.'
        ),
        (
            'COMISSAO_PME',
            'Comissão Gestora do Plano Municipal de Educação (PME)',
            'Técnica e Focada',
            'Coordenar diretamente o fluxo de elaboração, monitoramento metódico e revisão técnica do texto-base do Plano Municipal de Educação de Crateús.',
            'Ato do Poder Executivo Municipal e Lei do Plano Municipal de Educação de Crateús.',
            'Séries temporais do Inep, microdados censitários CAEd, taxas de fluxo e distorção idade-série.',
            'Equipe técnica multidisciplinar designada pela SME e FME com dedicação metodológica estrita.',
            'Cruzamento das metas de aprendizagem do 1º ao 5º ano da Escola Airam Veras com as metas 1, 2, 4, 5 e 7 do PME de Crateús.'
        ),
        (
            'SME',
            'Secretaria Municipal de Educação de Crateús',
            'Executiva e Administrativa',
            'Planejar, executar, gerir e supervisionar a rede pública municipal de ensino, fornecendo suporte técnico, financeiro e administrativo às instâncias de governança.',
            'Lei Orgânica do Município de Crateús e Estrutura Administrativa Municipal.',
            'Orçamento da Educação, folha de pagamento, censo escolar/INEP e SIGE/SME.',
            'Secretário Municipal de Educação, Coordenadorias Pedagógicas, Gestão de Tempo Integral e Supervisão Escolar.',
            'Provedoria institucional dos recursos materiais, merenda, transporte escolar, lotação de profissionais de AEE/SRM e formação continuada para a equipe docente.'
        )
    ]

    for sigla, nome, nat, func, base, instrum, comp, artic in instancias:
        cur.execute("SELECT id FROM dim_governanca_fme_pme_crateus WHERE instancia_sigla = ?", (sigla,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO dim_governanca_fme_pme_crateus
                (instancia_sigla, instancia_nome, natureza_juridica, funcao_principal, base_legal, instrumentos_dados, composicao_representativa, articulacao_escola_airam_veras)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sigla, nome, nat, func, base, instrum, comp, artic))
            print(f" -> Inserida instância: {sigla} - {nome}")

    print("\n=== 3. CRIANDO TABELA fato_alinhamento_pme_crateus_metas ===")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS fato_alinhamento_pme_crateus_metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        meta_numero INTEGER NOT NULL,
        tema_meta TEXT NOT NULL,
        descricao_meta_municipal TEXT NOT NULL,
        indicador_inep_caed TEXT NOT NULL,
        status_alcance_airam_veras TEXT NOT NULL,
        evidencia_dossie_laudas TEXT NOT NULL,
        diretriz_fme_comissao TEXT NOT NULL
    );
    """)

    metas_pme = [
        (
            2,
            'Ensino Fundamental de 9 Anos',
            'Garantir que 100% dos educandos concluam o Ensino Fundamental na idade correta de 14 anos, reduzindo a distorção idade-série a níveis inferiores a 5%.',
            'Taxa de Rendimento Escolar e Fluxo Censitário do Inep / CAEd 2026',
            '100% Censitário (172 estudantes matriculados e acompanhados com EWS preditivo)',
            'Laudas 01 a 40 (Diagnóstico Censitário e Matriz de Retenção Zero)',
            'Monitoramento sistemático do Early Warning System (EWS) pelo FME para prevenção de evasão.'
        ),
        (
            4,
            'Educação Especial Inclusiva (PAEE / PEI)',
            'Universalizar o atendimento educacional especializado (AEE) para os estudantes com deficiência, TGD/TEA e altas habilidades/superdotação na faixa de 4 a 17 anos em salas de recursos multifuncionais.',
            'Censo Escolar / Matrícula Dupla Fundeb e Auditoria de PEIs Registrados',
            '100% das 45 crianças identificadas com PEI individualizado, DUA e atendimento SRM',
            'Cadernos Individuais (Lauda 03: PEI Oficial; Lauda 04: Práticas Adaptadas)',
            'Garantia orçamentária no PME para ampliação de tecnologia assistiva e mediadores exclusivos.'
        ),
        (
            5,
            'Alfabetização Plena e Fluência na Idade Certa',
            'Alfabetizar 100% das crianças da rede municipal até o final do 2º ano do Ensino Fundamental com domínio de leitura fluente, escrita correta e cálculo inicial.',
            'Índice SPAECE Alfa (Régua CAEd: Padrão Adequado ≥ 150 pontos)',
            'Avanço de +28.4 pts em LP e 100% da turma do 2º Ano consolidada com fluência ≥ 85 PPM',
            'Laudas 05 a 30 (26 laudas de Alfabetização Fônica Sistemática e Fluência por aluno)',
            'Adoção da metodologia fônica estruturada Kumon/Dehaene como padrão referencial do município.'
        ),
        (
            6,
            'Educação em Tempo Integral (35H)',
            'Oferecer educação em tempo integral em, no mínimo, 50% das escolas públicas, de forma a atender a pelo menos 25% dos alunos da educação básica.',
            'Censo Escolar / Horas Semanais Registradas no INEP (≥ 35 horas semanais)',
            '100% das 7 turmas da Escola Airam Veras sob jornada de Tempo Integral (35H)',
            'Front Matter Universal (Lauda 34: Matriz Horária e Rotina de Tempo Integral)',
            'Defesa da expansão do modelo Airam Veras no FME como benchmark de política pública municipal.'
        ),
        (
            7,
            'Qualidade da Educação Básica e Elevação do Ideb/SPAECE',
            'Fomentar a qualidade da educação básica em todas as etapas com melhoria do fluxo escolar e da aprendizagem, superando as médias estaduais e municipais.',
            'Ideb (Meta Municipal ≥ 6.2) e Escala TRI CAEd/SPAECE (Níveis Adequado/Desejável)',
            'Crescimento linear verificado nos Ciclos I, II e III em Língua Portuguesa e Matemática',
            'Cadernos Individuais (Lauda 02: Comparativo Longitudinal Multiciclo dos 3 Ciclos)',
            'Uso dos relatórios analíticos territoriais do Inep pelo FME para eliminar disparidades educacionais.'
        ),
        (
            19,
            'Gestão Democrática e Participação Social',
            'Efetivar a gestão democrática da educação, com a consolidação e pleno funcionamento do Fórum Municipal de Educação e órgãos colegiados escolares.',
            'Atas de Plenária do FME, Decretos de Nomeação e Índices de Participação Social',
            'Participação ativa na Plenária Municipal e acolhimento total das diretrizes do FME/SNE',
            'Front Matter Master (Lauda 01 e 04: Marco Legal e Governança Democrática SNE)',
            'Fortalecimento do FME com mandato representativo e decisões estritamente baseadas em dados.'
        )
    ]

    cur.execute("DELETE FROM fato_alinhamento_pme_crateus_metas;")
    for meta, tema, descr, ind, status, evid, dir_fme in metas_pme:
        cur.execute("""
            INSERT INTO fato_alinhamento_pme_crateus_metas
            (meta_numero, tema_meta, descricao_meta_municipal, indicador_inep_caed, status_alcance_airam_veras, evidencia_dossie_laudas, diretriz_fme_comissao)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (meta, tema, descr, ind, status, evid, dir_fme))
        print(f" -> Inserida Meta {meta}: {tema}")

    conn.commit()

    # Registrar Bloco 33 no Ledger
    cur.execute("SELECT sequencia_bloco, hash_bloco_atual FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 1;")
    last_block = cur.fetchone()
    last_seq = last_block[0]
    last_hash = last_block[1]

    seq = last_seq + 1
    tabela = "dim_governanca_fme_pme_crateus"
    tipo_op = "ADEQUACAO_LEGAL_FME_PME_SNE_LC220"
    reg_id = "FORUM_MUNICIPAL_EDUCACAO_CRATEUS_SNE_2026"
    resumo = (
        "Adequação regulatória do banco de dados e dossiês com a Lei Complementar nº 220/2025 (Sistema Nacional de Educação - SNE, "
        "Arts. 16 a 21), Plano Nacional de Educação (Lei 13.005/2014, Art. 5º), Plano Municipal de Educação (PME) e Fórum Municipal "
        "de Educação (FME) de Crateús, estabelecendo matriz de competências (FME, CME, Comissão PME, SME) e governança baseada em dados "
        "do Inep, Ideb e SPAECE Censitário."
    )
    agente = "AIRAM_FME_GOVERNANCA_ENGINE_2026"
    h_atual = hashlib.sha256(f"{seq}_{tabela}_{tipo_op}_{reg_id}_{last_hash}_{now_utc}".encode('utf-8')).hexdigest()

    cur.execute("""
        INSERT INTO fato_auditoria_transacional_ledger
        (sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash, resumo_transacao, hash_bloco_anterior, hash_bloco_atual, timestamp_utc, agente_ou_processo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (seq, tabela, tipo_op, reg_id, resumo, last_hash, h_atual, now_utc, agente))

    conn.commit()
    conn.close()
    print(f"\n-> Sucesso! Bloco {seq} registrado com sucesso no Ledger! Hash: {h_atual}")
    return h_atual

if __name__ == '__main__':
    integrar_normativas()
