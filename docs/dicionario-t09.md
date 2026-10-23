# T09 → próximas etapas: cenários condicionais e gate temporal

Versões: `airam-cenarios-t09-v1` (agregado) e `airam-cenarios-restritos-t09-v1` (individual local). Os contratos de estrutura estão em `docs/esquema-t09.json` e `docs/esquema-restrito-t09.json`. Esta entrega consome os checkpoints T05 sem alterar a observação original.

## Entradas e saídas autenticadas

| Caminho | SHA256 | Uso |
| --- | --- | --- |
| `estatistica/t05/checkpoint.json` | `5bfa87b38394d171589a7799751127dceb7d81587bbbfcefa67d2bb4a8420231` | Categorias agregadas de referência; 24 escopos de Meta A. |
| `restrito/t05/checkpoint.json` | `6e6090bee2bd483822a75aa1c18f9599953d353dfaac8e28cf7b0983a6bdb95b` | Avaliações e medidas individuais locais. Ignorado pelo Git. |
| `config/cenarios.json` | `2d66c04bee5d495a4a1250ea1bc83f731255e5437a2a15f4905d4af14d56f95b` | Hipóteses fixadas antes da execução real. |
| `estatistica/t09/checkpoint.json` | `150592d325fde9c80bfd98717a974b3a53e816987601b1b3968168e558f14339` | Cenários e sensibilidade agregados; sem chaves individuais. |
| `restrito/t09/checkpoint.json` | `0e8359f648e3a4a01dce2a817d2fb7fb5397b31752a83c04ca2082f37cbc0901` | Distâncias e resultados individuais, somente local e ignorado pelo Git. |

Esses hashes identificam o checkpoint produzido em `analise02`; qualquer nova execução deve gerar recibo e versão próprios. O diretório `restrito/` é ignorado pelo Git, mas seu nome não certifica controle de acesso do sistema de arquivos. O agregado é para revisão local; eventual compartilhamento depende da política institucional.

## Interfaces e interpretação

`projetar_cenario(observacoes: list[dict], metas: dict, hipoteses: dict) -> dict` recebe um escopo homogêneo e as metas A/B separadas. Devolve `tipo_resultado=cenario_condicional`, premissas, unidades, comparabilidade, status de validação, Meta A e uma linha de Meta B por observação na mesma ordem. As linhas de Meta B pertencem exclusivamente ao checkpoint restrito quando ligadas a aplicações reais.

Na Meta A, `avaliados` exclui não participantes; `adequados` conta apenas a categoria CAEd original `Adequado`; `alvo=teto(0,8×avaliados)`; `conversoes=max(0,alvo−adequados)`. `entradas` e `saidas` são mudanças hipotéticas de categoria entre a mesma população avaliada, limitadas respectivamente por não adequados e adequados originais. `adequados_projetados=adequados+entradas−saidas`; `entradas_minimas_com_perdas` condiciona o número de entradas às saídas assumidas; `fracao_projetada` conserva numerador e denominador. Turma e escola se sobrepõem: não somar as linhas como pessoas distintas nem somar alvos arredondados por turma para derivar o alvo escolar. Sem avaliados, alvo, conversões e status de atingimento ficam nulos.

A Meta B é individual: para uma prova válida, `alvo=teto(0,8×oportunidades)` e `lacuna=max(0,alvo−acertos)`. Nos instrumentos atuais de leitura e matemática com 22 itens, o alvo é 18. `ganho` e `perda` são hipóteses inteiras não negativas de deslocamento líquido dos acertos; `acertos_projetados` satura em `[0,oportunidades]`. `deslocamento_bruto` e `deslocamento_realizado` distinguem a hipótese da saturação. Ausência de prova permanece `prova_ausente` com valores projetados nulos; zero realmente observado permanece zero. `atingiram_projetado` no agregado é contagem descritiva das linhas individuais condicionais, não a formulação da Meta B como porcentagem de alunos. Não há probabilidades calibradas, eficácia causal ou quantidade de aulas inferida.

`acertos_ate_adequacao` da Meta A permanece nulo: não existe regra oficial auditada de acertos para mudança de nível na base. `distancia_adequacao_condicional` da Meta B só aparece quando o consumidor fornece explicitamente um corte com `status=hipotese_nao_oficial` e referência não vazia; a configuração executada não fornece tal corte. Um rótulo de regra oficial sem o documento e sem auditoria é recusado. Acertos projetados não alteram automaticamente categorias CAEd originais.

Escrita e fluência continuam em suas unidades, medidas e categorias próprias, com `meta_A_status=unidade_nao_aplicavel` e `meta_B_status=unidade_nao_aplicavel`. Não são convertidas em prova de 22 itens. O checkpoint público resume disponibilidade e categorias; o restrito conserva as observações e medidas originais.

`avaliar_prontidao_temporal(avaliacoes: list[dict], vinculos: list[dict]) -> dict` devolve um gate documental sem dados individuais. `prontidao_inputs_temporais` testa presença coerente de ciclos e datas de aplicação comprovados, comparabilidade, identidade longitudinal, partição temporal sem estudante em treino e teste, prevenção de vazamento, processamento ajustado no treino e desfecho futuro. Evidências declaradas com referência e hash exigem auditoria documental posterior. `previsao_temporal_validada` fica **falsa mesmo se os inputs estiverem prontos**, pois esta tarefa não treina, calibra nem valida modelo. Na base atual de apenas Ciclo I 2026, ambas as flags são falsas, com motivos; `cenarios_disponiveis` é verdadeiro.

## Forma do handoff

O público contém 96 linhas em `cenarios` (24 escopos × quatro hipóteses), 96 linhas de `sensibilidade_meta_A` (24 × quatro quantidades de saídas) e resumos escolares de escrita/fluência. O restrito contém 1.376 linhas individuais de leitura/matemática (apenas escopos escolares, sem duplicação por turma) e 296 aplicações de escrita/fluência preservadas. Estes números são conferidos em `evidencias/T09/analise-real-resultado.json`. A contraprova independente em `evidencias/T09/contraprova-resultado.json` conferiu 192 valores de Meta A, 1.376 de Meta B, 96 resumos e 296 aplicações sem divergência, conforme seu recibo. Ela não estabelece validação pedagógica ou temporal.

Para consumir: verificar SHA256, carregar o schema correspondente, manter o individual em área restrita, e tratar `status_validacao`, premissas e `limites` como parte do dado. Os campos de previsão indicam disponibilidade documental e validação de modelo separadamente. Não usar datas de exportação nem pseudônimos locais como prova de data de aplicação ou identidade longitudinal.
