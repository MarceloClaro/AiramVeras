# Operação local Airam Veras — T11

Estado: implementação independente de T01–T09 executada. Integração final de
`relatar` e `executar`, preservação de notas entre novas autorias e liberação do
pacote aguardam o handoff T10 aprovado. Esses comandos retornam não zero nesse
estado. A presença dos comandos não significa rotina final entregue.

## Uso

Na raiz do projeto, utilizar o Python do ambiente autorizado. No checkout T11,
o caminho é `../datamining/.venv/Scripts/python.exe`. No primário, `.venv/Scripts/python.exe`.

```text
python -m airam catalogar --config config/analise.json
python -m airam validar --config config/analise.json
python -m airam analisar --config config/analise.json
python -m airam gate --nome preflight --config config/analise.json
python -m airam gate --nome release --config config/analise.json --artefatos <manifesto-local.json>
```

`catalogar` autentica primeiro a baseline e publica os metadados em `catalogo/`.
`validar` confere hashes, compromisso Git/arquivo canônico BNCC, esquemas e
reingestão integral contra o checkpoint T02 autenticado.
`analisar` disponibiliza resultados T01–T09 já revisados, após autenticar todas
as dependências, e persiste a versão final em SQLite e CSV. O recibo registra
`modo=reutilizacao_autenticada` e `nova_inferencia=false`. Não é um ajuste novo de
correlações ou grupos. Mudança de entradas, módulos analíticos, parâmetros,
versões ou artefatos bloqueia a reutilização e exige uma nova execução analítica
com contraprova. Não altera automaticamente a baseline nem chama coletores
históricos com efeitos no nível superior.

Os caminhos `raiz_fontes` e saídas são relativos à raiz do projeto. O atributo
opcional `projeto` permite raiz explícita para fixtures isoladas. As fontes do
projeto real permanecem no diretório pai. São excluídos explicitamente da coleta
`00_ORGANIZACAO`, `.airam-cenarios-t09`, `.airam-cli-t11` e `COMECE_AQUI.lnk`.
O atalho é excluído por caminho exato; outros arquivos `.lnk` não somem por extensão.

## Integridade e cache

`config/fontes-baseline.json` contém 76 fontes: 18 ZIPs, 54 CSVs canônicos,
manifesto, mapa de posições, PDF CNCA e arquivo canônico BNCC. Os valores foram
importados do recibo histórico T01 autenticado contra o Git BASE
`28d88e356f3ce744f250331aa2f90a8de5bdc6be`, antes de qualquer catálogo novo.
A configuração fixa o hash dessa baseline.

`config/cache-analise-aprovada.json` fixa 15 checkpoints do handoff revisado,
produtores analíticos, quatro configurações, parâmetros de metas/ausência/identidade
e runtime. A compatibilidade de Python e bibliotecas foi conferida com snapshots
anteriores T06/T08/T09. A importação do contrato é documental/operacional, não
uma inferência nova nem um GREEN TDD. Os metadados de catálogo/CLI não alteram os
produtores estatísticos herdados; a ingestão atual é confrontada com T02.

Não executar `preparar_contratos.py` para “corrigir” uma divergência. Ele documenta
a importação única da base aprovada. Nova versão requer revisão do contrato,
produtor, contraprova e atualização explícita dos pins.

## Banco e arquivos

`restrito/banco/<hash-do-conteudo>/analise.sqlite3` contém 20 tabelas de dados
e a tabela `proveniencia`. Cada tabela possui ordem, contexto disponível e
`registro_json`, preservando integralmente máscaras, unidades, zero, ausência,
origens e objetos aninhados. `PRAGMA user_version=1`. Não há soma de componentes,
H/totais ou escola/turma para fabricar uma taxa global.

Há um CSV por tabela e `manifesto.json` com hashes. Objetos aninhados usam JSON
em células CSV; grandes estruturas de grafo/grupos são destinadas à leitura
programática, não a abrir diretamente em células Excel. A contraprova ajusta
explicitamente o limite de leitura CSV para 128 MiB por campo. `None` é célula
vazia, zero continua `0`. O banco guarda os tipos originais no JSON.

