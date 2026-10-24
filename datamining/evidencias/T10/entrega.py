"""Fecha manifestos e relatório sem ler/publicar linhas individuais."""
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
    analysis=read('analise-resultado.json');wb=read('workbook-resultado.json');audit=read('contraprova-resultado.json')
    snap=read('workbook04-antes.json');suite=read('suite05-antes.json');acl=read('acl-destino-resultado.json')
    code04=read('codigo-autoria04-preservado.json')
    checkpoint=ROOT/'restrito/t10/checkpoint.json'
    xlsx=ROOT/'restrito/outputs/01a16157-2a68-7253-9591-de126647cf53/intervencao-restrita.xlsx'
    assert sha(xlsx)==wb['xlsx_sha256']==audit['xlsx_sha256']
    assert sha(checkpoint)==wb['entrada_sha256']==audit['checkpoint_restrito_sha256']
    assert code04['fontes']['reports/build_workbook.mjs']['sha256']==wb['builder_sha256']==snap['hashes_codigo']['reports/build_workbook.mjs']
    for p in CODE:assert sha(ROOT/p)==suite['hashes_codigo'][p]
    assert wb['roundtrip_sem_erros'] and wb['fila_conferida_todas_linhas'] and audit['status']=='PASS'
    assert read('suite05-recibo.json')['codigo_saida']==0 and read('workbook04-recibo.json')['codigo_saida']==0
    assert len(read('mutacoes03-resultado.json'))==5 and all(r['detectada'] for r in read('mutacoes03-resultado.json'))
    outputs={str((ROOT/p).resolve()):sha(ROOT/p) for p in analysis['saidas']}
    outputs[str(xlsx.resolve())]=sha(xlsx)
    receipts={p.name:sha(p) for p in sorted(OUT.glob('*-recibo.json'))}
    manifest=dict(status='DONE_WITH_CONCERNS',timestamp=datetime.now(timezone.utc).isoformat(),
        base_commit=snap['head'],checkpoint_T11=str(checkpoint.resolve()),checkpoint_sha256=sha(checkpoint),
        codigo_sha256={p:sha(ROOT/p) for p in CODE},saidas_sha256=outputs,recibos_sha256=receipts,
        suite='360 passed; suite05',mutacoes_detectadas=5,auditoria=audit,
        limites=['Sem teste em Microsoft Excel nativo. Renderer Windows indisponível; leitura alternativa da cópia artificial separada.',
            'Armazenamento local ignorado; ACL por cargos escolares não certificada, contas/perfis pendentes.',
            'Identidade local provisória; revisão docente, eficácia e validação temporal/externa pendentes.',
            'Excel desta versão exige oportunidades comuns autenticadas; instrumentos heterogêneos são recusados.'])
    target=OUT/'entrega-final.json'
    if target.exists():raise ValueError('Preservar manifesto final anterior')
    target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    paths='\n'.join(f'- `{p}`\n  SHA256 `{h}`' for p,h in outputs.items())
    hashes='\n'.join(f'| {p} | {h} |' for p,h in manifest['codigo_sha256'].items())
    report=f'''# T10 — relatório de implementação e entrega

Status: **DONE_WITH_CONCERNS**. Data de fechamento: {manifest['timestamp']}.
Base: `{snap['head']}`; branch `airam/spec001`. Commit local final registrado ao término deste arquivo.
Não houve push, publicação ou mudança de remoto. Origin autorizado: MarceloClaro/AiramVeras.

## Entrega física e interfaces

Relatório HTML offline minucioso, JSON agregado integral, três figuras científicas autônomas em PNG/SVG e um XLSX real canônico local restrito. São 640 aplicações, 6.074 medidas originais sem fanout curricular, 133 perfis públicos, 428 associações completas, 24 escopos de Meta A e 20 contextos públicos de cobertura, incluindo indisponibilidade da fonte de E/F do primeiro ano. Não somar aplicações de componentes como estudantes distintos nem perfis sobrepostos.

`preparar_intervencao(observacoes, metas, vinculos, grupos)` retorna exclusivamente dados pessoais locais: identidade contextual, resultado original, Meta B individual, até três H com erros observados, associações documentais completas, apoio e revisão pendente. Sem média escolar imputada a aluno. `gerar_relatorio(resultados, out_dir)` aceita raiz pública fechada e bloqueia campos nominais mesmo aninhados antes de gravar. O coletor autentica dez checkpoints mais a contraprova FIX1 T08 contra o blob aprovado, liga fontes localmente e escaneia nomes/IDs nas saídas.

O builder único JS `reports/build_workbook.mjs` utiliza somente @oai/artifact-tool 2.8.99 / runtime oficial26.1020.11127. Autoria por openpyxl/xlsxwriter/pandas.ExcelWriter não foi usada. Abas: Metas; Intervenção nominal; Habilidades; Grupos; Cálculos; Fontes e Auditoria. Fonte e auditoria possuem regiões distintas; auditoria é terminal.

## Caminhos absolutos e hashes das entregas

{paths}

Checkpoint nominal T11 (ignorado/restrito): `{checkpoint.resolve()}`.
SHA256 `{sha(checkpoint)}`.
Manifesto público minimizado: `{target.resolve()}` (hash registrado no recibo de fechamento).
Os derivados de analise01/02 foram preservados por cópias verificadas antes de atualizações de apresentação/metadados. Fontes originais não foram sobrescritas.

## Contrato exato para T11

Leia `docs/dicionario-t10.md`, cujo hash final consta abaixo. A CLI pode montar as entradas como `evidencias/T10/analisar.py`: autenticar checkpoints e contraprova FIX1 contra baseline aprovada, carregar mapa nominal apenas localmente, ligar medidas por aplicação e contexto completo e chamar as duas interfaces. Não promover catálogo recém-gerado a baseline. O contrato público `airam-relatorio-t10-v1` contém fontes, componentes, metas_A, habilidades, associacoes, grupos sem membros, cenarios, sensibilidade, diagnosticos, limites e resumo. O contrato local `airam-workbook-t10-v1` contém metas, intervencao, habilidades, grupos públicos, curriculo integral, fontes, componentes, limites e complexos. As descrições completas e schemas/campos estão no dicionário.

Execução sem shell implícito: lista de argumentos `[NODE_OFICIAL, "reports/build_workbook.mjs", "--build", "restrito/t10/checkpoint.json", DESTINO_RESTRITO]`, cwd=`{ROOT}`. Node oficial: `C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`. A execução real04 acrescentou `--max-old-space-size=8192` e usou `restrito/outputs/01a16157-2a68-7253-9591-de126647cf53/versoes/autoria04`; após reabertura, somente o XLSX derivado foi movido ao caminho canônico com hash idêntico, sem segunda cópia real. A prévia já liberada ao controlador permaneceu estável.

`--verify-fixture` exige `sintetico=true`. `--prepare-artificial` prepara apenas cópia artificial. `--render-artificial` é operação explícita para um estado/engine em que a falha de render tenha sido resolvida; não foi repetida automaticamente. A junction oficial de módulos permanece ignorada/intacta. Não copiar, percorrer ou apagar suas dependências. O marcador já foi executado exatamente uma vez antes da primeira autoria em23/10 às20:36:46UTC, exit0 (marcador01); reruns desta operação não o repetem.

Entradas/saídas nominais só em arquivos locais restritos e ignorados. Sem nomes/IDs em stdout, HTML, figuras públicas, logs ou Git. Não enviar nominais para Core, Drive, serviços ou modelos. Falhas de integridade, cálculo, exportação ou contrato retornam não zero. O sucesso computacional é separado do estado visual `preparada_sem_render_local`; uma CLI deve mostrar a pendência ou ligar o recibo da inspeção alternativa, sem alegar imagem/Excel nativo. Falta temporal é ramo esperado, sem treino/previsão validada.

Metas B5/B6 controlam A/B; B7 necessidade/proximidade, B8 invalidez explícita. Meta A é CAEd original sem corte oficial em acertos. Meta B é teto(meta×oportunidades), 18/22 no universo atual, apenas L/M. E/F preservam unidades/máscaras. Zero numérico é válido, vazio não é meta zero. Escola usa seu próprio denominador, não soma tetos de turmas.

L/M de Cálculos calculam alvo/lacuna; N/O critérios; AI:AK precedentes; P posição por COUNTIFS sobre todo intervalo limitado. O caminho otimizado valida D comum (343 provas L/M disponíveis, D22); isso não é equivalência para novos instrumentos heterogêneos. A fixture D22/D30 exige recusa explícita antes de Workbook.create. Python conserva a fórmula individual geral. INDEX/MATCH gera a fila; o desempate K é ligado à chave, sem ROW/contagem cumulativa. Notas/revisão/apoio/data em Q:T permanecem com a chave, não com posição. Complexos são pré-calculados com versão/hash; sua atualização exige pipeline. Novas aplicações ampliam intervalos por regeneração; a CLI deve reaplicar notas por chave, sem promessa de migração automática nesta entrega inicial.

## Execuções, testes e contraprovas

Cada execução preservou comando, timestamp, versões, hashes de código/testes/config/coletor/entradas antes, log/exit reais. Não se atribuíram hashes posteriores a estados anteriores. Recibos completos em `{OUT}`; o manifesto inclui seus hashes.

- RED01:21 falhas funcionais controladas antes do produto; RED02: builder T24 ausente. GREEN01:22passaram.
- RED03/04/05: perfis suprimidos/notes, versões curriculares/fontes e detector; GREEN02/03/05:23/24/24passaram. GREEN04 e diagnóstico01/02: falha nativa0xC0000005 em autofitRows, não RED funcional. Alturas explícitas substituíram apenas layout, sem reduzir fonte.
- RED06: denominadores heterogêneos não recusados antes da autoria; GREEN09:25passaram. GREEN06/07/08 preservam refatores anteriores.
- RED07 ocorreu antes da transformação integral de prévia, asserção controlada de transformação/amostra ausente. Não demonstrou sobrevivência de escore em PNG antigo; a falha de minimização foi identificada por leitura do código antes de renderizar/abrir. GREEN10/11:26passaram.
- RED08 demonstrou arquivo exportado ausente após crash de imagem. GREEN12:27passaram com isolamento; GREEN13:27passaram após não repetir renderer indisponível e preparar cópia artificial separada. A exportação/reabertura real precede preparação visual.
- Suíte01:343passaram/13falharam por PDF primário ausente (ambiente, não RED). O controlador restaurou por cópia verificada; causa/autoria da ausência desconhecidas. SHA origem/antes/depois/destino2728d640c98510ff323cb542282ffc51db8288c021560aa55cac7b908c5f5f0e. Nenhuma atribuição ao usuário/equipe. Suíte02:356passaram; suíte03:358passaram; suíte04:359passaram; suíte05 final do código atual: **360 passed em108,50s**, exit0. O PDF restaurado integra seu snapshot. Conferência complementar do controlador autenticou76fontes primárias históricas sem divergência, sem substituir análise/teste.
- Mutacoes01/02 preservadas; **mutacoes03:cinco mutantes detectados**, sem alterar originais: necessidade invertida, vazamento agregado, obrigação80% por H, remoção do desempate por chave e retorno de observações originais à prévia.
- Ensaios artificiais40/80: exportação/reabertura12s/25s, todos controles/notas/ordem conferidos, sem dados reais. Não provam complexidade interna.
- Workbook01/02/03 interrompidos e preservados sem XLSX exportado: custo/lentidão e correção de minimização, não RED. O diagnóstico estático do controlador propôs leituras seletivas, snapshots apenas no mesmo estado, permutação somente de todos os inputs e layout sem getter da fila. Fórmulas/contraprova reais foram conservadas. Workbook04 possui exit0, exportação/reabertura, controles A/B/ordem/inversão, notas por chave, detector de erro injetado/limpo e scan de todas as abas. Snapshot e log identificam o código realmente executado.
- Contraprova independente: **{audit['verificacoes']} verificações**, stdlib/Fraction/SQL/OOXML, sem importar produto/builder:640 aplicações,6.074 medidas originais,157 relações documentais, metas por denominador, fila/notas/ausências/unidades e arquivos públicos sem identificadores. Hash do XLSX confere com autor e movimento canônico. Não é teste em Microsoft Excel.

O checkpoint guarda hashes dos produtores na montagem analise03; o XLSX registra adicionalmente hashes exatos `autoria/builder_js_sha256` e `autoria/entrada_checkpoint_sha256` da execução real04. Essa distinção preserva a proveniência das melhorias posteriores de autoria, sem atribuir código novo a montagem anterior.

## Inspeção visual e minimização

HTML agregado inspecionado pelo executor em navegador local antes do bloqueio complementar: servidor html-servidor01 iniciado23/10 às20:52:46UTC, HTTP200 para página/figuras às20:53:14UTC, inspeção da abertura e perfis por volta20:57–20:58UTC; legibilidade, navegação e M1 observados, sem corte visível nas regiões inspecionadas. Aba fechada e somente o servidor próprio encerrado às21:08:09UTC. Exit4294967295 é limpeza deliberada, não falha de HTML. Não se alegou inspeção de cada uma das centenas de linhas. O controlador inspecionou as três PNG agregadas; sem corte/sobreposição/rótulos ilegíveis observados. Os hashes PNG finais são os mesmos inspecionados. A tentativa complementar do controlador de iniciar outro servidor foi bloqueada antes de executar, sem contorno/serviço; registro html-qa-bloqueio.md. Nenhum novo servidor foi necessário.

O mapa H explica visivelmente que cada linha corresponde a instrumento distinto, H01 entre instrumentos não é a mesma variável e células brancas estão fora do instrumento. M1 permanece em diagnósticos, contrastes/perfis finais: geometrias iguais L1/L2/L3/L5/M2 com seleções diferentes L1/L2, causa específica não isolada; sem benefício curricular demonstrado.

Prévia: oito aplicações/16medidas inteiramente artificiais por regra explícita, sem escores/H/pertenças/notas/identidades/fontes individuais reais; somente comprimentos/quebras são aproveitados para X, e agregados/fontes públicos podem permanecer reais. `previa-conferencia02` verificou todo JSON/OOXML contra nomes/IDs/chaves reais e a regra geradora. O primeiro scan foi interrompido por recomputar casefold do XML a cada termo; corrigido sem remover termos, tentativa preservada. O XLSX artificial foi liberado ao controlador com SHA1f157ffd7fd3b2b2367ca53aa5f2b5c4dcb1090dbfb745f0adb4e9d7a0b6c70c e mantido estável durante leitura.

Render Windows: falha nativa0xC0000005 em uma célula artificial PNG e JPEG, registrada sem atribuir culpa ao documento. Uma consulta pública limitada workbook.render confirmou formatos; nenhuma inspeção interna de pacote. A autoria real04 não repete essa chamada. Leitura alternativa pelo controlador no WSL/LibreOffice e inspeção das seis abas têm recibo complementar registrado abaixo; não equivalem a Microsoft Excel nativo. Calc inicialmente ausente foi falha de dependência, não de documento.

## Permissões, autorrevisão e limites

ACL04 observa na pasta final herança protegida={str(acl['heranca_protegida']).lower()}, quatro regras herdadas: FullControl usuário atual/SYSTEM/Administradores, ReadAndExecute+Synchronize outra identidade. Nenhuma ACL alterada; não certifica acesso por cargos escolares. ACL01 era comando defeituoso; ACL02 retornou nulos e não é validação; ACL03 explicitou módulo PS5 indisponível; ACL04 usou pwsh oficial e exigiu estrutura válida. Novas contas/perfis escolares de leitura/edição aguardam informação do usuário.

Autorrevisão: dados públicos/nominais separados; originais preservados; máscaras/zeros/unidades originais; escola/turma não somadas; vínculos contextuais com fonte/versão/ocorrência; sem fanout individual; metas independentes e sem corte oficial inventado; cobertura/maiores lacunas mantidas; H80% não requisito do total80%; fila recalculada em todo intervalo com empate estável; notas por chave; análises complexas rotuladas; limites de temporalidade, M1, domínio BNCC, eficácia, revisão humana e identidade provisória explícitos. Receitas/scripts de auditoria não substituem produto como oráculo. Não foram criados subagentes/revisores pelo executor; diagnóstico estático read-only do controlador foi distinto da revisão independente que vem após este handoff.

Preservados e não incorporados: agents/, hooks/, .gdoc externos em docs/evidencias, SPEC002.docx e os três bootstrap untracked. Não alterados fontes primárias, clone BNCC ou junction ignorada. Staging somente desta T10. Nenhum dado nominal ou arquivoXLSX/PDF/PNG foi incluído no commit.

Concerns: renderer Windows indisponível; fidelidade do leitor alternativo não é Excel; contas/ACL por cargos pendentes; identidade local, atividades e revisão docente/eficácia não validadas externamente; instrumentos futuros heterogêneos exigem novo contrato/pipeline. Não há treino temporal, previsão validada, capacidade fixa ou domínio BNCC inferidos.

## Hashes finais de código/contrato

| Arquivo | SHA256 |
|---|---|
{hashes}

## Complementos finais

Inspeção alternativa, staging e commit são registrados aqui após seus recibos, sem modificar os hashes históricos das execuções.
'''
    (ROOT/'.superpowers/sdd/implementation-plan/task-10-report.md').write_text(report,encoding='utf-8')
    print(json.dumps({'status':manifest['status'],'manifesto_sha256':sha(target),'checkpoint_sha256':sha(checkpoint),
        'xlsx_sha256':sha(xlsx),'relatorio':str(ROOT/'.superpowers/sdd/implementation-plan/task-10-report.md')}))
if __name__=='__main__':main()
