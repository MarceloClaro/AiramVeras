import pdfplumber
from PIL import Image

# Let's inspect the exact lines/rects in the PDF using pdfplumber!
# The PDF has vector rects and curves, which means the cell coordinates are mathematically exact!

with pdfplumber.open("SAAP- 1ANO- LEITURA.pdf") as pdf:
    for p_idx, page in enumerate(pdf.pages):
        print(f"\n--- LEITURA PAGE {p_idx+1} ---")
        # Find horizontal and vertical lines from rects / curves
        rects = page.rects
        print(f"Total rects: {len(rects)}")
        # Let's see the curves: text glyphs are curves!
        # The 'X' marks are curves! An 'X' consists of two intersecting diagonal strokes.
        # Let's find curves that form 'X' or look at their bounding boxes!
        x_marks = []
        for c in page.curves:
            # c has 'x0', 'top', 'x1', 'bottom', 'width', 'height'
            if 4 <= c['width'] <= 15 and 4 <= c['height'] <= 15:
                x_marks.append(c)
        print(f"Candidate X marks (small curves): {len(x_marks)}")
        # Let's print unique Y positions (rows) and X positions (columns)
