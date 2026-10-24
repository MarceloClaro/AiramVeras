-- ============================================================================
-- PROJETO AIRAM VERAS — SCHEMA RELACIONAL CANÔNICO E AUDITÁVEL DO ECOSSISTEMA
-- ============================================================================
-- Banco de Dados: airam_veras_ecossistema.sqlite
-- Compatibilidade: SQLite 3, PostgreSQL, Supabase, MySQL e Cloud SQL
-- Padrão de Engenharia: 3FN (Terceira Forma Normal) com Views Desnormalizadas
-- Padrão de Segurança: Zero-PII e Proteção de Dados Sensíveis de Saúde (LGPD)
-- ============================================================================

PRAGMA foreign_keys = ON;
PRAGMA encoding = 'UTF-8';

-- ============================================================================
-- 1. MÓDULO DE GOVERNANÇA, PROVENIÊNCIA E AUDITORIA (LINEAGE)
-- ============================================================================

CREATE TABLE IF NOT EXISTS dim_fontes_auditaveis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caminho_relativo TEXT NOT NULL UNIQUE,
    tipo_arquivo TEXT NOT NULL CHECK(tipo_arquivo IN ('CSV', 'ZIP', 'PDF', 'XLSX', 'SQLITE', 'JSON')),
    sha256_hash TEXT NOT NULL,
    tamanho_bytes INTEGER NOT NULL,
    orgao_emissor TEXT NOT NULL, -- 'CAEd', 'MEC_CNCA', 'SEDUC_CE', 'BNCC_MEC'
    ano_referencia INTEGER NOT NULL,
    ciclo_avaliacao TEXT, -- 'I', 'II', 'III', 'HISTORICO'
    data_extracao TEXT NOT NULL,
    data_registro_utc TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS sys_trilha_auditoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp_utc TEXT NOT NULL DEFAULT (datetime('now')),
    operacao TEXT NOT NULL CHECK(operacao IN ('INSERT', 'UPDATE', 'DELETE', 'CALCULO_PSICOMETRICO', 'INGESTAO', 'CONTRAPROVA')),
    tabela_afetada TEXT NOT NULL,
    id_registro_afetado TEXT,
    agente_executor TEXT NOT NULL,
    detalhes_operacao TEXT,
    sha256_estado_apos TEXT
);

-- ============================================================================
-- 2. MÓDULO INSTITUCIONAL, TURMAS E CENSO ESCOLAR
-- ============================================================================

CREATE TABLE IF NOT EXISTS dim_escola (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    inep_codigo TEXT NOT NULL UNIQUE,
    nome_escola TEXT NOT NULL,
    municipio TEXT NOT NULL DEFAULT 'Crateús',
    uf TEXT NOT NULL DEFAULT 'CE',
    dependencia_administrativa TEXT NOT NULL DEFAULT 'Municipal',
    data_criacao_registro TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS dim_turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    turma_codigo TEXT NOT NULL UNIQUE,
    ano_escolar INTEGER NOT NULL CHECK(ano_escolar BETWEEN 1 AND 5),
    nome_turma TEXT NOT NULL,
    turno TEXT NOT NULL DEFAULT 'Manhã',
    ano_letivo INTEGER NOT NULL DEFAULT 2026,
    escola_id INTEGER NOT NULL,
    FOREIGN KEY (escola_id) REFERENCES dim_escola(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS dim_estudantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL UNIQUE, -- HMAC-SHA256 determinístico (Zero-PII pública)
    turma_id INTEGER NOT NULL,
    ano_escolar INTEGER NOT NULL CHECK(ano_escolar BETWEEN 1 AND 5),
    situacao_matricula TEXT NOT NULL DEFAULT 'Matriculado' CHECK(situacao_matricula IN ('Matriculado', 'Transferido', 'Evadido', 'Não Avaliado')),
    possui_laudo_aee BOOLEAN NOT NULL DEFAULT 0,
    data_cadastro_utc TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (turma_id) REFERENCES dim_turmas(id) ON DELETE RESTRICT
);

-- Tabela isolada restrita com nomes civis (acesso restrito autorizado / LGPD)
CREATE TABLE IF NOT EXISTS dim_estudantes_nominal_restrito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL UNIQUE,
    nome_completo_criptografado TEXT NOT NULL,
    data_nascimento TEXT,
    matricula_institucional TEXT,
    FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id) ON DELETE CASCADE
);

-- ============================================================================
-- 3. MÓDULO DE EDUCAÇÃO ESPECIAL (AEE), CIDs E ACESSIBILIDADE AVALIATIVA
-- ============================================================================

