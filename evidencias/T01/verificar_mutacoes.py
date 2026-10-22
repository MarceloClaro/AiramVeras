"""Executa duas mutações em cópias temporárias, sem alterar o produto."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parents[2]
source = (root / "airam/catalogo.py").read_text(encoding="utf-8")
mutations = [
    ("hash_removido", "if not resolved.is_file() or _sha256(resolved) != expected_sha256.lower():", "if not resolved.is_file():", "test_t01_rejeita_byte_alterado"),
    ("zip_raiz_removida", 'if name.startswith("/") or ".." in parts or ":" in name or stat.S_ISLNK(info.external_attr >> 16):', "if False:", "test_zip_escape_rejeitado_sem_extrair"),
]
results = []
for identifier, old, new, test in mutations:
    assert source.count(old) == 1
    with tempfile.TemporaryDirectory(prefix="airam-mutacao-") as directory:
        workspace = Path(directory)
        shutil.copytree(root / "airam", workspace / "airam", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(root / "tests", workspace / "tests", ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copytree(root / "config", workspace / "config")
        (workspace / "airam/catalogo.py").write_text(source.replace(old, new), encoding="utf-8")
        command = [sys.executable, "-m", "pytest", f"tests/test_catalogo.py::{test}", "-q"]
        result = subprocess.run(command, cwd=workspace, capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONUTF8": "1"})
        log = root / f"evidencias/T01/mutacao-{identifier}-stdout.txt"
        log.write_text(result.stdout, encoding="utf-8")
        assert result.returncode == 1 and "1 failed" in result.stdout and not result.stderr, "Mutacao nao foi morta por falha funcional"
        results.append({"id": identifier, "teste": test, "codigo_saida": result.returncode, "morta": True, "artefato": log.relative_to(root).as_posix(), "sha256": hashlib.sha256(log.read_bytes()).hexdigest()})
assert (root / "airam/catalogo.py").read_text(encoding="utf-8") == source
summary = {"timestamp": datetime.now(timezone.utc).isoformat(), "comando": [".venv/Scripts/python.exe", "evidencias/T01/verificar_mutacoes.py"], "codigo_saida": 0, "mutacoes": results, "produto_preservado": True, "limite": "Duas mutacoes direcionadas; nao e cobertura exaustiva de mutacao."}
(root / "evidencias/T01/mutacoes-recibo.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"mutacoes_mortas": len(results), "produto_preservado": True}))
