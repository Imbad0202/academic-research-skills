#!/usr/bin/env python3
"""ARS v3.7.1 Step 2 — D2 audit Scope Report block lint.

Spec: docs/design/2026-04-30-ars-v3.6.8-trust-provenance-and-drift-transparency-spec.md
      §3.2 (D2 — Audit scope coverage non-disclosure)
      §4 Step 2 — Audit report Scope Report block (lines 412-425)

Enforces, on the codex audit prompt template:

  R1. A Section 0 Scope Report header appears strictly BEFORE the first
      Section 1 heading (spec line 146: "must appear before any pass/fail
      summary"). The header is the literal "## Codex Audit Round N — Scope
      Report" (spec line 134).
  R2. The Scope Report block carries the four mandatory content fields
      (spec lines 136-140):
        - Total entries audited
        - Entries with retrieved original source
        - Entries description-only (no retrieved source)
        - Audit scope warning
  R3. The aggregate-status section carries the three required splits
      (spec lines 147-150):
        - verified-against-source: PASS | FAIL
        - description-internally-consistent: PASS | FAIL
        - unaudited-due-to-missing-source: <count>
  R4. The combined-aggregate "PASSED" verb is forbidden in audit summary
      contexts (spec line 152). We forbid the literal pattern
      "Audit summary ... PASSED" (case-insensitive on the surrounding
      tokens) anywhere in the template.
  R5. Additive-prepend invariant per Q5 amend (spec §3.2 line 131,
      §3.7 line 346): the Section 1 heading must appear with exact bytes
      "## Section 1 — Round metadata" so prepending Section 0 has not
      altered the existing v3.6.7 audit template's byte-equivalent
      Sections 1-7 zone.

Attack-surface design notes (informed by issue #77 lessons):
  - Heading-anchored matching uses begin-of-line regex `^## ` to skip
    headings that appear inside fenced code blocks. The Scope Report
    block in the canonical template DOES contain a fenced sub-block with
    its own "## Codex Audit Round N — Scope Report" heading; our header
    detector must recognize that as the canonical Scope Report marker
    even though it lives inside a fence. We resolve this by allowing the
    Scope Report header to be inside the first fenced block of Section 0
    OR at top-level — but require that AT LEAST ONE such header anchor
    exists strictly before the Section 1 boundary, and that exactly one
    Section-0 anchor exists at top level (the H2 outside any fence).
  - Multiple Section-0 H2 anchors at top level → reject (mirror of #77
    P1-1 duplicate-marker bypass).

Exit codes: 0 on PASS, 1 on FAIL.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TARGET = REPO_ROOT / "shared" / "templates" / "codex_audit_multifile_template.md"

# The canonical Section-0 H2 anchor at the top level of the template.
SECTION_0_H2 = "## Section 0"
# The Scope Report header literal, placed inside the fenced markdown block
# of Section 0 per spec line 134.
SCOPE_REPORT_HEADER = "## Codex Audit Round N — Scope Report"
# The byte-equivalent Section 1 heading per Q5 invariant.
SECTION_1_HEADING_EXACT = "## Section 1 — Round metadata"

# Required Scope Report content fields (spec lines 136-140).
REQUIRED_FIELDS: list[str] = [
    "**Total entries audited:**",
    "**Entries with retrieved original source:**",
    "**Entries description-only (no retrieved source):**",
    "**Audit scope warning:**",
]

# Required aggregate-status splits (spec lines 147-150).
REQUIRED_SPLITS: list[str] = [
    "verified-against-source",
    "description-internally-consistent",
    "unaudited-due-to-missing-source",
]

# Forbidden combined-aggregate "PASSED" verb in audit summary contexts.
# Spec line 152: "The combined-aggregate 'PASSED' verb is forbidden in
# audit summary." Codex round-4 forced fence-content scan; round-5 P2-5
# broadened the verdict-key set (verdict / status / result / final /
# overall) so the lint catches `Overall status: PASSED` etc., not only
# `verdict: PASSED`. PASSED is matched case-insensitive on the surrounding
# tokens but the verb itself stays caps-only — that IS the forbidden
# verb form. The 80-char window after `audit summary` keeps the spec
# self-explanation prose (`...forbidden in the audit summary.`) clear
# of any PASSED token within reach.
# A verdict-shaped key word: any of the canonical verdict tokens, optionally
# preceded by one or two short qualifier words (e.g. "Final verdict",
# "Audit status", "Overall final result"). Codex round-6 P2-9 broadened
# this so multi-word keys like `Final verdict: PASSED` are also caught.
# Each qualifier is restricted to alphabetic characters of length 1-15
# so the regex does not gobble unrelated text on the same line.
_VERDICT_TOKEN = r"(?:verdict|status|result|final|outcome|overall)"
_VERDICT_KEY = rf"(?:[A-Za-z]{{1,15}}\s+){{0,2}}{_VERDICT_TOKEN}"
FORBIDDEN_AGGREGATE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"audit\s+summary[^\n]{0,80}\bPASSED\b", re.IGNORECASE),
    re.compile(rf"^\s*{_VERDICT_KEY}\s*:\s*PASSED\b", re.IGNORECASE | re.MULTILINE),
]

# Bare-verdict line patterns used to detect a pass/fail summary preceding
# Section 0 (spec line 146 firm rule). Wider than R4 because here we want
# to catch BOTH PASS and FAIL — anything resembling a verdict line counts
# as a pass/fail summary, regardless of the verb.
BARE_VERDICT_BEFORE_SECTION_0_PATTERNS: list[re.Pattern[str]] = [
    # Heading-style pass/fail summary
    re.compile(r"^##\s+[A-Za-z][^\n]{0,80}\b(Summary|Verdict)\b", re.MULTILINE),
    # Existing first-aggregate-split line (kept from earlier rounds)
    re.compile(r"^\s*verified-against-source\s*:\s*(PASS|FAIL)\b", re.MULTILINE),
    # Bare `<key>: PASS|FAIL` line, no heading framing
    re.compile(rf"^\s*{_VERDICT_KEY}\s*:\s*(PASS|FAIL|PASSED|FAILED)\b", re.IGNORECASE | re.MULTILINE),
]


def _strip_fenced_blocks(text: str) -> str:
    """Replace fenced code blocks with same-length whitespace so headings
    inside fences don't count as top-level H2 anchors.

    Length preservation keeps any line/column reporting consistent with
    the original file. We support the standard ``` and ~~~ fences.
    """

    def _replace(match: re.Match[str]) -> str:
        content = match.group(0)
        # Replace non-newline characters with spaces so newlines and
        # column positions are preserved, but content is neutralized.
        return "".join(" " if ch != "\n" else "\n" for ch in content)

    pattern = re.compile(
        r"^([ \t]*)(```|~~~)[^\n]*\n.*?^\1\2[ \t]*$",
        re.DOTALL | re.MULTILINE,
    )
    return pattern.sub(_replace, text)


