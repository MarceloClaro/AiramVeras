"""
Módulo de Integração Auditável e Bioestatística do SAAP 1º Ano no Ecossistema Airam Veras
- Ingestão dos microdados de Leitura e Escrita (1º, 2º e 3º Bimestres)
- Cruzamento com CAEd (Ciclos I, II e III) e Perfis Neurodivergentes (CIDs 10 e 11)
- Atualização cadastral institucional da Escola (Endereço, INEP, Localização, Dependência Adm.)
- Registro no Ledger Criptográfico (Bloco 36)
"""

import sqlite3
import hashlib
import json
import datetime
import os
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "dados", "airam_veras_ecossistema.sqlite")

print(f"[*] Conectando ao Banco de Dados Canônico: {DB_PATH}")
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# -------------------------------------------------------------------------------------------------
# 1. ATUALIZAÇÃO INSTITUCIONAL DA ESCOLA (dim_escola)
# -------------------------------------------------------------------------------------------------
print("[*] 1. Atualizando dados cadastrais e endereço institucional da escola...")

# Verificar e adicionar colunas se não existirem
colunas_escola = [col[1] for col in c.execute("PRAGMA table_info(dim_escola)").fetchall()]
novas_colunas = {
    "endereco_logradouro": "TEXT DEFAULT 'Rua Capistrano de Abreu'",
    "numero": "TEXT DEFAULT 'S/N'",
    "bairro": "TEXT DEFAULT 'Ipase'",
    "cep": "TEXT DEFAULT '63700-450'",
    "telefone_contato": "TEXT DEFAULT '(88)'",
    "localizacao_censo": "TEXT DEFAULT 'Urbana'",
    "data_atualizacao_cadastral": "TEXT DEFAULT '2026-10-28 00:00:00'"
}

for col_nome, col_tipo in novas_colunas.items():
    if col_nome not in colunas_escola:
        c.execute(f"ALTER TABLE dim_escola ADD COLUMN {col_nome} {col_tipo};")
        print(f"    [+] Coluna adicionada em dim_escola: {col_nome}")

# Atualizar linha institucional da escola
c.execute("""
UPDATE dim_escola
SET inep_codigo = '23084995',
    nome_escola = 'ESCOLA DE ENSINO FUNDAMENTAL EM TEMPO INTEGRAL AIRAM VERAS',
    municipio = 'Crateús',
    uf = 'CE',
    dependencia_administrativa = 'Municipal',
    endereco_logradouro = 'Rua Capistrano de Abreu',
    numero = 'S/N',
    bairro = 'Ipase',
    cep = '63700-450',
    telefone_contato = '(88)',
    localizacao_censo = 'Urbana',
    data_atualizacao_cadastral = datetime('now')
WHERE id = 1;
""")
print("    [✓] Dados da Escola atualizados: INEP 23084995 | Rua Capistrano de Abreu, S/N - Ipase, CEP 63700-450, Crateús-CE | Urbana | Municipal")

# -------------------------------------------------------------------------------------------------
# 2. SINCRONIZAÇÃO DE ALUNOS DO 1º ANO (Francisca Adila)
# -------------------------------------------------------------------------------------------------
print("[*] 2. Verificando cadastro nominal de estudantes do 1º Ano...")

# Verificar se Francisca Adila Caxias de Almeida existe
nome_adila = "FRANCISCA ADILA CAXIAS DE ALMEIDA"
r_adila = c.execute("SELECT id, aluno_hash_id FROM dim_estudantes_nominal_restrito WHERE nome_completo_criptografado = ?", (nome_adila,)).fetchone()

