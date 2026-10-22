"""Recibos de execução de metadados, com validação antes da escrita atômica."""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
from pathlib import Path
import re
import tempfile
import os

_FIELDS = {"incremento", "requisitos", "testes", "estado", "comando", "timestamp", "codigo_saida",
           "hashes_codigo", "hashes_dados", "versoes", "mutacao", "artefatos", "limites", "executor"}


def _hash(value) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def gravar_recibo(path: Path, payload: dict) -> str:
    """Valida o contrato T53 e retorna SHA256 dos bytes gravados.

    O schema não aceita tabelas, alunos ou campos arbitrários. Texto livre deve conter
    apenas metadados minimizados; a revisão de sigilo continua obrigatória na entrega.
    """
    if not isinstance(payload, dict) or _FIELDS - payload.keys():
        raise ValueError("Recibo sem rastreabilidade obrigatoria")
    if payload.keys() - _FIELDS:
        raise ValueError("Recibo possui campo nao autorizado")
    for key in ("incremento", "requisitos", "testes", "comando", "hashes_codigo", "hashes_dados", "versoes", "artefatos", "limites", "executor"):
        if not payload[key]:
            raise ValueError("Recibo sem rastreabilidade obrigatoria")
    for key in ("requisitos", "testes", "comando", "limites"):
        if not isinstance(payload[key], list) or not all(isinstance(v, str) and v for v in payload[key]):
            raise ValueError("Recibo sem rastreabilidade: lista de metadados invalida")
    for key in ("hashes_codigo", "hashes_dados"):
        if not isinstance(payload[key], dict) or not all(isinstance(k, str) and _hash(v) for k, v in payload[key].items()):
            raise ValueError("Recibo com hash invalido")
    if not isinstance(payload["versoes"], dict):
        raise ValueError("Recibo sem rastreabilidade de versoes")
    if not isinstance(payload["artefatos"], list):
        raise ValueError("Recibo sem rastreabilidade de artefatos")
    for artifact in payload["artefatos"]:
        if not isinstance(artifact, dict) or set(artifact) != {"caminho", "sha256"} or not isinstance(artifact["caminho"], str) or not artifact["caminho"] or not _hash(artifact["sha256"]):
            raise ValueError("Recibo com artefato/hash invalido")
    if not isinstance(payload["incremento"], str) or not isinstance(payload["executor"], str):
        raise ValueError("Recibo sem rastreabilidade do executor")
    if payload["mutacao"] is not None and not isinstance(payload["mutacao"], str):
        raise ValueError("Campo mutacao invalido")
    try:
        timestamp = datetime.fromisoformat(payload["timestamp"])
        if timestamp.tzinfo is None:
            raise ValueError
    except (TypeError, ValueError):
        raise ValueError("Timestamp deve incluir fuso horario") from None
    state, code = payload["estado"], payload["codigo_saida"]
    if type(code) is not int or state not in {"RED", "GREEN", "REFACTOR"}:
        raise ValueError("Recibo com estado/codigo invalido")
    if (state == "RED" and code == 0) or (state in {"GREEN", "REFACTOR"} and code != 0):
        raise ValueError("Recibo contradiz estado da execucao")
    raw = (json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode("utf-8")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(raw)
        os.replace(temporary, path)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
    return hashlib.sha256(raw).hexdigest()
