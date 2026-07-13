#!/usr/bin/env python3
"""Tests for check_tools_allowlist.py (#524).

Mutation discipline: every invariant has a passing case (green fixture tree +
the real repo tree) and failing cases proving the check fires when the
guarded property is broken. The load-bearing mutation is the SYMMETRIC
source+mirror edit re-adding Bash: it passes check_agents_mirror_sync.py
(byte-equal pair) and the name-keyed runtime guard lint, so before #524 it
sailed through CI green — the exact drift scenario the issue documents.
"""
from __future__ import annotations

import json
from pathlib import Path

from check_tools_allowlist import (
    ALLOWLISTED_FILES,
    MANIFEST,
    PINNED_TOOLS_LINE,
    REPO_ROOT,
    check,
)


def make_tree(tmp_path: Path) -> Path:
    """A green fixture tree: six allowlisted files carrying the pinned line,
    plus a minimal Bucket A manifest and one fenced/one unfenced extra agent."""
    for rel in ALLOWLISTED_FILES:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"---\nname: {p.stem}\ndescription: \"x\"\nmodel: inherit\n"
            f"{PINNED_TOOLS_LINE}\n---\n\nbody\n",
            encoding="utf-8",
        )
    manifest = tmp_path / MANIFEST
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"agents": {
        "report_compiler_agent": {},
        "research_architect_agent": {},
        "synthesis_agent": {},
        "eic_agent": {},
    }}), encoding="utf-8")
    # A Bucket A agent with NO tools key (inherit) — must pass untouched.
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.parent.mkdir(parents=True, exist_ok=True)
    eic.write_text("---\nname: eic_agent\n---\n\nbody\n", encoding="utf-8")
    # A NON-Bucket-A agent advertising Bash — allowed (invariant 2 is
    # scoped to fenced agents; the orchestrator legitimately holds shell).
    orch = tmp_path / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    orch.parent.mkdir(parents=True, exist_ok=True)
    orch.write_text(
        "---\nname: pipeline_orchestrator_agent\ntools: Read, Bash\n---\n\nbody\n",
        encoding="utf-8",
    )
    return tmp_path


def first_pair() -> tuple[str, str]:
    """One (source, mirror) pair for symmetric-edit mutations."""
    return ("deep-research/agents/research_architect_agent.md",
            "agents/research_architect_agent.md")


def rewrite_tools_line(path: Path, new_line: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace(PINNED_TOOLS_LINE, new_line),
                    encoding="utf-8")


# --- invariant 0: the real tree is green --------------------------------------

def test_real_repo_passes():
    assert check(REPO_ROOT) == []


# --- green fixture -------------------------------------------------------------

def test_green_tree_passes(tmp_path):
    make_tree(tmp_path)
    assert check(tmp_path) == []


# --- invariant 1: exact pinned value -------------------------------------------

def test_symmetric_bash_readd_fails_on_both_files(tmp_path):
    # THE #524 drift scenario: source+mirror edited together to re-add Bash.
    # Mirror-sync stays green (byte-equal pair); this lint must fire on BOTH.
    make_tree(tmp_path)
    src, mirror = first_pair()
    for rel in (src, mirror):
        rewrite_tools_line(tmp_path / rel, PINNED_TOOLS_LINE + ", Bash")
    errs = check(tmp_path)
    assert any(src in e and "drifted" in e for e in errs)
    assert any(mirror in e and "drifted" in e for e in errs)


def test_dropped_tool_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src, "tools: Read, Write, Edit, Glob")
    errs = check(tmp_path)
    assert any(src in e and "drifted" in e for e in errs)


def test_typoed_tool_name_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src, "tools: Read, Write, Edit, Gerp, Glob")
    errs = check(tmp_path)
    assert any(src in e and "drifted" in e for e in errs)


def test_trailing_whitespace_is_drift(tmp_path):
    # Exact byte pin: even whitespace divergence must fire, or the "exact
    # line" contract quietly weakens to "roughly that line".
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src, PINNED_TOOLS_LINE + " ")
    errs = check(tmp_path)
    assert any(src in e and "drifted" in e for e in errs)


