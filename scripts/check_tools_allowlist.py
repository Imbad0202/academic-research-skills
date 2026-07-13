#!/usr/bin/env python3
"""Lint: pin the #514 tools-allowlist CONTENT on the three plugin agents (#524).

#521 shipped `tools: Read, Write, Edit, Grep, Glob` on the three top-level
plugin agents (deep-research sources + agents/ mirrors), but no lint read a
frontmatter `tools` key: check_agents_mirror_sync.py pins mirror==source
byte-equality (the PAIR, never the VALUE), and the runtime write-scope guard
(scripts/ars_write_scope_guard.py) keys on agent NAME, never frontmatter. A
future PR editing a source+mirror pair symmetrically back to `..., Bash` (or
dropping `Grep`, or typoing a tool name) would pass every CI gate green —
exactly the drift class the repo's defrift locks exist to catch (cf. the
v3.15 locks). This lint pins the VALUE.

Invariants:
  1. Every file in ALLOWLISTED_FILES exists and carries, inside its YAML
     frontmatter, exactly ONE `tools:` line, byte-equal to PINNED_TOOLS_LINE.
     Changing the allowlist is a deliberate security-surface change: edit the
     agent files AND this lint's PINNED_TOOLS_LINE in the same commit
     (standard lock semantics — the lint edit is the review surface).
  2. Frontmatter/guard reconciliation: any agent file under AGENT_DIRS whose
     frontmatter `name` is a Bucket A key in
     scripts/ars_phase_scope_manifest.json must NOT list Bash in a `tools:`
     key. The runtime guard denies Bucket A agents ALL Bash (zero
     fail-open); a frontmatter advertising Bash would silently widen
     capability in hook-less installs while contradicting the guard in
     hook-active ones. Agents with no `tools:` key are untouched (they
     inherit; the runtime guard still fences them).

The manifest is load-bearing for invariant 2, so a missing/unparseable
manifest FAILS the lint (fail-closed) rather than skipping the check.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The exact frontmatter line shipped by #521 (frozen #514 spec). Single
# source of truth for the VALUE — a symmetric source+mirror edit cannot
# change it without touching this lint in the same commit.
PINNED_TOOLS_LINE = "tools: Read, Write, Edit, Grep, Glob"

# The six #514 surfaces: three canonical sources + three agents/ mirrors
# (mirror==source byte-equality is check_agents_mirror_sync.py's job; the
# mirrors are still listed here so THIS lint stays correct even if that one
# is skipped or edited).
ALLOWLISTED_FILES = (
    "deep-research/agents/report_compiler_agent.md",
    "deep-research/agents/research_architect_agent.md",
    "deep-research/agents/synthesis_agent.md",
    "agents/report_compiler_agent.md",
    "agents/research_architect_agent.md",
    "agents/synthesis_agent.md",
)

# Every directory that holds agent prompt files (invariant 2 scan surface).
AGENT_DIRS = (
    "deep-research/agents",
    "academic-paper/agents",
    "academic-paper-reviewer/agents",
    "academic-pipeline/agents",
    "shared/agents",
    "agents",
)

MANIFEST = "scripts/ars_phase_scope_manifest.json"


def _frontmatter(text: str) -> list[str] | None:
    """Return the YAML frontmatter lines (between the opening and closing
    `---` fences), or None when the file has no frontmatter block."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:i]
    return None


def _fm_value(fm_lines: list[str], key: str) -> list[str]:
    """All frontmatter lines for `key:` (verbatim, for exact-pin checks)."""
    prefix = f"{key}:"
    return [ln for ln in fm_lines if ln.startswith(prefix)]


def _bucket_a_names(root: Path) -> tuple[set[str] | None, str | None]:
    """Bucket A agent names from the manifest, or (None, error)."""
    mp = root / MANIFEST
    try:
        agents = json.loads(mp.read_text(encoding="utf-8")).get("agents")
    except (OSError, json.JSONDecodeError) as exc:
        return None, (
            f"{MANIFEST}: unreadable or unparseable ({exc}) — invariant 2 "
            "(frontmatter/guard reconciliation) cannot run; failing closed."
        )
    if not isinstance(agents, dict):
        return None, (
            f"{MANIFEST}: no `agents` object — invariant 2 cannot run; "
            "failing closed."
        )
    return set(agents), None


def check(root: Path) -> list[str]:
    errors: list[str] = []

    # --- invariant 1: exact pinned line on each of the six files -------------
    for rel in ALLOWLISTED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(
                f"{rel}: allowlisted agent file is missing — the #514 "
                "surface changed; update ALLOWLISTED_FILES in "
                "check_tools_allowlist.py deliberately or restore the file."
            )
            continue
        fm = _frontmatter(path.read_text(encoding="utf-8"))
        if fm is None:
            errors.append(f"{rel}: no YAML frontmatter block found.")
            continue
        tools_lines = _fm_value(fm, "tools")
        if not tools_lines:
            errors.append(
                f"{rel}: frontmatter has no `tools:` line — the #514 "
                "allowlist was dropped (a silent capability widening: the "
                "agent would inherit ALL tools). Restore "
                f"`{PINNED_TOOLS_LINE}`."
            )
        elif len(tools_lines) > 1:
            errors.append(
                f"{rel}: {len(tools_lines)} `tools:` lines in frontmatter — "
                "exactly one expected."
            )
        elif tools_lines[0] != PINNED_TOOLS_LINE:
            errors.append(
                f"{rel}: tools allowlist drifted from the frozen #514 "
                f"value.\n    expected: {PINNED_TOOLS_LINE}\n    found:    "
                f"{tools_lines[0]}\n  Changing the allowlist is a deliberate "
                "security-surface change: update PINNED_TOOLS_LINE in "
                "check_tools_allowlist.py in the same commit."
            )

    # --- invariant 2: no Bucket A agent advertises Bash ----------------------
    bucket_a, manifest_err = _bucket_a_names(root)
    if manifest_err:
        errors.append(manifest_err)
        return errors
    for rel_dir in AGENT_DIRS:
        d = root / rel_dir
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            fm = _frontmatter(path.read_text(encoding="utf-8"))
            if fm is None:
                continue
            names = _fm_value(fm, "name")
            name = names[0].split(":", 1)[1].strip() if names else ""
            if name not in bucket_a:
                continue
            for tools_line in _fm_value(fm, "tools"):
                declared = [
                    t.strip()
                    for t in tools_line.split(":", 1)[1].split(",")
                ]
                if "Bash" in declared:
                    errors.append(
                        f"{path.relative_to(root).as_posix()}: frontmatter "
                        f"advertises Bash but `{name}` is a Bucket A agent "
                        f"in {MANIFEST} — the runtime guard denies Bucket A "
                        "agents ALL Bash (zero fail-open), so this grant is "
                        "either dead (hook-active) or a silent widening "
                        "(hook-less). Remove Bash from the tools list."
                    )

    return errors


def main() -> int:
    errors = check(REPO_ROOT)
    if errors:
        print("tools allowlist check failed (#524):")
        for err in errors:
            print(f"- {err}")
        return 1
    print("tools allowlist check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
