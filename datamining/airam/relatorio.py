"""Apresentação agregada e preparação nominal local, sem inferência ecológica.

O relatório aceita somente o contrato agregado T10. A preparação nominal é uma
interface separada e seu retorno é dado pessoal restrito, mesmo sem nomes.
"""
from copy import deepcopy
from fractions import Fraction
import hashlib
import html
import json
from pathlib import Path
from .metas import meta_acertos

VERSION = 'airam-relatorio-t10-v1'
CONTEXT = ('avaliacao_id','ano_avaliacao','ciclo','ano_escolar','componente','fonte_id','sha256','exportacao')
PRIVACY_KEYS = {'nome','nome_bruto','nome_normalizado','aluno_local_id','avaliacao_local_id',
                'matricula_local_id','membros','alunos','pseudonimo','origens'}
PUBLIC_KEYS = {'versao_schema','fontes','componentes','metas_A','habilidades','associacoes',
               'grupos','cenarios','sensibilidade','diagnosticos','limites','resumo'}
GEOMETRY_LIMIT = ('Em L1, L2, L3, L5 e M2, O-controle e P-controle tiveram distâncias '
    'quadradas iguais. L1/L2 tiveram seleções diferentes. A causa numérica específica '
    'não foi isolada. Isso é sensibilidade do ajuste e não demonstra benefício curricular '
    'ou mudança geométrica. Observado e propagado são estimandos separados.')


def _canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def _individual_key(row):
    values = [row.get(k) for k in CONTEXT] + [row.get('aluno_local_id'),row.get('avaliacao_local_id')]
    if any(v is None or v == '' for v in values):
        raise ValueError('Contexto/identidade individual incompleto')
    return hashlib.sha256(_canonical(values).encode('utf-8')).hexdigest()


def _valid_count(c,d):
    if type(c) is not int or type(d) is not int or d<=0 or not 0<=c<=d:
        raise ValueError('Contagens individuais invalidas')


