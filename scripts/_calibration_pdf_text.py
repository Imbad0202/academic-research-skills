"""Shared manuscript-text normalization for the reviewer-calibration suite (#653).

The corpus assembler (freeze / verify) and the isolated dispatcher must hash
the SAME bytes for `extracted_text_sha256`, so the normalization lives here
and both import it. The rule is recorded in the manifest's `extraction`
block as `text_normalization` and compared by `verify` as a hard failure —
it is a rule, not a version, so drift is never downgraded to a warning.

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
import unicodedata

TEXT_NORMALIZATION = "pypdf-pages-joined-lf; NFC; lone-surrogate->U+FFFD"

_SURROGATE_LO = 0xD800
_SURROGATE_HI = 0xDFFF


def normalize_extracted_text(text: str) -> str:
    """Apply steps 2-3 of TEXT_NORMALIZATION to already-joined page text."""
    normalized = unicodedata.normalize("NFC", text)
    if any(_SURROGATE_LO <= ord(ch) <= _SURROGATE_HI for ch in normalized):
        normalized = "".join(
            "�" if _SURROGATE_LO <= ord(ch) <= _SURROGATE_HI else ch
            for ch in normalized
        )
    return normalized


def extract_manuscript_text(reader) -> str:
    """Steps 1-3 of TEXT_NORMALIZATION over a pypdf.PdfReader."""
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    return normalize_extracted_text(text)


def extracted_text_sha256(normalized: str) -> str:
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
