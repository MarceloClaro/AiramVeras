"""Resolução pública somente leitura, sem criar planilha nem repetir marcador."""
import json
from pathlib import Path
import pytest
from test_cli import api,ROOT


def test_runtime_ausente_falha_sem_instalar(tmp_path):
    module=api('runtime_artifact')
    with pytest.raises(ValueError):module.verificar_runtime({'node':str(tmp_path/'missing.exe'),'base':str(tmp_path)})
    assert not list(tmp_path.iterdir())


def test_runtime_oficial_importa_exports_sem_scratch_ou_autoria():
    module=api('runtime_artifact')
    path=ROOT/'config/runtime.json'
    assert path.is_file(),'Configuracao persistente do runtime ausente'
    result=module.verificar_runtime(json.loads(path.read_text(encoding='utf-8')))
    assert result['codigo_saida']==0
    assert result['exports']=={'Workbook':True,'SpreadsheetFile':True,'FileBlob':True}
    assert result['autoria_executada'] is False
    assert '.superpowers' not in result['AIRAM_ARTIFACT_RUNTIME']
