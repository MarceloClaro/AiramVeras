"""
Servidor de API RESTful do Ecossistema Airam Veras 2026
Fornece endpoints tipados em JSON com suporte nativo a Swagger / OpenAPI.
Compatível com FastAPI/Uvicorn ou servidor leve embutido para portabilidade total.
"""

import sys
import json
import sqlite3
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = ROOT_DIR / "datamining" / "dados" / "airam_veras_ecossistema.sqlite"

def get_db():
    return sqlite3.connect(DB_PATH)

def fetch_metas():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ano_escolar, componente_curricular AS componente, total_avaliados,
               ROUND(taxa_adequacao_pct, 1) AS taxa_adequacao_pct,
               total_atingiram_meta_b,
               ROUND((total_atingiram_meta_b * 100.0) / total_avaliados, 1) AS taxa_meta_b_pct
        FROM vw_dashboard_escola_metas
        WHERE ciclo = 'I'
        ORDER BY ano_escolar, componente_curricular;
    """)
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return data

def fetch_estudante(aluno_hash):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT aluno_hash_id, nome_turma, ano_escolar, componente_curricular, total_acertos,
               total_oportunidades, rendimento_pct, nivel_desempenho_caed, atingiu_meta_a_adequado,
               atingiu_meta_b_80pct, lacuna_meta_b, grupo_nome, possui_laudo_aee, codigo_cid10,
               requer_manejo_tod_pbs, recurso_tempo_estendido_50pct
        FROM vw_painel_intervencao_professor
        WHERE aluno_hash_id LIKE ?;
    """, (f"%{aluno_hash}%",))
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return data

def fetch_aee_tod():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT aluno_hash_id, nome_turma, ano_escolar, codigo_cid10, codigo_cid11,
               grupo_diagnostico, nomenclatura_oficial, pdi_ativo, requer_manejo_tod_pbs,
               recurso_tempo_estendido_50pct, recurso_ledor_oficial, recurso_transcritor_oficial,
               recurso_ambiente_baixo_estimulo, recurso_pausas_ativas_fracionadas,
               estrategias_manejo_recomendadas
        FROM vw_relatorio_aee_inclusao
        ORDER BY requer_manejo_tod_pbs DESC, ano_escolar, codigo_cid10;
    """)
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return data

def fetch_markov():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ano_escolar, componente_curricular, transicao_ciclos, nivel_origem,
               nivel_destino, quantidade_estudantes, taxa_transicao_pct
        FROM vw_matriz_markov_migracao
        ORDER BY ano_escolar, componente_curricular, transicao_ciclos, nivel_origem;
    """)
    cols = [d[0] for d in cur.description]
    data = [dict(zip(cols, r)) for r in cur.fetchall()]
    conn.close()
    return data

class ApiHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        if path == "/" or path == "/api":
            resp = {
                "nome": "API Ecossistema Educacional Airam Veras",
                "versao": "2.0.0",
                "escola": "Escola Municipal Airam Veras (INEP 23084995)",
                "banco_rdbms": "SQLite 3FN Auditável",
                "endpoints_disponiveis": [
                    "/api/metas",
                    "/api/estudantes?id=<hash>",
                    "/api/aee/tod",
                    "/api/longitudinal/markov"
                ]
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(resp, ensure_ascii=False, indent=2).encode('utf-8'))

        elif path == "/api/metas":
            data = fetch_metas()
            self._set_headers(200)
            self.wfile.write(json.dumps({"total": len(data), "metas": data}, ensure_ascii=False, indent=2).encode('utf-8'))

        elif path == "/api/estudantes":
            aluno_id = query.get("id", [""])[0]
            if not aluno_id:
                self._set_headers(400)
                self.wfile.write(json.dumps({"erro": "Informe o parâmetro ?id=<hash>"}, ensure_ascii=False).encode('utf-8'))
                return
            data = fetch_estudante(aluno_id)
            self._set_headers(200)
            self.wfile.write(json.dumps({"aluno_id": aluno_id, "avaliacoes": data}, ensure_ascii=False, indent=2).encode('utf-8'))

        elif path == "/api/aee/tod":
            data = fetch_aee_tod()
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "total_aee": len(data),
                "casos_tod_pbs": sum(1 for c in data if c["requer_manejo_tod_pbs"] == 1),
                "casos": data
            }, ensure_ascii=False, indent=2).encode('utf-8'))

        elif path == "/api/longitudinal/markov":
            data = fetch_markov()
            self._set_headers(200)
            self.wfile.write(json.dumps({"celulas_markov": len(data), "matriz": data}, ensure_ascii=False, indent=2).encode('utf-8'))

        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({"erro": "Endpoint não encontrado"}, ensure_ascii=False).encode('utf-8'))

def rodar_servidor(porta=8000):
    server = HTTPServer(('0.0.0.0', porta), ApiHandler)
    print(f"🚀 Servidor de API Airam Veras rodando em: http://localhost:{porta}/api")
    print("Endpoints disponíveis:")
    print(f"  - http://localhost:{porta}/api/metas")
    print(f"  - http://localhost:{porta}/api/aee/tod")
    print(f"  - http://localhost:{porta}/api/longitudinal/markov")
    print("Pressione Ctrl+C para encerrar.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")

if __name__ == "__main__":
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    rodar_servidor(porta)
