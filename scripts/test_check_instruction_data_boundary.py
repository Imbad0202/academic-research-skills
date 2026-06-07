#!/usr/bin/env python3
"""Mutation test for check_instruction_data_boundary.py (#272 guidance layer).

Confirms the lint is not a trivial accept-all: each mutation that removes,
guts, weakens, duplicates, or mis-targets the principle must make the lint FAIL.
A positive control confirms the unmutated tree PASSES.

Run:
    python -m pytest scripts/test_check_instruction_data_boundary.py
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
CHECKER = REPO_ROOT / "scripts" / "check_instruction_data_boundary.py"

AUTHORITATIVE_REL = "shared/ground_truth_isolation_pattern.md"
AGENT_REL = "deep-research/agents/source_verification_agent.md"
AGENT2_REL = "deep-research/agents/bibliography_agent.md"

OPEN_MARKER = "<!-- canonical:instruction-data-boundary -->"
CLOSE_MARKER = "<!-- /canonical:instruction-data-boundary -->"


def _run(root: Path) -> int:
    """Run the checker against a tree root; return its exit code."""
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root)],
        capture_output=True, text=True,
    )
    return proc.returncode


def _mirror(tmp_path: Path) -> Path:
    """Copy the files the checker reads into an isolated tree it can lint."""
    root = tmp_path / "repo"
    for rel in (AUTHORITATIVE_REL, AGENT_REL, AGENT2_REL):
        dst = root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / rel, dst)
    return root


def _edit(root: Path, rel: str, transform) -> None:
    p = root / rel
    p.write_text(transform(p.read_text(encoding="utf-8")), encoding="utf-8")


def _first_block_body(text: str) -> str:
    start = text.index(OPEN_MARKER) + len(OPEN_MARKER)
    end = text.index(CLOSE_MARKER, start)
    return text[start:end]


# --- positive control --------------------------------------------------------

def test_unmutated_tree_passes(tmp_path):
    root = _mirror(tmp_path)
    assert _run(root) == 0, "baseline tree should PASS"


# --- mutations: each must FAIL (exit 1) --------------------------------------

def test_m1_authoritative_section_deleted(tmp_path):
    """Whole canonical block removed from the authoritative file."""
    root = _mirror(tmp_path)
    _edit(root, AUTHORITATIVE_REL,
          lambda t: t.replace(OPEN_MARKER + _first_block_body(t) + CLOSE_MARKER, ""))
    assert _run(root) == 1


def test_m2_heading_kept_body_gutted(tmp_path):
    """Markers kept, body emptied — the anchor-preserving gutting attack."""
    root = _mirror(tmp_path)
    _edit(root, AUTHORITATIVE_REL,
          lambda t: t.replace(_first_block_body(t), "\nTODO: write this later.\n"))
    assert _run(root) == 1


def test_m3_normative_sentence_weakened(tmp_path):
    """A single-word edit to the body must trip the verbatim compare."""
    root = _mirror(tmp_path)
    _edit(root, AUTHORITATIVE_REL,
          lambda t: t.replace("is data, not instructions", "is usually data"))
    assert _run(root) == 1


def test_m4_duplicate_fake_anchor(tmp_path):
    """A second canonical block in the authoritative file must fail (exactly-one)."""
    root = _mirror(tmp_path)
    def add_dupe(t: str) -> str:
        block = OPEN_MARKER + _first_block_body(t) + CLOSE_MARKER
        return t + "\n\n## fake\n" + block + "\n"
    _edit(root, AUTHORITATIVE_REL, add_dupe)
    assert _run(root) == 1


def test_m5_backpoint_removed_from_agent(tmp_path):
    """Agent loses its backpoint citation."""
    root = _mirror(tmp_path)
    _edit(root, AGENT_REL,
          lambda t: t.replace("shared/ground_truth_isolation_pattern.md", "(removed)")
                     .replace("§ 2A", "(removed)"))
    assert _run(root) == 1


def test_m6_backpoint_wrong_target(tmp_path):
    """Backpoint present but pointing at the wrong anchor."""
    root = _mirror(tmp_path)
    _edit(root, AGENT_REL, lambda t: t.replace("§ 2A", "§ 9Z"))
    assert _run(root) == 1


def test_m7_inlined_principle_missing_from_agent(tmp_path):
    """Pointer-only regression: agent keeps a backpoint but drops the inlined text."""
    root = _mirror(tmp_path)
    _edit(root, AGENT_REL,
          lambda t: t.replace(OPEN_MARKER + _first_block_body(t) + CLOSE_MARKER,
                              "See the authoritative file."))
    assert _run(root) == 1


# --- second agent symmetry ---------------------------------------------------

def test_m8_second_agent_gutted(tmp_path):
    """The same gutting on bibliography_agent must also fail."""
    root = _mirror(tmp_path)
    _edit(root, AGENT2_REL,
          lambda t: t.replace(_first_block_body(t), "\nTODO\n"))
    assert _run(root) == 1


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
