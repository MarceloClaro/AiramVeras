"""Associa posições a ocorrências e BNCC sem propagar resultados individuais."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path

CONFIG = Path(__file__).resolve().parents[1] / 'config/ressalvas_curriculares.json'


def _id(values):
    return hashlib.sha256(json.dumps(values, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()


def vincular_posicoes(posicoes: list[dict], ocorrencias: list[dict], bncc: dict) -> list[dict]:
    """Uma linha por posição/ocorrência/BNCC; candidatos anteriores têm peso zero.

    O ano avaliado nunca é derivado do prefixo CAEd. Somente ocorrências da tabela do
    próprio ano prevalecem; na ausência, fontes anteriores permanecem candidatas.
    """
    config = json.loads(CONFIG.read_text(encoding='utf-8'))
    occurrence_ids = [o['ocorrencia_id'] for o in ocorrencias]
    if len(occurrence_ids) != len(set(occurrence_ids)):
        raise ValueError('ocorrencia duplicada na fonte contextual')
    for occurrence in ocorrencias:
        codes = occurrence['codigos_bncc']
        if len(codes) != len(set(codes)):
            raise ValueError('Codigo BNCC duplicado na mesma celula')
    result, seen = [], set()
    for position in posicoes:
        fields = ['avaliacao_id', 'ano_avaliacao', 'ciclo', 'ano_escolar', 'componente', 'posicao',
                  'fonte_posicao', 'versao_posicao']
        if any(position.get(k) is None or position.get(k) == '' for k in fields):
            raise ValueError('Posicao sem contexto/fonte/versao obrigatorios')
        key = [position[k] for k in fields]
        pid = _id(key)
        if pid in seen:
            raise ValueError('Posicao duplicada no mesmo contexto')
        seen.add(pid)
        year = int(position['ano_escolar'])
        code = position['codigo_caed_observado']
        matches = [o for o in ocorrencias if o['codigo_caed'] == code
                   and o['componente'] == position['componente']]
        own = [o for o in matches if o['ano_tabela'] == year]
        candidates = own or [o for o in matches if o['ano_tabela'] < year]
        rows = []
        for occurrence in candidates or [None]:
            status = ('sem_ocorrencia_contextual' if occurrence is None else
                      'fonte_anterior_integracao_a_confirmar' if occurrence['ano_tabela'] < year else
                      'proprio_ano_ciclo_confirmado' if position['ciclo'] in occurrence['ciclos'] else
                      'ciclo_nao_assinalado')
            for bc in occurrence['codigos_bncc'] if occurrence else [None]:
                normative = bncc.get(bc)
                valid = bool(normative and normative.get('codigo') == bc
                             and normative.get('vigencia', {}).get('status') == 'vigente')
                warnings = [r['ressalva'] for r in config['regras']
                            if code in r['codigos_caed'] and bc == r['codigo_bncc']]
                if status == 'fonte_anterior_integracao_a_confirmar':
                    warnings.append('Fonte anterior; integração a confirmar. A nota geral não confirma aplicabilidade individual ao ano avaliado.')
                if not valid:
                    warnings.append('Código BNCC inexistente ou inativo: relação não confirmada, sem substituição.')
                semantica = any(code in r['codigos_caed'] and bc == r['codigo_bncc'] for r in config['regras'])
                rows.append(dict(vinculo_id=_id([pid, occurrence['ocorrencia_id'] if occurrence else None, bc]),
                    posicao_id=pid, avaliacao_id=position['avaliacao_id'], ano_avaliacao=position['ano_avaliacao'],
                    ano_avaliado=year, componente=position['componente'], posicao=position['posicao'],
                    ciclo_avaliado=position['ciclo'], fonte_posicao=position['fonte_posicao'],
                    versao_posicao=position['versao_posicao'], codigo_caed=code,
                    ocorrencia_id=occurrence['ocorrencia_id'] if occurrence else None,
                    ano_tabela=occurrence['ano_tabela'] if occurrence else None,
                    pagina_matriz=occurrence['pagina_matriz'] if occurrence else None,
                    fonte_matriz=occurrence['fonte_matriz'] if occurrence else None,
                    sha256_pdf=occurrence['sha256_pdf'] if occurrence else None,
                    ciclos_matriz=deepcopy(occurrence['ciclos']) if occurrence else [],
                    texto_caed=occurrence['texto_caed'] if occurrence else None,
                    codigo_bncc=bc, texto_bncc=normative['texto'] if normative else None,
                    localizador_bncc=deepcopy(normative['fonte']) if normative else None,
                    bncc=deepcopy(normative), nota_integracao=deepcopy(occurrence.get('nota_integracao')) if occurrence else None,
                    status_contextual=status, status_bncc='confirmado' if valid else 'nao_confirmado',
                    status_semantico='associacao_publicada_com_ressalva_semantica' if semantica else 'associacao_publicada_sem_equivalencia_integral',
                    ressalva=' '.join(warnings) or config['limite_geral'], peso_analitico=0.0))
        eligible = [r for r in rows if r['status_contextual'] == 'proprio_ano_ciclo_confirmado'
                    and r['status_bncc'] == 'confirmado']
        for row in eligible:
            row['peso_analitico'] = 1 / len(eligible)
        result.extend(rows)
    return result
