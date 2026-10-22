# Dicionário e checkpoint T03 → T04/T05

Entrada autenticada: `restrito/t02/tabelas.json`, SHA256 `82a24045cb75d85eeefd4394a73cb0dcec37dbbd8a542350fb04d7da0653d9f5`.

Saída principal: **`restrito/t03/tabelas.json`**, SHA256 **`b26bef93117c7c38906cd9e6e025cfc5f2a9969cc4834e4b785618d29dd56dbb`**. As sete tabelas e suas medidas conservam os contratos T02 (`docs/dicionario-t02.md`), com a substituição de `matricula_local_id` por `aluno_local_id` em avaliações e medidas. `qualidade_vinculo` foi acrescentada a essas linhas. `avaliacao_local_id` continua ligando a aplicação a suas medidas. O schema observado está em `docs/esquemas-t03.json`.

Contagens: 172 matrículas, 640 avaliações, 4618 H, 864 medidas de escrita, 592 tarefas de fluência, 44 agregados e 20 registros de disponibilidade. Agregados e disponibilidade permanecem integralmente iguais à entrada. Valores, brutos, máscaras, categorias, fontes, hashes e números de linha foram comparados integralmente à entrada; brutos foram confrontados com os CSVs originais autenticados por hash.

## Interfaces e segredo

`vincular_localmente(matriculas: list[dict], secret: bytes) -> tuple[list[dict], list[dict]]`: primeiro retorno contém somente `aluno_local_id`, `escola_codigo`, `ano_escolar`, `turma`, `qualidade_vinculo` e `origens` sem nomes. O segundo contém cópia da matrícula nominal e a relação explícita `matricula_local_id` → `aluno_local_id`. Nomes brutos/normalizados, inclusive os das origens, ficam somente nesse mapa restrito. A entrada não é modificada. Duplicata da chave normalizada ou da referência antiga bloqueia a operação.

`carregar_ou_criar_segredo(path: Path) -> bytes`: cria chave aleatória de 32 bytes com criação exclusiva e a reutiliza. Chave existente inválida é erro e não é substituída. Na execução real, fica em `~/.airam-local/secrets/spec001-hmac.key`, fora do repositório. O conteúdo e o hash do segredo não integram logs ou recibos. Mode 0600 é aplicado onde suportado; isto não certifica ACLs Windows. Perder ou trocar a chave rompe a estabilidade dos pseudônimos: preservar chave e mapa de forma restrita.

`pseudonimizar_tabelas(tabelas: dict[str, list[dict]], secret: bytes) -> tuple[dict, list[dict]]`: integra as sete tabelas T02, valida bijeção das referências e integridade matrícula/aplicação/medida, substitui referências e rejeita campos nominais inesperados, inclusive aninhados. O primeiro retorno continua sendo dado pessoal pseudonimizado; permanece em `restrito/`, ignorado pelo Git. Não há exportação pública de registros individuais.

## Chave e alcance

O HMAC-SHA256 recebe JSON UTF-8 sem espaços, nesta ordem: `["airam-local-v1", escola_normalizada, ano_escolar, turma_normalizada, nome_normalizado]`. Escola, turma e nome usam NFKD sem diacríticos, maiúsculas e espaços compactados; nome normalizado é recalculado do bruto. O ano escolar é inteiro e significa série, não ano de aplicação. A referência transitória T02 não integra o HMAC. O segredo é específico desta base local. Não se deve reutilizar automaticamente esta identidade para novas coletas sem revisão do contrato.

`qualidade_vinculo` é sempre `local_provisorio_sem_id_institucional`. A normalização facilita ligação entre componentes, mas não prova identidade civil ou institucional, nem identifica transferências/mudanças de turma. Homônimos em turmas diferentes ficam separados; homônimo ou duplicata na mesma chave é conflito bloqueante. Nenhuma identidade longitudinal foi validada. Datas de aplicação continuam nulas; rótulos antigos de referência/contraprova permanecem presumidos, sem reconstrução de temporalidade.

## Pareamento

`parear_componentes(rows: list[dict], esquerda: str, direita: str) -> tuple[list[dict], list[dict]]` recebe avaliações pseudonimizadas. A chave é `(aluno_local_id, avaliacao_id, ano_avaliacao, ciclo, ano_escolar)`, com todos os campos obrigatórios. Componentes distintos são informados exatamente como nas fontes atuais: `LEITURA`, `MATEMATICA`, `ESCRITA`, `FLUENCIA`. Cada lado conserva integralmente seu contexto de fonte, versão/hash, componente e ocorrência. Versões concorrentes na mesma chave/lado são conflito bloqueante; não ocorre deduplicação nem produto cartesiano.

O primeiro retorno contém `aluno_local_id`, `qualidade_vinculo`, `esquerda` e `direita`; cada lado é uma cópia integral da avaliação. O segundo contém somente registros dos dois componentes pedidos sem contraparte, com `lado`, `motivo` e `registro`. Motivos: `componente_direito_ausente` ou `componente_esquerdo_ausente`. Outros componentes ficam fora do universo da consulta. Não pareados e seus motivos ficam no checkpoint restrito `restrito/t03/pareamentos.json`.

São **pares cadastrais**: não participantes permanecem com suas máscaras e resultados nulos. O número analítico deve ser calculado posteriormente com participação e disponibilidade das medidas escolhidas, dentro do ano/instrumento comparável. Não misturar séries nem converter escrita/fluência em taxa de acertos. A existência de um par cadastral não demonstra comparabilidade dos instrumentos ou validade de correlação.

| Consulta | Pares cadastrais | Não pareados | Ambos participantes | Ambos com taxa disponível |
|---|---:|---:|---:|---:|
| LEITURA–MATEMATICA | 172 | 0 | 171 | 171 |
| ESCRITA–FLUENCIA | 148 | 0 | 145 | 0 |
| ESCRITA–LEITURA | 148 | 24 | 145 | 0 |
| ESCRITA–MATEMATICA | 148 | 24 | 145 | 0 |
| FLUENCIA–LEITURA | 148 | 24 | 146 | 0 |
| FLUENCIA–MATEMATICA | 148 | 24 | 146 | 0 |

As 24 lacunas são cadastros do 1º ano sem arquivo do componente esquerdo nessas consultas. Taxa ausente em escrita/fluência não significa desempenho zero. A coluna de taxas somente informa disponibilidade do campo T02; não define uma análise para escrita/fluência.

`auditar_pareamento(rows, pares, nao_pareados, esquerda, direita) -> dict` recebe referência independente do pareador. Compara valores e proveniência completos por multiconjuntos, além de chave, exclusividade, cobertura e motivos; não chama `parear_componentes`. Detecta adulteração mesmo quando todos os IDs continuam iguais. A referência também precisa ser autenticada: a execução real parte do T02 de hash fixo, confronta seus brutos com os CSVs e só depois audita os pares. Os testes sintéticos T38 não certificam cronologia nem resultados históricos externos.

## Evidências e limites

`evidencias/T03/` contém RED/GREEN, snapshots anteriores às execuções, mutações funcionais, contraprova e cobertura agregada. Não contém nomes nem pseudônimos. O mapa nominal e os pares individuais ficam exclusivamente em `restrito/t03/`; o recibo publica apenas seus hashes. Código executado pelo Codex; não houve inferência comprovada do Core. A validação é documental/computacional local, sem validação pedagógica externa, inferência causal, modelo treinado ou previsão temporal.