CREATE TABLE IF NOT EXISTS dim_cid_catalogo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_cid10 TEXT NOT NULL,
    codigo_cid11 TEXT NOT NULL,
    grupo_diagnostico TEXT NOT NULL, -- 'TEA', 'TDAH', 'TOD', 'Transtorno Aprendizagem', 'Deficiencia Intelectual', 'Neurologico', 'Malformacao', 'Doenca Cronica'
    nomenclatura_oficial TEXT NOT NULL,
    impacto_avaliativo_resumo TEXT NOT NULL,
    estrategias_manejo_recomendadas TEXT NOT NULL,
    protocolo_sala_aula TEXT,
    protocolo_avaliativo_caed TEXT,
    fundamentacao_legal TEXT
);

CREATE TABLE IF NOT EXISTS fato_estudante_aee_perfil (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL UNIQUE,
    cid_primario_id INTEGER NOT NULL,
    cid_secundario_id INTEGER, -- Comorbidade (ex: F84.0 + F90.0 ou F91.3)
    pdi_ativo BOOLEAN NOT NULL DEFAULT 1,
    data_ultima_revisao_pdi TEXT,
    terminalidade_especifica BOOLEAN NOT NULL DEFAULT 0,
    -- Flags de recursos de acessibilidade mandatórios (LBI / Art. 28)
    recurso_tempo_estendido_50pct BOOLEAN NOT NULL DEFAULT 0,
    recurso_ledor_oficial BOOLEAN NOT NULL DEFAULT 0,
    recurso_transcritor_oficial BOOLEAN NOT NULL DEFAULT 0,
    recurso_ambiente_baixo_estimulo BOOLEAN NOT NULL DEFAULT 0,
    recurso_pausas_ativas_fracionadas BOOLEAN NOT NULL DEFAULT 0,
    recurso_tipografia_acessivel BOOLEAN NOT NULL DEFAULT 0,
    recurso_material_concreto BOOLEAN NOT NULL DEFAULT 0,
    recurso_prancha_comunicacao_caa BOOLEAN NOT NULL DEFAULT 0,
    -- Protocolo comportamental específico
    requer_manejo_tod_pbs BOOLEAN NOT NULL DEFAULT 0, -- Plano de Suporte Comportamental Positivo
    observacoes_clinico_pedagogicas TEXT,
    FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id) ON DELETE CASCADE,
    FOREIGN KEY (cid_primario_id) REFERENCES dim_cid_catalogo(id) ON DELETE RESTRICT,
    FOREIGN KEY (cid_secundario_id) REFERENCES dim_cid_catalogo(id) ON DELETE RESTRICT
);

-- ============================================================================
-- 4. MÓDULO CURRICULAR: BNCC, CAEd, CNCA E SPAECE
-- ============================================================================

CREATE TABLE IF NOT EXISTS dim_bncc_habilidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_bncc TEXT NOT NULL UNIQUE, -- 'EF01LP01', 'EF04MA02', 'EF03CI01', etc.
    etapa TEXT NOT NULL, -- 'Ensino Fundamental'
    ano_escolar INTEGER NOT NULL CHECK(ano_escolar BETWEEN 1 AND 5),
    componente_curricular TEXT NOT NULL, -- 'Língua Portuguesa', 'Matemática', 'Ciências', 'Geografia', 'História', 'Arte', 'Educação Física', 'Computação'
    unidade_tematica TEXT NOT NULL,
    objeto_conhecimento TEXT NOT NULL,
    descricao_habilidade TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_caed_descritores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_caed TEXT NOT NULL, -- '3EF09_P', '4EF07_M', etc.
    ano_escolar INTEGER NOT NULL CHECK(ano_escolar BETWEEN 1 AND 5),
    componente_curricular TEXT NOT NULL, -- 'LEITURA', 'MATEMATICA', 'ESCRITA', 'FLUENCIA'
    descricao_descritor TEXT NOT NULL,
    UNIQUE(codigo_caed, ano_escolar, componente_curricular)
);

CREATE TABLE IF NOT EXISTS dim_spaece_descritores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_spaece TEXT NOT NULL UNIQUE, -- 'D01', 'D12', etc.
    componente_curricular TEXT NOT NULL,
    etapa_ano TEXT NOT NULL,
    descricao_descritor TEXT NOT NULL
);

-- Arestas do Grafo Curricular Bipartido: CAEd ➔ BNCC
CREATE TABLE IF NOT EXISTS rel_caed_bncc_grafo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    caed_descritor_id INTEGER NOT NULL,
    bncc_habilidade_id INTEGER NOT NULL,
    ano_contextual INTEGER NOT NULL,
    peso_aresta REAL NOT NULL DEFAULT 1.0, -- Normalizado por grau para propagação
    tem_ressalva_semantica BOOLEAN NOT NULL DEFAULT 0,
    descricao_ressalva TEXT,
    FOREIGN KEY (caed_descritor_id) REFERENCES dim_caed_descritores(id) ON DELETE RESTRICT,
    FOREIGN KEY (bncc_habilidade_id) REFERENCES dim_bncc_habilidades(id) ON DELETE RESTRICT,
    UNIQUE(caed_descritor_id, bncc_habilidade_id, ano_contextual)
);

