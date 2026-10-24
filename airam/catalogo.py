"""Catálogo de arquivos: metadados e hashes; nunca retorna linhas de estudantes."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import unicodedata
import zipfile


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _inside(path: Path, root: Path) -> Path:
    resolved = path.resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError("Caminho fora da raiz permitida")
    return resolved


def validar_fonte(path: Path, expected_sha256: str, allowed_root: Path) -> None:
    """Falha fechada para fonte fora da raiz ou hash diferente do esperado."""
    resolved = _inside(Path(path), Path(allowed_root))
    if not re.fullmatch(r"[0-9a-fA-F]{64}", expected_sha256 or ""):
        raise ValueError("Formato de hash SHA256 invalido")
    if not resolved.is_file() or _sha256(resolved) != expected_sha256.lower():
        raise ValueError("Fonte ausente ou hash SHA256 divergente")


def _normal(value: str) -> str:
    return " ".join("".join(c for c in unicodedata.normalize("NFKD", value.upper())
                            if not unicodedata.combining(c)).split())


def _csv_metadata(raw: bytes) -> dict:
    """Só conserva colunas de contexto. Nomes e respostas não saem deste leitor."""
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = raw.decode("cp1252")
    first = text.splitlines()[0] if text.splitlines() else ""
    delimiter = ";" if first.count(";") >= first.count(",") else ","
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    columns = {_normal(k): k for k in reader.fieldnames or []}
    components, years = set(), set()
    for row in reader:
        column = columns.get("COMPONENTE CURRICULAR") or columns.get("COMPONENTE")
        if column and row.get(column):
            components.add(_normal(row[column]))
        column = columns.get("ANO ESCOLAR")
        if column and row.get(column):
            match = re.search(r"([1-9])(?:[º°oO])?\s*ANO\b", row[column], flags=re.IGNORECASE)
            if match is None:
                match = re.fullmatch(r"([1-9])", row[column].strip())
            if match:
                years.add(int(match.group(1)))
    return {"componentes": sorted(components), "anos": sorted(years)}


def _safe_member(info: zipfile.ZipInfo) -> str:
    name = info.filename.replace("\\", "/")
    parts = PurePosixPath(name).parts
    if name.startswith("/") or ".." in parts or ":" in name or stat.S_ISLNK(info.external_attr >> 16):
        raise ValueError("Membro ZIP fora da raiz permitida")
    return name


def _archive_metadata(path: Path) -> tuple[dict, list[tuple[str, str]]]:
    components, years, members = set(), set(), []
    with zipfile.ZipFile(path) as archive:
        for info in archive.infolist():
            name = _safe_member(info)
            if info.is_dir() or not name.lower().endswith(".csv"):
                continue
            if info.file_size > 128 * 1024 * 1024:
                raise ValueError("Membro CSV excede limite local de leitura")
            raw = archive.read(info)
            metadata = _csv_metadata(raw)
            components.update(metadata["componentes"])
            years.update(metadata["anos"])
            members.append((name, hashlib.sha256(raw).hexdigest()))
    return {"componentes": sorted(components), "anos": sorted(years)}, members


def _configuration() -> dict:
    configured = os.environ.get("AIRAM_CONFIG")
    path = Path(configured) if configured else Path(__file__).resolve().parents[1] / "config/analise.json"
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.is_file() else {}


def _context(manifest: dict, entry: dict) -> dict | None:
    # A etiqueta de arquivo nunca preenche um ciclo ou data ausente.
    cycle = entry.get("ciclo", manifest.get("ciclo"))
    identifier = entry.get("avaliacao_id", manifest.get("avaliacao_id"))
    if not cycle or not identifier or not manifest.get("ano_avaliacao"):
        return None
    return {"avaliacao_id": identifier, "ano_avaliacao": manifest["ano_avaliacao"],
            "ciclo": cycle, "ano_escolar": entry.get("ano_escolar"),
            "componente": entry.get("componente")}


def _same_context(contexts: list[dict]) -> dict:
    unique = {json.dumps(c["avaliacao"], sort_keys=True, ensure_ascii=False) for c in contexts}
    if len(unique) != 1:
        raise ValueError("Proveniencia ambigua: mesmo conteudo em anos ou componentes distintos")
    return contexts[0]


def _component_family(value: str) -> str:
    value = _normal(value)
    return "LINGUA PORTUGUESA" if value in {"LEITURA", "LP", "PORTUGUES", "LINGUA PORTUGUESA"} else value


def _initial_status(kind: str, verified: bool) -> str:
    if verified:
        return "verificada"
    return {"pdf": "documental_nao_comparavel", "zip": "historica_nao_comparavel"}.get(kind, "avaliacao_nao_identificada")


def catalogar(root: Path) -> list[dict]:
    """Cataloga arquivos físicos sob root, validando manifestos e ZIPs sem extrair.

    CSVs extraídos só herdam contexto pelo hash de membro de um ZIP verificado.
    Fontes sem contexto comprovado permanecem bloqueadas para mistura de avaliações.
    """
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("A raiz do catalogo deve ser um diretorio")
    config = _configuration()
    excluded = set(config.get("catalogo", {}).get("excluir_diretorios", []))
    excluded_files = set(config.get("catalogo", {}).get("excluir_arquivos", []))
    files = []
    for directory, subdirs, filenames in os.walk(root, followlinks=False):
        subdirs[:] = sorted(d for d in subdirs if d not in excluded)
        for dirname in subdirs:
            _inside(Path(directory) / dirname, root)
        for name in sorted(filenames):
            path = Path(directory) / name
            if path.relative_to(root).as_posix() in excluded_files:
                continue
            _inside(path, root)
            files.append(path)
    files.sort(key=lambda p: p.relative_to(root).as_posix())
    hashes = {p: _sha256(p) for p in files}
    metadata, members = {}, {}
    for path in files:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            metadata[path] = _csv_metadata(path.read_bytes())
        elif suffix == ".zip":
            metadata[path], members[path] = _archive_metadata(path)
    direct, member_contexts = {}, {}
    for path in files:
        if path.name != "manifesto_coleta.json":
            continue
        manifest = json.loads(path.read_text(encoding="utf-8-sig"))
        for entry in manifest.get("exportacoes", []):
            if not entry.get("arquivo"):
                continue
            target = _inside(path.parent / entry["arquivo"], root)
            validar_fonte(target, entry.get("sha256", ""), root)
            context = _context(manifest, entry)
            if context is None:
                continue
            source = {"avaliacao": context, "programa": manifest.get("programa"),
                      "data_exportacao": manifest.get("data_coleta"),
                      "manifesto": path.relative_to(root).as_posix(),
                      "sha256_manifesto": hashes[path], "vinculo": "manifesto_sha256"}
            direct.setdefault(target, []).append(source)
            for member_name, digest in members.get(target, []):
                inherited = {**source, "vinculo": "sha256_membro_zip_verificado",
                             "zip": target.relative_to(root).as_posix(), "membro": member_name}
                member_contexts.setdefault(digest, []).append(inherited)
    aliases = config.get("fontes", {})
    records = []
    for path in files:
        relative = path.relative_to(root).as_posix()
        kind = path.suffix.lower().lstrip(".") or "sem_extensao"
        observed = metadata.get(path, {"componentes": [], "anos": []})
        candidates = direct.get(path, [])
        if not candidates and kind == "csv":
            candidates = member_contexts.get(hashes[path], [])
        source = _same_context(candidates) if candidates else None
        assessment = source["avaliacao"] if source else None
        status = _initial_status(kind, source is not None)
        issue = None
        expected = assessment.get("componente") if assessment else None
        label = _normal(path.stem)
        if not expected:
            expected = next((c for c in ("MATEMATICA", "LEITURA", "ESCRITA", "FLUENCIA") if c in label), None)
        if expected and observed["componentes"]:
            if any(_component_family(c) != _component_family(expected) for c in observed["componentes"]):
                issue = "componente declarado difere do conteudo observado"
                status = "incompativel"
        if assessment and assessment.get("ano_escolar") and observed["anos"]:
            if observed["anos"] != [assessment["ano_escolar"]]:
                issue = "ano escolar declarado difere do conteudo observado"
                status = "incompativel"
        aliases_for_path = sorted(k for k, v in aliases.items() if v.get("caminho") == relative)
        records.append({
            "fonte_id": "sha256:" + hashlib.sha256((relative + "\0" + hashes[path]).encode()).hexdigest(),
            "caminho": relative, "sha256": hashes[path], "tipo": kind, "aliases": aliases_for_path,
            "programa": source["programa"] if source else None, "avaliacao": assessment,
            "status": status, "incompatibilidade": issue,
            "componente_observado": observed["componentes"], "anos_observados": observed["anos"],
            "proveniencia": source, "origem": "arquivo_local", "licenca": "nao_declarada",
            "data_exportacao": source["data_exportacao"] if source else None,
            "apta_para_mistura": status == "verificada",
        })
    return records
