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
    audit,
    is_covered,
    is_exempt,
    pr_number,
    Uncovered,
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


class IsExemptTest(unittest.TestCase):
    def test_exempt_types(self):
        for subj in [
            "chore: bump deps (#1)",
            "test: add pin (#2)",
            "ci: tweak workflow (#3)",
            "build: package (#4)",
            "ci(scope): scoped ci (#5)",  # scope-tolerant
        ]:
            self.assertTrue(is_exempt(subj), subj)

    def test_exempt_internal_docs_scopes(self):
        self.assertTrue(is_exempt("docs(design): spec (#6)"))
        self.assertTrue(is_exempt("docs(superpowers): plan (#7)"))

    def test_required_prefixes(self):
        for subj in [
            "feat: thing (#8)",
            "fix: bug (#9)",
            "docs: user-facing (#10)",          # bare docs REQUIRED
            "docs(contributing): guide (#11)",  # other docs scope REQUIRED
            "refactor: cleanup (#12)",
            "perf: speed (#13)",
            "Harden title-fallback (#14)",      # no-prefix REQUIRED
        ]:
            self.assertFalse(is_exempt(subj), subj)

    def test_breaking_marker_and_case_sensitivity(self):
        # breaking-change "!" marker must not disturb scope parsing
        self.assertTrue(is_exempt("docs(design)!: breaking spec (#15)"))
        self.assertTrue(is_exempt("chore(deps)!: bump (#16)"))
        # type match is case-sensitive: capitalized prefixes are REQUIRED
        self.assertFalse(is_exempt("Chore: capitalized (#17)"))
        self.assertFalse(is_exempt('Revert "feat: x" (#18)'))


class IsCoveredTest(unittest.TestCase):
    UNRELEASED = "- **Thing (#432).** did a thing\n- another (#89 Item 7)\n"

    def test_covered_exact(self):
        self.assertTrue(is_covered(432, self.UNRELEASED))

    def test_token_boundary_no_substring_match(self):
        # #42 must NOT be "covered" by #432 in the text
        self.assertFalse(is_covered(42, self.UNRELEASED))

    def test_uncovered(self):
        self.assertFalse(is_covered(999, self.UNRELEASED))

    def test_requires_hash_prefix(self):
        # a bare "432" (no #) in prose must not count
        self.assertFalse(is_covered(432, "the year was 432 AD\n"))


class AuditTest(unittest.TestCase):
    def test_required_covered_passes(self):
        subjects = ["feat: thing (#432)"]
        unreleased = "- thing (#432)\n"
        self.assertEqual(audit(subjects, unreleased), [])

    def test_required_uncovered_fails(self):
        subjects = ["feat: thing (#999)"]
        unreleased = "- something else (#1)\n"
        result = audit(subjects, unreleased)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pr, 999)
        self.assertEqual(result[0].reason, "not in [Unreleased]")

    def test_exempt_skipped_even_if_uncovered(self):
        subjects = ["chore: x (#7)", "test: y (#8)"]
        self.assertEqual(audit(subjects, ""), [])

    def test_no_trailing_pr_is_unverifiable(self):
        subjects = ["feat: thing with no suffix"]
        result = audit(subjects, "anything")
        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0].pr)
        self.assertEqual(result[0].reason, "no trailing (#N)")

    def test_revert_requires_own_pr(self):
        # Revert's own PR is #433; the reverted #432 must not cover it.
        subjects = ['Revert "feat: thing (#432)" (#433)']
        # changelog mentions only the OLD #432, not the revert #433
        result = audit(subjects, "- thing (#432)\n")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].pr, 433)

    def test_revert_covered_by_own_pr_passes(self):
        subjects = ['Revert "feat: thing (#432)" (#433)']
        self.assertEqual(audit(subjects, "- reverted thing (#433)\n"), [])

    def test_mixed_list_accumulates_in_order(self):
        subjects = [
            "chore: x (#7)",                      # exempt -> skip
            "feat: covered (#100)",               # required, covered -> pass
            "feat: uncovered (#200)",             # required -> fail
            "Harden thing no suffix",             # no PR -> fail
            'Revert "feat: old (#432)" (#433)',   # revert, #433 uncovered -> fail
        ]
        result = audit(subjects, "- covered (#100)\n")
        self.assertEqual(
            result,
            [
                Uncovered("feat: uncovered (#200)", 200, "not in [Unreleased]"),
                Uncovered("Harden thing no suffix", None, "no trailing (#N)"),
                Uncovered('Revert "feat: old (#432)" (#433)', 433, "not in [Unreleased]"),
            ],
        )