-- Correlação Interdisciplinar: Habilidades CAEd ➔ Ciências, Humanas, Artes e Computação
CREATE TABLE IF NOT EXISTS rel_interdisciplinar_bncc (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bncc_origem_id INTEGER NOT NULL, -- Habilidade LP ou Matemática
    bncc_correlata_id INTEGER NOT NULL, -- Habilidade Ciências, Geografia, História, etc.
    tipo_transferencia TEXT NOT NULL, -- 'Pré-requisito', 'Aplicação Prática', 'Pensamento Computacional', 'Semiótica'
    justificativa_pedagogica TEXT NOT NULL,
    FOREIGN KEY (bncc_origem_id) REFERENCES dim_bncc_habilidades(id) ON DELETE CASCADE,
    FOREIGN KEY (bncc_correlata_id) REFERENCES dim_bncc_habilidades(id) ON DELETE CASCADE
);

-- ============================================================================
-- 5. MÓDULO DE AVALIAÇÕES DIAGNÓSTICAS, RESPOSTAS E INSTRUMENTOS
-- ============================================================================

CREATE TABLE IF NOT EXISTS dim_avaliacoes_cadernos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    avaliacao_codigo TEXT NOT NULL UNIQUE, -- 'AV12026', 'AV22026', 'AV32026'
    ciclo TEXT NOT NULL CHECK(ciclo IN ('I', 'II', 'III')),
    ano_letivo INTEGER NOT NULL DEFAULT 2026,
    ano_escolar INTEGER NOT NULL CHECK(ano_escolar BETWEEN 1 AND 5),
    componente_curricular TEXT NOT NULL CHECK(componente_curricular IN ('LEITURA', 'MATEMATICA', 'ESCRITA', 'FLUENCIA')),
    total_itens_instrumento INTEGER NOT NULL DEFAULT 22,
    alvo_meta_b INTEGER NOT NULL DEFAULT 18 -- 80% de 22 itens
);

CREATE TABLE IF NOT EXISTS fato_participacao_estudante (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL,
    avaliacao_caderno_id INTEGER NOT NULL,
    turma_id INTEGER NOT NULL,
    status_participacao TEXT NOT NULL CHECK(status_participacao IN ('Avaliado', 'Ausente', 'Sem Resultado', 'Aplicação Mediada')),
    houve_recusa_comportamental_tod BOOLEAN NOT NULL DEFAULT 0,
    aplicacao_com_recursos_aee BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id) ON DELETE RESTRICT,
    FOREIGN KEY (avaliacao_caderno_id) REFERENCES dim_avaliacoes_cadernos(id) ON DELETE RESTRICT,
    FOREIGN KEY (turma_id) REFERENCES dim_turmas(id) ON DELETE RESTRICT,
    UNIQUE(aluno_hash_id, avaliacao_caderno_id)
);

