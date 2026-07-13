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
     frontmatter, exactly ONE line whose key resolves to `tools` (quoted or
     indented key variants count toward the total, so a second `"tools":`
     line cannot hide behind the pinned one), and that line is byte-equal to
     PINNED_TOOLS_LINE. Lines are split on bare `\\n` with CR retained, so a
     CRLF-converted file is drift, not a silent pass. As a belt against YAML
     forms the line scan cannot see, the frontmatter is ALSO parsed as YAML
     and the semantic `tools` value must normalize to exactly the canonical
     five tools (duplicate keys resolve last-wins in YAML, so a smuggled
     second key diverges semantically even if a line-level trick slipped
     past the count). Changing the allowlist is a deliberate
     security-surface change: edit the agent files AND this lint's
     PINNED_TOOLS_LINE in the same commit (standard lock semantics — the
     lint edit is the review surface).
  2. Frontmatter/guard reconciliation: any agent file under AGENT_DIRS whose
     frontmatter `name` is a Bucket A key in
     scripts/ars_phase_scope_manifest.json must NOT declare Bash in a
     `tools:` key — in ANY YAML-legal form (comma string, flow list, block
     list, quoted values, inline comments, `Bash(...)` permission
     specifiers). The runtime guard denies Bucket A agents ALL Bash (zero
     fail-open); a frontmatter advertising Bash would silently widen
     capability in hook-less installs while contradicting the guard in
     hook-active ones. `Bash` is matched as an exact base tool name
     (`BashOutput` is a different tool and is not flagged). Agents with no
     `tools:` key are untouched (they inherit; the runtime guard still
     fences them). Fail-closed rules: a Bucket A agent whose frontmatter is
     not parseable YAML, or whose `tools` value has an unrecognized shape,
     is an ERROR, never a skip.

The manifest is load-bearing for invariant 2, so a missing, unparseable, or
non-mapping manifest FAILS the lint (fail-closed) rather than skipping.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent

# The exact frontmatter line shipped by #521 (frozen #514 spec). Single
# source of truth for the VALUE — a symmetric source+mirror edit cannot
# change it without touching this lint in the same commit.
PINNED_TOOLS_LINE = "tools: Read, Write, Edit, Grep, Glob"
CANONICAL_TOOLS = ("Read", "Write", "Edit", "Grep", "Glob")

# Any frontmatter line whose KEY resolves to `tools`: bare, quoted, or
# indented. Used for the exactly-one count so a `"tools":` duplicate cannot
# coexist with the pinned bare line.
_TOOLS_KEY_RE = re.compile(r'^\s*["\']?tools["\']?\s*:')

# The six #514 surfaces: three canonical sources + three agents/ mirrors
# (mirror==source byte-equality is check_agents_mirror_sync.py's job; the
# mirrors are still listed here so THIS lint stays correct even if that one
# is skipped or edited — deliberately re-derived, not imported, per the
# repo's independent-second-witness lint convention).
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


def _read_raw(path: Path) -> str:
    """Read WITHOUT universal-newline translation, so a CRLF file keeps its
    `\\r` bytes and cannot satisfy an exact LF line pin."""
    return path.read_bytes().decode("utf-8")


