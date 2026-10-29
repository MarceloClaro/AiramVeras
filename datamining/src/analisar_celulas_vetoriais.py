import pdfplumber

def analyze_pdf(pdf_path, is_leitura=True):
    print(f"\n==================== {pdf_path} ====================")
    with pdfplumber.open(pdf_path) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            print(f"\n--- PAGE {p_idx+1} ---")
            tables = page.find_tables()
            if not tables:
                print("No tables found")
                continue
            tab = tables[0]
            print(f"Table bbox: {tab.bbox}")
            print(f"Rows count: {len(tab.rows)}")
            
            # Find the header row and determine column intervals
            # Let's inspect the cells of each row
            for r_idx, row in enumerate(tab.rows):
                # row.cells is a list of (x0, top, x1, bottom) or None
                cells = row.cells
                non_empty = [c for c in cells if c is not None]
                # Check how many curves fall into each cell
                cell_marks = []
                for c_idx, cell in enumerate(cells):
                    if cell is None:
                        continue
                    x0, top, x1, bottom = cell
                    # Count curves inside this cell
                    # filter out the boundary rects
                    inside = [
                        cv for cv in page.curves
                        if (x0 + 2 <= cv['x0'] <= x1 - 2 or x0 + 2 <= cv['x1'] <= x1 - 2)
                        and (top + 2 <= cv['top'] <= bottom - 2 or top + 2 <= cv['bottom'] <= bottom - 2)
                    ]
                    if inside:
                        cell_marks.append((c_idx, len(inside), round(x0, 1), round(x1, 1)))
                if r_idx < 4:
                    print(f"Header Row {r_idx}: cells={len(cells)}, marks={cell_marks}")
                else:
                    # Student row
                    print(f"Row {r_idx:2d}: marks in cols {[m[0] for m in cell_marks]}")

analyze_pdf("SAAP- 1ANO- ESCRITA.pdf", is_leitura=False)
analyze_pdf("SAAP- 1ANO- LEITURA.pdf", is_leitura=True)