def preparar_intervencao(observacoes: list[dict], metas: dict, vinculos: list[dict], grupos: list[dict]) -> list[dict]:
    """Uma linha por aplicação, conservando contexto e medidas individuais.

    Ordem: evidência insuficiente, lacuna B, medidas próprias E/F, B atingida.
    Dentro da lacuna B, maior necessidade primeiro; proximidade é cenário opcional.
    O desempate lexicográfico conserva chave contextual, sem posição física.
    """
    order=metas.get('ordenacao','necessidade')
    if order not in {'necessidade','proximidade'}:
        raise ValueError('Ordenacao desconhecida')
    # Valida ambos os controles, embora Meta A não possua distância individual.
    for control in ('A','B'):
        meta_acertos(None,None,metas[control])
    rows=[];seen=set()
    for source in observacoes:
        r=deepcopy(source);key=_individual_key(r)
        if key in seen:
            raise ValueError('Aplicacao contextual duplicada')
        seen.add(key)
        comp=r['componente']
        if comp not in {'LEITURA','MATEMATICA','ESCRITA','FLUENCIA'} or type(r['participacao']) is not bool:
            raise ValueError('Componente/participacao invalido')
        own=comp in {'ESCRITA','FLUENCIA'}
        c,d=r.get('acertos'),r.get('oportunidades')
        if not own:
            result=meta_acertos(c,d,metas['B'])
            if not r['participacao'] and (c is not None or d is not None):
                raise ValueError('Mascara de participacao incoerente')
            available=r['participacao'] and result['status']=='disponivel'
        else:
            if c is not None or d is not None:
                raise ValueError('Unidade propria nao aceita contagens de itens')
            result=dict(meta='B',alvo=None,lacuna=None,atingida=None,status='unidade_nao_aplicavel')
            available=r['participacao'] and any(m.get('disponibilidade') is True for m in r.get('medidas',[]))
        hs=[];positions=set()
        for h in r.get('habilidades',[]):
            position=h['posicao']
            if position in positions:
                raise ValueError('H individual duplicada')
            positions.add(position)
            hc=h.get('acertos',h.get('numerador'));hd=h.get('oportunidades',h.get('denominador'))
            if h.get('disponibilidade') is not True:
                if hc is not None or hd is not None:
                    raise ValueError('Mascara de habilidade incoerente')
                continue
            _valid_count(hc,hd)
            if not r['participacao']:
                raise ValueError('Habilidade de nao participante')
            if hc==hd:
                continue
            edges=[deepcopy(v) for v in vinculos if v['ano_avaliado']==r['ano_escolar']
                and v['ano_avaliacao']==r['ano_avaliacao'] and v['avaliacao_id']==r['avaliacao_id']
                and v['ciclo_avaliado']==r['ciclo'] and v['componente']==comp and v['posicao']==position]
            if len({(v.get('fonte_posicao'),v.get('versao_posicao')) for v in edges})>1:
                raise ValueError('Contexto curricular ambiguo: fontes/versoes concorrentes')
            hs.append(dict(posicao=position,acertos=hc,oportunidades=hd,taxa=hc/hd,vinculos=edges,
                atividade=('Sondar com tarefas novas do descritor documentado, registrar estratégia e ajuda, '
                    'praticar com apoio e verificar novamente sem apoio. Os blocos não identificam os itens errados. '
                    'Adequação e eficácia pendem de revisão docente.')))
        hs.sort(key=lambda h:(Fraction(h['acertos'],h['oportunidades']),h['posicao']))
        gap=result['lacuna']
        cls=0 if not available else 1 if not own and gap>0 else 2 if own else 3
        membership=[dict(grupo_id=g['grupo_id'],versao=g['versao'],tipo=g.get('tipo'),
            contexto=deepcopy(g['contexto'])) for g in grupos
            if r['aluno_local_id'] in g.get('membros',[])
            and all(g['contexto'].get(k)==r[k] for k in CONTEXT)]
        support=('Verificar participação, barreiras de acesso e obter nova evidência na unidade original.' if cls==0
            else 'Garantir apoio orientado às dificuldades observadas e verificar estratégias com o docente.' if cls==1
            else 'Revisar tarefas e categoria original, preservando unidade e disponibilidade.' if own
            else 'Manter acompanhamento e rever dificuldades pontuais observadas.')
        r.update(chave=key,meta_B=result,meta_A_status='unidade_nao_aplicavel' if own else 'categoria_CAEd_original_sem_corte_em_acertos',
            acertos_ate_adequacao=None,disponivel=available,classe_prioridade=cls,
            habilidades_prioritarias=hs[:3],grupos=membership,apoio_sugerido=support,
            revisao_docente='pendente',notas_docentes='',data_reavaliacao=None,
            limite_identidade='local_provisorio_sem_id_institucional',
            criterio_reavaliacao='Após ciclo acordado com docente ou nova avaliação comparável, com data e apoios registrados.')
        rows.append(r)
    # Desempate contextual legível e independente de hash/ordem das linhas.
    rows.sort(key=lambda r:(r['classe_prioridade'],
        ((-1 if order=='necessidade' else 1)*r['meta_B']['lacuna']) if r['classe_prioridade']==1 else 0,
        tuple(str(r[k]) for k in CONTEXT),r['aluno_local_id'],r['avaliacao_local_id']))
    for i,r in enumerate(rows,1):
        r['ordem']=i
    return rows


def validar_agregado(value, path='raiz'):
    """Bloqueia identidade mesmo em objetos não apresentados/ocultos."""
    if isinstance(value,dict):
        for key,item in value.items():
            if key.lower() in PRIVACY_KEYS:
                raise ValueError('privacidade: campo individual em '+path)
            validar_agregado(item,path+'.'+key)
    elif isinstance(value,list):
        for item in value:
            validar_agregado(item,path+'[]')


def _escape(value):
    if value is None:
        return '<span class="ausente">não disponível</span>'
    if isinstance(value,bool):
        return 'sim' if value else 'não'
    if isinstance(value,(dict,list)):
        return '<details><summary>Ver detalhes</summary><pre>'+html.escape(json.dumps(value,ensure_ascii=False,indent=2))+'</pre></details>'
    if isinstance(value,float):
        return html.escape(f'{value:.5g}')
    return html.escape(str(value))


def _table(rows, columns):
    if not rows:
        return '<p class="ausente">Sem registros neste recorte.</p>'
    header=''.join('<th scope="col">'+html.escape(label)+'</th>' for key,label in columns)
    body=''.join('<tr>'+''.join('<td>'+_escape(r.get(key))+'</td>' for key,_ in columns)+'</tr>' for r in rows)
    return '<div class="table-wrap"><table><thead><tr>'+header+'</tr></thead><tbody>'+body+'</tbody></table></div>'