def test_missing_tools_line_fails_as_widening(tmp_path):
    # Dropping the key silently widens capability (agent inherits ALL tools).
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(p.read_text(encoding="utf-8").replace(
        PINNED_TOOLS_LINE + "\n", ""), encoding="utf-8")
    errs = check(tmp_path)
    assert any(src in e and "no `tools:` line" in e for e in errs)


def test_duplicate_tools_line_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    rewrite_tools_line(tmp_path / src,
                       f"{PINNED_TOOLS_LINE}\n{PINNED_TOOLS_LINE}")
    errs = check(tmp_path)
    assert any(src in e and "2 `tools:` lines" in e for e in errs)


def test_missing_allowlisted_file_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    (tmp_path / src).unlink()
    errs = check(tmp_path)
    assert any(src in e and "missing" in e for e in errs)


def test_no_frontmatter_fails(tmp_path):
    make_tree(tmp_path)
    src, _ = first_pair()
    (tmp_path / src).write_text("body only\n", encoding="utf-8")
    errs = check(tmp_path)
    assert any(src in e and "frontmatter" in e for e in errs)


def test_body_tools_line_does_not_satisfy_pin(tmp_path):
    # The pinned line must live in FRONTMATTER; a body mention is not a grant.
    make_tree(tmp_path)
    src, _ = first_pair()
    p = tmp_path / src
    p.write_text(p.read_text(encoding="utf-8").replace(
        PINNED_TOOLS_LINE + "\n", "") + f"\n{PINNED_TOOLS_LINE}\n",
        encoding="utf-8")
    errs = check(tmp_path)
    assert any(src in e and "no `tools:` line" in e for e in errs)


# --- invariant 2: Bucket A frontmatter must not advertise Bash ------------------

def test_bucket_a_agent_advertising_bash_fails(tmp_path):
    make_tree(tmp_path)
    eic = tmp_path / "academic-paper-reviewer/agents/eic_agent.md"
    eic.write_text("---\nname: eic_agent\ntools: Read, Bash\n---\n\nbody\n",
                   encoding="utf-8")
    errs = check(tmp_path)
    assert any("eic_agent" in e and "Bash" in e for e in errs)


def test_non_bucket_a_agent_with_bash_passes(tmp_path):
    # Baked into the green fixture (pipeline_orchestrator_agent declares
    # Bash); assert it raises nothing on its own.
    make_tree(tmp_path)
    assert check(tmp_path) == []


def test_bucket_a_agent_without_tools_key_passes(tmp_path):
    # eic_agent in the green fixture has no tools key — inherit is fine;
    # the runtime guard still fences it.
    make_tree(tmp_path)
    assert not [e for e in check(tmp_path) if "eic_agent" in e]


def test_missing_manifest_fails_closed(tmp_path):
    make_tree(tmp_path)
    (tmp_path / MANIFEST).unlink()
    errs = check(tmp_path)
    assert any(MANIFEST in e and "failing closed" in e for e in errs)


def test_unparseable_manifest_fails_closed(tmp_path):
    make_tree(tmp_path)
    (tmp_path / MANIFEST).write_text("{not json", encoding="utf-8")
    errs = check(tmp_path)
    assert any(MANIFEST in e and "failing closed" in e for e in errs)


# --- lock shape ------------------------------------------------------------------

def test_pinned_line_is_the_frozen_514_value():
    # Editing the allowlist is a deliberate security-surface change: it must
    # touch this lint in the same commit. This test is the second witness.
    assert PINNED_TOOLS_LINE == "tools: Read, Write, Edit, Grep, Glob"


def test_allowlisted_files_are_the_three_pairs():
    assert set(ALLOWLISTED_FILES) == {
        "deep-research/agents/report_compiler_agent.md",
        "deep-research/agents/research_architect_agent.md",
        "deep-research/agents/synthesis_agent.md",
        "agents/report_compiler_agent.md",
        "agents/research_architect_agent.md",
        "agents/synthesis_agent.md",
    }
