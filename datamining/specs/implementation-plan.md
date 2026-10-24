# Airam Veras Datamining Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** entregar uma análise pedagógica reproduzível dos resultados reais CAEd/CNCA do 1º ao 5º ano, com duas metas independentes, vínculo documental BNCC, contraprova, correlações, grupos e cenários rastreáveis.

**Architecture:** pipeline local com fontes imutáveis, tabelas normalizadas, vinculação individual provisória explicitada e banco SQLite. Cálculos observados, vínculos publicados, propagação em grafo e cenários permanecem identificados em campos distintos. O Core coordena seus próprios perfis e recebe recibos minimizados; a identidade nominal permanece na pasta restrita.

**Tech Stack:** Python 3.12; stdlib, NumPy, pandas, SciPy, scikit-learn, matplotlib, pypdf, pdfplumber e pytest em ambiente isolado da análise. SQLite para dados e contraprova; biblioteca padrão/Fraction para verificação independente. Excel por `@oai/artifact-tool` no runtime fornecido pelo aplicativo, conforme a skill de planilhas; documentação Markdown e relatório HTML agregado.

**Spec:** `docs/superpowers/specs/2026-10-22-airam-datamining-design.md`, SPEC-AIRAM-001 v0.1 aprovada pelo usuário em 22/10/2026.

**Estado:** aprovado pelo usuário: subagentes com revisão por etapa. A execução é registrada no ledger e nos recibos.

## Global Constraints

- “Pasta de trabalho: `C:\Users\marce\Downloads\Airam veras`.”
- “Meta A: ao menos 80% dos estudantes avaliados classificados no nível de aprendizagem adequado, conforme classificação original CAEd.”
- “Meta B: cada estudante atingir pelo menos 80% dos acertos, quando o instrumento oferece contagens de acertos e oportunidades.”
- “Os caminhos originais permanecerão preservados para não romper os manifestos e o MCP existente.”
- “Vazios, `-` e ‘sem resultado’ não viram zero. Zero obtido por participante permanece zero.”
- “Não usar nome isolado como chave nem chamar o pseudônimo derivado de identidade longitudinal validada.”
- “A chave da relação inclui fonte, versão, ano, componente e ocorrência.”
- “Não enviar dados nominais a serviços ou executores externos; identificar explicitamente qualquer handoff com dados minimizados.”
- “A ausência de dados temporais não bloqueia os demais resultados honestos.”
- “Não marcar PASS, RED ou GREEN sem recibo de uma execução real.”

## Review Focus

1. CSV com BOM, ponto e vírgula, espaços em cabeçalhos ou `Turmma`: preservar bruto e normalizar por alias explícito; teste adicional na tarefa 2.
2. ZIP com caminhos absolutos/`..` ou fonte com symlink escapando da pasta autorizada: rejeitar extração/leitura insegura; teste adicional na tarefa 1.
3. Mesmo código CAEd com duas descrições/contextos: versionar a ocorrência, não escolher a primeira correspondência; teste adicional na tarefa 4.
4. Aluno sem cobertura suficiente ou atributo constante: mantê-lo no cadastro, indicar insuficiência e evitar distância/cluster enganoso; testes adicionais nas tarefas 6 e 8.
5. Segundo processamento sobre as mesmas fontes: resultados determinísticos e sem duplicação, preservando saídas anteriores versionadas; teste adicional na tarefa 12.

## Preparação comum de execução

O workspace completo não é um repositório Git. O clone BNCC é fonte, não repositório de implementação. Após aprovação deste plano, criar o código em `datamining/` e um repositório local apenas para código/configuração/testes, com originais, identidade, resultados e chaves ignorados. Copiar a SPEC aprovada para `datamining/specs/SPEC-AIRAM-001.md`, registrando o hash da origem. Não publicar ou criar remoto automaticamente.

Comandos do plano, executados a partir de `datamining/`, usam `.venv\Scripts\python.exe`. Construir o ambiente com o Python bundled já localizado; instalar dependências pelo PyPI e registrar as versões realmente resolvidas em `requirements.lock.txt`. A inspeção atual encontrou NumPy/pandas/pypdf/pdfplumber no runtime, mas não SciPy/scikit-learn/pytest; nenhuma dessas ausências deve ser contada como RED funcional.

