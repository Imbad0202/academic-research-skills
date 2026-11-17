#!/usr/bin/env python3
"""Keep the #1098 premise-row sentence identical in every place it appears (#1099).

The #1098 rule is one sentence that ends with "(#1098)." It must appear word for
word in five places:

  * DA Phase 2 item 3 in the DA agent file (the dispatched inline mirror),
  * Challenge Dimension 7 in the DA agent file,
  * Frame-Lock Detection in the DA agent file,
  * the da-phase2 fragment of the canonical prompt source,
  * the DA report structure in the reviewer SKILL.md.

The canonical sentence is read from the da-phase2 fragment, which
check_reviewer_sprint_prompt_sync.py already pins. It must sit on one line and
start after the previous sentence, so a line break cannot hide an edit to its
first half. Every "(#1098)." in the checked files must close an exact copy of
that sentence, and each file must hold the expected number of copies. In the DA
agent file, each of the three named sections must hold exactly one copy, so a
copy moved from one section to another fails. DA_SECTIONS gives each section as
two fixed heading lines, its own and the one that follows it; each line must
appear exactly once. An edit to one copy, a lost copy, a moved copy, or an extra
copy fails.

Exit 0 = clean, 1 = any failure.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = "academic-paper-reviewer/references/reviewer_sprint_prompt_source.md"
DA_AGENT = "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md"
SKILL = "academic-paper-reviewer/SKILL.md"
END_TOKEN = "(#1098)."

# Each DA copy belongs to one section, given by its own heading line and the
# heading line that follows it. Both lines are fixed text, so the lint does not
# parse Markdown; a renamed or duplicated heading fails with a clear message.
DA_SECTIONS = (
    ("### Phase 2 — Paper-visible review", "## Role Boundaries — DA vs Other Reviewers"),
    ("### 7. Stakeholder Blind Spots", '### 8. "So What?" Test'),
    ("### Frame-Lock Detection", "### Origin"),
)

EXPECTED_COPIES = {
    DA_AGENT: len(DA_SECTIONS),
    SOURCE: 1,
    SKILL: 1,
}

DA_PHASE2_RE = re.compile(
    r"^<!-- reviewer-sprint-canonical:da-phase2:BEGIN -->\n(?P<body>.*?)"
    r"^<!-- reviewer-sprint-canonical:da-phase2:END -->$",
    re.MULTILINE | re.DOTALL,
)


def canonical_sentence(root: Path, errors: list[str]) -> str | None:
    """Return the sentence that ends with "(#1098)." in the da-phase2 fragment."""
    text = (root / SOURCE).read_text(encoding="utf-8")
    match = DA_PHASE2_RE.search(text)
    if match is None:
        errors.append(f"{SOURCE}: da-phase2 fragment markers not found")
        return None
    body = match.group("body")
    if body.count(END_TOKEN) != 1:
        errors.append(
            f"{SOURCE}: da-phase2 fragment must hold exactly one {END_TOKEN!r}, "
            f"found {body.count(END_TOKEN)}"
        )
        return None
    end = body.index(END_TOKEN) + len(END_TOKEN)
    previous_sentence_end = body.rfind(". ", 0, end - len(END_TOKEN))
    start = previous_sentence_end + 2 if previous_sentence_end != -1 else 0
    sentence = body[start:end]
    if "\n" in sentence:
        errors.append(
            f"{SOURCE}: the #1098 sentence in da-phase2 must sit on one line, "
            "after the previous sentence on that line"
        )
        return None
    if "CRITICAL or MAJOR" not in sentence or len(sentence) < 100:
        errors.append(f"{SOURCE}: the #1098 sentence in da-phase2 looks truncated: {sentence!r}")
        return None
    return sentence


def section(text: str, start: str, end: str, errors: list[str]) -> str | None:
    """Return the text from the start heading line to the end heading line."""
    offsets = {}
    for heading in (start, end):
        found = [m.start() for m in re.finditer(rf"^{re.escape(heading)}$", text, re.MULTILINE)]
        if len(found) != 1:
            errors.append(f"{DA_AGENT}: heading {heading!r} must appear exactly once, found {len(found)}")
            return None
        offsets[heading] = found[0]
    if offsets[end] < offsets[start]:
        errors.append(f"{DA_AGENT}: heading {end!r} must follow {start!r}")
        return None
    return text[offsets[start]:offsets[end]]


def check(root: Path = REPO_ROOT) -> list[str]:
    errors: list[str] = []
    sentence = canonical_sentence(root, errors)
    if sentence is None:
        return errors
    for rel, want in EXPECTED_COPIES.items():
        text = (root / rel).read_text(encoding="utf-8")
        exact = text.count(sentence)
        endings = text.count(END_TOKEN)
        if exact != want:
            errors.append(f"{rel}: expected {want} exact copies of the #1098 sentence, found {exact}")
        if endings != exact:
            errors.append(
                f"{rel}: {endings - exact} {END_TOKEN!r} ending(s) close a sentence that "
                "differs from the canonical da-phase2 copy"
            )
    da_text = (root / DA_AGENT).read_text(encoding="utf-8")
    for start, end in DA_SECTIONS:
        body = section(da_text, start, end, errors)
        if body is not None and body.count(sentence) != 1:
            errors.append(
                f"{DA_AGENT}: section {start!r} must hold exactly one copy of the "
                f"#1098 sentence, found {body.count(sentence)}"
            )
    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    print("OK: the #1098 premise-row sentence is identical in all expected places")
    return 0


if __name__ == "__main__":
    sys.exit(main())
