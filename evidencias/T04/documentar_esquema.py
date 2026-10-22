"""Gera JSON Schema fechado da interface observada no checkpoint público versionado."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def schema(values):
    variants = []
    for kind, name in [(dict, 'object'), (list, 'array'), (str, 'string'),
                       (int, 'integer'), (float, 'number'), (bool, 'boolean'), (type(None), 'null')]:
        group = [v for v in values if type(v) is kind]
        if not group:
            continue
        item = {'type': name}
        if kind is dict:
            keys = sorted({k for v in group for k in v})
            item.update(properties={k: schema([v[k] for v in group if k in v]) for k in keys},
                        required=[k for k in keys if all(k in v for v in group)], additionalProperties=False)
        if kind is list:
            elements = [e for v in group for e in v]
            item['items'] = schema(elements) if elements else {}
        variants.append(item)
    return variants[0] if len(variants) == 1 else {'anyOf': variants}


data = json.loads((ROOT / 'curriculo/t04/checkpoint.json').read_text(encoding='utf-8'))
result = schema([data])
result['$schema'] = 'https://json-schema.org/draft/2020-12/schema'
result['title'] = 'Checkpoint curricular Airam T04 v1 (interface observada)'
result['properties']['versao_schema'] = {'const': 'airam-curriculo-t04-v1'}
result['properties']['bncc'] = {'type': 'object', 'additionalProperties': schema(list(data['bncc'].values()))}
for field in ['ano_tabela', 'ano_avaliado', 'pagina_matriz']:
    # Nulos são permitidos para posições sem ocorrência nas APIs; checkpoint atual está coberto.
    prop = result['properties']['vinculos_posicoes']['items']['properties'][field]
    result['properties']['vinculos_posicoes']['items']['properties'][field] = {'anyOf': [prop, {'type': 'null'}]}
(ROOT / 'docs/esquema-t04.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'schema': 'docs/esquema-t04.json', 'versao_schema': data['versao_schema']}))
