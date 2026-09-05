"""Shared manuscript hashing for the reviewer-calibration suite (#653).

The corpus assembler (freeze / verify) and the isolated dispatcher must hash
the SAME bytes for `pdf_sha256` and `extracted_text_sha256`, so the extraction
and normalization live here and both import it. The normalization rule is
recorded in the manifest's `extraction` block as `text_normalization` and
compared by `verify` as a hard failure — it is a rule, not a version, so drift
is never downgraded to a warning.

Rule (`TEXT_NORMALIZATION`):
  1. pypdf page texts joined with "\n" (empty pages contribute "");
  2. Unicode NFC;
  3. every lone UTF-16 surrogate code point (U+D800..U+DFFF, which pypdf can
     emit from math / symbol fonts and which strict UTF-8 refuses to encode)
     is replaced by U+FFFD REPLACEMENT CHARACTER.

Step 3 is what makes the hash computable on real manuscripts: the first ICLR
2026 freeze hit a paper whose extracted text carried 61 lone surrogates and
`str.encode("utf-8")` raised. Replacement is one-to-one, so the page/line
structure the reviewers see is unchanged.
"""

from __future__ import annotations

import hashlib
import io
import re
import unicodedata
from pathlib import Path

try:
    import pypdf
except ImportError:  # pragma: no cover - exercised only on broken envs
    pypdf = None

TEXT_NORMALIZATION = "pypdf-pages-joined-lf; NFC; lone-surrogate->U+FFFD"

_LONE_SURROGATE = re.compile("[\ud800-\udfff]")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_extracted_text(text: str) -> str:
    """Apply steps 2-3 of TEXT_NORMALIZATION to already-joined page text."""
    return _LONE_SURROGATE.sub("�", unicodedata.normalize("NFC", text))


def extract_manuscript_text(reader) -> str:
    """Steps 1-3 of TEXT_NORMALIZATION over a pypdf.PdfReader."""
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return normalize_extracted_text(text)


def extracted_text_sha256(normalized: str) -> str:
    return sha256_hex(normalized.encode("utf-8"))


def pdf_facts(
    pdf_path: Path, *, extract_text: bool = True
) -> tuple[str, str | None, int, str | None]:
    """(pdf_sha256, extracted_text_sha256, page_count, normalized_text) for a
    cached PDF, parsed from the same bytes that were hashed. With
    `extract_text=False` the text fields are None (page count only)."""
    if pypdf is None:
        raise RuntimeError("pypdf is required to hash manuscripts")
    data = pdf_path.read_bytes()
    reader = pypdf.PdfReader(io.BytesIO(data))
    if not extract_text:
        return sha256_hex(data), None, len(reader.pages), None
    normalized = extract_manuscript_text(reader)
    return sha256_hex(data), extracted_text_sha256(normalized), len(reader.pages), normalized
