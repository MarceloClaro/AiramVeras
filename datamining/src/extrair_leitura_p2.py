import pdfplumber

def extract_saap_leitura():
    results = []
    col_map = {
        # 1o Bimestre
        1: ("1B", "NL"), 2: ("1B", "LS"), 3: ("1B", "LP"), 4: ("1B", "LF"), 5: ("1B", "LTSF"), 6: ("1B", "LTF"),
        # 2o Bimestre
        7: ("2B", "NL"), 8: ("2B", "LS"), 9: ("2B", "LP"), 10: ("2B", "LF"), 11: ("2B", "LTSF"), 12: ("2B", "LTF"),
        # 3o Bimestre
        13: ("3B", "NL"), 14: ("3B", "LS"), 15: ("3B", "LP"), 16: ("3B", "LF"), 17: ("3B", "LTSF"), 18: ("3B", "LTF"),
        # 4o Bimestre
        19: ("4B", "NL"), 20: ("4B", "LS"), 21: ("4B", "LP"), 22: ("4B", "LF"), 23: ("4B", "LTSF"), 24: ("4B", "LTF")
    }

    with pdfplumber.open("SAAP- 1ANO- LEITURA.pdf") as pdf:
        # Page 1
        p1 = pdf.pages[0]
        t1 = p1.find_tables()[0]
        # In p1, col 0 is student name, cols 1..18 are 1B, 2B, 3B
        # Let's inspect each row from row 3
        # Let's verify student list for p1
        p1_names = [
            "ANTONIO CALLEBY PEREIRA LIMA",
            "DANIEL CONCEICAO PIMENTEL",
            "EMANUELLY DO NASCIMENTO BEZERRA",
            "FRANCISCA ADILA CAXIAS DE ALMEIDA",
            "FRANCISCO MIGUEL MARTINS DE SOUSA",
            "GUSTAVO HENRIQUE MORENO DA SILVA",
            "GUSTAVO SALES MACHADO",
            "ISABELLA MARTINS FEITOSA",
            "ISAC LUCCA FERNANDES MARTINS",
            "ISIS GOMES MESQUITA",
            "ISIS KETLEN SOUSA DA SILVA",
            "JOSE YHUDY BENICIO FERREIRA DE ANDRADE",
            "LIVYA MARIA ALVES MELO",
            "LUNNA DE SOUSA SILVA",
            "MARIA AGATHA DE SOUSA NEVES",
            "MARIA ISIS DA CONCEICAO DE SOUSA",
            "MARIA ISIS PEREIRA GOMES",
            "MARIA JULIANA VIEIRA GOMES"
        ]
        
        # Page 2 names:
        p2_names = [
            "MARIA LETICIA MARTINS DA SILVA",
            "MARIA SOPHIA MARQUES SILVA",
            "MARIA YORRANA OLIVEIRA ARAUJO",
            "MOISES TOLEDO DE SOUSA",
            "RUAN LUCAS DE SOUZA SALES"
        ]
        
        # Let's inspect page 2 with exact curve bounding boxes
        p2 = pdf.pages[1]
        t2 = p2.find_tables()[0]
        print("Page 2 table rows:", len(t2.rows))
        for idx, name in enumerate(p2_names):
            r = t2.rows[idx + 3] # rows 0,1,2 are headers
            row_marks = {}
            for c_idx in range(1, len(r.cells)):
                cell = r.cells[c_idx]
                if not cell:
                    continue
                x0, top, x1, bottom = cell
                # check curves inside
                inside = [
                    cv for cv in p2.curves
                    if (x0 + 1 <= cv['x0'] <= x1 - 1 or x0 + 1 <= cv['x1'] <= x1 - 1)
                    and (top + 1 <= cv['top'] <= bottom - 1 or top + 1 <= cv['bottom'] <= bottom - 1)
                ]
                if inside:
                    bim, niv = col_map.get(c_idx, (f"col{c_idx}", "UNK"))
                    row_marks[bim] = niv
            print(f"{name}: {row_marks}")

extract_saap_leitura()
