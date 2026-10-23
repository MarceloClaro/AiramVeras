# T08 → T10/T11: agrupamentos e perfis pedagógicos revisáveis

Entrega local executada em 23/10/2026, sobre a base `fbbd17c003459cb9f63b3dbb0feefbc39d058159`.
As duas análises reais concluíram com os mesmos hashes. A segunda incorporou a proteção
contra chamar acerto integral de lacuna ou zero de força; esse caso de fronteira não
alterou os resultados desta base. Revisão docente e validação externa permanecem pendentes.

## Checkpoints e consumo

| Arquivo | SHA256 | Uso |
|---|---|---|
| `restrito/t08/checkpoint.json` | `17d71689ba27724f8b165358e810210ee7c6d4a9001dbaa403f125a47b8c1e3e` | Membros pseudonimizados, rótulos, E/Fs, exclusões e perfis integrais; somente local |
| `estatistica/t08/checkpoint.json` | `d298a8754ad6e896c7e1077dcccc35c963a90777d82f4fb40c90e2224e4cacc1` | Agregado sem identificadores individuais; perfis pequenos suprimidos |
| `estatistica/t08/perfis-pedagogicos.md` | `2238f99d6b95b8305dae6919cf2046b8a4faefea57b7f49d535a4ee068fcd0d1` | Texto completo de regras, solução observada, controles principais e E/F para revisão |
| `docs/esquema-t08.json` | `b580d6bd2c1ea59d7fc962aae6341ee04ce2856dce5184a3899eb5bfef176f9c` | Estrutura agregada `airam-grupos-t08-v1` |
| `docs/esquema-restrito-t08.json` | `296ab70598581008f2be5a3e7e7c369de6f93c5c2e832396568ea26e2fc80a0c` | Estrutura restrita `airam-grupos-restrito-t08-v1` |

O restrito é ignorado pelo Git; o nome da pasta não certifica ACL. O agregado é para
revisão local, não autorização irrestrita de publicação. Grupos com N<5 não têm
contagens, distribuição ou turmas no perfil público; células 1–4 de transições são
intervalos no agregado. Os dados individuais não foram impressos em logs nem enviados
a serviços externos. Não reconstituir membros pelos centroides ou por inferência.

Antes de consumir, verificar SHA, `versao_schema`, `config_sha256` e `fontes`. O JSON
agregado aponta ao SHA do restrito. Os schemas fecham a estrutura efetiva da versão;
foram gerados das formas da entrega e validados com todos os keywords utilizados.
São documentação estrutural, não contraprova independente das decisões analíticas.
A contraprova independente de conteúdo está em `evidencias/T08/auditar.py`.

## Estrutura e chaves

`instrumentos` tem dez contextos de Leitura/Matemática. A identidade contextual é
`(avaliacao_id, ano_avaliacao, ciclo, ano_escolar, componente, fonte_id, sha256, exportacao)`.
Fonte e versão não são descartadas. Cada instrumento contém:

- `regras` (restrito) e `perfis_regras`: alternativa explícita, sempre produzida;
- `observado_operacional` e `perfis_observado`: todos os casos completos observados no
  contexto, com status e eventual menor K admissível;
- `cenarios`: cinco cenários pré-declarados, seleção E/F0/Fs, resultados por braço,
  comparações em K fixo, confronto com regras, perfis e sensibilidade;
- `sensibilidade_observado`: reavaliação dos mesmos diagnósticos com mínimo 6 e
  limiares mais/menos exigentes, sem refazer ajustes.

`unidades_proprias` tem oito contextos de Escrita/Fluência. Usa grupos por categoria
original, não clusters de acertos. `valor`, campo e unidade originais geram distribuições
separadas; não há conversão para 22 itens, Meta B ou vínculo BNCC não documentado.

A chave de um perfil inclui contexto completo, cenário, braço e `grupo_id`. Não unir
`cluster_1` de contextos/cenários diferentes. Os rótulos não têm significado ordinal
de capacidade e não estabelecem identidade longitudinal. Alunos podem aparecer em
instrumentos e cenários diferentes: não somar N como estudantes distintos da escola.
Perfis por regra e clusters são visões alternativas, não grupos disjuntos entre si.

## Interfaces de produto

`agrupar(features: dict, config: dict, seed: int) -> dict` recebe `contexto`, `alunos`,
`colunas`, `valores` de proporções, `cobertura` e `pesos` opcionais. Ordena alunos/colunas
antes de sorteios e ajuste; recusa duplicatas, escala inválida e pesos inválidos.
`seed` controla subamostras; `config.seeds` fixa as inicializações originais. `alunos`,
`excluidos`, `grupos.membros` e `candidatos.rotulos` são sempre restritos. Ausência é
null/NaN em memória; não vira zero. Retorna `sem_agrupamento_estavel` por amostra,
colunas, variação ou controles insuficientes, com motivo explícito.

