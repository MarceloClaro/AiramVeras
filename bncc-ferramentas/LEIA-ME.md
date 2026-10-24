# BNCC para mineração de dados

Instalação local em `C:\Users\marce\Downloads\Airam veras`.

## Componentes instalados

- `bncc-dados/`: clone completo de https://github.com/bncc-dev/bncc-dados.
- `bncc-dados/derivados/bncc.sqlite`: banco SQLite com 1.721 aprendizagens.
- `bncc-dados/derivados/csv/`: tabelas em CSV.
- `bncc-dados/.venv/`: Python com `bncc==0.5.1` e `jsonschema==4.26.0`.
- `bncc-ferramentas/node_modules/`: `@bncc/mcp==0.5.0`, `@bncc/dados==0.7.0` e SDK MCP.
- MCP `bncc-local` registrado no Codex, com execução local por Node e dados embutidos.
- `.codex/agents/`: perfis `bncc_pesquisador`, `bncc_minerador` e `bncc_auditor` no escopo desta pasta.

## Como usar no Codex

Abra uma nova conversa nesta pasta para carregar as novas configurações. Exemplo de solicitação:

> Use o agente bncc_minerador para consultar as habilidades de Língua Portuguesa e Matemática do 1º e 2º anos no banco local. Exporte os resultados para bncc-ferramentas/resultados e peça ao bncc_auditor para conferir contagens e fontes.

Os perfis seguem o formato de agentes personalizados documentado em https://learn.chatgpt.com/docs/agent-configuration/subagents. Herdam o modelo e as permissões da conversa. Foram gravados e validados como TOML; sua execução por modelo não foi testada nesta instalação.

## Verificação executada

- SQLite: integridade OK, nenhuma violação de chave estrangeira.
- Contagens: EI 93; EF 1.304; EM 183; Computação 141.
- Os sete arquivos canônicos passaram na validação JSON Schema. O autoteste rejeitou 10 de 10 corrupções.
- Cliente MCP iniciou o servidor, listou sete ferramentas e consultou estatísticas e EF01LP01, incluindo a página 101 da fonte oficial.
- O commit informado pelo MCP coincide com o clone: `9c268978efa2aa250834c6a9edb6074432752838`.
- O repositório clonado permanece sem alterações rastreadas.

Evidências: `instalacao.json` e `verificacao-mcp.json` (sequência de respostas JSON do teste). O pipeline completo de reextração dos PDFs não foi executado.

## Consulta SQL inicial

```sql
SELECT h.codigo, h.texto, h.componente, a.ano
FROM habilidade_ef h
JOIN habilidade_ef_ano a ON a.codigo = h.codigo
WHERE h.componente IN ('ef-comp-lp', 'ef-comp-ma')
  AND a.ano IN (1, 2)
ORDER BY a.ano, h.componente, h.codigo;
```

Abra o banco em modo somente leitura. Preserve os arquivos canônicos e grave análises na pasta `resultados/`. Cruzamentos com CAEd precisam de correspondências documentadas entre descritores e habilidades; similaridade textual não estabelece equivalência.

Dados: atribuição ao projeto bncc.dev / Profy, conforme `bncc-dados/dados/LICENSE.md` e `bncc-dados/CITATION.cff`.
