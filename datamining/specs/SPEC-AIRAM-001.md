# SPEC-AIRAM-001: mineração pedagógica auditável CAEd/CNCA–BNCC

Versão: 0.1, 22/10/2026. Estado: **DESENHO APROVADO PELO USUÁRIO; implementação e testes de produto ainda não executados**.

Aprovação registrada nesta conversa: “Aprovo; prepare o plano de implementação”. A aprovação cobre o desenho; o plano terá revisão própria antes da implementação, conforme o fluxo solicitado.

Pasta de trabalho: `C:\Users\marce\Downloads\Airam veras`.

## 1. Objetivo e decisões do usuário

Organizar fontes, relatórios e agentes; construir um processo reproduzível com SDD, TDD e hooks; analisar alunos, grupos, turmas e escola; relacionar habilidades CAEd à BNCC; produzir correlações, contraprovas, agrupamentos pedagógicos e cenários de intervenção.

O usuário confirmou **duas metas independentes**:

- **Meta A:** ao menos 80% dos estudantes avaliados classificados no nível de aprendizagem adequado, conforme classificação original CAEd.
- **Meta B:** cada estudante atingir pelo menos 80% dos acertos, quando o instrumento oferece contagens de acertos e oportunidades.

Não substituir essas metas por uma terceira, como “80% dos alunos com 80% de acertos”. Meta B não será aplicada mecanicamente a notas de escrita, categorias de fluência ou escalas SPAECE.

Horizonte temporal ainda não confirmado. A entrega inicial usa o Ciclo I/2026 como diagnóstico e cenários condicionais para uma próxima avaliação comparável. Não equipara CNCA, Avalie.CE, SAAP e SPAECE. Previsão temporal calibrada permanece indisponível até cumprir os requisitos da seção 8.

## 2. Alternativas de desenho

1. **Diagnóstico e cenários aritméticos:** menor complexidade, atende às duas metas e à intervenção com evidência observada; agrupamentos apenas por regras explícitas.
2. **Diagnóstico, grafo curricular e clusters exploratórios auditados, recomendado:** acrescenta análise estrutural CAEd–BNCC e agrupamentos estáveis, preservando a distinção entre observação e propagação.
3. **Aprendizagem supervisionada temporal/GCN treinada:** etapa posterior, condicionada a identidade longitudinal validada, ciclos datados, desfechos e validação fora da amostra. A base atual não satisfaz esses requisitos.

A recomendação é a alternativa 2, com a alternativa 1 como referência de comparação. A complexidade adicional só permanece se produzir resultados interpretáveis e estáveis.

## 3. Evidência existente e universo da análise

### 3.1 Fontes principais

`resultados-caed-ciclo-i-2026/manifesto_coleta.json` documenta 20 combinações, das quais 18 têm ZIPs efetivamente exportados. São 54 CSVs originais, incluindo 18 de estudantes. Escrita e fluência do 1º ano estão sem resultado no portal.

| Ano | Cadastro | Leitura avaliados | Matemática avaliados | Escrita avaliados | Fluência avaliados |
|---|---:|---:|---:|---:|---:|
| 1º | 24 | 24 | 24 | sem resultado | sem resultado |
| 2º | 28 | 28 | 28 | 28 | 28 |
| 3º | 24 | 24 | 24 | 24 | 24 |
| 4º | 42 | 42 | 42 | 41 | 42 |
| 5º | 54 | 53 | 54 | 52 | 52 |

São 172 registros de cadastro na população por ano, não a soma de todas as aplicações. As comparações devem informar quantos estudantes possuem observações válidas nas variáveis envolvidas.

As provas de leitura/matemática oferecem acertos/itens por bloco H. Nas observações avaliadas auditadas, os denominadores somam 22 itens; um bloco H agrega entre 1 e 4 itens. Não há informação suficiente para inventar qual item específico dentro do bloco foi acertado.

### 3.2 Fontes curriculares

