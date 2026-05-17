#!/usr/bin/env python3
"""v3.9.0 spec lint: verify formatter pass-through allowlist + refusal-list-unchanged + suffix shape consistency.

Per spec v3.9.0 §3.8 rules 5-6 (R3 P2 closure: exact-token extraction,
not substring matching).

Usage:
    python scripts/check_v3_9_0_triangulation.py
    python scripts/check_v3_9_0_triangulation.py --formatter-path PATH
        (for test fixtures only)

Exit codes:
    0 — all checks pass
    1 — one or more checks failed
    2 — invocation error (e.g., file missing)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FORMATTER = REPO_ROOT / "academic-paper/agents/formatter_agent.md"


# Canonical 9-suffix allowlist per spec v3.9.0 §3.8 rule 5.
EXPECTED_ALLOWLIST_TOKENS = {
    # v3.7.3 legacy (3)
    "CONTAMINATED-PREPRINT",
    "CONTAMINATED-UNMATCHED",
    "CONTAMINATED-PREPRINT+UNMATCHED",
    # v3.9.0 new (6)
    "CONTAMINATED-COVERAGE-NOISE",
    "CONTAMINATED-PARTIAL-UNMATCH",
    "CONTAMINATED-TRIANGULATION-UNMATCHED",
    "CONTAMINATED-PREPRINT+COVERAGE-NOISE",
    "CONTAMINATED-PREPRINT+PARTIAL-UNMATCH",
    "CONTAMINATED-PREPRINT+TRIANGULATION-UNMATCHED",
}


def extract_allowlist_tokens(formatter_text: str) -> set[str]:
    """Parse the pass-through allowlist sentence (anchored at 'DO NOT trigger refusal').

    Strategy: locate the sentence containing 'DO NOT trigger refusal' (the canonical
    anchor phrase from v3.7.3 + v3.9.0 specs). Walk backward to find the opening '(' of
    the enclosing parenthetical, then forward to ')'. Extract backtick-quoted
    CONTAMINATED-* tokens from that parenthetical only.

    This avoids substring collisions because tokens are parsed from backtick-delimited
    code spans, not from arbitrary text. CONTAMINATED-PREPRINT and
    CONTAMINATED-PREPRINT+UNMATCHED are extracted as distinct tokens.
    """
    anchor = "DO NOT trigger refusal"
    idx = formatter_text.find(anchor)
    if idx < 0:
        return set()
    paren_start = formatter_text.rfind("(", 0, idx)
    paren_end = formatter_text.find(")", paren_start) if paren_start >= 0 else -1
    if paren_start < 0 or paren_end < 0:
        return set()
    parenthetical = formatter_text[paren_start:paren_end]
    pattern = re.compile(r"`(CONTAMINATED-[A-Z+\-]+)`")
    return set(pattern.findall(parenthetical))


def extract_refusal_rule_tokens(formatter_text: str) -> set[str]:
    """Parse the formatter refusal rules block (numbered list before the allowlist).

    Find numbered list lines (^N. ...) that appear BEFORE the allowlist anchor.
    Extract any backtick-quoted CONTAMINATED-* token in those rule bodies — there
    must be none, per R-L3-2-E.
    """
    anchor_idx = formatter_text.find("DO NOT trigger refusal")
    if anchor_idx < 0:
        return set()
    pre = formatter_text[:anchor_idx]
    rule_pattern = re.compile(r"^\d+\.\s.*$", re.MULTILINE)
    rule_lines = rule_pattern.findall(pre)
    if not rule_lines:
        return set()
    # Scan the last 15 numbered list lines (safely covers rules 1-10).
    contam_pattern = re.compile(r"`(CONTAMINATED-[A-Z+\-]+)`")
    found = set()
    for line in rule_lines[-15:]:
        found |= set(contam_pattern.findall(line))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="v3.9.0 triangulation spec lint")
    parser.add_argument(
        "--formatter-path",
        default=str(DEFAULT_FORMATTER),
        help="Path to formatter_agent.md (for test fixtures)",
    )
    args = parser.parse_args()

    formatter_path = Path(args.formatter_path)
    if not formatter_path.exists():
        print(f"ERROR: formatter not found: {formatter_path}", file=sys.stderr)
        return 2
    formatter_text = formatter_path.read_text(encoding="utf-8")

    failures = []

    allowlist = extract_allowlist_tokens(formatter_text)
    missing = EXPECTED_ALLOWLIST_TOKENS - allowlist
    extra = allowlist - EXPECTED_ALLOWLIST_TOKENS
    if missing:
        failures.append(f"allowlist missing tokens: {sorted(missing)}")
    if extra:
        failures.append(f"allowlist has extra tokens: {sorted(extra)}")

    in_refusal = extract_refusal_rule_tokens(formatter_text)
    if in_refusal:
        failures.append(
            f"CONTAMINATED-* found in refusal rules (R-L3-2-E violation): {sorted(in_refusal)}"
        )

    if failures:
        print("v3.9.0 triangulation lint FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("v3.9.0 triangulation lint OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