def _find_section_1_position(text_no_fences: str) -> int:
    """Return the byte offset of the exact top-level Section 1 heading, or -1 if absent.

    Codex round-3 P2-3: a decoy heading inside a fenced code block (e.g. in
    a worked example) was previously accepted as the anchor. The check now
    runs against the fence-stripped text and requires line-start anchoring
    so a fenced occurrence of the exact heading bytes cannot satisfy R5.
    """
    pos = text_no_fences.find(SECTION_1_HEADING_EXACT)
    if pos == -1:
        return -1
    # Must start at line beginning.
    if pos > 0 and text_no_fences[pos - 1] != "\n":
        return -1
    return pos


def _format_target_for_report(target: Path) -> str:
    """Format target path for lint report.

    Codex round-2 P2-2: when --target is a relative repo path or points
    outside REPO_ROOT, `target.relative_to(REPO_ROOT)` raises ValueError.
    Resolve to absolute first, then attempt relativization, falling back
    to the raw path if the resolved path is not under REPO_ROOT.
    """
    try:
        resolved = target.resolve()
    except (OSError, RuntimeError):
        return str(target)
    try:
        return str(resolved.relative_to(REPO_ROOT))
    except ValueError:
        return str(resolved)


def _section_0_block(text_full: str, text_no_fences: str) -> str:
    """Slice the Section 0 block from the H2 anchor up to (but not including)
    the next H2 boundary at top level. Returns "" if the anchor is missing.

    Codex round-2 P2-1: required-field and aggregate-status-split checks
    must scope to Section 0 only, not whole-file. Otherwise a marker that
    appears in a later appendix or documentation block can falsely satisfy
    the check while Section 0 itself is incomplete.

    Boundary detection runs on the fence-stripped string so a fenced sub-
    block inside Section 0 (e.g. the canonical Scope Report header) does
    not terminate the slice. The returned slice is taken from the original
    text so contents are byte-equivalent to the source.
    """
    import re as _re
    section_0_match = _re.search(
        r"^## Section 0\b", text_no_fences, _re.MULTILINE
    )
    if section_0_match is None:
        return ""
    start = section_0_match.start()
    next_h2 = _re.search(r"^## ", text_no_fences[start + 1 :], _re.MULTILINE)
    end = (start + 1 + next_h2.start()) if next_h2 else len(text_full)
    return text_full[start:end]


