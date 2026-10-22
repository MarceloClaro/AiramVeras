"""Auditoria independente das fontes; nao e implementacao nem teste T05.

Somente stdlib. Nunca exporta linhas individuais, nomes ou identificadores.
Hash de si e de todas as fontes persistido antes de interpretar qualquer CSV.
"""
import csv
import hashlib
import io
import json
import re
import sys
import unicodedata
import zipfile
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
SOURCE = ROOT.parent / "resultados-caed-ciclo-i-2026"
EXPECTED = "0059670041831280892c45e9c3ed3c0b769f579c881631fb64c9afdf03409946"
CATEGORIES = ("Defasagem", "Aprendizado intermediário", "Aprendizado adequado")
CATEGORY_SOURCE = {"Defasagem": "Defasagem", "Aprendizado intermediário": "Intermediário", "Aprendizado adequado": "Adequado"}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (HERE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def norm(value):
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def ratio(value):
    return {"numerador": value.numerator, "denominador": value.denominator,
            "decimal_aproximado": str(Decimal(value.numerator) / Decimal(value.denominator))}


def rounded(value, places, even=False):
    """Arredondamento racional exato: metade para cima ou metade para par."""
    scaled = value * 10 ** places
    q, rem = divmod(scaled.numerator, scaled.denominator)
    tie = 2 * rem == scaled.denominator
    if 2 * rem > scaled.denominator or (tie and (not even or q % 2)):
        q += 1
    return Fraction(q, 10 ** places), tie


def percent_check(context, field, numerator, denominator, raw):
    clean = raw.strip().removesuffix("%").replace(",", ".")
    published_decimal = Decimal(clean)
    published = Fraction(published_decimal)
    places = max(0, -published_decimal.as_tuple().exponent)
    exact = Fraction(100 * numerator, denominator)
    half_up, tie = rounded(exact, places)
    half_even, _ = rounded(exact, places, even=True)
    distance = abs(published - exact)
    half_quantum = Fraction(1, 2 * 10 ** places)
    return {**context, "campo": field, "numerador": numerator, "denominador": denominator,
            "percentual_exato": ratio(exact), "publicado_bruto": raw,
            "casas_originais": places, "calculado_half_up": ratio(half_up),
            "reproduzido_half_up": published == half_up,
            "reproduzido_half_even": published == half_even, "meio_caso": tie,
            "distancia_absoluta_pp": ratio(distance),
            "meia_unidade_precisao_original_pp": ratio(half_quantum),
            "compativel_intervalo_fechado_quantizacao": distance <= half_quantum,
            "fronteira_intervalo_quantizacao": distance == half_quantum,
            "exige_arredondamento": exact != published,
            "diferenca_publicado_menos_exato_pp": ratio(published - exact)}


def read_csv(path):
    # Descartar campos nominais antes de construir o resultado interno.
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        headers = reader.fieldnames
        rows = []
        for row in reader:
            if None in row or any(v is None for v in row.values()):
                raise ValueError("Largura CSV invalida; detalhes individuais suprimidos")
            rows.append({k: v for k, v in row.items() if k not in ("Estudante",)})
    return headers, rows


def main():
    start = datetime.now(timezone.utc).isoformat()
    manifest_path = SOURCE / "manifesto_coleta.json"
    if sha(manifest_path) != EXPECTED:
        raise ValueError("Manifesto fora do hash canonico")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    csvs = sorted((SOURCE / "csv_originais").rglob("*.csv"))
    exports = [e for e in manifest["exportacoes"] if e["status"] == "baixado"]
    zips = [SOURCE / e["arquivo"] for e in exports]
    if len(csvs) != 54 or len(zips) != 18:
        raise ValueError("Inventario nao canonico")
    snapshots = [{"caminho": p.relative_to(SOURCE).as_posix(), "sha256": sha(p),
                  "bytes": p.stat().st_size} for p in [manifest_path, *zips, *csvs]]
    collector_hash = sha(Path(__file__))
    write("hashes-antes.json", {"inicio_utc": start, "coletor_sha256": collector_hash,
          "manifesto_sha256": EXPECTED, "fontes": snapshots,
          "etapa": "anterior_a_qualquer_parse_de_csv"})
    zip_checks = []
    authenticated = set()
    for e in exports:
        zpath = SOURCE / e["arquivo"]
        if sha(zpath) != e["sha256"]:
            raise ValueError("ZIP diverge do manifesto")
        with zipfile.ZipFile(zpath) as archive:
            if archive.testzip() is not None:
                raise ValueError("CRC ZIP invalido")
            members = [m for m in archive.namelist() if m.lower().endswith(".csv")]
            if len(members) != 3:
                raise ValueError("ZIP fora do inventario de tres CSV")
            for member in members:
                cpath = SOURCE / "csv_originais" / zpath.stem / Path(member).name
                if not cpath.is_file() or cpath.read_bytes() != archive.read(member):
                    raise ValueError("CSV nao coincide byte a byte com membro ZIP")
                authenticated.add(cpath)
        zip_checks.append({"exportacao": zpath.stem, "sha256_manifesto_confere": True,
                           "crc_valido": True, "csv_identicos": len(members)})
    if authenticated != set(csvs):
        raise ValueError("CSV fora dos ZIP autenticados")
    checks, summaries, coherence, metadata = [], [], [], []
    for e in exports:
        if e["componente"] not in ("LEITURA", "MATEMATICA"):
            continue
        folder = SOURCE / "csv_originais" / Path(e["arquivo"]).stem
        files = list(folder.glob("*.csv"))
        students_path, = [p for p in files if p.name.startswith("HABILIDADES_DESEMPENHO_ESTUDANTE")]
        school_path, = [p for p in files if p.name.startswith("HABILIDADE_DESEMPENHO_ESCOLA")]
        classes_path, = [p for p in files if p.name.startswith("HABILIDADE_DESEMPENHO_TURMA")]
        hfields, students = read_csv(students_path)
        hfields = [h for h in hfields if re.fullmatch(r"H \d+", h)]
        _, school = read_csv(school_path)
        _, classes = read_csv(classes_path)
        if len(school) != 1:
            raise ValueError("Escopo de escola nao unico")
        for rows in (students, school, classes):
            for row in rows:
                if norm(row["Ano Escolar"]) != norm(e["filtros_observados_no_portal"]["DADOS.VL_FILTRO_ETAPA"]) or norm(row["Componente Curricular"]) != norm(e["filtros_observados_no_portal"]["DADOS.VL_FILTRO_DISCIPLINA"]):
                    raise ValueError("Metadata interna contradiz manifesto")
        metadata.append({"fonte": folder.name, "linhas_conferidas": len(students) + len(school) + len(classes)})
        base = {"fonte": folder.name, "ano_escolar": e["ano_escolar"], "componente": e["componente"]}
        groups = [("escola", None, students, school[0], school_path)]
        for row in classes:
            group = [s for s in students if s["Turma"].strip() == row["Turma"].strip()]
            groups.append(("turma", row["Turma"].strip(), group, row, classes_path))
        class_names = [r["Turma"].strip() for r in classes]
        if len(class_names) != len(set(class_names)) or Counter(s["Turma"].strip() for s in students) != Counter({r["Turma"].strip(): len([s for s in students if s["Turma"].strip() == r["Turma"].strip()]) for r in classes}):
            raise ValueError("Particao de turmas invalida")
        group_summaries = []
        for level, class_name, group, published, published_path in groups:
            context = {**base, "nivel": level, "turma": class_name,
                       "fonte_agregado": published_path.relative_to(SOURCE).as_posix()}
            flags = Counter(norm(s["Avaliado"]) for s in group)
            if any(f not in ("sim", "não") for f in flags) or not group:
                raise ValueError("Participacao nao reconhecida ou grupo vazio")
            participants = [s for s in group if norm(s["Avaliado"]) == "sim"]
            categories = Counter(norm(s["Nível de aprendizagem"]) for s in participants)
            if set(categories) - set(map(norm, CATEGORY_SOURCE.values())):
                raise ValueError("Categoria avaliada desconhecida")
            checks.append(percent_check(context, "Avaliados (%)", len(participants), len(group), published["Avaliados (%)"]))
            for cat in CATEGORIES:
                checks.append(percent_check(context, cat, categories[norm(CATEGORY_SOURCE[cat])], len(participants), published[cat]))
            hcounts = {}
            missing = 0
            for h in hfields:
                correct, opportunities, valid = 0, 0, 0
                denominators = Counter()
                for s in group:
                    cell = s[h].strip()
                    participating = norm(s["Avaliado"]) == "sim"
                    if cell in ("", "-"):
                        missing += 1
                        if participating:
                            raise ValueError("H ausente em participante; comparacao impossivel")
                        continue
                    parsed = re.fullmatch(r"(\d+)\s*/\s*(\d+)", cell)
                    if not parsed or not participating:
                        raise ValueError("H invalida ou presente em nao participante")
                    n, d = map(int, parsed.groups())
                    if not 0 <= n <= d or d <= 0:
                        raise ValueError("Contagem H invalida")
                    correct += n
                    opportunities += d
                    denominators[d] += 1
                    valid += 1
                hcounts[h] = {"acertos": correct, "oportunidades": opportunities, "participantes_com_medida": valid,
                              "itens_por_celula_frequencias": dict(sorted(denominators.items()))}
                checks.append(percent_check(context, h + " (%)", correct, opportunities, published[h + " (%)"]))
            total_n = sum(x["acertos"] for x in hcounts.values())
            total_d = sum(x["oportunidades"] for x in hcounts.values())
            summary = {**base, "nivel": level, "turma": class_name, "cadastros_exportados": len(group),
                       "avaliados": len(participants), "nao_avaliados": len(group) - len(participants),
                       "categorias_contagens": {cat: categories[norm(CATEGORY_SOURCE[cat])] for cat in CATEGORIES},
                       "celulas_h_ausentes": missing, "habilidades": hcounts,
                       "taxa_todos_itens_derivada_nao_publicada": {"acertos": total_n, "oportunidades": total_d, "percentual": ratio(Fraction(total_n * 100, total_d))},
                       "media_simples_das_taxas_h_apenas_diagnostico": ratio(sum((Fraction(x["acertos"] * 100, x["oportunidades"]) for x in hcounts.values()), Fraction()) / len(hcounts))}
            summaries.append(summary)
            group_summaries.append(summary)
        sc, *cl = group_summaries
        for key in ("cadastros_exportados", "avaliados", "nao_avaliados", "celulas_h_ausentes"):
            coherence.append({**base, "campo": key, "escola": sc[key], "soma_turmas": sum(x[key] for x in cl), "coincide": sc[key] == sum(x[key] for x in cl)})
        for h in hfields:
            for key in ("acertos", "oportunidades", "participantes_com_medida"):
                values = [x["habilidades"][h][key] for x in group_summaries]
                coherence.append({**base, "campo": h + ":" + key, "escola": values[0], "soma_turmas": sum(values[1:]), "coincide": values[0] == sum(values[1:])})
        for cat in CATEGORIES:
            values = [x["categorias_contagens"][cat] for x in group_summaries]
            coherence.append({**base, "campo": cat, "escola": values[0], "soma_turmas": sum(values[1:]), "coincide": values[0] == sum(values[1:])})
    unchanged = all(sha(SOURCE / s["caminho"]) == s["sha256"] for s in snapshots) and sha(Path(__file__)) == collector_hash
    if not unchanged:
        raise ValueError("Fonte ou coletor mudou durante auditoria")
    counts = {"checks_percentuais": len(checks), "reproduzidos_half_up": sum(c["reproduzido_half_up"] for c in checks),
              "divergencias_half_up": sum(not c["reproduzido_half_up"] for c in checks),
              "reproduzidos_half_even": sum(c["reproduzido_half_even"] for c in checks),
              "meios_casos": sum(c["meio_caso"] for c in checks), "exigem_arredondamento": sum(c["exige_arredondamento"] for c in checks),
              "checks_coerencia_contagens": len(coherence), "divergencias_coerencia": sum(not c["coincide"] for c in coherence),
              "por_familia": dict(Counter("H" if c["campo"].startswith("H ") else "participacao" if c["campo"] == "Avaliados (%)" else "categoria" for c in checks)),
              "precisoes_originais": dict(Counter(c["casas_originais"] for c in checks)),
              "compativeis_intervalo_fechado_quantizacao": sum(c["compativel_intervalo_fechado_quantizacao"] for c in checks),
              "fronteiras_intervalo_quantizacao": sum(c["fronteira_intervalo_quantizacao"] for c in checks)}
    families = {}
    for kind in ("participacao", "categoria", "H"):
        subset = [c for c in checks if ("H" if c["campo"].startswith("H ") else "participacao" if c["campo"] == "Avaliados (%)" else "categoria") == kind]
        families[kind] = {"checks": len(subset), "reproduzidos_half_up": sum(c["reproduzido_half_up"] for c in subset),
                          "divergencias_half_up": sum(not c["reproduzido_half_up"] for c in subset),
                          "meios_casos": sum(c["meio_caso"] for c in subset)}
    counts["detalhe_familias"] = families
    counts["por_nivel"] = {level: {"checks": sum(c["nivel"] == level for c in checks),
                          "divergencias": sum(c["nivel"] == level and not c["reproduzido_half_up"] for c in checks)}
                          for level in ("escola", "turma")}
    category_sums = []
    for s in summaries:
        subset = [c for c in checks if c["fonte"] == s["fonte"] and c["nivel"] == s["nivel"] and c["turma"] == s["turma"] and c["campo"] in CATEGORIES]
        published_sum = sum((Fraction(Decimal(c["publicado_bruto"].strip().removesuffix("%"))) for c in subset), Fraction())
        category_sums.append({"fonte": s["fonte"], "nivel": s["nivel"], "turma": s["turma"],
                              "soma_percentuais_publicados": ratio(published_sum),
                              "contagens_somam_avaliados": sum(s["categorias_contagens"].values()) == s["avaliados"]})
    receipt = {"tipo": "auditoria_fontes_preparacao_nao_gate_produto_T05", "inicio_utc": start,
               "fim_utc": datetime.now(timezone.utc).isoformat(), "python": sys.version,
               "coletor_sha256": collector_hash, "hashes_antes_sha256": sha(HERE / "hashes-antes.json"),
               "manifesto_sha256": EXPECTED, "fontes_inalteradas_ao_final": unchanged,
               "autenticacao": {"csv": len(csvs), "zip": len(zips), "exportacoes": zip_checks},
               "metadata_interna": metadata, "politica_arredondamento": "Mais proximo, meios para cima, na precisao lexical original; metade para par tambem confrontada separadamente. Nenhuma politica oficial inferida.",
               "resumo": counts, "checks_percentuais": checks, "checks_coerencia_contagens": coherence,
               "diagnostico_somas_categorias": category_sums,
               "agregados_recalculados": summaries,
               "divergencias": [c for c in checks if not c["reproduzido_half_up"]],
               "limites": ["Auditoria dos CSV coletados; sem consulta nova ao portal nem validacao pedagogica externa.",
                            "Nenhum percentual total de acertos entre todas H e publicado nestes CSV; taxa global derivada conserva somas de itens e participantes.",
                            "Avaliados (%) nao publica contagens previstas; denominador observado sao cadastros exportados, sem afirmar matricula institucional completa.",
                            "Categorias preservadas como classificacao original; nao se infere corte de acertos.",
                            "Escrita e fluencia somente autenticadas nos hashes/ZIP; fora da analise.",
                            "Nao constitui RED/GREEN, teste de mutacao, pacote de liberacao ou aprovacao T05."]}
    write("recibo-portal.json", receipt)
    print(json.dumps({"resumo": counts, "recibo_sha256": sha(HERE / "recibo-portal.json"),
                      "coletor_sha256": collector_hash, "fontes_inalteradas": unchanged}, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Nao deixar excecoes de parsing exporem valores individuais.
        print("Auditoria interrompida; diagnostico individual suprimido.", file=sys.stderr)
        raise SystemExit(1)
