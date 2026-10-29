"""
Transcrição e validação estrita dos dados oficiais do SAAP 1º ANO 2026:
- SAAP- 1ANO- ESCRITA.pdf (2 páginas)
- SAAP- 1ANO- LEITURA.pdf (2 páginas)
"""

# Mapeamento oficial dos 23 alunos avaliados no SAAP 1º Ano:
# Níveis de Escrita:
# PRE: Pré-Silábico (escore 1)
# SIL: Silábico (escore 2)
# SIL_ALF: Silábico-Alfabético (escore 3)
# ALF: Alfabético (escore 4)
# ORT: Ortográfico (escore 5)

# Níveis de Leitura:
# NL: Não Leitor (escore 1)
# LS: Leitor de Sílabas (escore 2)
# LP: Leitor de Palavras (escore 3)
# LF: Leitor de Frases (escore 4)
# LTSF: Leitor de Texto Sem Fluência (escore 5)
# LTF: Leitor de Texto com Fluência (escore 6)

DADOS_SAAP_1ANO = [
    {
        "nome": "ANTONIO CALLEBY PEREIRA LIMA",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "ALF"},
        "leitura": {"1B": "NL", "2B": "LP", "3B": "LF"}
    },
    {
        "nome": "DANIEL CONCEICAO PIMENTEL",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL_ALF"},
        "leitura": {"1B": "NL", "2B": "LP", "3B": "LS"}
    },
    {
        "nome": "EMANUELLY DO NASCIMENTO BEZERRA",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "ALF"},
        "leitura": {"1B": "NL", "2B": "LP", "3B": "LF"}
    },
    {
        "nome": "FRANCISCA ADILA CAXIAS DE ALMEIDA",
        "escrita": {"1B": "SIL_ALF", "2B": "SIL", "3B": "PRE"},
        "leitura": {"1B": "LS", "2B": "NL", "3B": "NL"}
    },
    {
        "nome": "FRANCISCO MIGUEL MARTINS DE SOUSA",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL_ALF"},
        "leitura": {"1B": "NL", "2B": "LS", "3B": "LS"}
    },
    {
        "nome": "GUSTAVO HENRIQUE MORENO DA SILVA",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "NL"}
    },
    {
        "nome": "GUSTAVO SALES MACHADO",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "LS"}
    },
    {
        "nome": "ISABELLA MARTINS FEITOSA",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "LS", "3B": "LS"}
    },
    {
        "nome": "ISAC LUCCA FERNANDES MARTINS",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "LS", "3B": "LS"}
    },
    {
        "nome": "ISIS GOMES MESQUITA",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "NL"}
    },
    {
        "nome": "ISIS KETLEN SOUSA DA SILVA",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "LS"}
    },
    {
        "nome": "JOSE YHUDY BENICIO FERREIRA DE ANDRADE",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "ALF"},
        "leitura": {"1B": "NL", "2B": "LP", "3B": "LF"}
    },
    {
        "nome": "LIVYA MARIA ALVES MELO",
        "escrita": {"1B": "SIL_ALF", "2B": "SIL", "3B": "ALF"},
        "leitura": {"1B": "LF", "2B": "LTSF", "3B": "LF"}
    },
    {
        "nome": "LUNNA DE SOUSA SILVA",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL_ALF"},
        "leitura": {"1B": "NL", "2B": "LP", "3B": "LF"}
    },
    {
        "nome": "MARIA AGATHA DE SOUSA NEVES",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "LS"}
    },
    {
        "nome": "MARIA ISIS DA CONCEICAO DE SOUSA",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "PRE"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "NL"}
    },
    {
        "nome": "MARIA ISIS PEREIRA GOMES",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "LP", "3B": "NL"}
    },
    {
        "nome": "MARIA JULIANA VIEIRA GOMES",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "SIL_ALF"},
        "leitura": {"1B": "NL", "2B": "LTSF", "3B": "LF"}
    },
    {
        "nome": "MARIA LETICIA MARTINS DA SILVA",
        "escrita": {"1B": "PRE", "2B": "SIL", "3B": "SIL"},
        "leitura": {"1B": "NL", "2B": "LTSF", "3B": "NL"}
    },
    {
        "nome": "MARIA SOPHIA MARQUES SILVA",
        "escrita": {"1B": "SIL_ALF", "2B": "ALF", "3B": "ALF"},
        "leitura": {"1B": "LF", "2B": "LTSF", "3B": "LTF"}
    },
    {
        "nome": "MARIA YORRANA OLIVEIRA ARAUJO",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "SIL_ALF"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "NL"}
    },
    {
        "nome": "MOISES TOLEDO DE SOUSA",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "SIL_ALF"},
        "leitura": {"1B": "NL", "2B": "NL", "3B": "LS"}
    },
    {
        "nome": "RUAN LUCAS DE SOUZA SALES",
        "escrita": {"1B": "PRE", "2B": "SIL_ALF", "3B": "SIL_ALF"},
        "leitura": {"1B": "NL", "2B": "LTSF", "3B": "NL"}
    }
]

print(f"Total de estudantes transcritos: {len(DADOS_SAAP_1ANO)}")
