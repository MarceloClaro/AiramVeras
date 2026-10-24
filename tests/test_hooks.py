"""T50: executar PowerShell real, observar códigos e ausência de efeitos posteriores."""
import json
from pathlib import Path
import shutil
import subprocess
import sys

from test_cli import ROOT, api, fixture_config, invoke, release_fixture


def run_hook(name,*args):
    path=ROOT/'hooks'/(name+'.ps1')
    assert path.is_file(), 'Hook T11 ausente'
    shell=shutil.which('pwsh') or shutil.which('powershell')
    assert shell, 'Ambiente sem PowerShell'
    return subprocess.run([shell,'-NoProfile','-File',str(path),'-Python',sys.executable,*args],
        cwd=ROOT,capture_output=True,text=True)


def test_preflight_real_falha_interrompe_cli_antes_catalogo(tmp_path):
    config, original=fixture_config(tmp_path)
    original.write_text('ATAQUE ARTIFICIAL')
    assert run_hook('preflight','-Config',str(config)).returncode != 0
    result=invoke(config,'catalogar')
    assert result.returncode != 0
    assert not (tmp_path/'catalogo/fontes.json').exists()


def test_release_real_propaga_falha_e_sucesso(tmp_path):
    api('cli'); config,_=fixture_config(tmp_path)
    fixture=release_fixture(tmp_path)
    manifest=tmp_path/'release.json'; manifest.write_text(json.dumps(fixture))
    assert run_hook('release','-Config',str(config),'-Artifacts',str(manifest)).returncode==0
    (tmp_path/'agregado.json').write_text('adulterado')
    assert run_hook('release','-Config',str(config),'-Artifacts',str(manifest)).returncode != 0
