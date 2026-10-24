"""Execução real T05: autenticação, rota bruta independente e handoff minimizado."""
import csv
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import traceback
import unicodedata
from collections import Counter, defaultdict

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.metricas import agregar_habilidades
from airam.contraprova import auditar_resultados
from airam.metas import meta_adequados, meta_acertos, corte_empirico

T03 = 'b26bef93117c7c38906cd9e6e025cfc5f2a9969cc4834e4b785618d29dd56dbb'
T04 = 'a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True,allow_nan=False)+'\n',encoding='utf-8')


def need(condition, message):
    if not condition:
        raise ValueError(message)


def class_key(value):
    if value is None:
        return None
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD',value) if not unicodedata.combining(c)).upper().split())


def main():
    t3, t4 = ROOT/'restrito/t03/tabelas.json', ROOT/'curriculo/t04/checkpoint.json'
    need(sha(t3)==T03 and sha(t4)==T04,'Checkpoint de entrada diverge')
    tables=json.loads(t3.read_text(encoding='utf-8'))
    curriculum=json.loads(t4.read_text(encoding='utf-8'))
    evidence=ROOT/'evidencias/T05'
    # Coletor preservado é executado sem editar bytes e sem sobrescrever seu recibo histórico.
    collector=evidence/'preparacao-preservada/coletor_portal.py'
    spec=importlib.util.spec_from_file_location('portal_independente',collector)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.HERE=evidence/('portal-'+(sys.argv[1] if len(sys.argv)>1 else 'atual'))
    need(not module.HERE.exists(),'Diretorio da auditoria ja existe; preservar evidencia')
    module.HERE.mkdir()
    module.ROOT=ROOT
    module.SOURCE=ROOT.parent/'resultados-caed-ciclo-i-2026'
    module.main()
    raw=json.loads((module.HERE/'recibo-portal.json').read_text(encoding='utf-8'))
    need(raw['fontes_inalteradas_ao_final'],'Auditoria bruta incompleta')
    # Autenticar cada referência individual e seu bruto contra os CSV, sem exportar linhas.
    cache={}
    def source(row):
        path=ROOT.parent/row['caminho']
        need(sha(path)==row['sha256'],'Hash de CSV nao coincide com T03')
        if path not in cache:
            with path.open(encoding='utf-8-sig',newline='') as f:
                cache[path]=list(csv.DictReader(f,delimiter=';'))
        return cache[path][row['linha_fonte']-2]
    verified=Counter()
    for table in ('habilidades','escrita','fluencia'):
        for row in tables[table]:
            original=source(row)
            need(original[row['campo_original']]==row['bruto'],'Bruto da medida difere da fonte')
            need((original.get('Avaliado',original.get('Participação','')).strip().casefold()=='sim')==row['participacao'],'Participacao difere da fonte')
            if table=='habilidades':
                match=re.fullmatch(r'(\d+)\s*/\s*(\d+)',row['bruto'].strip())
                pair=tuple(map(int,match.groups())) if match else (None,None)
                need(pair==(row['numerador'],row['denominador']),'Contagem normalizada difere do bruto')
            verified[table]+=1
    evaluations={r['avaliacao_local_id']:r for r in tables['avaliacoes']}
    for row in tables['avaliacoes']:
        original=source(row)
        need(original[row['campo_categoria_original']]==row['categoria_bruto'],'Categoria bruta difere da fonte')
        need((original.get('Avaliado',original.get('Participação','')).strip().casefold()=='sim')==row['participacao'],'Participacao de avaliacao difere')
        verified['avaliacoes']+=1
    joined=[]
    for row in tables['habilidades']:
        application=evaluations[row['avaliacao_local_id']]
        need(all(row[k]==application[k] for k in ('aluno_local_id','ano_escolar','componente','fonte_id','sha256','linha_fonte','participacao')),
            'Join individual/contexto diverge')
        joined.append(row | dict(turma=application['turma']))
    results=agregar_habilidades(joined)
    audit=auditar_resultados(joined,results)
    individuals=[r for r in results if r['nivel']=='aluno']
    applications_by_student={(r['aluno_local_id'],r['fonte_id'],r['sha256']):r for r in tables['avaliacoes']}
    for row in individuals:
        original=applications_by_student[(row['aluno_local_id'],row['fonte_id'],row['sha256'])]
        need((original['acertos_observados'],original['oportunidades_observadas'])==
            ((row['acertos'],row['oportunidades']) if row['validas'] else (None,None)),
            'Total individual nao reconcilia com T03')
        need(original['taxa']==row['taxa'],'Taxa de prova nao reconcilia com T03')
    # Cada H contextual tem exatamente uma posição curricular; nenhuma expansão de arestas.
    context=('avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente','posicao')
    observed={tuple(r[k] for k in context) for r in tables['habilidades']}
    documented={tuple(r[k] for k in context) for r in curriculum['posicoes']}
    need(observed==documented,'Cobertura contextual curricular divergente')
    # Rota bruta independente -> turma/escola; comparar todos H e totais, não só cardinalidades.
    grouped={}
    for row in results:
        if row['nivel']=='aluno':
            continue
        key=(row['ano_escolar'],row['componente'],row['nivel'],row['turma'],row['posicao'])
        need(key not in grouped,'Multiplas versoes exigem selecao explicita')
        grouped[key]=row
    raw_groups=raw['agregados_recalculados']
    reconciled=0
    goals=[]
    categories_alias={'Defasagem':'Defasagem','Aprendizado intermediário':'Intermediário','Aprendizado adequado':'Adequado'}
    for scope in raw_groups:
        base=(scope['ano_escolar'],scope['componente'],scope['nivel'],class_key(scope['turma']))
        row=grouped[(*base,None)]
        need((row['cadastros'],row['avaliados'],row['ausentes'])==
            (scope['cadastros_exportados'],scope['avaliados'],scope['celulas_h_ausentes']),'Denominadores divergem do bruto')
        total=scope['taxa_todos_itens_derivada_nao_publicada']
        need((row['acertos'],row['oportunidades'])==(total['acertos'],total['oportunidades']),'Total por instrumento diverge')
        need(Path(row['exportacao']).stem==scope['fonte'],'Fonte/exportacao divergente')
        selected=[r for r in tables['avaliacoes'] if r['ano_escolar']==base[0] and r['componente']==base[1]
            and (base[2]=='escola' or r['turma']==base[3])]
        cats=Counter(r['categoria'] for r in selected if r['participacao'])
        need({cat:cats[alias] for cat,alias in categories_alias.items()}==scope['categorias_contagens'],'Categorias originais divergem do bruto')
        for position, counts in scope['habilidades'].items():
            h=grouped[(*base,position)]
            need((h['acertos'],h['oportunidades'],h['validas'])==
                (counts['acertos'],counts['oportunidades'],counts['participantes_com_medida']),'H/turma/escola diverge do bruto')
            reconciled+=1
        goals.append(dict(ano_escolar=base[0],componente=base[1],nivel=base[2],turma=base[3],
            categorias_contagens=dict(sorted(cats.items())),meta_A=meta_adequados(row['avaliados'],cats['Adequado'],.8),
            corte_empirico=corte_empirico(selected)))
    # Verifica todos os percentuais publicados/brutos e a proveniência dos agregados T03.
    aggregates={(r['ano_escolar'],r['componente'],r['nivel'],class_key(r['turma'])):r for r in tables['agregados']
        if r['componente'] in ('LEITURA','MATEMATICA')}
    for check in raw['checks_percentuais']:
        row=aggregates[(check['ano_escolar'],check['componente'],check['nivel'],class_key(check['turma']))]
        need(row['caminho']=='resultados-caed-ciclo-i-2026/'+check['fonte_agregado'],'Proveniencia de agregado divergente')
        need(sha(ROOT.parent/row['caminho'])==row['sha256'],'Hash de agregado divergente')
        matches=[m for m in row['medidas'] if m['campo_original']==check['campo']]
        need(len(matches)==1 and matches[0]['bruto']==check['publicado_bruto'],'Percentual publicado divergente')
    nominal_goals=[]
    for row in tables['avaliacoes']:
        compatible=row['componente'] in ('LEITURA','MATEMATICA')
        goal=meta_acertos(row['acertos'],row['oportunidades'],.8) if compatible else dict(meta='B',alvo=None,lacuna=None,atingida=None,status='unidade_nao_aplicavel')
        nominal_goals.append(dict(avaliacao_local_id=row['avaliacao_local_id'],aluno_local_id=row['aluno_local_id'],
            componente=row['componente'],meta_B=goal))
    public_aggregates=[{k:v for k,v in r.items() if k!='aluno_local_id'} for r in results if r['nivel']!='aluno']
    public=dict(versao_schema='airam-estatistica-t05-v1',fontes=dict(t03_sha256=T03,t04_sha256=T04,
        manifesto_sha256=raw['manifesto_sha256'],coletor_bruto_sha256=sha(collector)),
        politica=dict(meta='4/5',taxa='soma_acertos/soma_oportunidades',
            corte_oficial=None,arredondamento='half_up_adotado_nao_oficial; compatibilidade_inteira_com_empate_separada',
            escopo='instrumentos separados; escrita/fluencia mantem unidades; identidade local provisoria'),
        agregados=public_aggregates,metas_A=goals,resumo_portal=raw['resumo'],divergencias_portal=raw['divergencias'],
        contraprova=audit,cobertura_curricular=dict(posicoes=len(observed),arestas_nao_expandem_medidas=True),
        limites=['Validacao documental/computacional local; sem validacao pedagogica externa.',
            'Sem corte oficial de acertos para adequacao; sem previsao temporal validada.'])
    restricted=ROOT/'restrito/t05/checkpoint.json'
    write(restricted,dict(versao_schema='airam-estatistica-restrita-t05-v1',fontes=public['fontes'],observado=tables,
        metricas_alunos=individuals,metas_individuais=nominal_goals,agregado=public,
        curriculo_referencia='curriculo/t04/checkpoint.json'))
    output=ROOT/'estatistica/t05/checkpoint.json'
    write(output,public)
    summary=dict(estado='CONCLUIDO_COM_DISCREPANCIA_DE_EXIBICAO_PRESERVADA',brutos_conferidos=dict(verified),
        contraprova=audit,aplicacoes_h_conferidas=len(individuals),grupos_h_brutos_conferidos=reconciled,
        percentuais_publicados_conferidos=len(raw['checks_percentuais']),resumo_portal=raw['resumo'],
        handoff=dict(restrito_sha256=sha(restricted),agregado_sha256=sha(output)),
        fontes_inalteradas=sha(t3)==T03 and sha(t4)==T04)
    write(evidence/'analise-real.json',summary)
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    try:
        main()
    except Exception as exc:
        # Mensagens são deliberadamente estáticas: não imprimir traceback/linhas de dados.
        print('Analise T05 interrompida; classe='+type(exc).__name__+('; '+str(exc) if isinstance(exc,ValueError) else '; detalhes restritos'),file=sys.stderr)
        print('Localizadores de codigo: '+str([(frame.name,frame.lineno) for frame in traceback.extract_tb(exc.__traceback__)]),file=sys.stderr)
        raise SystemExit(1)
