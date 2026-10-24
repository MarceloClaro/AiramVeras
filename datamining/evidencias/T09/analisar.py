"""Execução real local T09; logs só de agregados/hashes, identidade só no restrito."""
from collections import Counter, defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.cenarios import projetar_cenario
from airam.predicao_gate import avaliar_prontidao_temporal


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_authenticated(relative, expected):
    p=ROOT/relative
    if sha(p)!=expected:
        raise ValueError('Hash de entrada divergente')
    return json.loads(p.read_text(encoding='utf-8'))


def write(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def summary(rows):
    valid=[r for r in rows if r['status']=='disponivel']
    return dict(cadastros=len(rows), disponiveis=len(valid), ausentes=len(rows)-len(valid),
        unidade='acertos_por_estudante', alvo_individual=18,
        atingiram_observado=sum(r['atingida'] for r in valid),
        atingiram_projetado=sum(r['atingida_projetada'] for r in valid),
        lacunas_observadas=dict(sorted(Counter(str(r['lacuna']) for r in valid).items())),
        lacunas_projetadas=dict(sorted(Counter(str(r['lacuna_projetada']) for r in valid).items())))


def main():
    source_public='5bfa87b38394d171589a7799751127dceb7d81587bbbfcefa67d2bb4a8420231'
    source_restricted='6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b'
    public=read_authenticated('estatistica/t05/checkpoint.json',source_public)
    restricted=read_authenticated('restrito/t05/checkpoint.json',source_restricted)
    config=json.loads((ROOT/'config/cenarios.json').read_text(encoding='utf-8'))
    evaluations=restricted['observado']['avaliacoes']
    # O gate recebe os metadados realmente existentes: não inventar comprovação.
    gate_rows={r['avaliacao_id']: {k:deepcopy(v) for k,v in r.items()
        if k not in {'aluno_local_id','avaliacao_local_id'}} for r in evaluations}
    gate=avaliar_prontidao_temporal(list(gate_rows.values()),[])
    assert gate['previsao_temporal_validada'] is False and gate['prontidao_inputs_temporais'] is False
    sources=dict(t05_publico_sha256=source_public,t05_restrito_sha256=source_restricted,
                 config_sha256=sha(ROOT/'config/cenarios.json'),coletor_sha256=sha(Path(__file__)))
    outputs, sensitivity, individuals = [], [], []
    contract=None
    for scope in public['metas_A']:
        context={k:scope[k] for k in ['ano_escolar','componente','nivel','turma']}
        selected=[dict(r,unidade='itens') for r in evaluations
            if r['ano_escolar']==scope['ano_escolar'] and r['componente']==scope['componente']
            and (scope['nivel']=='escola' or r['turma']==scope['turma'])]
        for scenario in config['cenarios']:
            result=projetar_cenario(selected,config['metas'],scenario['hipoteses'])
            contract={k:result[k] for k in ['tipo_resultado','premissas','unidade','comparabilidade','status_validacao']}
            # Confere a unidade real antes de divulgar alvo 18 no agregado.
            assert all(r['oportunidades'] in (22,None) for r in result['meta_B'])
            outputs.append(dict(context,cenario=scenario['nome'],hipoteses=result['hipoteses'],
                                meta_A=result['meta_A'],meta_B_resumo=summary(result['meta_B'])))
            if scope['nivel']=='escola':
                for original, projected in zip(selected,result['meta_B'],strict=True):
                    individuals.append(dict(cenario=scenario['nome'],
                        aluno_local_id=original['aluno_local_id'],avaliacao_local_id=original['avaliacao_local_id'],
                        ano_escolar=original['ano_escolar'],componente=original['componente'],turma=original['turma'],
                        resultado_observado=deepcopy(original),meta_B=projected))
        for exits in config['saidas_sensibilidade_institucional']:
            result=projetar_cenario(selected,config['metas'],{'saidas_adequado':exits})
            sensitivity.append(dict(context,saidas=exits,meta_A=result['meta_A']))
    others=[]; details=[]
    for component,table in [('ESCRITA','escrita'),('FLUENCIA','fluencia')]:
        own=[r for r in evaluations if r['componente']==component]
        measures=restricted['observado'][table]
        for year in sorted({r['ano_escolar'] for r in own}):
            apps=[r for r in own if r['ano_escolar']==year]
            units=sorted({r['unidade'] for r in measures if r['ano_escolar']==year})
            others.append(dict(ano_escolar=year,componente=component,nivel='escola',
                cadastros=len(apps),avaliados=sum(r['participacao'] for r in apps),
                unidades=units,categorias_contagens=dict(sorted(Counter(r['categoria'] for r in apps if r['participacao']).items())),
                meta_A_status='unidade_nao_aplicavel',meta_B_status='unidade_nao_aplicavel',
                medidas_disponiveis=sum(r['disponibilidade'] for r in measures if r['ano_escolar']==year)))
        by_application=defaultdict(list)
        for row in measures:
            by_application[row['avaliacao_local_id']].append(row)
        for row in own:
            details.append(dict(resultado_observado=deepcopy(row),
                medidas_observadas=deepcopy(by_application[row['avaliacao_local_id']]),
                meta_A_status='unidade_nao_aplicavel',meta_B_status='unidade_nao_aplicavel'))
    out=dict(versao_schema='airam-cenarios-t09-v1',fontes=sources,contrato=contract,gate_temporal=gate,
        cenarios=outputs,sensibilidade_meta_A=sensitivity,outros_instrumentos=others,
        limites=config['limites']+['Turma e escola se sobrepoem; nao somar linhas como pessoas distintas.',
            'Contagens hipoteticas de acertos nao alteram automaticamente categorias CAEd originais.',
            'Distancias individuais somente no checkpoint restrito local.'])
    private=dict(versao_schema='airam-cenarios-restritos-t09-v1',fontes=sources,contrato=contract,
        gate_temporal=gate,observado_referencia='restrito/t05/checkpoint.json',
        cenarios_individuais=individuals,outros_instrumentos=details)
    write(ROOT/'estatistica/t09/checkpoint.json',out)
    write(ROOT/'restrito/t09/checkpoint.json',private)
    report=dict(cenarios_agregados=len(outputs),sensibilidades=len(sensitivity),
        cenarios_individuais_restritos=len(individuals),outras_aplicacoes=len(details),
        previsao_temporal_validada=False,prontidao_inputs_temporais=False,
        publico_sha256=sha(ROOT/'estatistica/t09/checkpoint.json'),
        restrito_sha256=sha(ROOT/'restrito/t09/checkpoint.json'))
    write(ROOT/'evidencias/T09/analise-real-resultado.json',report)
    print(json.dumps(report))


if __name__=='__main__':
    main()