def _figures(resultados,folder):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'svg.fonttype':'none',
        'axes.spines.top':False,'axes.spines.right':False,'figure.dpi':140,'savefig.dpi':220})
    paths=[]
    def save(fig,name):
        for ext in ('png','svg'):
            path=folder/(name+'.'+ext);fig.savefig(path,bbox_inches='tight');paths.append(path)
        plt.close(fig)
    school=[r for r in resultados['metas_A'] if r['nivel']=='escola']
    fig,ax=plt.subplots(figsize=(10,5))
    labels=[str(r['ano_escolar'])+'º '+r['componente'].title() for r in school]
    values=[r['adequados']/r['avaliados'] if r['avaliados'] else np.nan for r in school]
    bars=ax.barh(labels,values,color='#315c87')
    for b,r,v in zip(bars,school,values):
        if r['avaliados']:
            near_target=abs(v-.8)<.07
            ax.text(v-.02 if near_target else min(v+.015,.94),b.get_y()+b.get_height()/2,
                f"{r['adequados']}/{r['avaliados']}",va='center',ha='right' if near_target else 'left',
                color='white' if near_target else 'black',fontsize=9)
    ax.axvline(.8,color='#9c4f14',linestyle='--',label='Meta A de referência (80%)')
    ax.set(xlim=(0,1.07),xlabel='Proporção de adequados CAEd entre avaliados',title='Meta A por ano e componente')
    ax.legend(loc='lower right',fontsize=8);fig.tight_layout();save(fig,'meta-a')
    components=resultados['componentes']
    fig,ax=plt.subplots(figsize=(10,max(4,len(components)*.27)))
    ys=np.arange(len(components));cad=[r['cadastros'] for r in components];valid=[r['com_resultado'] for r in components]
    ax.barh(ys,cad,color='#e0e5ea',label='Cadastros');ax.barh(ys,valid,color='#3e7865',label='Com resultado disponível')
    ax.set_yticks(ys,[str(r['ano_escolar'])+'º '+r['componente'].title() for r in components]);ax.invert_yaxis()
    for y,n,d in zip(ys,valid,cad):ax.text(d+.4,y,f'{n}/{d}' if d else 'sem arquivo / universo não definido',va='center',fontsize=8)
    ax.set(xlabel='Aplicações por instrumento (não estudantes distintos)',title='Cobertura de resultados nas unidades originais')
    ax.legend(fontsize=8);fig.tight_layout();save(fig,'cobertura')
    hs=[r for r in resultados['habilidades'] if r.get('nivel')=='escola' and r.get('posicao')]
    if hs:
        contexts=sorted({(r['ano_escolar'],r['componente']) for r in hs});positions=sorted({r['posicao'] for r in hs})
        matrix=np.full((len(contexts),len(positions)),np.nan)
        fig,ax=plt.subplots(figsize=(14,max(4,len(contexts)*.52)))
        for r in hs:
            if r['taxa_observada'] is not None:matrix[contexts.index((r['ano_escolar'],r['componente'])),positions.index(r['posicao'])]=r['taxa_observada']
        image=ax.imshow(matrix,vmin=0,vmax=1,cmap='cividis',aspect='auto')
        for r in hs:
            if r['taxa_observada'] is not None:
                i=contexts.index((r['ano_escolar'],r['componente']));j=positions.index(r['posicao'])
                ax.text(j,i,f"{r['acertos']}/{r['oportunidades']}",ha='center',va='center',fontsize=6,color='white' if matrix[i,j]<.45 else 'black')
        ax.set_xticks(range(len(positions)),positions,rotation=45,ha='right')
        ax.set_yticks(range(len(contexts)),[f'{y}º {c.title()}' for y,c in contexts])
        ax.set_title('Acertos e oportunidades observadas por bloco contextualizado')
        fig.colorbar(image,ax=ax,label='C/D observado (0–1)');fig.tight_layout();save(fig,'habilidades')
    return paths


