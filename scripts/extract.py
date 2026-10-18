#!/usr/bin/env python3
"""Download an arXiv source archive and publish its original figure assets."""
import argparse
import io
import json
import re
import tarfile
import urllib.request
from pathlib import Path

EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".pdf", ".eps", ".webp"}

def safe_extract(archive, destination):
    destination = destination.resolve()
    for member in archive.getmembers():
        target = (destination / member.name).resolve()
        if not target.is_relative_to(destination) or member.issym() or member.islnk():
            raise ValueError("Unsafe archive member: " + member.name)
    archive.extractall(destination)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("arxiv_id")
    args = parser.parse_args()
    paper_id = args.arxiv_id.strip()
    if not re.fullmatch(r"\d{4}\.\d{4,5}(v\d+)?", paper_id):
        raise ValueError("Invalid arXiv ID")
    root = Path("assets") / paper_id
    source_dir = root / "source"
    source_dir.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request("https://arxiv.org/src/" + paper_id, headers={"User-Agent": "arxiv-paper-assets/1.0 (academic figure extraction)"})
    with urllib.request.urlopen(req, timeout=120) as response:
        data = response.read(100 * 1024 * 1024 + 1)
    if len(data) > 100 * 1024 * 1024:
        raise ValueError("Source archive too large")
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            safe_extract(archive, source_dir)
    except tarfile.ReadError:
        (source_dir / "source.tex").write_bytes(data)
    tex_files = list(source_dir.rglob("*.tex"))
    references = []
    for tex in tex_files:
        content = tex.read_text(encoding="utf-8", errors="replace")
        for match in re.finditer(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", content):
            references.append({"tex": str(tex.relative_to(source_dir)), "graphic": match.group(1)})
    figures = root / "figures"
    figures.mkdir(exist_ok=True)
    import shutil
    manifest = []
    for file in source_dir.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in EXTENSIONS:
            continue
        relative = file.relative_to(source_dir)
        target = figures / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, target)
        manifest.append({"file": str(target), "raw_url": "https://raw.githubusercontent.com/lishangli/arxiv-paper-assets/orgin/" + str(target)})
    (root / "manifest.json").write_text(json.dumps({"arxiv_id": paper_id, "figures": manifest, "latex_references": references}, indent=2), encoding="utf-8")
    print(f"Extracted {len(manifest)} figure assets; found {len(references)} LaTeX references")

if __name__ == "__main__":
    main()
