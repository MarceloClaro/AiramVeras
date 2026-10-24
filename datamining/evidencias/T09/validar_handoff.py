"""Executa a validação local de schemas sem ecoar dados individuais."""
from pathlib import Path
import subprocess

script = Path(__file__).with_suffix('.ps1')
result = subprocess.run(['pwsh', '-NoProfile', '-File', str(script)],
                        capture_output=True, text=True, encoding='utf-8')
print(result.stdout.strip())
if result.returncode:
    print('validacao_falhou_codigo=' + str(result.returncode))
raise SystemExit(result.returncode)
