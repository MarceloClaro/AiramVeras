# T07 → T08/T10: evidência observada e propagação curricular

Versões `airam-grafo-t07-v1` (agregado) e `airam-grafo-restrito-t07-v1` (individual).
Schemas fechados em `docs/esquema-t07.json` e `docs/esquema-restrito-t07.json`.

## Entradas e checkpoints

| Arquivo | SHA256 |
|---|---|
| `curriculo/t04/checkpoint.json` | `a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796` |
| `restrito/t05/checkpoint.json` | `6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b` |
| `estatistica/t07/checkpoint.json` | `71a0302d7ec9ae0f837069eea3b5c867052ff3885d5a9fb7491eee616abd9d58` |
| `restrito/t07/checkpoint.json` | `17916019d8a8787c95ec3db580aae7987b11c5c93a72c34ad13846a7bf1bb8fe` |

O agregado não contém nomes, pseudônimos, membros de grupos ou matrizes individuais.
O checkpoint restrito contém identificadores locais provisórios e fica ignorado pelo Git.
Esta separação é de armazenamento; não certifica ACL nem proteção nativa de Excel.
Nenhum dado de estudante foi enviado a serviços externos.

## Universo e chaves

Dez instrumentos: mesma avaliação, edição, ciclo I, ano escolar e componente.
Cada instrumento é processado nas políticas `estrita` e `ressalvada`, totalizando 20 blocos.
O contexto das observações ainda conserva fonte_id, SHA256 e exportação T05; não se
unem H de instrumentos diferentes. A bipartida recebe um único contexto de mapa,
incluindo fonte/versão. O nó CAEd conserva fonte PDF, SHA e ocorrência; BNCC conserva
documento, commit e código. Ordem de `nos`, `bncc`, `posicoes` e `alunos` define os eixos.
Somente `alunos` é individual e restrito. Nós sem arestas elegíveis permanecem nos eixos.

`ressalvada`: associações confirmadas do próprio ano/ciclo e BNCC confirmada, com peso
positivo, incluindo ressalvas semânticas. `estrita`: remove adicionalmente a ressalva
semântica. Candidatas anteriores continuam peso zero em ambas. A publicação original
não é corrigida ou reinterpretada como confirmação. As 118 posições elegíveis na
ressalvada caem para 110 na estrita; 146 relações positivas caem para 138. A união de
BNCC ativas é 73/71. Colunas inativas são conservadas, portanto contar todas as colunas
não é o mesmo que contar BNCC ativas. São 129 nós contextualizados, incluindo 11
candidatos, e não as 202 ocorrências documentais do PDF inteiro.

## Matrizes e equações

`construir_bipartida(vinculos, policy)` retorna B, W, A, graus, massa_grau e eixos.
Duplicatas idênticas de vínculo são idempotentes; divergências são recusadas.
B distribui uma unidade por ocorrência entre suas BNCC elegíveis distintas: 3 BNCC
recebem 1/3 cada. W=B Bᵀ; a vizinhança remove a diagonal e A normaliza cada linha não
nula. `graus` conta vizinhos distintos; `massa_grau` é a soma anterior à normalização.
Nenhum desses valores é quantidade de itens ou evidência pedagógica independente.

`matrizes_evidencia(rows, posicoes, grafo)` retorna:

| Campo | Unidade e ausência |
|---|---|
| C / D | Acertos/oportunidades originais por aluno × posição, inteiros representados numericamente; null ausente |
| P | C/D apenas onde disponível; zero obtido é zero |
| observado_mask | Máscara original por aluno × posição |
| cobertura_observada | Fração das posições previstas com medida, não cobertura ponderada por itens |
| Q | Posição × ocorrência: unidade repartida entre ocorrências elegíveis distintas; linha zero quando não associada |
| C_alocada / D_alocada | Massa alocada C Q / D Q; pode ser fracionária, não são novos itens |
| P_ocorrencias / mask_ocorrencias | Razão das massas / denominador alocado positivo, por aluno × ocorrência |

As contagens originais permanecem disponíveis mesmo em posições excluídas do grafo.
Nos dados atuais cada posição positiva alcança uma ocorrência; a API também testa a
repartição entre duas ocorrências sem multiplicar acertos/oportunidades. Ausência de
observação e ausência de associação são causas diferentes, visíveis em P e em Q.

