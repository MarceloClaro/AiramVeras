# T06 → T07/T10/T11: associações por ano e instrumento

Entrega: `estatistica/t06/entrega/checkpoint.json` (agregado, `airam-associacoes-t06-v1`), SHA256 **`2a0472e9b391e0a1c66af53c6d4572f00109a81b49ff547fd5cf8bf8c3e42570`**, `associacoes.csv`, `plano.json` e `instrumentos.json`. Pares exclusivamente em `restrito/t06/entrega/plano-pares.json`, SHA256 **`dc4f3d0721db427c7001cabbd5199f98a653881be021d274fde2bfead4c58af6`**. Hashes definitivos em `evidencias/T06/analise-entrega.json` e `verificacao-entrega.json`. Não usar tentativa-04/final como versão entregue: são execuções históricas preservadas. A pasta restrita não certifica ACL. O CSV usa células vazias para nulos; zero é valor observado. O JSON é a interface completa. Em `plano.json`, os valores de `familias_planejadas` contam pares de variáveis; cada par gera dois testes, discriminados em `checkpoint.json.familias`.

Fontes fixas: checkpoint restrito T05 `6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b`; agregado T05 `5bfa87b38394d171589a7799751127dceb7d81587bbbfcefa67d2bb4a8420231`; currículo T04 `a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796`. O observado T05 foi confrontado integralmente com T03, sem substituir as sete tabelas ou editar os checkpoints anteriores.

## APIs

- `correlacionar(pares, x, y, strata, seed, *, config=None) -> list[dict]`: um contexto comparável por chamada, dois registros agregados (Pearson/Spearman). Entrada com `aluno_local_id`, `turma`, `ano_escolar`, `ano_avaliacao`, `ciclo`, `instrumento`, valores quantitativos nos campos x/y; participação/disponibilidade devem estar mascaradas como `None` pelo preparador. Exige todos os estratos declarados, recusa duplicatas, anos/instrumentos misturados e valores não finitos/categóricos. Configuração padrão em `config/correlacoes.json`.
- `ajustar_bh(p_values)`: aceita p válidos ou `None`, conserva posição/ausência. m é o comprimento planejado; não testados ocupam p=1 somente internamente. Resultado ausente nunca se torna zero.
- `ajustar_familias(rows)`: recebe todos os registros planejados com família/metodo/p; acrescenta BH/BY por família e BH global. O chamador não deve filtrar p ou selecionar coeficientes antes do ajuste.
- `total_sem_bloco(rows, posicao)`: entrada H T03 enriquecida com turma. Valida contrato T05, recusa oportunidades diferentes por H/contexto, retira numerador e denominador do próprio bloco. Saída individual **restrita**, com x=taxa H, y=taxa restante, contagens restantes e cobertura. Um único bloco ou ausência em qualquer bloco restante produz y ausente.
- `preparar_analises(tables, *, config=None)`: recebe `observado` T05 e produz plano com pares individuais **restritos**. Valida vínculos de medidas, contexto/versão, turma e denominadores. Une avaliações no mesmo ano/ciclo; não assume que N cadastral é N analítico. Categorias não entram.
- `auditar_pares(pares, referencia)`: compara multiconjunto de linhas completas. A referência deve vir de fonte independente autenticada; a função não autentica sozinha a referência. O executor real lê CSV original e reconstrói valores com parsing e `Fraction`, sem reutilizar as funções analíticas.

## Campos públicos

`tipo` distingue intercomponentes e H–total corrigido. `instrumento` é hash de contexto público de fontes/versões, cuja expansão está em `instrumentos.json`; não é identificador de estudante. `familia` inclui todos os dois coeficientes e todas as comparações planejadas antes da análise. `ano_escolar`, `ano_avaliacao`, `ciclo`, `componente` (H), `x`, `y`, `unidade_x/y` preservam interpretação.

`n` conta pares completos; `n_x/n_y` contam cada variável no universo de cadastros daquele contexto; `cadastros`, `excluidos`, `estratos`, `distintos_x/y`, `amplitude_x/y` mostram cobertura e variabilidade (distintos/amplitudes nos pares completos). `coeficiente` é tamanho de efeito descritivo no conjunto avaliado. `motivo_coeficiente` e `motivo_inferencia` explicam ausências. `p` é permutação condicional de pareamento, nunca probabilidade de H0. `q` significa p ajustado por BH, não outro estimador chamado q-value. `q_by` e `q_bh_global` são sensibilidades. `m_planejado/m_elegivel/m_bh/m_global` registram universos distintos.

`permutacao` conserva modo, número de replicações válidas, espaço permutável, seed, convenção e extremos da nula; estratos unitários ficam fixos. `sensibilidade` contém faixa percentílica, replicações válidas/degeneradas, motivo de supressão e rótulo censitário. `influencia` resume exclusão de um estudante por vez, sem divulgar sua identidade. `selecao_texto` sinaliza comparações ligadas às tarefas de texto/compreensão, cuja cobertura deve ser lida variável a variável; não afirma que toda tarefa perdeu a mesma quantidade de resultados.

