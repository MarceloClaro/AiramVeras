"""Entrada local. Hooks reais e recibos de operação; falhas nunca viram sucesso."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from airam.cache import dentro, sha
from airam.catalogo import catalogar, validar_fonte
from airam.gates import avaliar_gate
from airam.operacao import agora, gravar, gravar_versionado, iniciar, carregar_contratos
from airam.pipeline import analisar, validar_entradas

ROOT=Path(__file__).resolve().parents[1]


def configuracao(path):
    path=Path(path).resolve(strict=True)
    config=json.loads(path.read_text(encoding='utf-8-sig'))
    project=Path(config.get('projeto',ROOT)).resolve()
    sources=(project/config['raiz_fontes']).resolve()
    ref=config['baseline']; baseline=dentro(project,ref['caminho'])
    validar_fonte(baseline,ref['sha256'],project)
    return config,project,sources,json.loads(baseline.read_text(encoding='utf-8-sig'))


def acionar_hook(name,config,artifacts=None):
    shell=shutil.which('pwsh') or shutil.which('powershell')
    if not shell: raise ValueError('PowerShell indisponivel')
    args=[shell,'-NoProfile','-File',str(ROOT/'hooks'/(name+'.ps1')),
        '-Python',sys.executable,'-Config',str(config)]
    if artifacts: args+=['-Artifacts',str(artifacts)]
    result=subprocess.run(args,cwd=ROOT,capture_output=True,timeout=300)
    return {'nome':name,'codigo_saida':result.returncode,'disparo_real':True}


def main(argv=None):
    parser=argparse.ArgumentParser(description='Rotina local auditavel Airam Veras')
    parser.add_argument('comando',choices=['catalogar','validar','analisar','relatar','gate','executar'])
    parser.add_argument('--config',default='config/analise.json')
    parser.add_argument('--nome',default='preflight')
    parser.add_argument('--artefatos')
    args=parser.parse_args(argv)
    folder=None; receipt={'tipo':'operacional','versao_schema':'airam-operacao-v1','comando':args.comando,
        'timestamp':agora(),'codigo_saida':2,'estado':'bloqueado','hooks':[]}
    try:
        path=Path(args.config).resolve()
        config,project,sources,baseline=configuracao(path)
        os.environ['AIRAM_CONFIG']=str(path)
        inputs={p:dentro(sources,p) for p in baseline['fontes']}
        for label in ('cache_analise','checkpoint_ingestao'):
            if config.get(label):
                ref=config[label]; inputs[label]=dentro(project,ref['caminho'])
        folder,snapshot=iniciar(project,args.comando,path,inputs); receipt['snapshot_sha256']=snapshot
        if config.get('agentes'):
            receipt['integracao_core']=carregar_contratos(project,config['agentes'])
        if args.comando=='gate':
            artifacts=json.loads(Path(args.artefatos).read_text(encoding='utf-8-sig')) if args.artefatos else {'raiz':str(sources),'baseline':baseline}
            outcome=avaliar_gate(args.nome,artifacts)
            receipt.update(estado=outcome['estado'] if 'estado' in outcome else 'gate_avaliado',codigo_saida=outcome['codigo_saida'],resultado=outcome)
        else:
            hook=acionar_hook('preflight',path); receipt['hooks'].append(hook)
            if hook['codigo_saida']:
                receipt['codigo_saida']=hook['codigo_saida']
            elif args.comando=='validar':
                counts=validar_entradas(config,project,sources)
                receipt.update(estado='validacao_concluida',codigo_saida=0,fontes=len(baseline['fontes']),contagens=counts)
            elif args.comando=='catalogar':
                target=dentro(project,config['catalogo']['saida'])
                if not target.is_relative_to(project/'catalogo') or target in inputs.values():
                    raise ValueError('Destino do catalogo deve ser derivado e separado das fontes')
                records=catalogar(sources)
                receipt.update(estado='catalogo_concluido',codigo_saida=0,artefatos={str(target.relative_to(project)):gravar_versionado(target,records)})
            elif args.comando=='analisar':
                result=analisar(config,project,sources)
                receipt.update(estado='analise_disponibilizada',codigo_saida=0,resultado=result)
            else:
                receipt['motivo']='handoff_T10_aprovado_pendente'
    except (OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError):
        receipt.update(estado='bloqueado',codigo_saida=2,motivo='contrato_ou_dependencia_nao_verificado')
    receipt['fim']=agora()
    if folder: gravar(folder/'recibo.json',receipt)
    print(json.dumps(receipt,ensure_ascii=False))
    return receipt['codigo_saida']
