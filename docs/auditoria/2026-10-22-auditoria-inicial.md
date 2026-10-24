# Auditoria inicial para o projeto de mineração Airam Veras

Estado: inspeção real de arquivos, contraprovas em memória e diagnóstico do Core; sem implementação do novo pipeline.

## Achados que determinam a especificação

1. O pacote atual tem 18 ZIPs/54 CSVs e somente Ciclo I/2026 comprovado por manifesto da coleta. Escrita/fluência do 1º ano não têm resultados.
2. Há 172 registros de cadastro por ano somado; ausência de ID institucional impede identidade longitudinal forte. O 5º ano tem 54 alunos locais e 53 nomes distintos; a turma distingue o homônimo.
3. As observações de leitura/matemática têm numeradores e denominadores por H; nas provas avaliadas, a soma é 22. A média simples de percentuais H pode divergir em até 10,909 pontos percentuais da taxa por itens.
4. Os históricos usam rótulos assumidos de referência/contraprova. Os notebooks não têm execution_count ou outputs. A posição das células não comprova RED→GREEN executado.
5. Uma condição antiga `len(zero) >= 0` é sempre verdadeira. Testes de pares não conferem integralmente os valores com a origem. Esses casos entram como regressões obrigatórias.
6. O arquivo antigo rotulado matemática do 1º ano contém LP. A nova exportação está correta. O ZIP histórico de resultados com sufixo -1ANO na raiz inclui 1º e 2º anos.
7. O corte observado entre adequados nos dados históricos não é corte oficial do CAEd. Os 80% de acertos correspondem a 18/22, enquanto os mínimos históricos de adequação eram 17/22 e 16/22. As metas são distintas.
8. O mapa CAEd observado contém 124 linhas/93 códigos. Todos constam no PDF; 118 estão na tabela do próprio ano e seis do 5º apenas em tabelas anteriores. Há quatro códigos matemáticos cujos conjuntos BNCC variam por contexto de ano.
9. Vínculos publicados com ressalva semântica devem conservar textos e fontes. O mapa não autoriza equivalência integral, pré-requisitos ou causalidade.
10. A marca de Ciclo I do 3EF16_P na p.7 foi conferida visualmente. A posição é válida dentro da célula, apesar do alinhamento à esquerda.
11. Não foi localizado cluster implementado nos notebooks/pacotes auditados. Cenários binomiais anteriores usam probabilidades hipotéticas não calibradas e devem permanecer cenários.
12. A pasta SAAP contém uma imagem; não há base individual SAAP validada para emparelhamento.

## Contraprovas históricas executadas em memória

Nos 102 registros de avaliação e 1.054 registros aluno–H do ZIP anonimizado antigo, as contagens somadas reconciliam sem divergência. Isso audita o pacote histórico, não confirma identidade longitudinal ou datas reais.

| Medida histórica | 1º ano | 2º ano |
|---|---:|---:|
| Registros da aplicação rotulada contraprova | 24 | 28 |
| Adequados registrados | 10 | 18 |
| Alvo de 80% adequados | 20 | 23 |
| Estudantes com ao menos 18/22 | 9 | 14 |
| Lacuna total até 18/22 para todos | 49 | 106 |
| Pares históricos disponíveis | 24 | 25 |
| Pearson recalculado | 0,1074469869 | 0,5864046712 |
| McNemar exato recalculado | 0,3876953125 | 0,7265625 |

Esses coeficientes pertencem a pares rotulados por um script antigo. Não devem ser apresentados como evolução entre Ciclos I e II ou efeito de intervenção.

## OpenCode Core, chamadas reais

- `ecosystem_integration_status`: configuração conferida; execução/inferência não comprovada.
- `ecosystem_agent_profile(inventory)`: inventário retornou status blocked com 59 cartões rejeitados; existem perfis managed-v1 validados úteis. Não foi tentada correção global ou criação de perfis nesta auditoria.
- `ecosystem_route`: roteamento disponível, mas o primeiro resultado foi uma skill genérica sem capacidades estatísticas declaradas; não foi tratado como seleção especializada válida.
- `ecosystem_text_spec`: contrato textual de auditoria registrado como `TSPEC-fa8267bd`; critérios textuais não entregam software.
- `python3 -m marceloclaro.cli doctor`: código de saída 0; overall degraded, modo structural/installation_only; 21 pass, 1 warn, 0 fail. O aviso refere-se a 78 entradas históricas não modeladas do registro de evolução, preservadas. Diagnóstico não confirma autenticação ou inferência.

## BNCC remoto

A API GitHub confirmou o fork público MarceloClaro/bncc-dados e o commit main `9c268978efa2aa250834c6a9edb6074432752838`, igual ao HEAD do clone local auditado. A comparação de commit não constitui revisão de cada texto curricular; o pipeline deverá preservar fonte e localizador por registro.

## Próximos estados

Especificação em revisão → plano de implementação revisado → incrementos TDD com RED real → GREEN/REFACTOR → contraprova e mutações → artefatos inspecionados → liberação interna com limites explícitos.
