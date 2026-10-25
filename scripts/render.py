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

# Figure 2 is typeset Lean code rather than a standalone graphics file.
# Crop its exact printed panel from page 6 of the original arXiv PDF.
import io
import urllib.request
request = urllib.request.Request(
    f"https://arxiv.org/pdf/{ARXIV_ID}",
    headers={"User-Agent": "arxiv-paper-assets/1.0 (figure extraction)"}
)
with urllib.request.urlopen(request, timeout=120) as response:
    pdf_bytes = response.read()
paper = fitz.open(stream=pdf_bytes, filetype="pdf")
page = paper[5]
anchors = page.search_for("Figure 2:")
if not anchors:
    anchors = page.search_for("Figure 2")
if not anchors:
    raise RuntimeError("Cannot find Figure 2 caption on page 6")
caption = anchors[0]
clip = fitz.Rect(32, 35, page.rect.width - 32, min(page.rect.height - 20, caption.y1 + 48))
pix = page.get_pixmap(matrix=fitz.Matrix(2.5, 2.5), clip=clip, alpha=False)
target = figures / "figure-2-source-crop.png"
pix.save(str(target))
print(f"Cropped original Figure 2 {target} ({pix.width}x{pix.height})")
