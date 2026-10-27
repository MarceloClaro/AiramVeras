# -*- coding: utf-8 -*-
"""
Monitor Inteligente de Downloads do CAEd
Verifica a pasta Downloads do usuário e ingere automaticamente arquivos dos Ciclos II e III.
"""
import os
import sys
import shutil
import zipfile
import hashlib
from pathlib import Path
from datetime import datetime

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

DOWNLOADS_DIR = Path(r"C:\Users\marce\Downloads")
WORKSPACE_DIR = Path(r"c:\Users\marce\Downloads\Airam veras")
CICLO_II_ORIGINAIS = WORKSPACE_DIR / "resultados-caed-ciclo-ii-2026" / "originais"
CICLO_III_ORIGINAIS = WORKSPACE_DIR / "resultados-caed-ciclo-iii-2026" / "originais"

def verificar_e_mover_downloads():
    CICLO_II_ORIGINAIS.mkdir(parents=True, exist_ok=True)
    CICLO_III_ORIGINAIS.mkdir(parents=True, exist_ok=True)

    zips_encontrados = list(DOWNLOADS_DIR.glob("*.zip"))
    print(f"Varrendo {DOWNLOADS_DIR} ({len(zips_encontrados)} arquivos ZIP encontrados)...")

    movidos = 0
    for zf in zips_encontrados:
        nome = zf.name.upper()
        # Verificar se é arquivo de exportação do CAEd
        eh_caed = any(k in nome for k in ['CICLO', 'AV1', 'AV2', 'AV3', 'HABILIDADE', 'DESEMPENHO', 'LEITURA', 'MATEMATICA', 'ESCRITA', 'FLUENCIA'])
        
        # Inspecionar conteúdo interno do zip se o nome não for óbvio
        if not eh_caed:
            try:
                with zipfile.ZipFile(zf, 'r') as z:
                    nomes_internos = [n.upper() for n in z.namelist()]
                    if any('HABILIDADE' in n or 'DESEMPENHO' in n or 'ESTUDANTE' in n for n in nomes_internos):
                        eh_caed = True
            except Exception:
                continue

        if eh_caed:
            destino = CICLO_II_ORIGINAIS if ('AV2' in nome or 'CICLO_II' in nome or 'CICLO II' in nome) else CICLO_III_ORIGINAIS
            if 'CICLO_I_' in nome or 'CICLO I' in nome:
                continue # Preservar Ciclo I já consolidado

            dest_file = destino / zf.name
            shutil.copy2(zf, dest_file)
            print(f" -> Arquivo CAEd detectado e copiado para {destino.parent.name}: {zf.name}")
            movidos += 1

    print(f"Total de arquivos de novos ciclos capturados e transferidos: {movidos}")
    return movidos

if __name__ == '__main__':
    verificar_e_mover_downloads()
