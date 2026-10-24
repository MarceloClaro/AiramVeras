# Contraprova independente dos percentuais do portal — preparação para T05

Data: 22/10/2026. Auditoria documental/computacional das fontes de LEITURA e MATEMATICA. Não constitui implementação, teste RED/GREEN, teste de mutação, aprovação de produto, pacote de liberação ou alteração do ledger da T05.

## Resultado observado

Foram confrontados **407 campos percentuais comparáveis**, em 10 agregados de escola e 14 de turma, cobrindo todas as H, todas as três categorias e participação dos 10 instrumentos de leitura/matemática do 1º ao 5º ano. **406 campos reproduzem o arredondamento racional ao inteiro mais próximo com metade para cima; um não reproduz essa regra.** Nenhuma diferença foi omitida ou corrigida no original.

| Família | Comparações | Reproduções metade para cima | Divergências dessa regra | Meios casos |
|---|---:|---:|---:|---:|
| Participação | 24 | 24 | 0 | 0 |
| Categorias originais | 72 | 72 | 0 | 2 |
| H | 311 | 310 | 1 | 15 |
| Total | 407 | 406 | 1 | 17 |

Por nível: escola, 164 comparações e nenhuma divergência da regra adotada; turma, 243 comparações e uma divergência. Das 407 comparações, 94 coincidem com o percentual exato sem arredondamento e 313 precisam de arredondamento. Todos os percentuais são publicados com zero casas decimais, preservados no recibo como texto original, inclusive sufixos `%`.

As 442 verificações adicionais de soma das contagens aluno → turma → escola coincidem integralmente: 70 de cadastros/participação/ausências/categorias e 372 de acertos, oportunidades e participantes por H. Esses checks são de contagens derivadas das mesmas fontes individuais; não são 442 percentuais publicados adicionais. A partição das turmas é completa e sem turma duplicada nos agregados.

## Divergência literal e quantização

Fonte: `csv_originais/4ANO_LEITURA_CICLO_I_2026/HABILIDADE_DESEMPENHO_TURMA 22-10-2026 6-13-30.csv`, turma **4º ANO B**, **H 13 (%)**. Os registros participantes do CSV individual correspondente somam **23 acertos em 40 oportunidades**, isto é, **57,5% exatos**. O agregado publica literalmente **`57`**. A diferença publicado − exato é **−0,5 ponto percentual**, com distância absoluta exatamente **0,5 ponto percentual**. Metade para cima e metade para par resultam ambos em **58**, portanto não reproduzem o publicado.

Separação necessária: para inteiro publicado 57, o intervalo **fechado** de quantização por proximidade é [56,5; 57,5] pontos percentuais. O exato está precisamente na fronteira superior desse intervalo, um empate entre os inteiros 57 e 58. Assim, há **compatibilidade com a precisão inteira quando ambas as fronteiras são admitidas**, mas **não há reprodução pela regra explícita metade para cima nem metade para par**. O recibo registra as duas afirmações em campos distintos. Essa compatibilidade não elimina a discrepância e não é usada para aprovar a T05 nem relaxar tolerância silenciosamente.

Nos 17 meios casos observados, 16 publicados correspondem à escolha do inteiro superior e este corresponde ao inferior. Metade para par reproduz 395/407 campos, com 12 diferenças. Nenhuma dessas regras foi identificada como política oficial. As fontes não demonstram a causa do caso H 13, não permitem atribuir erro a estudante e não autorizam corrigir o portal. Uma nova fonte oficial seria necessária para estabelecer o tratamento oficial de empates ou a cadeia numérica usada na publicação.

Todos os 407 valores estão dentro do intervalo fechado de meia unidade da sua precisão original; 17 estão na fronteira e 390 no interior estrito. Isso descreve resolução numérica e não transforma as 407 comparações em reprodução exata por uma regra única.

## Método e independência

