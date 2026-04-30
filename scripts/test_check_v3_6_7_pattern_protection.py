"""Unit tests for check_v3_6_7_pattern_protection.py (ARS v3.6.7 lint).

Mutation evidence preserved from codex review rounds R3-R5 (B2 phase). Each
test mutates a v3.6.7 PATTERN PROTECTION clause in a temporary copy of the
repo and asserts the lint flags it. This guards against future regressions
in the lint contract — without these tests, CI would only verify that the
*current* prompt prose passes, but a checker regression that silently
accepts weakened obligations would be caught only by ad-hoc mutation runs.

The test suite operates on a sandboxed copy of the repo: each test
constructs the copy via `git archive HEAD | tar -x`, applies a single
mutation, and runs `scripts/check_v3_6_7_pattern_protection.py` against
that copy. The repo's actual files are never modified.
"""
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LINT_SCRIPT_REL = "scripts/check_v3_6_7_pattern_protection.py"


def _archive_repo(dest: Path) -> None:
    """Materialise current `HEAD` into `dest` via git archive | tar."""
    archive = subprocess.Popen(
        ["git", "archive", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE
    )
    try:
        subprocess.run(
            ["tar", "-x", "-C", str(dest)], stdin=archive.stdout, check=True
        )
    finally:
        if archive.stdout is not None:
            archive.stdout.close()
        archive.wait()
    if archive.returncode != 0:
        raise RuntimeError(f"git archive failed: rc={archive.returncode}")


def _run_lint(repo_dir: Path) -> tuple[int, str, str]:
    """Run the v3.6.7 lint inside `repo_dir`. Returns (rc, stdout, stderr)."""
    proc = subprocess.run(
        ["python3", LINT_SCRIPT_REL],
        cwd=repo_dir,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout, proc.stderr


def _mutate(repo_dir: Path, rel_path: str, old: str, new: str) -> None:
    """Apply a single replace mutation to `repo_dir/rel_path`. Asserts the
    `old` string is present (so a refactored prompt that no longer matches
    surfaces as a clear test failure rather than silently-no-op)."""
    path = repo_dir / rel_path
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(
            f"Mutation source string not found in {rel_path}: "
            f"{old[:80]!r}..."
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


class _MutationTestBase(unittest.TestCase):
    """Each test materialises a fresh repo copy under self._repo_dir."""

    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory(prefix="ars-v367-test.")
        self._repo_dir = Path(self._tmpdir.name)
        _archive_repo(self._repo_dir)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def assert_baseline_passes(self) -> None:
        rc, _stdout, stderr = _run_lint(self._repo_dir)
        self.assertEqual(rc, 0, f"baseline lint should pass; stderr={stderr}")

    def assert_mutation_fails(self) -> None:
        rc, _stdout, _stderr = _run_lint(self._repo_dir)
        self.assertNotEqual(rc, 0, "mutation should make lint fail")


class BaselineTest(_MutationTestBase):
    def test_unmutated_repo_passes(self) -> None:
        self.assert_baseline_passes()


class R2MutationTests(_MutationTestBase):
    """R2-001 closure: per-regex allow_prohibition stops C3's `must not`
    exemption from leaking into C1's assertion-style obligation."""

    def test_c1_inverted_must_not_preserve_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "Compression must preserve protected hedging phrases",
            "Compression must not preserve protected hedging phrases",
        )
        self.assert_mutation_fails()

    def test_c3_audit_passed_sentence_deleted_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "\n- Output metadata must not claim audit-passed state.",
            "",
        )
        self.assert_mutation_fails()


class R3MutationTests(_MutationTestBase):
    """R3-001 (span-restricted prohibition exemption), R3-002 (token →
    regex), R3-003 (except/unless weakeners)."""

    def test_r3_001_trailing_must_not_be_enforced_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "Output metadata must not claim audit-passed state.",
            "Output metadata must not claim audit-passed state; this must not be enforced.",
        )
        self.assert_mutation_fails()

    def test_r3_001_orchestrator_does_not_run_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "The orchestrator runs codex audit afterward.",
            "The orchestrator does not run codex audit afterward.",
        )
        self.assert_mutation_fails()

    def test_r3_002_a2_pending_verification_optional_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            'wrap claims in explicit hedge ("pending verification of X" / "inferred from upstream Y").',
            "pending verification language is optional; claims may be written as facts.",
        )
        self.assert_mutation_fails()

    def test_r3_002_c2_may_use_year_range_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            'Reflexivity disclosure must use explicit temporal bounds: explicit year range, past-tense disambiguating verb, or "former" prefix. Deictic temporal phrases ("during this period" / "at the time") are forbidden.',
            'Reflexivity disclosure may use an explicit year range, but deictic temporal phrases ("during this period" / "at the time") are allowed when shorter.',
        )
        self.assert_mutation_fails()

    def test_r3_003_no_subsetting_except_when_concise_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/research_architect_agent.md",
            "No subsetting, no over-setting, no scope cross-contamination.",
            "No subsetting except when concise, no over-setting, no scope cross-contamination.",
        )
        self.assert_mutation_fails()


