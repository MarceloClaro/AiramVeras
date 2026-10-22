"""Conferência final de integridade, minimização e esquema do handoff público."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(value):
    if isinstance(value, dict):
        assert not {'nome', 'aluno_local_id', 'matricula_local_id', 'turma', 'acertos',
                    'oportunidades', 'percentual', 'participacao', 'taxa'} & value.keys()
        for child in value.values():
            inspect(child)
    elif isinstance(value, list):
        for child in value:
            inspect(child)


baseline = json.loads((ROOT / 'evidencias/T04/red-funcional-antes.json').read_text(encoding='utf-8'))
hashes = {}
for filename, expected in baseline['hashes_dados'].items():
    actual = digest(ROOT / filename)
    assert actual == expected, 'Entrada original modificada'
    hashes[filename] = dict(antes=expected, depois=actual, preservada=True)
mutations = json.loads((ROOT / 'evidencias/T04/mutacoes-resumo.json').read_text(encoding='utf-8'))
for row in mutations:
    filename = 'airam/matriz_cnca.py' if row['mutacao'] == 'centro_ciclo' else 'airam/vinculos.py'
    assert digest(ROOT / filename) == row['original_sha256'], 'Codigo temporariamente mutado nao restaurado'
checkpoint = ROOT / 'curriculo/t04/checkpoint.json'
inspect(json.loads(checkpoint.read_text(encoding='utf-8')))
powershell = shutil.which('pwsh')
assert powershell
command = "$taskValido = Test-Json -Json (Get-Content 'curriculo/t04/checkpoint.json' -Raw) -SchemaFile 'docs/esquema-t04.json' -ErrorAction Stop; if (!$taskValido) { exit 1 }; [Console]::WriteLine($PSVersionTable.PSVersion.ToString())"
validation = subprocess.run([powershell, '-NoProfile', '-NonInteractive', '-Command', command],
                             cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
assert validation.returncode == 0, validation.stderr
assert not subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT.parent / 'bncc-dados'), 'Clone fonte alterado'
result = dict(status='PASS', fontes_imutaveis=hashes, fontes_originais_nunca_mutadas=True,
    arquivos_de_codigo_temporariamente_mutados=['airam/matriz_cnca.py', 'airam/vinculos.py'],
    codigo_restaurado_por_bytes=True, checkpoint_sha256=digest(checkpoint),
    esquema_sha256=digest(ROOT / 'docs/esquema-t04.json'), validacao_esquema='Test-Json',
    powershell=validation.stdout.strip(), minimizacao='Sem campos individuais/medidas no checkpoint curricular',
    bncc_integridade='HEAD fixado e bytes canonicos comparados ao blob Git, somente CRLF/LF normalizados')
(ROOT / 'evidencias/T04/auto-revisao.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=False))
