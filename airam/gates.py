"""Gates fail-closed; indisponibilidade temporal não bloqueia análise transversal."""
import json
import csv
from pathlib import Path
import unicodedata

from airam.cache import dentro, sha
from airam.catalogo import validar_fonte
from airam.predicao_gate import avaliar_prontidao_temporal


def validar_publico(value):
    if isinstance(value,dict):
        for key,item in value.items():
            normalized=''.join(c for c in unicodedata.normalize('NFKD',str(key).lower()) if not unicodedata.combining(c))
            if any(word in normalized for word in ('nome','aluno_local_id','avaliacao_local_id','matricula','pseudonimo','membros','intervencao','metricas_alunos','metas_individuais')):
                raise ValueError('Campo individual em saida publica')
            validar_publico(item)
    elif isinstance(value,list):
        for item in value: validar_publico(item)


def _release(a):
    root=Path(a['raiz'])
    if not a.get('limites') or not a.get('artefatos'):
        raise ValueError('Entrega incompleta')
    receipts=a['recibos']
    for kind in ('testes','contraprova','inspecao'):
        r=receipts[kind]; path=dentro(root,r['caminho'])
        validar_fonte(path,r['sha256'],root)
        evidence=json.loads(path.read_text(encoding='utf-8-sig'))
        if type(evidence.get('codigo_saida')) is not int or evidence['codigo_saida']!=0:
            raise ValueError('Evidencia com falha')
        if evidence.get('estado') not in ('PASS','GREEN','REFACTOR','CONCLUIDO'):
            raise ValueError('Evidencia sem conclusao verificada')
        if kind=='testes':
            snapshot=path.parent/evidence['snapshot']; log=path.parent/evidence['log']
            validar_fonte(snapshot,evidence['snapshot_sha256'],root)
            validar_fonte(log,evidence['log_sha256'],root)
            previous=json.loads(snapshot.read_text(encoding='utf-8-sig'))
            if not previous.get('hashes_codigo'):raise ValueError('Testes sem estado previo')
            for relative,expected in previous['hashes_codigo'].items():
                validar_fonte(dentro(root,relative),expected,root)
    for p,h in a['artefatos'].items(): validar_fonte(dentro(root,p),h,root)
    trace=a['rastreabilidade']
    if {r['requisito'] for r in trace} != {'R'+str(i) for i in range(1,25)}:
        raise ValueError('Rastreabilidade incompleta')
    for r in trace:
        if not r.get('testes') or not r.get('artefatos') or not r.get('recibos') or any(p not in a['artefatos'] for p in r['artefatos']) or any(p not in receipts for p in r['recibos']):
            raise ValueError('Rastreabilidade incompleta')
    for p in a['publicos']:
        if p not in a['artefatos']: raise ValueError('Saida publica nao autenticada')
        path=dentro(root,p)
        if path.suffix.lower()=='.json': validar_publico(json.loads(path.read_text(encoding='utf-8-sig')))
        elif path.suffix.lower()=='.csv':
            with path.open(encoding='utf-8-sig',newline='') as stream:
                for row in csv.DictReader(stream):
                    validar_publico(row)
                    for value in row.values():
                        if value and value.lstrip().startswith(('{','[')):
                            validar_publico(json.loads(value))
        elif path.suffix.lower() not in ('.html','.csv','.svg','.png','.md'):
            raise ValueError('Formato publico nao aprovado')
    # Varredura local adicional de nomes e IDs conhecidos; termos nunca entram no recibo.
    if a.get('mapa_nominal'):
        ref=a['mapa_nominal']; path=dentro(root,ref['caminho']); validar_fonte(path,ref['sha256'],root)
        terms={str(v) for row in json.loads(path.read_text(encoding='utf-8-sig')) for k,v in row.items()
            if ('nome' in k or k in ('aluno_local_id','matricula_local_id')) and isinstance(v,str) and v}
        for p in a['publicos']:
            path=dentro(root,p)
            if path.suffix.lower()!='.png':
                text=path.read_text(encoding='utf-8-sig')
                if any(term in text for term in terms): raise ValueError('Dado pessoal em saida publica')
    return {'estado':'liberacao_computacional_local','codigo_saida':0,'ressalva_tdd':'T02 RED inicial sem hashes/versoes contemporaneos; historico preservado'}


def avaliar_gate(name,artifacts):
    try:
        if name in ('temporal','previsao'):
            result=avaliar_prontidao_temporal(artifacts['avaliacoes'],artifacts['vinculos'])
            return result | {'analise_disponivel':True,'codigo_saida':0 if name=='temporal' else 4}
        if name in ('preflight','integridade'):
            root=Path(artifacts['raiz']); baseline=artifacts['baseline']
            if not baseline.get('fontes'): raise ValueError('Baseline ausente')
            for p,h in baseline['fontes'].items(): validar_fonte(dentro(root,p),h,root)
            return {'estado':'integridade_verificada','codigo_saida':0,'fontes':len(baseline['fontes'])}
        if name=='release': return _release(artifacts)
        raise ValueError('Gate desconhecido')
    except (OSError,ValueError,KeyError,TypeError):
        return {'estado':'bloqueado','codigo_saida':2,'gate':name,'motivo':'contrato_ou_evidencia_nao_verificado'}
