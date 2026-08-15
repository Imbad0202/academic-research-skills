"""Compatibility tests for the retired rubric-weight checker filename."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from tests.test_helpers import run_script


SCRIPT = Path(__file__).resolve().parent / "check_rubric_weight_consistency.py"
REPO_ROOT = SCRIPT.parent.parent


def _run(root: Path) -> subprocess.CompletedProcess:
    return run_script(SCRIPT, "--root", str(root))


class TestRubricWeightCompatibility(unittest.TestCase):
    def test_real_repo_routes_to_honesty_guard(self) -> None:
        result = _run(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("retired", result.stdout)
        self.assertIn("honesty OK", result.stdout)

    def test_missing_tree_fails_loud(self) -> None:
        result = _run(Path("/definitely/not/a/repository"))
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
