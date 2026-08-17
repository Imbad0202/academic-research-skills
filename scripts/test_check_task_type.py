# scripts/test_check_task_type.py
"""Unit tests for check_task_type.py lint script."""
import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.test_helpers import run_skill_linter, write_skill as _write_skill

SCRIPT = Path(__file__).resolve().parent / "check_task_type.py"


def _run(root: Path) -> subprocess.CompletedProcess:
    return run_skill_linter(SCRIPT, root)


class TestTaskTypeLint(unittest.TestCase):
    def test_missing_field_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(
                root, "example",
                textwrap.dedent("""\
                    name: example
                    description: "test"
                    metadata:
                      version: "1.0"
                      status: active
                    """),
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("task_type", result.stdout + result.stderr)

    def test_invalid_value_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_skill(
                root, "example",
                textwrap.dedent("""\
                    name: example
                    description: "test"
                    metadata:
                      version: "1.0"
                      status: active
                      task_type: experimental
                    """),
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("experimental", result.stdout + result.stderr)

    def test_valid_value_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, value in [("a", "open-ended"), ("b", "outcome-gradable")]:
                _write_skill(
                    root, name,
                    textwrap.dedent(f"""\
                        name: {name}
                        description: "test"
                        metadata:
                          version: "1.0"
                          status: active
                          task_type: {value}
                        """),
                )
            result = _run(root)
            self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_malformed_yaml_reports_on_stdout(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "broken"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: broken\nmetadata:\n\tversion: \"1.0\"\n---\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("malformed YAML frontmatter", result.stdout)
            self.assertNotIn("malformed YAML frontmatter", result.stderr)

    def test_missing_closing_fence_reports_on_stdout(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "broken"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\nname: broken\nmetadata:\n  task_type: open-ended\n# missing closing fence\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing closing YAML frontmatter fence", result.stdout)
            self.assertNotIn("missing closing YAML frontmatter fence", result.stderr)

    def test_non_mapping_frontmatter_reports_on_stdout(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = root / "broken"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                "---\n- just\n- a\n- list\n---\n",
                encoding="utf-8",
            )
            result = _run(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("must be a mapping/object", result.stdout)
            self.assertNotIn("must be a mapping/object", result.stderr)


if __name__ == "__main__":
    unittest.main()
