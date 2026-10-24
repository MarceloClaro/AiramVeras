# AiramVeras

Repositório do projeto: [MarceloClaro/AiramVeras](https://github.com/MarceloClaro/AiramVeras).

Especificação: [SPEC-AIRAM-001](specs/SPEC-AIRAM-001.md). As etapas 1 a 9 estão concluídas e revisadas; relatório, planilha nominal, CLI e liberação final estão em implementação.

Os dados individuais e as planilhas nominais permanecem em armazenamento local ignorado pelo Git. O conjunto BNCC continua registrado como fonte curricular com versão fixada.

## Registro inicial da Tarefa 1

Tarefa 1: catálogo local de fontes e contrato de recibos. A Tarefa 1 não calcula resultados escolares, não realiza inferência e não estabelece identidade longitudinal.

Use Python 3.11 ou posterior. O ambiente verificado está descrito em `evidencias/T01/ambiente.json`; `requirements.in` declara dependências do pipeline e `requirements.lock.txt` fixa a instalação verificada no Windows/Python 3.12.14. As funções da Tarefa 1 usam a biblioteca padrão.

```powershell
.venv/Scripts/python.exe -m pip install -r requirements.lock.txt
.venv/Scripts/python.exe -m pytest
.venv/Scripts/python.exe evidencias/T01/validar_fontes_reais.py
```

As interfaces públicas são `airam.catalogo.catalogar(root: Path) -> list[dict]`, `airam.catalogo.validar_fonte(path: Path, expected_sha256: str, allowed_root: Path) -> None` e `airam.recibos.gravar_recibo(path: Path, payload: dict) -> str`. A última retorna o hash dos bytes JSON gravados, após validar o schema e realizar substituição atômica.

`config/analise.json` preserva as duas metas independentes e os aliases dos caminhos existentes. `raiz_fontes` é relativa à raiz deste projeto no script de validação; a API recebe a raiz explicitamente. A variável `AIRAM_CONFIG` permite usar outra configuração, sem editar funções nem embutir um caminho da máquina. O catálogo exclui dependências, repositórios internos e saídas deste projeto; inclui os arquivos físicos das fontes e os metadados necessários à proveniência. Não extrai ZIPs. Mantém PDF sem proveniência como documental não comparável e ZIP histórico sem manifesto como histórico não comparável.

O ciclo não é deduzido de nomes de arquivos ou rótulos históricos. Um manifesto deve confirmar arquivo e SHA256; arquivos extraídos podem herdar contexto apenas quando seu conteúdo coincide com um membro do ZIP verificado. Contextos ambíguos causam erro. Incompatibilidade entre componente declarado e conteúdo ganha status próprio e `apta_para_mistura=false`. Programa, data de exportação e licença desconhecidos permanecem nulos ou não declarados.

O catálogo gerado em `catalogo/fontes.json` é local e ignorado pelo Git. O checkpoint para o próximo incremento contém seu hash em `evidencias/T01/fontes-recibo.json`; a contraprova independente usa `hashlib.file_digest`, comparando inventários antes/depois e cada hash publicado. O catálogo contém caminhos e metadados de arquivos, não linhas de estudantes. Recibos aceitam somente campos de execução e rejeitam campos arbitrários, inclusive tabelas nominais; quem os produz deve manter texto livre, comandos e caminhos minimizados. A validação do schema não é um classificador universal de dados pessoais em texto livre.

Cada recibo de teste exige incremento, requisitos, testes, estado, comando, timestamp com fuso, código de saída, hashes de código/dados, versões, mutação (ou nulo), artefatos e limites. O mapa `versoes` aceita identificadores com letras/números, ponto, hífen e sublinhado, associados somente a texto não vazio; listas, dicionários e outros valores não são aceitos. RED exige saída diferente de zero; GREEN/REFACTOR exigem saída zero. A presença de um recibo verifica rastreabilidade estrutural; não certifica a veracidade de um comando não executado pelo chamador nem substitui a inspeção dos logs. Os recibos deste incremento derivam de subprocessos reais capturados.

Os perfis Core configurados não representam a execução Codex. Fontes e nomes individuais não são enviados a serviços. Validação computacional e documental local não constitui validação pedagógica externa.