Os módulos ficam em `datamining/airam/` e os testes em `datamining/tests/`. Evitar instalação do pacote em diretórios do aplicativo. A CLI será `python -m airam`. Execuções e revisões de código não devem imprimir linhas nominais em logs; sanitizar mensagens de teste.

### Convenção de teste inicial

Quando a função ainda não existir, o teste deve produzir falha controlada de funcionalidade ausente, sem confundir erro de dependência/importação com RED. Após disponibilizar a função, o mesmo teste precisa verificar seu comportamento, e os testes de casos negativos precisam falhar quando se introduz a mutação correspondente. Não preparar uma implementação completa para depois construir os testes.

Cada tarefa registra evidência em `datamining/evidencias/TNN/`, com RED, GREEN, REFACTOR, parâmetros, hashes e revisão. Commits locais pequenos contêm somente código, testes, documentação não nominal e configuração pública. O checkpoint de uma tarefa inclui o hash da saída entregue à seguinte.

## Task 1: catálogo de fontes, configuração e recibos

**Files:** criar `datamining/pyproject.toml`, `requirements.in`, `.gitignore`, `airam/__init__.py`, `airam/catalogo.py`, `airam/recibos.py`, `config/analise.json`, `tests/test_catalogo.py`, `tests/test_recibos.py`.

**Interfaces:** `catalogar(root: Path) -> list[dict]`; `validar_fonte(path: Path, expected_sha256: str, allowed_root: Path) -> None`; `gravar_recibo(path: Path, payload: dict) -> str`. O catálogo inclui `fonte_id`, caminho relativo, hash, tipo, programa, avaliação, status e incompatibilidade; não carrega nomes individuais no recibo.

- [ ] Escrever testes T01–T03, T53 e caso de ZIP escapando da raiz. Asserções: byte alterado é rejeitado; ausência de manifesto não recebe ciclo inventado; PDF/ZIP histórico incompatível recebe status próprio.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_catalogo.py tests/test_recibos.py -q`; registrar falhas funcionais previstas.
- [ ] Implementar catálogo e recibos; incluir runtime/configuração necessários a esse entregável e aliases das fontes existentes. Usar SHA256 e comparação de caminhos resolvidos.
- [ ] Executar os testes, inspecionar que o catálogo não contém linhas nominais e conferir que os originais mantêm hashes. Registrar GREEN/REFACTOR.
- [ ] Commit local de código/configuração/testes; revisar o diff para excluir dados e segredos.

**Deliverable:** catálogo íntegro e contrato de execução verificável, independentemente de qualquer modelo estatístico.

## Task 2: ingestão dos resultados com máscaras de ausência

**Files:** criar `airam/ingestao.py`, `airam/esquemas.py`, `tests/test_ingestao.py`, `tests/test_participacao.py`.

**Interfaces:** `ler_exportacoes(catalogo: list[dict]) -> dict[str,list[dict]]`; chaves `matriculas`, `avaliacoes`, `habilidades`, `escrita`, `fluencia`. `reconciliar_blocos(rows: list[dict]) -> list[dict]`; cada medida conserva bruto, numerador, denominador, unidade, participação e disponibilidade.

- [ ] Escrever T07–T09, T12–T14, T18–T19 e teste BOM/`Turmma`; separar aluno ausente, tarefa não aplicável e zero legítimo.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_ingestao.py tests/test_participacao.py -q`; registrar RED.
- [ ] Implementar os leitores por formato. Extrair os pares de contagens H sem inventar itens individuais. Aplicar os atributos de ciclo/ano/componente do manifesto quando ausentes no CSV; manter essa origem explícita.
- [ ] Executar testes e contraprova das contagens atuais: 18 exportações/54 CSVs; leitura e matemática com 172 cadastros cada; escrita/fluência com 148 cada. Conferir os denominadores dos participantes e os casos de ausência por ano na SPEC.
- [ ] Refatorar e registrar GREEN, hashes, dicionário de medidas e commit local.

**Deliverable:** tabelas normalizadas e rastreáveis; nenhuma correlação depende de reparo silencioso da fonte.

## Task 3: identidade local, matrículas e pareamento

**Files:** criar `airam/identidade.py`, `airam/pareamento.py`, `tests/test_identidade.py`, `tests/test_pareamento.py`.

**Interfaces:** `vincular_localmente(matriculas: list[dict], secret: bytes) -> tuple[list[dict],list[dict]]`; primeiro retorno pseudonimizado, segundo nominal restrito. `parear_componentes(rows: list[dict], esquerda: str, direita: str) -> tuple[list[dict],list[dict]]`; segundo retorno contém não pareados com motivos.

