"""Mutation tests for check_command_frontmatter_name.py (#633).

Each test builds a synthetic repo root under a TemporaryDirectory and runs
the lint as a subprocess, mirroring CI invocation. The mutations cover every
violation class the lint claims to catch, so a silently weakened check fails
here before it fails in the field.
"""
from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.test_helpers import run_script


LINT = Path(__file__).parent / "check_command_frontmatter_name.py"
REPO_ROOT = Path(__file__).parent.parent


def make_command(root: Path, stem: str, frontmatter: str) -> Path:
    cmd_dir = root / "commands"
    cmd_dir.mkdir(exist_ok=True)
    path = cmd_dir / f"{stem}.md"
    path.write_text(frontmatter, encoding="utf-8")
    return path


GOOD = "---\nname: {stem}\ndescription: x\nmodel: sonnet\n---\n\nBody.\n"


class RealRepoTest(unittest.TestCase):
    def test_real_repo_passes(self) -> None:
        result = run_script(LINT, "--repo-root", str(REPO_ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("OK", result.stdout)


class MutationTest(unittest.TestCase):
    def run_lint(self, root: Path):
        return run_script(LINT, "--repo-root", str(root))

    def test_all_good_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(root, "ars-full", GOOD.format(stem="ars-full"))
            make_command(root, "ars-plan", GOOD.format(stem="ars-plan"))
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("2 command files", result.stdout)

    def test_missing_name_key_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(root, "ars-full", "---\ndescription: x\n---\nBody.\n")
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no `name:` key", result.stdout)

    def test_mismatched_name_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(root, "ars-full", GOOD.format(stem="ars-fill"))
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("!= filename stem", result.stdout)

    def test_homoglyph_name_fails(self) -> None:
        # Cyrillic 'а' (U+0430) in place of ASCII 'a': byte-equality rejects it.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(
                root, "ars-plan", "---\nname: аrs-plan\n---\nBody.\n"
            )
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("!= filename stem", result.stdout)

    def test_duplicate_name_keys_fail(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(
                root,
                "ars-full",
                "---\nname: ars-full\nname: ars-other\n---\nBody.\n",
            )
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("name-like keys", result.stdout)

    def test_yaml_equivalent_quoted_duplicate_fails(self) -> None:
        # codex P2 (PR #635): a YAML loader resolves `"name":` to the same
        # key, so a later quoted duplicate would override the canonical value.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(
                root,
                "ars-full",
                '---\nname: ars-full\n"name": ars-other\n---\nBody.\n',
            )
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("name-like keys", result.stdout)

    def test_yaml_equivalent_spaced_colon_duplicate_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(
                root,
                "ars-full",
                "---\nname: ars-full\nname : ars-other\n---\nBody.\n",
            )
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("name-like keys", result.stdout)

    def test_non_canonical_sole_spelling_fails(self) -> None:
        # A single quoted key is semantically valid YAML but not the
        # canonical spelling; the lint accepts exactly `name: <stem>`.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(
                root, "ars-full", '---\n"name": ars-full\n---\nBody.\n'
            )
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("non-canonical name key spelling", result.stdout)

    def test_quoted_value_fails(self) -> None:
        # `name: "ars-full"` resolves to ars-full in YAML but is not the
        # canonical byte form; fail closed rather than interpret quoting.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(
                root, "ars-full", '---\nname: "ars-full"\n---\nBody.\n'
            )
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("!= filename stem", result.stdout)

    def test_missing_frontmatter_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(root, "ars-full", "No frontmatter here.\n")
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("missing frontmatter", result.stdout)

    def test_unterminated_frontmatter_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(root, "ars-full", "---\nname: ars-full\nBody.\n")
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unterminated frontmatter", result.stdout)

    def test_name_in_body_does_not_satisfy(self) -> None:
        # `name:` after the closing '---' is body text, not frontmatter.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_command(
                root,
                "ars-full",
                "---\ndescription: x\n---\nname: ars-full\n",
            )
            result = self.run_lint(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("no `name:` key", result.stdout)

    def test_empty_inventory_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            result = self.run_lint(Path(tmp))
            self.assertEqual(result.returncode, 1)
            self.assertIn("no files matched", result.stdout)


if __name__ == "__main__":
    unittest.main()
