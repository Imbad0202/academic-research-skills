#!/usr/bin/env python3
"""SETUP cross-model example parity lint (#491 fold-in).

The quick-setup bash blocks in docs/SETUP.md + docs/SETUP.zh-TW.md hardcode
verifier model IDs (`ARS_CROSS_MODEL="..."`) because they are literal export
strings a user pastes — they cannot be made version-agnostic the way the
canonical doc's primary row was. That makes them a drift surface: the
gpt-5.4→gpt-5.5 lineup migration (2026-06-10, F-003) fixed the canonical doc
but missed SETUP for three weeks (B4-F02, audits/harness-retirement-2026-07-04.md).

This lint pins the two invariants that broke:

1. **en/zh-TW parity** — both SETUP files must carry the same set of
   `ARS_CROSS_MODEL` example values (the zh-TW file mirrors the bash block
   verbatim; a one-sided edit is drift).
2. **canonical membership** — every example value must appear (backticked)
   in shared/cross_model_verification.md, the single source of truth for the
   supported lineup. A SETUP example naming a model the canonical doc no
   longer lists is exactly the B4-F02 failure.

Fail-closed: finding zero ARS_CROSS_MODEL examples in a SETUP file is an
error (the extraction regex went stale), never a silent pass.

Exit codes: 0 on pass, 1 on any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

SETUP_EN = REPO_ROOT / "docs/SETUP.md"
SETUP_ZH = REPO_ROOT / "docs/SETUP.zh-TW.md"
CANONICAL = REPO_ROOT / "shared/cross_model_verification.md"

# Matches active and commented example lines alike:
#   export ARS_CROSS_MODEL="gpt-5.5"
#   # or: export ARS_CROSS_MODEL="gemini-3.1-pro-preview"
ASSIGNMENT_RE = re.compile(r'ARS_CROSS_MODEL="([^"]+)"')

# Canonical membership = the ID appears backticked anywhere in the canonical
# doc (supported-model table or compat-provider table).
def _backticked(canonical_text: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", canonical_text))


def extract_ids(setup_text: str) -> list[str]:
    """All ARS_CROSS_MODEL example values in a SETUP file, in order."""
    return ASSIGNMENT_RE.findall(setup_text)


def check(en_text: str, zh_text: str, canonical_text: str) -> list[str]:
    errors: list[str] = []
    en_ids = extract_ids(en_text)
    zh_ids = extract_ids(zh_text)

    for label, ids in (("docs/SETUP.md", en_ids), ("docs/SETUP.zh-TW.md", zh_ids)):
        if not ids:
            errors.append(
                f"{label}: no ARS_CROSS_MODEL example values found — either the "
                f"quick-setup block was removed or the extraction regex went "
                f"stale. Fail-closed per lint contract."
            )

    if en_ids and zh_ids and set(en_ids) != set(zh_ids):
        errors.append(
            f"SETUP en/zh-TW ARS_CROSS_MODEL example drift: "
            f"en={sorted(set(en_ids))} zh-TW={sorted(set(zh_ids))}. The two "
            f"quick-setup bash blocks must carry the same example values."
        )

    known = _backticked(canonical_text)
    for label, ids in (("docs/SETUP.md", en_ids), ("docs/SETUP.zh-TW.md", zh_ids)):
        for model_id in ids:
            if model_id not in known:
                errors.append(
                    f"{label}: ARS_CROSS_MODEL example {model_id!r} does not "
                    f"appear in shared/cross_model_verification.md — the SETUP "
                    f"example names a model outside the canonical lineup "
                    f"(B4-F02 drift class). Update the example or the canonical "
                    f"doc, in the same PR."
                )
    return errors


def main() -> int:
    errors = check(
        SETUP_EN.read_text(encoding="utf-8"),
        SETUP_ZH.read_text(encoding="utf-8"),
        CANONICAL.read_text(encoding="utf-8"),
    )
    if errors:
        print("SETUP cross-model parity lint FAILED:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("SETUP cross-model parity lint PASSED: en/zh-TW examples match and "
          "all values are in the canonical lineup.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