- [ ] Escrever T04–T06 e T38. Testar homônimos de turmas distintas, duplicata na mesma chave e valores adulterados em pares históricos; verificar conteúdo, não só contagem de IDs.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_identidade.py tests/test_pareamento.py -q`; registrar RED real.
- [ ] Implementar vinculação local por escola+ano+turma+nome normalizado, documentando sua limitação. Usar segredo local persistente fora do Git para a pseudonimização e impedir exposição em recibos.
- [ ] Conferir unicidade e conjuntos por componente; produzir log agregado de cobertura, conflitos e qualidade de ligação. Identidade longitudinal institucional permanece indisponível.
- [ ] Executar GREEN/REFACTOR, revisar os arquivos restritos sem expor conteúdo em ferramenta e registrar commit somente do código.

**Deliverable:** pareamento local auditado, com lacunas e homônimos tratados sem colapso.

## Task 4: relações oficiais contextualizadas CAEd–BNCC

**Files:** criar `airam/matriz_cnca.py`, `airam/bncc.py`, `airam/vinculos.py`, `tests/test_matriz_cnca.py`, `tests/test_vinculos.py`, `config/ressalvas_curriculares.json`.

**Interfaces:** `extrair_ocorrencias(pdf: Path) -> list[dict]`; `carregar_bncc(root: Path, expected_commit: str) -> dict[str,dict]`; `vincular_posicoes(posicoes: list[dict], ocorrencias: list[dict], bncc: dict) -> list[dict]`. Cada vínculo devolve ano avaliado, ano da tabela, página, código, ciclo, status contextual, texto e ressalva.

- [ ] Escrever T26–T31 e teste de código repetido com texto/contexto divergente; casos obrigatórios `3EF06_M`, `3EF07_M`, `3EF09_M`, `4EF07_M` e a marca de Ciclo I da página 7.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_matriz_cnca.py tests/test_vinculos.py -q`; registrar RED.
- [ ] Implementar extração por limites das células, inclusive colunas de ciclos. Fixar o commit BNCC observado `9c268978efa2aa250834c6a9edb6074432752838` e conferir localizadores/códigos canônicos.
- [ ] Executar a conferência real: 124 posições/93 códigos, 118 correspondências do próprio ano, seis exceções anteriores; conferir as 73 BNCC presentes nos contextos auditados, sem forçar o mesmo total em políticas mais estritas.
- [ ] Marcar associações semanticamente ressalvadas e vínculos de integração a confirmar; executar GREEN/REFACTOR e registrar commit.

**Deliverable:** relação muitos para muitos versionada, sem multiplicação de resultados ou equivalência inventada.

## Task 5: estatística descritiva, contraprova e duas metas

**Files:** criar `airam/metricas.py`, `airam/contraprova.py`, `airam/metas.py`, `tests/test_metricas.py`, `tests/test_contraprova.py`, `tests/test_metas.py`.

**Interfaces:** `taxa_por_itens(acertos: list[int], oportunidades: list[int]) -> float | None`; `contraprovar(rows: list[dict]) -> dict`; `meta_adequados(avaliados: int, adequados: int, meta: float) -> dict`; `meta_acertos(acertos: int, oportunidades: int, meta: float) -> dict`. A contraprova usa stdlib/Fraction e/ou SQL; não importa a função principal.

- [ ] Escrever T10–T11, T15, T20–T25. Asserções mínimas:

```python
assert taxa_por_itens([1, 0], [1, 3]) == 0.25
assert meta_adequados(24, 10, 0.8)['conversoes'] == 10
assert meta_acertos(17, 22, 0.8)['lacuna'] == 1
```

- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_metricas.py tests/test_contraprova.py tests/test_metas.py -q`; registrar RED.
- [ ] Implementar soma de contagens, cortes aritméticos e classificações originais. Para Meta A, devolver `acertos_ate_adequacao=None` quando faltar corte oficial; corte empírico histórico continua identificado como hipótese.
- [ ] Executar a contraprova real aluno→turma→escola, comparando com arredondamento do portal. Inspecionar denominadores por ano; o 5º em leitura usa 53 avaliados, não 54 cadastros.
- [ ] Executar GREEN/REFACTOR e mutação T55; registrar o resultado da mutação e commit local.

**Deliverable:** medidas exatas observadas, metas separadas e reconciliação independente.

## Task 6: correlações com N, incerteza e multiplicidade

**Files:** criar `airam/correlacoes.py`, `tests/test_correlacoes.py`, `tests/test_multiplicidade.py`.

**Interfaces:** `correlacionar(pares: list[dict], x: str, y: str, strata: list[str], seed: int) -> list[dict]`; `ajustar_bh(p_values: list[float]) -> list[float]`; `total_sem_bloco(rows: list[dict], posicao: str) -> list[dict]`.

- [ ] Escrever T16–T17 e T37–T39; acrescentar casos de coluna constante, dois pares, empates e mudança de composição da turma. Testar p e q sem tratar não estimável como zero.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_correlacoes.py tests/test_multiplicidade.py -q`; registrar RED.
- [ ] Implementar Pearson/Spearman por ano/comparabilidade, total corrigido e famílias declaradas; usar permutações de pareamento para associação. Registrar N, tamanho de efeito, p/q e limitações da inferência na escola.
- [ ] Confrontar casos definidos com funções SciPy e uma contraprova algébrica/SQL quando aplicável; revisar famílias e permutações antes de gerar tabelas reais.
- [ ] Executar GREEN/REFACTOR e commit; liberar uma tabela que diferencia descrição censitária e inferência/generalização.

**Deliverable:** tabelas de associação rastreáveis; nenhuma relação é rotulada causal.

## Task 7: matrizes de evidência e propagação curricular

**Files:** criar `airam/grafo.py`, `airam/agregacoes.py`, `tests/test_grafo.py`, `tests/test_agregacoes.py`.

**Interfaces:** `construir_bipartida(vinculos: list[dict], policy: str) -> dict`; `propagar(observado: ndarray, observado_mask: ndarray, adjacency: ndarray, passos: int) -> dict`; `agregar_observacoes(rows: list[dict], nivel: str, grupos: list[dict] | None) -> list[dict]`.

- [ ] Escrever T32–T36. Usar grafo pequeno com solução manual, aluno sem vizinhos, associação múltipla e grupos sobrepostos; testar invariância a permutação consistente das colunas.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_grafo.py tests/test_agregacoes.py -q`; registrar RED.
- [ ] Construir B com linhas de ocorrência CAEd e colunas BNCC, separar políticas estrita/ressalvada e impedir contagem duplicada. Calcular `W=B@B.T`; retirar diagonal para vizinhança compartilhada e normalizar cada linha não nula. Propagar soma de valores ponderados dividida pela massa de evidência observada; se massa zero, devolver ausência.
- [ ] Gerar observado, propagado, máscara e cobertura como saídas distintas. Produzir visões aluno/grupo/turma/escola com soma de contagens quando disponível e deduplicação de participantes.
- [ ] Executar GREEN/REFACTOR, conferir contraprova matricial manual e registrar commit.

**Deliverable:** matrizes explicáveis e auditáveis, sem apresentar GCN treinada ou domínio BNCC comprovado.

## Task 8: agrupamentos e descrição pedagógica completa

**Files:** criar `airam/clusters.py`, `airam/perfis_grupo.py`, `tests/test_clusters.py`, `tests/test_perfis_grupo.py`, `config/agrupamentos.json`.

**Interfaces:** `agrupar(features: dict, config: dict, seed: int) -> dict`; `descrever_grupos(resultado: dict, observacoes: list[dict], vinculos: list[dict]) -> list[dict]`. A saída inclui membros pseudonimizados, estabilidade, cobertura, critérios e status de liberação.

- [ ] Escrever T45–T48; incluir aluno sem cobertura, coluna constante, apenas um perfil e reordenação de linhas. Testar que a função pode devolver “sem agrupamento estável”.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_clusters.py tests/test_perfis_grupo.py -q`; registrar RED.
- [ ] Comparar representação observada e propagada dentro de ano/componente comparável. Pré-declarar K de 2 a `min(5, floor(N/5))`, grupo mínimo 5 e política de ausência; tratar esses valores como escolhas técnicas passíveis de sensibilidade, não normas pedagógicas.
- [ ] Avaliar sementes e reamostragens com ARI/separação, sem escolher uma única execução conveniente. Liberar descrições exploratórias somente com estabilidade reportada; caso contrário, usar grupos de intervenção por regras explícitas sem alegar clusters descobertos.
- [ ] Produzir descrições com distribuição de resultados, lacunas CAEd, BNCC e ressalvas, cobertura, revisão docente e critério de reavaliação; executar GREEN/REFACTOR e commit.

