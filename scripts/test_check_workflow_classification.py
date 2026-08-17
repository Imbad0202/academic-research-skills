"""Mutation tests for check_workflow_classification.py (#755)."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from check_workflow_classification import (
    DOC_RELPATH,
    WORKFLOWS_DIR,
    run_all_checks,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """Real doc + real workflow inventory, copied so mutations are isolated."""
    dst_doc = tmp_path / DOC_RELPATH
    dst_doc.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(REPO_ROOT / DOC_RELPATH, dst_doc)
    (tmp_path / WORKFLOWS_DIR).mkdir(parents=True, exist_ok=True)
    for wf in sorted((REPO_ROOT / WORKFLOWS_DIR).glob("*.yml")):
        shutil.copyfile(wf, tmp_path / WORKFLOWS_DIR / wf.name)
    return tmp_path


def _mutate_doc(root: Path, old: str, new: str) -> None:
    doc = root / DOC_RELPATH
    text = doc.read_text(encoding="utf-8")
    assert old in text, f"mutation anchor not found: {old!r}"
    doc.write_text(text.replace(old, new), encoding="utf-8")


def test_real_tree_passes() -> None:
    assert run_all_checks(REPO_ROOT) == []


def test_fixture_baseline_passes(repo: Path) -> None:
    assert run_all_checks(repo) == []


def test_missing_doc_is_single_fatal_error(repo: Path) -> None:
    (repo / DOC_RELPATH).unlink()
    errors = run_all_checks(repo)
    assert len(errors) == 1
    assert "missing" in errors[0]


def test_missing_section_fires(repo: Path) -> None:
    _mutate_doc(
        repo,
        "### 7.1 CI workflow enforcement classes",
        "### 7.1 CI workflow something else",
    )
    errors = run_all_checks(repo)
    assert any("WC-1" in e and "not found" in e for e in errors)


def test_new_workflow_without_row_fires(repo: Path) -> None:
    (repo / WORKFLOWS_DIR / "brand-new-check.yml").write_text(
        "name: Brand New\non:\n  push:\n", encoding="utf-8"
    )
    errors = run_all_checks(repo)
    assert any(
        "WC-1" in e and "brand-new-check.yml" in e and "no row" in e
        for e in errors
    )


def test_row_for_removed_workflow_fires(repo: Path) -> None:
    (repo / WORKFLOWS_DIR / "freshness-check.yml").unlink()
    errors = run_all_checks(repo)
    assert any(
        "WC-1" in e and "freshness-check.yml" in e and "names no file" in e
        for e in errors
    )


def test_duplicate_row_fires(repo: Path) -> None:
    doc = repo / DOC_RELPATH
    lines = doc.read_text(encoding="utf-8").split("\n")
    idx = next(
        i for i, line in enumerate(lines) if line.startswith("| `pytest.yml`")
    )
    lines.insert(idx, lines[idx])
    doc.write_text("\n".join(lines), encoding="utf-8")
    errors = run_all_checks(repo)
    assert any(
        "pytest.yml" in e and "more than one table row" in e for e in errors
    )


def test_off_vocabulary_class_fires(repo: Path) -> None:
    _mutate_doc(repo, "| Administrative |", "| Mandatory |")
    errors = run_all_checks(repo)
    assert any(
        "WC-2" in e and "Mandatory" in e for e in errors
    )


def test_class_with_qualifier_still_passes(repo: Path) -> None:
    # Qualified cells like "Blocking when triggered" are in-vocabulary by
    # prefix; the baseline table already contains them — pin that explicitly.
    _mutate_doc(
        repo,
        "| Administrative |",
        "| Administrative (opens an issue) |",
    )
    assert run_all_checks(repo) == []
