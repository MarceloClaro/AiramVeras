# Projeto Airam Veras — Diagnóstico, Intervenção e Mineração de Dados Educacionais 2026

Repositório unificado com todos os recursos, dados, matrizes curriculares, ferramentas e pipeline analítico do **Projeto Airam Veras**.

---

## 📂 Estrutura do Repositório

O projeto reúne a infraestrutura pedagógica, bases de avaliação e o pipeline de engenharia de dados:

```
Airam veras/
├── 00_ORGANIZACAO/                                # Documentos organizacionais, relatórios e manuais pedagógicos
├── bncc-dados/                                     # Matrizes curriculares BNCC, habilidades estruturadas e metadados
├── bncc-ferramentas/                               # Ferramentas pedagógicas, interfaces e utilitários curriculares
├── caed-dados/                                     # Microdados, cadernos e registros de avaliação diagnóstica CAEd
├── CAEd_Airam_Veras_2026_Colab_SDD_TDD_PACOTE-1ANO/ # Pacotes de integração e rotinas colaborativas de 1º ano
├── datamining/                                     # Pipeline de dados, estatística psicométrica, builder XLSX e testes
│   ├── curriculo/                                  # Habilitações, cruzamentos e mapeamento CAEd x BNCC
│   ├── estatistica/                                # Modelos IRT (TRI), Teoria Clássica dos Testes e Rasch
│   ├── reports/                                    # Geradores de relatórios e builder de planilhas oficiais
│   ├── tests/                                      # Suíte de testes automatizados (T01 a T11) com cobertura TDD
│   ├── specs/                                      # Especificações técnicas e contratos de dados
│   ├── evidencias/                                 # Recibos criptográficos e relatórios de contraprova
│   └── restrito/                                   # Saídas consolidadas, bancos SQLite e dados de aplicação
├── docs/                                           # Especificações de intervenção, planos SDD e documentação
├── resultados-caed-ciclo-i-2026/                   # Resultados consolidados do Ciclo I das turmas
├── resultados-saap-ciclo-i-2026/                   # Resultados SAAP
├── spaece-dados/                                   # Dados e matrizes históricas do SPAECE
└── MEC_2026_CNCA_Av_Cont_Apren_Matriz_Ref_Defeso.pdf # Matriz de referência e documento regulatório MEC/CNCA
```

---

## 🎯 Objetivos do Projeto

1. **Diagnóstico Educacional de Precisão**:
   - Processamento psicométrico (Teoria de Resposta ao Item - TRI / Rasch) para identificar defasagens reais de aprendizagem em Língua Portuguesa e Matemática.
   - Cruzamento automatizado com a Matriz BNCC e descritores do CAEd/SPAECE.

2. **Intervenção Pedagógica Estruturada**:
   - Geração de planos de ação individualizados e por agrupamento de estudantes.
   - Planilhas operacionais e relatórios executivos para gestores e professores.

3. **Rastreabilidade e Integridade Técnica**:
   - Pipeline orientado a testes (TDD/SDD) com contraprova matemática independente.
   - Verificação criptográfica de todas as etapas de ingestão, cálculo e emissão de artefatos.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagens**: Python 3.12, JavaScript / Node.js
- **Modelagem Psicométrica**: SciPy, NumPy, Scikit-learn, Pandas
- **Persistência**: SQLite 3, JSON criptograficamente auditável
- **Geração de Artefatos**: Runtime `@oai/artifact-tool` para geração de planilhas XLSX canônicas
- **Qualidade de Software**: Pytest (360+ testes automatizados)
