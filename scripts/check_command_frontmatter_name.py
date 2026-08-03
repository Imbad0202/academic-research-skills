"""CI lint: every commands/*.md declares an explicit frontmatter `name`
equal to its filename stem (#633).

Since Claude Code v2.1.216, a plugin command's frontmatter `name` keeps the
namespaced form (`/academic-research-skills:ars-<mode>`) canonical while also
exposing the bare alias (`/ars-<mode>`) when no other command claims it. The
SessionStart announce script already advertises the bare form, so this lint
pins the invariant that makes that advertisement true on plugin installs:

  1. every command file carries a frontmatter block;
  2. the block declares `name:` exactly once (a duplicate key would let a
     second value silently win, re-opening the drift this lint closes);
  3. the declared value is byte-identical to the filename stem — no
     re-spelling, no Unicode confusables, no case drift. Equality against
     the ASCII stem fails closed on any non-ASCII homoglyph.

Pure stdlib; deterministic; read-only. Run from repo root:
    python3 scripts/check_command_frontmatter_name.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

COMMANDS_GLOB = "commands/*.md"

# Any frontmatter line whose KEY a YAML loader could resolve to `name`:
# optional indentation, optional single/double quoting, optional whitespace
# before the colon. A bare `name:` line scan would miss `"name": other` or
# `name : other` re-spellings, letting a later YAML-equivalent duplicate
# override the value while CI stays green (codex P2, PR #635). Instead of
# parsing YAML (this workflow is dependency-free), the lint requires the ONE
# canonical spelling below and rejects every other name-like variant, so no
# semantic override can ride in through a re-spelled key.
NAME_LIKE = re.compile(r"""^\s*(?:name|"name"|'name')\s*:""")
CANONICAL = re.compile(r"^name: (?P<value>.*)$")


def check_file(path: Path) -> list[str]:
    """Return a list of violation strings for one command file (empty = ok)."""
    rel = path.as_posix()
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return [f"{rel}: missing frontmatter block (file must start with '---')"]
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return [f"{rel}: unterminated frontmatter block (no closing '---')"]

    name_like = [line for line in lines[1:end] if NAME_LIKE.match(line)]
    if not name_like:
        return [f"{rel}: frontmatter has no `name:` key (required since #633)"]
    if len(name_like) > 1:
        return [
            f"{rel}: {len(name_like)} name-like keys in frontmatter — a "
            f"YAML-equivalent duplicate could override the canonical value"
        ]

    match = CANONICAL.match(name_like[0])
    if match is None:
        return [
            f"{rel}: non-canonical name key spelling {name_like[0]!r} — "
            f"only the exact form `name: <stem>` is accepted"
        ]

    expected = path.stem
    value = match.group("value")
    if value != expected:
        return [
            f"{rel}: frontmatter `name: {value}` != filename stem "
            f"`{expected}` (bare-alias exposure would advertise the wrong "
            f"command)"
        ]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="repository root containing commands/ (default: script's parent repo)",
    )
    args = parser.parse_args(argv)

    command_files = sorted(args.repo_root.glob(COMMANDS_GLOB))
    if not command_files:
        print(
            f"ERROR: no files matched {COMMANDS_GLOB} under {args.repo_root} "
            f"(wrong --repo-root, or the inventory moved?)"
        )
        return 1

    violations: list[str] = []
    for path in command_files:
        violations.extend(check_file(path))

    if violations:
        print(f"check_command_frontmatter_name: {len(violations)} violation(s)")
        for v in violations:
            print(f"  - {v}")
        return 1

    print(
        f"check_command_frontmatter_name: OK "
        f"({len(command_files)} command files, all `name:` == filename stem)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
