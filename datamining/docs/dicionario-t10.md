# T10 → T11: relatório agregado e intervenção local restrita

As interfaces de produto são `preparar_intervencao(observacoes, metas, vinculos, grupos)` e `gerar_relatorio(resultados, out_dir)`, em `airam/relatorio.py`. Autoria XLSX exclusivamente pelo único builder `reports/build_workbook.mjs`, usando o pacote público `@oai/artifact-tool` 2.8.99 do runtime oficial 26.1020.11127. Nenhuma execução no Excel nativo é alegada.

## Preparação de intervenções

`observacoes` contém uma aplicação por linha, com todos os oito campos contextuais T05 (`avaliacao_id`, `ano_avaliacao`, `ciclo`, `ano_escolar`, `componente`, `fonte_id`, `sha256`, `exportacao`), `aluno_local_id`, `avaliacao_local_id`, turma, participação, categoria CAEd, acertos/oportunidades e os atributos originais. A identidade permanece local provisória. O coletor acrescenta `nome` exclusivamente a partir do mapa nominal autenticado T03. Nunca imprimir ou devolver essas linhas a modelos/ferramentas externas.

Cada aplicação recebe `habilidades` com suas próprias linhas T03 de H ou `medidas` com suas próprias medidas de escrita/fluência. Para H, acertos/oportunidades podem estar em `numerador`/`denominador` ou `acertos`/`oportunidades`. Disponibilidade é explícita. A lista contém também as medidas ausentes, sem imputação. Os vínculos são as 157 arestas T04, contextualizadas por edição/ciclo/ano/instrumento/componente/posição, conservando fonte, versão e ocorrência. Versões concorrentes do mapa na mesma posição são recusadas. Vínculos múltiplos não multiplicam observações.

`metas={"A":0.8,"B":0.8,"ordenacao":"necessidade"}`. A ordenação opcional `proximidade` conserva todas as linhas. A preparação valida os dois controles e devolve uma linha por aplicação, com chave SHA256 do JSON compacto UTF-8 da sequência dos oito campos contextuais mais aluno/aplicação, metadados originais, Meta B, até três H com algum erro observado, vínculos completos e proposta de atividade. Não se exigem 80% em cada H. Nenhuma média de grupo/escola entra em uma linha individual.

A ordem principal usa classes: 0 ausência de evidência, 1 lacuna individual B, 2 unidades próprias E/F, 3 Meta B atingida. Dentro da classe 1, a maior lacuna vem primeiro. O cenário de proximidade inverte somente esse critério. Empates usam identificação contextual estável, sem linha física. O Excel usa a ordem lexicográfica da chave SHA256 como desempate estável, explicitamente identificada. A diferença entre os desempates das duas interfaces não muda lacunas nem elegibilidade ao apoio. Grupos estatísticos não restringem atendimento.

Meta A é a proporção original de adequados por avaliados. Não existe distância individual oficial em acertos para mudar a categoria. Meta B é `teto(meta × oportunidades) − acertos`, limitada inferiormente a zero, apenas em provas de itens válidas. Em 22 itens e 80%, o alvo é 18. Escrita/fluência conservam notas, tarefas, contagens/percentuais publicados e categorias originais. Não há WPM nem acertos artificiais.

## Contrato público para gerar o relatório

`resultados.versao_schema="airam-relatorio-t10-v1"`. A raiz é fechada e exige exatamente:

- `fontes`: referência → hash SHA256 dos checkpoints/versões e produtores efetivamente utilizados;
- `componentes`: ano/componente, cadastros, participantes, com resultado, unidades e disponibilidade da fonte; arquivo ausente não define universo avaliado;
- `metas_A`: 24 escopos T05, com ano/componente/nível/turma, avaliados, adequados, alvo, conversões e meta. Escola/turma são visões sobrepostas;
- `habilidades`: os agregados T05, conservando nível/turma/posição, C/D, máscaras, proveniência e vínculos T04 contextualizados em `curriculo`;
- `associacoes`: os 428 registros completos T06, incluindo ausências/motivos, N, efeitos, intervalos/sensibilidade, p/q e família. Não filtrar por significância;
- `grupos`: 133 perfis públicos T08, incluindo as supressões `suprimido_n_menor_5`. Renomear o nome do grupo para `titulo_perfil`; não transportar membros;
- `cenarios` e `sensibilidade`: os 96+96 registros públicos T09;
- `diagnosticos`: dez diagnósticos de geometria/seleção da contraprova T08 FIX1 autenticada;
- `limites`: texto explícito das limitações e pendências;
- `resumo`: reconciliação portal, método de grafo, gate temporal, configurações/proveniência e contrastes T08 agregados.

