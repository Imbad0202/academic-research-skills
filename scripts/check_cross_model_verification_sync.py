"""Doc-sync lint for the cross-model grounding guards (#346 / #349).

The contract-bearing jq for the cross-model verifier lives in canonical files under
`scripts/cross_model_verification/`; `shared/cross_model_verification.md` consumes them via
`jq -f`. The behavioral tests (`test_cross_model_verification_guards.py`) pin what the jq DOES;
this lint pins that the documented bash actually WIRES to the canonical files and still carries
the fail-closed control flow — so a doc edit cannot quietly re-inline a (possibly weaker) filter
or drop a safety branch while the behavioral tests keep passing against the untouched .jq.

It deliberately does NOT byte-pin the whole bash block (it is a copy-paste example users adapt).
It checks:
  1. REQUIRED_FILTERS exactly matches the .jq files on disk (so a newly added filter can't escape
     the lint by simply not being listed — REQUIRED_FILTERS is the single source of truth);
  2. every canonical .jq file is referenced by the doc via `jq -f`;
  3. the NOT_SEARCHED and CROSS-MODEL-ERROR safety branches are present;
  4. no provider block re-inlines a `jq -e`/`jq -r` expression instead of loading a `-f` file
     (which would bypass the behavior-tested filters).

Exit codes: 0 = pass; 1 = a required reference or safety branch is missing.
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DOC = REPO / "shared" / "cross_model_verification.md"
GUARD_DIR = REPO / "scripts" / "cross_model_verification"

# Canonical filters that MUST exist on disk and be referenced by the doc via `jq -f`.
REQUIRED_FILTERS = [
    "openai_has_completed_web_search.jq",
    "openai_text.jq",
    "openai_sources.jq",
    "gemini_is_grounded.jq",
    "gemini_sources.jq",
]

# Safety branches the documented patterns must retain (the whole point of the guard).
REQUIRED_BRANCHES = [
    "NOT_SEARCHED",       # ungrounded / from-memory downgrade
    "CROSS-MODEL-ERROR",  # non-2xx transport-failure split (distinct from NOT_SEARCHED)
]


def main() -> int:
    failures: list[str] = []

    if not DOC.is_file():
        print(f"[cross-model-sync] FAIL: doc not found: {DOC}")
        return 1
    text = DOC.read_text(encoding="utf-8")

    # 1. REQUIRED_FILTERS is the single source of truth: it must match the .jq files on disk
    #    exactly, so a newly added filter can't silently escape the lint by not being listed.
    on_disk = {p.name for p in GUARD_DIR.glob("*.jq")}
    listed = set(REQUIRED_FILTERS)
    for name in sorted(listed - on_disk):
        failures.append(f"REQUIRED_FILTERS lists {name} but it is not on disk in {GUARD_DIR.name}/")
    for name in sorted(on_disk - listed):
        failures.append(
            f"{name} exists in {GUARD_DIR.name}/ but is not in REQUIRED_FILTERS "
            f"(add it so the lint pins its doc reference)"
        )

    # 2. Every canonical filter is referenced by the doc via `jq -f`. The reference form is
    #    `jq ... -f "$GUARD/<name>"` (or a bare path); require `-f` followed by anything up to the
    #    filename, anywhere in the doc — robust to the $GUARD/ prefix and to line wrapping.
    for name in REQUIRED_FILTERS:
        if name not in text:
            failures.append(f"doc does not reference canonical filter: {name}")
        elif not re.search(r"-f\s+\S*" + re.escape(name), text):
            failures.append(f"doc mentions {name} but not via `jq -f` (must be loaded as a filter file)")

    # 3. Both safety branches are present.
    for branch in REQUIRED_BRANCHES:
        if branch not in text:
            failures.append(f"doc dropped required safety branch: {branch}")

    # 4. Guard against re-inlining: the grounding guards and source extractors must be loaded via
    #    `-f`, never inlined. Rather than blacklist specific historical literals (which rot on any
    #    reword), forbid any *inline* `jq '...'` program (no `-f`) that references a grounding
    #    structure — these tokens only appear in the guard/sources filters, so an inline jq
    #    touching them is a re-inlined guard the behavioral tests would not cover. The one allowed
    #    inline jq is the plain verdict-TEXT extraction (`.candidates[0].content.parts...`), which
    #    references none of these tokens.
    GROUNDING_TOKENS = (
        "web_search_call", "url_citation", "groundingSupports",
        "groundingChunkIndices", "groundingChunks", "webSearchQueries",
    )
    # An inline jq invocation is `jq [flags without -f] '<program>'`; capture the quoted program.
    for m in re.finditer(r"jq\s+(?:-[A-Za-z]+\s+)*'([^']*)'", text):
        program = m.group(1)
        hit = next((t for t in GROUNDING_TOKENS if t in program), None)
        if hit:
            failures.append(
                f"doc inlines a jq program referencing {hit!r}; load the canonical .jq via "
                f"`jq -f` instead so the guard stays behavior-tested"
            )

    if failures:
        print(f"[cross-model-sync] FAIL: {len(failures)} issue(s):")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(
        f"[cross-model-sync] PASS: doc references all {len(REQUIRED_FILTERS)} canonical filters "
        f"via jq -f and retains the {', '.join(REQUIRED_BRANCHES)} branches"
    )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
