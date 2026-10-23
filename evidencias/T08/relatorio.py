"""Renderização textual do agregado, sem abrir identificações individuais."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def fmt(x):
    return 'ausente' if x is None else f'{x:.3f}' if isinstance(x,float) else str(x)


def render_profile(profile):
    if profile.get('status_publicacao')=='suprimido_n_menor_5':
        return [f"### {profile['grupo_id']} — descrição somente no arquivo restrito",'',
                'Grupo com menos de cinco integrantes. Revisão docente pendente; dados detalhados preservados localmente.', '']
    p=profile; observed=p['observado']
    lines=[f"### {p['grupo_id']} — {p['nome']}",'',
        f"Tipo: {p['tipo']}. N={p['n']}. Turmas: "+', '.join(f'{k}: {v}' for k,v in p['turmas'].items())+'.',
        f"Pertencimento: {p['criterio_pertencimento']}.",'',
        f"Observado: C={fmt(observed['acertos'])}; D={fmt(observed['oportunidades'])}; C/D={fmt(observed['taxa'])}.",
        f"Distribuição das taxas individuais: {json.dumps(observed['distribuicao_taxas_individuais'],ensure_ascii=False)}.",
        f"Categorias originais: {json.dumps(p['categorias_caed_originais'],ensure_ascii=False)}.",
        f"Meta A: {json.dumps(p['meta_A'],ensure_ascii=False)}. Meta B: {json.dumps(p['meta_B'],ensure_ascii=False)}.",
        f"Cobertura: {json.dumps(p['cobertura'],ensure_ascii=False)}.",'',
        'Lacunas com erro observado, por ordem de taxa: '+(', '.join(p['lacunas_priorizadas']) or 'nenhuma nas posições disponíveis')+'.',
        'Forças relativas com algum acerto observado: '+(', '.join(p['forcas_relativas']) or 'não identificadas neste resultado')+'.',
        p['criterio_prioridade']+'.','']
    if p['estabilidade_global']:
        st=p['estabilidade_global']
        lines.extend([f"Estabilidade global: K={st['k']}; ARI sementes {json.dumps(st['seeds']['ari'])}; ARI subamostras {json.dumps(st['subamostras']['ari'])}.",
            f"Estabilidade deste grupo: {json.dumps(p['estabilidade'],ensure_ascii=False)}.",''])
    else:
        lines.extend(['Estabilidade: grupo por regra explícita; não é cluster descoberto nem conclusão estatística robusta.',''])
    for h in p['habilidades']:
        lines.extend([f"#### {h['posicao']} — C={fmt(h['acertos'])}, D={fmt(h['oportunidades'])}, taxa={fmt(h['taxa'])}",'',
            f"Disponíveis={h['disponiveis']}; ausentes={h['ausentes']}; constante={h['constante']}; distribuição={json.dumps(h['distribuicao'])}.",''])
        for v in h['curriculo']:
            lines.extend([f"- CAEd {v['codigo_caed']}: {v['texto_caed']}",
                f"- BNCC {v['codigo_bncc']}: {v['texto_bncc']}",
                f"- Contexto: {v['status_contextual']}; {v['status_semantico']}; peso documental {v['peso_analitico']}.",
                f"- Ressalva: {v['ressalva']}",
                f"- Fonte: {v['fonte_matriz']}, página {v['pagina_matriz']}, SHA {v['sha256_pdf']}; mapa {v['fonte_posicao']} / {v['versao_posicao']}; versão BNCC {json.dumps(v['versao_bncc'],ensure_ascii=False)}.",''])
        if not h['curriculo']: lines.extend(['Vínculo curricular não documentado; não atribuir habilidade BNCC.',''])
        for activity in h['atividades']:
            lines.extend([f"- {activity['etapa']}: {activity['proposta']} Evidência a registrar: {activity['evidencia_esperada']}.",''])
    for measure in p['medidas_proprias']:
        lines.extend([f"#### {measure['campo_original']} — unidade {measure['unidade']}",'',
            f"Distribuição: {json.dumps(measure['distribuicao'])}; disponíveis={measure['disponiveis']}; ausentes={measure['ausentes']}.",
            f"BNCC: {measure['bncc']}. Proposta: {measure['atividades']}",''])
    lines.extend(['Revisão docente: **pendente**. Data de reavaliação: **pendente**.',p['reavaliacao']['gatilho']+'.','',
        *['- '+r for r in p['ressalvas']],'',f"Proveniência das observações: {p['proveniencia_observacoes_sha256']}.",''])
    return lines


def main():
    path=ROOT/'estatistica/t08/checkpoint.json'; data=json.loads(path.read_text(encoding='utf-8'))
    lines=['# T08 — perfis pedagógicos para revisão docente','',
        'Versão v1. Perfis exploratórios locais; não são rótulos de capacidade, diagnósticos ou indicação de retenção. '
        'As duas metas são controles distintos. Escrita e fluência conservam as unidades originais. '
        'Integrantes e pequenos grupos permanecem somente no arquivo restrito, ignorado pelo Git.','',
        f"Checkpoint agregado SHA256: {hashlib.sha256(path.read_bytes()).hexdigest()}.",'',
        '## Resultados principais','',
        '| Ano | Componente | N observado elegível | K observado | Comparação curricular principal |',
        '|---|---|---:|---|---|']
    for inst in data['instrumentos']:
        c=inst['contexto']; r=inst['observado_operacional']; s=inst['cenarios'][0]
        lines.append(f"| {c['ano_escolar']} | {c['componente']} | {r['cobertura']['elegiveis']} | {r['k'] or 'sem agrupamento estável'} | {s['status']} |")
    lines.extend(['','Propagação é estimativa curricular, não evidência independente. O-total/O-controle separa seleção de colunas; '
                  'O-controle/P-controle mantém estudantes, colunas e pesos. Os diagnósticos por K, sementes e subamostras, '
                  'incluindo falhas e sensibilidades, estão no checkpoint. As sensibilidades não resgatam a análise principal.',''])
    for inst in data['instrumentos']:
        c=inst['contexto']
        lines.extend([f"## {c['ano_escolar']}º ano — {c['componente']}",'',
            'Contexto: '+json.dumps(c,ensure_ascii=False)+'.','',
            '### Referência por regras',''])
        for p in inst['perfis_regras']: lines.extend(render_profile(p))
        lines.extend(['### Agrupamento observado operacional','',inst['observado_operacional']['status']+'.',''])
        for p in inst['perfis_observado']: lines.extend(render_profile(p))
        primary=next(s for s in inst['cenarios'] if s['cenario']=='ressalvada_passo1')
        for arm in ('observado_controle','propagado_controle'):
            if arm not in primary['perfis']: continue
            lines.extend([f'### Comparação principal — {arm}','',primary['resultados'][arm]['status']+'.',''])
            for p in primary['perfis'][arm]: lines.extend(render_profile(p))
    for inst in data['unidades_proprias']:
        c=inst['contexto']; lines.extend([f"## {c['ano_escolar']}º ano — {c['componente']} (unidades próprias)",''])
        for p in inst['perfis']: lines.extend(render_profile(p))
    target=ROOT/'estatistica/t08/perfis-pedagogicos.md'
    target.write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='relatorio_agregado_gerado',sha256=hashlib.sha256(target.read_bytes()).hexdigest(),bytes=target.stat().st_size)))


if __name__=='__main__': main()