**Deliverable:** grupos revisáveis e descrições rastreáveis, sem rótulo de capacidade fixa.

## Task 9: cenários e gate de previsão temporal

**Files:** criar `airam/cenarios.py`, `airam/predicao_gate.py`, `tests/test_cenarios.py`, `tests/test_predicao_gate.py`, `config/cenarios.json`.

**Interfaces:** `avaliar_prontidao_temporal(avaliacoes: list[dict], vinculos: list[dict]) -> dict`; `projetar_cenario(observacoes: list[dict], metas: dict, hipoteses: dict) -> dict`. Campos obrigatórios: tipo de resultado, premissas, unidade, comparabilidade e status de validação.

- [ ] Escrever T40–T44: ciclo único, falsas datas por exportação, rótulos assumidos de aplicação, vazamento e congelamento dos adequados. Verificar que cenário continua disponível quando a previsão é bloqueada.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_cenarios.py tests/test_predicao_gate.py -q`; registrar RED.
- [ ] Implementar cenários aritméticos e lacunas até Meta B. Meta A calcula conversões institucionais e só usa acertos por nível com regra oficial ou hipótese explicitada. Sensibilidade inclui ausência de ganho e perdas, sem probabilidades arbitrárias apresentadas como calibradas.
- [ ] Para a base atual, produzir gate `previsao_temporal_validada=False` com motivos; não treinar modelo temporal usando as etiquetas históricas presumidas.
- [ ] Executar GREEN/REFACTOR e commit; revisar frases e rótulos dos relatórios.

**Deliverable:** cenários transparentes e uma decisão verificável sobre o que não é estimável.

## Task 10: relatório agregado e planilha nominal restrita

**Files:** criar `airam/relatorio.py`, `reports/templates/relatorio.html`, `reports/build_workbook.mjs`, `tests/test_relatorio.py`, `tests/test_intervencao.py`.

**Interfaces:** `preparar_intervencao(observacoes: list[dict], metas: dict, vinculos: list[dict], grupos: list[dict]) -> list[dict]`; `gerar_relatorio(resultados: dict, out_dir: Path) -> list[Path]`. O builder JS consome JSON local de contrato fixo e gera Excel com abas Metas, Intervenção nominal, Habilidades, Grupos, Cálculos e Fontes/Auditoria conforme necessidade, evitando repetição.

- [ ] Escrever testes T24–T25, T48 e T52; verificar que nenhuma conclusão individual deriva de média escolar, que a fila é recalculada por critérios e que o relatório agregado não traz nomes/IDs individuais.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_relatorio.py tests/test_intervencao.py -q`; registrar RED.
- [ ] Preparar as tabelas analíticas e o relatório HTML; gerar figuras científicas em arquivos próprios. Para Excel, ler integralmente a skill de planilhas/API, carregar o runtime oficial e executar o marcador de autoria uma única vez imediatamente antes da primeira criação. Não autorar workbook com openpyxl/pandas.ExcelWriter.
- [ ] Manter metas e parâmetros em células identificadas; fórmulas aritméticas simples devem atualizar distâncias e prioridades quando os controles mudarem. Análises complexas pré-calculadas recebem versão/hash e indicação de recálculo pelo pipeline, sem simular atualização automática.
- [ ] Reabrir/inspecionar o Excel e renderizar amostras de abas/figuras. Conferir totais, fórmulas, nomes restritos e ausência de erros/células cortadas; registrar GREEN/REFACTOR e commit somente do código.

**Deliverable:** relatório minucioso e utilizável, planilha nominal de acesso restrito e fontes por resultado.

## Task 11: contratos de agentes, hooks e CLI do projeto

**Files:** criar `airam/__main__.py`, `airam/cli.py`, `airam/gates.py`, `hooks/preflight.ps1`, `hooks/release.ps1`, `agents/contratos.json`, `tests/test_cli.py`, `tests/test_hooks.py`, `tests/test_agent_receipts.py`.

**Interfaces:** CLI `python -m airam catalogar|validar|analisar|relatar|gate|executar --config config/analise.json`; `avaliar_gate(name: str, artifacts: dict) -> dict`; cada comando devolve código de saída compatível com seu recibo e não oculta falha.