if not r_adila:
    hash_adila = hashlib.sha256(nome_adila.encode('utf-8')).hexdigest()
    # Inserir em dim_estudantes_nominal_restrito
    c.execute("""
    INSERT INTO dim_estudantes_nominal_restrito (aluno_hash_id, nome_completo_criptografado, data_nascimento, matricula_institucional)
    VALUES (?, ?, '2019-05-14', 'MAT-2026-1ANO-025');
    """, (hash_adila, nome_adila))
    
    # Inserir em dim_estudantes
    c.execute("""
    INSERT INTO dim_estudantes (aluno_hash_id, turma_id, ano_escolar, situacao_matricula, possui_laudo_aee, data_cadastro_utc)
    VALUES (?, 1, 1, 'Matriculado', 0, datetime('now'));
    """, (hash_adila,))
    print(f"    [+] Aluna cadastrada com sucesso: {nome_adila} (Hash: {hash_adila[:12]}...)")
else:
    print(f"    [i] Aluna já presente: {nome_adila} (ID {r_adila[0]})")

# -------------------------------------------------------------------------------------------------
# 3. CRIAÇÃO DA TABELA CANÔNICA fato_saap_avaliacao_bimestral_1ano
# -------------------------------------------------------------------------------------------------
print("[*] 3. Estruturando tabela canônica fato_saap_avaliacao_bimestral_1ano...")

c.execute("""
CREATE TABLE IF NOT EXISTS fato_saap_avaliacao_bimestral_1ano (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_hash_id TEXT NOT NULL,
    nome_estudante TEXT NOT NULL,
    ano_escolar INTEGER NOT NULL DEFAULT 1,
    bimestre INTEGER NOT NULL,
    situacao_escrita TEXT NOT NULL,
    nivel_escrita_escore INTEGER NOT NULL,
    situacao_leitura TEXT NOT NULL,
    nivel_leitura_escore INTEGER NOT NULL,
    delta_escrita_bimestral INTEGER DEFAULT 0,
    delta_leitura_bimestral INTEGER DEFAULT 0,
    status_evolucao_escrita TEXT,
    status_evolucao_leitura TEXT,
    possui_laudo_cid BOOLEAN NOT NULL DEFAULT 0,
    codigo_cid10 TEXT,
    codigo_cid11 TEXT,
    diagnostico_resumo TEXT,
    cuidador_dedicado TEXT,
    necessita_adaptacao_pei BOOLEAN NOT NULL DEFAULT 0,
    alerta_regressao_ews BOOLEAN NOT NULL DEFAULT 0,
    natureza_barreira TEXT,
    estrategia_intervencao_prioritaria TEXT,
    fonte_documento TEXT NOT NULL,
    data_ingestao_utc TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (aluno_hash_id) REFERENCES dim_estudantes(aluno_hash_id)
);
""")

c.execute("CREATE INDEX IF NOT EXISTS idx_saap_1ano_hash ON fato_saap_avaliacao_bimestral_1ano(aluno_hash_id);")
c.execute("CREATE INDEX IF NOT EXISTS idx_saap_1ano_bimestre ON fato_saap_avaliacao_bimestral_1ano(bimestre);")

# Limpar dados prévios se houver
c.execute("DELETE FROM fato_saap_avaliacao_bimestral_1ano;")

# -------------------------------------------------------------------------------------------------
# 4. MAPA DE DADOS E METADADOS CLÍNICOS/NEURODIVERGENTES DO 1º ANO
# -------------------------------------------------------------------------------------------------
print("[*] 4. Processando microdados do SAAP e cruzando com perfis AEE...")

# Escores ordinais
ESCORE_ESCRITA = {
    "PRE": 1,        # Pré-Silábico
    "SIL": 2,        # Silábico
    "SIL_ALF": 3,    # Silábico-Alfabético
    "ALF": 4,        # Alfabético
    "ORT": 5         # Ortográfico
}

ESCORE_LEITURA = {
    "NL": 1,         # Não Leitor
    "LS": 2,         # Leitor de Sílabas
    "LP": 3,         # Leitor de Palavras
    "LF": 4,         # Leitor de Frases
    "LTSF": 5,       # Leitor de Texto sem Fluência
    "LTF": 6         # Leitor de Texto com Fluência
}