Coletor próprio, exclusivamente stdlib (`csv`, `Fraction`, `Decimal`, `hashlib`, `zipfile` e auxiliares), sem importar qualquer módulo `airam`, de ingestão, métrica ou produto. Lê diretamente os CSV brutos autenticados; não usa tabelas T02/T03 como fonte aritmética. A análise usa `csv.DictReader`, UTF-8 com remoção de BOM e delimitador `;`; não divide registros por texto manualmente. Nomes de estudantes são descartados ao construir os registros internos. Não há exportação de linhas individuais, nomes, IDs ou pseudônimos, nem envio a serviços externos.

O coletor registra seu SHA256 e os hashes de manifesto, 18 ZIP e 54 CSV em `hashes-antes.json` **antes de interpretar qualquer CSV**. O manifesto precisa ter SHA256 fixo `0059670041831280892c45e9c3ed3c0b769f579c881631fb64c9afdf03409946`. Cada ZIP precisa coincidir com seu hash declarado, apresentar CRC válido e conter três CSV que coincidam byte a byte com os arquivos extraídos. Isso autenticou os **54 CSV canônicos**, incluindo escrita/fluência apenas na verificação física de fontes. Ao final, todos os hashes de entrada e o hash do coletor foram reconferidos sem mudança.

A análise numérica limita-se a 30 CSV de leitura/matemática: 344 registros individuais, dos quais 343 participações, 10 registros de escola e 14 de turma. A etapa e o componente internos de todas essas 368 linhas foram confrontados com os filtros registrados no manifesto. O ciclo/ano de aplicação permanecem informações de proveniência do manifesto; não se infere temporalidade dos CSV.

Participação: contagem de `Avaliado=Sim` dividida pelos cadastros efetivamente exportados no escopo. Esses CSV não fornecem contagem institucional `Previstos`; o denominador observado não deve ser renomeado para matrícula institucional total sem outra fonte. Participantes precisam ter categoria válida. A correspondência textual é explícita: `Defasagem` → `Defasagem`, `Intermediário` → `Aprendizado intermediário`, `Adequado` → `Aprendizado adequado`. Não há dedução de cortes ou equivalências pedagógicas entre anos.

H: cada célula válida é interpretada como acertos/oportunidades inteiros, com denominador positivo e numerador entre zero e denominador. Percentual por H = 100 × soma dos acertos / soma das oportunidades de participantes com medida. Não participante e H vazia/hífen ficam ausentes, não viram zero. Um zero numérico de participante permanece válido. Foram observadas 4.618 posições de célula H, 4.602 válidas e 16 ausentes, todas no único não participante do 5º ano de leitura. Nenhum participante desses componentes tem H ausente.

O cálculo racional e a decisão de arredondamento usam `Fraction`, inclusive detecção exata de empates. `Decimal` interpreta o percentual lexical publicado e fornece representações decimais aproximadas das razões; estas representações não decidem coincidência. Não se usa tolerância de ponto flutuante.

O recibo também conserva uma taxa derivada por instrumento e escopo, **não publicada no portal**: 100 × soma de todos os acertos / soma de todas as oportunidades entre as H. Não se faz média simples dos percentuais H, nem média de percentuais arredondados das turmas. A média simples é gravada somente como diagnóstico explícito do viés dessa alternativa. As H não são presumidas equivalentes entre anos ou componentes.

## Denominador destacado: 5º ano de leitura

**54 cadastros, 53 avaliados, 1 não avaliado.** Escola: participação 53/54 = 98,148148…%, publicada 98; categorias entre os 53 avaliados: 2 em defasagem, 6 intermediários, 45 adequados. Adequados = 45/53 = 84,905660…%, publicado 85%. As 16 H ausentes pertencem ao não participante e não entram nos denominadores de acertos ou categorias.

