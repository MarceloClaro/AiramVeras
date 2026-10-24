# Dicionário T04: currículo contextual para T05/T07

Interface pública versionada: `curriculo/t04/checkpoint.json`, `versao_schema=airam-curriculo-t04-v1`, SHA256 **`a4a73d2523d459d0dda102f6e4b6f14176be444717f428bb6d1772822ffd5796`**. `docs/esquema-t04.json` descreve o formato observado por JSON Schema 2020-12. O checkpoint não contém nomes, pseudônimos, turmas, resultados ou medidas de participantes. Fontes originais e clone BNCC permaneceram intactos.

## Interfaces executáveis

- `airam.matriz_cnca.extrair_ocorrencias(pdf: Path) -> list[dict]`: perfil específico do PDF de SHA fixo abaixo. Descobre colunas nos retângulos vetoriais do cabeçalho e limites de cada linha nas arestas da célula CAEd. Descritor, BNCC e marcas X são lidos exclusivamente na célula correspondente. Continuações herdam somente blocos documentais explicitamente auditados. Outro PDF/hash exige novo perfil; é recusado.
- `airam.bncc.carregar_bncc(root: Path, expected_commit: str) -> dict[str,dict]`: consome exclusivamente `dados/bncc-2018/ensino-fundamental.json` no commit fixado. Confere arquivo contra o blob Git, admitindo apenas conversão CRLF/LF; rejeita alteração ou commit divergente. Filtra `vigencia.status=vigente`, mantém textos/campos normativos e acrescenta `proveniencia_dataset` com commit e hashes.
- `airam.vinculos.vincular_posicoes(posicoes, ocorrencias, bncc) -> list[dict]`: devolve arestas por posição/ocorrência/BNCC. Não modifica entradas, não transporta medidas individuais nem deduz ano avaliado pelo prefixo CAEd. Rejeita posição contextual, ocorrência ou código BNCC da mesma célula duplicados.

Reprodução real: `.venv/Scripts/python.exe evidencias/T04/executar.py <rotulo-novo> ANALISE evidencias/T04/analisar_fontes_reais.py`. Cada rótulo é exclusivo e preserva snapshot anterior, saída e exit code. O script autentica o T03 antes da leitura local e publica somente cardinalidades de cobertura; não imprime registros individuais.

## Tabelas do checkpoint

| Campo | Conteúdo e chave |
|---|---|
| `fontes` | PDF, mapa público, canônico BNCC e hash do checkpoint restrito T03; não contém registros T03. |
| `politica` | Recorte contextual, pesos documentais, limites semânticos, geometria e prevenção de multiplicação. |
| `contagens` | Cardinalidades calculadas pela execução real, não tabelas preenchidas por constantes. |
| `posicoes` | 124 posições públicas. Chave lógica: `(avaliacao_id, ano_avaliacao, ciclo, ano_escolar, componente, posicao, fonte_posicao, versao_posicao)`. `codigo_caed_observado` é atributo observado, não a posição H. |
| `ocorrencias_matriz` | 202 linhas: `ocorrencia_id` inclui SHA PDF, página, limite superior e CAEd. Inclui `ano_tabela`, componente, descritor, BNCC, ciclos, células, caixas das marcas, UT matemática e nota de integração. |
| `bncc` | 81 habilidades vigentes presentes nas 202 ocorrências, por código canônico. Inclui texto, organização, objetos, vigência e fonte canônicos sem reescrita. |
| `vinculos_posicoes` | 157 arestas, chave `vinculo_id`: SHA256 do JSON compacto `[posicao_id, ocorrencia_id, codigo_bncc]`. A posição é SHA256 do JSON compacto UTF-8 da chave lógica acima, nessa ordem. |

`ano_avaliacao=2026` designa edição; `ano_avaliado`/`ano_escolar` designa série avaliada; `ano_tabela` designa série da tabela do PDF; prefixo CAEd é apenas parte do código. São dimensões distintas. O ciclo `I` e a edição foram declarados pelo contexto do mapa Ciclo I 2026, registrado em `fontes.mapa.contexto_declarado`. As posições não foram extraídas de dados nominais.

As caixas `celulas` e `marcas_ciclo[].bbox` usam pontos PDF, `(x0, top, x1, bottom)`, origem superior esquerda. `texto_caed` compacta somente espaços/quebras; `texto_caed_celula` conserva as linhas extraídas. `bncc_celula` mantém o texto da célula e `codigos_bncc` preserva sua ordem. `nota_integracao` contém texto e página reais da nota do bloco, propagados explicitamente às ocorrências desse bloco. Não atribui aplicabilidade individual ao 5º ano.

## Estados e consumo analítico

