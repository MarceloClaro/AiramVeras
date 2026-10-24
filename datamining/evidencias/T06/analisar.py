"""Execução T06 autenticada; valores individuais nunca saem da área restrita."""
from collections import Counter, defaultdict
import csv
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import traceback
import unicodedata

import numpy as np
from scipy import stats

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.correlacoes import (preparar_analises,correlacionar,ajustar_familias,
                              auditar_pares,configuracao)

PINNED={
    'restrito/t05/checkpoint.json':'6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b',
    'estatistica/t05/checkpoint.json':'5bfa87b38394d171589a7799751127dceb7d81587bbbfcefa67d2bb4a8420231',
    'curriculo/t04/checkpoint.json':'a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796',
    'restrito/t03/tabelas.json':'b26bef93117c7c38906cd9e6e025cfc5f2a9969cc4834e4b785618d29dd56dbb'}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False)
def need(condition,message):
    if not condition:raise ValueError(message)
def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def turma(s):return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',s) if not unicodedata.combining(c)).upper().split())


def main():
    label=sys.argv[1]
    private=ROOT/'restrito/t06'/label
    public=ROOT/'estatistica/t06'/label
    need(not private.exists() and not public.exists(),'Rotulo ja existe')
    private.mkdir(parents=True); public.mkdir(parents=True)
    for path,digest in PINNED.items():need(sha(ROOT/path)==digest,'Entrada autenticada diverge')
    checkpoint=json.loads((ROOT/'restrito/t05/checkpoint.json').read_text(encoding='utf-8'))
    tables=checkpoint['observado']
    need(tables==json.loads((ROOT/'restrito/t03/tabelas.json').read_text(encoding='utf-8')),'Observado diverge do T03')
    cfg=configuracao()
    plan=preparar_analises(tables,config=cfg)
    # Plano nominal restrito e manifestação pública fixados ANTES da estatística.
    write(private/'plano-pares.json',plan)
    manifest=[{k:v for k,v in a.items() if k!='pares'} for a in plan]
    write(public/'plano.json',dict(config_sha256=sha(ROOT/'config/correlacoes.json'),
        plano_restrito_sha256=sha(private/'plano-pares.json'),associacoes=manifest,
        familias_planejadas=dict(Counter(a['familia'] for a in plan))))
    # Referência independente: leitura direta dos CSV e parsing local sem APIs airam.
    cache={}; input_hashes={}; raw_av={}; raw_measure={}; raw_h=defaultdict(dict)
    def source(row):
        path=ROOT.parent/row['caminho']
        if path not in cache:
            need(sha(path)==row['sha256'],'CSV alterado')
            with path.open(encoding='utf-8-sig',newline='') as f:cache[path]=list(csv.DictReader(f,delimiter=';'))
            input_hashes[str(path.relative_to(ROOT.parent)).replace('\\','/')]=row['sha256']
        return cache[path][row['linha_fonte']-2]
    audited=Counter()
    for av in tables['avaliacoes']:
        original=source(av)
        part=original.get('Avaliado',original.get('Participação','')).strip().casefold()=='sim'
        need(part==av['participacao'],'Participacao diverge da fonte')
        need(turma(original.get('Turma',original.get('Turmma','')))==turma(av['turma']),'Turma diverge da fonte')
        raw_av[av['avaliacao_local_id']]=dict(original=original,participacao=part)
        audited['avaliacoes']+=1
    for table in ('habilidades','escrita','fluencia'):
        for row in tables[table]:
            original=source(row); text=original[row['campo_original']].strip()
            need(original[row['campo_original']]==row['bruto'],'Bruto diverge da fonte')
            missing=text.casefold() in ('','-','sem resultado')
            n=d=value=percent=None
            if not missing:
                if table=='habilidades' or row['campo_original']=='Texto (Compreensão)':
                    m=re.fullmatch(r'(\d+)\s*/\s*(\d+)',text)
                    need(m is not None,'Par de itens invalido'); n,d=map(int,m.groups()); value=n
                elif row['campo_original'] in ('Palavras (leitura global)','Palavras possivelmente desconhecidas'):
                    m=re.fullmatch(r'(\d+)\s+de\s+(\d+)',text)
                    need(m is not None,'Lista de palavras invalida'); n,d=map(int,m.groups()); value=n
                elif row['campo_original']=='Texto (Palavras corretas)':
                    m=re.fullmatch(r'(\d+)\s*-\s*(\d+(?:[.,]\d+)?)%',text)
                    need(m is not None,'Texto invalido'); value=int(m[1]); percent=float(m[2].replace(',','.'))
                else:value=float(text.replace(',','.'))
            need((row['numerador'],row['denominador'],row['valor'],row['percentual'])==(n,d,value,percent),
                 'Valor normalizado difere da leitura independente')
            need(row['disponibilidade']==(not missing),'Mascara diverge da fonte')
            need(missing or row['participacao'],'Resultado em nao participante')
            key=(row['avaliacao_local_id'],row['campo_original'])
            raw_measure[key]=dict(valor=value,percentual=percent,numerador=n,denominador=d)
            if table=='habilidades':raw_h[row['avaliacao_local_id']][row['posicao']]=(n,d)
            audited[table]+=1
    # Campos numéricos e pareamento são confrontados, não só N/pertença.
    contexts=('avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente','fonte_id','sha256','exportacao')
    av_index={(r['ano_escolar'],r['ano_avaliacao'],r['ciclo'],r['aluno_local_id'],r['componente']):r for r in tables['avaliacoes']}
    variables={v['nome']:v for v in cfg['variaveis']}
    instruments={}
    for analysis in plan:
        if analysis['tipo']=='intercomponentes':
            comps=[variables[analysis[k]]['componente'] for k in ('x','y')]
            entries={comp:sorted({tuple(av[k] for k in contexts) for av in tables['avaliacoes']
                if av['ano_escolar']==analysis['ano_escolar'] and av['componente']==comp
                and av['ano_avaliacao']==analysis['ano_avaliacao'] and av['ciclo']==analysis['ciclo']}) for comp in comps}
        else:
            entries=next({k:av[k] for k in contexts} for av in tables['avaliacoes']
                if av['ano_escolar']==analysis['ano_escolar'] and av['componente']==analysis['componente']
                and av['ano_avaliacao']==analysis['ano_avaliacao'] and av['ciclo']==analysis['ciclo'])
        need(hashlib.sha256(canonical(entries).encode()).hexdigest()==analysis['instrumento'],'Instrumento do par diverge')
        instruments[analysis['instrumento']]=entries
        reference=[]
        for row in analysis['pares']:
            ref={k:row[k] for k in ('aluno_local_id','turma','ano_escolar','ano_avaliacao','ciclo','instrumento')}
            context=(analysis['ano_escolar'],analysis['ano_avaliacao'],analysis['ciclo'],row['aluno_local_id'])
            if analysis['tipo']=='intercomponentes':
                for axis in ('x','y'):
                    var=variables[analysis[axis]]; av=av_index.get(context+(var['componente'],))
                    value=None
                    if av:
                        need(row['turma']==turma(av['turma']),'Turma do par diverge')
                        if raw_av[av['avaliacao_local_id']]['participacao']:
                            if var['tabela']=='avaliacoes':
                                blocks=list(raw_h[av['avaliacao_local_id']].values())
                                if blocks and all(n is not None for n,d in blocks):
                                    value=float(Fraction(sum(n for n,d in blocks),sum(d for n,d in blocks)))
                            else:value=raw_measure.get((av['avaliacao_local_id'],var['campo_original']),{}).get(var['campo'])
                    ref[axis]=value
            else:
                av=av_index[context+(analysis['componente'],)]
                blocks=raw_h[av['avaliacao_local_id']]
                n,d=blocks[analysis['x']]; rest=[v for k,v in blocks.items() if k!=analysis['x']]
                good=bool(rest) and all(a is not None for a,b in rest)
                ns=sum(a for a,b in rest) if good else None; ds=sum(b for a,b in rest) if good else None
                ref.update(x=float(Fraction(n,d)) if n is not None else None,y=float(Fraction(ns,ds)) if good else None,
                    acertos_restantes=ns,oportunidades_restantes=ds,blocos_restantes=len(rest),cobertura_completa=good)
            reference.append(ref)
        audited['pares_conferidos']+=auditar_pares(analysis['pares'],reference)['pares_conferidos']
    write(public/'instrumentos.json',dict(campos_contexto=list(contexts),instrumentos=instruments))
    # A cobertura das posições é independente dos resultados e usa checkpoint T04 autenticado.
    curriculum=json.loads((ROOT/'curriculo/t04/checkpoint.json').read_text(encoding='utf-8'))
    pos_fields=('avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente','posicao')
    expected={tuple(p[k] for k in pos_fields) for p in curriculum['posicoes']}
    observed={tuple(p[k] for k in pos_fields) for p in tables['habilidades']}
    need(expected==observed,'Cobertura curricular contextual diverge')
    audited['posicoes_conferidas']=len(expected)
    results=[]
    independent=Counter()
    max_delta=0.
    for j,analysis in enumerate(plan):
        seed=cfg['seed']+int(hashlib.sha256(canonical(manifest[j]).encode()).hexdigest()[:8],16)
        estimates=correlacionar(analysis['pares'],'x','y',cfg['strata'],seed,config=cfg)
        for estimate in estimates:
            if estimate['coeficiente'] is not None:
                complete=[r for r in analysis['pares'] if r['x'] is not None and r['y'] is not None]
                x=np.array([r['x'] for r in complete]); y=np.array([r['y'] for r in complete])
                method=estimate['metodo']
                scipy_value=(stats.pearsonr(x,y) if method=='pearson' else stats.spearmanr(x,y)).statistic
                if method=='spearman':
                    # Postos médios independentes sem rankdata nem auxiliares do produto.
                    x=np.array([1+sum(v<a for v in x)+(sum(v==a for v in x)-1)/2 for a in x])
                    y=np.array([1+sum(v<b for v in y)+(sum(v==b for v in y)-1)/2 for b in y])
                n=len(x)
                cov=n*sum(x*y)-sum(x)*sum(y)
                algebra=cov/math.sqrt((n*sum(x*x)-sum(x)**2)*(n*sum(y*y)-sum(y)**2))
                delta=max(abs(estimate['coeficiente']-float(scipy_value)),abs(estimate['coeficiente']-float(algebra)))
                need(delta<1e-10,'Contraprova de coeficiente diverge')
                max_delta=max(max_delta,delta); independent[method]+=1
            results.append(manifest[j]|estimate)
    results=ajustar_familias(results)
    # Ajustes confrontados com SciPy, preservando não estimáveis.
    groups=defaultdict(list)
    for i,r in enumerate(results):groups[r['familia']].append(i)
    for indices in groups.values():
        p=[1. if results[i]['p'] is None else results[i]['p'] for i in indices]
        bh,by=stats.false_discovery_control(p,method='bh'),stats.false_discovery_control(p,method='by')
        for i,q1,q2 in zip(indices,bh,by):
            if results[i]['p'] is not None:
                need(abs(results[i]['q']-q1)<1e-12 and abs(results[i]['q_by']-q2)<1e-12,'BH/BY diverge')
    families=[dict(familia=k,planejadas=len(v),elegiveis=sum(results[i]['p'] is not None for i in v),m_bh=len(v)) for k,v in sorted(groups.items())]
    limits=[
        'Descricao censitaria dos pares avaliados, sujeita a qualidade de registro e identidade local provisoria.',
        'Permutacao depende da intercambiabilidade condicional de Y dentro de turma/ano/instrumento; hipotese nao demonstrada por estes registros.',
        'p nao e probabilidade de H0, nem efeito causal, eficacia de ensino ou correlacao populacional irrestrita.',
        'Faixa bootstrap e sensibilidade a recomposicao dos avaliados; nao erro amostral do censo, medida de ausencia ou variabilidade entre escolas.',
        'Quantidade/percentual do Texto tem disponibilidade parcial possivelmente selecionada. Compreensao tem cobertura propria; ausencia aleatoria nao demonstrada.',
        'BH exige condicoes de dependencia nao garantidas aqui; BY e BH global sao sensibilidades. Nenhum ajuste corrige p invalido.',
        'Nao ha previsao temporal validada, categorias convertidas em numeros ou equivalencia de Nota com percentual.',
        'Sem afirmacao unica de significancia da escola; comparar efeitos, cobertura e limites, sem selecionar menor p.'
    ]
    data=dict(versao_schema='airam-associacoes-t06-v1',fontes=PINNED,
        config_sha256=sha(ROOT/'config/correlacoes.json'),plano_sha256=sha(public/'plano.json'),
        instrumentos_sha256=sha(public/'instrumentos.json'),familias=families,associacoes=results,
        contraprova=dict(contagens=dict(audited),coeficientes=dict(independent),max_diferenca=max_delta,
            metodo='CSV_original+Fraction+somas_algebricas+SciPy',fontes_csv=input_hashes),limites=limits)
    # Fronteira pública explícita: proibir identificadores reais e chaves individuais.
    encoded=canonical(data)
    identities={r['aluno_local_id'] for r in tables['avaliacoes']}|{r['avaliacao_local_id'] for r in tables['avaliacoes']}
    need(not any(i in encoded for i in identities),'Identificador individual em agregado')
    need(not any('"'+k+'"' in encoded for k in ('aluno_local_id','avaliacao_local_id','nome','nome_normalizado','pares')),
         'Chave individual em agregado')
    write(public/'checkpoint.json',data)
    fields=['tipo','ano_escolar','ano_avaliacao','ciclo','componente','instrumento','familia','x','y','unidade_x','unidade_y',
            'metodo','n','n_x','n_y','cadastros','coeficiente','p','q','q_by','q_bh_global',
            'm_planejado','m_elegivel','m_bh','motivo_coeficiente','motivo_inferencia','selecao_texto',
            'sensibilidade_inferior','sensibilidade_superior','bootstrap_validas','bootstrap_degeneradas']
    with (public/'associacoes.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in results:
            row={k:r.get(k) for k in fields}; band=r['sensibilidade']['faixa']
            row.update(sensibilidade_inferior=band[0] if band else None,sensibilidade_superior=band[1] if band else None,
                bootstrap_validas=r['sensibilidade']['validas'],bootstrap_degeneradas=r['sensibilidade']['degeneradas'])
            writer.writerow(row)
    for path,digest in PINNED.items():need(sha(ROOT/path)==digest,'Entrada mudou durante execucao')
    summary=dict(status='CONCLUIDO',associacoes=len(plan),coeficientes=len(results),familias=len(families),
        estimaveis=sum(r['coeficiente'] is not None for r in results),p_disponivel=sum(r['p'] is not None for r in results),
        nao_inferenciais=dict(Counter(r['motivo_inferencia'] for r in results if r['p'] is None)),
        plano_sha256=sha(public/'plano.json'),checkpoint_sha256=sha(public/'checkpoint.json'),
        csv_sha256=sha(public/'associacoes.csv'),restrito_sha256=sha(private/'plano-pares.json'),
        contraprova=data['contraprova'])
    write(ROOT/'evidencias/T06'/('analise-'+label+'.json'),summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='contraprova'},ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except Exception as exc:
        dest=ROOT/'restrito/t06'/('falha-'+(sys.argv[1] if len(sys.argv)>1 else 'argumento')+'.txt')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(traceback.format_exc(),encoding='utf-8')
        print('Falha T06: '+type(exc).__name__+'. Detalhes preservados somente na area restrita.')
        raise SystemExit(1)
