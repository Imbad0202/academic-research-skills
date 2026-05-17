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


# ---------------------------------------------------------------------------
# Rule 1 — marker syntax
# ---------------------------------------------------------------------------

def test_rule1_all_markers_present_in_real_repo():
    """Rule 1: real orchestrator has all 3 new v3.9.0 markers in subsection."""
    result = run_lint()
    assert result.returncode == 0


def test_rule1_missing_marker_fails(tmp_path):
    """Rule 1: remove CONTAMINATED-PARTIAL-UNMATCH from orchestrator subsection — lint fails."""
    orch = REPO_ROOT / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    content = orch.read_text()
    broken = content.replace("`CONTAMINATED-PARTIAL-UNMATCH`", "`CONTAMINATED-XXX-PARTIAL`")
    p = tmp_path / "orch.md"
    p.write_text(broken)
    result = run_lint(["--orchestrator-path", str(p)])
    assert result.returncode == 1
    assert "rule 1" in result.stderr.lower() or "marker" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Rule 2 — preprint composition order
# ---------------------------------------------------------------------------

def test_rule2_preprint_order_correct_in_real_repo():
    """Rule 2: real orchestrator has all PREPRINT compositions with PREPRINT first."""
    result = run_lint()
    assert result.returncode == 0


def test_rule2_preprint_order_violated_fails(tmp_path):
    """Rule 2: inject CONTAMINATED-COVERAGE-NOISE+PREPRINT into orchestrator — lint fails."""
    orch = REPO_ROOT / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    content = orch.read_text()
    broken = content.replace(
        "## Cite-Time Provenance Finalizer — v3.9.0 extension",
        "## Cite-Time Provenance Finalizer — v3.9.0 extension\n\nFAKE: `CONTAMINATED-COVERAGE-NOISE+PREPRINT` violates order.\n",
        1,
    )
    p = tmp_path / "orch.md"
    p.write_text(broken)
    result = run_lint(["--orchestrator-path", str(p)])
    assert result.returncode == 1
    assert "rule 2" in result.stderr.lower() or "preprint" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Rule 3 — v3.7.3 legacy compat
# ---------------------------------------------------------------------------

def test_rule3_legacy_compat_preserved_in_real_repo():
    """Rule 3: real orchestrator's k=1 k_max=1 S2 row produces CONTAMINATED-UNMATCHED."""
    result = run_lint()
    assert result.returncode == 0


def test_rule3_legacy_compat_violated_fails(tmp_path):
    """Rule 3: change the legacy row's suffix to COVERAGE-NOISE — lint fails."""
    orch = REPO_ROOT / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    content = orch.read_text()
    broken = content.replace(
        "| `semantic_scholar_unmatched` | `CONTAMINATED-UNMATCHED` (v3.7.3 legacy)",
        "| `semantic_scholar_unmatched` | `CONTAMINATED-COVERAGE-NOISE` (BROKEN)",
        1,
    )
    p = tmp_path / "orch.md"
    p.write_text(broken)
    result = run_lint(["--orchestrator-path", str(p)])
    assert result.returncode == 1
    assert "rule 3" in result.stderr.lower() or "legacy" in result.stderr.lower()


def test_rule3_preprint_legacy_drift_fails(tmp_path):
    """Rule 3: drift preprint legacy row's suffix to CONTAMINATED-PREPRINT+COVERAGE-NOISE — lint fails."""
    orch = REPO_ROOT / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    content = orch.read_text()
    broken = content.replace(
        "`CONTAMINATED-PREPRINT+UNMATCHED` (v3.7.3 legacy)",
        "`CONTAMINATED-PREPRINT+COVERAGE-NOISE` (BROKEN)",
        1,
    )
    p = tmp_path / "orch.md"
    p.write_text(broken)
    result = run_lint(["--orchestrator-path", str(p)])
    assert result.returncode == 1
    assert "rule 3" in result.stderr.lower() or "preprint" in result.stderr.lower()


def test_rule3_missing_legacy_rows_fails(tmp_path):
    """Rule 3: delete BOTH legacy S2 rows from the table — lint must fail."""
    orch = REPO_ROOT / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    content = orch.read_text()
    # Delete the bare legacy row.
    broken = content.replace(
        "| `ok` / `LOW-WARN` | false / absent | 1 | 1 | `semantic_scholar_unmatched` | `CONTAMINATED-UNMATCHED` (v3.7.3 legacy) |\n",
        "",
        1,
    )
    # Delete the preprint legacy row.
    broken = broken.replace(
        "| `ok` / `LOW-WARN` | true | 1 | 1 | `semantic_scholar_unmatched` | `CONTAMINATED-PREPRINT+UNMATCHED` (v3.7.3 legacy) |\n",
        "",
        1,
    )
    p = tmp_path / "orch.md"
    p.write_text(broken)
    result = run_lint(["--orchestrator-path", str(p)])
    assert result.returncode == 1
    # Both row-missing messages should fire.
    err = result.stderr.lower()
    assert "missing" in err
    assert "rule 3" in err


# ---------------------------------------------------------------------------
# Rule 4 — no *-BLOCK in v3.9.0 subsection
# ---------------------------------------------------------------------------

def test_rule4_no_block_tokens_in_real_repo():
    """Rule 4: real orchestrator's v3.9.0 subsection has no backtick-quoted *-BLOCK tokens."""
    result = run_lint()
    assert result.returncode == 0


def test_rule4_high_block_injection_fails(tmp_path):
    """Rule 4: inject `CONTAMINATED-HIGH-BLOCK` into v3.9.0 subsection — lint fails."""
    orch = REPO_ROOT / "academic-pipeline/agents/pipeline_orchestrator_agent.md"
    content = orch.read_text()
    broken = content.replace(
        "## Cite-Time Provenance Finalizer — v3.9.0 extension",
        "## Cite-Time Provenance Finalizer — v3.9.0 extension\n\nFAKE: `CONTAMINATED-HIGH-BLOCK` policy-layer marker.\n",
        1,
    )
    p = tmp_path / "orch.md"
    p.write_text(broken)
    result = run_lint(["--orchestrator-path", str(p)])
    assert result.returncode == 1
    assert "rule 4" in result.stderr.lower() or "block" in result.stderr.lower()


# ---------------------------------------------------------------------------
# Invocation error handling
# ---------------------------------------------------------------------------

def test_orchestrator_path_missing_returns_2(tmp_path):
    """Missing orchestrator file → exit 2 (invocation error)."""
    result = run_lint(["--orchestrator-path", str(tmp_path / "nonexistent.md")])
    assert result.returncode == 2


def test_formatter_path_missing_returns_2(tmp_path):
    """Missing formatter file → exit 2 (invocation error)."""
    result = run_lint(["--formatter-path", str(tmp_path / "nonexistent.md")])
    assert result.returncode == 2
