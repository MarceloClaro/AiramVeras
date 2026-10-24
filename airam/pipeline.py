"""Composição local das entregas revisadas; reuso não é nova inferência."""
import json
from pathlib import Path

from airam.bncc import carregar_bncc
from airam.cache import dentro, runtime, sha, verificar_cache
from airam.catalogo import catalogar, validar_fonte
from airam.ingestao import ler_exportacoes
from airam.persistencia import persistir
from airam.gates import validar_publico
from airam.operacao import gravar_versionado


def _perfis_sem_nominais(value,path=()):
    """Renomeia somente títulos de perfis nas posições documentadas T08."""
    allowed={('instrumentos','*','perfis_regras','*'),('instrumentos','*','perfis_observado','*'),
        ('unidades_proprias','*','perfis','*'),
        *(('instrumentos','*','cenarios','*','perfis',arm,'*') for arm in
            ('observado_controle','observado_total','propagado_controle'))}
    if isinstance(value,list): return [_perfis_sem_nominais(v,path+('*',)) for v in value]
    if isinstance(value,dict):
        return {('titulo_perfil' if k=='nome' and path in allowed else k):
            _perfis_sem_nominais(v,path+(k,)) for k,v in value.items()}
    return value


def tabelas_analiticas(project,manifest):
    tables=json.loads((project/'restrito/t03/tabelas.json').read_text(encoding='utf-8-sig'))
    for task,fields in {'t05':['metricas_alunos','metas_individuais'],
        't07':['blocos','visoes_aluno'],'t08':['instrumentos','unidades_proprias'],
        't09':['cenarios_individuais','outros_instrumentos']}.items():
        relative=f'restrito/{task}/checkpoint.json'
        if relative not in manifest['saidas']: continue
        data=json.loads((project/relative).read_text(encoding='utf-8-sig'))
        if task=='t08': data=_perfis_sem_nominais(data)
        for field in fields: tables[task+'_'+field]=data[field]
    for relative,fields in {'curriculo/t04/checkpoint.json':['posicoes','vinculos_posicoes'],
        'estatistica/t05/checkpoint.json':['agregados','metas_A'],
        'estatistica/t06/entrega/checkpoint.json':['associacoes']}.items():
        if relative not in manifest['saidas']: continue
        data=json.loads((project/relative).read_text(encoding='utf-8-sig'))
        task=relative.split('/')[1]
        for field in fields: tables[task+'_'+field.lower()]=data[field]
    return tables


def validar_entradas(config,project,sources):
    counts={}
    declared=config.get('fontes',{})
    if 'bncc_canonico' in declared:
        ref=declared['bncc_canonico']; data=carregar_bncc(sources/ref['caminho'],ref['commit'])
        counts['habilidades_bncc']=len(data)
    if 'coleta_ciclo_i_2026' in declared:
        tables=ler_exportacoes(catalogar(sources))
        counts.update({k:len(v) for k,v in tables.items()})
        if config.get('checkpoint_ingestao'):
            ref=config['checkpoint_ingestao']; path=dentro(project,ref['caminho'])
            validar_fonte(path,ref['sha256'],project)
            if json.loads(path.read_text(encoding='utf-8-sig')) != tables:
                raise ValueError('Reingestao difere do checkpoint autenticado')
    return counts


def analisar(config,project,sources):
    """Autentica artefatos aprovados antes de abrir conteúdo individual.

    Configuração/calculador diferente invalida esta versão da análise. Não dispara
    coletores históricos que contêm pins fixos nem refaz inferência dispendiosa
    silenciosamente. Uma nova versão requer o produtor e sua contraprova próprios.
    """
    ref=config['cache_analise']; path=dentro(project,ref['caminho'])
    validar_fonte(path,ref['sha256'],project)
    manifest=json.loads(path.read_text(encoding='utf-8-sig'))
    check=verificar_cache(project,manifest,runtime())
    if not check['reutilizavel']:
        raise ValueError('Cache invalido: requer nova execucao analitica e contraprova')
    if any(config.get(k)!=v for k,v in manifest.get('parametros',{}).items()):
        raise ValueError('Parametros alterados: requer nova execucao analitica')
    counts=validar_entradas(config,project,sources)
    private='restrito/t03/tabelas.json'; public='estatistica/t05/checkpoint.json'
    temporal='estatistica/t09/checkpoint.json'
    if any(p not in manifest['saidas'] for p in (private,public,temporal)):
        raise ValueError('Contrato analitico incompleto')
    tables=tabelas_analiticas(project,manifest)
    persisted=persistir(tables,project/'restrito/banco',project,manifest['saidas'])
    aggregate=json.loads((project/public).read_text(encoding='utf-8-sig'))
    # Seleção de tabela, sem somar níveis H/totais ou escola/turma.
    validar_publico(aggregate)
    digest=sha(project/public)
    destination=project/'relatorios/agregados'/digest
    gravar_versionado(destination/'estatistica.json',aggregate)
    import csv
    outputs={}
    for name in ('agregados','metas_A'):
        rows=aggregate[name]; columns=sorted({k for row in rows for k in row})
        target=destination/(name+'.csv')
        with target.open('w',encoding='utf-8-sig',newline='') as stream:
            writer=csv.DictWriter(stream,fieldnames=columns); writer.writeheader()
            for row in rows:
                writer.writerow({k:json.dumps(v,ensure_ascii=False,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()})
        outputs[target.relative_to(project).as_posix()]=sha(target)
    temporal_data=json.loads((project/temporal).read_text(encoding='utf-8-sig'))
    gate=temporal_data.get('gate_temporal',temporal_data.get('temporalidade',{}))
    return {'modo':'reutilizacao_autenticada','nova_inferencia':False,'cache_sha256':sha(path),
        'contagens_ingestao':counts,'persistencia_sha256':sha(persisted['manifesto']),
        'sqlite':str(Path(persisted['sqlite']).relative_to(project)),
        'agregados':outputs,'previsao_temporal_validada':False,
        'cenarios_disponiveis':gate.get('cenarios_disponiveis',True),
        'limites':['Dados pseudonimizados permanecem pessoais e restritos.',
            'Reutilizacao autenticada de entregas revisadas, sem nova inferencia.',
            'Validacao local; T02 RED inicial sem hashes/versoes contemporaneos.']}
