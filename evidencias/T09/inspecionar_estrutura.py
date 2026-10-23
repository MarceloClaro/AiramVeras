"""Somente contagens e nomes de campos; nenhum valor individual no log."""
import hashlib
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
p=root/'restrito/t05/checkpoint.json'
assert hashlib.sha256(p.read_bytes()).hexdigest()=='6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b'
d=json.loads(p.read_text(encoding='utf-8'))
print(json.dumps({k:{'quantidade':len(v),'campos':sorted({x for r in v for x in r})} for k,v in d['observado'].items()}, ensure_ascii=False))
