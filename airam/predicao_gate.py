"""Prontidão documental temporal separada de validação de modelo (não executada)."""
from datetime import date
import re


def _evidence(value):
    return isinstance(value, dict) and isinstance(value.get('fonte_sha256'), str) and bool(
        re.fullmatch('[a-f0-9]{64}', value['fonte_sha256'])) and isinstance(value.get('referencia'), str) and bool(value['referencia'].strip())


def _date(value):
    try:
        return date.fromisoformat(value) if isinstance(value, str) else None
    except ValueError:
        return None


def avaliar_prontidao_temporal(avaliacoes: list[dict], vinculos: list[dict]) -> dict:
    """Verifica o contrato declarado, sem autenticar documentos externos nem treinar.

    Evidência exige hash SHA256 e referência; booleanos/rótulos não bastam. Para
    modelagem posterior ainda se exigem auditoria dos documentos e validação real.
    Nenhuma chave ou dado individual é devolvido pelo gate.
    """
    if not isinstance(avaliacoes, list) or not isinstance(vinculos, list) or not all(isinstance(r, dict) for r in avaliacoes + vinculos):
        raise ValueError('Contrato de prontidao invalido')
    reasons = set()
    cycles = {r.get('ciclo') for r in avaliacoes if isinstance(r.get('ciclo'), str) and r['ciclo'].strip() and _evidence(r.get('ciclo_evidencia'))}
    if len(cycles) < 2:
        reasons.add('ciclos_documentados_insuficientes')
    ids = [r.get('avaliacao_id') for r in avaliacoes]
    if not ids or any(not isinstance(i, str) or not i for i in ids) or len(set(i for i in ids if isinstance(i,str))) != len(ids):
        reasons.add('avaliacoes_sem_chave_unica')
    dates, partitions, groups = [], {'treino':[], 'teste':[]}, set()
    for row in avaliacoes:
        application = row.get('data_aplicacao')
        actual = _date(application.get('valor')) if isinstance(application, dict) else None
        if not actual or application.get('tipo') != 'aplicacao' or not _evidence(application.get('evidencia')):
            reasons.add('datas_aplicacao_nao_comprovadas'); actual = None
        dates.append(actual)
        comparison = row.get('comparabilidade')
        if not isinstance(comparison, dict) or not isinstance(comparison.get('grupo'),str) or not comparison['grupo'].strip() or not _evidence(comparison.get('evidencia')):
            reasons.add('comparabilidade_nao_comprovada')
        else:
            groups.add(comparison['grupo'])
        part = row.get('particao')
        if part not in partitions:
            reasons.add('particao_temporal_invalida')
        elif actual:
            partitions[part].append(actual)
        cutoff = _date(row.get('data_limite_features'))
        if not cutoff or not actual:
            reasons.add('corte_temporal_nao_comprovado')
        elif cutoff >= actual:
            reasons.add('vazamento_temporal')
        inputs, target, components = row.get('variaveis_entrada'), row.get('alvo'), row.get('componentes_alvo')
        if not isinstance(inputs,list) or not inputs or not all(isinstance(v,str) and v for v in inputs) or not isinstance(target,str) or not target or not isinstance(components,list) or not all(isinstance(v,str) and v for v in components):
            reasons.add('contrato_variaveis_incompleto')
        elif set(inputs) & {target,*components}:
            reasons.add('vazamento_alvo')
        processing = row.get('processamento')
        if not isinstance(processing,dict) or not _evidence(processing.get('evidencia')):
            reasons.add('processamento_treino_nao_comprovado')
        elif processing.get('ajustado_em') != 'treino':
            reasons.add('processamento_fora_treino')
        if part == 'teste' and not _evidence(row.get('desfecho_observado')):
            reasons.add('desfecho_futuro_nao_comprovado')
    if not avaliacoes or any(v is None for v in dates) or len(set(dates)) < 2:
        reasons.add('datas_aplicacao_nao_comprovadas')
    if len(groups) != 1:
        reasons.add('comparabilidade_nao_comprovada')
    if not partitions['treino'] or not partitions['teste'] or max(partitions['treino']) >= min(partitions['teste']):
        reasons.add('particao_temporal_invalida')
    # Features de teste também precisam ser posteriores ao encerramento do treino.
    for row in avaliacoes:
        cutoff = _date(row.get('data_limite_features'))
        if row.get('particao') == 'teste' and cutoff and partitions['treino'] and cutoff <= max(partitions['treino']):
            reasons.add('particao_temporal_invalida')
    by_id = {r.get('avaliacao_id'):r for r in avaliacoes if isinstance(r.get('avaliacao_id'),str)}
    members, linked = {'treino':set(), 'teste':set()}, set()
    seen = set()
    for link in vinculos:
        key, student = link.get('avaliacao_id'), link.get('aluno_local_id')
        if not isinstance(key,str) or key not in by_id or not isinstance(student,str) or not student or not _evidence(link.get('identidade_longitudinal')):
            reasons.add('identidade_longitudinal_nao_comprovada'); continue
        pair = (key,student)
        if pair in seen:
            reasons.add('vinculo_duplicado')
        seen.add(pair); linked.add(key)
        part = by_id[key].get('particao')
        if part in members:
            members[part].add(student)
    if not vinculos or any(key not in linked for key in by_id):
        reasons.add('identidade_longitudinal_nao_comprovada')
    if members['treino'] & members['teste']:
        reasons.add('estudante_em_treino_e_teste')
    return dict(tipo_resultado='gate_documental_temporal',
        prontidao_inputs_temporais=not reasons, previsao_temporal_validada=False,
        cenarios_disponiveis=True, motivos=sorted(reasons),
        pendencias_modelo=['auditar_documentos_e_identidade', 'baseline_simples',
            'ajuste_apenas_treino', 'avaliacao_holdout_temporal_e_por_estudante',
            'calibracao', 'incerteza', 'execucao_e_validacao_do_modelo'],
        premissas=['Hashes e referencias sao declaracoes a auditar, nao autenticacao externa.',
                  'Exportacao e etiquetas historicas assumidas nao sao aplicacao.'],
        unidade='avaliacoes_e_vinculos_documentais',
        comparabilidade='contrato_documental' if not reasons else 'nao_comprovada',
        status_validacao='sem_modelo_temporal_validado')