`preparar_bracos(bloco, grafo, config, passos=1, sem_retorno=False, pesos=None)` consome
um bloco T07 autenticado e o grafo do mesmo contexto/política. O coletor associa por
contexto completo e não chama `matrizes_evidencia`; portanto não depende da ressalva
da API T07 sobre recusa de mistura de contextos. Na comparação, F0 são todas as
posições observadas; Fs são posições cujo Q liga a nós estruturalmente apoiados pelo
kernel. O propagado de uma posição é a média ponderada pelo Q de seus nós elegíveis,
somente quando todos têm suporte. E contém casos completos em F0 e Fs. Isolados não
recebem zero e a ausência de Fs torna a comparação indisponível.

`comparar_particoes(left, right)` recusa alunos/contextos diferentes. Confronta os
candidatos por K fixo, incluindo os reprovados com status explícito. Traz ARI,
transição agregada e número de pares cujo coagrupamento mudou. K escolhido por braço
é uma decisão separada. Não subtrair ARIs nem interpretar silhuetas de geometrias
diferentes como efeito pedagógico.

`grupos_por_regras(observacoes, cobertura_minima=0.8)` separa cobertura insuficiente,
total C/D abaixo de 4/5 e total C/D que atinge 4/5, somente em acertos de itens.
Meta A usa categoria original, sem corte empírico. Em E/F mantém categoria original.

`descrever_grupos(resultado, observacoes, vinculos) -> list[dict]` recusa duplicação e
mistura de contextos. As contagens são calculadas antes da expansão curricular.
`perfis_publicos(perfis)` remove membros e suprime detalhes de grupos menores que cinco.

## Desenho fixado antes dos dados reais

`config/agrupamentos.json` já estava no snapshot de RED01, antes da análise real.
Os números são escolhas técnicas exploratórias, não normas pedagógicas:

- K de 2 a `min(5,floor(N/5))`; mínimo de cinco na referência original; menor K
  aprovado é preferido. Não impor cinco em cada subamostra.
- KMeans Lloyd, proporções, euclidiana, pesos iguais por posição, sem padronizar pelo
  desvio-padrão. Constantes permanecem na geometria e no perfil; contribuem distância
  zero. Sensibilidade de peso usa as oportunidades de cada posição.
- Sementes originais 11, 29, 47, 71, 101, 131, 173, 211; uma inicialização por seed.
  Referência medóide dos ARIs, desempate por inércia e seed. Rótulos por centroide.
- Quarenta subamostras sem reposição, `floor(0.8N)`, uma seed derivada de 81022 por
  sorteio, cinco inicializações internas. Os mesmos sorteios são usados nos braços
  e K do mesmo E. São amostras simples, não estratificadas por turma; não se alegou
  execução das 200 replicações/leave-one-out sugeridas no memo preparatório.
- Planejadas, válidas, falhas por razão, convergência/limite de iterações, tamanho
  mínimo, ARI de todos os pares válidos de seeds e ARI de subamostras são reportados.
- Cada grupo: correspondência Hungarian um-a-um por Jaccard. Interseção com menos de
  dois membros é suporte insuficiente, separada de ajuste inválido. Retenção,
  intrusos, tamanhos correspondentes e dissoluções complementam o Jaccard.
- Gate: ≥90% ajustes válidos; ARI mediana≥0,70/p10≥0,40; cada grupo avaliável em
  ≥80% planejadas e Jaccard mediana≥0,60/p10≥0,35, tanto em seeds como subamostras;
  silhueta global>0, mediana por grupo≥0 e ≤25% negativas por grupo. Quantis lineares.
- Cobertura: soma D observados dividida pelas oportunidades previstas; casos
  completos também exigidos. O coletor confere que o D por posição é único e a soma
  coincide com o total de instrumento T05. Aplica essa composição aos ausentes,
  sem criar acertos ou nova observação. Massa de grafo não é D.

Sensibilidades: cobertura 70/90/100%; mínimo original 6; limiares mais/menos exigentes;
política estrita; dois passos; dois passos sem retorno; peso por oportunidades.
Limiar/minimum reutilizam diagnósticos. Mudanças de E/features/pesos têm estimando
identificado. A configuração principal não é substituída por cenário favorável.
O cache reutiliza apenas entradas completas idênticas, incluindo contexto e pesos.

