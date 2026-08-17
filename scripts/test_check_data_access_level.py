"""Unit + mutation tests for check_data_access_level.py.

Two layers, matching the lint's shape after the #756 single-pass rewrite:
- CLI-level tests (subprocess via `--path`, preserving the stdout-not-stderr
  reporting contract for frontmatter failures);
- in-process mutation tests for the EXPECTED_LEVELS pin layer.

Since #756 the pin layer runs on every skill, so scenarios that probe field
handling use REGISTERED skill names (an arbitrary synthetic skill correctly
fails as unregistered before its field is examined).
"""
import shutil
import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from tests.test_helpers import run_skill_linter, write_skill as _write_skill

from check_data_access_level import EXPECTED_LEVELS, run_all_checks

SCRIPT = Path(__file__).resolve().parent / "check_data_access_level.py"
REPO_ROOT = Path(__file__).resolve().parent.parent


def _run(root: Path) -> subprocess.CompletedProcess:
    return run_skill_linter(SCRIPT, root)


def _write_registered_fleet(root: Path) -> None:
    """All four registered skills at their pinned levels."""
    for name, level in EXPECTED_LEVELS.items():
        _write_skill(
            root,
            name,
            textwrap.dedent(
                f"""\
                name: {name}
                description: "test"
                metadata:
                  version: "1.0"
                  status: active
                  data_access_level: {level}
                """
            ),
        )


class TestLintScript(unittest.TestCase):
    def test_missing_field_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registered_fleet(root)
            _write_skill(
                root,
                "deep-research",
                textwrap.dedent(
                    """\
                    name: deep-research
                    description: "test"
                    metadata:
                      version: "1.0"
                      status: active
                    """
                ),
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("data_access_level", result.stdout + result.stderr)

    def test_invalid_value_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registered_fleet(root)
            _write_skill(
                root,
                "deep-research",
                textwrap.dedent(
                    """\
                    name: deep-research
                    description: "test"
                    metadata:
                      version: "1.0"
                      status: active
                      data_access_level: public
                    """
                ),
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("public", result.stdout + result.stderr)

    def test_valid_value_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registered_fleet(root)
            result = _run(root)
            self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_non_mapping_metadata_reports_violation(self) -> None:
        # codex R1: `metadata: active` is valid YAML but not a mapping — the
        # pin layer must report it as a violation, not crash.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_registered_fleet(root)
            _write_skill(
                root,
                "deep-research",
                "name: deep-research\nmetadata: active\n",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("metadata must be a mapping/object", result.stdout)

    def test_malformed_yaml_reports_on_stdout(self) -> None:
        """FrontmatterError detail must appear on stdout, not only stderr."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "bad-skill"
            skill_dir.mkdir()
            # Deliberately invalid YAML: tab character where spaces are required
            (skill_dir / "SKILL.md").write_text(
                "---\nkey: valid\n\tbad_indent: boom\n---\n\n# bad-skill\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            # The yaml.YAMLError detail must be on stdout so CI stdout-only
            # capture preserves the root cause.
            self.assertIn("malformed YAML frontmatter", result.stdout)
            # Nothing about this error should leak only to stderr.
            self.assertNotIn("malformed YAML frontmatter", result.stderr)

    def test_missing_closing_fence_reports_on_stdout(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "bad-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: broken\nmetadata:\n  data_access_level: raw\n# missing closing fence\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing closing YAML frontmatter fence", result.stdout)
            self.assertNotIn("missing closing YAML frontmatter fence", result.stderr)

    def test_non_mapping_frontmatter_reports_on_stdout(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "bad-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\n- just\n- a\n- list\n---\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must be a mapping/object", result.stdout)
            self.assertNotIn("must be a mapping/object", result.stderr)


# --- #756 EXPECTED_LEVELS pin layer (in-process mutation tests) ---


@pytest.fixture()
def fixture_repo(tmp_path: Path) -> Path:
    _write_registered_fleet(tmp_path)
    return tmp_path


def test_real_tree_passes() -> None:
    assert run_all_checks(REPO_ROOT) == []


def test_pipeline_reverting_to_verified_only_fires(fixture_repo: Path) -> None:
    # The #756 regression itself: silently flipping the pipeline back to
    # verified_only must fail against the pin.
    _write_skill(
        fixture_repo,
        "academic-pipeline",
        "name: academic-pipeline\nmetadata:\n"
        "  data_access_level: verified_only\n  status: active\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any(
        "academic-pipeline" in e and "pinned value is 'raw'" in e
        for e in errors
    )


def test_unregistered_new_skill_fires(fixture_repo: Path) -> None:
    _write_skill(
        fixture_repo,
        "brand-new-skill",
        "name: brand-new-skill\nmetadata:\n"
        "  data_access_level: raw\n  status: active\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any(
        "brand-new-skill" in e and "not registered" in e for e in errors
    )


def test_pin_without_skill_dir_fires(fixture_repo: Path) -> None:
    shutil.rmtree(fixture_repo / "deep-research")
    errors = run_all_checks(fixture_repo)
    assert any(
        "deep-research" in e and "no top-level" in e for e in errors
    )


def test_one_violation_per_problem(fixture_repo: Path) -> None:
    # The single-pass rewrite exists so one broken skill yields ONE row, not
    # a vocabulary row plus a pin row.
    _write_skill(
        fixture_repo,
        "academic-pipeline",
        "name: academic-pipeline\nmetadata:\n"
        "  data_access_level: public\n  status: active\n",
    )
    errors = run_all_checks(fixture_repo)
    assert len(errors) == 1
    assert "public" in errors[0]
