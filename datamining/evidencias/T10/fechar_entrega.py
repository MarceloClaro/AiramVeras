"""Concilia entrega final apos ajuste, preservando manifestos/relato anteriores."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'evidencias/T10'
CODE=['airam/relatorio.py','reports/templates/relatorio.html','reports/build_workbook.mjs',
    'tests/test_relatorio.py','tests/test_intervencao.py','tests/fixtures/t10_workbook.json',
    'tests/fixtures/t10_workbook_heterogeneo.json','docs/dicionario-t10.md','.gitattributes']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(name):return json.loads((OUT/name).read_text(encoding='utf-8'))
def main():
    previous=read('entrega-final.json');wb=read('workbook-resultado.json');layout=read('layout-resultado.json')
    invariance=read('refinamento02-invariancia-resultado.json');audit=read('contraprova02-resultado.json')
    move=read('refinamento-canonico-resultado.json');snap=read('workbook04-antes.json')
    suite=read('suite06-antes.json');archive=read('codigo-autoria04-preservado.json')
    scan=read('previa-segura-05-resultado.json')
    checkpoint=ROOT/'restrito/t10/checkpoint.json'
    folder=ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53'
    xlsx=folder/'intervencao-restrita.xlsx';old=folder/'versoes/autoria04/intervencao-restrita.xlsx'
    assert sha(xlsx)==layout['xlsx_sha256']==invariance['xlsx_sha256']==audit['xlsx_sha256']==move['sha256_final']
    assert sha(old)==wb['xlsx_sha256']==layout['origem_sha256']==invariance['origem_sha256']==move['sha256_versao04']
    assert sha(checkpoint)==wb['entrada_sha256']==audit['checkpoint_restrito_sha256']
    assert wb['builder_sha256']==archive['fontes']['reports/build_workbook.mjs']['sha256']==snap['hashes_codigo']['reports/build_workbook.mjs']
    assert sha(ROOT/'reports/build_workbook.mjs')==layout['builder_sha256']==scan['builder_sha256']
    for p in CODE:assert sha(ROOT/p)==suite['hashes_codigo'][p]
    for label in ['workbook04','layout02','invariancia03','contraprova-final02','suite06','green16','previa05','previa-conferencia05']:
        assert read(label+'-recibo.json')['codigo_saida']==0,label
    assert invariance['status']==audit['status']==scan['status']=='PASS'
    assert '360 passed' in (OUT/'suite06.log').read_text(encoding='utf-8')
    # Native inspection is by the controller, using a fully artificial copy only.
    visual=ROOT/'.superpowers/sdd/implementation-plan/inspecao-nativa-artificial-t10-final.md'
    assert visual.is_file(),'Aguardar recibo visual final do controlador'
    report=ROOT/'.superpowers/sdd/implementation-plan/task-10-report.md'
    preserved=report.with_name('task-10-report-inicial.md')
    final=OUT/'entrega-final02.json'
    if preserved.exists() or final.exists():raise ValueError('Preservar fechamento anterior')
    preserved.write_bytes(report.read_bytes())
    manifest={**previous,'timestamp':datetime.now(timezone.utc).isoformat(),
        'manifesto_anterior_sha256':sha(OUT/'entrega-final.json'),
        'codigo_sha256':{p:sha(ROOT/p) for p in CODE},'auditoria':audit,
        'autoria04':wb,'refinamento':layout,'invariancia':invariance,
        'previa_artificial_final':scan,'inspecao_nativa_recibo':str(visual.resolve()),'inspecao_nativa_sha256':sha(visual),
        'suite':'360 passed; suite06','recibos_sha256':{p.name:sha(p) for p in sorted(OUT.glob('*-recibo.json'))}}
    manifest['saidas_sha256'][str(xlsx.resolve())]=sha(xlsx)
    final.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    text=report.read_text(encoding='utf-8')
    text=text.replace(previous['saidas_sha256'][str(xlsx.resolve())],sha(xlsx),1)
    text=text.replace('Manifesto público minimizado:', 'Manifesto público minimizado inicial (preservado; substituído pelo final02 no complemento):',1)
    text+='''\n## Fechamento após correção visual e invariância integral\n\n'''
    text+=f'''Data: {manifest['timestamp']}. O relato acima conserva a cronologia anterior; o fechamento inicial foi preservado integralmente em `{preserved}`. O manifesto vigente é `{final}` (SHA256 `{sha(final)}`).

O XLSX canônico agora é `{xlsx}` (SHA256 `{sha(xlsx)}`). A autoria04 original permanece em `{old}` (SHA256 `{sha(old)}`), após controles, permutação integral e restauração, exportação e reabertura reais. Seu builder foi `{wb['builder_sha256']}`; não lhe foi atribuído o código novo. A execução04 iniciou2026-10-24T07:39:10.688UTC e terminou08:49:35.460UTC. A permutação de640 linhas terminou em1793s; restauração/checagens seguintes concluíram sem OOM/timeout. Custo local alto deve ser considerado pela CLI, sem timeout curto implícito nem promessa de desempenho.

Ajuste oficial JS final: `{layout['builder_sha256']}`. layout01 preservou a primeira revisão visual (SHA094b492f54b1a86ad6a6aadcef47b532a3eca24525317ff39ad9cc666ce3408d); layout02 corrigiu também o somatório de linhas quebradas e a exibição do helper. A invariância independente conferiu {invariance['celulas_conferidas']} células e {invariance['formulas_identicas']} fórmulas idênticas, todas as validações/tabelas com relacionamentos resolvidos, nenhum externalLink/referência externa. Somente135 textos deliberados mudaram: Grupos!G8:G140, Metas!A9 e retirada do rótulo técnico Intervenção nominal!Z7. Todos os demais valores, fórmulas, máscaras, notas e controles permaneceram iguais. Não se repetiram controles/permutação640 após alteração exclusivamente visual. Contraprova final: {audit['verificacoes']} verificações PASS,640 aplicações,6074 medidas e157 relações curriculares.

RED09/green14 já cobriam legibilidade e idempotência do ajuste. A inspeção nativa da primeira revisão detectou altura insuficiente em resumos com quebras. RED10 demonstrou85pt para9linhas, abaixo de137pt; corrigida a soma dos segmentos de cada célula. green15:28 testes focais. RED11 demonstrou rótulo técnico ainda presente após largura zero; green16:28 testes focais após retirar Z7 e aplicar formato padrão `;;;` em Z8:Z647. Esse formato retira a exibição numérica, sem flag hidden, segurança ou mudança dos valores/fórmulas; todos os erros continuam no scan integral. Suíte06 final:360 testes passaram, exit0. A falha invariancia01 comparava IDs internos regenerados; invariancia02 passou após resolver seus destinos e estruturas. Não foi divergência de conteúdo nem perda de validação/tabela; tentativas preservadas. Mutacoes03 continua sendo evidência dos cinco comportamentos analíticos/privacidade, antes destes ajustes de altura.

A prévia inicial1f157ffd foi mantida estável. A prévia b471f3ef14e5538dde8a8d1d3e21cc874e61577d8f3e428d3ade49779e55ffb3 foi reconferida nativamente; oportunidades e estado/unidade ficaram legíveis, e a altura dos resumos motivou a correção acima. A cópia artificial final está em `{folder/'apresentacao03/previas-sinteticas/inspecao-artificial.xlsx'}` (SHA256 `{scan['xlsx_sha256']}`); scan JSON/OOXML `{OUT/'previa-segura-05-resultado.json'}` PASS. Regra: todos os conteúdos individuais artificiais, incluindo H, escores, notas e pertencimento; frases fictícias com espaços preservam apenas comprimentos/quebras desafiadores. O metadado incorreto de produtor no scan03 foi corrigido aditivamente em previa03-proveniencia-correcao.json, preservando o recibo anterior; produtor28a3502b e verificador67fdb1 foram distinguidos. Os scans finais05 reportam separadamente produtor e verificador.

Conferência focal nativa final pelo controlador: `{visual}` (SHA256 `{sha(visual)}`). Somente cópia completamente artificial; as seis abas foram vistas na inspeção inicial e as regiões alteradas nas revisões. Autoria/editoração XLSX permaneceu JS; LibreOffice/Poppler só produziram PDF/imagens de leitura. Não equivale a Microsoft Excel nativo nem a inspeção visual de todas as640 linhas nominais. As limitações de renderer Windows/Excel e contas/ACL permanecem observações explícitas; apresentação e preservação de escopo foram tratadas antes do handoff.

Contrato CLI complementar: `--refine-layout CHECKPOINT ORIGINAL_XLSX DESTINO_RESTRITO` preserva ORIGINAL e reabre o novo; exigir o recibo de comparação integral antes de promover. A execução habitual `--build` já incorpora o layout corrigido, produz um arquivo canônico e a cópia artificial separada; não repetir marcador. Se a fonte/calibragem muda, regenerar complexos no pipeline e preservar/reaplicar notas por chave. O checkpoint T11 segue `{sha(checkpoint)}`. Os hashes de código abaixo substituem a tabela histórica para o estado final:

| Arquivo | SHA256 final |
|---|---|
'''
    text+='\n'.join(f'| {p} | {h} |' for p,h in manifest['codigo_sha256'].items())+'\n'
    report.write_text(text,encoding='utf-8')
    print(json.dumps(dict(status=manifest['status'],manifesto=str(final),manifesto_sha256=sha(final),xlsx_sha256=sha(xlsx))))
if __name__=='__main__':main()