CREATE TABLE IF NOT EXISTS fato_respostas_itens_habilidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participacao_id INTEGER NOT NULL,
    posicao_bloco TEXT NOT NULL, -- 'H01', 'H02', etc.
    caed_descritor_id INTEGER,
    acertos INTEGER NOT NULL CHECK(acertos >= 0),
    oportunidades INTEGER NOT NULL CHECK(oportunidades > 0),
    FOREIGN KEY (participacao_id) REFERENCES fato_participacao_estudante(id) ON DELETE CASCADE,
    FOREIGN KEY (caed_descritor_id) REFERENCES dim_caed_descritores(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS fato_producao_escrita (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participacao_id INTEGER NOT NULL UNIQUE,
    nota_pontuacao REAL,
    categoria_nivel TEXT, -- 'Nível 1' a 'Nível 4'
    atendeu_proposta BOOLEAN,
    adequacao_vocabular TEXT,
    FOREIGN KEY (participacao_id) REFERENCES fato_participacao_estudante(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fato_fluencia_leitora (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participacao_id INTEGER NOT NULL UNIQUE,
    palavras_lidas_minuto REAL,
    pseudopalavras_lidas REAL,
    precisao_leitura_pct REAL,
    perfil_leitor TEXT CHECK(perfil_leitor IN ('Pré-Leitor', 'Leitor de Sílabas/Palavras', 'Leitor de Frases', 'Leitor de Texto sem Fluência', 'Leitor Fluente')),
    FOREIGN KEY (participacao_id) REFERENCES fato_participacao_estudante(id) ON DELETE CASCADE
);

-- ============================================================================
-- 6. MÓDULO PSICOMÉTRICO (TRI/TCT), METAS E INTERVENÇÃO DOCENTE
-- ============================================================================

CREATE TABLE IF NOT EXISTS fato_escores_psicometricos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    participacao_id INTEGER NOT NULL UNIQUE,
    -- Escore Aritmético Censitário
    total_acertos INTEGER NOT NULL,
    total_oportunidades INTEGER NOT NULL,
    taxa_rendimento_ponderada REAL NOT NULL, -- ∑ Acertos / ∑ Oportunidades
    -- Modelagem Psicométrica TRI / Rasch
    theta_habilidade_latente REAL,
    erro_padrao_theta REAL,
    proficiencia_escala_spaece REAL, -- Escala 0 a 500
    nivel_desempenho_caed TEXT NOT NULL CHECK(nivel_desempenho_caed IN ('Abaixo do Básico', 'Básico', 'Adequado', 'Avançado', 'Não Aplicável')),
    -- Metas Institucionais
    atingiu_meta_a_adequado BOOLEAN NOT NULL DEFAULT 0,
    acertos_adicionais_para_meta_a INTEGER DEFAULT 0,
    atingiu_meta_b_80pct BOOLEAN NOT NULL DEFAULT 0, -- Acertos >= 18
    lacuna_meta_b INTEGER NOT NULL DEFAULT 0, -- max(0, 18 - acertos)
    data_processamento TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (participacao_id) REFERENCES fato_participacao_estudante(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS dim_grupos_intervencao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_grupo TEXT NOT NULL UNIQUE, -- 'G1', 'G2', 'G3', 'G4'
    nome_perfil TEXT NOT NULL,
    descricao_clinico_pedagogica TEXT NOT NULL,
    estrategias_didaticas_prioritarias TEXT NOT NULL,
    frequencia_semanal_reforco_sugerida TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_estudante_agrupamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL,
    avaliacao_caderno_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    estabilidade_bootstrap_pct REAL NOT NULL DEFAULT 100.0,
    FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id) ON DELETE CASCADE,
    FOREIGN KEY (avaliacao_caderno_id) REFERENCES dim_avaliacoes_cadernos(id) ON DELETE CASCADE,
    FOREIGN KEY (grupo_id) REFERENCES dim_grupos_intervencao(id) ON DELETE RESTRICT,
    UNIQUE(aluno_hash_id, avaliacao_caderno_id)
);

CREATE TABLE IF NOT EXISTS fato_cenarios_what_if (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ano_escolar INTEGER NOT NULL,
    componente_curricular TEXT NOT NULL,
    ciclo TEXT NOT NULL,
    nome_cenario TEXT NOT NULL CHECK(nome_cenario IN ('sem_mudanca', 'ganho_um', 'perda_um', 'ganho_um_perda_um')),
    taxa_adequacao_projetada_pct REAL NOT NULL,
    alunos_adequados_projetados INTEGER NOT NULL,
    meta_a_atingida_projetada BOOLEAN NOT NULL,
    alunos_meta_b_projetados INTEGER NOT NULL
);

-- ============================================================================
-- 7. VIEWS ANALÍTICAS PARA FRAMEWORKS (REACT, NEXT.JS, FASTAPI, FLUTTER, BI)
-- ============================================================================

-- Visão 1: Painel Executivo Consolidado por Ano e Componente (Meta A e Meta B)
CREATE VIEW IF NOT EXISTS vw_dashboard_escola_metas AS
SELECT 
    t.ano_escolar,
    ac.componente_curricular,
    ac.ciclo,
    COUNT(fpe.id) AS total_cadastros,
    SUM(CASE WHEN fpe.status_participacao = 'Avaliado' THEN 1 ELSE 0 END) AS total_avaliados,
    SUM(CASE WHEN fpe.status_participacao = 'Ausente' THEN 1 ELSE 0 END) AS total_ausentes,
    SUM(CASE WHEN fep.atingiu_meta_a_adequado = 1 THEN 1 ELSE 0 END) AS total_adequados,
    ROUND(100.0 * SUM(CASE WHEN fep.atingiu_meta_a_adequado = 1 THEN 1 ELSE 0 END) / 
          NULLIF(SUM(CASE WHEN fpe.status_participacao = 'Avaliado' THEN 1 ELSE 0 END), 0), 1) AS taxa_adequacao_pct,
    CAST(ROUND(0.8 * SUM(CASE WHEN fpe.status_participacao = 'Avaliado' THEN 1 ELSE 0 END) + 0.499) AS INTEGER) AS alvo_meta_a_80pct,
    MAX(0, CAST(ROUND(0.8 * SUM(CASE WHEN fpe.status_participacao = 'Avaliado' THEN 1 ELSE 0 END) + 0.499) AS INTEGER) - 
           SUM(CASE WHEN fep.atingiu_meta_a_adequado = 1 THEN 1 ELSE 0 END)) AS conversoes_necessarias_meta_a,
    SUM(CASE WHEN fep.atingiu_meta_b_80pct = 1 THEN 1 ELSE 0 END) AS total_atingiram_meta_b,
    ROUND(AVG(fep.proficiencia_escala_spaece), 1) AS media_proficiencia_spaece
FROM dim_avaliacoes_cadernos ac
JOIN fato_participacao_estudante fpe ON ac.id = fpe.avaliacao_caderno_id
JOIN dim_turmas t ON fpe.turma_id = t.id
LEFT JOIN fato_escores_psicometricos fep ON fpe.id = fep.participacao_id
GROUP BY t.ano_escolar, ac.componente_curricular, ac.ciclo;

-- Visão 2: Painel Operacional do Professor (Intervenção Individual por Turma)
CREATE VIEW IF NOT EXISTS vw_painel_intervencao_professor AS
SELECT 
    e.aluno_hash_id,
    t.nome_turma,
    t.ano_escolar,
    ac.componente_curricular,
    fpe.status_participacao,
    fep.total_acertos,
    fep.total_oportunidades,
    ROUND(fep.taxa_rendimento_ponderada * 100, 1) AS rendimento_pct,
    fep.nivel_desempenho_caed,
    fep.atingiu_meta_a_adequado,
    fep.atingiu_meta_b_80pct,
    fep.lacuna_meta_b,
    gi.codigo_grupo,
    gi.nome_perfil AS grupo_nome,
    e.possui_laudo_aee,
    cid.codigo_cid10,
    cid.codigo_cid11,
    perfil.requer_manejo_tod_pbs,
    perfil.recurso_tempo_estendido_50pct,
    perfil.recurso_ledor_oficial
FROM dim_estudantes e
JOIN dim_turmas t ON e.turma_id = t.id
JOIN fato_participacao_estudante fpe ON e.aluno_hash_id = fpe.aluno_hash_id
JOIN dim_avaliacoes_cadernos ac ON fpe.avaliacao_caderno_id = ac.id
LEFT JOIN fato_escores_psicometricos fep ON fpe.id = fep.participacao_id
LEFT JOIN fato_estudante_agrupamento fea ON e.aluno_hash_id = fea.aluno_hash_id AND ac.id = fea.avaliacao_caderno_id
LEFT JOIN dim_grupos_intervencao gi ON fea.grupo_id = gi.id
LEFT JOIN fato_estudante_aee_perfil perfil ON e.aluno_hash_id = perfil.aluno_hash_id
LEFT JOIN dim_cid_catalogo cid ON perfil.cid_primario_id = cid.id;

-- Visão 3: Relatório de Acessibilidade e Educação Especial Inclusiva (AEE)
CREATE VIEW IF NOT EXISTS vw_relatorio_aee_inclusao AS
SELECT 
    e.aluno_hash_id,
    t.nome_turma,
    t.ano_escolar,
    cid.codigo_cid10,
    cid.codigo_cid11,
    cid.grupo_diagnostico,
    cid.nomenclatura_oficial,
    perfil.pdi_ativo,
    perfil.terminalidade_especifica,
    perfil.recurso_tempo_estendido_50pct,
    perfil.recurso_ledor_oficial,
    perfil.recurso_transcritor_oficial,
    perfil.recurso_ambiente_baixo_estimulo,
    perfil.recurso_pausas_ativas_fracionadas,
    perfil.requer_manejo_tod_pbs,
    cid.estrategias_manejo_recomendadas,
    cid.protocolo_sala_aula,
    cid.protocolo_avaliativo_caed,
    cid.fundamentacao_legal,
    perfil.observacoes_clinico_pedagogicas
FROM fato_estudante_aee_perfil perfil
JOIN dim_estudantes e ON perfil.aluno_hash_id = e.aluno_hash_id
JOIN dim_turmas t ON e.turma_id = t.id
JOIN dim_cid_catalogo cid ON perfil.cid_primario_id = cid.id;

-- Visão 4: Grafo Curricular Completo (CAEd ➔ BNCC com Áreas e Objetos)
CREATE VIEW IF NOT EXISTS vw_grafo_curricular_caed_bncc AS
SELECT 
    dcaed.codigo_caed,
    dcaed.ano_escolar,
    dcaed.componente_curricular,
    dcaed.descricao_descritor,
    dbncc.codigo_bncc,
    dbncc.componente_curricular AS bncc_componente,
    dbncc.unidade_tematica,
    dbncc.objeto_conhecimento,
    dbncc.descricao_habilidade,
    grafo.peso_aresta,
    grafo.tem_ressalva_semantica,
    grafo.descricao_ressalva
FROM rel_caed_bncc_grafo grafo
JOIN dim_caed_descritores dcaed ON grafo.caed_descritor_id = dcaed.id
JOIN dim_bncc_habilidades dbncc ON grafo.bncc_habilidade_id = dbncc.id;

-- ============================================================================
-- 9. MÓDULO DE BIOMARCADORES ESTATÍSTICOS, ALTAS HABILIDADES E TOPOLOGIA
-- ============================================================================

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

-- Visão 5: Painel de Rastreio de Altas Habilidades e Dupla Excepcionalidade (2e)
CREATE VIEW IF NOT EXISTS vw_rastreio_altas_habilidades_dupla_excepcionalidade AS
SELECT 
    ah.aluno_hash_id,
    t.nome_turma,
    ah.ano_escolar,
    ah.indice_global_eficiencia_cognitiva AS igec,
    ah.dominio_talento_predominante,
    ah.possui_dupla_excepcionalidade_2e,
    ah.codigo_cid_comorbidade_2e,
    cid.nomenclatura_oficial AS comorbidade_nome,
    ah.tipo_enriquecimento_renzulli,
    ah.estrategias_compactacao_curricular,
    ah.indicacao_aceleracao_conteudo,
    ah.hash_validacao_forense
FROM fato_rastreio_altas_habilidades ah
JOIN dim_estudantes e ON ah.aluno_hash_id = e.aluno_hash_id
JOIN dim_turmas t ON e.turma_id = t.id
LEFT JOIN dim_cid_catalogo cid ON ah.codigo_cid_comorbidade_2e = cid.codigo_cid10;
-- ============================================================================
-- CAMADA OURO: METODOLOGIAS DE APRENDIZAGEM, KUMON GRANULAR E MÉTODO FÔNICO
-- Validação Neurocientífica, Autodidatismo e Rastreio Interdisciplinar Conectado
-- ============================================================================

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

CREATE TABLE IF NOT EXISTS dim_kumon_niveis_granulares (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_nivel TEXT NOT NULL UNIQUE,
    disciplina_eixo TEXT NOT NULL,
    nome_nivel TEXT NOT NULL,
    ano_escolar_sugerido TEXT NOT NULL,
    foco_operacional_micro_passo TEXT NOT NULL,
    tempo_padrao_conclusao_min INTEGER NOT NULL,
    meta_maestria_pct REAL NOT NULL,
    descritores_caed_alvo TEXT NOT NULL,
    habilidades_bncc_alvo TEXT NOT NULL,
    prerequisito_nivel TEXT,
    FOREIGN KEY (prerequisito_nivel) REFERENCES dim_kumon_niveis_granulares(codigo_nivel)
);

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

CREATE TABLE IF NOT EXISTS rel_kumon_fonico_rede_interdisciplinar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    origem_tipo TEXT NOT NULL,
    origem_codigo TEXT NOT NULL,
    componente_conectado TEXT NOT NULL,
    habilidade_bncc_conectada TEXT NOT NULL,
    descritor_caed_conectado TEXT NOT NULL,
    mecanismo_interdisciplinar TEXT NOT NULL,
    peso_conexao REAL NOT NULL,
    hash_conexao TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fato_trilha_aprendizagem_granular_aluno (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL,
    ano_escolar TEXT NOT NULL,
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
    FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id),
    FOREIGN KEY (estagio_fonico_atual) REFERENCES dim_metodo_fonico_estagios(codigo_estagio),
    FOREIGN KEY (nivel_kumon_mat_atual) REFERENCES dim_kumon_niveis_granulares(codigo_nivel),
    FOREIGN KEY (nivel_kumon_leit_atual) REFERENCES dim_kumon_niveis_granulares(codigo_nivel)
);

-- Visão 6: Painel Unificado de Rastreio Interdisciplinar (Fônico + Kumon + CAEd)
CREATE VIEW IF NOT EXISTS vw_painel_fonico_kumon_rastreio AS
SELECT 
    t.aluno_hash_id,
    e.turma_id,
    tur.nome_turma,
    t.ano_escolar,
    f.nome_estagio AS estagio_fonico,
    f.fase_ehri_correspondente,
    km.nome_nivel AS kumon_mat_nivel,
    kl.nome_nivel AS kumon_leit_nivel,
    t.indice_autodidatismo_pct,
    t.taxa_maestria_granular_pct,
    t.tempo_medio_folha_min,
    t.status_evolucao_kumon,
    t.estrategia_interdisciplinar_ativa,
    t.hash_validacao_forense
FROM fato_trilha_aprendizagem_granular_aluno t
JOIN dim_estudantes e ON t.aluno_hash_id = e.aluno_hash_id
JOIN dim_turmas tur ON e.turma_id = tur.id
JOIN dim_metodo_fonico_estagios f ON t.estagio_fonico_atual = f.codigo_estagio
JOIN dim_kumon_niveis_granulares km ON t.nivel_kumon_mat_atual = km.codigo_nivel
-- ============================================================================
-- CAMADA PLATINUM: EARLY WARNING SYSTEM (EWS), AUDITORIA LEDGER E VISÃO 360º
-- Governança Criptográfica, Índices B-Tree de Alta Performance e Predição de Risco
-- ============================================================================

-- Índices B-Tree Analíticos Compostos
CREATE INDEX IF NOT EXISTS idx_participacao_aluno_caderno ON fato_participacao_estudante (aluno_hash_id, avaliacao_caderno_id);
CREATE INDEX IF NOT EXISTS idx_escores_participacao_nivel ON fato_escores_psicometricos (participacao_id, nivel_desempenho_caed);
CREATE INDEX IF NOT EXISTS idx_trilha_kumon_fonico ON fato_trilha_aprendizagem_granular_aluno (aluno_hash_id, status_evolucao_kumon, taxa_maestria_granular_pct);
CREATE INDEX IF NOT EXISTS idx_aee_perfil_aluno ON fato_estudante_aee_perfil (aluno_hash_id, cid_primario_id);
CREATE INDEX IF NOT EXISTS idx_grafo_caed_bncc ON rel_caed_bncc_grafo (caed_descritor_id, bncc_habilidade_id);
CREATE INDEX IF NOT EXISTS idx_altas_habilidades_aluno ON fato_rastreio_altas_habilidades (aluno_hash_id, possui_dupla_excepcionalidade_2e);

-- Catálogo de Fatores de Risco EWS
CREATE TABLE IF NOT EXISTS dim_fatores_risco_ews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_fator TEXT NOT NULL UNIQUE,
    categoria_fator TEXT NOT NULL,
    descricao_fator TEXT NOT NULL,
    peso_algoritmico REAL NOT NULL,
    acao_mitigadora_recomendada TEXT NOT NULL
);

