"""Fixtures sintéticas; nenhuma observação escolar nominal é usada nestes testes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import zipfile

import pytest


def api(name):
    # A ausência da API é uma falha funcional controlada, sem erro de coleta/import.
    assert importlib.util.find_spec("airam") is not None, "API de catálogo ainda ausente"
    from airam import catalogo
    function = getattr(catalogo, name, None)
    assert callable(function), f"API {name} ainda ausente"
    return function


def csv_source(path, component="MATEMÁTICA"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(f"Ano Escolar;Componente Curricular;Nome\n1º ANO;{component};PESSOA_SINTETICA\n".encode("utf-8"))
    return path


def manifest(root, filename, digest):
    (root / "manifesto_coleta.json").write_text(json.dumps({
        "programa": "CNCA", "ciclo": "I", "ano_avaliacao": 2026,
        "avaliacao_id": "AV12026", "data_coleta": "2026-10-22",
        "exportacoes": [{"arquivo": filename, "sha256": digest, "status": "baixado",
                         "ano_escolar": 1, "componente": "MATEMATICA"}]
    }), encoding="utf-8")


def test_t01_rejeita_byte_alterado(tmp_path):
    source = csv_source(tmp_path / "fonte.csv")
    original_hash = hashlib.sha256(source.read_bytes()).hexdigest()
    api("validar_fonte")(source, original_hash, tmp_path)
    source.write_bytes(source.read_bytes() + b"x")
    with pytest.raises(ValueError, match="hash"):
        api("validar_fonte")(source, original_hash, tmp_path)


def test_validar_fonte_rejeita_fora_da_raiz(tmp_path):
    allowed = tmp_path / "permitida"
    allowed.mkdir()
    source = csv_source(tmp_path / "externa.csv")
    with pytest.raises(ValueError, match="raiz"):
        api("validar_fonte")(source, hashlib.sha256(source.read_bytes()).hexdigest(), allowed)


def test_t02_nome_ciclo_nao_substitui_manifesto(tmp_path):
    csv_source(tmp_path / "MATEMATICA_CICLO_I_2026.csv")
    record = api("catalogar")(tmp_path)[0]
    assert record["avaliacao"] is None
    assert record["status"] == "avaliacao_nao_identificada"
    assert record["programa"] is None
    assert record["caminho"] == "MATEMATICA_CICLO_I_2026.csv"
    assert "PESSOA_SINTETICA" not in json.dumps(record)


def test_manifesto_com_hash_identifica_sem_mudar_original(tmp_path):
    source = csv_source(tmp_path / "fonte.csv")
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest(tmp_path, "fonte.csv", digest)
    record = next(r for r in api("catalogar")(tmp_path) if r["caminho"] == "fonte.csv")
    assert record["sha256"] == digest
    assert record["avaliacao"]["ciclo"] == "I"
    assert record["avaliacao"]["ano_avaliacao"] == 2026
    assert record["status"] == "verificada"
    assert record["fonte_id"]
    assert source.read_bytes() == f"Ano Escolar;Componente Curricular;Nome\n1º ANO;MATEMÁTICA;PESSOA_SINTETICA\n".encode()


def test_ano_da_etapa_nao_e_duracao_de_nove_anos(tmp_path):
    source = tmp_path / "fonte.csv"
    source.write_bytes("Ano Escolar;Componente Curricular\nENSINO FUNDAMENTAL DE 9 ANOS - 1º ANO;MATEMÁTICA\n".encode())
    manifest(tmp_path, "fonte.csv", hashlib.sha256(source.read_bytes()).hexdigest())
    record = next(r for r in api("catalogar")(tmp_path) if r["tipo"] == "csv")
    assert record["anos_observados"] == [1]
    assert record["status"] == "verificada"


def test_manifesto_adulterado_bloqueia_catalogo(tmp_path):
    csv_source(tmp_path / "fonte.csv")
    manifest(tmp_path, "fonte.csv", "0" * 64)
    with pytest.raises(ValueError, match="hash"):
        api("catalogar")(tmp_path)


def test_t03_zip_matematica_com_lp_incompativel(tmp_path):
    source = csv_source(tmp_path / "conteudo.csv", "LÍNGUA PORTUGUESA")
    archive = tmp_path / "1ANO_MATEMATICA.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.write(source, "dados.csv")
    record = next(r for r in api("catalogar")(tmp_path) if r["tipo"] == "zip")
    assert record["status"] == "incompativel"
    assert record["componente_observado"] == ["LINGUA PORTUGUESA"]
    assert "componente" in record["incompatibilidade"]
    assert record["avaliacao"] is None


def test_zip_escape_rejeitado_sem_extrair(tmp_path):
    archive = tmp_path / "escape.zip"
    with zipfile.ZipFile(archive, "w") as z:
        z.writestr("../fora.csv", "sintetico")
    with pytest.raises(ValueError, match="raiz"):
        api("catalogar")(tmp_path)
    assert not (tmp_path.parent / "fora.csv").exists()


@pytest.mark.parametrize("member", ["/absoluto.csv", "C:\\fora.csv", "..\\fora.csv"])
def test_zip_caminhos_perigosos_rejeitados(tmp_path, member):
    with zipfile.ZipFile(tmp_path / "escape.zip", "w") as z:
        z.writestr(member, "sintetico")
    with pytest.raises(ValueError, match="raiz"):
        api("catalogar")(tmp_path)


def test_pdf_sem_proveniencia_recebe_status_proprio(tmp_path):
    (tmp_path / "historico_CICLO_II.pdf").write_bytes(b"%PDF-1.4\n% sintetico")
    record = api("catalogar")(tmp_path)[0]
    assert record["status"] == "documental_nao_comparavel"
    assert record["avaliacao"] is None


def test_zip_historico_sem_proveniencia_nao_ganha_ciclo(tmp_path):
    with zipfile.ZipFile(tmp_path / "referencia_contraprova_CICLO_II.zip", "w") as z:
        z.writestr("dados.csv", "Ano;Acertos ref;Acertos contra\n1;1;2\n")
    record = api("catalogar")(tmp_path)[0]
    assert record["status"] == "historica_nao_comparavel"
    assert record["avaliacao"] is None


def test_manifesto_nao_autoriza_escape(tmp_path):
    manifest(tmp_path, "../externa.csv", "0" * 64)
    with pytest.raises(ValueError, match="raiz"):
        api("catalogar")(tmp_path)


def test_csv_extraido_herda_proveniencia_somente_pelo_hash(tmp_path):
    source = csv_source(tmp_path / "extraidos" / "dados.csv")
    with zipfile.ZipFile(tmp_path / "exportado.zip", "w") as z:
        z.write(source, "dados.csv")
    digest = hashlib.sha256((tmp_path / "exportado.zip").read_bytes()).hexdigest()
    manifest(tmp_path, "exportado.zip", digest)
    record = next(r for r in api("catalogar")(tmp_path) if r["caminho"] == "extraidos/dados.csv")
    assert record["status"] == "verificada"
    assert record["avaliacao"]["avaliacao_id"] == "AV12026"
    assert record["proveniencia"]["vinculo"] == "sha256_membro_zip_verificado"


def test_membros_zip_iguais_com_contextos_distintos_bloqueiam(tmp_path):
    source = csv_source(tmp_path / "extraidos/dados.csv")
    entries = []
    for year in (1, 2):
        archive = tmp_path / f"ano{year}.zip"
        with zipfile.ZipFile(archive, "w") as z:
            z.write(source, "dados.csv")
        entries.append({"arquivo": archive.name, "sha256": hashlib.sha256(archive.read_bytes()).hexdigest(),
                        "ano_escolar": year, "componente": "MATEMATICA", "status": "baixado"})
    (tmp_path / "manifesto_coleta.json").write_text(json.dumps({
        "ciclo": "I", "ano_avaliacao": 2026, "avaliacao_id": "AV12026", "exportacoes": entries
    }))
    with pytest.raises(ValueError, match="ambigua|componente|ano"):
        api("catalogar")(tmp_path)
