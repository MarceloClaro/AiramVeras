"""Ingestão local restrita: cinco tabelas individuais e apoios de auditoria.

Não imprime registros. Identificadores locais são referências transitórias,
não IDs institucionais nem pseudônimos HMAC. Persistência final pertence à T11.
"""
from __future__ import annotations

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re
import unicodedata

from airam.catalogo import _configuration, _inside, validar_fonte
from airam.esquemas import medida, numero


def _normal(text: str) -> str:
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD', text)
                            if not unicodedata.combining(c)).upper().split())


def _categoria(raw: str | None) -> str | None:
    if raw is None or raw.strip().casefold() in {'', '-', 'sem resultado'}:
        return None
    return raw.strip().replace('Pré - leitor', 'Pré-leitor')


def _participacao(raw: str) -> bool:
    value = _normal(raw)
    if value not in {'SIM', 'NAO'}:
        raise ValueError('Flag de participacao nao reconhecida')
    return value == 'SIM'


def reconciliar_blocos(rows: list[dict]) -> list[dict]:
    """Soma H por aplicação local; cobertura parcial nunca vira prova completa.

    Totais declarados opcionais são comparados, jamais substituídos. Os CSVs
    atuais não publicam um total por aluno; a contraprova de 22 é externa a esta
    função. Sem itens individuais, não se inventa a posição de cada acerto.
    """
    groups = defaultdict(list)
    for row in rows:
        groups[row['avaliacao_local_id']].append(row)
    totals = []
    for identifier, blocks in groups.items():
        if len({b['campo_original'] for b in blocks}) != len(blocks):
            raise ValueError('Bloco duplicado na reconciliacao')
        if len({b['participacao'] for b in blocks}) != 1:
            raise ValueError('Participacao divergente na reconciliacao')
        available = [b for b in blocks if b['disponibilidade']]
        for block in available:
            n, d = block['numerador'], block['denominador']
            if not isinstance(n, int) or not isinstance(d, int) or not 0 <= n <= d or d <= 0:
                raise ValueError('Contagens impossiveis na reconciliacao')
        n = sum(b['numerador'] for b in available)
        d = sum(b['denominador'] for b in available)
        complete = len(available) == len(blocks) and blocks[0]['participacao'] is True
        for key, value in [('total_acertos', n), ('total_oportunidades', d)]:
            declared = {b[key] for b in blocks if b.get(key) is not None}
            if declared and (not complete or declared != {value}):
                raise ValueError('Falha de reconciliacao de total declarado')
        totals.append(dict(avaliacao_local_id=identifier, acertos=n if complete else None,
                           oportunidades=d if complete else None, taxa=n / d if complete else None,
                           blocos_previstos=len(blocks), blocos_disponiveis=len(available),
                           acertos_observados=n if available else None,
                           oportunidades_observadas=d if available else None,
                           cobertura_completa=complete))
    return totals


def _csv(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream, delimiter=';')
        header = reader.fieldnames
        if not header or len(set(header)) != len(header):
            raise ValueError('Cabecalho ausente ou duplicado')
        rows = list(reader)
    if any(None in r or any(v is None for v in r.values()) for r in rows):
        raise ValueError('Largura CSV inconsistente')
    return header, rows


def _metadata(row: dict, assessment: dict) -> dict:
    origin = {k: 'manifesto' for k in assessment}
    if 'Ano Escolar' in row:
        matches = re.findall(r'(\d+)\s*[O°]?\s*ANO\b', _normal(row['Ano Escolar']))
        if not matches or int(matches[-1]) != assessment['ano_escolar']:
            raise ValueError('ano escolar incompativel com manifesto')
        origin['ano_escolar'] = 'csv_e_manifesto_conferidos'
    if 'Componente Curricular' in row:
        expected = 'LINGUA PORTUGUESA' if assessment['componente'] == 'LEITURA' else assessment['componente']
        if _normal(row['Componente Curricular']) != expected:
            raise ValueError('componente incompativel com manifesto')
        origin['componente'] = 'csv_e_manifesto_conferidos'
    return origin


def _family(header: list[str]) -> str:
    if any(re.fullmatch(r'H \d+(?: \(%\))?', h) for h in header):
        return 'habilidades'
    if any(h in header for h in ['Nota', 'Nota média', 'Categoria de escrita']):
        return 'escrita'
    if any(h in header for h in ['Perfil de leitor', 'Pré-leitor (Total)']):
        return 'fluencia'
    raise ValueError('Familia de esquema nao reconhecida')


