"""Tests for the public-repo boundary lint."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent / "check_public_repo_boundary.py"
spec = importlib.util.spec_from_file_location("boundary_lint", SCRIPT_PATH)
boundary_lint = importlib.util.module_from_spec(spec)
sys.modules["boundary_lint"] = boundary_lint
spec.loader.exec_module(boundary_lint)
scan_file = boundary_lint.scan_file


def write(tmp_path: Path, content: str, name: str = "test.md") -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# --- Should be flagged (true leakage) ---------------------------------

def test_heeact_springer_co_occurrence_flagged(tmp_path):
    p = write(
        tmp_path,
        "The HEEACT Springer chapter session produced 53 entries.",
    )
    violations = scan_file(p)
    assert any("HEEACT + Springer" in v for v in violations)


def test_springer_then_heeact_also_flagged(tmp_path):
    p = write(
        tmp_path,
        "Submitting to a Springer Nature handbook, the HEEACT case study revealed...",
    )
    violations = scan_file(p)
    assert any("HEEACT + Springer" in v for v in violations)


def test_heeact_chapter_session_flagged(tmp_path):
    p = write(
        tmp_path,
        "Replayed on the 2026-04-30 HEEACT chapter session corpus.",
    )
    violations = scan_file(p)
    assert any("chapter/session" in v or "Springer" in v for v in violations)


def test_hei_platform_flagged(tmp_path):
    p = write(
        tmp_path,
        "Downstream `hei-platform` SCR Loop tracking stays separate.",
    )
    violations = scan_file(p)
    assert any("hei-platform" in v for v in violations)


def test_internal_path_with_heeact_flagged(tmp_path):
    p = write(
        tmp_path,
        "Output at `chapter/literature_review/B_heeact_documents/registry.md`.",
    )
    violations = scan_file(p)
    assert any("Internal directory path" in v for v in violations)


def test_b_heeact_handbook_registry_flagged(tmp_path):
    p = write(
        tmp_path,
        "The B_HEEACT_HANDBOOK_QUOTE_REGISTRY indexes verified quotes.",
    )
    violations = scan_file(p)
    assert any("Internal directory" in v for v in violations)


# --- Should NOT be flagged (legitimate public-knowledge use) ----------

def test_heeact_alone_as_institution_name_passes(tmp_path):
    """HEEACT as Taiwan QA institution introduction is generic knowledge."""
    p = write(
        tmp_path,
        "HEEACT (Higher Education Evaluation and Accreditation Council of Taiwan) "
        "administers institutional accreditation since 2005.",
    )
    assert scan_file(p) == []


def test_springer_alone_as_publisher_passes(tmp_path):
    """Springer as a publisher name in citation guides is generic."""
    p = write(
        tmp_path,
        "*Higher Education* | Springer | Q1; values contextual description.",
    )
    assert scan_file(p) == []


def test_heeact_in_apa_citation_example_passes(tmp_path):
    """APA citation example using HEEACT as the cited institution."""
    p = write(
        tmp_path,
        "First mention: Higher Education Evaluation and Accreditation "
        "Council of Taiwan [HEEACT] (2024). Subsequent: HEEACT (2024).",
    )
    assert scan_file(p) == []


def test_maintainer_attribution_line_passes(tmp_path):
    """CONTRIBUTING.md maintainer line is on the allowlist."""
    p = write(
        tmp_path,
        "The repo is maintained by [Cheng-I Wu](https://github.com/Imbad0202) (HEEACT).",
    )
    assert scan_file(p) == []


def test_boundary_teaching_procedure_passes(tmp_path):
    """A procedure step that TEACHES the boundary rule itself."""
    p = write(
        tmp_path,
        "17. Open PR. Manual pre-merge check: no hei-platform content, "
        "no personal data, no school names.",
    )
    assert scan_file(p) == []


def test_grep_pattern_teaching_passes(tmp_path):
    """A grep pattern that teaches boundary scanning."""
    p = write(
        tmp_path,
        'grep -iE "(?:10|172|192)\\.[0-9]+\\.[0-9]+\\.[0-9]+|\\.local|hei-platform|ISMS-P" '
        "/tmp/v3.5.1-full.diff",
    )
    assert scan_file(p) == []


def test_higher_education_general_passes(tmp_path):
    """Generic 'higher education' terminology must not trip."""
    p = write(
        tmp_path,
        "## Higher Education Quality Assurance\n"
        "QA practices across higher education institutions...",
    )
    assert scan_file(p) == []


def test_hei_abbreviation_alone_passes(tmp_path):
    """HEI as a generic abbreviation (Higher Education Institution) is fine."""
    p = write(
        tmp_path,
        "Most HEIs adopt outcome-based assessment under the third cycle.",
    )
    assert scan_file(p) == []