`gerar_relatorio` recusa campos nominais/individuais mesmo aninhados antes de criar qualquer arquivo. Perfis não suprimidos sem fonte/descrição curricular também bloqueiam a entrega. O coletor real verifica ainda todos os termos nominais/identificadores contra as saídas textuais, sem expor o termo que falhar.

O retorno contém caminhos de `relatorio.html`, `tabelas.json` agregado e três figuras em PNG/SVG: `meta-a`, `cobertura`, `habilidades`. As figuras são arquivos autônomos, não screenshots do Excel. O HTML funciona offline, com tabelas completas e detalhes expansíveis. Nomes/IDs/objetos individuais não são embutidos.

## Contrato JSON local do builder

`restrito/t10/checkpoint.json` tem `versao_schema="airam-workbook-t10-v1"` e as chaves `sintetico`, `metas`, `intervencao`, `habilidades`, `grupos`, `curriculo`, `fontes`, `componentes`, `limites`, `complexos`. É dado pessoal restrito, ignorado pelo Git.

- `intervencao`: as 640 linhas retornadas pela preparação, com nome e chave local. `instrumento` é SHA256 dos oito campos contextuais. A linha conserva medidas e dados originais; chaves duplicadas bloqueiam autoria.
- `habilidades`: as 6.074 medidas originais, uma vez cada, ligadas à `chave` da aplicação e à turma. Campos: posição/campo, valor/numerador, denominador, unidade, disponibilidade, códigos documentais, fonte e linha. Não expandir medidas por arestas BNCC.
- `grupos`: perfis públicos, sem membros; `recorte` distingue regras, observado e cada cenário/braço. As descrições extensas permanecem integrais no HTML/JSON agregado; o Excel resume distribuições/estabilidade e aponta para essa descrição.
- `curriculo`: arestas T04 integrais, com descritores, BNCC, textos, localizadores, página, fonte, versão, ocorrência, peso e ressalvas;
- `componentes`: escopos de instrumento por escola/turma, com `instrumento`, ano, componente, nível e turma. Nunca somar turmas para gerar o teto escolar;
- `complexos`: versão/configuração T08 e aviso de reexecução do pipeline. Metas editáveis não refazem grupos, propagação ou correlações.

Comando de autoria, a partir da raiz do projeto:

```text
<NODE_OFICIAL> reports/build_workbook.mjs --build restrito/t10/checkpoint.json restrito/outputs/01a16157-2a68-7253-9591-de126647cf53
```

`NODE_OFICIAL=C:/Users/marce/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe`. A resolução usa a entrada pública do pacote através da junction oficial já existente em `.superpowers/sdd/implementation-plan/runtime-probe/node_modules`. `AIRAM_ARTIFACT_RUNTIME` permite indicar outro scratch com a mesma junction oficial; não copiar/percorrer/apagar a junction existente nem alterar dependências. O builder não executa o marcador: a coordenação registrou o marcador exatamente uma vez antes da primeira autoria desta operação. Reruns T10 não devem duplicá-lo.

O comando produz um único XLSX canônico real `intervencao-restrita.xlsx`, uma cópia inteiramente artificial para inspeção e recibo público minimizado. O modo `--verify-fixture` aceita somente `sintetico=true` e é usado nos testes artificiais, sem entregar uma variante real adicional. `--prepare-artificial <checkpoint> <destino>` prepara somente a cópia artificial no mesmo builder, sem exportar uma planilha real. A cópia e seu JSON ficam em `previas-sinteticas/inspecao-artificial.xlsx` e `entrada-artificial.json`. A cópia artificial serve exclusivamente para layout; não substitui a contraprova de valores do canônico.

A exportação/reabertura e a conferência real terminam antes da preparação visual, preservando o canônico se a etapa de prévia falhar. `wb.render` encerrou o Node Windows com 0xC0000005 até para uma célula artificial, nos formatos PNG e JPEG publicamente documentados (render-minimo01/02). Após esses diagnósticos não é repetido automaticamente: o recibo informa `preparada_sem_render_local`, `tentativa_automatica=false` e nenhuma imagem alegada. `--render-artificial <entrada-artificial.json> <destino>` é operação explícita apenas para um ambiente/estado em que a falha tenha sido resolvida. O controlador dispõe de LibreOffice/Poppler já instalados no WSL para leitura/renderização da cópia artificial; essa inspeção é registrada separadamente e não demonstra comportamento de Microsoft Excel nativo. Nenhuma autoria de XLSX é feita pelo leitor alternativo. Uma CLI deve distinguir sucesso computacional de inspeção visual pendente e apresentar ambos os estados.

## Controles e dependências do Excel

As seis abas são Metas; Intervenção nominal; Habilidades; Grupos; Cálculos; Fontes e Auditoria. Fontes e auditoria têm regiões separadas. A auditoria é terminal e não alimenta cálculos/saídas.

