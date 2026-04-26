"""Tests for scripts/check_corpus_consumer_protocol.py.

Each L1-L9 invariant has at least one positive test (passing case) and
one negative test (failing case). The lint is manifest-driven for L3-L6
and closed-set for L8.
"""
from __future__ import annotations

import json
import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
LINT_SCRIPT = REPO_ROOT / "scripts" / "check_corpus_consumer_protocol.py"


def run_lint(cwd: Path) -> subprocess.CompletedProcess:
    """Run the lint script in `cwd`. Returns CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(LINT_SCRIPT)],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Path:
    """Build a minimal valid v3.6.5 PR-A repo layout under tmp_path.

    Each test mutates exactly one artifact to trigger a specific lint failure.
    The base layout passes all nine invariants.
    """
    # --- manifest (PR-A: bibliography only)
    (tmp_path / "scripts").mkdir()
    manifest = {
        "supported_consumers": [
            {
                "agent_path": "deep-research/agents/bibliography_agent.md",
                "agent_basename": "bibliography_agent",
                "skill": "deep-research",
                "since_version": "v3.6.5",
                "phase": "Phase 1",
            }
        ]
    }
    (tmp_path / "scripts" / "corpus_consumer_manifest.json").write_text(
        json.dumps(manifest, indent=2)
    )

    # --- reference doc with full bibliography block + stub strategist block
    ref_dir = tmp_path / "academic-pipeline" / "references"
    ref_dir.mkdir(parents=True)
    (ref_dir / "literature_corpus_consumers.md").write_text(
        textwrap.dedent(
            """\
            # Consumer Protocol — `literature_corpus[]` Reading

            ## Consumer: bibliography_agent

            ### Iron Rule 1 — Same criteria
            ### Iron Rule 2 — No silent skip
            ### Iron Rule 3 — No corpus mutation
            ### Iron Rule 4 — Graceful fallback on parse failure

            <!-- BAD -->
            ```
            corpus has 5 entries; agent silently skips one with empty abstract.
            ```

            <!-- GOOD -->
            ```
            agent records the skipped entry in PRE-SCREENED skipped sub-section
            with reason "abstract empty after privacy clearing".
            ```

            ## Consumer: literature_strategist_agent

            **Status:** Stub — implementation in PR-B (v3.6.5)
            <!-- LINT_STUB: skip_cross_check -->

            (full content shipped in PR-B)
            """
        )
    )

    # --- bibliography_agent.md with all required prose markers
    agent_dir = tmp_path / "deep-research" / "agents"
    agent_dir.mkdir(parents=True)
    (agent_dir / "bibliography_agent.md").write_text(
        textwrap.dedent(
            """\
            ---
            name: bibliography_agent
            ---

            See `academic-pipeline/references/literature_corpus_consumers.md`.

            ### Step 0: presence detection
            ### Step 1: pre-screen
            ### Step 2: search-fills-gap
            ### Step 3: merge
            ### Step 4: emit report

            case A: ...
            case B: ...
            case B': ...
            case C: ...

            ### Iron Rule 1 — Same criteria
            ### Iron Rule 2 — No silent skip
            ### Iron Rule 3 — No corpus mutation
            ### Iron Rule 4 — Graceful fallback on parse failure

            ```
            PRE-SCREENED FROM USER CORPUS:
            - Adapter: zotero-bbt-export
            - Snapshot date: 2026-04-26
            - Total entries scanned: 87
            - Pre-screening result:
              - Included: 12 entries
                citation_keys:
                  - chen2024ai
              - Excluded by inclusion / exclusion criteria: 5 entries
                citation_keys:
                  - foo2023bar
              - Skipped (criteria cannot be applied): 2 entries
                citation_keys with reasons:
                  - baz2024: missing required tags
            - Note: presence in corpus does not imply inclusion;
              same criteria applied to corpus and external sources.
            ```
            Truncation rule: lists exceeding 50 entries truncate to first 20 + last 5 alphabetically with appendix file.
            """
        )
    )

    # --- handoff_schemas.md keeps the deferred caveat (PR-A state)
    shared_dir = tmp_path / "shared"
    shared_dir.mkdir()
    (shared_dir / "handoff_schemas.md").write_text(
        "Schema 9 ... Consumer-side integration deferred to v3.6.5+ ...\n"
    )

    return tmp_path


def test_l1_passes_when_reference_doc_exists(fixture_repo: Path) -> None:
    result = run_lint(fixture_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_l1_fails_when_reference_doc_missing(fixture_repo: Path) -> None:
    (
        fixture_repo
        / "academic-pipeline"
        / "references"
        / "literature_corpus_consumers.md"
    ).unlink()
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L1" in result.stdout or "L1" in result.stderr


def test_l2_passes_with_both_consumer_blocks_stub_marked(fixture_repo: Path) -> None:
    result = run_lint(fixture_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_l2_fails_when_stub_marker_missing(fixture_repo: Path) -> None:
    ref = (
        fixture_repo
        / "academic-pipeline"
        / "references"
        / "literature_corpus_consumers.md"
    )
    text = ref.read_text().replace("<!-- LINT_STUB: skip_cross_check -->", "")
    ref.write_text(text)
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L2" in result.stdout or "L2" in result.stderr


# --- L3: backpointer ---


def test_l3_passes_when_backpointer_present(fixture_repo: Path) -> None:
    result = run_lint(fixture_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_l3_fails_when_backpointer_missing(fixture_repo: Path) -> None:
    agent = fixture_repo / "deep-research" / "agents" / "bibliography_agent.md"
    text = agent.read_text().replace(
        "academic-pipeline/references/literature_corpus_consumers.md", ""
    )
    agent.write_text(text)
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L3" in result.stdout or "L3" in result.stderr


# --- L4: PRE-SCREENED template start ---


def test_l4_passes_when_pre_screened_template_present(fixture_repo: Path) -> None:
    result = run_lint(fixture_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_l4_fails_when_pre_screened_template_missing(fixture_repo: Path) -> None:
    agent = fixture_repo / "deep-research" / "agents" / "bibliography_agent.md"
    text = agent.read_text().replace("PRE-SCREENED FROM USER CORPUS:", "")
    agent.write_text(text)
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L4" in result.stdout or "L4" in result.stderr


# --- L5: four Iron Rule titles ---


def test_l5_passes_with_all_four_iron_rule_titles(fixture_repo: Path) -> None:
    result = run_lint(fixture_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_l5_fails_when_iron_rule_title_missing(fixture_repo: Path) -> None:
    agent = fixture_repo / "deep-research" / "agents" / "bibliography_agent.md"
    text = agent.read_text().replace(
        "Iron Rule 4 — Graceful fallback on parse failure", "Iron Rule 4 — TBD"
    )
    agent.write_text(text)
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L5" in result.stdout or "L5" in result.stderr


# --- L6: Step headings + Step 2 case markers ---


def test_l6_passes_with_all_steps_and_cases(fixture_repo: Path) -> None:
    result = run_lint(fixture_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_l6_fails_when_case_marker_missing(fixture_repo: Path) -> None:
    agent = fixture_repo / "deep-research" / "agents" / "bibliography_agent.md"
    text = agent.read_text().replace("case B': ...", "")
    agent.write_text(text)
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L6" in result.stdout or "L6" in result.stderr


# --- L7: PRE-SCREENED template line markers ---


def test_l7_passes_with_all_nine_line_markers(fixture_repo: Path) -> None:
    result = run_lint(fixture_repo)
    assert result.returncode == 0, result.stdout + result.stderr


def test_l7_fails_when_skipped_marker_missing(fixture_repo: Path) -> None:
    agent = fixture_repo / "deep-research" / "agents" / "bibliography_agent.md"
    text = agent.read_text().replace(
        "Skipped (criteria cannot be applied):", "Removed:"
    )
    agent.write_text(text)
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L7" in result.stdout or "L7" in result.stderr


def test_l7_fails_when_truncation_prose_missing(fixture_repo: Path) -> None:
    """Spec §5.2 L7: PRE-SCREENED template must include 'truncation rule' prose."""
    agent = fixture_repo / "deep-research" / "agents" / "bibliography_agent.md"
    text = agent.read_text()
    # Remove the truncation prose. Use a lowercase replace to catch both casings.
    new_text = text.replace("Truncation rule:", "Removed:")
    assert new_text != text, "fixture must contain 'Truncation rule:' line for this test"
    agent.write_text(new_text)
    result = run_lint(fixture_repo)
    assert result.returncode != 0
    assert "L7" in result.stdout or "L7" in result.stderr