| Campo/estado | Interpretação |
|---|---|
| `status_contextual=proprio_ano_ciclo_confirmado` | Ocorrência da tabela do próprio ano com marca do ciclo avaliado; 118 posições. |
| `fonte_anterior_integracao_a_confirmar` | Não há ocorrência do próprio ano; conserva todos os candidatos anteriores e seus localizadores; seis posições, 11 arestas. Peso zero. |
| `ciclo_nao_assinalado` | Ocorrência do próprio ano sem marca do ciclo pedido; mantém publicação, peso zero. Não ocorre nesta base. |
| `sem_ocorrencia_contextual` | Posição preservada com campos de ocorrência nulos, peso zero. Não ocorre nesta base. |
| `status_bncc=confirmado` | Código existe no conjunto recebido e está vigente; todos os 157 vínculos reais. |
| `status_bncc=nao_confirmado` | Código ausente/inativo; não há substituição por similaridade; peso zero. |
| `status_semantico=associacao_publicada_com_ressalva_semantica` | Diferença semântica documentada: ambos os textos e associação oficial são mantidos; nove posições nesta base. |
| `associacao_publicada_sem_equivalencia_integral` | Associação publicada sem ressalva específica cadastrada; não certifica equivalência integral. |

As seis posições ressalvadas são do 5º ano: `3EF09_P`, `3EF15_P`, `4EF10_P`, `3EF11_M`, `3EF12_M`, `3EF17_M`. O primeiro tem fontes 3º/4º anos, assim como os demais salvo `4EF10_P`, que tem apenas 4º ano. Não existem ocorrências inventadas em tabela do 5º ano.

`peso_analitico` reparte unidade entre arestas vigentes do próprio ano e ciclo confirmado, por `posicao_id`; demais arestas têm peso zero. Esta é normalização de associação publicada, não pontuação de domínio BNCC. As ressalvas semânticas permanecem explícitas mesmo quando a associação documental recebe peso. Uma política pedagógica que as exclua deve recalcular pesos e cobertura, registrando sua decisão.

T05 deve manter resultados CAEd originais por avaliação/ano/componente/posição e usar cobertura curricular como metadado. T07 deve agregar cada observação uma vez por posição antes de expandir relações; nunca somar resultados repetidos por aresta ou tratar candidatos de integração como evidência confirmada. Posição H01 em anos/componentes/avaliações/fontes diferentes não é a mesma variável. Dados pessoais T03 permanecem em `restrito/`.

Há 131 CAEd nas 202 ocorrências e 93 CAEd nas 124 posições. A união de todos os contextos dos códigos observados tem 73 BNCC. A política contextual implementada também retornou 73 nesta execução, por cálculo independente; o programa não impõe igualdade desses totais nem o número 73. Todas as ocorrências, incluindo códigos não exportados, cobrem 81 BNCC. Quatro CAEd variam por ano: `3EF06_M`, `3EF07_M`, `3EF09_M`, `4EF07_M`; nunca unir seus conjuntos entre anos para preencher uma posição individual.

## Proveniência e validação

| Entrada | Versão/hash SHA256 |
|---|---|
| Matriz MEC PDF | `2728d640c98510ff323cb542282ffc51db8288c021560aa55cac7b908c5f5f0e` |
| Mapa público de posições | `da6c780f03b37653996436140c29fde8284c96a72666713089ca0d3e7b192648` |
| T03 restrito | `b26bef93117c7c38906cd9e6e025cfc5f2a9969cc4834e4b785618d29dd56dbb` |
| BNCC commit | `9c268978efa2aa250834c6a9edb6074432752838` |
| BNCC arquivo local | `2bb775102aed7342842e7f87e2024db915d2fca6277f9016828e5053cbc77cd3` |
| BNCC blob Git | `bdc84d6bb6f4b38ca1331b0319cb04ea8f9240d076d3097928124c0b9ba38c0b` |

O hash local difere do blob pela conversão de finais de linha do checkout Windows; o carregador confere os bytes normalizados. A fonte BNCC fornece localizador de planilha e `localizador_pdf` textual canônico, distinto de `pagina_matriz` MEC. Exemplo: `EF01LP02` aponta para página PDF BNCC 101, enquanto a associação `1EF10_P` está na página MEC 4.

`evidencias/T04/` registra T26–T31, RED real, GREEN focal/integral, quatro mutações detectadas, análise real e auditoria sem chamadas às APIs produtoras, com leitura independente por pypdf das 17 páginas. A marca deslocada da página 7 foi inspecionada visualmente, assim como as páginas matemáticas 23, 25 e 27. A conferência T03 cobre 4.618 medidas H/124 posições, sem lacunas. Validação documental/computacional local; não houve inferência Core, validação pedagógica externa, confirmação das seis integrações ou demonstração de domínio individual BNCC.
