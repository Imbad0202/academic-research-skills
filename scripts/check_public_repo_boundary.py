#!/usr/bin/env python3
"""ARS public-repo boundary scan.

ARS is a public repo. Some terms ARE legitimate as generic educational
content (HEEACT as a Taiwan QA institution name in IRB / accreditation
discussion; Springer as a publisher name in citation guides; HEI as a
generic abbreviation for higher education institutions) but become
boundary-violating when they appear in **maintainer's private-project
context** (spec docs documenting specific session events, internal repo
names, internal file paths, internal product codenames).

This lint scans the repo for boundary-violating contexts. It is NOT a
blanket blocklist on the keywords themselves — it flags only the
co-occurrence patterns that indicate private-project leakage into public
spec / agent / template content.

External motivation: 2026-05-12 v3.7.3 ship retrospective. The author
re-used a v3.6.8 spec phrase ("HEEACT Springer chapter session") in a
new v3.7.3 spec doc on the (incorrect) reasoning that "v3.6.8 already
public ⇒ phrase is now licensed". This lint mechanically blocks that
class of error.

Exit codes:
  0 - no boundary violations
  1 - one or more violations
  2 - invocation error
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Patterns that indicate private-project leakage. Each is a regex that
# matches the BOUNDARY-VIOLATING context, not the keyword alone.
#
# Why each pattern is here:
#   1. HEEACT + Springer co-occurrence: the canonical 2026-04-30
#      production-session signature. Generic mention of HEEACT in
#      IRB/accreditation discussion does NOT match; only the
#      "HEEACT Springer ..." or "HEEACT ... chapter ..." pattern does.
#   2. hei-platform: private downstream repo name. Mentioning it by name
#      in ARS public docs is always leakage; the one legitimate context
#      is procedure documentation that explicitly TEACHES "don't leak
#      hei-platform" (caught by allowlist below).
#   3. Internal directory paths like `B_heeact_documents/`: private
#      project file structure.
#   4. Specific session identifiers + institutional names: e.g.
#      "HEEACT chapter session", "HEEACT [project] session" — same
#      class as pattern 1.
LEAKAGE_PATTERNS: list[tuple[str, re.Pattern]] = [
    (
        "HEEACT + Springer co-occurrence (private-session signature)",
        re.compile(r"HEEACT[^.\n]{0,80}Springer|Springer[^.\n]{0,80}HEEACT"),
    ),
    (
        "HEEACT + chapter/session co-occurrence",
        re.compile(r"HEEACT\s+\w*\s*chapter\s+session|HEEACT\s+chapter\s+(?:authoring|session)"),
    ),
    (
        "hei-platform private repo name",
        re.compile(r"\bhei-platform\b"),
    ),
    (
        "Internal directory path containing 'heeact'",
        re.compile(r"`[^`]*/B_heeact_documents/[^`]*`|B_HEEACT_HANDBOOK_QUOTE_REGISTRY"),
    ),
]

# Allowlist: substrings whose containing LINE is exempted from the scan.
# The allowlist is intentionally narrow — only contexts that are
# self-evidently teaching the boundary rule itself or maintainer
# attribution (which is already public on GitHub).
ALLOWLIST_LINE_SUBSTRINGS = [
    # CONTRIBUTING.md maintainer line — public GitHub identity
    "The repo is maintained by [Cheng-I Wu]",
    # Procedure that TEACHES the boundary rule
    "no hei-platform content, no personal data, no school names",
    # Memory file that documents the rule itself (won't be in ARS repo
    # anyway — defensive)
    "feedback_ars_public_repo_boundary",
    # Plan-doc grep pattern that TEACHES boundary scanning (the pattern
    # naturally contains the banned keyword as a search target)
    'grep -iE "(?:10|172|192)\\.[0-9]+\\.[0-9]+\\.[0-9]+|\\.local|hei-platform',
    # Review-protocol prompt template that TEACHES which patterns codex
    # should flag — the example list necessarily contains the keywords
    "(b) named private downstream repos (e.g. `hei-platform`",
]

# File patterns to scan. Markdown / YAML / Python / JSON.
SCAN_EXTENSIONS = {".md", ".yaml", ".yml", ".py", ".json"}

# Directories to skip.
SKIP_DIRS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".local-plans",  # local-only scratch
    "node_modules",
}

# This file is the lint itself — it MUST reference the banned keywords
# in its patterns and documentation. Skip self-scanning.
SELF_FILENAME = "check_public_repo_boundary.py"
TEST_SELF_FILENAME = "test_check_public_repo_boundary.py"


def is_line_allowlisted(line: str) -> bool:
    return any(s in line for s in ALLOWLIST_LINE_SUBSTRINGS)


def scan_file(path: Path) -> list[str]:
    violations: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return violations
    try:
        display_path = path.relative_to(REPO_ROOT)
    except ValueError:
        display_path = path  # outside repo root (e.g. test fixtures)
    for line_no, line in enumerate(text.split("\n"), start=1):
        if is_line_allowlisted(line):
            continue
        for name, pattern in LEAKAGE_PATTERNS:
            if pattern.search(line):
                violations.append(
                    f"{display_path}:{line_no}: [{name}] {line.strip()[:160]}"
                )
    return violations


def iter_files(root: Path):
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix not in SCAN_EXTENSIONS:
            continue
        if p.name in (SELF_FILENAME, TEST_SELF_FILENAME):
            continue
        yield p


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to scan (default: repo containing this script)",
    )
    args = parser.parse_args()

    if not args.root.exists():
        print(f"ERROR: root does not exist: {args.root}", file=sys.stderr)
        return 2

    all_violations: list[str] = []
    files_scanned = 0
    for f in iter_files(args.root):
        files_scanned += 1
        all_violations.extend(scan_file(f))

    if all_violations:
        for v in all_violations:
            print(v, file=sys.stderr)
        print(
            f"\n[public-repo-boundary lint] FAILED "
            f"({len(all_violations)} violation(s) across {files_scanned} files scanned)",
            file=sys.stderr,
        )
        print(
            "\nRemediation: replace private-project context with de-identified "
            "phrasing (e.g., 'YYYY-MM-DD production session' instead of named "
            "institution + publisher). See "
            "shared/templates/public_repo_boundary_remediation.md for examples "
            "(if present) or feedback_ars_public_repo_boundary memory.",
            file=sys.stderr,
        )
        return 1

    print(
        f"[public-repo-boundary lint] PASSED "
        f"({files_scanned} files scanned, 0 violations)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
