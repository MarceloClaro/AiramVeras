import sys
from pathlib import Path

def main():
    print("Iniciando inserção da Galeria de Gráficos no README.md...")

    galeria_md = """
---

## 📊 Galeria Completa de Gráficos e Evidências Analíticas das Avaliações

> Todos os gráficos, matrizes e evidências visuais gerados pelos motores analíticos (`airam/relatorio.py`, `analise_bioestatistica_avancada.py`, `gerar_dossie_mestre_ampliado_1ano.py`) e pela suíte de auditoria do CAEd/SPAECE 2026. As figuras encontram-se versionadas em alta resolução e integradas ao ecossistema.

```mermaid
graph TD
    classDef main fill:#1e3a8a,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef plot fill:#0f172a,stroke:#10b981,stroke-width:2px,color:#fff;
    classDef dash fill:#581c87,stroke:#a855f7,stroke-width:2px,color:#fff;
    classDef evid fill:#701a75,stroke:#ec4899,stroke-width:2px,color:#fff;

    G["📊 Ecossistema Gráfico e Analítico (16 Figuras Principais)"]:::main
    G --> G1["1. Gráficos Psicométricos Matplotlib / SciPy"]:::plot
    G --> G2["2. Painéis Executivos e Simulações SPA / D3.js"]:::dash
    G --> G3["3. Evidências Documentais Oficiais (CAEd/SPAECE/CNCA)"]:::evid

    G1 --> P1["Meta A (80%) por Ano e Componente"]
    G1 --> P2["Cobertura Censitária nas Unidades Originais"]
    G1 --> P3["Heatmap Cividis de Habilidades H01-H19"]

    G2 --> D1["Coorte Censitária e Fila de Conversão"]
    G2 --> D2["Simulador What-If das Metas A e B"]
    G2 --> D3["Grafo Curricular Fônico e Kumon"]
    G2 --> D4["Painel de Intervenção EWS e Manejos AEE"]
    G2 --> D5["Cadeia de Markov Longitudinal (C1-C3)"]
    G2 --> D6["Radar Raio-X e Bioestatística Multivariada"]

    G3 --> E1["Conferência Matemática CAEd 2026"]
    G3 --> E2["Conferência SPAECE Alfabetização"]
    G3 --> E3["Boletim SAAP 1º Ano Ciclo I"]
    G3 --> E4["Matrizes Oficiais de Itens (Págs 07, 23, 25, 27)"]
```

---

### 1. 📈 Gráficos Centrais das Avaliações CAEd (T10 / Metas A e B)

#### 🎯 Meta A e Distância Institucional por Ano e Componente
Proporção de estudantes classificados no nível **Adequado** no CAEd em relação ao teto institucional da **Meta A (80%)**. O 1º Ano (Matemática e Leitura) e o 3º Ano atingiram ou superaram a meta de referência, enquanto o 4º e 5º Anos em Matemática compõem a fila prioritária do Plano de Intervenção Pedagógica (PIP).

![Meta A e Distância Institucional por Ano e Componente](docs/figuras/analises/meta-a-distancia-institucional.png)

*Figura 1: Proporção de adequados CAEd entre avaliados vs. linha de referência da Meta A (80%). Gerado autonomamente por `airam/relatorio.py`.*

---

#### 📋 Cobertura Censitária e Disponibilidade nas Unidades Originais
Comparação entre o universo total de alunos cadastrados e os estudantes com resultado válido disponível por componente curricular avaliado (Leitura, Matemática, Escrita e Fluência Leitora).

![Cobertura Censitária nas Unidades Originais](docs/figuras/analises/cobertura-censitaria-componentes.png)

*Figura 2: Total de cadastros escolares vs. avaliações com resultado disponível por componente curricular nas unidades originais do CAEd.*

---

#### 🗺️ Heatmap de Acertos e Oportunidades por Bloco Curricular (Cividis)
Matriz bidimensional cruzando cada ano escolar e componente com as posições de habilidades avaliadas (**H01 a H19**). Cada célula exibe a razão empírica $C/D$ (acertos / oportunidades), variando de 0.0 (amarelo claro/defasagem) a 1.0 (azul escuro/domínio consolidado).

![Heatmap de Habilidades C/D por Bloco](docs/figuras/analises/heatmap-habilidades-matriz-cd.png)

*Figura 3: Heatmap de taxa de acerto por bloco curricular contextualizado (escala Cividis 0 a 1). Identifica nós críticos de aprendizagem sem inferência ecológica.*

---

### 2. 🖥️ Painéis Interativos e Simulações do Ecossistema Web (Dashboard SPA)

#### 👥 Painel 1: Coorte Censitária Geral e Fila de Conversão
Visão macro da distribuição de proficiência dos 172 estudantes nas turmas regulares e turmas de AEE, demonstrando o contingente em cada nível (Abaixo do Básico, Básico, Adequado e Avançado).

![Painel de Análise da Coorte Geral](docs/figuras/analises/painel-analise-coorte-geral.png)

*Figura 4: Painel Executivo da Coorte Censitária da Escola Airam Veras 2026 no Dashboard SPA.*

---

#### 🎲 Painel 2: Diagnóstico Oficial das Metas A e B com Simulador What-If
Mesa de trabalho dinâmica que simula o impacto de intervenções pedagógicas pontuais na taxa de conversão institucional da Meta A (80% adequado) e Meta B (80%+ de acertos individuais).

![Painel de Metas A e B com Simulador](docs/figuras/analises/painel-analise-metas-a-b.png)

*Figura 5: Simulador de Sensibilidade e Conversão das Metas A e B por Turma e Componente.*

---

#### 🕸️ Painel 3: Grafo Curricular de Habilidades & Progressão Fônico/Kumon em Rede
Topologia curricular em rede que estrutura os pré-requisitos pedagógicos da alfabetização fônica e raciocínio lógico-matemático (níveis A a F do Kumon adaptado).

![Painel do Grafo Curricular em Rede](docs/figuras/analises/painel-analise-grafo-curricular.png)

*Figura 6: Grafo Curricular Interdisciplinar conectando habilidades BNCC, descritores CAEd e trilhas de progressão.*

---

#### 🧠 Painel 4: Intervenção Pedagógica, Early Warning System (EWS) e Manejos AEE
Monitoramento preventivo de evasão e defasagem acadêmica (EWS) conjugado à matriz de manejos clínicos e psiconeuropedagógicos por CID (TOD/PBS, TDAH, TEA, Dislexia, Paralisia Cerebral e Altas Habilidades).

![Painel de Intervenção Pedagógica e AEE](docs/figuras/analises/painel-analise-intervencao-aee.png)

*Figura 7: Painel de Acompanhamento Individualizado, AEE e Alertas Precoces de Defasagem (EWS).*

---

#### 🔄 Painel 5: Trajetória Longitudinal e Matriz de Transição de Markov
Acompanhamento dos ciclos avaliativos (Ciclo I Diagnóstico ➔ Ciclo II Formativo ➔ Ciclo III Somativo) modelado por Cadeias de Markov com matriz estocástica de probabilidades de transição entre níveis de proficiência.

![Painel de Trajetória Longitudinal e Markov](docs/figuras/analises/painel-analise-markov-longitudinal.png)

*Figura 8: Matriz de Transição de Markov e Projeção Longitudinal dos 3 Ciclos Avaliativos 2026.*

---

#### 🧬 Painel 6: Raio-X Universal Neurocognitivo & Bioestatística Multivariada
Visualização integrada dos 7 domínios neurocognitivos (Atenção Sustentada, Memória de Trabalho, Funções Executivas, Fluência Fonológica, Senso Numérico, Coordenação Visomotora e Cognição Social) articulados ao modelo RTI em 3 Camadas.

![Painel de Raio-X Cognitivo e Bioestatística](docs/figuras/analises/painel-analise-raiox-bioestatistica.png)

*Figura 9: Raio-X Cognitivo Interdisciplinar, RTI e painel de inferência bioestatística (ANOVA, Kruskal-Wallis e Fisher).*

---

### 3. 📑 Evidências Oficiais de Coleta, Conferência e Matrizes de Referência

Para auditoria forense e rastreabilidade irrefutável, o ecossistema armazena e cruza os espelhos originais de conferência emitidos pelas bancas aplicadoras:

| Evidência Oficial | Instrumento / Âmbito | Registro no Repositório | Finalidade e Descrição |
|:---|:---:|:---:|:---|
| **Conferência CAEd Matemática** | Diagnóstica 2026 | [`docs/figuras/analises/caed-conferencia-oficial-matematica.png`](docs/figuras/analises/caed-conferencia-oficial-matematica.png) | Espelho censitário oficial emitido pelo CAEd com contagens brutas e confirmação de participação escolar. |
| **Conferência SPAECE Alfabetização** | SPAECE / Alfa | [`docs/figuras/analises/spaece-conferencia-oficial-alfabetizacao.png`](docs/figuras/analises/spaece-conferencia-oficial-alfabetizacao.png) | Ata de aplicação e verificação de proficiência em leitura e alfabetização inicial do SPAECE. |
| **Boletim Diagnóstico SAAP 1º Ano** | Ciclo I 2026 | [`docs/figuras/analises/saap-ciclo1-1ano-boletim.jpg`](docs/figuras/analises/saap-ciclo1-1ano-boletim.jpg) | Boletim consolidado da turma de 1º Ano no Sistema de Avaliação da Aprendizagem Permanente (SAAP). |
| **Matriz Oficial CNCA (Pág. 07)** | MEC / Compromisso | [`docs/figuras/analises/matriz-cnca-pagina-07.png`](docs/figuras/analises/matriz-cnca-pagina-07.png) | Matriz de habilidades essenciais do Compromisso Nacional Criança Alfabetizada (CNCA). |
| **Caderno de Prova CAEd (Págs. 23, 25 e 27)** | Matriz de Descritores | `docs/figuras/analises/matriz-caed-caderno-itens-p2*.png` | Caderno original de itens com correspondência direta aos descritores de Língua Portuguesa e Matemática. |

<div align="center">

#### Espelho Oficial de Conferência Censitária CAEd Matemática 2026
![Conferência Oficial CAEd Matemática](docs/figuras/analises/caed-conferencia-oficial-matematica.png)

#### Ata Oficial de Aplicação SPAECE Alfabetização
![Conferência Oficial SPAECE](docs/figuras/analises/spaece-conferencia-oficial-alfabetizacao.png)

#### Boletim Diagnóstico SAAP Ciclo I — 1º Ano Ensino Fundamental
![Boletim Oficial SAAP Ciclo I 1º Ano](docs/figuras/analises/saap-ciclo1-1ano-boletim.jpg)

#### Matriz Oficial de Habilidades CNCA (Página 07)
![Matriz CNCA Página 07](docs/figuras/analises/matriz-cnca-pagina-07.png)

#### Caderno de Itens e Descritores CAEd (Páginas 23, 25 e 27)
| Página 23 | Página 25 | Página 27 |
|:---:|:---:|:---:|
| ![CAEd p23](docs/figuras/analises/matriz-caed-caderno-itens-p23.png) | ![CAEd p25](docs/figuras/analises/matriz-caed-caderno-itens-p25.png) | ![CAEd p27](docs/figuras/analises/matriz-caed-caderno-itens-p27.png) |

</div>

---
"""

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    target = "## 🔬 Análise Completa dos Resultados CAEd 2026, Inferência Bioestatística Avançada e Raio-X Universal Neurocognitivo"

    if target in content:
        new_content = content.replace(target, galeria_md + "\n" + target, 1)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("-> Galeria de Gráficos e Evidências inserida no README.md com sucesso!")
    else:
        print("Target não encontrado no README.md!")

if __name__ == "__main__":
    main()