def _audit_aggregate(record: dict, assessments: list[dict]) -> None:
    selected = [a for a in assessments if a['exportacao'] == record['exportacao']
                and (record['nivel'] == 'escola' or a['turma'] == record['turma'])]
    if not selected:
        raise ValueError('Agregado sem registros individuais correspondentes')
    expected, assessed = len(selected), sum(a['participacao'] for a in selected)
    record.update(cadastros_observados=expected, avaliados_observados=assessed,
                  participacao_calculada=100 * assessed / expected)
    measures = {m['campo_original']: m for m in record['medidas']}
    for field, value in [('Previstos', expected), ('Avaliados', assessed)]:
        if field in measures and measures[field]['valor'] != value:
            raise ValueError('Falha de reconciliacao de participacao agregada')
    if 'Pré-leitor (Total)' in measures:
        counts = {k: v['valor'] for k, v in measures.items() if v['unidade'] == 'contagem'}
        if counts['Pré-leitor (Total)'] != sum(counts[f'Pré-leitor (Nível {i})'] for i in range(1, 5)):
            raise ValueError('Falha de reconciliacao de subniveis de fluencia')
        if counts['Pré-leitor (Total)'] + counts['Leitor Iniciante'] + counts['Leitor Fluente'] != assessed:
            raise ValueError('Falha de reconciliacao de perfis de fluencia')


