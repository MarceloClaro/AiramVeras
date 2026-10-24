"""Registra a coleta observada no portal e empacota os downloads originais."""
import csv
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parent
COMPONENTS = {'LEITURA':'LÍNGUA PORTUGUESA','MATEMATICA':'MATEMÁTICA','ESCRITA':'ESCRITA','FLUENCIA':'FLUÊNCIA'}
# Códigos e ordem lidos nos cartões do portal durante as exportações.
CODES = {
 (1,'LEITURA'): '1EF01_P 1EF02_P 1EF03_P 1EF04_P 1EF06_P 1EF07_P 1EF08_P 1EF09_P 1EF10_P',
 (1,'MATEMATICA'): '1EF01_M 1EF02_M 1EF06_M 1EF08_M 1EF09_M 1EF10_M 1EF11_M',
 (2,'LEITURA'): '1EF05_P 1EF06_P 1EF07_P 1EF08_P 1EF09_P 1EF12_P 1EF13_P 1EF14_P 2EF06_P 2EF07_P 2EF10_P',
 (2,'MATEMATICA'): '1EF07_M 1EF10_M 1EF12_M 1EF13_M 2EF01_M 2EF02_M 2EF03_M 2EF05_M 2EF06_M 2EF08_M 2EF09_M',
 (3,'LEITURA'): '1EF08_P 1EF09_P 1EF13_P 1EF15_P 2EF08_P 2EF11_P 2EF14_P 2EF15_P 2EF19_P 3EF06_P 3EF16_P',
 (3,'MATEMATICA'): '2EF07_M 2EF08_M 2EF12_M 2EF13_M 2EF14_M 2EF15_M 3EF01_M 3EF06_M 3EF07_M 3EF09_M 3EF15_M 3EF16_M',
 (4,'LEITURA'): '1EF09_P 2EF08_P 2EF19_P 3EF01_P 3EF02_P 3EF03_P 3EF06_P 3EF09_P 3EF15_P 3EF21_P 4EF10_P 4EF22_P 4EF24_P',
 (4,'MATEMATICA'): '3EF06_M 3EF07_M 3EF08_M 3EF09_M 3EF11_M 3EF12_M 3EF13_M 3EF14_M 3EF16_M 3EF17_M 4EF02_M 4EF03_M 4EF04_M 4EF05_M 4EF07_M',
 (5,'LEITURA'): '2EF08_P 3EF06_P 3EF09_P 3EF15_P 4EF10_P 4EF13_P 4EF14_P 4EF16_P 4EF17_P 4EF23_P 5EF04_P 5EF06_P 5EF15_P 5EF16_P 5EF19_P 5EF22_P',
 (5,'MATEMATICA'): '3EF07_M 3EF09_M 3EF11_M 3EF12_M 3EF17_M 4EF01_M 4EF02_M 4EF03_M 4EF04_M 4EF06_M 4EF07_M 4EF08_M 4EF09_M 4EF10_M 4EF11_M 4EF12_M 4EF13_M 5EF04_M 5EF07_M',
}
exports, bridge = [], []
for year in range(1,6):
    for comp,discipline in COMPONENTS.items():
        name=f'{year}ANO_{comp}_CICLO_I_2026.zip'
        file=ROOT/'originais'/name
        params={'DADOS.VL_FILTRO_AVALIACAO':'AV12026',
                'DADOS.VL_FILTRO_ETAPA':f'ENSINO FUNDAMENTAL DE 9 ANOS - {year}º ANO',
                'DADOS.VL_FILTRO_DISCIPLINA':discipline,'DADOS.VL_FILTRO_REDE':'MUNICIPAL'}
        if comp in ('LEITURA','MATEMATICA'):
            params['DADOS.DC_FAIXA_PERCENTUAL_HABILIDADE']='Alto-Médio Baixo-Médio Alto-Baixo'
        url='https://criancaalfabetizada.caeddigital.net/#!/pagina/VIEW_RESULTADOS?'+ '&'.join(quote(k)+'='+quote(v) for k,v in params.items())
        item={'ano_escolar':year,'componente':comp,'ciclo':'I','avaliacao_id':'AV12026',
              'filtros_observados_no_portal':params,'url_filtros':url,
              'status':'baixado' if file.exists() else 'Nenhum resultado encontrado no portal'}
        if file.exists():
            item['arquivo']='originais/'+name
            item['sha256']=hashlib.sha256(file.read_bytes()).hexdigest()
            with zipfile.ZipFile(file) as z:
                assert z.testzip() is None
                assert len(z.namelist())==3
                schoolfile=next(n for n in z.namelist() if 'ESCOLA' in n.upper())
                rows=list(csv.DictReader(io.StringIO(z.read(schoolfile).decode('utf-8-sig')),delimiter=';'))
                assert len(rows)==1
                if (year,comp) in CODES:
                    codes=CODES[year,comp].split()
                    cols=[k for k in rows[0] if re.fullmatch(r'H \d+ \(%\)',k)]
                    assert len(cols)==len(codes),(name,cols,codes)
                    for pos,code in enumerate(codes,1):
                        key=f'H {pos:02d} (%)'
                        bridge.append({'avaliacao_id':'AV12026','ano_escolar':year,'componente':comp,
                                       'posicao':f'H {pos:02d}','codigo_caed_observado':code,
                                       'percentual_escola_original':rows[0][key],
                                       'fonte_codigo':'cartão exibido no portal durante a exportação',
                                       'fonte_percentual':name+' :: '+schoolfile})
        else:
            assert year==1 and comp in ('ESCRITA','FLUENCIA')
        exports.append(item)
manifest={'data_coleta':'2026-10-22','programa':'CNCA / Avaliação Contínua da Aprendizagem',
          'ano_avaliacao':2026,'ciclo':'I','avaliacao_id':'AV12026',
          'escola':'AIRAM VERAS ESC CID','codigo_escola':'23084995','rede':'MUNICIPAL',
          'origem_dos_filtros':'Controles e URL observados no navegador antes de cada exportação.',
          'limite':'O ciclo não consta nos CSVs. Escrita e fluência também não trazem ano escolar e componente. Essas informações são de proveniência da interface.',
          'exportacoes':exports}
(ROOT/'manifesto_coleta.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with (ROOT/'conferencia/mapa_posicao_codigo_caed.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(bridge[0]),delimiter=';');w.writeheader();w.writerows(bridge)
assert sum(x['status']=='baixado' for x in exports)==18
archive=ROOT.parent/'CAEd_Airam_Veras_Ciclo_I_2026_1ao5_ANO_RESTRITO.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for f in ROOT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(ROOT))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'zip_final':str(archive),'exportacoes':18,'sem_resultado':2,'mapa_codigo_registros':len(bridge),'bytes':archive.stat().st_size},ensure_ascii=False))
