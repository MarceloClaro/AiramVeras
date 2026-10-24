# Resultados CAEd / CNCA: Ciclo I de 2026, 1º ao 5º ano

Escola: AIRAM VERAS ESC CID, código 23084995, rede municipal.

Foram realizadas novas exportações pelo portal Criança Alfabetizada em 22/10/2026, com a avaliação **Ciclo I / 2026**, identificador **AV12026**.

| Ano | Leitura | Matemática | Escrita | Fluência |
|---|---|---|---|---|
| 1º | Baixado | Baixado | Sem resultado no portal | Sem resultado no portal |
| 2º | Baixado | Baixado | Baixado | Baixado |
| 3º | Baixado | Baixado | Baixado | Baixado |
| 4º | Baixado | Baixado | Baixado | Baixado |
| 5º | Baixado | Baixado | Baixado | Baixado |

## Conteúdo

- `originais/`: 18 ZIPs efetivamente baixados, identificados por ano e componente, com arquivos de escola, turma e estudante.
- `csv_originais/`: os 54 CSVs extraídos, preservando seus bytes e nomes originais, em subpastas por exportação.
- `manifesto_coleta.json`: filtros observados no navegador, avaliação, rede, ano, componente, URL e SHA256 de cada ZIP.
- `conferencia/validacao_arquivos.json`: CRC, SHA256, integrantes, contagens, colunas e metadados conferidos, sem reproduzir nomes individuais no relatório.
- `conferencia/mapa_posicao_codigo_caed.csv`: posições H 01 etc. associadas aos códigos exibidos no portal para leitura e matemática. Os percentuais vêm do CSV original da escola.

O mapa é uma transcrição da correspondência exibida pelo próprio portal; não é uma equivalência inferida com BNCC ou SPAECE.

## Conferência e limites

Os 18 ZIPs passaram na verificação CRC. Ano escolar e componente foram comparados com os campos internos quando disponíveis; a escola foi conferida pelo nome/código. As extrações preservam os originais, incluindo rótulos e erros tipográficos da plataforma.

Os CSVs não registram o ciclo da avaliação. Os formatos de escrita e fluência também não registram ano escolar nem componente. Por isso esses atributos devem ser consultados no manifesto da coleta, que documenta a seleção observada na interface. Não deduza o ciclo pela data de atualização da base.

Os dois casos sem resultados no 1º ano foram conferidos na interface e registrados no manifesto. Isso não significa desempenho zero.

O ZIP de matemática do 1º ano foi exportado novamente e teve o componente conferido, corrigindo a ambiguidade de um arquivo antigo que estava rotulado como matemática, mas continha Língua Portuguesa.

Este pacote contém dados individuais de estudantes e deve permanecer com acesso restrito à equipe autorizada.
