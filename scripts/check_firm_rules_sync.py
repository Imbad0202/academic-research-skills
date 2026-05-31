#!/usr/bin/env python3
"""Firm-rules sync + collision lint (v3.10 PR-A).

Pins two things against regression:

1. **Sync** (R-CIM-* only): the canonical R-CIM-* (claim-manifest) firm-rule
   wording in `shared/references/firm_rules.md` matches the copies mirrored into
   the three writing-stage agent prompts. The mirrors differ only by the agent
   self-reference noun (the `<AGENT>` placeholder in the canonical block); this
   lint normalizes that noun before comparing the operative clause.
   The contamination R-L3-2-* blocks are NOT wording-synced here: their mirrors
   are prose references rather than full-block copies (see firm_rules.md
   "Mirrored in (contamination rules)" note), so only their IDs are guarded
   (see check 2). Wording-sync for the contamination side lands with the PR-B
   reword, which makes those mirrors full-block copies.

2. **Collision guard** (the v3.10 PR-A disambiguation): the `R-L3-2-A/B/C` ID
   (contamination) MUST NOT appear inside any `## Claim Intent Manifest Emission`
   prompt section or inside `claim_intent_manifest.schema.json`; and `R-CIM-A/B/C`
   MUST NOT appear inside a contamination context. Before v3.10 the same
   `R-L3-2-A/B/C` ID named two unrelated rule families; a blind grep-replace of
   either would corrupt the other. This guard fails if the collision reappears.

Usage:
    python scripts/check_firm_rules_sync.py
    python scripts/check_firm_rules_sync.py --root PATH   (for test fixtures)

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

FIRM_RULES_REL = "shared/references/firm_rules.md"

# Prompts that mirror the claim-manifest rules. The canonical `<AGENT>`
# placeholder is matched as a wildcard, not a fixed noun, because each prompt's
# self-reference noun differs AND can differ between R-CIM-A and R-CIM-B within
# the same prompt (e.g. synthesis_agent uses "agent" in R-CIM-A but "synthesis
# agent" in R-CIM-B). So the lint compares the canonical operative clause with
# `<AGENT>` allowed to be any short noun phrase.
CLAIM_MANIFEST_PROMPTS = [
    "deep-research/agents/synthesis_agent.md",
    "deep-research/agents/report_compiler_agent.md",
    "academic-paper/agents/draft_writer_agent.md",
]

CLAIM_MANIFEST_SCHEMA = "shared/contracts/passport/claim_intent_manifest.schema.json"

# The Claim Intent Manifest section heading; the collision guard scans this
# section for forbidden contamination IDs.
CIM_SECTION_HEADER = "## Claim Intent Manifest Emission"

# Contamination contexts the collision guard scans for forbidden R-CIM IDs.
# Update this list when a new agent/reference file starts carrying R-L3-2-* rules
# (a deliberate, infrequent operation — a hardcoded list is intentional here per
# the no-unrequested-abstraction rule; the set is small and stable).
# Asymmetry to be aware of: a new contamination file that mirrors an R-L3-2-* rule
# but is NOT added here is scanned by nothing, so a stray R-CIM-* leaking into it
# passes silently. (The CLAIM_MANIFEST_PROMPTS side fails loudly instead: a listed
# prompt that is missing is reported.) Registering the file here is the guard.
CONTAMINATION_CONTEXT_FILES = [
    "academic-paper/agents/formatter_agent.md",
    "deep-research/references/crossref_api_protocol.md",
    "deep-research/references/openalex_api_protocol.md",
    "academic-pipeline/agents/pipeline_orchestrator_agent.md",
    "deep-research/agents/bibliography_agent.md",
]

# The full contamination namespace (A-E). The historical collision was only on
# A/B/C (the three IDs the claim-manifest prompts borrowed), but a claim-manifest
# surface must not carry ANY contamination ID — guarding D/E too seals the
# namespace against a future leak rather than just patching the known overlap.
CONTAMINATION_IDS = ("R-L3-2-A", "R-L3-2-B", "R-L3-2-C", "R-L3-2-D", "R-L3-2-E")
CIM_IDS = ("R-CIM-A", "R-CIM-B", "R-CIM-C")

CANONICAL_BLOCK_RE = re.compile(
    r"<!--\s*canonical:(?P<id>[A-Za-z0-9-]+)\s*-->\n(?P<body>.*?)\n<!--\s*/canonical:(?P=id)\s*-->",
    re.DOTALL,
)


def _norm(text: str) -> str:
    """Collapse whitespace so byte-for-byte comparison tolerates wrapping."""
    return re.sub(r"\s+", " ", text).strip()


def parse_canonical_blocks(firm_rules_text: str) -> dict[str, str]:
    """Extract {rule_id: operative_clause} from firm_rules.md canonical markers."""
    blocks: dict[str, str] = {}
    for m in CANONICAL_BLOCK_RE.finditer(firm_rules_text):
        blocks[m.group("id")] = _norm(m.group("body"))
    return blocks


# A canonical `<AGENT>` slot matches a SHORT noun phrase: a head word plus at
# most ONE more word, joined by a single space or hyphen. The real self-reference
# nouns are all ≤ 2 words ("agent", "synthesis agent", "compiler", "writer",
# "draft-writer"), so this covers them while rejecting a semantic edit smuggled
# into the slot — e.g. "agent or compiler" (3 words) fails to match, so changing
# "per agent invocation" into "per agent or compiler invocation" is correctly
# flagged as drift rather than silently accepted.
AGENT_WILDCARD = r"[A-Za-z]+(?:[- ][A-Za-z]+)?"


def _canonical_to_regex(canonical_clause: str) -> re.Pattern[str]:
    """Build a regex from an already-normalized canonical clause.

    Literal text is escaped; each `<AGENT>` placeholder becomes a bounded
    noun-phrase wildcard so any prompt's self-reference noun matches. Callers
    pass clauses from `parse_canonical_blocks`, which already `_norm`-ed them.
    """
    parts = canonical_clause.split("<AGENT>")
    pattern = AGENT_WILDCARD.join(re.escape(p) for p in parts)
    return re.compile(pattern)


def check_claim_manifest_sync(
    cim_patterns: dict[str, re.Pattern[str]],
    prompt_texts: dict[str, str],
    violations: list[str],
) -> None:
    """Each prompt mirror must contain the canonical R-CIM operative clause.

    Note: this is a presence check (canonical clause appears, modulo the <AGENT>
    noun). It detects deletion and word-for-word alteration. It does NOT catch an
    *additive override* appended after the canonical clause — appending context is
    legitimate here (report_compiler R-CIM-B appends a standalone-mode sentence).
    """
    for rel in CLAIM_MANIFEST_PROMPTS:
        text = prompt_texts.get(rel)
        if text is None:
            violations.append(f"missing claim-manifest prompt: {rel}")
            continue
        normed = _norm(text)
        for rid in CIM_IDS:
            pat = cim_patterns.get(rid)
            if pat is None:
                violations.append(f"firm_rules.md missing canonical block: {rid}")
                continue
            if not pat.search(normed):
                violations.append(
                    f"{rel}: {rid} mirror drifted from canonical "
                    f"(canonical operative clause not found, modulo the <AGENT> noun)"
                )


def check_collision_guard(root: Path, prompt_texts: dict[str, str], violations: list[str]) -> None:
    """R-L3-2 IDs must not leak into claim-manifest surfaces, and vice versa."""
    # (1) Forbidden contamination IDs inside claim-manifest prompt sections.
    for rel in CLAIM_MANIFEST_PROMPTS:
        text = prompt_texts.get(rel)
        if text is None:
            continue  # missing prompt already flagged by the sync check
        section = _extract_section(text, CIM_SECTION_HEADER)
        if section is None:
            # The Claim Intent Manifest section header was not found — the guard
            # would otherwise scan nothing and pass vacuously. Flag it so a
            # header rename can never silently disable the collision guard.
            violations.append(
                f"{rel}: Claim Intent Manifest section header not found "
                f"({CIM_SECTION_HEADER!r}); collision guard cannot run"
            )
            continue
        for bad in CONTAMINATION_IDS:
            if bad in section:
                violations.append(
                    f"{rel}: contamination ID {bad} reappeared inside the "
                    f"Claim Intent Manifest section (collision regression)"
                )

    # (2) Forbidden contamination IDs inside the claim-manifest schema.
    schema_path = root / CLAIM_MANIFEST_SCHEMA
    if not schema_path.exists():
        violations.append(f"missing collision-guard file: {CLAIM_MANIFEST_SCHEMA}")
    else:
        schema_text = schema_path.read_text(encoding="utf-8")
        for bad in CONTAMINATION_IDS:
            if bad in schema_text:
                violations.append(
                    f"{CLAIM_MANIFEST_SCHEMA}: contamination ID {bad} present "
                    f"(should be R-CIM-* after v3.10 PR-A)"
                )

    # (3) Forbidden R-CIM IDs inside contamination contexts.
    for rel in CONTAMINATION_CONTEXT_FILES:
        path = root / rel
        if not path.exists():
            violations.append(f"missing collision-guard file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for bad in CIM_IDS:
            if bad in text:
                violations.append(
                    f"{rel}: claim-manifest ID {bad} leaked into a contamination "
                    f"context (collision regression)"
                )


_HEADER_LINE_RE = re.compile(r"#{1,2} ")
_FENCE_RE = re.compile(r"\s*(```|~~~)")


def _extract_section(text: str, header: str) -> str | None:
    """Return the body from the `header` line up to the next `#`/`##` heading.

    `header` is a fixed level-2 constant (CIM_SECTION_HEADER). The header LINE
    may carry a trailing suffix after the header text — live prompts use
    `## Claim Intent Manifest Emission (v3.8)` — so a trailing suffix on the
    header line is tolerated, but it must be followed by a space or the line end
    (not more word chars) so `## Claim Intent Manifest Emissionary` does not
    match. The section stops at the next line beginning with `# ` or `## ` (a
    `###` sub-heading inside the section does NOT stop it). A `# `/`## ` line
    INSIDE a fenced code block (``` or ~~~) does NOT stop it either — otherwise a
    forbidden ID hidden after a fake heading in a fenced example would escape the
    collision guard. Returns None when the header line is absent (so callers can
    flag a silently-missing section rather than treating it as vacuously clean).
    """
    lines = text.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        stripped = line.rstrip("\n")
        if stripped == header or (
            stripped.startswith(header) and stripped[len(header):len(header) + 1] == " "
        ):
            start = i + 1
            break
    if start is None:
        return None

    body: list[str] = []
    in_fence = False
    for line in lines[start:]:
        fence = _FENCE_RE.match(line)
        if fence:
            in_fence = not in_fence
            body.append(line)
            continue
        if not in_fence and _HEADER_LINE_RE.match(line):
            break
        body.append(line)
    return "".join(body)


def main() -> int:
    parser = argparse.ArgumentParser(description="firm-rules sync + collision lint")
    parser.add_argument("--root", default=str(REPO_ROOT), help="repo root (for fixtures)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    firm_rules_path = root / FIRM_RULES_REL
    if not firm_rules_path.exists():
        print(f"ERROR: firm_rules.md not found: {firm_rules_path}", file=sys.stderr)
        return 2

    canon = parse_canonical_blocks(firm_rules_path.read_text(encoding="utf-8"))
    if not canon:
        print("ERROR: no canonical blocks parsed from firm_rules.md", file=sys.stderr)
        return 2

    # Compile each R-CIM pattern once; read each claim-manifest prompt once and
    # share the text between the sync check and the collision guard.
    cim_patterns = {rid: _canonical_to_regex(canon[rid]) for rid in CIM_IDS if rid in canon}
    prompt_texts: dict[str, str] = {}
    for rel in CLAIM_MANIFEST_PROMPTS:
        path = root / rel
        if path.exists():
            prompt_texts[rel] = path.read_text(encoding="utf-8")

    violations: list[str] = []
    check_claim_manifest_sync(cim_patterns, prompt_texts, violations)
    check_collision_guard(root, prompt_texts, violations)

    if violations:
        print("firm-rules sync/collision lint FAILED:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        return 1

    print("firm-rules sync/collision lint PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
