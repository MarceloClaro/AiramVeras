---
name: pdf-report-generator
description: >-
  Compila relatórios executivos, dossiês analíticos e dashboards em PDF vetorial A4 de alta
  fidelidade no Windows sem dependências externas (C/C++, GTK, WeasyPrint), utilizando o runtime
  Chromium/Edge headless residente com controle estrito de paginação (Strict Page Budgeting) e CSS print-ready.
---

# PDF Report Generator — Zero-Dependency Pattern no Windows

Este módulo padroniza a geração de relatórios periciais, prontuários pedagógicos/médicos e dossiês executivos em PDF vetorial de alta definição diretamente no Windows.

## Princípio Fundamental
No Windows, bibliotecas Python como `weasyprint` ou `pdfkit` frequentemente falham ou exigem instalação de DLLs pesadas em C/GTK (Pango, Cairo, GObject). O padrão arquitetural comprovado consiste em:
1. Extrair os dados da base canônica (SQLite 3FN, JSON, Dataframes).
2. Renderizar um documento HTML semântico com CSS moderno otimizado para impressão (`@page`, `.page`).
3. Compilar em milissegundos para PDF via Google Chrome ou Microsoft Edge headless nativo.

## Protocolo de Execução

### 1. Invocação do Navegador Headless (CLI)
```python
import subprocess
import pathlib

# Localizar binário residente
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
]
browser_exe = next((p for p in chrome_paths if pathlib.Path(p).exists()), None)

# Comando otimizado de renderização
cmd = [
    browser_exe,
    "--headless=new",
    "--disable-gpu",
    "--no-pdf-header-footer",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={str(pdf_path.resolve())}",
    html_path.resolve().as_uri()  # OBRIGATÓRIO: passar como URI de arquivo absoluto
]
subprocess.run(cmd, check=True, timeout=30)
```

### 2. Regras de Ouro de CSS & Paginação (Strict Page Budgeting)
- **Tamanho e Margens:**
  ```css
  @page {
      size: A4 portrait;
      margin: 10mm 10mm 12mm 10mm;
      @bottom-right {
          content: "Página " counter(page) " de " counter(pages);
          font-size: 8pt;
          color: #64748b;
      }
  }
  ```
- **Controle de Quebra e Altura Rígida:**
  ```css
  .page {
      page-break-after: always;
      page-break-inside: avoid;
      height: 275mm;
      position: relative;
      overflow: hidden; /* Evita que 1 ou 2 linhas criem uma página órfã acidental */
  }
  .page:last-child {
      page-break-after: avoid;
  }
  ```
- **Tabelas com Mais de 20 Registros:**
  Utilizar classes de compactação cirúrgica (`table-compact`) com `padding: 2.5px 4px; font-size: 7pt;` para assegurar que listas completas de turmas (ex.: 24 estudantes) caibam com folga e elegância em uma única página.

### 3. Escrita de Templates em Python
- Ao embutir regras de estilo CSS dentro de f-strings (`f"""..."""`), todas as chaves de blocos CSS devem ser duplicadas (`{{` e `}}`) para prevenir `NameError` durante a interpolação.