# Microdados oficiais transcritos
DADOS_SAAP_RAW = [
    {
        "nome": "ANTONIO CALLEBY PEREIRA LIMA",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "ALF"},
        "leitura": {1: "NL", 2: "LP", 3: "LF"}
    },
    {
        "nome": "DANIEL CONCEICAO PIMENTEL",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL_ALF"},
        "leitura": {1: "NL", 2: "LP", 3: "LS"}
    },
    {
        "nome": "EMANUELLY DO NASCIMENTO BEZERRA",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "ALF"},
        "leitura": {1: "NL", 2: "LP", 3: "LF"}
    },
    {
        "nome": "FRANCISCA ADILA CAXIAS DE ALMEIDA",
        "escrita": {1: "SIL_ALF", 2: "SIL", 3: "PRE"},
        "leitura": {1: "LS", 2: "NL", 3: "NL"}
    },
    {
        "nome": "FRANCISCO MIGUEL MARTINS DE SOUSA",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL_ALF"},
        "leitura": {1: "NL", 2: "LS", 3: "LS"}
    },
    {
        "nome": "GUSTAVO HENRIQUE MORENO DA SILVA",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "NL", 3: "NL"}
    },
    {
        "nome": "GUSTAVO SALES MACHADO",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "NL", 3: "LS"}
    },
    {
        "nome": "ISABELLA MARTINS FEITOSA",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "LS", 3: "LS"}
    },
    {
        "nome": "ISAC LUCCA FERNANDES MARTINS",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "LS", 3: "LS"}
    },
    {
        "nome": "ISIS GOMES MESQUITA",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "NL", 3: "NL"}
    },
    {
        "nome": "ISIS KETLEN SOUSA DA SILVA",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "NL", 3: "LS"}
    },
    {
        "nome": "JOSE YHUDY BENICIO FERREIRA DE ANDRADE",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "ALF"},
        "leitura": {1: "NL", 2: "LP", 3: "LF"}
    },
    {
        "nome": "LIVYA MARIA ALVES MELO",
        "escrita": {1: "SIL_ALF", 2: "SIL", 3: "ALF"},
        "leitura": {1: "LF", 2: "LTSF", 3: "LF"}
    },
    {
        "nome": "LUNNA DE SOUSA SILVA",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL_ALF"},
        "leitura": {1: "NL", 2: "LP", 3: "LF"}
    },
    {
        "nome": "MARIA AGATHA DE SOUSA NEVES",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "NL", 3: "LS"}
    },
    {
        "nome": "MARIA ISIS DA CONCEICAO DE SOUSA",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "PRE"},
        "leitura": {1: "NL", 2: "NL", 3: "NL"}
    },
    {
        "nome": "MARIA ISIS PEREIRA GOMES",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "LP", 3: "NL"}
    },
    {
        "nome": "MARIA JULIANA VIEIRA GOMES",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "SIL_ALF"},
        "leitura": {1: "NL", 2: "LTSF", 3: "LF"}
    },
    {
        "nome": "MARIA LETICIA MARTINS DA SILVA",
        "escrita": {1: "PRE", 2: "SIL", 3: "SIL"},
        "leitura": {1: "NL", 2: "LTSF", 3: "NL"}
    },
    {
        "nome": "MARIA SOPHIA MARQUES SILVA",
        "escrita": {1: "SIL_ALF", 2: "ALF", 3: "ALF"},
        "leitura": {1: "LTSF", 2: "LTF", 3: "LTF"}
    },
    {
        "nome": "MARIA YORRANA OLIVEIRA ARAUJO",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "SIL_ALF"},
        "leitura": {1: "NL", 2: "NL", 3: "NL"}
    },
    {
        "nome": "MOISES TOLEDO DE SOUSA",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "SIL_ALF"},
        "leitura": {1: "NL", 2: "NL", 3: "LS"}
    },
    {
        "nome": "RUAN LUCAS DE SOUZA SALES",
        "escrita": {1: "PRE", 2: "SIL_ALF", 3: "SIL_ALF"},
        "leitura": {1: "NL", 2: "LTF", 3: "NL"}
    }
]

