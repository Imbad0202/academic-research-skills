"""Unit tests for check_215_field_norm.py (#215).

The lint reads the three real reviewer surfaces. These tests (a) assert the shipped
files pass, and (b) monkey-patch the file reader to inject mutated content so every
assertion is shown to be non-vacuous (RED when the #215 block/marker is removed or
de-scoped). Mirrors the falsifiability discipline of check_v3_9_2_phase_boundary.
"""
from __future__ import annotations

import re
import unittest

from scripts import check_215_field_norm as cfn


DOMAIN = "academic-paper-reviewer/agents/domain_reviewer_agent.md"
DA = "academic-paper-reviewer/agents/devils_advocate_reviewer_agent.md"
CAL = "academic-paper-reviewer/references/calibration_mode_protocol.md"


def _real_reads() -> dict[str, str]:
    return {p: cfn._read(p) for p in (DOMAIN, DA, CAL)}


class TestShipped(unittest.TestCase):
    def test_shipped_surfaces_pass(self) -> None:
        self.assertEqual(cfn.check(), [], msg="shipped reviewer surfaces should pass #215 lint")


class TestMutations(unittest.TestCase):
    """Each test patches cfn._read to serve a mutated copy of ONE surface and asserts the
    lint goes RED with a message naming that surface."""

    def setUp(self) -> None:
        self._orig_read = cfn._read
        self._files = _real_reads()

    def tearDown(self) -> None:
        cfn._read = self._orig_read

    def _patch(self, path: str, mutate) -> list[str]:
        files = dict(self._files)
        files[path] = mutate(files[path])
        cfn._read = lambda p: files[p]
        return cfn.check()

    def test_domain_step5_removed_fails(self) -> None:
        errors = self._patch(
            DOMAIN, lambda t: t.replace("### Step 5: Field-Norm Severity Discipline (#215)", "### Step 5: Removed")
        )
        self.assertTrue(
            any("domain_reviewer_agent.md" in e and "Step 5" in e for e in errors),
            msg=f"expected domain Step 5 error: {errors!r}",
        )

    def test_domain_broadened_evidence_removed_fails(self) -> None:
        errors = self._patch(
            DOMAIN, lambda t: t.replace("not limited to a literature citation", "limited to a literature citation")
        )
        self.assertTrue(
            any("broadened-evidence" in e for e in errors),
            msg=f"expected broadened-evidence error: {errors!r}",
        )

    def test_domain_must_not_scoped_to_block(self) -> None:
        """Removing 'MUST NOT' from the Step 5 block must fail even though MUST NOT may exist
        elsewhere in the file — proving the check is block-scoped, not file-wide."""
        errors = self._patch(
            DOMAIN,
            lambda t: self._strip_in_block(
                t, "### Step 5: Field-Norm Severity Discipline (#215)", "MUST NOT", "must-not"
            ),
        )
        self.assertTrue(
            any("domain_reviewer_agent.md Step 5" in e and "MUST NOT" in e for e in errors),
            msg=f"expected block-scoped MUST NOT error: {errors!r}",
        )

    def test_da_dimension9_removed_fails(self) -> None:
        errors = self._patch(
            DA, lambda t: t.replace("### 9. Field-Norm Severity Calibration (#215)", "### 9. Removed")
        )
        self.assertTrue(
            any("devils_advocate_reviewer_agent.md" in e and "dimension" in e for e in errors),
            msg=f"expected DA dimension 9 error: {errors!r}",
        )

    def test_da_field_removed_fails(self) -> None:
        errors = self._patch(
            DA, lambda t: t.replace("field_norm_boundary", "xxx").replace("evidence_crossing_rationale", "yyy")
        )
        self.assertTrue(
            any("field_norm_boundary" in e for e in errors)
            and any("evidence_crossing_rationale" in e for e in errors),
            msg=f"expected DA missing-field errors: {errors!r}",
        )

    def test_calibration_phase35_removed_fails(self) -> None:
        errors = self._patch(
            CAL, lambda t: t.replace("### Phase 3.5: Severity-miscalibration measurement (#215)", "### Phase 3.5: Removed")
        )
        self.assertTrue(
            any("calibration_mode_protocol.md" in e and "Phase 3.5" in e for e in errors),
            msg=f"expected calibration Phase 3.5 error: {errors!r}",
        )

    def test_calibration_anti_circularity_removed_fails(self) -> None:
        """Removing the anti-circularity anchor (the gold-set pointer) from Phase 3.5 must fail —
        this is the codex P1 fix that the classifier rates grounding, not norm-correctness."""
        errors = self._patch(
            CAL,
            lambda t: self._strip_in_block(
                t,
                "### Phase 3.5: Severity-miscalibration measurement (#215)",
                "evals/gold/field_norm_severity",
                "evals/gold/REMOVED",
            ),
        )
        self.assertTrue(
            any("calibration_mode_protocol.md Phase 3.5" in e and "anti-circularity" in e for e in errors),
            msg=f"expected anti-circularity error: {errors!r}",
        )

    @staticmethod
    def _strip_in_block(text: str, header: str, needle: str, replacement: str) -> str:
        """Replace `needle` with `replacement` ONLY inside the block starting at `header`
        (up to the next ##/### header), leaving any same-string occurrences elsewhere intact.
        Lets a test prove block-scoping rather than file-wide presence. Reuses the lint's own
        `_block()` so the test and the production scope logic cannot drift apart."""
        block = cfn._block(text, re.escape(header))
        if block is None:
            return text
        start = text.index(block)
        return text[:start] + block.replace(needle, replacement) + text[start + len(block):]


if __name__ == "__main__":
    unittest.main()
