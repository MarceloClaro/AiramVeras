"""Validação estrutural fechada, hashes e síntese agregada de sensibilidade."""
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]


def main():
    spec=importlib.util.spec_from_file_location('validador_t07',ROOT/'evidencias/T07/validar_entrega.py')
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    paths=['estatistica/t08/checkpoint.json','restrito/t08/checkpoint.json',
           'docs/esquema-t08.json','docs/esquema-restrito-t08.json','config/agrupamentos.json']
    for source,definition in [(paths[0],paths[2]),(paths[1],paths[3])]:
        module.validate(json.loads((ROOT/source).read_text(encoding='utf-8')),
                        json.loads((ROOT/definition).read_text(encoding='utf-8')))
    public=json.loads((ROOT/paths[0]).read_text(encoding='utf-8'))
    summary=[]
    for inst in public['instrumentos']:
        scenarios=[]
        for scenario in inst['cenarios']:
            scenarios.append(dict(cenario=scenario['cenario'],status=scenario['status'],
                features_comuns=scenario['selecao']['features_comuns'],
                resultados={arm:dict(k=r['k'],status=r['status']) for arm,r in scenario['resultados'].items()},
                mudancas_limiares=sum(s['mudou_selecao'] for ss in scenario['sensibilidade_limiares'].values() for s in ss),
                cobertura_muda_eixos=sum(not s['mesmos_eixos_e_valores'] for s in scenario['sensibilidade_cobertura'])))
        summary.append(dict(ano=inst['contexto']['ano_escolar'],componente=inst['contexto']['componente'],
            observado_k=inst['observado_operacional']['k'],
            mudancas_limiares_observado=sum(s['mudou_selecao'] for s in inst['sensibilidade_observado']),cenarios=scenarios))
    report=dict(status='PASS',schemas=2,hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
        validador='Subconjunto completo utilizado: type,const,oneOf,required,properties,additionalProperties,items',
        natureza_schema='estrutura efetiva versionada; sem alegar validacao independente do conteudo',
        sensibilidade=summary,limites='Revisao docente, data de reavaliacao, eficacia e validacao externa pendentes')
    (ROOT/'evidencias/T08/validacao-entrega.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PASS',schemas=2,instrumentos=len(summary),
        mudancas_limiares=sum(x['mudancas_limiares_observado']+sum(s['mudancas_limiares'] for s in x['cenarios']) for x in summary),
        cobertura_muda_eixos=sum(s['cobertura_muda_eixos'] for x in summary for s in x['cenarios']))))


if __name__=='__main__': main()