-- Predição Censitária EWS por Estudante
CREATE TABLE IF NOT EXISTS fato_predicao_alerta_precoce_ews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL UNIQUE,
    ano_escolar TEXT NOT NULL,
    probabilidade_risco_defasagem REAL NOT NULL,
    nivel_risco_ews TEXT NOT NULL, -- CRITICO, ALTO, MODERADO, CONSOLIDADO
    fator_risco_preponderante TEXT NOT NULL,
    score_tri_impacto REAL NOT NULL,
    score_kumon_lacuna REAL NOT NULL,
    score_aee_vulnerabilidade REAL NOT NULL,
    score_frequencia_participacao REAL NOT NULL,
    protocolo_intervencao_sugerido TEXT NOT NULL,
    data_calculo_predicao TEXT NOT NULL,
    hash_validacao_forense TEXT NOT NULL,
    FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id)
);

-- Ledger de Auditoria Criptográfica Imutável (Blockchain-like Forense)
CREATE TABLE IF NOT EXISTS fato_auditoria_transacional_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sequencia_bloco INTEGER NOT NULL UNIQUE,
    tabela_afetada TEXT NOT NULL,
    tipo_operacao TEXT NOT NULL, -- INSERT, UPDATE, DELETE, HOMOLOGACAO
    registro_id_ou_hash TEXT NOT NULL,
    resumo_transacao TEXT NOT NULL,
    hash_bloco_anterior TEXT NOT NULL,
    hash_bloco_atual TEXT NOT NULL,
    timestamp_utc TEXT NOT NULL,
    agente_ou_processo TEXT NOT NULL
);

