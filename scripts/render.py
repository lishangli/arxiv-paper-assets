#!/usr/bin/env python3
"""Render source figure PDFs into PNGs without altering their contents."""
from pathlib import Path
import fitz

ARXIV_ID = "2610.30188"
figures = Path("assets") / ARXIV_ID / "figures"
for source in sorted(figures.rglob("*.pdf")):
    doc = fitz.open(str(source))
    if not len(doc):
        continue
    target = source.with_suffix(".png")
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(2.4, 2.4), alpha=False)
    pix.save(str(target))
    print(f"Rendered {target} ({pix.width}x{pix.height})")