`propagar(P_ocorrencias, mask_ocorrencias, A, passos)` aceita um ou dois passos.
Para K=A^s: numerador[i,j]=Σ K[j,k] M[i,k] P[i,k]; cobertura[i,j]=Σ K[j,k] M[i,k].
Propagado é numerador/cobertura; massa zero resulta em null (NaN apenas em memória).
`fontes_distintas` conta nós observados que alcançam o destino, não caminhos ou itens.
`observado` e `observado_mask` são cópias separadas, nunca sobrescritas pelo propagado.
Sempre se usa a máscara original; a estimativa do passo 1 não alimenta nova evidência.

A² pode conter diagonal. `massa_retorno[i,j]=M[i,j] K[j,j]` revela esse autorretorno.
`sem_retorno` usa K com diagonal removida e divide pela massa observada restante;
`cobertura_sem_retorno` conserva essa massa sem renormalizar previamente o kernel.
Um par isolado tem A²=I: dois passos repetem o próprio dado, e a sensibilidade fica
inteiramente ausente. Isso não é confirmação independente. Matemática do 1º ano não
possui vizinhos compartilhados: toda propagação permanece ausente, com observado intacto.

## Visões e grupos

`agregar_observacoes(rows, nivel, grupos=None)` aceita somente observações individuais
de acertos/oportunidades, nunca um agregado escolar para atribuir a estudantes. Chave
deduplicada: contexto completo T05 + aluno_local_id + posição. Duplicatas semanticamente
idênticas não acrescentam massa; conflitos de contagem, aplicação, turma ou participação
são recusados. Razão de somas, nunca média de taxas. As quatro visões se originam nas
linhas originais; não se somam grupos para reconstruir escola/turma.

`cadastros`/`avaliados` são estudantes distintos dentro do instrumento, não células.
`validas`/`ausentes` contam células H; `taxa_observada` usa células disponíveis, enquanto
`taxa` fica ausente se há célula faltante de participante. Zero soma sem observações
não vira taxa zero. Turmas/escola e grupos estão no agregado; alunos ficam restritos.

Os grupos entregues são regras operacionais explícitas, sobrepostas: `evidencia_completa`
e `abaixo_meta_B_observada` (total individual <80% em instrumento completo). Membros
somente no restrito; não são clusters nem rótulos de capacidade. Grupos estatísticos
da T08 podem usar a mesma API com seus membros locais. Meta A não é inferida dessas
regras. Não somar resultados de instrumentos/componentes como se fossem pessoas únicas.

## Verificação e consumo

T32–T36 exercitam fanout, duplicatas, isolados, ausência, zero, dois passos, retorno,
permutação consistente dos eixos, grupos sobrepostos e recusa de atribuição ecológica.
A contraprova `evidencias/T07/contraprova.py` relê T04/T05, reconstrói B/A e cada caminho
com Fraction/laços sem importar airam/numpy; confere todos os blocos e contagens das
visões. São 129.997 comparações reais, além das contas manuais fechadas nos testes.
Quatro mutações deliberadas em cópia temporária foram detectadas funcionalmente.

Reproduzir com `.venv/Scripts/python.exe evidencias/T07/executar.py <rotulo-novo> ANALISE
evidencias/T07/analisar.py`; usar rótulos novos preserva recibos. O coletor captura
hashes/versões antes de executar. Checkpoints determinísticos diferentes não são
sobrescritos automaticamente. Para contraprova e entrega, usar o mesmo coletor com
`contraprova.py` e `validar_entrega.py`. O validador de entrega implementa todos os
keywords efetivamente usados nos dois schemas, sem alegar validação de keywords não usados.

T08 deve comparar observado e propagado com suas máscaras no mesmo instrumento,
conservar oportunidades e explicitar exclusões por cobertura; grafos esparsos não
autorizam cruzar anos/ciclos para obter clusters. T10 deve separar observado, propagado,
cobertura e autorretorno; somente C/D originais alimentam contagens e metas. Associação
curricular não demonstra domínio BNCC, causalidade, GCN treinada ou previsão validada.