- [ ] Escrever T49–T51 e T53; testar falha real de preflight/release e propagação do código de saída. Distinguir perfil configurado de ativado/inferido.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_cli.py tests/test_hooks.py tests/test_agent_receipts.py -q`; registrar RED.
- [ ] Implementar hooks de projeto acionados pela CLI. Para integração Core, usar perfis existentes com validade comprovada ou validar/registrar explicitamente um novo perfil; não contornar os 59 cartões rejeitados no inventário por mudança global silenciosa.
- [ ] Registrar spec_id de cada execução textual exigida pelo Core e os recibos minimizados. Testar disparo real de eventos de sessão apenas em harness compatível; se não houver evidência, relatar somente configurado.
- [ ] Executar GREEN/REFACTOR, teste de hooks sem dados nominais externos e commit local.

**Deliverable:** rotina executável com gates verificados, papéis delimitados e status reais de integração.

## Task 12: mutações, reprodução e liberação interna

**Files:** criar `tests/test_reproducao.py`, `tests/test_release_gate.py`, `tests/mutations/`, `README.md`, `docs/REPRODUCAO.md`, `docs/LIMITACOES.md` no projeto de código.

**Interfaces:** `python -m airam executar --config config/analise.json` e `python -m airam gate release`; o recibo final referencia hashes de todas as entradas, resultados, testes e contraprovas.

- [ ] Escrever T54–T58 e teste de segunda execução idempotente: hashes analíticos determinísticos, sem duplicação e sem substituir fontes. Metadados variáveis de horário são excluídos explicitamente da comparação de conteúdo.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests/test_reproducao.py tests/test_release_gate.py -q`; registrar RED funcional.
- [ ] Executar mutações de média indevida, remoção de turma da chave e perda de contexto curricular em cópias isoladas do código; demonstrar que os testes específicos as detectam. Não alterar originais para simular erro real.
- [ ] Executar `.venv\Scripts\python.exe -m pytest tests -q`, a análise completa, a contraprova independente e o gate de release. Conferir arquivos publicados, hashes, fórmulas/figuras e cobertura R01–R24/T01–T58.
- [ ] Solicitar revisão independente do código e da interpretação, corrigir problemas e repetir somente as verificações afetadas. Finalizar commit local e recibo de liberação; separar claramente entrega analítica atual e previsão temporal indisponível.

**Deliverable:** pacote interno reproduzível, resultados reais, testes e limitações coerentes com a SPEC.

## Rastreabilidade e ordem

| Tarefa | Requisitos principais | Dependências |
|---|---|---|
| 1 | R01, R21, R24 | nenhuma |
| 2 | R01, R03–R05, R08 | 1 |
| 3 | R02, R05, R15 | 2 |
| 4 | R12 | 1, 2 |
| 5 | R03–R11 | 2, 3 |
| 6 | R07, R15 | 3, 5 |
| 7 | R12–R14 | 4, 5 |
| 8 | R18 | 3, 7 |
| 9 | R09–R11, R16–R17 | 3, 5 |
| 10 | R11, R14–R18, R24 | 5–9 |
| 11 | R19–R21, R24 | 1–10 |
| 12 | R21–R24 | todas |

Ingestão, identidade, currículo, análise e liberação formam um pipeline com interfaces comuns; por isso o plano único tem incrementos revisáveis, em vez de projetos desconectados. Trabalho paralelo é permitido somente entre tarefas cujas dependências e arquivos não conflitam.

## Revisão do próprio plano

- Cobertura de R01–R24 e T01–T58 conferida na matriz acima e nos passos das tarefas.
- Nomes de funções e contratos entre tarefas consistentes; nenhuma tarefa depende de um modelo treinado não disponível.
- As cinco classes do Review Focus têm testes atribuídos.
- Nenhum passo está concluído por antecipação; exemplos são contratos esperados, não saída de execução.
- Instalação isolada de dependências, proteção de dados e limites do Core explícitos.

## Decisões para execução

Recomendo **subagentes com revisão por tarefa**, porque erros de identidade, denominadores e relações curriculares podem gerar intervenções nominais inadequadas. Alternativa: execução direta nesta sessão, com revisão independente integral ao final.

Antes de implementar, o usuário revisa este plano e escolhe o método. A revisão não transforma testes planejados em testes executados. O horizonte de avaliação ainda deve ser confirmado; os cenários atuais permanecem condicionais e separados de uma previsão validada.

