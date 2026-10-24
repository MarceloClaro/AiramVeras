"""Confere localmente a cópia artificial antes de permitir inspeção externa."""
import hashlib
import html
import json
from pathlib import Path
import zipfile
import sys

ROOT=Path(__file__).resolve().parents[2]
FOLDER=ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53/previas-sinteticas'
def read(p):return json.loads((ROOT/p).read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    folder=Path(sys.argv[1]).resolve().parent if len(sys.argv)>1 else FOLDER
    label=sys.argv[2] if len(sys.argv)>2 else '02'
    data=json.loads((folder/'entrada-artificial.json').read_text(encoding='utf-8'))
    rows=data['intervencao'];hs=data['habilidades']
    assert len(rows)==8 and len(hs)==16
    assert [r['acertos'] for r in rows]==[0,3,6,9,None,None,None,None]
    assert all(r['chave'].startswith('ARTIFICIAL') and r['nome'].startswith('PESSOA ARTIFICIAL')
        and r['grupos']==[] and r['notas_docentes'].startswith('ARTIFICIAL')
        and r['fonte']=='ARTIFICIAL' and r['linha_fonte']==1 for r in rows)
    assert all(h['fonte']=='ARTIFICIAL' and h['linha_fonte']==1 and h['posicao']=='H01' for h in hs)
    if data.get('regra_texto_artificial')=='frase-ficticia-v1':
        sentence='Frase inteiramente fictícia para verificar espaço e quebra. '
        assert all(line==(sentence*((len(line)+len(sentence)-1)//len(sentence)))[:len(line)]
            for s in data['comprimentos_artificiais'].values() for line in s.split('\n'))
    else:assert all(not set(s)-{'X','\n'} for s in data['comprimentos_artificiais'].values())
    nominal=read('restrito/t03/mapa-nominal.json')
    raw=read('restrito/t05/checkpoint.json')['observado']
    prepared=read('restrito/t10/checkpoint.json')
    terms={str(r[k]) for r in nominal for k in ['nome_bruto','nome_normalizado','aluno_local_id','matricula_local_id'] if r.get(k)}
    terms.update(r['avaliacao_local_id'] for r in raw['avaliacoes'])
    terms.update(r['chave'] for r in prepared['intervencao'])
    xlsx=folder/'inspecao-artificial.xlsx'
    with zipfile.ZipFile(xlsx) as z:
        text='\n'.join(html.unescape(z.read(n).decode('utf-8')) for n in z.namelist() if n.endswith('.xml'))
    text+='\n'+json.dumps(data,ensure_ascii=False)
    folded=text.casefold()
    assert not any(term.casefold() in folded for term in terms), 'Identificador individual na copia artificial'
    result=dict(status='PASS',aplicacoes_artificiais=8,medidas_artificiais=16,
        observacoes_geradas_por_regra=True,nomes_ids_reais_ausentes=True,grupos_individuais_vazios=True,
        textos_por_regra_inteiramente_artificial=True,agregados_publicos_preservados=True,
        xlsx_sha256=sha(xlsx),json_sha256=sha(folder/'entrada-artificial.json'),
        builder_sha256=data['fontes'].get('autoria/builder_js_sha256'),
        codigo_verificador_sha256=sha(Path(__file__)))
    target=ROOT/f'evidencias/T10/previa-segura-{label}-resultado.json'
    if target.exists():raise ValueError('Preservar verificacao anterior')
    target.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
if __name__=='__main__':main()