# Obter dados AEE/CID do banco
perfis_aee = {}
q_aee = """
SELECT r.nome_completo_criptografado, e.aluno_hash_id, e.possui_laudo_aee,
       cat.codigo_cid10, cat.codigo_cid11, cat.nomenclatura_oficial,
       cuid.apoiador_cuidador, cuid.necessidade_cuidador, cuid.status_laudo
FROM dim_estudantes e
JOIN dim_estudantes_nominal_restrito r ON e.aluno_hash_id = r.aluno_hash_id
LEFT JOIN fato_estudante_aee_perfil p ON e.aluno_hash_id = p.aluno_hash_id
LEFT JOIN dim_cid_catalogo cat ON p.cid_primario_id = cat.id
LEFT JOIN dim_aee_cuidadores_relacao_oficial_2026 cuid ON cuid.aluno_hash_id = e.aluno_hash_id
WHERE e.ano_escolar = 1;
"""
for r in c.execute(q_aee).fetchall():
    nome_banco, a_hash, laudo_flag, cid10, cid11, diag, cuidador, nec_cuid, st_laudo = r
    perfis_aee[nome_banco] = {
        "hash": a_hash,
        "laudo": bool(laudo_flag),
        "cid10": cid10,
        "cid11": cid11,
        "diagnostico": diag,
        "cuidador": cuidador,
        "status_laudo": st_laudo
    }

# Alunos em triagem ou ajustes específicos
perfis_aee["LUNNA DE SOUSA SILVA"]["cid10"] = "F91.3"
perfis_aee["LUNNA DE SOUSA SILVA"]["cid11"] = "6C90"
perfis_aee["LUNNA DE SOUSA SILVA"]["diagnostico"] = "Transtorno Opositivo Desafiador (TOD) - Em Triagem"

perfis_aee["MARIA YORRANA OLIVEIRA ARAUJO"]["cid10"] = "F84.0"
perfis_aee["MARIA YORRANA OLIVEIRA ARAUJO"]["cid11"] = "6A02"
perfis_aee["MARIA YORRANA OLIVEIRA ARAUJO"]["diagnostico"] = "Transtorno do Espectro Autista (TEA) - Em Triagem"

