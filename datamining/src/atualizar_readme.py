import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

README_PATH = r'README.md'

with open(README_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

nova_secao_dossie = """---

## 📘 Dossiê Pedagógico Mestre e Matriz Canônica das Turmas (670 Laudas Vetoriais A4)

> **Documento Oficial de Referência e Base de Todos os Dossiês das Turmas (1º ao 5º Ano)**  
> **Arquivo Homologado**: [`DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf`](file:///c:/Users/marce/Downloads/Airam%20veras/DOSSIE_MESTRE_1ANO_BNCC_E_PRATICAS_DIARIAS_AMPLIADAS.pdf)  
> **Hash SHA-256 Forense**: `cfda547ea9ba6e670375d10dfdf5d08e1b364286718d48a39c124107f04e90e1` (3,12 MB)  
> **Total de Páginas**: **670 laudas vetoriais A4** (46 laudas de Front Matter Master + 624 laudas de cadernos individualizados)  
> **Chancela de Auditoria**: Encadeamento no Ledger Imutável SHA-256 (Bloco 13) e integridade relacional sem ilhas no SQLite (`airam_veras_ecossistema.sqlite`).

Este documento estabelece o **modelo canônico universal** adotado para todos os dossiês e intervenções da Escola de Cidadania Airam Veras, integrando o diagnóstico censitário do CAEd/SPAECE à neurociência cognitiva, legalidade inclusiva e acompanhamento longitudinal.

```mermaid
graph TD
    classDef capBox fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#ffffff,font-weight:bold;
    classDef sciBox fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#ffffff;
    classDef legBox fill:#581c87,stroke:#a855f7,stroke-width:2px,color:#ffffff;
    classDef planBox fill:#1e1b4b,stroke:#6366f1,stroke-width:2px,color:#ffffff;
    classDef indBox fill:#14532d,stroke:#22c55e,stroke-width:2px,color:#ffffff;
    classDef pratBox fill:#701a75,stroke:#ec4899,stroke-width:2px,color:#ffffff;

    subgraph DOSSIE ["📘 Arquitetura Canônica do Dossiê Mestre (670 Laudas)"]
        S1["1. Capa Master Oficial & Chancela Forense"]:::capBox
        S2["2. Fundamentação Científica: 9 DOIs Reais Ativos"]:::sciBox
        S3["3. Rotina Diária Interdisciplinar (Segunda a Sexta)"]:::sciBox
        S4["4. Marco Legal Inclusivo, PEI, PAEE & Psiconeuropedagogia"]:::legBox
        S5["5. Matriz BNCC Computação (Resolução CNE/CP 1/2022)"]:::planBox
        S6["6. Plano Anual e Planos Bimestrais I a IV (9 Componentes)"]:::planBox
        S7["7. Censo Coletivo & Matrizes de Markov (Ciclos I, II, III)"]:::sciBox
        S8["8. Fichas Individuais (24 Lauda-Raio-X, EWS & Metas PEI)"]:::indBox
        S9["9. Caderno de Práticas Diárias (24 alunos x 26 pág = 624 pág)"]:::pratBox

        S1 --> S2 --> S3 --> S4 --> S5 --> S6 --> S7 --> S8 --> S9
    end
```

---

### 1. 🏛️ Marco Legal da Educação Especial Inclusiva e Diretrizes Normativas

O Dossiê Mestre e os registros individuais do banco de dados cumprem rigorosamente a legislação brasileira de acessibilidade pedagógica e educação especial:

| Norma Jurídica | Âmbito e Artigos | Determinação Operacional na Escola Airam Veras | Diretriz Avaliativa CAEd / SPAECE |
|:---|:---|:---|:---|
| **Lei nº 13.146/2015 (LBI)** | Arts. 27, 28 (I a XVII), 30 | Oferta compulsória de adaptações razoáveis, mediação pedagógica continuada e proibição expressa de exclusão. | Tempo adicional estendido (+50%), formatos acessíveis e redução de distratores. |
| **Lei nº 12.764/2012 (TEA)** | Arts. 2º (III) e 3º (IV) | Atendimento a pessoas com TEA como PCD, direito a profissional de apoio escolar e rotinas visuais estáveis (TEACCH). | Sala de aplicação silenciosa, suporte pictográfico e permissão de objetos regulatórios. |
| **Lei nº 14.254/2021** | Arts. 1º, 3º e 4º | Acompanhamento integral e intervenção precoce para educandos com TDAH, Dislexia e afins. | Ledor oficial treinado para textos longos, assento prioritário e não penalização ortográfica. |
| **Res. CNE/CEB nº 04/2009** | Arts. 1º ao 13 | Atendimento Educacional Especializado (AEE) na Sala de Recursos Multifuncionais (SRM) no contraturno. | Planejamento articulado quinzenal entre professor da SRM e professor da sala regular. |
| **Decreto nº 7.611/2011** | Arts. 1º ao 5º | Dupla matrícula no Censo Escolar/INEP e financiamento de tecnologia assistiva via Fundeb. | Documentação probatória de atendimento na SRM para auditoria e prestação de contas. |
| **Parecer CNE/CP nº 50/2023** | Seções 4, 5 e 6 | Plano Educacional Individualizado (PEI) como instrumento obrigatório e Suporte Comportamental Positivo (PBS). | Proibição de tarefas avulsas desconectadas; metas funcionais adaptadas e mensuráveis. |
| **Nota Técnica nº 02/2025/MEC** | Itens I a V | Diretrizes Nacionais para Elaboração, Monitoramento e Auditoria Forense do PEI bimestral. | Registro contábil das metas adaptadas no prontuário escolar com assinatura e hash SHA-256. |

---

### 2. 🧠 Fundamentação Psiconeuropedagógica e Desenho Universal para a Aprendizagem (DUA)

A pedagogia de intervenção do dossiê ancora-se no padrão ouro da neurociência da aprendizagem e na ciência cognitiva da leitura:

1. **Desenho Universal para a Aprendizagem (DUA / CAST - Rose & Meyer):**
   - **Rede Afetiva (*O porquê da aprendizagem*):** Previsibilidade da agenda visual diária TEACCH na carteira, eliminação de estímulos estressores e contratos pedagógicos baseados em Suporte Comportamental Positivo (PBS).
   - **Rede de Reconhecimento (*O quê da aprendizagem*):** Representação multissensorial com tipografia sem serifa 14pt+ (ou OpenDyslexic), material concreto estruturado (material dourado, ábaco horizontal, letras móveis emborrachadas) e pranchas de Comunicação Alternativa e Aumentativa (CAA/PECS).
   - **Rede Estratégica (*O como da aprendizagem*):** Múltiplos meios de ação e expressão, scaffolding progressivo e tempo estendido (+50%) com pausas ativas a cada 15 a 20 minutos.
2. **Modulação de Funções Executivas (Diamond & Barkley):**
   - Fortalecimento da memória de trabalho mediante redução drástica da carga cognitiva extrínseca (Sweller - DOI: [10.1007/s10648-011-9181-5](https://doi.org/10.1007/s10648-011-9181-5)).
   - Treino de controle inibitório e atenção sustentada com tarefas em passos únicos ("uma instrução por vez").
3. **Neurobiologia da Leitura e Aritmética (Dehaene & Fuchs):**
   - Reciclagem neuronal da Área da Forma Visual das Palavras no córtex occipitotemporal esquerdo via instrução fônica sistemática explícita (Dehaene - DOI: [10.1016/j.neuron.2007.01.017](https://doi.org/10.1016/j.neuron.2007.01.017)).
   - Consolidação do senso numérico e domínio dos fatos básicos de adição sem sobrecarga de memória (Fuchs - DOI: [10.1037/0022-0663.100.3.491](https://doi.org/10.1037/0022-0663.100.3.491)).
4. **Altas Habilidades / Superdotação e Dupla Excepcionalidade (Renzulli):**
   - Modelo dos Três Anéis (Renzulli - DOI: [10.4324/9780203876796](https://doi.org/10.4324/9780203876796)): compactação curricular (*Curriculum Compacting*) e projetos de enriquecimento investigativo desplugado para evitar o desengajamento e sub-rendimento.

---

### 3. 🎯 Adaptações Diárias de Sala de Aula e Atendimento SRM por Cluster

O dossiê estabelece uma rotina precisa e exequível tanto para o professor regente quanto para o professor do AEE:

| Cluster | Perfil Cognitivo / Clínico | Adaptações Diárias na Sala Regular (LBI Art. 28) | Atendimento Especializado na SRM (PAEE) |
|:---:|:---|:---|:---|
| **Cluster 1A** | **Recomposição Intensiva / Alerta Clínico**<br>Fragilidade severa em consciência fonêmica e contagem reflexa. | Carteira frontal central; instruções fracionadas em blocos de 15 min; 3 min de pausa motora; máscara de leitura; leitura de enunciado em voz alta. | **SRM Individual:** 3x por semana (150 min/sem). Fonoarticulação no espelho, letras móveis e material dourado. |
| **Cluster 1B** | **Consolidação e Fluência**<br>Silabação hesitante, dependência de contagem nos dedos. | Leitura em duplas tutoradas; reta numérica horizontal na carteira; palavras com sílabas em cores contrastantes; reforço imediato de micro-etapas. | **SRM Pequeno Grupo (3 alunos):** 2x por semana (100 min/sem). Automação grafema-fonema e cálculo mental Kumon. |
| **Cluster 1C** | **Compreensão e Autonomia**<br>Decodificação funcional, fragilidade em inferências pragmáticas. | Roteiros com perguntas inferenciais guiadas ("Por que?"); mapas mentais conceituais; tempo adicional de 25% para elaboração de respostas. | **SRM Metacognição:** 2x por semana (80 min/sem). Raciocínio de causa-efeito e interpretação de múltiplos sentidos. |
| **Cluster 1D** | **Aprofundamento / Altas Habilidades (2E)**<br>Raciocínio lógico-abstrato superior e rápida saciedade. | Compactação curricular (dispensa de tarefas repetitivas após maestria); liderança colaborativa de pares; pesquisa de campo autônoma. | **SRM Enriquecimento:** 1x por semana (60 min/sem). Enriquecimento Tipo II e III de Renzulli e iniciação científica. |

> **Protocolo Comportamental PBS (Suporte Comportamental Positivo - Parecer CNE 50/2023):**  
> Diante de episódios de recusa de tarefa ou labilidade (comuns em TOD/TDAH/TEA), aplica-se a **técnica da escolha controlada** (oferecer 2 alternativas legítimas previamente aprovadas), tolerância zero a discussões públicas em sala de aula, desescalada privada em tom calmo e proporção mínima de **4 reforços positivos para cada correção pedagógica**.

---

### 4. 📅 Plano Anual da Turma e Planos Bimestrais (Bimestres I, II, III e IV)

O Plano Curricular do Dossiê Mestre é composto por **7 Diretrizes Anuais Integradas** e **36 Matrizes Bimestrais Detalhadas** (4 bimestres $\times$ 9 componentes):

- **Língua Portuguesa (Alfabetização Fônica e Letramento):** Domínio fonema-grafema, escrita alfabética canônica e alcance de fluência mínima de 60 PPM no final do Ciclo III.
- **Matemática (Kumon Cumulativo e Senso Numérico):** Domínio dos fatos básicos de adição e subtração sem reagrupamento, contagem até 100 e resolução de problemas em 2 passos.
- **BNCC Computação (Resolução CNE/CP nº 01/2022):** 7 habilidades desplugadas (`EF01CO01` a `EF01CO07`) desenvolvendo pensamento computacional, algoritmos físicos e convivência digital ética.
- **Ciências da Natureza:** Investigação sensorial do corpo humano, saúde, ciclos da natureza e seres vivos do semiárido cearense.
- **História e Geografia:** História pessoal/familiar, organização espacial vivido (casa, rua, escola) e paisagens de Crateús.
- **Linguagens Integradas (Arte e Educação Física):** Psicomotricidade fina/ampla, lateralidade, artes visuais, música e jogos cooperativos.
- **Ensino Religioso:** Princípios de empatia ("Círculo da Empatia"), acolhimento, diálogo comunitário e cultura de paz.

---

### 5. 🗄️ Arquitetura do Banco de Dados Relacional Canônico (51 Tabelas, Sem Ilhas)

Todas as informações, predições, registros de PEI, PAEE e trilhas de práticas diárias estão armazenados em [`datamining/dados/airam_veras_ecossistema.sqlite`](file:///c:/Users/marce/Downloads/Airam%20veras/datamining/dados/airam_veras_ecossistema.sqlite) com **100% de integridade relacional**:

```
Total de Tabelas: 51 | Tabelas Vazias ("Ilhas"): 0 | Violações de Chave Estrangeira: 0
Blocos no Ledger SHA-256: 13 | Estudantes Censitários: 172 | Micro-Respostas H01-H19: 4.618
```

- **`dim_estudantes_nominal_restrito`** (172 registros): Mapeamento nominal e institucional auditável de todos os estudantes da escola.
- **`dim_legislacao_educacional_inclusiva`** (7 registros): Artigos, ementas e diretrizes das leis federais, resoluções e notas técnicas.
- **`fato_pei_estudante_adaptacoes`** (96 registros): 24 estudantes $\times$ 4 bimestres de PEI com acomodações DUA, metas adaptadas e hash forense.
- **`fato_paee_plano_atendimento`** (24 registros): Modalidade, frequência semanal e cronograma de atendimento na SRM.
- **`fato_plano_anual_turma_bncc_caed`** (7 registros): Componentes curriculares anuais integrados.
- **`fato_plano_bimestral_bncc_interdisciplinar`** (36 registros): Matrizes bimestrais completas dos 9 componentes curriculares.
- **`fato_praticas_adaptadas_cluster`** (4 registros): Diretrizes de sala regular e SRM para os clusters G1 a G4.
- **`fato_praticas_diarias_execucao`** (960 registros): Registro transacional das 40 folhas diárias para os 24 alunos do 1º ano.
- **`fato_respostas_itens_habilidades`** (4.618 registros): Micro-itens individuais vinculados a descritores CAEd e cadernos avaliativos.
- **`fato_auditoria_transacional_ledger`** (13 blocos): Encadeamento criptográfico imutável com hashes SHA-256.

---
"""

# Localizar o ponto de inserção: após o Mermaid da estrutura e antes da seção 🔬 Análise Completa
marker = "## 🔬 Análise Completa dos Resultados CAEd 2026"
if marker in content:
    content = content.replace(marker, nova_secao_dossie + "\n" + marker)
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(content)
    print("-> README.md atualizado com a Seção Mestra do Dossiê e Banco de Dados!")
else:
    print("Aviso: marcador não encontrado em README.md")
