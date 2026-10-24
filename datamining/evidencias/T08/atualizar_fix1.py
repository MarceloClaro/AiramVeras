"""FIX1: recalcula somente perfis E/F; autentica e reutiliza os clusters anteriores."""
from copy import deepcopy
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from evidencias.T08.analisar import EXPECTED, produzir, digest

OLD={
    'restrito/t08/checkpoint.json':'17d71689ba27724f8b165358e810210ee7c6d4a9001dbaa403f125a47b8c1e3e',
    'estatistica/t08/checkpoint.json':'d298a8754ad6e896c7e1077dcccc35c963a90777d82f4fb40c90e2224e4cacc1',
    'estatistica/t08/perfis-pedagogicos.md':'2238f99d6b95b8305dae6919cf2046b8a4faefea57b7f49d535a4ee068fcd0d1',
    'docs/esquema-t08.json':'b580d6bd2c1ea59d7fc962aae6341ee04ce2856dce5184a3899eb5bfef176f9c',
    'docs/esquema-restrito-t08.json':'296ab70598581008f2be5a3e7e7c369de6f93c5c2e832396568ea26e2fc80a0c'}


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path): return json.loads(path.read_text(encoding='utf-8'))


def archive(path):
    if path.startswith('restrito/'):
        return ROOT/'restrito/t08/versoes/pre-fix1'/Path(path).name
    return ROOT/'estatistica/t08/versoes/pre-fix1'/path


def store(path,value):
    raw=(json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def main():
    snapshot_path=ROOT/'evidencias/T08/analise02-antes.json'
    original_snapshot=read(snapshot_path)
    for path,expected in EXPECTED.items():
        if sha(ROOT/path)!=expected: raise ValueError('Fonte primaria divergente')
    unchanged={p:h for p,h in original_snapshot['hashes_codigo'].items()
               if (p.startswith('airam/') and p!='airam/perfis_grupo.py') or p=='config/agrupamentos.json'}
    for path,expected in unchanged.items():
        if sha(ROOT/path)!=expected: raise ValueError('Modulo/calculo reutilizado divergente')
    versions={name:importlib.metadata.version(name) for name in ('numpy','scipy','scikit-learn','threadpoolctl')}
    if any(original_snapshot['versoes'][name]!=version for name,version in versions.items()):
        raise ValueError('Runtime dos calculos reutilizados divergente')
    for path,expected in OLD.items():
        target=archive(path)
        if not target.exists():
            if sha(ROOT/path)!=expected: raise ValueError('Artefato anterior nao autenticado')
            target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(ROOT/path,target)
        if sha(target)!=expected: raise ValueError('Arquivo historico divergente')
    old_private=read(archive('restrito/t08/checkpoint.json'))
    old_public=read(archive('estatistica/t08/checkpoint.json'))
    config=read(ROOT/'config/agrupamentos.json')
    if old_private['config']!=config or old_public['config']!=config:
        raise ValueError('Configuracao anterior divergente')
    source=read(ROOT/'restrito/t05/checkpoint.json')
    only_ef={'observado':{**source['observado'],'habilidades':[]}}
    fresh_private,fresh_public=produzir(only_ef,{'blocos':[]},{'blocos':[]},{'vinculos_posicoes':[]},config)
    if fresh_private['instrumentos'] or fresh_private['execucao']['estimandos_distintos_ajustados']!=0:
        raise ValueError('FIX1 nao pode ajustar clusters')
    private=deepcopy(old_private); public=deepcopy(old_public)
    provenance=dict(fix='T08-FIX1-I1',base_commit='b375768e6ece19a6d15aca7914868d1e016c12c4',
        checkpoints_anteriores_sha256={p:h for p,h in OLD.items() if p.endswith('checkpoint.json')},
        snapshot_ajustes_originais='evidencias/T08/analise02-antes.json',snapshot_ajustes_sha256=sha(snapshot_path),
        modulos_config_reutilizados_sha256=unchanged,versoes_verificadas=versions,
        calculos_reutilizados='instrumentos L/M completos, todas as particoes e sensibilidades; sem reexecucao de clustering',
        calculos_novos='somente grupos por regras/perfis/cobertura E/F a partir de T05 autenticado',
        novos_ajustes_clusters=0,modulo_perfis_atual_sha256=sha(ROOT/'airam/perfis_grupo.py'))
    for target,fresh,old in ((private,fresh_private,old_private),(public,fresh_public,old_public)):
        target['versao_schema']=fresh['versao_schema']
        target['unidades_proprias']=fresh['unidades_proprias']
        target['proveniencia_fix1']=provenance
        if target['instrumentos']!=old['instrumentos']:
            raise ValueError('Instrumentos L/M alterados no FIX1')
        if [u['contexto'] for u in target['unidades_proprias']]!=[u['contexto'] for u in old['unidades_proprias']]:
            raise ValueError('Universo E/F alterado no FIX1')
    h_private=store(ROOT/'restrito/t08/checkpoint.json',private)
    public['checkpoint_restrito_sha256']=h_private
    h_public=store(ROOT/'estatistica/t08/checkpoint.json',public)
    coverage=[dict(ano=u['contexto']['ano_escolar'],componente=u['contexto']['componente'],
                   **u['regras']['cobertura']) for u in private['unidades_proprias']]
    report=dict(status='PASS',checkpoint_restrito_sha256=h_private,checkpoint_agregado_sha256=h_public,
        instrumentos_reutilizados_sha256=digest(private['instrumentos']),
        instrumentos_publicos_reutilizados_sha256=digest(public['instrumentos']),
        igualdade_LM_antes_depois=True,novos_ajustes_clusters=0,cobertura_ef=coverage,
        proveniencia=provenance)
    store(ROOT/'evidencias/T08/fix1-atualizacao-resultado.json',report)
    print(json.dumps(dict(status='PASS',contextos_ef=len(coverage),novos_ajustes_clusters=0,
        checkpoint_restrito_sha256=h_private,checkpoint_agregado_sha256=h_public)))


if __name__=='__main__': main()
