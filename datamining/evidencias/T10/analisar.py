"""Integra fontes autenticadas e prepara entregas locais T10, sem log individual."""
from collections import defaultdict
from copy import deepcopy
import hashlib
import html
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from airam.relatorio import CONTEXT, GEOMETRY_LIMIT, gerar_relatorio, preparar_intervencao

EXPECTED={
 'restrito/t03/mapa-nominal.json':'5a4b62dab471de27b7a9b2fc510806f66fd205a65f28e5ab30c60e463d7ff3be',
 'restrito/t05/checkpoint.json':'6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b',
 'estatistica/t05/checkpoint.json':'5bfa87b38394d171589a7799751127dceb7d81587bbbfcefa67d2bb4a8420231',
 'curriculo/t04/checkpoint.json':'a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796',
 'estatistica/t06/entrega/checkpoint.json':'2a0472e9b391e0a1c66af53c6d4572f00109a81b49ff547fd5cf8bf8c3e42570',
 'estatistica/t07/checkpoint.json':'71a0302d7ec9ae0f837069eea3b5c867052ff3885d5a9fb7491eee616abd9d58',
 'estatistica/t08/checkpoint.json':'8c45186534b952df47574b636e2f101f3c784fcb9f03a7eb5c9e5537dba1e24e',
 'restrito/t08/checkpoint.json':'44fe791ddfe15ea5449ac052fe1a7fc37838388732831c9d20f007255d2e4526',
 'estatistica/t09/checkpoint.json':'150592d325fde9c80bfd98717a974b3a53e816987601b1b3968168e558f14339',
 'restrito/t09/checkpoint.json':'0e8359f648e3a4a01dce2a817d2fb7fb5397b31752a83c04ca2082f37cbc0901',
}


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def digest(obj):return hashlib.sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def write(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    content=json.dumps(obj,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n'
    if path.exists() and path.read_text(encoding='utf-8')!=content:
        preserved=list((path.parent/'versoes').glob('analise*/'+path.name))
        if not any(p.is_file() and sha(p)==sha(path) for p in preserved):
            raise ValueError('Saida existente divergente: preservar versao antes de atualizar')
    path.write_text(content,encoding='utf-8')


def auth(relative,expected):
    p=ROOT/relative
    if sha(p)!=expected:raise ValueError('Hash de entrada divergente: '+relative)
    return json.loads(p.read_text(encoding='utf-8'))


def instrument(r):return digest([r[k] for k in CONTEXT])


def flatten_profiles(checkpoint):
    result=[]
    def add(profiles,recorte):
        for original in profiles:
            p=deepcopy(original)
            if 'nome' in p:p['titulo_perfil']=p.pop('nome')
            p['recorte']=recorte
            p.setdefault('ressalvas',[]).append(GEOMETRY_LIMIT)
            result.append(p)
    for inst in checkpoint['instrumentos']:
        add(inst['perfis_regras'],'regra operacional')
        add(inst['perfis_observado'],'observado operacional')
        for scenario in inst['cenarios']:
            for arm,profiles in scenario['perfis'].items():add(profiles,scenario['cenario']+'/'+arm)
    for inst in checkpoint['unidades_proprias']:add(inst['perfis'],'categoria original E/F')
    return result


def main():
    loaded={p:auth(p,h) for p,h in EXPECTED.items()}
    source_private=loaded['restrito/t05/checkpoint.json'];tables=source_private['observado']
    public5=loaded['estatistica/t05/checkpoint.json'];curriculum=loaded['curriculo/t04/checkpoint.json']
    t8=loaded['estatistica/t08/checkpoint.json'];p8=loaded['restrito/t08/checkpoint.json'];t9=loaded['estatistica/t09/checkpoint.json']
    nominal=loaded['restrito/t03/mapa-nominal.json']
    # Diagnóstico atualizado autenticado contra o arquivo revisado e sua referência de T08.
    diag_path='evidencias/T08/fix1-contraprova-resultado.json'
    committed=subprocess.check_output(['git','show','28d88e356f3ce744f250331aa2f90a8de5bdc6be:'+diag_path],cwd=ROOT)
    observed=(ROOT/diag_path).read_bytes()
    if committed.replace(b'\r\n',b'\n')!=observed.replace(b'\r\n',b'\n'):raise ValueError('Diagnostico T08 alterado')
    diagnostics=json.loads(observed)
    if diagnostics['hashes']['estatistica/t08/checkpoint.json']!=EXPECTED['estatistica/t08/checkpoint.json']:raise ValueError('Diagnostico T08 de outra versao')
    sources={**EXPECTED,diag_path:sha(ROOT/diag_path),'pipeline/relatorio.py':sha(ROOT/'airam/relatorio.py'),
        'pipeline/build_workbook.mjs':sha(ROOT/'reports/build_workbook.mjs'),'pipeline/coletor_T10':sha(Path(__file__))}
    names={r['aluno_local_id']:r['nome_bruto'] for r in nominal}
    if len(names)!=len(nominal):raise ValueError('Mapa nominal nao bijetivo')
    measures=defaultdict(list)
    for table in ('habilidades','escrita','fluencia'):
        for m in tables[table]:measures[m['avaliacao_local_id']].append(deepcopy(m))
    groups=[]
    for inst in p8['instrumentos']:
        groups.extend(inst['perfis_regras']);groups.extend(inst['perfis_observado'])
    for inst in p8['unidades_proprias']:groups.extend(inst['perfis'])
    evaluations=[]
    for source in tables['avaliacoes']:
        r=deepcopy(source);ms=measures[r['avaliacao_local_id']]
        if r['aluno_local_id'] not in names:raise ValueError('Nome restrito sem correspondencia')
        r['nome']=names[r['aluno_local_id']];r['habilidades']=ms if r['componente'] in ('LEITURA','MATEMATICA') else []
        r['medidas']=ms if r['componente'] in ('ESCRITA','FLUENCIA') else []
        r['instrumento']=instrument(r)
        if r['habilidades'] and r['acertos'] is not None:
            if sum(m['numerador'] for m in ms)!=r['acertos'] or sum(m['denominador'] for m in ms)!=r['oportunidades']:
                raise ValueError('Totais individuais nao reconciliam H')
        evaluations.append(r)
    rows=preparar_intervencao(evaluations,{'A':.8,'B':.8},curriculum['vinculos_posicoes'],groups)
    by_app={r['avaliacao_local_id']:r for r in rows}
    if len(by_app)!=len(evaluations):raise ValueError('Aplicacao nominal nao bijetiva')
    components=[];scopes=[];by_instrument=defaultdict(list)
    for r in rows:by_instrument[instrument(r)].append(r)
    for inst,rs in sorted(by_instrument.items(),key=lambda x:(x[1][0]['ano_escolar'],x[1][0]['componente'])):
        r=rs[0]
        components.append(dict(ano_escolar=r['ano_escolar'],componente=r['componente'],cadastros=len(rs),
            participantes=sum(x['participacao'] for x in rs),com_resultado=sum(x['disponivel'] for x in rs),
            unidades=sorted({m['unidade'] for x in rs for m in x['medidas']}) if r['medidas'] else ['itens'],status_fonte='arquivo_disponivel'))
        scopes.append(dict(ano_escolar=r['ano_escolar'],componente=r['componente'],instrumento=inst,nivel='escola',turma=None))
        for turma in sorted({x['turma'] for x in rs}):scopes.append(dict(ano_escolar=r['ano_escolar'],componente=r['componente'],instrumento=inst,nivel='turma',turma=turma))
    for unavailable in tables['disponibilidade_arquivos']:
        if not unavailable['disponibilidade']:
            components.append(dict(ano_escolar=unavailable['ano_escolar'],componente=unavailable['componente'],cadastros=0,
                participantes=0,com_resultado=0,unidades=[],status_fonte='arquivo_nao_disponivel; sem universo avaliado'))
    components.sort(key=lambda r:(r['ano_escolar'],r['componente']))
    metas=[]
    for x in public5['metas_A']:
        m=x['meta_A'];metas.append(dict(ano_escolar=x['ano_escolar'],componente=x['componente'],nivel=x['nivel'],turma=x['turma'],
            avaliados=m['avaliados'],adequados=m['adequados'],alvo=m['alvo'],conversoes=m['conversoes'],meta=.8,
            acertos_ate_adequacao=None,fonte_sha256=EXPECTED['estatistica/t05/checkpoint.json']))
    hrows=[]
    for original in public5['agregados']:
        r=deepcopy(original)
        r['curriculo']=[v for v in curriculum['vinculos_posicoes'] if v['ano_avaliado']==r['ano_escolar'] and v['componente']==r['componente']
            and v['posicao']==r['posicao'] and v['avaliacao_id']==r['avaliacao_id'] and v['ano_avaliacao']==r['ano_avaliacao'] and v['ciclo_avaliado']==r['ciclo']]
        hrows.append(r)
    profiles=flatten_profiles(t8)
    limits=list(dict.fromkeys(public5['limites']+loaded['estatistica/t06/entrega/checkpoint.json']['limites']+t9['limites']+[
        GEOMETRY_LIMIT,'Revisão docente, composição prática dos grupos e data de reavaliação pendentes.',
        'A identidade local é provisória; não comprova identidade longitudinal.',
        'Validação documental/computacional local, sem eficácia de atividades ou validação pedagógica externa.',
        'O relatório agregado é para revisão local; compartilhamento exige política institucional.',
        '407 percentuais compatíveis com precisão inteira ±0,5 ponto percentual; 406 reproduzem metade para cima. '
        'Leitura 4º/B/H13: 23/40=57,5%, publicado 57. Política oficial de empate desconhecida; original preservado.']))
    public=dict(versao_schema='airam-relatorio-t10-v1',fontes=sources,componentes=components,metas_A=metas,
        habilidades=hrows,associacoes=loaded['estatistica/t06/entrega/checkpoint.json']['associacoes'],grupos=profiles,
        cenarios=t9['cenarios'],sensibilidade=t9['sensibilidade_meta_A'],diagnosticos=diagnostics['diagnosticos'],limites=limits,
        resumo=dict(reconciliacao_portal=public5['resumo_portal'],divergencias=public5['divergencias_portal'],
            contrastes_grupos=[dict(contexto=i['contexto'],observado=i['observado_operacional'],
                cenarios=[{k:s[k] for k in ['cenario','status','motivo','selecao','propagacao','comparacoes','sensibilidade_limiares','sensibilidade_cobertura']}
                    for s in i['cenarios']],limite=GEOMETRY_LIMIT) for i in t8['instrumentos']],
            grafo=dict(equacao='W=B Bᵀ; A normaliza W sem diagonal; propagado=Σ K M P / Σ K M, K=A^s',
                limites='A² pode retornar ao próprio nó. Massa de grafo não é oportunidade/item. M1 sem vizinhos permanece ausente. Observado não é sobrescrito.'),
            config_grupos=t8['config'],proveniencia_grupos=t8.get('proveniencia_fix1'),gate_temporal=t9['gate_temporal']))
    # Validação de conteúdo por termos reais: só retorna booleanos, nunca termos/linhas.
    forbidden=set()
    for r in nominal:
        forbidden.update(str(r[k]) for k in ('nome_bruto','nome_normalizado','aluno_local_id','matricula_local_id'))
    forbidden.update(r['avaliacao_local_id'] for r in evaluations)
    serialized=json.dumps(public,ensure_ascii=False).casefold()
    if any(s.casefold() in serialized for s in forbidden if s):raise ValueError('privacidade: termo individual no agregado')
    targets=gerar_relatorio(public,ROOT/'relatorios/t10')
    for p in targets:
        if p.suffix in ('.html','.json','.svg'):
            content=p.read_text(encoding='utf-8').casefold()
            if any(s.casefold() in content or html.escape(s).casefold() in content for s in forbidden if s):raise ValueError('privacidade: termo individual na saida')
    individual_measures=[]
    for source in tables['avaliacoes']:
        r=by_app[source['avaliacao_local_id']]
        for original in measures[source['avaliacao_local_id']]:
            m=deepcopy(original)
            edges=[v for v in curriculum['vinculos_posicoes'] if v['ano_avaliado']==m['ano_escolar'] and v['componente']==m['componente']
                and v['posicao']==m['posicao'] and v['avaliacao_id']==m['avaliacao_id'] and v['ano_avaliacao']==m['ano_avaliacao'] and v['ciclo_avaliado']==m['ciclo']]
            m.update(chave=r['chave'],turma=r['turma'],codigo_caed='; '.join(sorted({v['codigo_caed'] for v in edges})),
                bncc='; '.join(sorted({v['codigo_bncc'] for v in edges})),
                ressalvas='; '.join(sorted({v['status_contextual']+'; '+v['status_semantico'] for v in edges})))
            individual_measures.append(m)
    private=dict(versao_schema='airam-workbook-t10-v1',sintetico=False,metas={'A':.8,'B':.8},intervencao=rows,
        habilidades=individual_measures,grupos=profiles,curriculo=curriculum['vinculos_posicoes'],fontes=sources,
        componentes=scopes,limites=limits,complexos=dict(versao_t08=t8['versao_schema'],config_sha256=t8['config_sha256'],
            recalc='Reexecutar pipeline; alterar metas não recalcula grupos, currículo ou associações.'))
    write(ROOT/'restrito/t10/checkpoint.json',private)
    result=dict(status='PASS',aplicacoes=len(rows),medidas=len(individual_measures),grupos=len(profiles),
        componentes=len(components),metas_A=len(metas),associacoes=len(public['associacoes']),
        publico_sem_termos_individuais=True,fontes_autenticadas=len(EXPECTED)+1,
        checkpoint_restrito_sha256=sha(ROOT/'restrito/t10/checkpoint.json'),
        saidas={p.relative_to(ROOT).as_posix():sha(p) for p in targets})
    write(ROOT/'evidencias/T10/analise-resultado.json',result)
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__':main()
