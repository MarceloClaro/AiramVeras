"""Diagnóstico local só com classe e localizadores; não imprime dados nem exceção."""
import os
from pathlib import Path
import sys
import traceback

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.cli import configuracao
from airam.pipeline import analisar


def main():
    path=ROOT/'config/analise.json';os.environ['AIRAM_CONFIG']=str(path)
    try:
        config,project,sources,baseline=configuracao(path)
        result=analisar(config,project,sources)
        print('Diagnostico analitico concluido; nova_inferencia='+str(result['nova_inferencia']))
        return 0
    except Exception as exc:
        print(type(exc).__name__)
        print([(frame.name,frame.lineno) for frame in traceback.extract_tb(exc.__traceback__)])
        return 1


if __name__=='__main__':raise SystemExit(main())
