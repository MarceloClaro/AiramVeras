"""Preserva versões derivadas anteriores ao ajuste visual; nunca segue junctions."""
from pathlib import Path
import hashlib
import json
import shutil
import sys

ROOT=Path(__file__).resolve().parents[2]
FILES=['relatorios/t10/relatorio.html','relatorios/t10/tabelas.json',
       'relatorios/t10/figuras/meta-a.png','relatorios/t10/figuras/meta-a.svg',
       'relatorios/t10/figuras/cobertura.png','relatorios/t10/figuras/cobertura.svg',
       'relatorios/t10/figuras/habilidades.png','relatorios/t10/figuras/habilidades.svg',
       'restrito/t10/checkpoint.json','evidencias/T10/analise-resultado.json']

def main():
    label=sys.argv[1] if len(sys.argv)>1 else '01'
    if not label.isdigit():raise ValueError('Rotulo invalido')
    copies={}
    for relative in FILES:
        source=(ROOT/relative).resolve()
        if not source.is_relative_to(ROOT) or not source.is_file():raise ValueError('Origem derivada invalida')
        target=source.parent/('versoes/analise'+label)/source.name
        if not target.resolve().is_relative_to(ROOT) or target.exists():raise ValueError('Destino invalido/existente')
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target)
        copies[relative]=hashlib.sha256(target.read_bytes()).hexdigest()
    (ROOT/f'evidencias/T10/preservacao{label}-resultado.json').write_text(json.dumps(copies,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'derivados_preservados':len(copies),'fontes_originais_alteradas':0}))

if __name__=='__main__':main()
