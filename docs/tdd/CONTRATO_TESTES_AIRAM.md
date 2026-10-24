# Contrato TDD e contraprova, SPEC-AIRAM-001

Estado: **cenários especificados; testes de produto ainda não implementados/executados**.

Não marcar PASS, RED ou GREEN sem recibo de uma execução real. As verificações de leitura dos dados atuais são registradas separadamente no relatório de auditoria.

## Procedimento por incremento

1. Aprovar requisito e resultado esperado, incluindo casos negativos.
2. Escrever teste isolado; executá-lo e registrar RED pela ausência/defeito alvo. Erro de instalação não serve como RED funcional.
3. Implementar o mínimo; registrar GREEN.
4. Refatorar e repetir os testes afetados.
5. Executar contraprova independente e mutações relevantes.
6. Registrar hash de entrada/saída, versão, comando, código de saída e limitação científica.

Fixtures sintéticas são permitidas para testar software, sempre identificadas. Resultados escolares e relatórios científicos devem derivar exclusivamente das fontes reais e autorizadas.

## Casos obrigatórios e rastreabilidade

| Teste | Requisito | Caso/ataque | Resultado exigido |
|---|---|---|---|
| T01 | R01 | Alterar um byte da fonte | Ingestão rejeitada por hash |
| T02 | R01 | CSV sem ciclo interno e sem manifesto | Avaliação não identificada; bloquear mistura |
| T03 | R01 | ZIP antigo nomeado matemática contendo LP | Conteúdo prevalece; incompatibilidade explícita |
| T04 | R02 | Aluno duplicado na mesma chave | Bloqueio com diagnóstico, sem deduplicação silenciosa |
| T05 | R02 | Homônimos em duas turmas do 5º ano | Dois alunos locais, sem colapso por nome |
| T06 | R02 | Cruzamento sem ID institucional | Qualidade da ligação local provisória preservada |
| T07 | R03 | 3 acertos em 2 oportunidades; negativos | Rejeitar valores impossíveis |
| T08 | R03 | Somatório dos H difere do total | Falha de reconciliação |
| T09 | R03 | Prova real atual avaliada | Denominadores reconciliados; 22 como contrato da fonte atual |
| T10 | R04 | H com 1/1 e 0/3 | Resultado 25%, nunca 50% |
| T11 | R04 | Reordenar alunos/H/arquivos | Totais e resultados invariantes |
| T12 | R05 | 53 avaliados em 54 cadastros | Meta e taxas usam denominador explicitado |
| T13 | R05 | Não avaliado com H vazio | Excluir da taxa de avaliado, preservar cadastro |
| T14 | R05 | Participante com zero legítimo | Manter zero, não converter em ausência |
| T15 | R06 | Verificador usa a função principal | Contraprova recusada por dependência compartilhada |
| T16 | R07 | Coluna constante ou N insuficiente | Correlação não estimável e motivo explícito |
| T17 | R07 | Família de múltiplos testes | p e q ajustado disponíveis, família e N rastreáveis |
| T18 | R08 | Contagem de fluência lida como percentual | Contrato de unidade impede cálculo indevido |
| T19 | R08 | Escrita ausente marcada '-' | Ausência preservada sem zero |
| T20 | R09 | 10 adequados em 24 avaliados | Alvo 20; faltam 10 conversões, sem estimar acertos oficiais |
| T21 | R09 | Corte mínimo observado entre adequados | Rotular empírico; não promovê-lo a regra oficial |
| T22 | R10 | 22 itens por aluno e meta 80% | Alvo 18; 17 acertos não atinge a Meta B |
| T23 | R10 | 80% exato, zero itens, prova ausente | Respeitar limite, rejeitar denominador zero e não inventar meta |
| T24 | R11 | Reordenar linhas Excel | Prioridade recalculada por critérios, sem depender da ordem física |
| T25 | R11 | Empate ou grande lacuna | Critério de desempate explícito e apoio não excludente |
| T26 | R12 | H01 em anos/componentes diferentes | Posições não confundidas |
| T27 | R12 | Quatro códigos com BNCC contextual variável | Preservar conjuntos por ano/fonte; rejeitar união global |
| T28 | R12 | Seis exceções do 5º ano | Fonte anterior identificada, integração ainda ressalvada |
| T29 | R12 | Código BNCC inexistente/inativo | Relação não confirmada, sem substituição inventada |
| T30 | R12 | Leitura de frase ligada a BNCC de escrita | Preservar publicação e ressalva semântica |
| T31 | R12 | X alinhado à esquerda na célula de Ciclo I | Extrair por limites da célula; regressão da p.7 |
| T32 | R13 | Um CAEd com três BNCC | Evidência não triplicada; pesos/normalização conferidos |
| T33 | R13 | Grafo sem vizinhos ou com autolaço | Resultado definido e regra documentada |
| T34 | R13 | Propagação altera observação original | Teste falha; observado e derivado ficam distintos |
| T35 | R14 | Grupos sobrepostos | Turma/escola deduplicadas; sem soma ingênua dos grupos |
| T36 | R14 | Agregado escolar atribuído a aluno | Fluxo recusado |
| T37 | R15 | H correlacionado com total que o contém | Usar total corrigido e demonstrar a diferença |
| T38 | R15 | Par adulterado no dataset histórico | Comparar valores à fonte, além de contar pertencimento |
| T39 | R15 | Permutação rompe pareamento indevidamente | Desenho inválido recusado |
| T40 | R16 | Ganho hipotético tratado como intervenção causal | Rótulo cenário obrigatório; interpretação causal recusada |
| T41 | R16 | Todos adequados congelados com probabilidade 1 | Exigir cenário de perda/regressão ou ressalva explícita |
| T42 | R17 | Somente Ciclo I confirmado | Sem previsão temporal validada; cenários continuam disponíveis |
| T43 | R17 | Alvo/observação futura entra no treino | Gate de vazamento deve falhar |
| T44 | R17 | Mesmo aluno em treino/teste de generalização indevida | Partição incompatível recusada |
| T45 | R18 | Ordem/semente/reamostragem dos clusters | Estabilidade medida e registrada |
| T46 | R18 | Grupo minúsculo ou instável | Não liberar cluster como conclusão robusta |
| T47 | R18 | Característica ausente vira déficit | Teste impede imputação sem política aprovada |
| T48 | R18 | Perfil de grupo sem descrição curricular/fonte | Entrega incompleta |
| T49 | R19 | Perfil só inventariado/registrado | Nunca afirmar inferência executada |
| T50 | R20 | Hook retorna falha e o processo continua | Gate falha no teste de integração |
| T51 | R20 | Configuração de evento sem disparo real | Estado configurado, não ativo verificado |
| T52 | R20 | Fonte nominal em saída agregada de compartilhamento | Bloquear liberação e indicar origem do vazamento |
| T53 | R21 | Requisito sem teste/artefato/recibo | Rastreabilidade incompleta |
| T54 | R22 | Função pronta antes do primeiro teste | Não fabricar histórico RED; declarar evidência insuficiente |
| T55 | R23 | Mutação: trocar média ponderada por simples | Teste T10 deve matar a mutação |
| T56 | R23 | Mutação: retirar turma da chave | Teste de homônimo deve matar a mutação |
| T57 | R23 | Mutação: remover ano da ligação curricular | Testes contextuais devem matar a mutação |
| T58 | R24 | Falha de teste ou artefato com hash incorreto | Não liberar pacote como validado |

## Contraprovas reais prioritárias

- Reconciliar os 18 ZIPs/54 CSVs e o manifesto sem usar os nomes dos arquivos como único identificador de conteúdo.
- Recalcular taxas H/turma/escola por soma de contagens, comparando com os arredondamentos do portal.
- Confirmar as 124 posições e os códigos publicados no PDF, incluindo os contextos múltiplos e exceções.
- Comparar as duas metas separadamente; conservar cortes empíricos históricos apenas como hipóteses.
- Reavaliar as correlações e cenários anteriores; expor o que não é temporalmente identificado.

## Registro de execução esperado

Cada incremento terá ID, requisito, teste, estado RED/GREEN/REFACTOR, comando, timestamp, código de saída, hash do código e dos dados, versão de dependências, mutação e artefato correspondente. Estado inicial de T01–T58: **NÃO EXECUTADO**.

O checklist não constitui evidência de testes aprovados. Nenhum relatório futuro pode usar a existência deste documento para alegar uma execução que não ocorreu.
