import zipfile
import xml.etree.ElementTree as ET
import sqlite3
import re
import unicodedata

def normalizar_nome(nome):
    if not nome:
        return ""
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('ASCII')
    nome = re.sub(r'[^a-zA-Z\s]', '', nome)
    return ' '.join(nome.upper().split())

def extrair_alunos_docx():
    docx_path = r'C:\Users\marce\Downloads\Airam veras\RELAÇÃO CUIDADORESALUNOS AEE 2026 AIRAN VERAS (2).docx'
    with zipfile.ZipFile(docx_path) as z:
        xml_content = z.read('word/document.xml')
    tree = ET.fromstring(xml_content)
    namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

    registros = []
    
    # Processar tabela
    for table in tree.findall('.//w:tbl', namespaces):
        rows = table.findall('.//w:tr', namespaces)
        for r_idx, row in enumerate(rows):
            cells = [ ''.join(node.text for node in cell.findall('.//w:t', namespaces) if node.text).strip() for cell in row.findall('.//w:tc', namespaces) ]
            if len(cells) >= 5 and cells[0] not in ['Nº', 'Turma', '']:
                # Possível linha de dados
                registros.append({
                    'origem': 'tabela',
                    'numero': cells[0] if len(cells) > 5 else '',
                    'turma': cells[1] if len(cells) > 5 else cells[0],
                    'nome': cells[2] if len(cells) > 5 else cells[1],
                    'apoiadores': cells[3] if len(cells) > 5 else cells[2],
                    'contatos': cells[4] if len(cells) > 5 else cells[3],
                    'cid': cells[5] if len(cells) > 5 else cells[4]
                })

    # Processar paragrafos caso a tabela esteja fragmentada
    # Vamos extrair linhas de texto dos paragrafos
    linhas_p = []
    for p in tree.findall('.//w:p', namespaces):
        t = ''.join(node.text for node in p.findall('.//w:t', namespaces) if node.text).strip()
        if t:
            linhas_p.append(t)

    return registros, linhas_p

def main():
    registros, linhas_p = extrair_alunos_docx()
    print(f"Total registros extraidos da tabela: {len(registros)}")

    conn = sqlite3.connect('datamining/dados/airam_veras_ecossistema.sqlite')
    cur = conn.cursor()

    cur.execute("SELECT id, aluno_hash_id, nome_estudante, ano_escolar, turma_nome FROM fato_praticas_diarias_leitura_fluencia;")
    alunos_banco = cur.fetchall()
    print(f"Total alunos no banco (fato_praticas): {len(alunos_banco)}")

    banco_map = {}
    for r in alunos_banco:
        norm = normalizar_nome(r[2])
        banco_map[norm] = {
            'id': r[0],
            'hash_id': r[1],
            'nome': r[2],
            'ano': r[3],
            'turma': r[4]
        }

    # Analisar parágrafos para capturar a lista completa com número, turma, nome, apoiador, contato e CID
    # O arquivo tem a estrutura em parágrafos:
    # 01 \n 1º Ano \n Daniel Conceição Pimentel \n Ryan Soares Silva MANHA- TARDE \n 88-9622-7324 \n CID 10: F 90.0 CID 11: 6A05
    alunos_docx_completos = []
    
    # Vamos fazer um parser robusto dos parágrafos
    i = 0
    while i < len(linhas_p):
        texto = linhas_p[i]
        # Detectar número de item como '01', '02', '55'
        if re.match(r'^\d{2}$', texto):
            num = texto
            turma = linhas_p[i+1] if i+1 < len(linhas_p) else ""
            nome = linhas_p[i+2] if i+2 < len(linhas_p) else ""
            apoiador = linhas_p[i+3] if i+3 < len(linhas_p) else ""
            
            # Pode haver varias linhas de apoiador/contato antes do CID
            j = i + 4
            contatos = []
            cid_linhas = []
            while j < len(linhas_p) and not re.match(r'^\d{2}$', linhas_p[j]) and 'TRIAGEM' not in linhas_p[j]:
                if any(k in linhas_p[j].upper() for k in ['CID', 'DIABETES', 'F84', 'F90', 'G40', 'Q02', 'Q37', 'G80']):
                    cid_linhas.append(linhas_p[j])
                elif re.search(r'\d{2}-\d+', linhas_p[j]) or re.search(r'\d{8,}', linhas_p[j]):
                    contatos.append(linhas_p[j])
                else:
                    if not cid_linhas:
                        apoiador += " / " + linhas_p[j]
                    else:
                        cid_linhas.append(linhas_p[j])
                j += 1
            
            alunos_docx_completos.append({
                'num': num,
                'turma': turma,
                'nome': nome,
                'apoiador': apoiador,
                'contato': ' | '.join(contatos),
                'cid': ' '.join(cid_linhas)
            })
            i = j
        else:
            i += 1

    print(f"Total alunos detectados via parser sequencial: {len(alunos_docx_completos)}")
    for a in alunos_docx_completos[:10]:
        print(f"#{a['num']} [{a['turma']}] {a['nome']} | Apoio: {a['apoiador']} | CID: {a['cid']}")

    # Detectar alunos em triagem
    triagem = []
    in_triagem = False
    for l in linhas_p:
        if 'TRIAGEM' in l.upper():
            in_triagem = True
            continue
        if in_triagem:
            if l.strip():
                triagem.append(l.strip())

    print(f"\nAlunos em Triagem ({len(triagem)}):")
    for t in triagem:
        print(" -", t)

    # Cruzar com banco de dados
    print("\n=== CRUZAMENTO COM BANCO CANÔNICO ===")
    matches = 0
    nao_encontrados = []
    for a in alunos_docx_completos:
        norm = normalizar_nome(a['nome'])
        if norm in banco_map:
            matches += 1
        else:
            # Busca aproximada
            achou = False
            for b_norm, b_data in banco_map.items():
                if norm in b_norm or b_norm in norm:
                    matches += 1
                    achou = True
                    break
            if not achou:
                nao_encontrados.append(a)

    print(f"Total com match no banco: {matches} / {len(alunos_docx_completos)}")
    if nao_encontrados:
        print(f"Alunos não localizados exatamente pelo nome ({len(nao_encontrados)}):")
        for ne in nao_encontrados:
            print(f" -> #{ne['num']} [{ne['turma']}] {ne['nome']}")

    conn.close()

if __name__ == '__main__':
    main()
