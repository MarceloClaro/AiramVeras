import sqlite3
import json
from pathlib import Path

def main():
    db_path = Path("datamining/dados/airam_veras_ecossistema.sqlite")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Inspecionar tabelas e views
    tabelas = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;").fetchall()]
    views = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name;").fetchall()]

    print(f"Total Tabelas: {len(tabelas)}")
    print(f"Total Views  : {len(views)}")

    # Validar contagens
    contagens = {}
    for t in tabelas:
        c = cur.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
        contagens[t] = c
        print(f"  [TABELA] {t:<35}: {c} registros")

    print("\nValidando Views:")
    views_amostras = {}
    for v in views:
        rows = cur.execute(f"SELECT * FROM {v} LIMIT 2;").fetchall()
        cols = [d[0] for d in cur.description]
        views_amostras[v] = {
            "colunas": cols,
            "total_linhas": cur.execute(f"SELECT COUNT(*) FROM {v};").fetchone()[0],
            "exemplo": [dict(zip(cols, r)) for r in rows]
        }
        print(f"  [VIEW]   {v:<35}: {views_amostras[v]['total_linhas']} registros encontrados.")

    # Gerar Especificação OpenAPI 3.0 e Contratos de Dados para Frameworks
    contratos = {
        "openapi": "3.0.3",
        "info": {
            "title": "Ecossistema de Dados Escola Airam Veras - API Canônica",
            "version": "1.0.0",
            "description": "Especificação universal e tipada para integração de qualquer framework frontend (Next.js, React, Flutter, Vue) ou backend (FastAPI, NestJS, Spring, Django) com o banco de dados canônico e auditável da Escola Airam Veras.",
            "contact": {
                "name": "Equipe de Engenharia Pedagógica e Psicométrica",
                "url": "https://github.com/MarceloClaro/AiramVeras"
            }
        },
        "banco_metadados": {
            "rdbms": "SQLite 3 / Compatível com PostgreSQL 15+ e Supabase",
            "sha256": "ab2deee80342c0dfc0e77e7c0701f660c08f704a4c676f52203e5651ba3282cc",
            "tabelas_registradas": contagens,
            "views_analiticas": views_amostras
        },
        "schemas": {
            "Estudante": {
                "type": "object",
                "properties": {
                    "aluno_hash_id": {"type": "string", "example": "4ef09930f305f..."},
                    "ano_escolar": {"type": "integer", "enum": [1, 2, 3, 4, 5]},
                    "turma_id": {"type": "integer"},
                    "possui_laudo_aee": {"type": "boolean"},
                    "situacao_matricula": {"type": "string", "example": "Matriculado"}
                },
                "required": ["aluno_hash_id", "ano_escolar", "turma_id"]
            },
            "EscorePsicometrico": {
                "type": "object",
                "properties": {
                    "participacao_id": {"type": "integer"},
                    "total_acertos": {"type": "integer", "example": 19},
                    "total_oportunidades": {"type": "integer", "example": 22},
                    "taxa_rendimento_ponderada": {"type": "number", "example": 0.8636},
                    "theta_habilidade_latente": {"type": "number", "example": 1.4545},
                    "erro_padrao_theta": {"type": "number", "example": 0.28},
                    "proficiencia_escala_spaece": {"type": "number", "example": 272.7},
                    "nivel_desempenho_caed": {"type": "string", "enum": ["Abaixo do Básico", "Básico", "Adequado", "Avançado"]},
                    "atingiu_meta_a_adequado": {"type": "boolean", "example": True},
                    "atingiu_meta_b_80pct": {"type": "boolean", "example": True},
                    "lacuna_meta_b": {"type": "integer", "example": 0}
                }
            },
            "PerfilClinicoAEE": {
                "type": "object",
                "properties": {
                    "aluno_hash_id": {"type": "string"},
                    "cid10": {"type": "string", "example": "F91.3"},
                    "cid11": {"type": "string", "example": "6C90"},
                    "grupo_diagnostico": {"type": "string", "example": "TOD"},
                    "pdi_ativo": {"type": "boolean", "example": True},
                    "recurso_tempo_estendido_50pct": {"type": "boolean", "example": True},
                    "recurso_pausas_ativas_fracionadas": {"type": "boolean", "example": True},
                    "requer_manejo_tod_pbs": {"type": "boolean", "example": True},
                    "observacoes_clinico_pedagogicas": {"type": "string"}
                }
            },
            "DiagnosticoMetas": {
                "type": "object",
                "properties": {
                    "ano_escolar": {"type": "integer", "example": 3},
                    "componente": {"type": "string", "example": "LEITURA"},
                    "total_estudantes": {"type": "integer", "example": 32},
                    "taxa_adequacao_pct": {"type": "number", "example": 56.25},
                    "taxa_meta_b_80pct": {"type": "number", "example": 40.62},
                    "meta_a_atingida": {"type": "string", "example": "SIM (Meta A Superada)"},
                    "meta_b_atingida": {"type": "string", "example": "NÃO (Em Progressão)"}
                }
            }
        }
    }

    out_file = Path("datamining/dados/schema_api_contratos.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(contratos, f, indent=2, ensure_ascii=False)

    print(f"\nContrato de API e Schemas gravado em: {out_file}")

if __name__ == "__main__":
    main()
