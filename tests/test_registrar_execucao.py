"""Executa o coletor real em workspace temporário com testes sintéticos."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest


@pytest.mark.parametrize("stage,passing,expected_state,expected_code", [
    ("GREEN_FIX1_HELPER", False, "VERIFICACAO_FALHOU", 1),
    ("REFACTOR_FIX1_HELPER", False, "VERIFICACAO_FALHOU", 1),
    ("RED_FIX1_HELPER", False, "RED", 1),
    ("GREEN_FIX1_HELPER", True, "GREEN", 0),
])
def test_resumo_do_coletor_reflete_estado_efetivo(tmp_path, stage, passing, expected_state, expected_code):
    root = Path(__file__).resolve().parents[1]
    helper = tmp_path / "evidencias/T01/registrar_execucao.py"
    helper.parent.mkdir(parents=True)
    shutil.copyfile(root / "evidencias/T01/registrar_execucao.py", helper)
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_catalogo.py").write_text(f"def test_fixture_sintetica():\n    assert {passing!r}\n", encoding="utf-8")
    result = subprocess.run([sys.executable, str(helper), stage, "-q"], cwd=tmp_path,
                            capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "PYTHONUTF8": "1"})
    assert result.returncode == expected_code
    assert not result.stderr
    summary = json.loads(result.stdout)
    receipt = json.loads((helper.parent / f"{stage.lower()}-recibo.json").read_text(encoding="utf-8"))
    assert summary["estado"] == expected_state
    assert summary["estado"] == receipt["estado"]
    assert summary["codigo_saida"] == receipt["codigo_saida"] == expected_code
