#!/usr/bin/env python3
"""Static lint for #215 field-norm severity coverage across the three reviewer surfaces.

Issue: #215 (field-norm severity calibration, Kim et al. 2026 arXiv:2605.20668v1 W1/§F.3.4).

Enforces that the three #215 changes are present AND scoped to their own block, so a
bare keyword appearing elsewhere in a file cannot make the lint pass while the actual
load-bearing instruction is missing (falsifiability discipline, per
feedback_lint_passes_but_prompt_silent.md — same pattern as check_v3_9_2_phase_boundary).

Three surfaces:

1. domain_reviewer_agent.md — a `### Step 5: Field-Norm Severity Discipline (#215)` block
   that contains the hard rule (MUST ground the norm in an external source, MUST NOT
   assert from model knowledge), the broadened evidence definition (not just a literature
   citation), and the `[FIELD-NORM UNVERIFIED]` down-rate label.

2. devils_advocate_reviewer_agent.md — a 9th challenge dimension
   `### 9. Field-Norm Severity Calibration (#215)` AND the two required CRITICAL/MAJOR
   fields `field_norm_boundary` + `evidence_crossing_rationale`.

3. calibration_mode_protocol.md — a `### Phase 3.5: Severity-miscalibration measurement (#215)`
   block carrying the low/med/high risk classification and the anti-circularity grounding
   discipline (classify grounding, NOT norm-correctness — do not repeat the W1 failure).

Exit 0 = clean, 1 = any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _read(rel: str) -> str:
    return (REPO_ROOT / rel).read_text(encoding="utf-8")


def _block(text: str, header_re: str) -> str | None:
    """Return the markdown block from a header matching header_re up to the next header of
    the same-or-higher level (## or ###), or end of file. None if the header is absent.

    Scopes keyword checks to the block so a keyword elsewhere in the file does not count.
    """
    m = re.search(header_re, text, re.M)
    if not m:
        return None
    start = m.start()
    # Next line starting with ## or ### (same/higher level) after this header's own line.
    nxt = re.search(r"^\#{2,3} ", text[m.end():], re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    return text[start:end]


def check() -> list[str]:
    errors: list[str] = []

    # --- Surface 1: domain_reviewer_agent.md Step 5 ---
    dr = _read("academic-paper-reviewer/agents/domain_reviewer_agent.md")
    step5 = _block(dr, r"^### Step 5: Field-Norm Severity Discipline \(#215\)")
    if step5 is None:
        errors.append("domain_reviewer_agent.md: missing '### Step 5: Field-Norm Severity Discipline (#215)' block")
    else:
        for needle in ("MUST", "MUST NOT", "[FIELD-NORM UNVERIFIED]"):
            if needle not in step5:
                errors.append(f"domain_reviewer_agent.md Step 5: missing required phrase {needle!r}")
        # codex P1: evidence is NOT limited to a literature citation.
        if "not limited to a literature citation" not in step5:
            errors.append(
                "domain_reviewer_agent.md Step 5: missing the broadened-evidence rule "
                "('not limited to a literature citation')"
            )

    # --- Surface 2: devils_advocate_reviewer_agent.md dimension 9 + CRITICAL fields ---
    da = _read("academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md")
    dim9 = _block(da, r"^### 9\. Field-Norm Severity Calibration \(#215\)")
    if dim9 is None:
        errors.append("devils_advocate_reviewer_agent.md: missing '### 9. Field-Norm Severity Calibration (#215)' dimension")
    # The two required fields must appear in the file (Output Format + the gating rule).
    for field in ("field_norm_boundary", "evidence_crossing_rationale"):
        if field not in da:
            errors.append(f"devils_advocate_reviewer_agent.md: missing required CRITICAL/MAJOR field {field!r}")
    if "[FIELD-NORM UNVERIFIED]" not in da:
        errors.append("devils_advocate_reviewer_agent.md: missing '[FIELD-NORM UNVERIFIED]' down-rate label")

    # --- Surface 3: calibration_mode_protocol.md Phase 3.5 ---
    cal = _read("academic-paper-reviewer/references/calibration_mode_protocol.md")
    phase35 = _block(cal, r"^### Phase 3\.5: Severity-miscalibration measurement \(#215\)")
    if phase35 is None:
        errors.append("calibration_mode_protocol.md: missing '### Phase 3.5: Severity-miscalibration measurement (#215)' block")
    else:
        for needle in ("low", "med", "high"):
            if needle not in phase35:
                errors.append(f"calibration_mode_protocol.md Phase 3.5: missing risk level {needle!r}")
        # codex P1: classify GROUNDING, not norm-correctness — do not repeat the failure.
        if "MUST NOT" not in phase35 or "evals/gold/field_norm_severity" not in phase35:
            errors.append(
                "calibration_mode_protocol.md Phase 3.5: missing the anti-circularity grounding "
                "discipline (MUST NOT guess norm-correctness; anchor to evals/gold/field_norm_severity)"
            )

    return errors


def main() -> int:
    errors = check()
    if errors:
        for e in errors:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print("215_field_norm: all three reviewer surfaces carry their scoped #215 blocks")
    return 0


if __name__ == "__main__":
    sys.exit(main())
