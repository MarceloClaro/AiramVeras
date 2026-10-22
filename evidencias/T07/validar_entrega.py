"""Valida os schemas usados e ausência de identificadores reais no agregado."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[2]


def validate(value,schema):
    if 'oneOf' in schema:
        successes=0
        for option in schema['oneOf']:
            try:
                validate(value,option)
                successes+=1
            except AssertionError:
                pass
        assert successes==1,'Schema oneOf divergente'
        return
    if 'const' in schema:
        assert value==schema['const'],'Schema const divergente'
    if 'enum' in schema:
        assert value in schema['enum'],'Schema enum divergente'
    expected=schema.get('type')
    if expected:
        kinds=expected if isinstance(expected,list) else [expected]
        actual=('null' if value is None else 'boolean' if type(value) is bool else
                'integer' if type(value) is int else 'number' if type(value) is float else
                'string' if isinstance(value,str) else 'array' if isinstance(value,list) else
                'object' if isinstance(value,dict) else 'desconhecido')
        assert actual in kinds or (actual=='integer' and 'number' in kinds),'Schema tipo divergente'
    if 'pattern' in schema:
        assert re.fullmatch(schema['pattern'],value),'Schema pattern divergente'
    if isinstance(value,dict):
        props=schema.get('properties',{})
        assert all(k in value for k in schema.get('required',[])),'Schema campo ausente'
        for k,v in value.items():
            if k in props:
                validate(v,props[k])
            elif schema.get('additionalProperties') is False:
                raise AssertionError('Schema campo excedente')
            elif isinstance(schema.get('additionalProperties'),dict):
                validate(v,schema['additionalProperties'])
    if isinstance(value,list) and 'items' in schema:
        for v in value:
            validate(v,schema['items'])


def main():
    for data,definition in [('estatistica/t07/checkpoint.json','docs/esquema-t07.json'),
                            ('restrito/t07/checkpoint.json','docs/esquema-restrito-t07.json')]:
        validate(json.loads((ROOT/data).read_text(encoding='utf-8')),
                 json.loads((ROOT/definition).read_text(encoding='utf-8')))
    protected=json.loads((ROOT/'restrito/t05/checkpoint.json').read_text(encoding='utf-8'))
    tokens=set()
    def collect(value):
        if isinstance(value,dict):
            for k,v in value.items():
                if (k in ('aluno_local_id','avaliacao_local_id','nome','nome_normalizado')
                        and isinstance(v,str) and len(v)>3):
                    tokens.add(v)
                collect(v)
        elif isinstance(value,list):
            for v in value:
                collect(v)
    collect(protected)
    candidates=[ROOT/'estatistica/t07/checkpoint.json']+[p for p in (ROOT/'evidencias/T07').rglob('*')
                if p.is_file() and p.suffix in ('.json','.log','.py')]
    for path in candidates:
        content=path.read_text(encoding='utf-8-sig')
        assert not any(t in content for t in tokens),'Dado individual em artefato compartilhavel'
    pub=json.loads((ROOT/'estatistica/t07/checkpoint.json').read_text(encoding='utf-8'))
    summaries=[]
    for block in pub['blocos']:
        g=block['grafo']
        active_skills=sum(any(r[j]>0 for r in g['B']) for j in range(len(g['bncc'])))
        summaries.append(dict(ano=block['contexto']['ano_escolar'],componente=block['contexto']['componente'],
            policy=block['policy'],posicoes_associadas=block['posicoes_associadas'],
            nos=len(g['nos']),nos_ativos=sum(any(r) for r in g['B']),bncc_ativas=active_skills,
            isolados=sum(d==0 for d in g['graus']),
            um_passo=block['propagacoes']['1']['celulas_suportadas'],
            dois_passos=block['propagacoes']['2']['celulas_suportadas'],
            dois_sem_retorno=block['propagacoes']['2']['celulas_suportadas_sem_retorno']))
    report=dict(status='PASS',schemas=2,arquivos_verificados=len(candidates),
        validador='Subconjunto completo usado: type,const,enum,pattern,oneOf,required,properties,additionalProperties,items',
        hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in
            ['estatistica/t07/checkpoint.json','restrito/t07/checkpoint.json','docs/esquema-t07.json','docs/esquema-restrito-t07.json']},
        resumo=summaries,limites='Armazenamento restrito ignorado pelo Git; ACL nao certificada')
    (ROOT/'evidencias/T07/validacao-entrega.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(dict(status='PASS',schemas=2,arquivos_verificados=len(candidates))))


if __name__=='__main__':
    main()
