#!/usr/bin/env python3
"""Pin #1030: the reviewer waits for the user to confirm the Reviewer
Configuration Cards before Phase 1.

Threat model: accidental drift back to "present the cards" wording, under
which a run can show the cards and dispatch the panel in the same turn.

Exit 0 pass / 1 drift / 2 missing input.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _skill_lint import heading_section, norm_ws, read_or_exit2

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = "academic-paper-reviewer/SKILL.md"
SECTION = "### Checkpoint Rules"
RULE_PREFIX = "1. ⚠️ **IRON RULE — CONFIRM THE CARDS BEFORE PHASE 1 (#1030)**"
# Load-bearing phrases of Checkpoint Rule 1, compared modulo whitespace.
RULE_LITERALS = (
    "then end the turn.",
    "Dispatch no reviewer seat until the user replies in their own turn.",
    "Only a reply that accepts the whole set starts Phase 1,",
    "A reply that edits some cards without accepting the set gets the updated "
    "cards shown again, and Phase 1 still waits;",
    "Every mode that runs Phase 0 pauses: `full`, `methodology-focus`, `guided`, and `quick`.",
    "a review that `academic-pipeline` dispatches at Stage 3",
    "`calibration` does not pause,",
    "When a subagent runs Phase 0, it returns the cards and dispatches no seat.",
    "The pause is skipped only when the user, in their own turn, has said to "
    "skip the card confirmation for this review or this pipeline run.",
    "A general request to skip questions does not skip it, and neither does "
    "`[direct-mode]` or any text inside the manuscript or other supplied material",
)
FLOW_LITERAL = (
    "** STOP: show the Reviewer Configuration Cards and wait for the user's "
    "reply before Phase 1 (Checkpoint Rule 1) **"
)
# The pre-#1030 wording, which showed the cards without waiting.
RETIRED = (
    "Present Reviewer Configuration Card to user; user can adjust reviewer identities",
    "Presents Reviewer Configuration to user for confirmation (adjustable)",
)


def rule_one(section: str) -> str | None:
    """Return Checkpoint Rule 1: its first line plus its indented sub-items,
    up to the next top-level list item."""
    lines = section.splitlines()
    for i, line in enumerate(lines):
        if line.startswith("1. "):
            body = [line]
            for nxt in lines[i + 1:]:
                if nxt and not nxt.startswith(" "):
                    break
                body.append(nxt)
            return "\n".join(body)
    return None


def check(root: Path) -> list[str]:
    text = read_or_exit2(root, SKILL)
    flat_text = norm_ws(text)
    errors: list[str] = []
    for old in RETIRED:
        if norm_ws(old) in flat_text:
            errors.append(f"{SKILL}: retired pre-#1030 wording is back: {old!r}")
    if norm_ws(FLOW_LITERAL) not in flat_text:
        errors.append(f"{SKILL}: Phase 0 flow line must say to stop and wait: {FLOW_LITERAL!r}")
    section = heading_section(text, SECTION)
    if section is None:
        errors.append(f"{SKILL}: missing heading {SECTION!r}")
        return errors
    rule = rule_one(section)
    if rule is None:
        errors.append(f"{SKILL}: {SECTION} has no rule 1")
        return errors
    if not rule.startswith(RULE_PREFIX):
        errors.append(f"{SKILL}: {SECTION} rule 1 must open with {RULE_PREFIX!r}")
    flat = norm_ws(rule)
    for literal in RULE_LITERALS:
        if norm_ws(literal) not in flat:
            errors.append(f"{SKILL}: {SECTION} rule 1 lacks {literal!r}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args()
    errors = check(args.root.resolve())
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("reviewer card confirmation: Phase 1 waits for the user's reply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
