# -*- coding: utf-8 -*-
import re

with open(r'datamining/src/gerar_dossie_1000_laudas_multidisciplinar.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
for i, line in enumerate(lines, 1):
    # Check for dollar signs (LaTeX markers)
    if '$' in line and not line.strip().startswith('#'):
        print(f"Line {i} [LaTeX $]: {line.strip()[:100]}")
    # Check for suspicious backslashes not used for \n, \t, etc.
    bad_escapes = re.findall(r'\\[^nt"\'\\]', line)
    if bad_escapes:
        print(f"Line {i} [Escape]: {bad_escapes} in {line.strip()[:100]}")