class R4MutationTests(_MutationTestBase):
    """R4-001 (modal verb scope), R4-002 (sub-clause coverage)."""

    def test_r4_001_a2_may_wrap_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            'For any source flagged "pending verification" upstream: wrap claims in explicit hedge',
            'For any source flagged "pending verification" upstream: may wrap claims in explicit hedge',
        )
        self.assert_mutation_fails()

    def test_r4_001_a3_may_include_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            "For each substantive claim: include a one-line anchor justification.",
            "For each substantive claim: may include a one-line anchor justification.",
        )
        self.assert_mutation_fails()

    def test_r4_001_a1_recommended_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            "pre-list the source's effect inventory and run a cross-section consistency self-check before output.",
            "pre-list the source's effect inventory and cross-section consistency self-check are recommended before output.",
        )
        self.assert_mutation_fails()

    def test_r4_002_a4_may_be_quoted_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            "surrounding context paraphrased and unquoted.",
            "surrounding context may be quoted.",
        )
        self.assert_mutation_fails()

    def test_r4_002_a5_drop_conditional_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            'use conditional language ("if document X argues Y, this chapter could dialogue by Z") or explicit gap acknowledgment. Declarative claims about un-provided documents are forbidden.',
            "Declarative claims about un-provided documents are forbidden.",
        )
        self.assert_mutation_fails()

    def test_r4_002_b4_allow_chapter_vocab_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/research_architect_agent.md",
            "Item phrasing must be neutral/balanced. Chapter argument vocabulary is forbidden in instrument items.",
            "Item phrasing may use chapter argument vocabulary in instrument items.",
        )
        self.assert_mutation_fails()

    def test_r4_002_b5_allow_overset_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/research_architect_agent.md",
            "No subsetting, no over-setting, no scope cross-contamination.",
            "No subsetting. Over-setting and scope cross-contamination are allowed.",
        )
        self.assert_mutation_fails()

    def test_r4_002_c1_drop_buffer_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "Word budget uses whitespace-split convention (`body.split()`), not hyphenated-as-1. Reserve 3–5% buffer below hard cap.",
            "Word budget uses whitespace-split convention (`body.split()`), not hyphenated-as-1.",
        )
        self.assert_mutation_fails()

    def test_r4_002_c2_drop_past_tense_form_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            'Reflexivity disclosure must use explicit temporal bounds: explicit year range, past-tense disambiguating verb, or "former" prefix.',
            "Reflexivity disclosure must use explicit temporal bounds: explicit year range.",
        )
        self.assert_mutation_fails()


class R5MutationTests(_MutationTestBase):
    """R5-001 (advisory weakeners: should/can/permitted)."""

    def test_r5_001_a2_should_wrap_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            'For any source flagged "pending verification" upstream: wrap claims in explicit hedge',
            'For any source flagged "pending verification" upstream: should wrap claims in explicit hedge',
        )
        self.assert_mutation_fails()

    def test_r5_001_a3_should_include_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            "For each substantive claim: include a one-line anchor justification.",
            "For each substantive claim: should include a one-line anchor justification.",
        )
        self.assert_mutation_fails()

    def test_r5_001_a4_can_be_quoted_tail_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            "surrounding context paraphrased and unquoted.",
            "surrounding context paraphrased and unquoted, but can be quoted for flow.",
        )
        self.assert_mutation_fails()

    def test_r5_001_b5_overset_permitted_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/research_architect_agent.md",
            "No subsetting, no over-setting, no scope cross-contamination.",
            "No subsetting, no scope cross-contamination; over-setting is permitted when concise.",
        )
        self.assert_mutation_fails()

    def test_r5_001_b5_should_declare_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/research_architect_agent.md",
            "Any list-of-options item must declare its primary-source list and enumerate fully.",
            "Any list-of-options item should declare its primary-source list and enumerate fully.",
        )
        self.assert_mutation_fails()

    def test_r5_001_c1_should_preserve_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "Compression must preserve protected hedging phrases identified by upstream calibration as budget-protected (the dispatch context carries the list).",
            "Compression should preserve protected hedging phrases identified by upstream calibration as budget-protected (the dispatch context carries the list).",
        )
        self.assert_mutation_fails()


class R6MutationTests(_MutationTestBase):
    """R6-001 (future/conditional modals + advisory adverb weakeners)."""

    def test_r6_001_c1_will_not_preserve_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "Compression must preserve protected hedging phrases",
            "Compression will not preserve protected hedging phrases",
        )
        self.assert_mutation_fails()

    def test_r6_001_c1_would_preserve_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/report_compiler_agent.md",
            "Compression must preserve protected hedging phrases",
            "Compression would preserve protected hedging phrases",
        )
        self.assert_mutation_fails()

    def test_r6_001_a2_ought_to_wrap_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            'For any source flagged "pending verification" upstream: wrap claims in explicit hedge',
            'For any source flagged "pending verification" upstream: ought to wrap claims in explicit hedge',
        )
        self.assert_mutation_fails()

    def test_r6_001_a3_ideally_include_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            "For each substantive claim: include a one-line anchor justification.",
            "For each substantive claim: ideally include a one-line anchor justification.",
        )
        self.assert_mutation_fails()

    def test_r6_001_b5_preferably_enumerate_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/research_architect_agent.md",
            "Any list-of-options item must declare its primary-source list and enumerate fully.",
            "Any list-of-options item must declare its primary-source list and preferably enumerate fully.",
        )
        self.assert_mutation_fails()

    def test_r6_001_a3_we_recommend_that_fails(self) -> None:
        _mutate(
            self._repo_dir,
            "deep-research/agents/synthesis_agent.md",
            "For each substantive claim: include a one-line anchor justification.",
            "We recommend that each substantive claim include a one-line anchor justification.",
        )
        self.assert_mutation_fails()


if __name__ == "__main__":
    unittest.main()