Metas B5/B6 são A/B. B7 seleciona 1 necessidade ou 2 proximidade. B8 expõe controles inválidos; vazio não vira meta zero. Zero numérico é permitido. `Cálculos` tem base com cabeçalho na linha 7 e dados a partir da linha 8. L/M calculam alvo/lacuna B; N/O são critérios e P é posição única por COUNTIFS em intervalos completos, com K ligado à chave estável. A fila recupera as linhas por INDEX/MATCH, resolvendo o MATCH uma vez por linha na coluna Z e compartilhando-o entre os INDEX. Não há ROW, contagem cumulativa, LET/LAMBDA, SORT/FILTER ou spill.

Campos editáveis Q:T de Cálculos são notas, revisão docente, apoio acordado e data de reavaliação. A fila consulta esses campos pela chave; escrever sobre a fila apaga fórmulas e não é o fluxo de uso. A próxima ação continua pendente se o professor marcou revisão mas não definiu apoio/data. Valores originais, hipóteses e observações docentes ficam separados. Reavaliação não tem prazo inventado.

Alterar B5/B6/B7 atualiza distâncias e a fila. Adicionar aplicações ou trocar fontes requer regeneração pelo pipeline, pois os intervalos são limitados ao contrato autenticado. O pipeline deve preservar e reaplicar notas por chave antes de regenerar, se houver notas preenchidas. A T10 inicial entrega os campos vazios/pendentes; não afirma migração automática entre arquivos gerados em datas diferentes.

## Execução pela CLI T11

A integração reproduzida é `evidencias/T10/analisar.py`: autentica os dez checkpoints com hashes aprovados, autentica a contraprova FIX1 contra o blob Git aprovado e seus hashes T08, liga mapa/medidas localmente, chama as duas interfaces e grava o JSON restrito. O wrapper `evidencias/T10/executar.py` captura código/testes/configuração/coletor, versões e todas as entradas antes da execução. Uma CLI pode seguir a mesma montagem ou executar esse coletor sem shell implícito, verificando seu código de saída, e depois chamar o builder com uma lista de argumentos e destino explícito restrito. Não promover um catálogo recém-gerado a baseline de integridade.

Reexecuções divergentes exigem preservar as versões anteriores. A execução inicial foi preservada antes do ajuste de apresentação. O coletor recusa substituir um JSON divergente sem uma cópia anterior coincidente. A CLI deve manter a mesma proteção ao atualizar artefatos e nunca sobrescrever fontes originais.

O processo usa somente fontes locais e metadados aprovados. Não exige login, Core, Drive ou envio nominal externo. A ausência de prontidão temporal permanece ramo esperado: relatório transversal/cenários disponíveis, sem treino ou previsão temporal validada. Falha de integridade, cálculo, exportação ou teste retorna código não zero.

### Pré-condição do caminho de contagem

O builder T10 valida explicitamente que todas as aplicações L/M disponíveis têm o mesmo total de oportunidades. No universo autenticado são 343 aplicações válidas com D=22; não participantes continuam ausentes e não entram nessa verificação. O alvo comum é mostrado em Metas D5/D6. Isso permite contar precedentes por classes, necessidade e chave diretamente sobre as colunas originais J/AD/H/K, evitando a avaliação recursiva de intervalos calculados no runtime. As lacunas continuam calculadas por estudante em L/M e são confrontadas independentemente. A prioridade por menor acerto equivale à maior lacuna somente sob essa pré-condição; a fila de proximidade conserva o filtro abaixo do alvo.

Os passos AI/ AJ/ AK de Cálculos mostram precedentes por classe, necessidade e desempate; P soma os passos e a fila consulta essa posição. Ausência é classe separada, unidades próprias permanecem sem Meta B, e o desempate percorre o intervalo completo. Uma fixture adversarial com D=22 e D=30, ambos com 17 acertos, exige recusa antes de criar workbook. Instrumentos futuros com D heterogêneo exigem novo contrato/reexecução, sem aplicar silenciosamente a equivalência. A API Python de Meta B e de preparação conserva a conta individual geral; essa restrição pertence ao caminho de autoria Excel desta versão.

## Validação e fronteira

Recibos T10 distinguem RED funcional, tentativas de GREEN, falha nativa de layout, alternativa verificada, análise real e contraprova. `autofitRows` encerrou o Node com 0xC0000005 neste Windows; os diagnósticos preservados isolaram a operação. O builder usa alturas explícitas, quebra de texto e fonte Arial 10, sem reduzir fonte para encaixar conteúdo.

