"""Contraprova local de catálogo e proteção das fontes; só imprime agregados."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys

project = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project))
from airam.catalogo import catalogar
from airam.recibos import gravar_recibo

config = json.loads((project / "config/analise.json").read_text(encoding="utf-8"))
source_root = (project / config["raiz_fontes"]).resolve()
excluded = set(config["catalogo"]["excluir_diretorios"])


def independent_hashes():
    result = {}
    for folder, subdirs, names in os.walk(source_root, followlinks=False):
        subdirs[:] = [name for name in subdirs if name not in excluded]
        for name in names:
            path = Path(folder) / name
            with path.open("rb") as stream:
                result[path.relative_to(source_root).as_posix()] = hashlib.file_digest(stream, "sha256").hexdigest()
    return result


before = independent_hashes()
records = catalogar(source_root)
after = independent_hashes()
assert before == after, "Fontes originais mudaram"
assert {r["caminho"]: r["sha256"] for r in records} == before, "Hash do catalogo diverge da contraprova independente"
current = [r for r in records if r["caminho"].startswith("resultados-caed-ciclo-i-2026/")]
current_zips = [r for r in current if r["tipo"] == "zip"]
current_csvs = [r for r in current if r["tipo"] == "csv" and "/csv_originais/" in r["caminho"]]
assert len(current_zips) == 18
assert len(current_csvs) == 54
assert all(r["status"] == "verificada" for r in [*current_zips, *current_csvs])
historic = next(r for r in records if r["caminho"] == config["fontes"]["historico_matematica_1ano"]["caminho"])
assert historic["status"] == "incompativel"
assert historic["componente_observado"] == ["LINGUA PORTUGUESA"]
assert historic["avaliacao"] is None
# O shape publicado só permite contexto de fonte; não há campo de linhas/alunos.
approved = {"fonte_id", "caminho", "sha256", "tipo", "aliases", "programa", "avaliacao", "status", "incompatibilidade", "componente_observado", "anos_observados", "proveniencia", "origem", "licenca", "data_exportacao", "apta_para_mistura"}
assert all(set(record) == approved for record in records)
output = project / config["catalogo"]["saida"]
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
folder = project / "evidencias/T01"
hash_manifest = folder / "fontes-hashes.json"
hash_manifest.write_text(json.dumps(before, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "fontes": len(records),
           "fontes_preservadas": before == after, "contraprova_hashes": "hashlib.file_digest independente",
           "zip_atuais": len(current_zips), "csv_atuais": len(current_csvs),
           "status": dict(Counter(r["status"] for r in records)), "dados_nominais_no_schema": False,
           "limites": ["Nomes de arquivos e metadados de origem são conservados; nenhuma linha de aluno é publicada.",
                       "Validação documental local; não valida temporalidade nem resultados pedagógicos."]}
summary_path = folder / "fontes-resumo.json"
summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
receipt = {
    "incremento": "T01-fontes-reais", "requisitos": ["R01", "R21", "R24"],
    "testes": ["18_ZIP", "54_CSV", "HASHES_ANTES_DEPOIS", "HASHES_CONTRAPROVA", "COMPONENTE_HISTORICO"],
    "estado": "GREEN", "comando": [".venv/Scripts/python.exe", "evidencias/T01/validar_fontes_reais.py"],
    "timestamp": summary["timestamp"], "codigo_saida": 0,
    "hashes_codigo": {p.relative_to(project).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in [*project.glob("airam/*.py"), Path(__file__).resolve(), project / "config/analise.json"]},
    "hashes_dados": before, "versoes": {"python": sys.version}, "mutacao": None,
    "artefatos": [{"caminho": p.relative_to(project).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (output, hash_manifest, summary_path)],
    "limites": summary["limites"], "executor": "Codex local; sem dados enviados a servicos externos",
}
gravar_recibo(folder / "fontes-recibo.json", receipt)
print(json.dumps(summary, ensure_ascii=True))