- PDF local `MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf`, 29 páginas.
- Mapa observado no portal: `resultados-caed-ciclo-i-2026/conferencia/mapa_posicao_codigo_caed.csv`, 124 observações de posição e 93 códigos CAEd distintos.
- Repositório solicitado: [MarceloClaro/bncc-dados](https://github.com/MarceloClaro/bncc-dados), branch `main`, commit consultado `9c268978efa2aa250834c6a9edb6074432752838`.
- O clone local `bncc-dados` está no mesmo commit; seu remoto original é `bncc-dev/bncc-dados`. A referência do usuário será registrada como origem do projeto, preservando a proveniência do dataset upstream e suas licenças.

### 3.3 Fontes históricas e incompatíveis

Os pacotes antigos de 1º/2º ano e suas planilhas são material de auditoria, não fonte prioritária para duplicar alunos. As etiquetas “referência” e “contraprova” foram assumidas por scripts antigos; não comprovam ciclos ou datas de aplicação.

O ZIP antigo rotulado como matemática do 1º ano contém Língua Portuguesa e será marcado incompatível. O novo ZIP de matemática tem componente correto. O arquivo de resultados antigo com sufixo `-1ANO` na raiz inclui resultados dos dois anos; sua classificação deve seguir conteúdo e hash.

A pasta SAAP contém uma imagem isolada. Ela não autoriza inferir uma tabela individual ou equivalências de alunos/provas.

## 4. Organização e contrato de dados

Os caminhos originais permanecerão preservados para não romper os manifestos e o MCP existente. A organização será feita por catálogo verificável, fontes referenciadas e saídas versionadas. Cópias eventualmente necessárias serão conferidas por hash; exclusões e substituições de fontes não fazem parte da rotina.

Estrutura proposta, a criar na implementação:

```text
docs/superpowers/specs/       especificação e revisões
docs/sdd/                    requisitos, decisões e rastreabilidade
docs/tdd/                    plano de testes e critérios de contraprova
docs/auditoria/              achados e evidências já inspecionadas
datamining/config/           metas, regras e parâmetros versionados
datamining/src/              ingestão, validação, relações e análises
datamining/tests/            testes, propriedades e casos de regressão
datamining/hooks/            verificações executáveis do projeto
datamining/agents/           contratos dos papéis, referenciados pelo Core
datamining/catalogo/         fontes, hashes, versões e incompatibilidades
datamining/dados/             tabelas normalizadas e banco analítico
datamining/restrito/          identidade local e intervenção nominal
datamining/relatorios/        relatórios agregados e figuras
datamining/evidencias/        RED, GREEN, mutações e recibos de execução
```

### Entidades mínimas

1. `fonte`: caminho, hash, licença, origem, data de exportação e avaliação identificada.
2. `avaliacao`: programa, edição, ciclo comprovado, componente, ano avaliado, instrumento e status de comparabilidade.
3. `aluno_local`: chave pseudonimizada, identidade restrita e qualidade da vinculação.
4. `matricula`: escola, turma, ano e período; não presumir permanência de turma entre avaliações.
5. `observacao_habilidade`: aluno/avaliação/posição, acertos, oportunidades, ausência e fonte bruta.
6. `observacao_escrita` e `observacao_fluencia`: medidas e categorias próprias, com unidades explícitas.
7. `posicao_avaliacao`: avaliação + ano + componente + posição H + código CAEd observado.
8. `ocorrencia_matriz`: versão do PDF, página, ano da tabela, componente, código e marcas de ciclo.
9. `vinculo_caed_bncc`: ocorrência contextual + BNCC + fonte + status e ressalva semântica.
10. `grupo_pedagogico` e `pertencimento_grupo`: definição, versão, membros, estabilidade e revisão docente; grupos podem se sobrepor.

### Identidade e ausência

Os arquivos não trazem identificador institucional de aluno. A ligação local provisória usa escola + ano + turma + nome normalizado, somente após verificar unicidade; o nome permanece em área restrita. Há homônimo no 5º ano, em turmas diferentes. Não usar nome isolado como chave nem chamar o pseudônimo derivado de identidade longitudinal validada.

Conservar campos distintos para cadastro, participação na avaliação, disponibilidade da tarefa e valor observado. Vazios, `-` e “sem resultado” não viram zero. Zero obtido por participante permanece zero.

## 5. Estatística e contraprova primeiro

Requisitos R01–R08:

- **R01:** validar hashes, esquema e origem dos filtros antes de calcular resultados.
- **R02:** rejeitar duplicação de alunos, fanout de joins e mistura de instrumentos.
- **R03:** testar `0 ≤ acertos ≤ oportunidades` e reconciliação de blocos, prova, turma e escola.
- **R04:** usar `soma(acertos)/soma(oportunidades)`, nunca média simples de percentuais H com denominadores diferentes. A auditoria encontrou divergência individual de até 10,909 pontos percentuais quando se usa essa média inadequada.
- **R05:** apresentar cadastro, avaliados e observações válidas; a proporção de adequados usa avaliados, com a cobertura reportada separadamente.
- **R06:** confirmar cálculos por implementação independente em inteiros/Fraction/stdlib ou SQL; a contraprova não pode chamar a mesma função do cálculo principal.
- **R07:** registrar estimativas, tamanhos de efeito, tamanho amostral, incerteza e universo de comparações; testes não transformam censo da escola em amostra aleatória.
- **R08:** manter diferenças de escala de escrita, fluência, leitura e matemática; categorias ou contagens não são percentuais por conveniência.

Contraprovas estatísticas incluem recomposição de totais, arredondamento, permutação adequada ao desenho, reamostragem de estudantes dentro dos estratos quando interpretável e análise de sensibilidade. Descrever incerteza de mensuração/generalização separadamente do resultado exato observado na escola.

## 6. Duas metas e intervenção

### R09: Meta A, 80% de adequados

Para cada ano/componente comparável: `alvo = teto(0,8 × avaliados)`; `conversoes = max(0, alvo − adequados_originais)`. Preservar os níveis CAEd registrados. Escrita/fluência possuem categorias próprias e não serão convertidas ao nível “adequado” sem regra oficial documentada.

O mínimo observado entre alunos adequados é um corte empírico da amostra, não um limiar oficial do instrumento. A distância individual até um corte de adequação e o número de acertos necessários para mudar de nível só serão apresentados como exatos quando houver regra oficial aplicável ou informação suficiente que a determine. Nos demais casos, informar indisponibilidade ou cenário explicitamente hipotético.

### R10: Meta B, 80% dos acertos por aluno

Para instrumentos com contagens válidas: `alvo_individual = teto(0,8 × oportunidades)` e `lacuna = max(0, alvo_individual − acertos)`. Nos instrumentos atuais de 22 itens, o alvo aritmético é 18 acertos. Não atribuir esse alvo às notas de escrita ou tarefas de fluência sem um contrato específico de unidade e finalidade.

### R11: matriz nominal de intervenção

Cada linha deve indicar chave/nome restrito, turma, avaliação, participação, resultado observado, meta aplicável, lacuna, habilidades CAEd prioritárias, BNCC documentadas e ressalvas, oportunidades de evidência, confiança/limites, sugestões de atividade e campo para revisão docente.

Priorizar necessidade e acesso ao apoio; a fila de alunos próximos de um limiar pode apoiar planejamento de cenários, mas não deve excluir alunos com maiores lacunas. Ordenações serão recalculadas, sem depender da ordem física do Excel. “Acertos adicionais” significa distância aritmética, não intervenção garantida ou número comprovado de aulas.

## 7. Relações curriculares, matrizes e convolução

### R12: correspondência contextual

Dos 124 registros observados, 118 aparecem na tabela do próprio ano e seis do 5º ano apenas em tabelas anteriores. Todos os 93 códigos existem no PDF; as relações presentes nos contextos auditados apontam para 73 BNCC existentes no canônico.

As seis exceções são `3EF09_P`, `3EF15_P`, `4EF10_P`, `3EF11_M`, `3EF12_M`, `3EF17_M`. Registrar “fonte anterior/integração a confirmar”, conservando a nota oficial sobre blocos de integração. Não converter essa nota em confirmação individual da ocorrência.

Quatro casos impedem um dicionário global simples CAEd→BNCC: `3EF06_M`, `3EF07_M`, `3EF09_M`, `4EF07_M`. Os conjuntos BNCC variam por ano da tabela. A chave da relação inclui fonte, versão, ano, componente e ocorrência.

Há vínculos publicados com diferenças semânticas entre os textos, como leitura de frases associada a BNCC de escrita. Preservar ambos os textos e marcar “associação publicada com ressalva semântica”; não corrigir silenciosamente o documento nem chamar a ligação de equivalência integral.

A marca de Ciclo I do `3EF16_P`, p.7, foi conferida visualmente: está na primeira coluna, alinhada à esquerda. A extração deve usar limites da célula, não proximidade com o centro esperado. Evidência: `docs/auditoria/figuras/matriz-cnca-pagina-07.png`.

### R13: propagação curricular explicável

Construir matriz bipartida `B` entre ocorrências contextualizadas CAEd e BNCC. Relações incertas entram em camadas separadas. Normalizar pesos para impedir multiplicação artificial de evidências em vínculos muitos para muitos.

Construir adjacência curricular a partir de `B Bᵀ`, com regra explícita de diagonal e normalização por grau. Produzir matrizes de evidência observada e, ao lado, versões propagadas em um ou dois passos. Divulgar equação, cobertura, graus e casos sem vizinhos.

Aresta significa compartilhamento de uma associação curricular documentada. Não significa pré-requisito, dependência causal ou domínio individual da BNCC. A propagação é transformação exploratória por grafo; não será apresentada como rede convolucional treinada ou previsão validada.

### R14: níveis de agregação

Produzir visões de aluno, grupo, turma e escola com denominadores rastreáveis. Não atribuir média de escola a aluno. Grupos sobrepostos não podem ser somados para reconstruir turma/escola sem deduplicar membros.

## 8. Correlações e projeções

### R15: correlações

Cruzar leitura/matemática/escrita/fluência por vinculação local auditada, dentro de ano/instrumento comparável. Apresentar Pearson e Spearman quando definidos, N de pares, intervalos/sensibilidade e controle Benjamini–Hochberg por família de hipóteses pré-declarada.

Correlações habilidade–total usarão total sem o próprio bloco, reduzindo correlação mecânica parte–todo. Constantes e ausência de pares produzem “não estimável”, nunca r=0 ou significância inventada. Permutações devem respeitar pareamento e estratos; tamanhos de turma e disponibilidade podem impedir inferência robusta.

Não comparar H01 de formas diferentes por posição. Não interpretar correlação de desempenho contemporâneo como efeito causal de ensinar uma habilidade, nem misturar séries com dificuldade distinta para obter uma correlação escolar artificial.

### R16: cenários condicionais

Calcular lacunas e cenários transparentes com ganhos aritméticos, listas de candidatos e premissas explícitas. Permitir perdas/regressões e ausência de intervenção na sensibilidade, sem congelar todos os adequados com probabilidade 1.

Não estimar probabilidades individuais de aprendizagem usando probabilidades arbitrárias. O benefício de uma atividade específica não foi observado experimentalmente. Recomendações de habilidade devem usar evidência de dificuldade, cobertura curricular, incerteza e revisão pedagógica.

### R17: previsão temporal, condicionada

Só liberar modelo preditivo após haver identidade longitudinal validada, datas de aplicação reais, avaliações comparáveis e desfecho futuro observado. Exigir baseline simples, particionamento temporal e por estudante, processamento ajustado apenas no treino, avaliação em dados mantidos fora do ajuste, calibração e análise de incerteza. Não usar rótulo futuro nem componentes do próprio alvo nas variáveis de entrada.

Na situação atual, o status esperado é **previsão temporal não estimável com validação; cenários condicionais disponíveis**. A ausência de dados temporais não bloqueia os demais resultados honestos.

## 9. Clusters e descrição pedagógica

### R18: agrupamentos exploratórios

Agrupar alunos dentro de ano e cobertura comparável, usando perfis observados de habilidades com suas oportunidades. Comparar ao menos uma alternativa simples e a representação curricular propagada; verificar se o grafo muda as conclusões. Manter ausência como ausência e não como baixo desempenho.

Avaliar poucos valores de K compatíveis com o N, estabilidade por reamostragem e sementes, separação e tamanho mínimo. Não impor clusters se os critérios de estabilidade falharem. Os limiares técnicos deverão constar da configuração e passar por sensibilidade; não serão descritos como verdades pedagógicas.

Cada descrição completa incluirá: versão, ano/componente, quantidade de alunos, turmas presentes, critérios de pertencimento, distribuição de resultados e oportunidades, forças e lacunas CAEd, BNCC vinculadas e ressalvas, alunos sem cobertura, estabilidade, exemplos de atividades, ordem sugerida de acompanhamento e data/critério de reavaliação. Os grupos serão nomeados pelo perfil de evidência, sem rótulos de capacidade fixa.

O professor decide a composição prática das intervenções. Os grupos não determinam retenção, exclusão, promoção escolar ou diagnóstico clínico.

## 10. Agentes, Core e hooks

### R19: papéis e execução real

Reutilizar o primário MarceloClaro e perfis Core existentes, quando cobrem o escopo: `plugin-data`, `scientific-profile`, `scientific-review` e `red-history-final-audit`. Validar e registrar pelo Core qualquer perfil novo antes de ativá-lo. A orquestração utilizará as fachadas `ecosystem_*`, com spec_id quando exigido; não criar um segundo coordenador do Core.

Papéis de trabalho previstos: curadoria de fontes, estatística principal, contraprova independente, vínculo curricular, análise exploratória e revisão de entrega. Um mesmo perfil existente pode assumir mais de um papel em operações distintas. O auditor não certifica o próprio cálculo sem contraprova independente.

Inventário/registro não comprovam inferência. Cada recibo separará configurado, validado, ativado, executado, testado e entregue. Não enviar dados nominais a serviços ou executores externos; identificar explicitamente qualquer handoff com dados minimizados.

### R20: hooks e gates verificáveis

1. Antes da ingestão: verificar manifesto, hash, esquema e proteção dos originais.
2. Antes da análise: verificar identidade, denominadores, versões curriculares e metas.
3. Antes de projeção: aplicar gate de temporalidade/comparabilidade; impedir rotular cenário como previsão validada.
4. Depois da execução: registrar parâmetros, versões de bibliotecas, seeds, hashes e contraprova.
5. Antes da entrega: testes aprovados, inspeção dos artefatos, validação nominal restrita e ausência de dados pessoais nas saídas agregadas destinadas a compartilhamento.

Os hooks do projeto terão comando executável e código de saída testados. Eventos de sessão do Core/aplicativo só serão declarados ativos depois de um teste de disparo real no host compatível. Um arquivo de configuração isolado não comprova proteção ativa.

## 11. SDD, TDD e critérios de liberação

R21–R24:

- **R21:** cada requisito rastreado até contratos, testes, artefatos e evidência.
- **R22:** TDD real por incremento: RED demonstrando ausência/defeito esperado, GREEN com implementação mínima e REFACTOR sem regressão. Não reconstruir um RED fictício após a implementação.
- **R23:** testes de mutação e propriedades atacam erros concretos auditados, como média indevida de percentuais, troca de componente, emparelhamento só por nome e união global de BNCC.
- **R24:** liberação exige recibo de execução, hashes reconciliados, testes/contraprovas aprovados e limitações presentes nos artefatos. Validação computacional local não equivale a validação pedagógica externa.

O contrato detalhado de testes está em `docs/tdd/CONTRATO_TESTES_AIRAM.md`. Seu estado inicial é **planejado**. A auditoria atual é evidência de inspeção/contraprova, não substitui o histórico RED→GREEN do software a construir.

## 12. Entregáveis previstos

1. Catálogo completo e verificável dos arquivos, versões e incompatibilidades.
2. Banco analítico e CSVs normalizados, com dicionário e máscaras de ausência.
3. Matrizes aluno–CAEd, CAEd–BNCC, adjacência/propagação, e visões grupo/turma/escola.
4. Relatório estatístico agregado com correlações, contraprovas e cenários honestos.
5. Planilha nominal restrita de intervenção e metas, com fórmulas e regras revisáveis.
6. Dossiê descritivo dos agrupamentos que passarem pelos critérios de estabilidade.
7. Código, testes, hooks, contratos de agentes e recibos reais de execução.
8. Guia de reprodução e lista de pendências para habilitar previsão temporal futura.

## 13. Revisão necessária

Escolher a alternativa de desenho; confirmar horizonte de avaliação; aprovar o tratamento estrito dos vínculos contextuais e o limite entre cenário e previsão temporal. Em seguida, revisar o plano de implementação e executar os incrementos TDD.

## 14. Referências metodológicas

- [BNCC dados, fork solicitado](https://github.com/MarceloClaro/bncc-dados), commit fixado na seção 3.
- [SciPy: permutation_test](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.permutation_test.html), desenho de permutações e pareamento.
- [scikit-learn: Common pitfalls](https://scikit-learn.org/stable/common_pitfalls.html), prevenção de vazamento e processamento ajustado no treino.
- [Kipf e Welling, 2017](https://arxiv.org/abs/1609.02907), referência de convolução em grafos; seus experimentos não constituem validação do uso educacional proposto aqui.

As regras específicas deste projeto são propostas técnicas a serem testadas. As fontes metodológicas não validam automaticamente os resultados da escola.