-- Trigger de Auditoria Automática
CREATE TRIGGER IF NOT EXISTS trg_audit_escores_psicometricos_ins
AFTER INSERT ON fato_escores_psicometricos
BEGIN
    INSERT INTO fato_auditoria_transacional_ledger (
        sequencia_bloco,
        tabela_afetada,
        tipo_operacao,
        registro_id_ou_hash,
        resumo_transacao,
        hash_bloco_anterior,
        hash_bloco_atual,
        timestamp_utc,
        agente_ou_processo
    )
    VALUES (
        (SELECT COALESCE(MAX(sequencia_bloco), 0) + 1 FROM fato_auditoria_transacional_ledger),
        'fato_escores_psicometricos',
        'INSERT',
        'PART_ID_' || NEW.participacao_id,
        'Novo escore computado: acertos ' || NEW.total_acertos || ' nivel ' || NEW.nivel_desempenho_caed,
        (SELECT COALESCE(MAX(hash_bloco_atual), '0000000000000000000000000000000000000000000000000000000000000000') FROM fato_auditoria_transacional_ledger),
        lower(hex(sha256(NEW.participacao_id || NEW.total_acertos || datetime('now')))),
        datetime('now'),
        'TRIGGER_SQLITE_AUDIT'
    );
END;

-- Visão 7: Visão Canônica 360º Universal do Estudante
CREATE VIEW IF NOT EXISTS vw_estudante_raiox_360 AS
SELECT 
    e.aluno_hash_id,
    t.nome_turma,
    CASE 
        WHEN t.nome_turma LIKE '%1º%' THEN '1º Ano'
        WHEN t.nome_turma LIKE '%2º%' THEN '2º Ano'
        WHEN t.nome_turma LIKE '%3º%' THEN '3º Ano'
        WHEN t.nome_turma LIKE '%4º%' THEN '4º Ano'
        ELSE '5º Ano'
    END AS ano_escolar,
    -- CAEd Língua Portuguesa
    MAX(CASE WHEN c.componente_curricular = 'LINGUA_PORTUGUESA' OR c.componente_curricular = 'LEITURA' THEN ROUND(ep.taxa_rendimento_ponderada * 100, 1) END) AS acerto_lp_pct,
    MAX(CASE WHEN c.componente_curricular = 'LINGUA_PORTUGUESA' OR c.componente_curricular = 'LEITURA' THEN ep.nivel_desempenho_caed END) AS nivel_caed_lp,
    MAX(CASE WHEN c.componente_curricular = 'LINGUA_PORTUGUESA' OR c.componente_curricular = 'LEITURA' THEN ep.atingiu_meta_b_80pct END) AS meta_b_lp,
    -- CAEd Matemática
    MAX(CASE WHEN c.componente_curricular = 'MATEMATICA' THEN ROUND(ep.taxa_rendimento_ponderada * 100, 1) END) AS acerto_mat_pct,
    MAX(CASE WHEN c.componente_curricular = 'MATEMATICA' THEN ep.nivel_desempenho_caed END) AS nivel_caed_mat,
    MAX(CASE WHEN c.componente_curricular = 'MATEMATICA' THEN ep.atingiu_meta_b_80pct END) AS meta_b_mat,
    -- Método Fônico & Kumon Granular
    tk.estagio_fonico_atual,
    mfe.nome_estagio AS nome_estagio_fonico,
    tk.nivel_kumon_mat_atual,
    tk.nivel_kumon_leit_atual,
    tk.taxa_maestria_granular_pct AS maestria_kumon_pct,
    tk.tempo_medio_folha_min,
    tk.indice_autodidatismo_pct,
    tk.status_evolucao_kumon,
    -- AEE & CIDs
    MAX(CASE WHEN aee.aluno_hash_id IS NOT NULL THEN 1 ELSE 0 END) AS eh_laudado_aee,
    MAX(cid.codigo_cid10) AS codigo_cid10,
    MAX(cid.nomenclatura_oficial) AS cid_nome,
    -- Altas Habilidades / Dupla Excepcionalidade
    MAX(CASE WHEN ah.aluno_hash_id IS NOT NULL THEN 1 ELSE 0 END) AS eh_superdotado_ahsd,
    MAX(COALESCE(ah.possui_dupla_excepcionalidade_2e, 0)) AS eh_dupla_excepcionalidade_2e,
    -- Early Warning System (EWS)
    ews.probabilidade_risco_defasagem,
    ews.nivel_risco_ews,
    ews.fator_risco_preponderante,
    ews.protocolo_intervencao_sugerido,
    ews.hash_validacao_forense
FROM dim_estudantes e
JOIN dim_turmas t ON e.turma_id = t.id
LEFT JOIN fato_participacao_estudante p ON e.aluno_hash_id = p.aluno_hash_id
LEFT JOIN dim_avaliacoes_cadernos c ON p.avaliacao_caderno_id = c.id
LEFT JOIN fato_escores_psicometricos ep ON p.id = ep.participacao_id
LEFT JOIN fato_estudante_aee_perfil aee ON e.aluno_hash_id = aee.aluno_hash_id
LEFT JOIN dim_cid_catalogo cid ON aee.cid_primario_id = cid.id
LEFT JOIN fato_trilha_aprendizagem_granular_aluno tk ON e.aluno_hash_id = tk.aluno_hash_id
LEFT JOIN dim_metodo_fonico_estagios mfe ON tk.estagio_fonico_atual = mfe.codigo_estagio
LEFT JOIN fato_rastreio_altas_habilidades ah ON e.aluno_hash_id = ah.aluno_hash_id
LEFT JOIN fato_predicao_alerta_precoce_ews ews ON e.aluno_hash_id = ews.aluno_hash_id
GROUP BY e.aluno_hash_id;

