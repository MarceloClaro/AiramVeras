# Dicionário e handoff T02 → T03

As tabelas são o retorno real de `airam.ingestao.ler_exportacoes(catalogo: list[dict]) -> dict[str, list[dict]]`. O checkpoint é `restrito/t02/tabelas.json`, JSON UTF-8; as sete tabelas também estão separadas nesse diretório. Toda a pasta é ignorada pelo Git. O schema de campos e tipos efetivamente observados está em `docs/esquemas-t02.json`; contagens, hashes e contraprova estão em `evidencias/T02/contraprova.json`. Nenhuma tabela nominal integra o commit.

## Tabelas

| Tabela | Granularidade | Linhas observadas | Vínculo e finalidade |
|---|---|---:|---|
| `matriculas` | escola + ano escolar + turma normalizada + nome normalizado | 172 | `matricula_local_id` é referência transitória, não ID institucional. Nome bruto/normalizado e origens permanecem restritos. |
| `avaliacoes` | matrícula + aplicação/componente + ocorrência na fonte | 640 | `avaliacao_local_id` liga as medidas; categoria original, participação e contexto por aplicação. |
| `habilidades` | aplicação + coluna H original | 4618 | Pares agregados de acertos/itens; não existem itens individuais inferidos. |
| `escrita` | aplicação + Nota ou aspecto original | 864 | Escala de escrita; não representa percentual de acertos. Categoria permanece em `avaliacoes`. |
| `fluencia` | aplicação + uma das quatro tarefas originais | 592 | Quantidades, denominadores, compreensão e percentual de palavras são mantidos com unidades distintas. Perfil em `avaliacoes`. |
| `agregados` | exportação + escola/turma | 44 | Medidas publicadas e participação calculada, com identificadores originais dos agregados. |
| `disponibilidade_arquivos` | combinação ano/componente declarada no manifesto | 20 | Inclui as duas combinações sem exportação. Ausência de arquivo não cria aplicação individual nem nota zero. |

## Proveniência e identidade

`fonte_id`, `sha256`, `caminho`, `linha_fonte`, `exportacao`, `sha256_exportacao`, `manifesto`, `sha256_manifesto`, `avaliacao_id`, `ano_avaliacao`, `ciclo`, `ano_escolar` e `componente` conservam contexto e versão da observação. `linha_fonte` é o número do registro CSV contando cabeçalho como 1; os CSVs atuais não têm registros multilinha. A chave da relação inclui fonte/versão, ano/componente e ocorrência; H 01 de outro contexto não é tratado como a mesma habilidade.

`origem_metadados` distingue `manifesto` de `csv_e_manifesto_conferidos`. `data_exportacao` conserva a coleta declarada; `data_aplicacao` é nula porque não foi informada. Não se deduz data do nome do arquivo. O programa vem da fonte catalogada. `status_original` é preservado na disponibilidade de arquivos.

`origens` de matrícula contém referência de cada aplicação, nome e turma brutos e `coluna_turma_original`, inclusive o alias explícito `Turmma`. A normalização local usa Unicode NFKD, remove marcas diacríticas, converte para maiúsculas e compacta espaços. Só se compartilha cadastro entre componentes pela chave completa; homônimos em turmas diferentes ficam separados. A mesma chave repetida no mesmo componente/aplicação é erro, sem deduplicação silenciosa. Não se afirma identidade longitudinal validada.

T03 deverá criar pseudônimo HMAC com seu contrato próprio e substituir `matricula_local_id` em avaliações e medidas por uma relação auditada. Deve guardar o mapeamento e nomes somente em área restrita. `avaliacao_local_id` deriva da fonte/linha, não de identidade pessoal; serve ao vínculo de medida com aplicação. Campos nominais também existem nas `origens` de matrícula: não exportar o objeto inteiro para saídas públicas.

## Máscaras e medidas

Todas as medidas possuem `bruto`, `valor`, `numerador`, `denominador`, `unidade`, `participacao`, `disponibilidade`, `aplicavel`, `motivo_ausencia`, `percentual`, `percentual_unidade` e `duracao_segundos`. O bruto conserva espaços e marcadores originais; a linha nominal completa permanece no CSV original.