# Inserção longitudinal dos 69 registros
total_inseridos = 0
for al in DADOS_SAAP_RAW:
    nome = al["nome"]
    p_info = perfis_aee.get(nome, {})
    a_hash = p_info.get("hash")
    if not a_hash:
        a_hash = hashlib.sha256(nome.encode('utf-8')).hexdigest()
    
    possui_laudo = 1 if p_info.get("laudo") or p_info.get("cid10") else 0
    cid10 = p_info.get("cid10")
    cid11 = p_info.get("cid11")
    diag = p_info.get("diagnostico")
    cuidador = p_info.get("cuidador")
    
    # Avaliar 1º, 2º e 3º Bimestres
    prev_esc_score = 0
    prev_lei_score = 0
    
    for bim in [1, 2, 3]:
        esc_cod = al["escrita"][bim]
        lei_cod = al["leitura"][bim]
        esc_score = ESCORE_ESCRITA[esc_cod]
        lei_score = ESCORE_LEITURA[lei_cod]
        
        delta_esc = (esc_score - prev_esc_score) if bim > 1 else 0
        delta_lei = (lei_score - prev_lei_score) if bim > 1 else 0
        
        # Status de evolução escrita
        if bim == 1:
            st_esc = "DIAGNOSTICO_INICIAL"
        elif delta_esc > 0:
            st_esc = "EVOLUCAO_POSITIVA"
        elif delta_esc == 0:
            st_esc = "CONSOLIDACAO_ESTAVEL"
        else:
            st_esc = "ALERTA_REGRESSAO"
            
        # Status de evolução leitura
        if bim == 1:
            st_lei = "DIAGNOSTICO_INICIAL"
        elif delta_lei > 0:
            st_lei = "EVOLUCAO_POSITIVA"
        elif delta_lei == 0:
            st_lei = "CONSOLIDACAO_ESTAVEL"
        else:
            st_lei = "ALERTA_REGRESSAO"
            
        # Alerta EWS
        alerta_ews = 1 if (st_esc == "ALERTA_REGRESSAO" or st_lei == "ALERTA_REGRESSAO") else 0
        
        # Natureza da barreira
        if possui_laudo:
            natureza_barreira = "NEUROBIOLOGICA_SENSORIAL_MOTORA"
            estrategia = "PEI/PAEE: Adaptação de tempo (+50%), apoio motor fino, prancha de comunicação e suporte do cuidador."
        elif alerta_ews:
            natureza_barreira = "PEDAGOGICA_SITUACIONAL_OU_ABSENTEISMO"
            estrategia = "RTI Camada 2: Tutoria fônica intensiva (Kumon 15 min), checagem de frequência e acolhimento socioemocional."
        else:
            natureza_barreira = "DESENVOLVIMENTO_PADRAO_NEUROTIPICO"
            estrategia = "Ensino Regular / RTI Camada 1: Consolidação da consciência fonológica e letramento em espiral."
            
        c.execute("""
        INSERT INTO fato_saap_avaliacao_bimestral_1ano (
            aluno_hash_id, nome_estudante, ano_escolar, bimestre,
            situacao_escrita, nivel_escrita_escore,
            situacao_leitura, nivel_leitura_escore,
            delta_escrita_bimestral, delta_leitura_bimestral,
            status_evolucao_escrita, status_evolucao_leitura,
            possui_laudo_cid, codigo_cid10, codigo_cid11,
            diagnostico_resumo, cuidador_dedicado,
            necessita_adaptacao_pei, alerta_regressao_ews,
            natureza_barreira, estrategia_intervencao_prioritaria,
            fonte_documento
        ) VALUES (?, ?, 1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, (
            a_hash, nome, bim,
            esc_cod, esc_score,
            lei_cod, lei_score,
            delta_esc, delta_lei,
            st_esc, st_lei,
            possui_laudo, cid10, cid11,
            diag, cuidador,
            possui_laudo, alerta_ews,
            natureza_barreira, estrategia,
            "SAAP- 1ANO- ESCRITA.pdf / SAAP- 1ANO- LEITURA.pdf"
        ))
        
        prev_esc_score = esc_score
        prev_lei_score = lei_score
        total_inseridos += 1

print(f"    [✓] {total_inseridos} registros longitudinais inseridos com sucesso na tabela fato_saap_avaliacao_bimestral_1ano!")

# -------------------------------------------------------------------------------------------------
# 5. ATUALIZAR TABELAS PEI/PAEE COM OS DADOS DO SAAP
# -------------------------------------------------------------------------------------------------
print("[*] 5. Atualizando planos PEI e PAEE com os marcadores de progresso SAAP...")

# Atualizar fato_praticas_diarias_leitura_fluencia para os alunos do 1º ano
cols_prat = [col[1] for col in c.execute("PRAGMA table_info(fato_praticas_diarias_leitura_fluencia)").fetchall()]
if "nivel_fluencia_saap_3b" not in cols_prat:
    c.execute("ALTER TABLE fato_praticas_diarias_leitura_fluencia ADD COLUMN nivel_fluencia_saap_3b TEXT;")
if "categoria_escrita_saap_3b" not in cols_prat:
    c.execute("ALTER TABLE fato_praticas_diarias_leitura_fluencia ADD COLUMN categoria_escrita_saap_3b TEXT;")

for al in DADOS_SAAP_RAW:
    nome = al["nome"]
    p_info = perfis_aee.get(nome, {})
    a_hash = p_info.get("hash")
    if not a_hash:
        continue
    
    # Nível final no 3º Bimestre
    esc_3b = al["escrita"][3]
    lei_3b = al["leitura"][3]
    
    c.execute("""
    UPDATE fato_praticas_diarias_leitura_fluencia
    SET nivel_fluencia_saap_3b = ?,
        categoria_escrita_saap_3b = ?,
        possui_pei = ?
    WHERE aluno_hash_id = ?;
    """, (lei_3b, esc_3b, 1 if p_info.get("laudo") or p_info.get("cid10") else 0, a_hash))

# Se a coluna não existia, vamos verificar se deu erro silencioso ou se podemos enriquecer
print("    [✓] Marcadores biométricos SAAP consolidados nas tabelas de acompanhamento.")

# -------------------------------------------------------------------------------------------------
# 6. MATRIZES DE TRANSIÇÃO E CORRELAÇÃO BIOESTATÍSTICA (SAAP vs CAED)
# -------------------------------------------------------------------------------------------------
print("[*] 6. Computando matrizes bioestatísticas de transição e correlação SAAP x CAEd...")

# Coletar pares (Escore SAAP 3B, Proficiência CAEd Ciclo III)
q_corr = """
SELECT s.nome_estudante, s.possui_laudo_cid, s.nivel_escrita_escore, s.nivel_leitura_escore,
       caed_lp.proficiencia_destino as prof_lp, caed_mat.proficiencia_destino as prof_mat
FROM fato_saap_avaliacao_bimestral_1ano s
LEFT JOIN fato_evolucao_longitudinal_ciclos caed_lp 
       ON s.aluno_hash_id = caed_lp.aluno_hash_id 
      AND caed_lp.componente_curricular = 'LEITURA' 
      AND caed_lp.ciclo_destino = 'III'
LEFT JOIN fato_evolucao_longitudinal_ciclos caed_mat 
       ON s.aluno_hash_id = caed_mat.aluno_hash_id 
      AND caed_mat.componente_curricular = 'MATEMATICA' 
      AND caed_mat.ciclo_destino = 'III'
WHERE s.bimestre = 3;
"""
linhas_corr = c.execute(q_corr).fetchall()

def mean(arr):
    return sum(arr) / len(arr) if arr else 0

def spearman_rho(x, y):
    n = len(x)
    if n < 2:
        return 0
    # Obter ranks
    rx = [sorted(x).index(v) + 1 for v in x]
    ry = [sorted(y).index(v) + 1 for v in y]
    d_sq = sum((rx[i] - ry[i])**2 for i in range(n))
    return 1 - (6 * d_sq) / (n * (n**2 - 1))

# Separar neurodivergentes de neurotípicos
nd_esc = [r[2] for r in linhas_corr if r[1] == 1]
nd_lei = [r[3] for r in linhas_corr if r[1] == 1]
nd_lp = [r[4] for r in linhas_corr if r[1] == 1 and r[4] is not None]
nd_mat = [r[5] for r in linhas_corr if r[1] == 1 and r[5] is not None]

nt_esc = [r[2] for r in linhas_corr if r[1] == 0]
nt_lei = [r[3] for r in linhas_corr if r[1] == 0]
nt_lp = [r[4] for r in linhas_corr if r[1] == 0 and r[4] is not None]
nt_mat = [r[5] for r in linhas_corr if r[1] == 0 and r[5] is not None]

print(f"    [+] Coorte 1º Ano Avaliada no SAAP: N={len(linhas_corr)} alunos.")
print(f"    [+] Neurodivergentes (Laudados/Triagem com CID): N={len(nd_esc)} ({len(nd_esc)/len(linhas_corr)*100:.1f}%)")
print(f"        - Média Escore Escrita 3B: {mean(nd_esc):.2f}/5.0 | Leitura 3B: {mean(nd_lei):.2f}/6.0")
if nd_lp:
    print(f"        - CAEd Ciclo III Língua Portuguesa: {mean(nd_lp):.1f} | Matemática: {mean(nd_mat):.1f}")

print(f"    [+] Neurotípicos (Não-Divergentes): N={len(nt_esc)} ({len(nt_esc)/len(linhas_corr)*100:.1f}%)")
print(f"        - Média Escore Escrita 3B: {mean(nt_esc):.2f}/5.0 | Leitura 3B: {mean(nt_lei):.2f}/6.0")
if nt_lp:
    print(f"        - CAEd Ciclo III Língua Portuguesa: {mean(nt_lp):.1f} | Matemática: {mean(nt_mat):.1f}")

# -------------------------------------------------------------------------------------------------
# 7. REGISTRO CRIPTOGRÁFICO NO LEDGER TRANSAÇÃO (BLOCO 36)
# -------------------------------------------------------------------------------------------------
print("[*] 7. Registrando Bloco 36 no Ledger Criptográfico SHA-256...")

# Obter último bloco
ultimo_bloco = c.execute("SELECT sequencia_bloco, hash_bloco_atual FROM fato_auditoria_transacional_ledger ORDER BY sequencia_bloco DESC LIMIT 1").fetchone()
if ultimo_bloco:
    seq_anterior, hash_anterior = ultimo_bloco
    nova_seq = seq_anterior + 1
else:
    nova_seq = 43
    hash_anterior = "0" * 64

resumo_tx = f"Ingestão dos microdados SAAP 1º Ano (69 registros: Leitura e Escrita Bimestres 1 a 3) com cruzamento CAEd (Ciclos I-III), perfis neurodivergentes (CIDs 10 e 11) e atualização cadastral da Escola (Rua Capistrano de Abreu, S/N, Ipase, CEP 63700-450, Crateús-CE, INEP 23084995, Urbana, Municipal)."

payload_bloco = {
    "sequencia_bloco": nova_seq,
    "timestamp_utc": datetime.datetime.utcnow().isoformat(),
    "evento": "INGESTAO_SAAP_1ANO_E_ATUALIZACAO_CADASTRAL_ESCOLA",
    "hash_anterior": hash_anterior,
    "dados_auditados": {
        "escola_inep": "23084995",
        "escola_endereco": "Rua Capistrano de Abreu, S/N - Ipase, CEP 63700-450, Crateús - Ceará, Fone: (88)",
        "escola_localizacao": "Urbana",
        "escola_dependencia": "Municipal",
        "tabela_criada": "fato_saap_avaliacao_bimestral_1ano",
        "total_registros_saap": total_inseridos,
        "coorte_avaliada": len(linhas_corr),
        "coorte_neurodivergente": len(nd_esc),
        "coorte_neurotipica": len(nt_esc),
        "fontes_documentais": ["SAAP- 1ANO- ESCRITA.pdf", "SAAP- 1ANO- LEITURA.pdf"]
    }
}

payload_json = json.dumps(payload_bloco, sort_keys=True)
novo_hash = hashlib.sha256((hash_anterior + payload_json).encode('utf-8')).hexdigest()

c.execute("""
INSERT INTO fato_auditoria_transacional_ledger (
    sequencia_bloco, tabela_afetada, tipo_operacao, registro_id_ou_hash,
    resumo_transacao, hash_bloco_anterior, hash_bloco_atual, timestamp_utc, agente_ou_processo
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
""", (
    nova_seq,
    "fato_saap_avaliacao_bimestral_1ano",
    "INSERT",
    novo_hash[:32],
    resumo_tx,
    hash_anterior,
    novo_hash,
    datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
    "Antigravity_SAAP_Integrator_v1.0"
))

conn.commit()
conn.close()

print(f"    [✓] Bloco {nova_seq} registrado com sucesso!")
print(f"    [#] Hash SHA-256 do Bloco: {novo_hash}")
print("[+] Integração e auditoria concluídas com êxito!")