Turma A: 27 cadastros/27 avaliados; turma B: 27 cadastros/26 avaliados. O denominador H é 53, ou 106 para H com dois itens por participante, na escola; na turma B é 26, ou 52. A taxa derivada para todos os itens da escola é **891/1.166 = 76,415094…%**. A média simples das taxas H seria 78,891509…%, diferença que mostra por que não pode substituir a razão de contagens. Nenhuma dessas duas taxas globais é um percentual global publicado nos CSV.

## Contagens derivadas por instrumento na escola

Cada linha fica dentro do próprio instrumento; não se agregam anos/componentes em uma única medida de desempenho.

| Ano/componente | Cadastros | Avaliados | Defasagem | Intermediário | Adequado | Acertos/oportunidades de todas H |
|---|---:|---:|---:|---:|---:|---:|
| 1 LEITURA | 24 | 24 | 0 | 14 | 10 | 401/528 |
| 1 MATEMATICA | 24 | 24 | 0 | 13 | 11 | 476/528 |
| 2 LEITURA | 28 | 28 | 7 | 3 | 18 | 425/616 |
| 2 MATEMATICA | 28 | 28 | 6 | 7 | 15 | 427/616 |
| 3 LEITURA | 24 | 24 | 0 | 6 | 18 | 451/528 |
| 3 MATEMATICA | 24 | 24 | 4 | 3 | 17 | 401/528 |
| 4 LEITURA | 42 | 42 | 6 | 3 | 33 | 633/924 |
| 4 MATEMATICA | 42 | 42 | 11 | 15 | 16 | 580/924 |
| 5 LEITURA | 54 | 53 | 2 | 6 | 45 | 891/1166 |
| 5 MATEMATICA | 54 | 54 | 5 | 14 | 35 | 776/1188 |

As categorias publicadas somam 101% em três escopos: matemática do 3º ano, escola e turma única; leitura do 5º ano, turma B. As contagens originais de categoria somam exatamente os respectivos avaliados em todos os 24 escopos. Não se ajustaram percentuais para forçar soma 100%.

## Arquivos e reprodução futura

Base dos caminhos abaixo: `C:/Users/marce/Downloads/Airam veras/datamining/.superpowers/sdd/implementation-plan/contraprova-preparacao/`.

| Arquivo | SHA256 |
|---|---|
| `coletor_portal.py` | `4bc60d69b62680f2d0f631ddd07670ffffbed66758bf07ddac960fee63ad6396` |
| `hashes-antes.json` | `1b8622f3a9b6f40f5aeedd9090e10fb08049b29c63567690cf5f52e78fbb0a54` |
| `recibo-portal.json` | `c98c796b4a2d6143468d926bfcabf1047447d9ff8a24371bb540e8d6b4f68229` |

Execução final: início `2026-10-22T15:28:53.624681+00:00`, fim `2026-10-22T15:28:53.775681+00:00`, Python 3.12.14. Comando, a partir de `datamining/`:

```powershell
.venv/Scripts/python.exe .superpowers/sdd/implementation-plan/contraprova-preparacao/coletor_portal.py
```

O coletor regrava snapshot e recibo; antes de uma reexecução para integração futura, preservar esta edição caso seja necessária como evidência histórica. O recibo contém, para cada campo confrontado, contexto de fonte/H/turma/escola, numerador, denominador, percentual exato, bruto publicado, precisão, duas regras de arredondamento, diferença racional, distância absoluta e posição no intervalo de quantização. Conserva também contagens agregadas e todos os hashes individuais das fontes. Nenhum registro individual integra essas saídas.

T05 deverá produzir seus próprios testes RED, implementação, GREEN/REFACTOR e mutações, integrar a contraprova a seu contrato e sinalizar explicitamente a discrepância H 13. Esta preparação não testa as futuras funções e não afirma aprovação da tarefa. Escrita/fluência, corte oficial para adequação, validade pedagógica externa, identidade longitudinal e desempenho temporal permanecem fora desta auditoria. Nenhum CSV, ZIP, manifesto, clone, ledger ou arquivo do produto foi alterado; não houve operação Git.