Nomes/nomes_normalizados e o mapa nominal não entram nas tabelas analíticas.
O campo documental `nome` de perfis T08 é renomeado para `titulo_perfil` apenas
nas posições conhecidas do schema. O mapa nominal continua em
`restrito/t03/mapa-nominal.json`. A chave HMAC permanece em seu local original,
fora do checkout, e não é lida ou copiada por esse caminho de reutilização.
Pseudônimos e resultados individuais continuam dados pessoais. `restrito/`
ignorado pelo Git não certifica ACL por papel nem criptografia.

Saídas compartilháveis de T05 ficam em `relatorios/agregados/<hash-T05>/`:
JSON completo, `agregados.csv` e `metas_A.csv`, mantendo nível/ano/componente/turma.
A Meta A escolar usa seu denominador e seu próprio teto; o pipeline não soma
tetos de turmas. Relatório HTML/Excel final depende da integração T10.

Versões de banco são imutáveis e endereçadas por conteúdo. Reutilização verifica
os hashes de todos os arquivos existentes. Catálogo/JSON divergente preserva
os bytes anteriores em `versoes/<hash>/` antes da troca.

## Hooks, gates e recibos

Os wrappers PowerShell `preflight.ps1` e `release.ps1` executam a CLI e retornam
seu código real. `preflight` é chamado pelo próprio processo antes da operação;
falha impede efeitos posteriores. `release` tem integração real por processo
testada com fixtures, mas a chamada na entrega completa depende de T10.

Gate temporal distingue disponibilidade transversal/cenários de previsão validada.
`temporal` pode sair com zero mantendo `previsao_temporal_validada=false`.
`previsao` permanece bloqueado: este projeto não dispõe de modelo temporal validado.

Gate de release exige artefatos autenticados, rastreabilidade R01–R24, limites e
recibos concluídos de testes/contraprova/inspeção. Autentica snapshot/log dos testes
e confere os hashes de código contra o estado atual: testes obsoletos não liberam
produto modificado. Inspeção pendente com exit zero continua bloqueada. Saídas
JSON/CSV são verificadas recursivamente contra campos individuais; manifesto
de entrega real deve fornecer o mapa nominal autenticado para varredura local
adicional de nomes/IDs em arquivos textuais públicos. Não confundir hash com
validação pedagógica externa.

Recibos operacionais em `evidencias/operacionais/<id>/` registram snapshot prévio,
runtime, configuração, hooks e exit code. Seu tipo é `operacional`; nunca usam
RED/GREEN/REFACTOR para rotular análise de dados. Os recibos TDD continuam separados
em `evidencias/T11/`. A ressalva histórica T02 (primeiro RED sem hashes/versões
contemporâneos) permanece explícita e não pode ser reparada retroativamente.

## Core e runtime de planilhas

`agents/contratos.json` conserva primário MarceloClaro, papéis, perfis e referências
a recibos minimizados. O consumidor autentica esses recibos e distingue cadastro,
validação, ativação A2A, execução, teste e entrega. As sondas
`TSPEC-4272ac13` e `TSPEC-a6e24d1b` ficaram bloqueadas, com zero passos. Nenhuma
política global foi alterada e nenhuma sonda bloqueada idêntica foi repetida.
Eventos globais seguem `contract_only`, sem disparo real comprovado.

`config/runtime.json` aponta o Node e os pacotes oficiais identificados por
`load_workspace_dependencies`. `verificar_runtime` importa somente a entrada
pública de `@oai/artifact-tool` e verifica Workbook/SpreadsheetFile/FileBlob, sem
criar workbook. A variável `AIRAM_ARTIFACT_RUNTIME` pode receber diretamente o
diretório oficial `dependencies/node`, que contém `node_modules`; essa resolução
não depende da pasta temporária SDD, não copia/instala dependências nem altera
as junctions existentes. Compatibilidade com a chamada final do builder será
confirmada após o handoff T10. O marcador da operação não foi repetido.

## Limites atuais

- Não houve revisão independente T11 nem liberação do pacote completo.
- `relatar`/`executar`, migração de notas por chave, cache final de autoria e
  release com a inspeção T10 aprovada ainda aguardam handoff.
- Fontes/configurações novas não são promovidas a válidas pela simples regeneração
  do catálogo ou cache; exigem nova execução e revisão apropriadas.
- Validação computacional/documental local não demonstra eficácia pedagógica,
  causalidade, identidade longitudinal ou previsão temporal validada.
