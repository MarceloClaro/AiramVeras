"""Contrato de execução e rastreabilidade com metadados sintéticos."""
import copy
import hashlib
import importlib.util
import json

import pytest


def writer():
    assert importlib.util.find_spec("airam") is not None, "API de recibos ainda ausente"
    from airam import recibos
    function = getattr(recibos, "gravar_recibo", None)
    assert callable(function), "API gravar_recibo ainda ausente"
    return function


@pytest.fixture
def payload():
    return {
        "incremento": "T01", "requisitos": ["R01", "R21"], "testes": ["T01", "T53"],
        "estado": "GREEN", "comando": ["python", "-m", "pytest"],
        "timestamp": "2026-10-22T12:00:00+00:00", "codigo_saida": 0,
        "hashes_codigo": {"airam/catalogo.py": "a" * 64},
        "hashes_dados": {"fonte_sintetica": "b" * 64}, "versoes": {"python": "3.12"},
        "mutacao": None, "artefatos": [{"caminho": "stdout.txt", "sha256": "c" * 64}],
        "limites": ["Teste de software com fixture sintetica"], "executor": "Codex",
    }


def test_recibo_persiste_payload_e_hash_real(tmp_path, payload):
    original = copy.deepcopy(payload)
    target = tmp_path / "evidencias/recibo.json"
    digest = writer()(target, payload)
    assert json.loads(target.read_text(encoding="utf-8")) == original
    assert payload == original
    assert digest == hashlib.sha256(target.read_bytes()).hexdigest()


@pytest.mark.parametrize("field", ["requisitos", "testes", "artefatos", "hashes_codigo", "hashes_dados"])
def test_t53_recibo_sem_rastreabilidade_rejeitado(tmp_path, payload, field):
    del payload[field]
    target = tmp_path / "recibo.json"
    with pytest.raises(ValueError, match="rastreabilidade"):
        writer()(target, payload)
    assert not target.exists()


def test_recibo_nao_aceita_dados_nominais(tmp_path, payload):
    payload["alunos"] = [{"nome": "PESSOA_SINTETICA"}]
    with pytest.raises(ValueError, match="campo"):
        writer()(tmp_path / "recibo.json", payload)


def test_green_com_codigo_falha_nao_e_validado(tmp_path, payload):
    payload["codigo_saida"] = 1
    with pytest.raises(ValueError, match="estado"):
        writer()(tmp_path / "recibo.json", payload)


def test_hash_invalido_nao_e_recibo_rastreavel(tmp_path, payload):
    payload["hashes_dados"] = {"fonte": "invalido"}
    with pytest.raises(ValueError, match="hash"):
        writer()(tmp_path / "recibo.json", payload)