As verificações alteram/restauram A/B/ordem, revertem toda a base física, confrontam a fila com ordenação independente, verificam notas por chave e as etapas de revisão/apoio/data, injetam/limpam um erro para comprovar o detector, recalculam, exportam e reabrem. A API recalcula dependências automaticamente após escritas; os ensaios leem esses novos resultados e reservam recálculos integrais explícitos para a conferência inicial/final, exportação e reabertura. A inversão escreve somente todos os blocos de entrada A:K/Q:AE/AG, preservando fórmulas; snapshots de chaves são reutilizados apenas no mesmo estado. Notas e lacunas são lidas somente nas colunas necessárias. O ajuste de alturas usa matrizes de texto de entrada para layout, sem ler a fila calculada nem substituir sua contraprova. A fila recebe altura suficiente para qualquer reordenação do conteúdo entregue.

As seis abas são renderizadas em workbook separado, sem alterar a base canônica, com oito aplicações e 16 medidas completamente artificiais. Regra explícita: L/L/M/M/E/E/F/F; L/M com 0/3/6/9 acertos e 22 oportunidades; categorias alternadas, um caso sem resultado, H01 artificial 0/2, sem pertencimento individual. Identidades, notas, fonte/linha individual, tarefas e medidas são geradas artificialmente. Somente comprimentos máximos/quebras de textos individuais são aproveitados para preencher células com X e testar encaixe; nenhum escore/perfil/H/lista individual real é transportado. Agregados, fontes e textos normativos já públicos podem permanecer reais. A prévia declara seu caráter artificial; não é conferência visual de valores individuais da escola. A integridade da base real é comprovada antes da exportação e pela leitura independente do arquivo final. Dados reais individuais nunca vão à prévia devolvida ao modelo.

A rotina anterior às correções de minimização teria conservado observações ao trocar apenas identidades/notas; a autorrevisão detectou isso antes de renderizar ou abrir qualquer prévia real. A tentativa workbook03 foi interrompida e preservada. RED07 é a falha funcional de ausência da transformação/amostra completa; não demonstrou sobrevivência de escores em imagem antiga. GREEN10/11 exercitam a transformação atual com valores conhecidos e verificam H/listas/notas/fontes artificiais. Crash/lentidão não são chamados de RED funcional. O memo de diagnóstico é estático: a hipótese de avaliações repetidas não certifica internals do runtime.

Armazenamento ignorado não certifica restrição por cargos escolares. O recibo NTFS descreve as permissões observadas no destino; não modifica ACLs. Identidade, revisão docente, eficácia, datas de aplicação e validação externa permanecem nos limites dos artefatos. M1 é transportado aos diagnósticos, contrastes e perfis: geometrias iguais em L1/L2/L3/L5/M2 com seleções distintas em L1/L2 não demonstram benefício curricular.

### Refinamento após inspeção nativa

`--refine-layout <checkpoint.json> <original.xlsx> <out_dir>` importa pelo mesmo JS oficial, ajusta apresentação, exporta outro destino e reabre. Preserva o original e registra sua hash, a do novo arquivo e a do builder efetivamente usado em `layout-verificacao.json`/`layout-resultado.json`. A aplicação nominal ocorre após a autoria04 e sua contraprova; não repete os ensaios caros de controles quando a comparação independente confirma todas as fórmulas e valores originais. A comparação integral admite somente os resumos deliberados de Grupos!G, a legenda Metas!A9 (referência de 80%; alvo editado em D6) e a retirada do rótulo técnico Intervenção nominal!Z7. Nenhuma fórmula/contagem/unidade/máscara/nota é trocada pelo ajuste visual.

O resumo de grupos distingue somas de acertos/oportunidades e C/D ponderado das distribuições individuais; mostra N, unidades, ausências e supressões. A precisão completa continua no JSON/HTML. Nas unidades próprias mostra até três medidas com suas distribuições e remete às demais completas, sem recomputar estatísticas. A altura soma todas as quebras e linhas ocupadas dentro de cada célula e toma o máximo entre células, com margem, sem reduzir fonte. A largura zero da coluna técnica Z não gerou flag hidden no exportador; a borda permaneceu visível em LibreOffice. As consultas públicas Worksheet/Range não localizaram API de ocultação. A solução de apresentação usa formato Excel padrão `;;;` em Z8:Z647 e remove somente o rótulo Z7. Valores e fórmulas permanecem auditáveis; não é ocultação de segurança nem afirmação de hidden=true. Erros continuam sujeitos aos scans integrais de cálculo/OOXML, independentemente da apresentação.

A prévia revisada troca sequências X por frase completamente fictícia com espaços e mesmo comprimento/quebras desafiadores. Sua geração usa o builder em versão registrada no próprio JSON; o verificador reporta esse hash histórico, não um hash de código posterior. A inspeção alternativa prova apenas as regiões efetivamente vistas em LibreOffice/Arimo, e não ausência de corte em todas as linhas nominais nem execução em Microsoft Excel.