def _frontmatter(text: str) -> list[str] | None:
    """Raw YAML frontmatter lines (between the `---` fences), split on bare
    `\\n` with CR retained, or None when the file has no frontmatter block."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return lines[1:i]
    return None


def _parse_yaml(fm_lines: list[str]) -> dict | None:
    """The frontmatter parsed as a YAML mapping, or None when it is not one."""
    try:
        data = yaml.safe_load("\n".join(fm_lines))
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def _normalized_tools(value: object) -> list[str] | None:
    """A frontmatter `tools` value normalized to base tool names, or None
    when the shape is unrecognized. Accepts the comma-string form and YAML
    lists; a `Bash(git:*)`-style permission specifier normalizes to `Bash`."""
    if isinstance(value, str):
        items: list[object] = value.split(",")
    elif isinstance(value, list):
        items = value
    else:
        return None
    out = []
    for item in items:
        base = str(item).strip().split("(", 1)[0].strip()
        if base:
            out.append(base)
    return out


def _raw_name(fm_lines: list[str]) -> str:
    """Best-effort `name:` extraction for files whose YAML does not parse."""
    for ln in fm_lines:
        if ln.startswith("name:"):
            return ln.split(":", 1)[1].strip().strip("\"'")
    return ""


def _bucket_a_names(root: Path) -> tuple[set[str] | None, str | None]:
    """Bucket A agent names from the manifest, or (None, error)."""
    mp = root / MANIFEST
    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, (
            f"{MANIFEST}: unreadable or unparseable ({exc}) — invariant 2 "
            "(frontmatter/guard reconciliation) cannot run; failing closed."
        )
    agents = data.get("agents") if isinstance(data, dict) else None
    if not isinstance(agents, dict):
        return None, (
            f"{MANIFEST}: no `agents` mapping — invariant 2 cannot run; "
            "failing closed."
        )
    return set(agents), None


def check(root: Path) -> list[str]:
    errors: list[str] = []

    # --- invariant 1: exact pinned line + semantic value on the six files ----
    for rel in ALLOWLISTED_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(
                f"{rel}: allowlisted agent file is missing — the #514 "
                "surface changed; update ALLOWLISTED_FILES in "
                "check_tools_allowlist.py deliberately or restore the file."
            )
            continue
        fm = _frontmatter(_read_raw(path))
        if fm is None:
            errors.append(f"{rel}: no YAML frontmatter block found.")
            continue
        key_lines = [ln for ln in fm if _TOOLS_KEY_RE.match(ln)]
        if not key_lines:
            errors.append(
                f"{rel}: frontmatter has no `tools:` line — the #514 "
                "allowlist was dropped (a silent capability widening: the "
                "agent would inherit ALL tools). Restore "
                f"`{PINNED_TOOLS_LINE}`."
            )
        elif len(key_lines) > 1:
            errors.append(
                f"{rel}: {len(key_lines)} frontmatter lines carry a "
                "`tools` key (quoted/indented variants included) — exactly "
                "one expected; a duplicate key can override the pinned line "
                "under YAML last-wins resolution."
            )
        elif key_lines[0] != PINNED_TOOLS_LINE:
            errors.append(
                f"{rel}: tools allowlist drifted from the frozen #514 "
                f"value.\n    expected: {PINNED_TOOLS_LINE}\n    found:    "
                f"{key_lines[0]!r}\n  Changing the allowlist is a deliberate "
                "security-surface change: update PINNED_TOOLS_LINE in "
                "check_tools_allowlist.py in the same commit."
            )
        # Semantic belt: catches any YAML form the line scan cannot see.
        data = _parse_yaml(fm)
        if data is None:
            errors.append(
                f"{rel}: frontmatter is not a parseable YAML mapping — the "
                "semantic tools check cannot run; failing closed."
            )
        elif _normalized_tools(data.get("tools")) != list(CANONICAL_TOOLS):
            errors.append(
                f"{rel}: the SEMANTIC `tools` value (YAML-parsed, duplicate "
                "keys resolve last-wins) diverges from the canonical "
                f"{', '.join(CANONICAL_TOOLS)} — the effective allowlist is "
                "not what the pinned line claims."
            )

    # --- invariant 2: no Bucket A agent declares Bash -------------------------
    bucket_a, manifest_err = _bucket_a_names(root)
    if manifest_err:
        errors.append(manifest_err)
        return errors
    for rel_dir in AGENT_DIRS:
        d = root / rel_dir
        if not d.is_dir():
            continue
        for path in sorted(d.glob("*.md")):
            rel = path.relative_to(root).as_posix()
            fm = _frontmatter(_read_raw(path))
            if fm is None:
                continue
            data = _parse_yaml(fm)
            if data is None:
                if _raw_name(fm) in bucket_a:
                    errors.append(
                        f"{rel}: Bucket A agent frontmatter is not "
                        "parseable YAML — cannot reconcile its tools "
                        "against the runtime guard; failing closed."
                    )
                continue
            name = str(data.get("name") or "").strip()
            if name not in bucket_a or "tools" not in data:
                continue
            declared = _normalized_tools(data["tools"])
            if declared is None:
                errors.append(
                    f"{rel}: Bucket A agent `{name}` has a `tools` value "
                    "of unrecognized shape — cannot verify it excludes "
                    "Bash; failing closed."
                )
            elif "Bash" in declared:
                errors.append(
                    f"{rel}: frontmatter declares Bash but `{name}` is a "
                    f"Bucket A agent in {MANIFEST} — the runtime guard "
                    "denies Bucket A agents ALL Bash (zero fail-open), so "
                    "this grant is either dead (hook-active) or a silent "
                    "widening (hook-less). Remove Bash from the tools list."
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
