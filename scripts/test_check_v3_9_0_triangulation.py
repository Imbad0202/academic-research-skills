#!/usr/bin/env python3
"""Tests for check_v3_9_0_triangulation.py lint per spec v3.9.0 §3.8."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parent / "check_v3_9_0_triangulation.py"
REPO_ROOT = Path(__file__).resolve().parents[1]


def run_lint(args: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, str(SCRIPT)] + (args or [])
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))


def test_lint_passes_on_clean_repo():
    """After T7 lands (formatter has all 9 allowlist entries), lint passes."""
    result = run_lint()
    assert result.returncode == 0, f"Lint failed: stderr={result.stderr}\nstdout={result.stdout}"


def test_lint_detects_missing_allowlist_entry(tmp_path):
    """Remove CONTAMINATED-TRIANGULATION-UNMATCHED from formatter — lint fails."""
    formatter = REPO_ROOT / "academic-paper/agents/formatter_agent.md"
    content = formatter.read_text()
    broken_content = content.replace(
        "`CONTAMINATED-TRIANGULATION-UNMATCHED`, ",
        "",
    )
    broken = tmp_path / "formatter_agent.md"
    broken.write_text(broken_content)
    result = run_lint(["--formatter-path", str(broken)])
    assert result.returncode == 1
    assert "CONTAMINATED-TRIANGULATION-UNMATCHED" in result.stderr


def test_lint_detects_extra_allowlist_entry(tmp_path):
    """Add a non-spec CONTAMINATED-* token to formatter — lint fails."""
    formatter = REPO_ROOT / "academic-paper/agents/formatter_agent.md"
    content = formatter.read_text()
    broken_content = content.replace(
        "`CONTAMINATED-PREPRINT`,",
        "`CONTAMINATED-PREPRINT`, `CONTAMINATED-FABRICATED`,",
    )
    broken = tmp_path / "formatter_agent.md"
    broken.write_text(broken_content)
    result = run_lint(["--formatter-path", str(broken)])
    assert result.returncode == 1
    assert "CONTAMINATED-FABRICATED" in result.stderr


def test_lint_detects_refusal_list_contamination(tmp_path):
    """If CONTAMINATED-* appears in refusal rules, lint fails (R-L3-2-E guard)."""
    formatter = REPO_ROOT / "academic-paper/agents/formatter_agent.md"
    content = formatter.read_text()
    # Inject a fake refusal rule containing CONTAMINATED-TRIANGULATION-UNMATCHED.
    # Use the unique first-refusal-rule text as anchor so we land inside
    # the refusal rules list, not in Core Principles (which also has "1. ").
    broken_content = content.replace(
        "1. A literal `[UNVERIFIED CITATION",
        "1. A literal `CONTAMINATED-TRIANGULATION-UNMATCHED` marker.\n1. A literal `[UNVERIFIED CITATION",
        1,
    )
    broken = tmp_path / "formatter_agent.md"
    broken.write_text(broken_content)
    result = run_lint(["--formatter-path", str(broken)])
    assert result.returncode == 1
    assert "refusal" in result.stderr.lower()


def test_lint_substring_collision_not_false_positive():
    """CONTAMINATED-PREPRINT inside CONTAMINATED-PREPRINT+... not double-counted.

    With set-equality extraction, the 9-token set is unambiguous.
    """
    result = run_lint()
    assert result.returncode == 0