Escalas: leitura/matemática e H têm frações 0–1 de acertos/oportunidades; escrita conserva Nota original; listas de palavras/compreensão conservam contagens com denominadores documentados constantes dentro de instrumento; Texto mantém quantidade e percentual publicado separados. Não há WPM, percentual de escrita, duração ou reconstrução de denominador do Texto.

## Resultados locais e interpretação

214 associações × dois métodos = **428 registros**, 15 famílias; 370 coeficientes estimáveis e 358 p disponíveis. Os 70 registros sem p se dividem em 46 com pares insuficientes, 12 com coluna constante e 12 com N abaixo do mínimo inferencial. Conferidos **7.714 pares**, 4.618 medidas H, 864 de escrita, 592 de fluência e 640 avaliações contra fonte. Os 185 Pearson e 185 Spearman estimáveis coincidiram com SciPy e cálculo algébrico independente; diferença máxima 5,08×10⁻¹⁴. BH/BY também foram confrontados com SciPy.

| Ano | N leitura–matemática | Pearson | p / BH | Spearman | p / BH |
|---|---:|---:|---:|---:|---:|
| 1º | 24 | 0,482 | 0,0197 / 0,3762 | 0,468 | 0,0209 / 0,3762 |
| 2º | 28 | 0,934 | 0,0001 / 0,0018 | 0,873 | 0,0001 / 0,0018 |
| 3º | 24 | 0,617 | 0,0051 / 0,01224 | 0,445 | 0,0297 / 0,05627 |
| 4º | 42 | 0,723 | 0,0001 / 0,000277 | 0,714 | 0,0001 / 0,000277 |
| 5º | 53 | 0,489 | 0,0009 / 0,0324 | 0,432 | 0,0032 / 0,0576 |

Os dois métodos não sustentam automaticamente a mesma conclusão. Não escolher o mais favorável. O p=0,0001 é o piso Monte Carlo bilateral, não um valor exato conhecido abaixo dessa resolução.

Seis faixas foram suprimidas por menos de 90% de reamostragens válidas: H02 e H11 de leitura/3º ano (1.293 e 1.234 válidas de 2.000, respectivamente) e H01 de leitura/4º ano (1.747), em ambos os coeficientes. Os coeficientes observados permanecem; não foram removidos estudantes para obter faixas.

Leitura–Nota de escrita: N=28/24/41/52 nos anos 2–5, com Pearson 0,088/0,676/0,651/0,068. Leitura–palavras globais: N=28/24/42/52, Pearson 0,239/0,561/0,667/0,317. As tabelas também incluem matemática–escrita, matemática–todas as cinco medidas de fluência e escrita–todas as cinco medidas de fluência; não se limitam aos exemplos acima.

Texto quantidade/percentual: N de leitura pareada 0/8/31/41 nos anos 2–5; o 3º ano é somente descritivo. Compreensão tem N próprio 28/24/42/52, sem herdar a máscara do Texto. Não se presumiu ausência aleatória. No 5º ano, leitura–matemática usa 53 pares, ainda que matemática tenha 54 disponíveis. Escrita e fluência não recebem acertos fictícios nem Meta A/B por esta tarefa.

| Objeto | O que sustenta | O que não sustenta |
|---|---|---|
| Coeficiente observado | Relação no conjunto de pares avaliados do ano/instrumento | Efeito de ensino, capacidade fixa ou relação escolar de séries misturadas |
| Permutação condicional | Compatibilidade com pareamento intercambiável dentro de turma sob hipótese declarada | Randomização demonstrada, causalidade, probabilidade de H0 ou generalização automática |
| Faixa de bootstrap | Sensibilidade à recomposição dos avaliados preservando turma | Erro amostral do censo, recuperação de ausentes, repetibilidade da prova ou variação entre escolas |
| BH/BY | Ajustes no universo planejado sob seus pressupostos | Reparação de pareamento inválido ou de seleção não modelada |

## Consumo e reprodução

T07 mantém sua fonte observada em T05 e o currículo em T04; não usa correlações como acertos adicionais. T10 pode exibir coeficientes/N/faixas/p/q e motivos, sempre com as unidades e limites; nenhum identificador individual está escondido no agregado. T11 integra os checkpoints pela CLI e deve preservar autenticação e fronteira restrita. Não houve autoria de workbook, novos agentes Core ou submissão externa nesta etapa.

Reproduzir: `.venv/Scripts/python.exe evidencias/T06/executar.py <rotulo-novo> ANALISE evidencias/T06/analisar.py <pasta-nova>`. Depois executar o verificador com a pasta nova. Rótulos/pastas existentes são recusados para preservar histórico. Os recibos incluem hashes anteriores de código, testes, configuração, coletor, entradas e versões. `docs/esquema-t06.json` e `docs/esquema-restrito-t06.json` são contratos 2020-12; o verificador local executa somente os keywords efetivamente usados e não se apresenta como implementação geral de JSON Schema.