- `participacao`: booleano da flag individual Sim/Não; nulo nos agregados.
- `disponibilidade`: booleano da presença de resultado de campo, independente da flag de participação.
- `aplicavel`: nulo quando a fonte não informa aplicabilidade. Não se transforma hífen em declaração de tarefa não aplicável. A API permite `False` somente por declaração explícita do chamador.
- `motivo_ausencia`: `nao_participacao` quando a flag é Não; `resultado_ausente` para marcador de campo sem causa codificada; `nao_aplicavel` somente se declarado explicitamente. Resultado disponível tem motivo nulo.
- Marcadores vazios, hífen e `sem resultado` conservam valores nulos. Zero numérico de participante é disponível e permanece zero. Texto inválido, denominador zero, contagem negativa ou numerador maior que denominador são erros.

| Unidade | Campos e interpretação |
|---|---|
| `acertos_itens` | H e compreensão; numerador/denominador inteiros da célula. |
| `palavras_total` | Global e possivelmente desconhecidas, no formato quantidade `de` total; não são percentuais. |
| `palavras` | Texto: `valor` é quantidade correta, `percentual` é a porcentagem publicada e `percentual_unidade` é `pontos_percentuais`. Denominador e duração ficam nulos; não se calcula total exato nem palavras/minuto. |
| `nota_escrita` | Nota/aspectos e média publicada; números decimais com ponto, sem conversão para acertos. |
| `percentual` | Agregados de participação/categorias/H, com ou sem `%`; `valor` em pontos percentuais. |
| `contagem` | Previstos/avaliados explícitos e perfis agregados de fluência; não são porcentagens. |

Categorias/perfis originais e brutos ficam em `avaliacoes`: `categoria`, `categoria_bruto`, `campo_categoria_original`; o único alias de perfil é `Pré - leitor` → `Pré-leitor`. Não se fundem subníveis nem se equiparam categorias entre anos/instrumentos.

## Reconciliação e denominadores

`reconciliar_blocos(rows: list[dict]) -> list[dict]` agrupa por `avaliacao_local_id`, rejeita H duplicado, flag divergente e contagens inválidas. Com cobertura completa e participante, devolve `acertos`, `oportunidades`, `taxa=soma(acertos)/soma(itens)`, quantidades de blocos e somas observadas. Com cobertura parcial ou não participante, o total/taxa de prova é nulo; as somas dos blocos disponíveis continuam identificadas como observadas. Totais declarados opcionais (`total_acertos`, `total_oportunidades`) devem coincidir com a soma completa, ou há erro. A API não impõe 22 itens a instrumentos futuros; a contraprova confirma 22 nas 343 aplicações avaliadas de leitura/matemática atuais.

Agregados conservam os campos de medidas e seus rótulos originais em `medidas`, identificadores originais em `campos_identificadores_originais`, além de `cadastros_observados`, `avaliados_observados` e `participacao_calculada` em pontos percentuais. A participação calculada divide avaliados por cadastros observados. `Previstos`/`Avaliados` explícitos são conferidos quando existem. Leitura/matemática não ganham um campo de contagem `Previstos` supostamente original. Percentual publicado arredondado permanece separado; não reconstrói contagens.

Fluência confere total pré-leitor contra subníveis e total das três categorias principais contra avaliados, sem somar total e subníveis em um denominador. Não se espera soma exata de 100% de categorias arredondadas. Médias publicadas são conservadas, sem inferir regras internas de nota.

Somente os CSVs canônicos de `csv_originais/` vinculados ao manifesto prioritário entram na ingestão. Manifesto, ZIPs e CSVs têm hashes revalidados. Cópias catalogadas fora desse conjunto permanecem no catálogo para auditoria. Cada exportação exige exatamente um CSV de escola, turma e estudante. Banco SQLite, CSVs pseudonimizados e CLI completa pertencem à T11.
