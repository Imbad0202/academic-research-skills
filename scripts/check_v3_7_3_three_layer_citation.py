#!/usr/bin/env python3
"""v3.7.3 Three-Layer Citation lint.

External motivation: Zhao et al. arXiv:2605.07723 (2026-05) — corpus-scale
audit of LLM hallucinations finds the L3 claim-faithfulness gap unaddressed
by existing safeguards. v3.7.3 extends Two-Layer Citation Emission with a
structured anchor marker. Spec:
  docs/design/2026-05-12-ars-v3.7.3-claim-faithfulness-and-contaminated-source-spec.md
  §3.1

The lint checks a draft markdown file (e.g., output of synthesis_agent,
draft_writer_agent, report_compiler_agent) for:

  1. Every `<!--ref:slug-->` is followed by `<!--anchor:<kind>:<value>-->`
     where <kind> ∈ {quote, page, section, paragraph, none}.
  2. When <kind> = quote, the URL-decoded value is <=25 words by whitespace
     split (per shared/references/word_count_conventions.md).
  3. No `<!--anchor:...-->` marker stands alone without a preceding
     `<!--ref:slug-->`.

Exit codes:
  0 - all citations conform
  1 - one or more violations
  2 - invocation error

This is a static lint over markdown text. It does NOT verify that the
anchor value is faithful to the cited source (that is v3.8 L3 audit scope).
It only verifies the anchor channel exists and is well-formed.

Usage:
  python scripts/check_v3_7_3_three_layer_citation.py <path-to-draft.md> [...]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from urllib.parse import unquote

REF_PATTERN = re.compile(r"<!--ref:([A-Za-z][A-Za-z0-9_:-]*)\s*([^-]*?)-->")
ANCHOR_PATTERN = re.compile(
    r"<!--anchor:(quote|page|section|paragraph|none):([^>]*?)-->"
)
ANY_ANCHOR_PATTERN = re.compile(r"<!--anchor:")
VALID_KINDS = {"quote", "page", "section", "paragraph", "none"}
QUOTE_WORD_CAP = 25


def _strip_fenced_code_blocks(text: str) -> str:
    """Replace content inside ``` fenced code blocks with blank lines so
    line numbers in violation messages stay accurate. v3.7.3 F7 closure
    (gemini review): example ref/anchor markers in spec docs and
    documentation belong inside code fences and must not be linted as
    contract violations.

    Handles ``` and ~~~ fences. Indented (4-space) code blocks are not
    handled — they are rare for Markdown contributors and unlikely to
    contain HTML comment markers in practice."""
    out_lines = []
    in_fence = False
    fence_char = None
    for line in text.split("\n"):
        stripped = line.lstrip()
        if not in_fence:
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = True
                fence_char = stripped[:3]
                out_lines.append(line)  # keep fence opener
                continue
            out_lines.append(line)
        else:
            if stripped.startswith(fence_char):
                in_fence = False
                fence_char = None
                out_lines.append(line)  # keep fence closer
                continue
            # Blank out content inside fence
            out_lines.append("")
    return "\n".join(out_lines)


def lint_file(path: Path) -> list[str]:
    """Return a list of violation strings; empty list = PASS."""
    if not path.exists():
        return [f"{path}: file does not exist"]
    raw_text = path.read_text(encoding="utf-8")
    text = _strip_fenced_code_blocks(raw_text)
    violations: list[str] = []

    # Find every ref marker; the very next non-whitespace token MUST be an
    # anchor marker. Allow optional whitespace/newline between ref and
    # anchor (F2). The ref marker can carry 0-2 status suffix tokens:
    #   `<!--ref:slug-->`                                  (0 — pre-finalizer)
    #   `<!--ref:slug ok-->` / `<!--ref:slug LOW-WARN-->`  (1 — post-finalizer v3.7.1)
    #   `<!--ref:slug ok CONTAMINATED-PREPRINT-->`         (2 — v3.7.3 contamination annotation)
    # v3.7.3 F8 closure (codex round-2): regex previously allowed only 0-1
    # tokens, causing finditer to skip 2-token contamination markers
    # entirely — violations on those refs went undetected.
    ref_anchor_pattern = re.compile(
        r"<!--ref:[A-Za-z][A-Za-z0-9_:-]*"
        r"(?:\s+[\w-]+(?:\+[\w-]+)*){0,2}"
        r"\s*-->"
        r"(\s*<!--anchor:([^:>]*):([^>]*?)-->)?"
    )
    for m in ref_anchor_pattern.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        anchor_match = m.group(1)
        if anchor_match is None:
            violations.append(
                f"{path}:{line_no}: ref marker without trailing anchor "
                f"(v3.7.3 R-L3-1-A): {m.group(0)!r}"
            )
            continue
        kind = m.group(2)
        value = m.group(3)
        if kind not in VALID_KINDS:
            violations.append(
                f"{path}:{line_no}: invalid anchor kind {kind!r}; "
                f"must be one of {sorted(VALID_KINDS)}"
            )
            continue
        # v3.7.3 F9 closure (codex round-2): empty value on a non-`none`
        # anchor kind bypasses the NO-LOCATOR gate while pretending to
        # satisfy the locator contract. Only `none` may have an empty
        # value; every other kind MUST have a non-empty locator payload.
        if kind != "none" and value.strip() == "":
            violations.append(
                f"{path}:{line_no}: empty anchor value for kind "
                f"{kind!r}; v3.7.3 F9 — only `none` may have an empty "
                f"value, every other kind requires a non-empty locator "
                f"payload"
            )
            continue
        if kind == "quote":
            decoded = unquote(value)
            word_count = len(decoded.split())
            if word_count > QUOTE_WORD_CAP:
                violations.append(
                    f"{path}:{line_no}: quote anchor exceeds {QUOTE_WORD_CAP} "
                    f"words by whitespace split (got {word_count}); "
                    f"v3.7.3 R-L3-1-B — replace with page or section locator"
                )
            # Raw `--` in the URL-encoded `quote:` value will prematurely
            # close the HTML comment in many parsers (gemini review F1).
            # Standard RFC 3986 percent-encoding does NOT encode `-`; the
            # v3.7.3 contract additionally requires `-` -> `%2D`. So the
            # ENCODED value (before unquote) must not contain consecutive
            # hyphens. Check the raw `value` not `decoded`.
            if "--" in value:
                violations.append(
                    f"{path}:{line_no}: quote anchor contains raw `--` "
                    f"in URL-encoded value; v3.7.3 F1 requires `-` to be "
                    f"percent-encoded as `%2D` to prevent premature HTML "
                    f"comment termination"
                )

    # Orphan anchor markers (anchor without preceding ref) are also a
    # violation. Detect anchor markers that are NOT immediately preceded
    # by a ref marker (allowing whitespace).
    orphan_pattern = re.compile(
        r"(?<!-->)\s*<!--anchor:([^:>]*):([^>]*?)-->"
    )
    for m in orphan_pattern.finditer(text):
        # Check if the previous text ends with a ref marker.
        preceding = text[: m.start()]
        if not re.search(
            r"<!--ref:[A-Za-z][A-Za-z0-9_:-]*(?:\s+[\w-]+(?:\+[\w-]+)*){0,2}\s*-->\s*$",
            preceding,
        ):
            line_no = text.count("\n", 0, m.start()) + 1
            violations.append(
                f"{path}:{line_no}: orphan anchor marker without preceding "
                f"ref marker: {m.group(0)!r}"
            )

    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help="markdown files to lint",
    )
    args = parser.parse_args()

    total_violations: list[str] = []
    for p in args.paths:
        total_violations.extend(lint_file(p))

    if total_violations:
        print("\n".join(total_violations), file=sys.stderr)
        print(
            f"\n[v3.7.3 three-layer-citation lint] FAILED "
            f"({len(total_violations)} violation(s))",
            file=sys.stderr,
        )
        return 1

    print(
        f"[v3.7.3 three-layer-citation lint] PASSED "
        f"({len(args.paths)} file(s) scanned)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
