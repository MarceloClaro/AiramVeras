# Matrizes CAEd do portal Ceará

Coleta completa da seção **Sistema de Avaliação > Matrizes de Referência** do portal https://avaliacaoemonitoramentoceara.caeddigital.net/#!/sistema, consultada em outubro de 2026.

## Cobertura

Foram baixados todos os sete links exibidos nessa seção: seis PDFs atuais e o ZIP de edições anteriores. O ZIP contém 48 PDFs, totalizando **54 documentos e 143 páginas**. Todos foram processados, com **2.388 registros em 129 matrizes**, diferenciadas por documento/edição, etapa, ano/série e tipo de instrumento.

Os 2.388 registros são ocorrências de descritores nas matrizes, não 2.388 habilidades distintas. Repetições entre anos e edições são preservadas.

| Grupo disponibilizado pelo portal | PDFs | Registros |
|---|---:|---:|
| Avalie.CE 2026.2 | 2 | 161 |
| Avalie.CE 2026.1 | 2 | 137 |
| SPAECE 2025, avaliação somativa | 2 | 268 |
| Edições anteriores | 48 | 1.822 |
| Total | 54 | 2.388 |

O histórico abrange 2017, 2018, 2019, 2022, 2023, 2024 e 2025. Não foram presumidas edições nos anos ausentes do ZIP. O recorte de 2026 contém 298 registros de Língua Portuguesa e Matemática para 2º, 4º, 5º, 8º e 9º anos do Ensino Fundamental.

## Arquivos para uso

- `dados/descritores.csv` e `dados/descritores.json`: base consolidada.
- `dados/descritores_2026.csv` e `dados/descritores_2026.json`: recorte das edições 2026.1 e 2026.2.
- `dados/caed.sqlite`: tabelas `descritores`, `documentos` e `paginas`.
- `dados/catalogo_documentos.csv` e `.json`: identificação dos 54 PDFs, edição anual, páginas, URL, membro do ZIP e SHA256.
- `dados/paginas_extraidas.json`: texto integral extraído por página, para conferência.
- `fontes/`: PDFs e ZIP originais. `fontes.json` registra os sete downloads oficiais.
- `validacao.json`: relatório de integridade e conferência de códigos por página.
- `extrair_portal.py`: procedimento reproduzível de extração a partir dos PDFs locais; depende de `pypdf` e `pdfplumber`.

Os CSVs usam UTF-8 com BOM e separador ponto e vírgula.

## Campos e interpretação

Use `matriz_id + codigo` como chave. O código isolado não identifica uma habilidade entre diferentes componentes, anos ou edições. A etapa e o ano/série vêm do cabeçalho da matriz, não do sufixo do código.

Cada registro conserva descrição, texto bruto da linha, eixo/tópico quando disponível, página, caminho da fonte, URL e SHA256. O ano da edição é o da publicação/pasta do portal, não uma declaração de vigência atual.

As matrizes diagnósticas de 2022 apresentam correspondências em duas colunas. Elas foram mantidas nos campos `codigo_relacionado_publicado` e `descricao_relacionada_publicada`, sem inferir novos vínculos. Os itens de resposta construída são identificados separadamente dos demais.

A descrição recebe apenas normalização de espaços e a correção de artefato de extração `T eorema` para `Teorema`. Os títulos de eixos preservam a capitalização extraída, que pode ser irregular devido às fontes tipográficas.

## Verificações executadas

- Todos os sete links do catálogo baixados; 48 PDFs do ZIP e seis PDFs atuais incluídos.
- SHA256 dos 54 PDFs conferido e componente comparado com o cabeçalho de cada documento.
- Códigos extraídos por ordem textual comparados com os códigos na primeira coluna por posição na página: 143 páginas conferidas.
- Descrições obrigatórias preenchidas, chave composta sem duplicatas, documentos referenciados existentes e integridade SQLite aprovada.
- Primeira página de Matemática do Avalie.CE 2026.2 renderizada e inspecionada visualmente.

Essa validação verifica a cobertura do catálogo e a extração; não constitui validação pedagógica de equivalências ou revisão visual integral das 143 páginas.

## Relação com os arquivos anteriores

O pacote `spaece-dados` entregue anteriormente contém sete matrizes do acervo antigo, obtidas por outros URLs. O catálogo atual inclui versões mais recentes, especialmente SPAECE 2025 e Avalie.CE 2026. Prefira esta base consolidada e selecione explicitamente a edição pretendida.

A matriz CNCA local `MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf` é de outro programa e não aparece nos sete links dessa seção do portal. Ela não foi incorporada nem confundida com o catálogo Ceará. Também não foram incorporados resultados individuais de alunos.

## Consultas

```sql
-- As duas edições de 2026, preservando a identificação da fonte.
SELECT fonte_arquivo, componente, ano_serie, codigo, descricao, pagina_pdf
FROM descritores
WHERE ano_edicao = 2026
ORDER BY fonte_arquivo, ano_serie, codigo;

-- Uma edição específica: Avalie.CE 2026.2, 2º ano.
SELECT componente, codigo, descricao, pagina_pdf
FROM descritores
WHERE fonte_arquivo LIKE '%2026.2%' AND ano_serie = 2 AND etapa = 'EF';
```

Créditos: documentos publicados pelo portal de Avaliação e Monitoramento da Educação do Ceará, SEDUC-CE / CAEd-UFJF. A coleta não altera os direitos dos documentos originais.
