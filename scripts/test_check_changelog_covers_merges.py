"""Unit tests for check_changelog_covers_merges.py."""
from __future__ import annotations

import subprocess
import textwrap
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from tests.test_helpers import run_script

SCRIPT = Path(__file__).resolve().parent / "check_changelog_covers_merges.py"
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_changelog_covers_merges import (  # noqa: E402
    pr_number,
)


class PrNumberTest(unittest.TestCase):
    def test_trailing_pr_is_identity(self):
        self.assertEqual(pr_number("Harden title-fallback (#432)"), 432)

    def test_mid_subject_ref_ignored_when_trailing_present(self):
        # #89 is a tracking issue mid-subject; #429 is the PR (trailing).
        self.assertEqual(
            pr_number("route integrity-FAIL (#89 Item 8) (#429)"), 429
        )

    def test_no_trailing_pr_returns_none(self):
        self.assertIsNone(pr_number("Harden title-fallback, no suffix"))

    def test_mid_ref_only_is_not_identity(self):
        # a number that is NOT a trailing (#N) does not count as the PR
        self.assertIsNone(pr_number("fixes (#89 Item 8) but no PR suffix"))

    def test_bare_hash_without_parens_is_none(self):
        # a #N without the surrounding parens is not a PR identity
        self.assertIsNone(pr_number("fixes bug #42"))
