# Matrizes de referência do SPAECE para mineração

**Atualização da coleta:** o catálogo completo e mais recente do portal foi reunido em `../caed-dados/LEIA-ME.md`, incluindo SPAECE 2025, Avalie.CE 2026.1, Avalie.CE 2026.2 e edições anteriores. Este pacote de sete PDFs permanece como acervo anterior; não deve ser tratado como a versão mais recente.

Foram baixadas sete matrizes do portal Avaliação e Monitoramento Ceará / CAEd e extraídos 146 registros de descritores por matriz. O acervo foi consultado nesta tarefa em outubro de 2026. Isso não confirma uma revisão ou vigência normativa específica para a edição de 2026.

| Etapa | Língua Portuguesa | Matemática |
|---|---:|---:|
| 2º ano EF, SPAECE-Alfa | 19 | Não incluída |
| 5º ano EF | 15 | 22 |
| 9º ano EF | 19 | 25 |
| 3ª série EM | 22 | 24 |

## Arquivos

- `dados/descritores.csv`: tabela UTF-8 com BOM e separador ponto e vírgula, para Excel e ferramentas de análise.
- `dados/descritores.json`: os mesmos registros com campos identificados.
- `dados/spaece.sqlite`: tabela `descritores`, com chave composta `(matriz_id, codigo)`.
- `fontes/`: PDFs oficiais baixados e textos extraídos.
- `fontes.json`: URL, nome e SHA256 de cada PDF.
- `validacao.json`: contagens e verificações executadas.
- `extrair.py`: extração reproduzível dos PDFs locais, com pypdf.

Cada registro inclui componente, etapa, ano/série, código, eixo/tópico extraído, subeixo quando presente, descrição, descrição bruta, URL oficial, página e SHA256. As maiúsculas irregulares dos títulos resultam das fontes tipográficas dos PDFs e foram preservadas no campo de extração.

## Fontes e limites

Portal CAEd: https://avaliacaoemonitoramentoceara.caeddigital.net/

Os URLs individuais dos sete PDFs estão em `fontes.json`. A estrutura do SPAECE, incluindo a avaliação de leitura do 2º ano, é descrita pela Seduc: https://paicintegral.seduc.ce.gov.br/spaece/.

Foi localizada também a página oficial "Matrizes de Referência – SPAECE 2024": https://paicintegral.seduc.ce.gov.br/matrizes-de-referencia-spaece-2024-3/. O download vinculado retornou HTTP 403 durante esta coleta. Portanto, não foi usado para confirmar equivalência ou atualização dos PDFs CAEd baixados.

Material formativo complementar de 2026, distinto da matriz completa: https://paicintegral.seduc.ce.gov.br/2026/09/21/cuidaspaece-2026/. Não foi incorporado à tabela de descritores.

Não foi incluída matriz de Matemática do 2º ano nem uma matriz do 1º ano. Materiais Saeb, CNCA, avaliações diagnósticas e orientações pedagógicas não devem receber automaticamente a identificação de matriz SPAECE.

O código D01, isoladamente, não identifica uma habilidade única entre componentes e etapas. Use sempre a chave completa da matriz. Nenhuma correspondência com BNCC ou descritores CAEd locais foi presumida.

## Verificação

Foram conferidos os hashes dos sete PDFs, a preservação da sequência completa de códigos extraídos de cada documento, a ausência de duplicatas por matriz, os campos obrigatórios e a integridade SQLite. A página do SPAECE-Alfa foi renderizada e inspecionada visualmente. Isso verifica a extração e a integridade do pacote, não a vigência em 2026 nem a equivalência curricular.

## Exemplo de consulta

```sql
SELECT codigo, descricao, subeixo, fonte_url, pagina_pdf
FROM descritores
WHERE matriz_id = 'SPAECE_LP_EF_2'
ORDER BY codigo;
```

Para cruzar com BNCC, abra os dois bancos em modo somente leitura. O resultado do cruzamento deve ser uma tabela separada, com justificativa e evidência para cada correspondência.
