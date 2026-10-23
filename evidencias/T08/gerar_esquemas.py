"""Documenta a estrutura efetiva v1; não certifica decisões estatísticas."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
DYNAMIC={'turmas','categorias_caed_originais','falhas','fontes'}


def schema(values,key=''):
    groups={}
    for v in values:
        kind=('null' if v is None else 'boolean' if type(v) is bool else 'number' if isinstance(v,(int,float))
              else 'string' if isinstance(v,str) else 'array' if isinstance(v,list) else 'object')
        groups.setdefault(kind,[]).append(v)
    if not groups: return {}
    if len(groups)>1:
        return {'oneOf':[schema(items,key) for _,items in sorted(groups.items())]}
    kind,items=next(iter(groups.items())); result={'type':kind}
    if kind=='object':
        if key in DYNAMIC:
            result['additionalProperties']=schema([v for obj in items for v in obj.values()])
        else:
            keys=sorted(set().union(*(obj.keys() for obj in items)))
            result['properties']={k:schema([obj[k] for obj in items if k in obj],k) for k in keys}
            result['required']=sorted(set(items[0]).intersection(*(set(obj) for obj in items[1:])))
            result['additionalProperties']=False
    elif kind=='array':
        result['items']=schema([v for item in items for v in item],key)
    return result


def main():
    output={}
    for source,target in [('estatistica/t08/checkpoint.json','docs/esquema-t08.json'),
                          ('restrito/t08/checkpoint.json','docs/esquema-restrito-t08.json')]:
        data=json.loads((ROOT/source).read_text(encoding='utf-8'))
        definition=schema([data]); definition['$schema']='https://json-schema.org/draft/2020-12/schema'
        definition['$id']=data['versao_schema']
        definition['properties']['versao_schema']={'const':data['versao_schema']}
        raw=(json.dumps(definition,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
        (ROOT/target).write_bytes(raw); output[target]=hashlib.sha256(raw).hexdigest()
    print(json.dumps(dict(status='esquemas_estruturais_gerados',hashes=output)))


if __name__=='__main__': main()
