#!/usr/bin/env python3
"""Render original arXiv figure PDFs and paper figure panels into PNG images."""
import re
import urllib.request
from pathlib import Path
import fitz

ARXIV_ID = "2610.20981"
root = Path("assets") / ARXIV_ID
figures = root / "figures"
figures.mkdir(parents=True, exist_ok=True)

def render(source, target):
    doc = fitz.open(str(source))
    if not len(doc): return
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
    pix.save(str(target))
    print("Rendered", target)

for source in figures.glob("*.pdf"):
    render(source, source.with_suffix(".png"))

# Figures 2, 3, 5 consist primarily of typeset pseudocode/equations rather
# than standalone graphics assets, so crop the exact figure region from the paper.
url = f"https://arxiv.org/pdf/{ARXIV_ID}"
request = urllib.request.Request(url, headers={"User-Agent":"arxiv-paper-assets/1.0"})
paper_bytes = urllib.request.urlopen(request, timeout=120).read()
doc = fitz.open(stream=paper_bytes, filetype="pdf")
for n in (2, 3, 5):
    found = False
    for page_no, page in enumerate(doc):
        text = page.get_text()
        anchors = list(page.search_for(f"Figure {n}."))
        if not anchors:
            anchors = list(page.search_for(f"Figure {n}"))
        if not anchors:
            continue
        caption = anchors[0]
        # Use the source PDF's actual figure layout above the caption.
        # Restrict to the same column for two-column papers and include
        # the full width where a caption spans both columns.
        half = page.rect.width / 2
        col_left = 0 if caption.x0 < half else half
        col_right = half if caption.x0 < half else page.rect.width
        clip = fitz.Rect(col_left + 15, max(30, caption.y0 - 265), col_right - 15, min(page.rect.height - 20, caption.y1 + 70))
        if clip.width < 50 or clip.height < 50: continue
        pix = page.get_pixmap(matrix=fitz.Matrix(2.5,2.5), clip=clip, alpha=False)
        dest = figures / f"paper_figure_{n}_crop.png"
        pix.save(str(dest))
        print("Cropped",dest,"page",page_no+1, "bounds",clip)
        found = True
        break
    if not found:
        print("WARNING: missing caption for Figure",n)