## Campos dos perfis e interpretação pedagógica

`observado` conserva C/D e distribuições de taxas, acertos e oportunidades individuais.
Todos são observados; propagado não entra no numerador ou denominador. Sem dado,
taxa e contagens de perfil são null, não uma prova zerada. `habilidades` contém todas
as H, inclusive constantes, cobertura, ausência, distribuição, CAEd, textos BNCC,
localizadores, versões, peso e ressalvas. Relações candidatas de peso zero continuam
identificadas como tal; associação documental não comprova domínio BNCC.

`lacunas_priorizadas` ordena até três posições com algum erro observado por menor
taxa; não converte ausência em déficit nem exige 80% por H. `forcas_relativas` ordena
posições com algum acerto, sem declarar proficiência absoluta. O perfil preserva todas
as H, mesmo as que não estão entre as três prioritárias. A ordem é uma proposta de
acompanhamento por necessidade observada, sujeita à decisão docente.

As atividades têm sondagem, prática orientada e verificação autônoma, ligadas ao
descritor documentado. São sugestões genéricas contextualizadas; materiais, rubrica,
adequação etária, composição prática e eficácia não foram validados pelo professor.
Há ressalva explícita de que o bloco agregado não identifica os itens individuais errados.
`revisao_docente=pendente`; data de reavaliação null; gatilho é ciclo de atividades
acordado com docente ou nova avaliação comparável, registrando data/unidade/apoio.

## Resultados e limites reais

N observados elegíveis por ano em Leitura/Matemática: 24/24, 28/28, 24/24, 42/42,
53/54. Leitura do 5º ano conserva um cadastro sem resultado; esse estudante não
vira zero nem entra na geometria. Nos dez observados operacionais, somente Leitura
do 4º ano libera K=2 nesta configuração. Os demais mantêm os grupos por regras.

Na comparação principal, Matemática do 1º ano fica indisponível por ausência de
suporte estrutural. Propagado libera L1 K=4, L2 K=2 e L5 K=3; O-controle libera L5 K=3.
Isso não demonstra benefício do grafo. A contraprova mostrou distâncias quadradas
O-controle/P-controle idênticas em L1, L2, L3, L5 e M2: diferenças de partição/seleção
nesses casos são sensibilidade do procedimento de ajuste a representação/empates/
aritmética, não alteração geométrica demonstrada pelo currículo. A causa numérica
específica não foi isolada; não atribuir essas diferenças a aprendizagem ou melhoria.

Houve 28 mudanças de seleção nas combinações de limiares/mínimo/representações
avaliadas, não 28 instrumentos nem 28 eventos independentes. Cortes de cobertura
70/90/100% não mudaram E neste conjunto de casos completos. Essas proporções não
são probabilidades de validade. Um ciclo não libera inferência temporal.

## Evidência e reprodução

RED01: 16 falhas funcionais controladas, sem erro de dependência. GREEN01: 16 pass.
RED02: dois casos (matriz vazia e coletor ausente); GREEN02: 18 pass. RED03: lacuna
indevida em acerto integral; GREEN03: 19 pass. Suíte final única após estabilização:
284 pass. Quatro mutações em cópias temporárias foram detectadas: ausência virando
zero, estabilidade de grupo ignorada, mínimo ignorado e fanout duplicando contagens.

Contraprova final: 6.903 verificações, 133 perfis e 294 ARIs refeitos com Fraction,
sem importar airam; varredura de 60 arquivos sem identificadores reais. Os números
contam perfis repetidos por cenário, não estudantes distintos. Schema PASS certifica
somente estrutura; revisão docente, externa e eficácia permanecem pendentes.

Usar `.venv/Scripts/python.exe evidencias/T08/executar.py <rotulo-novo> <fase> <script>`.
Scripts: `analisar.py`, `auditar.py`, `validar_entrega.py`, `relatorio.py`, `mutacoes.py`.
Não sobrescrever recibos. `analisar.py` recusa checkpoint diferente já existente;
preservar versões antes de atualizar. A primeira versão está também arquivada
localmente em `restrito/t08/versoes/analise01/` e `estatistica/t08/versoes/analise01/`.
Os recibos capturam código/testes/config/entradas/versões antes da execução. A primeira
versão do wrapper não listou o agregado T05 no snapshot externo; `analisar.py` já
verificava seu SHA esperado antes de ler as entradas. A partir de RED03 o wrapper
também o captura. Não foi atribuída retroativamente uma captura ao recibo anterior.
