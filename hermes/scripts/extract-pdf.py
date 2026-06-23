#!/usr/bin/env python
"""Extract text from a PDF for Hermes academic workflows.

Usage:
  python hermes/scripts/extract-pdf.py manuscript.pdf [out.txt]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except Exception as exc:  # pragma: no cover
    print(f"ERROR: PyMuPDF is required (pip install pymupdf): {exc}", file=sys.stderr)
    sys.exit(2)

if len(sys.argv) < 2:
    print("Usage: extract-pdf.py manuscript.pdf [out.txt]", file=sys.stderr)
    sys.exit(2)

pdf = Path(sys.argv[1])
if not pdf.exists():
    print(f"ERROR: file not found: {pdf}", file=sys.stderr)
    sys.exit(1)

out = Path(sys.argv[2]) if len(sys.argv) > 2 else pdf.with_suffix(".extracted.txt")

doc = fitz.open(str(pdf))
parts: list[str] = []
for i, page in enumerate(doc, start=1):
    parts.append(f"\n\n===== PAGE {i} =====\n")
    parts.append(page.get_text("text") or "")
text = "".join(parts)
out.write_text(text, encoding="utf-8")
words = len(re.findall(r"\b\w+\b", text))
print(f"PDF: {pdf}")
print(f"Pages: {doc.page_count}")
print(f"Chars: {len(text)}")
print(f"Words: {words}")
print(f"Output: {out}")
