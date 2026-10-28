import zipfile
import xml.etree.ElementTree as ET
import sqlite3
import unicodedata
import re

def norm(text):
    if not text:
        return ""
    text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII')
    return re.sub(r'[^A-Z0-9\s]', '', text.upper()).strip()

def extrair_tabela_docx():
    docx_path = r'C:\Users\marce\Downloads\Airam veras\RELAÇÃO CUIDADORESALUNOS AEE 2026 AIRAN VERAS (2).docx'
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    itens = []
    for table in tree.findall('.//w:tbl', namespaces):
        for row in table.findall('.//w:tr', namespaces):
            cells = [ ''.join(node.text for node in cell.findall('.//w:t', namespaces) if node.text).strip() for cell in row.findall('.//w:tc', namespaces) ]
            if len(cells) >= 5:
                # Se for cabecalho, pular
                if 'NOME' in cells[1].upper() or 'NOME' in cells[2].upper():
                    continue
                # Formato: [Nº, Turma, Nome, Apoiador, Contato, CID]
                itens.append(cells)
    return itens

def main():
    tabela = extrair_tabela_docx()
    print(f"Total linhas na tabela do docx: {len(tabela)}")
    
    conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')
    cur = conn.cursor()
    cur.execute("SELECT id, aluno_hash_id, nome_estudante, ano_escolar, turma_nome FROM fato_praticas_diarias_leitura_fluencia;")
    banco_alunos = cur.fetchall()

    print("\n--- BUSCA DOS 4 ALUNOS NÃO LOCALIZADOS DIRETAMENTE ---")
    buscas = ["ANTONY", "JOHN", "KENNED", "MAYZA", "MAYSA", "MAIZA", "CARLOS ALBERTO", "LOUISE", "GUSTAVO SALES"]
    for b in buscas:
        encontrados = [a for a in banco_alunos if b in norm(a[2])]
        print(f"Termo '{b}': {len(encontrados)} encontrados -> {[a[2] + ' (' + str(a[3]) + 'º ' + a[4] + ')' for a in encontrados]}")

    print("\n--- LISTAGEM COMPLETA DAS LINHAS DA TABELA DO DOCX ---")
    for i, row in enumerate(tabela):
        print(f"[{i+1}] " + ' | '.join(row))

    conn.close()

if __name__ == '__main__':
    main()
