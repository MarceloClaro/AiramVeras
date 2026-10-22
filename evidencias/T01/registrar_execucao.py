"""Registra uma execução real local; não reconstitui fases anteriores."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[2]
stage = sys.argv[1]
state = stage.split("_", 1)[0]
command = [sys.executable, "-m", "pytest", *sys.argv[2:]]
result = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})
folder = root / "evidencias" / "T01"
stdout = folder / f"{stage.lower()}-stdout.txt"
stderr = folder / f"{stage.lower()}-stderr.txt"
stdout.write_text(result.stdout, encoding="utf-8")
stderr.write_text(result.stderr, encoding="utf-8")
code_paths = [*root.glob("airam/*.py"), *root.glob("tests/*.py"), *root.glob("config/*.json")]
hashes = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(code_paths)}
versions = {"python": sys.version, "plataforma": sys.platform}
from importlib.metadata import version
versions["pytest"] = version("pytest")
receipt = {
    "incremento": "T01", "requisitos": ["R01", "R21", "R22", "R24"],
    "testes": ["T01", "T02", "T03", "T53", "ZIP_RAIZ"], "estado": state,
    "comando": [".venv/Scripts/python.exe", "-m", "pytest", *sys.argv[2:]],
    "timestamp": datetime.now(timezone.utc).isoformat(), "codigo_saida": result.returncode,
    "hashes_codigo": hashes, "hashes_dados": {"fixtures_sinteticas": hashlib.sha256((root / "tests/test_catalogo.py").read_bytes()).hexdigest()},
    "versoes": versions, "mutacao": None,
    "artefatos": [{"caminho": p.relative_to(root).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in (stdout, stderr)],
    "limites": ["Fixtures sinteticas; verificacao de fontes reais registrada separadamente."],
    "executor": "Codex executor local; perfil Core nao representa execucao",
}
if state in {"GREEN", "REFACTOR"} and result.returncode != 0:
    receipt["estado"] = "VERIFICACAO_FALHOU"
    receipt["fase_solicitada"] = stage
(folder / f"{stage.lower()}-recibo.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"estado": stage, "codigo_saida": result.returncode, "stdout": stdout.relative_to(root).as_posix(), "resumo": result.stdout.splitlines()[-1:]}, ensure_ascii=False))
sys.exit(result.returncode)
