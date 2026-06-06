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


def _strip_trailing_comment(line: str) -> str:
    """Remove a trailing bash comment (` #...`) that is outside quotes.

    A bash comment begins at a `#` that starts a word — i.e. at line start or preceded by
    whitespace — and is not inside a single- or double-quoted string. Stripping it means a
    filename surviving only in a trailing comment (`jq -r ".x"  # jq -f "$GUARD/x.jq"`) can't
    satisfy the wiring check. A `#` inside a quoted string (or a `$#`/`${#}`-style token) is left
    intact: it must follow whitespace and be unquoted to count as a comment.
    """
    in_single = in_double = False
    prev = ""
    for i, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double and (i == 0 or prev.isspace()):
            return line[:i].rstrip()
        prev = ch
    return line


def _bash_code_lines(text: str) -> list[str]:
    """Return the executable lines inside ```bash fenced blocks, comments removed.

    A comment-only line (first non-whitespace char is `#`) is dropped entirely; a trailing comment
    on an executable line is stripped (see `_strip_trailing_comment`). Both matter for the wiring
    check: a filename mentioned only in a comment — whole-line or trailing — must not count as the
    doc loading that filter via `jq -f`.
    """
    lines: list[str] = []
    in_block = False
    for raw in text.splitlines():
        stripped = raw.strip()
        if not in_block and stripped.startswith("```bash"):
            in_block = True
            continue
        if in_block and stripped == "```":
            in_block = False
            continue
        if in_block and not stripped.startswith("#"):
            code = _strip_trailing_comment(raw)
            if code.strip():
                lines.append(code)
    return lines


def main() -> int:
    failures: list[str] = []

    if not DOC.is_file():
        print(f"[cross-model-sync] FAIL: doc not found: {DOC}")
        return 1
    text = DOC.read_text(encoding="utf-8")

    # Operate the wiring/inline checks on EXECUTABLE bash only — lines inside ```bash fences with
    # comment lines stripped — so a commented-out `jq -f` reference (or a filename mentioned only in
    # prose / a comment) can't satisfy check 2, and a commented example can't trip check 4.
    bash_code = "\n".join(_bash_code_lines(text))

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

    # 2. Every canonical filter is loaded by executable bash via `jq ... -f .../<name>`. Checking
    #    bash_code (not the whole doc) means a commented-out or prose mention doesn't count.
    for name in REQUIRED_FILTERS:
        if not re.search(r"jq\b[^\n']*-f\s+\S*" + re.escape(name), bash_code):
            failures.append(
                f"doc does not load {name} via `jq -f` in an executable bash line "
                f"(prose/comment mentions don't count)"
            )

    # 3. Both safety branches are present (checked against the whole doc — they appear in prose
    #    and bash alike, and dropping them anywhere is the regression we care about).
    for branch in REQUIRED_BRANCHES:
        if branch not in text:
            failures.append(f"doc dropped required safety branch: {branch}")

    # 4. Guard against re-inlining: the grounding guards and source extractors must be loaded via
    #    `-f`, never inlined. Rather than blacklist specific historical literals (which rot on any
    #    reword), forbid any *inline* `jq` program (no `-f`) that references a grounding structure —
    #    these tokens only appear in the guard/sources filters, so an inline jq touching them is a
    #    re-inlined guard the behavioral tests would not cover. The one allowed inline jq is the
    #    plain verdict-TEXT extraction (`.candidates[0].content.parts...`), which references none of
    #    these tokens. Both single- and double-quoted inline programs are scanned.
    GROUNDING_TOKENS = (
        "web_search_call", "url_citation", "groundingSupports",
        "groundingChunkIndices", "groundingChunks", "webSearchQueries",
    )
    # An inline jq invocation is `jq [flags, none being -f] '<program>'` or "<program>".
    for m in re.finditer(r"jq\s+((?:-[A-Za-z]+\s+)*)(['\"])(.*?)\2", bash_code, re.DOTALL):
        flags, program = m.group(1), m.group(3)
        if re.search(r"(?<!\S)-f(?!\S)", flags):
            continue  # `-f` means it loads a file, not an inline program
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
