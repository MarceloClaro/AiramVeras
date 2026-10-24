# Portal de Ingestão e Resultados CAEd / CNCA: Ciclo III de 2026 (AV32026)

Escola: **AIRAM VERAS ESC CID** | Código INEP: **23084995** | Município: **Tianguá - CE** | Rede: **Municipal**

---

## 📥 Como Baixar os Dados Oficiais do Ciclo III (Final do Ano Letivo)

Esta pasta foi projetada para receber e custodiar os arquivos brutos do **Ciclo III / 2026** (identificador oficial no portal: **`AV32026`**).

### Passo a Passo para o Coordenador / Técnico de TI:
1. Acesse o portal oficial da avaliação do CAEd / Criança Alfabetizada: `https://avaliacaoemonitoramentocaed.net.br`
2. Faça login com as credenciais da escola ou da SME.
3. No menu lateral, acesse **Exportação de Dados** / **Downloads**.
4. Selecione os filtros mandatórios:
   - **Edição / Ciclo**: `2026 - Ciclo III` (código `AV32026`)
   - **Município**: `Tianguá`
   - **Escola**: `AIRAM VERAS ESC CID (23084995)`
5. Baixe os arquivos ZIP por componente curricular para cada ano escolar (1º ao 5º ano):
   - **Língua Portuguesa (Leitura)**
   - **Matemática**
   - **Produção de Escrita** (2º ao 5º ano)
   - **Fluência Leitora** (2º ao 5º ano)
6. **Deposite os arquivos ZIP baixados diretamente na pasta**:
   `resultados-caed-ciclo-iii-2026/originais/`
7. Execute o pipeline de extração, análise longitudinal e fechamento anual:
   ```bash
   python -m datamining.src.ingestao_multiciclos --ciclo III
   ```

---

## 📁 Estrutura desta Pasta

- `originais/`: Diretório de custódia dos arquivos ZIP oficiais brutos baixados da plataforma CAEd.
- `csv_originais/`: Subpastas com os CSVs extraídos (escola, turma, estudante e respostas item a item).
- `conferencia/`: Relatório de validação criptográfica (CRC32, SHA-256 e contagem de registros).
- `manifesto_coleta.json`: Manifesto de linhagem contendo hashes, data/hora da exportação e operador.

---

## 🔒 Governança e LGPD (Lei nº 13.709/2018)

Os arquivos brutos do portal contêm nomes e dados pessoais de estudantes. Esta pasta é de acesso restrito aos operadores autorizados da escola. O pipeline converterá automaticamente qualquer identificador para pseudônimos criptográficos (`aluno_hash_id`) antes de alimentar os relatórios públicos e dashboards.
