import pdfplumber

with pdfplumber.open("SAAP- 1ANO- LEITURA.pdf") as pdf:
    p2 = pdf.pages[1]
    # Header cells of row 2 (subcolumns)
    tab = p2.find_tables()[0]
    subcols = tab.rows[2].cells
    print("Subcol headers bounding boxes:")
    for i, c in enumerate(subcols):
        if c:
            print(f"  Col {i:2d}: [{c[0]:.1f}, {c[2]:.1f}]")
    
    # Let's inspect rows 4 to 8 of tab
    names = [
        "Header", "Header", "Header", "Header",
        "MARIA LETICIA MARTINS DA SILVA",
        "MARIA SOPHIA MARQUES SILVA",
        "MARIA YORRANA OLIVEIRA ARAUJO",
        "MOISES TOLEDO DE SOUSA",
        "RUAN LUCAS DE SOUZA SALES"
    ]
    for r_idx in range(4, len(tab.rows)):
        r = tab.rows[r_idx]
        row_name = names[r_idx] if r_idx < len(names) else f"Row {r_idx}"
        print(f"\n--- {row_name} (Row {r_idx}) ---")
        for c_idx, cell in enumerate(r.cells):
            if cell is None:
                continue
            x0, top, x1, bottom = cell
            # Check curves inside cell
            inside = [
                cv for cv in p2.curves
                if (x0 + 1 <= cv['x0'] <= x1 - 1 or x0 + 1 <= cv['x1'] <= x1 - 1)
                and (top + 1 <= cv['top'] <= bottom - 1 or top + 1 <= cv['bottom'] <= bottom - 1)
            ]
            if inside:
                print(f"  Col {c_idx:2d} [{x0:.1f} - {x1:.1f}]: MARCA ENCONTRADA ({len(inside)} curves)")
