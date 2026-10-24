"""Recibos operacionais, distintos das fases TDD e de inferência Core."""
from datetime import datetime, timezone
import json
from pathlib import Path
import uuid

from airam.cache import sha, runtime, dentro
from airam.catalogo import validar_fonte


def agora(): return datetime.now(timezone.utc).isoformat()


def gravar(path,obj):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    raw=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
    temp=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    try:
        temp.write_bytes(raw); temp.replace(path)
    finally:
        if temp.exists(): temp.unlink()
    return sha(path)


def gravar_versionado(path,obj):
    path=Path(path)
    if path.is_file():
        old=path.read_bytes()
        expected=(json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
        if old!=expected:
            archive=path.parent/'versoes'/sha(path)/path.name
            archive.parent.mkdir(parents=True,exist_ok=True)
            if archive.exists() and archive.read_bytes()!=old:
                raise ValueError('Versao anterior divergente')
            archive.write_bytes(old)
    return gravar(path,obj)


def carregar_contratos(root,reference):
    path=dentro(root,reference['caminho']); validar_fonte(path,reference['sha256'],root)
    contract=json.loads(path.read_text(encoding='utf-8-sig'))
    if contract.get('primario')!='marceloclaro': raise ValueError('Coordenador Core divergente')
    states=[]
    for profile in contract['perfis']:
        ref=profile['recibo']; receipt=dentro(root,ref['caminho']); validar_fonte(receipt,ref['sha256'],root)
        data=json.loads(receipt.read_text(encoding='utf-8-sig'))
        if 'execucao' in data:
            data=data['execucao'] | {'spec_id':data['chamada_execucao']['spec_id']}
        state=estado_agente({k:profile.get(k,False) for k in ('configurado','validado','ativado')}|data)
        states.append({'id':profile['id'],**state})
    return {'primario':'marceloclaro','perfis':states,
        'eventos_sessao':estado_evento(contract['eventos_sessao']),
        'dados_externos':'nenhum dado individual transmitido'}


def iniciar(root,command,config_path,entradas=None):
    folder=Path(root)/'evidencias/operacionais'/uuid.uuid4().hex
    folder.mkdir(parents=True)
    code_root=Path(__file__).resolve().parents[1]
    code={p.relative_to(code_root).as_posix():sha(p) for dirname in ('airam','hooks')
        for p in (code_root/dirname).glob('*') if p.is_file() and p.suffix in ('.py','.ps1','.mjs')}
    before={'tipo':'snapshot_operacional','timestamp':agora(),'comando':command,
        'config_sha256':sha(config_path),'codigo':code,'runtime':runtime(),
        'entradas':{label:sha(path) if Path(path).is_file() else None for label,path in (entradas or {}).items()}}
    digest=gravar(folder/'antes.json',before)
    return folder,digest


def estado_agente(receipt):
    # Etapas e entrega só são afirmadas mediante recibo de execução positiva.
    executed=(receipt.get('status')=='completed' and bool(receipt.get('agent_id'))
        and type(receipt.get('steps')) is int and receipt['steps']>0
        and bool(receipt.get('spec_id')) and bool(receipt.get('recibo_execucao_sha256')))
    return {k:receipt.get(k,False) for k in ('configurado','validado','ativado')} | {
        'spec_id':receipt.get('spec_id'),'status':receipt.get('status','nao_comprovado'),
        'executado':executed,'testado':executed and receipt.get('testado') is True,
        'entregue':executed and bool(receipt.get('artefato_sha256'))}


def estado_evento(receipt):
    verified=(receipt.get('disparo_real') is True and receipt.get('codigo_saida')==0
        and bool(receipt.get('harness')) and bool(receipt.get('recibo_sha256')))
    return {'configurado':receipt.get('configurado') is True,
        'ativo_verificado':verified,'estado':'ativo_verificado' if verified else 'contract_only'}