def check(target: Path) -> tuple[int, list[str]]:
    """Run all rules. Return (exit_code, report_lines)."""
    if not target.exists():
        return 1, [f"FAIL: target file does not exist: {target}"]

    text = text_full = target.read_text(encoding="utf-8")
    text_no_fences = _strip_fenced_blocks(text)
    section_0_only = _section_0_block(text_full, text_no_fences)

    report: list[str] = [f"[v3.7.1 audit-scope-block] target: {_format_target_for_report(target)}"]
    failed: bool = False

    # ---- R5: Section 1 byte-equivalence sentinel ----
    # Codex round-3 P2-3: search the fence-stripped string so a decoy heading
    # inside a fenced code block (e.g. worked example) cannot satisfy R5.
    section_1_pos = _find_section_1_position(text_no_fences)
    if section_1_pos == -1:
        failed = True
        report.append(
            "  FAIL [R5]: Section 1 heading exact bytes "
            f"{SECTION_1_HEADING_EXACT!r} missing or shifted; "
            "Q5 additive-prepend invariant broken (spec §3.2 line 131)."
        )

    # ---- R1: Section 0 H2 anchor present, before Section 1 ----
    section_0_anchors = [
        m.start()
        for m in re.finditer(r"^## Section 0\b", text_no_fences, re.MULTILINE)
    ]
    if not section_0_anchors:
        failed = True
        report.append(
            "  FAIL [R1]: Section 0 Scope Report header missing "
            f"(expected H2 anchor starting with {SECTION_0_H2!r} at top level)."
        )
    elif len(section_0_anchors) > 1:
        failed = True
        report.append(
            f"  FAIL [R1]: multiple Section 0 H2 anchors found at top level "
            f"(positions={section_0_anchors}); duplicate-marker hardening rejects "
            f"more than one (compare issue #77 P1-1)."
        )
    elif section_1_pos != -1 and section_0_anchors[0] >= section_1_pos:
        failed = True
        report.append(
            f"  FAIL [R1]: Section 0 anchor (offset {section_0_anchors[0]}) "
            f"appears at or after Section 1 heading (offset {section_1_pos}); "
            f"spec line 146 firm rule: Scope Report must appear BEFORE any "
            f"pass/fail summary."
        )

    # ---- R1 continued: Scope Report header literal must appear inside Section 0 ----
    # Codex round-3 P2-4: scope to section_0_only so a preamble decoy
    # (e.g. an "Appendix" or "historical reference" carrying the exact
    # header) cannot falsely satisfy R1 when the real Section 0 block
    # is missing the canonical header.
    # Codex round-6 P2-8: anchor to a real heading line. A prose mention
    # of the header literal (`The required header is "## Codex Audit Round
    # N — Scope Report"`) inside Section 0 must NOT satisfy the contract
    # because the rendered audit prompt needs the actual heading line.
    scope_header_line_re = re.compile(
        r"^##\s+Codex Audit Round N\s+—\s+Scope Report\b",
        re.MULTILINE,
    )
    if scope_header_line_re.search(section_0_only) is None:
        failed = True
        report.append(
            f"  FAIL [R1]: Scope Report header line {SCOPE_REPORT_HEADER!r} "
            "missing from Section 0 (spec line 134; must appear as a real "
            "heading line, not a prose mention)."
        )

    # ---- R6 firm-rule check: no pass/fail summary ahead of Section 0 ----
    # Codex round-5 P2-6 broadened this to detect bare-verdict lines (e.g.
    # `verdict: PASS`, `result: FAIL`) regardless of `## ... Summary`
    # heading framing. Any pre-Section-0 verdict signal violates spec
    # line 146 firm rule. Scan runs on text_no_fences so a verdict-shaped
    # line that lives inside a fenced reference / quoted documentation
    # block does NOT trip the rule.
    if section_0_anchors:
        section_0_pos = section_0_anchors[0]
        prefix = text_no_fences[:section_0_pos]
        for pattern in BARE_VERDICT_BEFORE_SECTION_0_PATTERNS:
            match = pattern.search(prefix)
            if match is not None:
                failed = True
                anchor = match.group(0).strip()
                report.append(
                    f"  FAIL [R1]: pass/fail summary detected ahead of Section 0 "
                    f"(anchor: {anchor!r}); spec line 146 requires Scope Report "
                    f"to appear BEFORE any pass/fail summary."
                )
                break  # one fail diagnostic per check is enough

    # ---- R2: required content fields ----
    # Codex round-2 P2-1: scope to Section 0 only. A marker in an appendix
    # or documentation block must NOT satisfy the contract — the audit
    # prompt that gets sent to codex contains Section 0, not the appendix.
    for field in REQUIRED_FIELDS:
        if field not in section_0_only:
            failed = True
            report.append(
                f"  FAIL [R2]: required Scope Report field missing from Section 0: "
                f"{field!r} (spec lines 136-140)."
            )

    # ---- R3: aggregate-status three-way split ----
    # Codex round-2 P2-1: same scoping fix as R2.
    for split in REQUIRED_SPLITS:
        if split not in section_0_only:
            failed = True
            report.append(
                f"  FAIL [R3]: required aggregate-status split missing from Section 0: "
                f"{split!r} (spec lines 147-150)."
            )

    # ---- R4: forbidden combined-aggregate 'PASSED' verb ----
    # Codex round-4 P2: fenced code blocks ARE the prompt content sent to
    # codex (the canonical Scope Report header lives inside a fence). A
    # forbidden 'verdict: PASSED' line in a fenced sub-block defeats the
    # spec line 152 contract just as much as one outside a fence. Run the
    # patterns against text_full so fence content is included.
    for pattern in FORBIDDEN_AGGREGATE_PATTERNS:
        match = pattern.search(text_full)
        if match is not None:
            failed = True
            report.append(
                f"  FAIL [R4]: forbidden combined-aggregate 'PASSED' verb in "
                f"audit summary context: {match.group(0)!r} "
                "(spec line 152: combined-aggregate 'PASSED' is forbidden)."
            )

    if failed:
        report.append("[v3.7.1 audit-scope-block] FAILED")
        return 1, report
    report.append("[v3.7.1 audit-scope-block] PASS")
    return 0, report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="ARS v3.7.1 Step 2 — D2 audit Scope Report block lint."
    )
    parser.add_argument(
        "--target",
        type=Path,
        default=DEFAULT_TARGET,
        help="Audit prompt template path (default: shared/templates/codex_audit_multifile_template.md).",
    )
    args = parser.parse_args()

    exit_code, report = check(args.target)
    print("\n".join(report))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
