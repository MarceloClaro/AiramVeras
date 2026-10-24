"""Reutilização local autenticada: jamais registra cache como nova inferência."""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dentro(root, relative):
    root=Path(root).resolve(); path=(root/relative).resolve()
    if not path.is_relative_to(root):
        raise ValueError('Caminho fora da raiz autorizada')
    return path


def runtime():
    return {'python':platform.python_version(),'sistema':platform.system(),
        'arquitetura':platform.machine(), 'bibliotecas':{
            name:importlib.metadata.version(name) for name in
            ('numpy','scipy','scikit-learn','threadpoolctl','pandas','pdfplumber','pypdf')}}


def criar_manifesto(root, entradas, codigo, config, saidas, versoes, origem):
    """Somente após execução concluída; não promove artefato histórico por existência."""
    groups={name:{p:sha(dentro(root,p)) for p in paths} for name,paths in
        [('entradas',entradas),('codigo',codigo),('config',config),('saidas',saidas)]}
    if not all(groups.values()) or not versoes or not origem:
        raise ValueError('Contrato de reutilizacao incompleto')
    return {'versao_schema':'airam-cache-v1',**groups,'runtime':versoes,'origem':origem}


def verificar_cache(root, manifest, versoes):
    reasons=[]
    if manifest.get('versao_schema')!='airam-cache-v1' or not manifest.get('origem'):
        reasons.append('contrato_invalido')
    for group in ('entradas','codigo','config','saidas'):
        values=manifest.get(group)
        if not isinstance(values,dict) or not values:
            reasons.append(group+'_ausente'); continue
        for path, expected in values.items():
            try:
                if sha(dentro(root,path)) != expected: reasons.append(group+'_divergente')
            except (OSError,ValueError): reasons.append(group+'_indisponivel')
    if manifest.get('runtime') != versoes: reasons.append('runtime_divergente')
    return {'reutilizavel':not reasons,'nova_inferencia':False,'motivos':sorted(set(reasons))}
