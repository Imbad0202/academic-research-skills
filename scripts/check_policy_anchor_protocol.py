#!/usr/bin/env python3
"""#108 policy_anchor_disclosure_protocol.md static lint.

Decision Doc reference:
  docs/design/2026-05-14-ai-disclosure-schema-decision.md §4.1 (item 6) +
  §4.3 invariants + §4.4 11 open concerns + §3 G10 7-row precedence table.

Implementation spec reference:
  docs/design/2026-05-14-ai-disclosure-impl-spec.md §3 (resolved-paths table).

This lint enforces presence-of-required-content invariants on the protocol
doc the LLM reads at runtime when in `disclosure` mode with
`--policy-anchor=<a>` selector.

Checks
------
1. All 8 §4.3 invariants are named verbatim (G1 / G2 / G3 / G10 / G4 / G5 /
   G7 / G8 / G9 — G3 and G10 combined into a single composite invariant).
2. All 11 §4.4 concerns have a resolution clause referenced by number
   (`concern #1` through `concern #11`).
3. The §3 G10 7-row precedence table is present with all 7 rows
   (numbered 1..7).
4. The auto-promotion forbiddance clause is present (G3/G10 invariant
   load-bearing constraint).
5. The 4 canonical anchor slugs are enumerated in the lookup mechanism
   section.
6. The Nature ↔ v3.2 venue dedup pointer
   (`shared/policy_data/nature_policy.md`) is referenced.

Exit codes
----------
  0 - all checks pass
  1 - one or more violations
  2 - invocation error

Usage
-----
  python scripts/check_policy_anchor_protocol.py academic-paper/references/policy_anchor_disclosure_protocol.md
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_INVARIANTS = (
    "G1 invariant",
    "G2 invariant",
    "G3 / G10 invariant",
    "G4 invariant",
    "G5 invariant",
    "G7 invariant",
    "G8 invariant",
    "G9 invariant",
)
REQUIRED_CONCERNS = tuple(f"concern #{i}" for i in range(1, 12))
REQUIRED_ANCHOR_SLUGS = ("prisma-trAIce", "icmje", "nature", "ieee")
DEDUP_POINTER = "shared/policy_data/nature_policy.md"
AUTO_PROMOTION_KEYWORDS = ("auto-promotion", "MUST NOT be rendered as though USED")


def lint_text(text: str) -> list[str]:
    violations: list[str] = []

    # Check 1: required invariants
    for inv in REQUIRED_INVARIANTS:
        if inv not in text:
            violations.append(f"missing required invariant reference: {inv}")

    # Check 2: required concern resolutions
    for concern in REQUIRED_CONCERNS:
        if concern not in text:
            violations.append(f"missing §4.4 {concern} resolution clause")

    # Check 3: G10 7-row precedence table — match actual markdown table rows
    # (start-of-line `| N |` after stripping leading whitespace). The earlier
    # version accepted any `row N` mention anywhere in the doc, which let prose
    # references satisfy the check even when the markdown row itself was
    # deleted (codex round-1 P2 #1 closure).
    for row in range(1, 8):
        table_row_pattern = re.compile(
            rf"^\s*\|\s*{row}\s*\|", re.MULTILINE
        )
        if not table_row_pattern.search(text):
            violations.append(
                f"missing G10 7-row precedence row {row} (no `| {row} |` markdown row found)"
            )

    # Check 4: auto-promotion forbiddance
    if not any(kw in text for kw in AUTO_PROMOTION_KEYWORDS):
        violations.append(
            "missing auto-promotion forbiddance clause (G3/G10 UNCERTAIN-not-USED invariant)"
        )

    # Check 5: anchor slug coverage
    for slug in REQUIRED_ANCHOR_SLUGS:
        if slug not in text:
            violations.append(f"missing canonical anchor slug reference: {slug}")

    # Check 6: dedup pointer
    if DEDUP_POINTER not in text:
        violations.append(
            f"missing Nature ↔ v3.2 venue dedup pointer: {DEDUP_POINTER}"
        )

    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "path",
        nargs="?",
        default="academic-paper/references/policy_anchor_disclosure_protocol.md",
        help="path to policy_anchor_disclosure_protocol.md (default: %(default)s)",
    )
    args = parser.parse_args(argv)
    target = Path(args.path)
    if not target.exists():
        print(f"error: file not found: {target}", file=sys.stderr)
        return 2
    text = target.read_text(encoding="utf-8")
    violations = lint_text(text)
    if violations:
        for v in violations:
            print(f"{target}: {v}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
