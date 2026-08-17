"""Mutation tests for check_data_access_level.py (#756).

The vocabulary check predates #756; these tests pin the new layer — the
per-skill EXPECTED_LEVELS map enforcing the dirtiest-input rule — plus the
real tree as baseline.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from check_data_access_level import EXPECTED_LEVELS, run_all_checks

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write_skill(root: Path, name: str, level: str | None) -> None:
    skill = root / name / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    field = f"  data_access_level: {level}\n" if level is not None else ""
    skill.write_text(
        f"---\nname: {name}\nmetadata:\n{field}  status: active\n---\n\n# {name}\n",
        encoding="utf-8",
    )


@pytest.fixture()
def fixture_repo(tmp_path: Path) -> Path:
    for name, level in EXPECTED_LEVELS.items():
        _write_skill(tmp_path, name, level)
    return tmp_path


def test_real_tree_passes() -> None:
    assert run_all_checks(REPO_ROOT) == []


def test_fixture_baseline_passes(fixture_repo: Path) -> None:
    assert run_all_checks(fixture_repo) == []


def test_pipeline_reverting_to_verified_only_fires(fixture_repo: Path) -> None:
    # The #756 regression itself: silently flipping the pipeline back to
    # verified_only must fail against the pin.
    _write_skill(fixture_repo, "academic-pipeline", "verified_only")
    errors = run_all_checks(fixture_repo)
    assert any(
        "academic-pipeline" in e and "pinned value is 'raw'" in e
        for e in errors
    )


def test_unregistered_new_skill_fires(fixture_repo: Path) -> None:
    _write_skill(fixture_repo, "brand-new-skill", "raw")
    errors = run_all_checks(fixture_repo)
    assert any(
        "brand-new-skill" in e and "not registered" in e for e in errors
    )


def test_pin_without_skill_dir_fires(fixture_repo: Path) -> None:
    import shutil

    shutil.rmtree(fixture_repo / "deep-research")
    errors = run_all_checks(fixture_repo)
    assert any(
        "deep-research" in e and "no top-level" in e for e in errors
    )


def test_invalid_vocabulary_fires(fixture_repo: Path) -> None:
    _write_skill(fixture_repo, "deep-research", "unverified")
    errors = run_all_checks(fixture_repo)
    assert any("deep-research" in e for e in errors)


def test_missing_field_fires(fixture_repo: Path) -> None:
    _write_skill(fixture_repo, "academic-paper", None)
    errors = run_all_checks(fixture_repo)
    assert any("academic-paper" in e for e in errors)