def gerar_relatorio(resultados: dict, out_dir: Path) -> list[Path]:
    """Escreve HTML offline, JSON agregado e figuras científicas autônomas."""
    validar_agregado(resultados)
    if set(resultados)!=PUBLIC_KEYS or resultados['versao_schema']!=VERSION:
        raise ValueError('Contrato agregado T10 invalido')
    for p in resultados['grupos']:
        if p.get('status_publicacao')=='suprimido_n_menor_5':
            continue
        required={'contexto','fontes_sha256','criterio_pertencimento','habilidades','medidas_proprias','ressalvas','reavaliacao'}
        if not required.issubset(p) or not p.get('fontes_sha256'):
            raise ValueError('perfil incompleto: fonte/descricao curricular ausente')
    out_dir=Path(out_dir);out_dir.mkdir(parents=True,exist_ok=True)
    figures=out_dir/'figuras';figures.mkdir(exist_ok=True)
    paths=_figures(resultados,figures)
    sections=[]
    sections.append('<section id="leitura"><h2>Como interpretar e usar</h2><p>Este recorte reúne o Ciclo I 2026. '
        'As contagens são exatas para os registros observados da escola. Incerteza de mensuração, cobertura e generalização '
        'permanece distinta das contagens. Cada aplicação pertence a um instrumento e ano. '
        'Turma e escola se sobrepõem. As aplicações de componentes diferentes não somam estudantes distintos.</p>'
        '<p>Meta A: ao menos 80% dos avaliados classificados como Adequado na categoria original CAEd. '
        'Meta B: alvo individual de teto(meta × oportunidades), atualmente 18/22 em leitura e matemática. '
        'As metas são independentes. Não existe corte oficial auditado em acertos para mudar a categoria CAEd. '
        'Escrita e fluência conservam unidades próprias e não recebem metas artificiais de itens.</p>'
        '<p>A fila nominal está apenas no arquivo local restrito. Ausência de evidência requer sondagem e acesso ao apoio. '
        'Maiores lacunas permanecem elegíveis. H abaixo de 80% não é pré-requisito para atingir 80% no total. '
        'As atividades precisam de adequação e revisão docente, com nova medida e data registradas.</p></section>')
    sections.append('<section id="cobertura"><h2>Universos e cobertura por componente</h2>'+_table(resultados['componentes'],[
        ('ano_escolar','Ano'),('componente','Componente'),('cadastros','Cadastros'),('participantes','Participantes'),
        ('com_resultado','Com resultado'),('unidades','Unidades originais'),('status_fonte','Disponibilidade da fonte')])+'<img src="figuras/cobertura.svg" alt="Cobertura de resultados por ano e componente"></section>')
    sections.append('<section id="metas"><h2>Meta A e distância institucional</h2><p>O alvo escolar usa o teto do denominador escolar. '
        'Não soma os tetos das turmas. Conversões são quantidades aritméticas de categorias, sem garantia de intervenção.</p>'+
        _table(resultados['metas_A'],[('ano_escolar','Ano'),('componente','Componente'),('nivel','Nível'),('turma','Turma'),
            ('avaliados','Avaliados'),('adequados','Adequados'),('alvo','Alvo A'),('conversoes','Conversões'),('meta','Meta A')])+
        '<img src="figuras/meta-a.svg" alt="Adequados por avaliados, com meta A de 80%"></section>')
    sections.append('<section id="habilidades"><h2>Habilidades observadas e currículo contextual</h2><p>C/D usa soma dos acertos dividida '
        'pela soma das oportunidades. Cada linha da figura é um instrumento distinto; células brancas estão fora do instrumento. '
        'H01 de instrumentos diferentes não representa a mesma variável. Blocos agregados não identificam '
        'itens individuais errados. Uma associação curricular publicada não comprova domínio BNCC, equivalência integral ou pré-requisito causal.</p>'+
        ('<img src="figuras/habilidades.svg" alt="C/D por bloco e contexto; áreas vazias representam posição não disponível">' if any(p.stem=='habilidades' for p in paths) else '')+
        _table(resultados['habilidades'],[('ano_escolar','Ano'),('componente','Componente'),('nivel','Nível'),('turma','Turma'),
            ('posicao','Posição'),('acertos','Acertos'),('oportunidades','Oportunidades'),('validas','Células válidas'),('ausentes','Ausentes'),
            ('taxa_observada','C/D observado'),('curriculo','Vínculos, textos, fontes e ressalvas')])+'</section>')
    sections.append('<section id="associacoes"><h2>Associações completas e ausências justificadas</h2><p>Pearson e Spearman são descritivos '
        'do conjunto avaliado. N é o número de pares completos da variável e pode variar por tarefa. H–total usa total sem o próprio bloco. '
        'BH foi aplicado na família planejada. Não filtrar apenas resultados significativos. Os intervalos/reamostragens descrevem a sensibilidade '
        'ao desenho e não tornam o censo escolar uma amostra aleatória nem demonstram causalidade.</p>'+
        _table(resultados['associacoes'],[('ano_escolar','Ano'),('tipo','Tipo'),('x','Variável X'),('y','Variável Y'),('metodo','Método'),
            ('n','Pares'),('coeficiente','Coeficiente'),('p','p'),('q','q BH'),('familia','Família'),('motivo_coeficiente','Ausência do coeficiente'),
            ('motivo_inferencia','Limite inferencial'),('sensibilidade','Intervalos e sensibilidade'),('limite','Ressalva')])+'</section>')
    sections.append('<section id="grupos"><h2>Perfis e agrupamentos exploratórios</h2><p>Grupos por regras, solução observada e controles '
        'propagados são alternativas sobrepostas. Não somar seus N. Rótulos descrevem evidência e não capacidade fixa. '
        'Grupos pequenos mantêm supressão pública. Mínimo estatístico de cinco não limita o atendimento individual.</p><p class="alerta">'+
        html.escape(GEOMETRY_LIMIT)+'</p>'+_table(resultados['diagnosticos'],[('ano','Ano'),('componente','Componente'),('n','N'),
        ('observado_status','Observado'),('comparacao','Comparabilidade'),('max_diferenca_distancias_quadradas_controle','Diferença máxima quadrática'),
        ('controle','Seleções por braço'),('interpretacao_geometria','Interpretação')]))
    for p in resultados['grupos']:
        sections.append('<article class="perfil"><h3>'+html.escape(p.get('titulo_perfil',p.get('grupo_id','Perfil')))+
            '</h3><p class="alerta">'+html.escape(GEOMETRY_LIMIT)+'</p><dl>'+''.join('<dt>'+html.escape(k.replace('_',' '))+'</dt><dd>'+_escape(v)+'</dd>' for k,v in p.items())+'</dl></article>')
    sections.append('</section><section id="cenarios"><h2>Cenários condicionais e perdas</h2><p>Ganhos e perdas são hipóteses '
        'aritméticas. Os adequados podem sair da categoria no cenário de perdas. Não representam probabilidades, aulas necessárias '
        'ou efeitos de uma atividade. Previsão temporal não estimável com validação: faltam identidade longitudinal validada, datas reais '
        'e desfecho futuro, além da avaliação temporal de um modelo.</p>'+_table(resultados['cenarios'],[(k,k.replace('_',' ')) for k in
        ['ano_escolar','componente','nivel','turma','cenario','hipoteses','meta_A','meta_B_resumo']])+
        '<h3>Sensibilidade da Meta A às saídas</h3>'+_table(resultados['sensibilidade'],[(k,k.replace('_',' ')) for k in
        ['ano_escolar','componente','nivel','turma','saidas','meta_A']])+'</section>')
    sections.append('<section id="fontes"><h2>Fontes, reconciliação e limites</h2>'+_table([dict(fonte=k,sha256=v) for k,v in resultados['fontes'].items()],
        [('fonte','Fonte/versão'),('sha256','SHA256')])+_escape(resultados['resumo'])+'<ul>'+''.join('<li>'+html.escape(s)+'</li>' for s in resultados['limites'])+
        '</ul><p>As figuras PNG e SVG são autônomas. O arquivo <a href="tabelas.json">tabelas.json</a> conserva todos os campos agregados '
        'com proveniência para conferência. Validação computacional local não equivale a validação pedagógica externa.</p></section>')
    template=Path(__file__).resolve().parents[1]/'reports/templates/relatorio.html'
    page=template.read_text(encoding='utf-8').replace('{{CONTEUDO}}','\n'.join(sections))
    target=out_dir/'relatorio.html';target.write_text(page,encoding='utf-8');paths.append(target)
    target=out_dir/'tabelas.json';target.write_text(json.dumps(resultados,ensure_ascii=False,sort_keys=True,indent=2,allow_nan=False)+'\n',encoding='utf-8');paths.append(target)
    return paths