def ler_exportacoes(catalogo: list[dict]) -> dict[str, list[dict]]:
    """Lê somente o conjunto canônico autorizado pelo manifesto prioritário.

    Revalida manifesto, ZIPs e CSVs. Cópias fora de csv_originais não entram na
    seleção, mesmo quando catalogadas como verificadas pelo hash do conteúdo.
    Todas as estruturas retornadas são locais restritas até a T03.
    """
    config = _configuration()
    project = Path(__file__).resolve().parents[1]
    root = (project / config['raiz_fontes']).resolve()
    manifest_relative = config['fontes']['coleta_ciclo_i_2026']['caminho']
    manifest_path = _inside(root / manifest_relative, root)
    manifests = [c for c in catalogo if c['caminho'] == manifest_relative]
    if len(manifests) != 1:
        raise ValueError('Manifesto prioritario ausente ou duplicado no catalogo')
    validar_fonte(manifest_path, manifests[0]['sha256'], root)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8-sig'))
    entries = [e for e in manifest['exportacoes'] if e.get('arquivo')]
    exports = {}
    for entry in entries:
        archive_path = _inside(manifest_path.parent / entry['arquivo'], root)
        validar_fonte(archive_path, entry['sha256'], root)
        key = (entry['ano_escolar'], entry['componente'])
        if key in exports:
            raise ValueError('Exportacao duplicada no manifesto')
        exports[key] = entry
    canonical = manifest_path.parent / 'csv_originais'
    chosen = [c for c in catalogo if c['tipo'] == 'csv'
              and (root / c['caminho']).resolve().is_relative_to(canonical.resolve())]
    result = {key: [] for key in ['matriculas', 'avaliacoes', 'habilidades', 'escrita',
                                 'fluencia', 'agregados', 'disponibilidade_arquivos']}
    for entry in manifest['exportacoes']:
        result['disponibilidade_arquivos'].append(dict(
            ano_escolar=entry['ano_escolar'], componente=entry['componente'],
            disponibilidade=bool(entry.get('arquivo')), status_original=entry.get('status'),
            manifesto=manifest_relative, sha256_manifesto=manifests[0]['sha256']))
    matriculas, seen, roles = {}, set(), defaultdict(list)
    for source in sorted(chosen, key=lambda c: c['caminho']):
        if source['status'] != 'verificada' or not source['apta_para_mistura']:
            raise ValueError('Fonte canonica incompativel ou nao verificada')
        prov = source['proveniencia']
        if not prov or prov['manifesto'] != manifest_relative or prov['sha256_manifesto'] != manifests[0]['sha256']:
            raise ValueError('Proveniencia de manifesto divergente')
        assessment = source['avaliacao']
        key = (assessment['ano_escolar'], assessment['componente'])
        entry = exports.get(key)
        expected = {k: entry.get(k, manifest.get(k)) for k in
                    ['avaliacao_id', 'ano_avaliacao', 'ciclo', 'ano_escolar', 'componente']} if entry else None
        if expected is None or any(v is None for v in expected.values()) or assessment != expected:
            raise ValueError('Contexto da avaliacao incompativel com manifesto')
        expected_archive = (manifest_path.parent / entry['arquivo']).relative_to(root).as_posix()
        if prov.get('zip') != expected_archive or prov.get('vinculo') != 'sha256_membro_zip_verificado':
            raise ValueError('Vinculo de exportacao divergente')
        path = _inside(root / source['caminho'], root)
        validar_fonte(path, source['sha256'], root)
        header, rows = _csv(path)
        family = _family(header)
        expected_family = {'LEITURA': 'habilidades', 'MATEMATICA': 'habilidades',
                           'ESCRITA': 'escrita', 'FLUENCIA': 'fluencia'}.get(key[1])
        if family != expected_family:
            raise ValueError('Familia de componente incompativel')
        level = 'estudante' if 'Estudante' in header else 'turma' if 'Turma' in header else 'escola'
        roles[key].append(level)
        for line, row in enumerate(rows, start=2):
            origins = _metadata(row, assessment)
            common = {**assessment, 'fonte_id': source['fonte_id'], 'sha256': source['sha256'],
                      'caminho': source['caminho'], 'linha_fonte': line,
                      'exportacao': expected_archive, 'sha256_exportacao': entry['sha256'],
                      'manifesto': manifest_relative, 'sha256_manifesto': manifests[0]['sha256']}
            if level != 'estudante':
                measures = []
                excluded = {'Rede', 'Ano Escolar', 'Componente Curricular', 'Estado', 'Regional',
                            'Município', 'Escola', 'Código da Escola', 'Código da escola',
                            'Código da Turma', 'Turma', 'Código do estado'}
                for field in header:
                    if field in excluded:
                        continue
                    unit = ('contagem' if field in {'Previstos', 'Avaliados'} or family == 'fluencia'
                            and field not in {'% Participação'} else 'nota_escrita'
                            if field == 'Nota média' or field.startswith('Questão') else 'percentual')
                    measures.append(dict(campo_original=field, **medida(row[field], unit, None)))
                result['agregados'].append(dict(**common, nivel=level,
                    turma=_normal(row['Turma']) if 'Turma' in row else None,
                    medidas=measures, origem_metadados=origins,
                    campos_identificadores_originais={k: v for k, v in row.items() if k in excluded}))
                continue
            turma_field = 'Turma' if 'Turma' in row else 'Turmma'
            if not row.get(turma_field, '').strip() or not row.get('Estudante', '').strip():
                raise ValueError('Chave local incompleta')
            local_key = (str(manifest['codigo_escola']), key[0], _normal(row[turma_field]), _normal(row['Estudante']))
            duplicate_key = (local_key, assessment['avaliacao_id'], assessment['ano_avaliacao'], assessment['ciclo'], key[1])
            if duplicate_key in seen:
                raise ValueError('Duplicata intracomponente de chave local')
            seen.add(duplicate_key)
            origin = dict(**common, coluna_turma_original=turma_field, turma_bruto=row[turma_field],
                          nome_bruto=row['Estudante'])
            if local_key not in matriculas:
                matriculas[local_key] = dict(matricula_local_id=f'M{len(matriculas) + 1:06}',
                    escola_codigo=local_key[0], ano_escolar=key[0], turma=local_key[2],
                    nome_normalizado=local_key[3], nome_bruto=row['Estudante'], origens=[],
                    qualidade_vinculo='local_provisorio_sem_id_institucional')
            matricula = matriculas[local_key]
            matricula['origens'].append(origin)
            participated = _participacao(row.get('Avaliado', row.get('Participação', '')))
            identifier = 'A' + hashlib.sha256((source['fonte_id'] + ':' + str(line)).encode()).hexdigest()
            linkage = dict(**common, matricula_local_id=matricula['matricula_local_id'],
                           avaliacao_local_id=identifier)
            category_field = {'habilidades': 'Nível de aprendizagem', 'escrita': 'Categoria de escrita',
                              'fluencia': 'Perfil de leitor'}[family]
            av = dict(**linkage, turma=local_key[2], participacao=participated,
                      participacao_bruto=row.get('Avaliado', row.get('Participação')),
                      categoria=_categoria(row.get(category_field)), categoria_bruto=row.get(category_field),
                      campo_categoria_original=category_field, origem_metadados=origins,
                      data_aplicacao=None, data_exportacao=source.get('data_exportacao'),
                      programa=source.get('programa'), acertos=None, oportunidades=None)
            result['avaliacoes'].append(av)
            if family == 'habilidades':
                fields = [(h, 'acertos_itens') for h in header if re.fullmatch(r'H \d+', h)]
            elif family == 'escrita':
                fields = [(h, 'nota_escrita') for h in header if h == 'Nota' or h.startswith('Questão')]
            else:
                fields = [('Palavras (leitura global)', 'palavras_total'),
                          ('Palavras possivelmente desconhecidas', 'palavras_total'),
                          ('Texto (Palavras corretas)', 'palavras_corretas'),
                          ('Texto (Compreensão)', 'acertos_itens')]
            for field, unit in fields:
                if field not in row:
                    raise ValueError('Coluna obrigatoria ausente')
                result[family].append(dict(**linkage, campo_original=field,
                    posicao=field if family == 'habilidades' else None,
                    **medida(row[field], unit, participated)))
    if set(roles) != set(exports) or any(sorted(v) != ['escola', 'estudante', 'turma'] for v in roles.values()):
        raise ValueError('Conjunto canonico incompleto ou duplicado')
    totals = {r['avaliacao_local_id']: r for r in reconciliar_blocos(result['habilidades'])}
    for av in result['avaliacoes']:
        av.update({k: v for k, v in totals.get(av['avaliacao_local_id'], {}).items() if k != 'avaliacao_local_id'})
    for aggregate in result['agregados']:
        _audit_aggregate(aggregate, result['avaliacoes'])
    result['matriculas'] = list(matriculas.values())
    return result
