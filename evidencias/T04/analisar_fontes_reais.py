"""Executa o incremento real; publica somente currículo e cobertura agregada T03."""
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from airam.bncc import BNCC_COMMIT, carregar_bncc
from airam.matriz_cnca import PDF_SHA256, extrair_ocorrencias
from airam.vinculos import vincular_posicoes

T03_SHA256 = 'b26bef93117c7c38906cd9e6e025cfc5f2a9969cc4834e4b785618d29dd56dbb'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def key(row):
    return row['avaliacao_id'], row['ano_escolar'], row['componente'], row['posicao']


def main():
    pdf = ROOT.parent / 'MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf'
    mapa = ROOT.parent / 'resultados-caed-ciclo-i-2026/conferencia/mapa_posicao_codigo_caed.csv'
    previous = ROOT / 'restrito/t03/tabelas.json'
    if digest(previous) != T03_SHA256:
        raise ValueError('Checkpoint T03 diverge do handoff autenticado')
    occurrences = extrair_ocorrencias(pdf)
    normative = carregar_bncc(ROOT.parent / 'bncc-dados', BNCC_COMMIT)
    with mapa.open(encoding='utf-8-sig', newline='') as stream:
        # Whitelist: percentuais e qualquer campo não curricular ficam fora do checkpoint.
        positions = [dict(avaliacao_id=r['avaliacao_id'], ano_escolar=int(r['ano_escolar']),
            ano_avaliacao=2026, ciclo='I', componente=r['componente'], posicao=r['posicao'],
            codigo_caed_observado=r['codigo_caed_observado'],
            fonte_posicao='resultados-caed-ciclo-i-2026/conferencia/' + mapa.name,
            versao_posicao=digest(mapa)) for r in csv.DictReader(stream, delimiter=';')]
    links = vincular_posicoes(positions, occurrences, normative)
    # A carga restrita é local; somente a cardinalidade de conjuntos sai deste processo.
    data = json.loads(previous.read_text(encoding='utf-8'))
    observed_keys = {key(r) for r in data['habilidades']}
    map_keys = {key(r) for r in positions}
    if observed_keys - map_keys:
        raise ValueError('Ha posicoes T03 sem cobertura no mapa publico')
    used = {p['codigo_caed_observado'] for p in positions}
    all_codes = {bc for o in occurrences for bc in o['codigos_bncc']}
    audited_union = {bc for o in occurrences if o['codigo_caed'] in used for bc in o['codigos_bncc']}
    if not all_codes <= normative.keys():
        raise ValueError('Codigo publicado sem confirmacao no canonico vigente')
    strict_union = {v['codigo_bncc'] for v in links if v['peso_analitico'] > 0}
    per_status = {status: len({v['posicao_id'] for v in links if v['status_contextual'] == status})
                  for status in sorted({v['status_contextual'] for v in links})}
    summary = dict(ocorrencias=len(occurrences), codigos_caed_matriz=len({o['codigo_caed'] for o in occurrences}),
        posicoes=len(positions), codigos_caed_posicoes=len(used), vinculos=len(links),
        posicoes_por_status=per_status, bncc_uniao_contextos_auditados=len(audited_union),
        bncc_politica_contextual=len(strict_union), bncc_todas_ocorrencias=len(all_codes),
        posicoes_com_ressalva_semantica=len({v['posicao_id'] for v in links if v['status_semantico'] == 'associacao_publicada_com_ressalva_semantica'}),
        ocorrencias_por_pagina=dict(Counter(str(o['pagina_matriz']) for o in occurrences)),
        t03_posicoes_distintas=len(observed_keys), t03_medidas_h=len(data['habilidades']),
        t03_posicoes_sem_cobertura=len(observed_keys - map_keys),
        mapa_posicoes_sem_medida_t03=len(map_keys - observed_keys))
    metadata = dict(versao_schema='airam-curriculo-t04-v1',
        fontes=dict(matriz=dict(arquivo=pdf.name, sha256=PDF_SHA256),
            mapa=dict(arquivo=positions[0]['fonte_posicao'], sha256=digest(mapa),
                      contexto_declarado=dict(ano_avaliacao=2026, ciclo='I')),
            bncc=next(iter(normative.values()))['proveniencia_dataset'],
            t03=dict(arquivo='restrito/t03/tabelas.json', sha256=T03_SHA256, dados_individuais_incluidos=False)),
        politica=dict(contexto='Preferir próprio ano e manter todas suas marcas; fontes anteriores somente se não há próprio ano.',
            peso='Peso unitário repartido entre associações vigentes do próprio ano e ciclo assinalado; demais pesos zero. Não é pontuação de domínio.',
            ressalvas='Ressalvas semânticas preservam associação publicada sem equivalência integral.',
            ciclos='Células vetoriais, inclusão de X por limites, sem regra especial por código.',
            anti_multiplicacao='Medidas T03 não integram arestas. Agregar observações uma vez por posição, antes de qualquer expansão.'),
        contagens=summary)
    checkpoint = dict(**metadata, posicoes=positions, ocorrencias_matriz=occurrences,
                      bncc={code: normative[code] for code in sorted(all_codes)}, vinculos_posicoes=links)
    output = ROOT / 'curriculo/t04/checkpoint.json'
    write_json(output, checkpoint)
    write_json(ROOT / 'evidencias/T04/conferencia-real.json', dict(**summary,
        checkpoint_sha256=digest(output), codigos_bncc_uniao_contextos_auditados=sorted(audited_union),
        codigos_bncc_politica_contextual=sorted(strict_union),
        excecoes=[dict(codigo_caed=v['codigo_caed'], ano_avaliado=v['ano_avaliado'],
                      ano_tabela=v['ano_tabela'], pagina_matriz=v['pagina_matriz'],
                      status=v['status_contextual']) for v in links
                  if v['status_contextual'] == 'fonte_anterior_integracao_a_confirmar']))
    print(json.dumps(dict(contagens=summary, checkpoint_sha256=digest(output)), ensure_ascii=False))


if __name__ == '__main__':
    main()
