"""Contrato público do runtime oficial, independente do scratch SDD."""
import json
from pathlib import Path
import subprocess

from airam.cache import sha


def verificar_runtime(config):
    node=Path(config['node']); base=Path(config['base'])
    package=base/'node_modules/@oai/artifact-tool/package.json'
    if not node.is_file() or not package.is_file() or '.superpowers' in base.parts:
        raise ValueError('Runtime oficial indisponivel ou temporario')
    metadata=json.loads(package.read_text(encoding='utf-8'))
    if metadata.get('name')!='@oai/artifact-tool':raise ValueError('Pacote oficial divergente')
    probe=Path(__file__).resolve().parents[1]/'hooks/verificar-runtime.mjs'
    process=subprocess.run([str(node),str(probe),str(base)],capture_output=True,text=True,
        encoding='utf-8',timeout=60)
    if process.returncode:raise ValueError('Importacao publica do runtime falhou')
    result=json.loads(process.stdout)
    return result | {'codigo_saida':0,'AIRAM_ARTIFACT_RUNTIME':str(base.resolve()),
        'node_executavel':str(node.resolve()),'pacote_versao':metadata['version'],
        'pacote_manifesto_sha256':sha(package),'probe_sha256':sha(probe)}
