"""D4-c uncited-assertion token-detector tests (T-U1..T-U5).

Per spec §7.4 in
docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md.

Spec §7 names the file `tests/test_uncited_assertion.py`; the repo
convention puts pytest-discovered tests under `scripts/test_*.py`
(matching the 30+ existing files), so this file mirrors the spec stem
under the repo root. The three-condition rule + pseudocode lives in
academic-pipeline/agents/claim_ref_alignment_audit_agent.md
§"Uncited-assertion detector (D4-c)" and constants ride in
scripts/_claim_audit_constants.py so lint + runtime cannot drift.

Run:
    python -m unittest scripts.test_uncited_assertion -v
"""
from __future__ import annotations

import unittest

from scripts.uncited_assertion_detector import (
    detect_uncited,
    detect_uncited_assertions,
)


class TestDetectUncited(unittest.TestCase):
    """Per-condition predicate tests (spec §7.4 T-U1..T-U5)."""

    def test_t_u1_quantifier_no_ref_is_candidate(self) -> None:
        """Sentence with quantifier + no ref → uncited_assertion candidate."""
        sentence = "Roughly 50% of participants withdrew before week four."
        is_candidate, tokens = detect_uncited(sentence)
        self.assertTrue(is_candidate, msg=f"expected candidate; tokens={tokens!r}")
        # Quantifier token must be surfaced in trigger_tokens (U-INV-2 schema
        # rejects empty trigger_tokens — the detector is responsible for
        # populating the array).
        self.assertTrue(
            any("50%" in t or "50" in t for t in tokens),
            msg=f"expected '50%' in trigger_tokens; got {tokens!r}",
        )

    def test_t_u2_definition_is_not_candidate(self) -> None:
        """Definition sentence (contains 'refers to') → NOT candidate."""
        sentence = "Sycophancy refers to over-agreement with the user prompt."
        is_candidate, _ = detect_uncited(sentence)
        self.assertFalse(
            is_candidate,
            msg="definitional sentences are excluded per D4-c condition 3",
        )

    def test_t_u3_methods_boilerplate_is_not_candidate(self) -> None:
        """Methods boilerplate list → NOT candidate.

        A neutral method-description sentence carries neither a quantifier
        nor an empirical-claim verb (D4-c condition 1 fails), so it never
        reaches the candidate state regardless of citation status.
        """
        sentence = "Participants were recruited from the undergraduate pool."
        is_candidate, _ = detect_uncited(sentence)
        self.assertFalse(
            is_candidate,
            msg="methods boilerplate without quantifier/verb is not a candidate",
        )

    def test_t_u4_empirical_verb_is_candidate(self) -> None:
        """Empirical claim ('showed X%') without ref → candidate."""
        sentence = "Pilot data showed that completion rates dropped sharply."
        is_candidate, tokens = detect_uncited(sentence)
        self.assertTrue(is_candidate, msg=f"expected candidate; tokens={tokens!r}")
        self.assertIn(
            "showed",
            [t.lower() for t in tokens],
            msg=f"expected 'showed' in trigger_tokens; got {tokens!r}",
        )

    def test_t_u5_manifest_claim_no_ref_is_still_candidate(self) -> None:
        """Claim in manifest but no ref → still candidate (D4-c last paragraph).

        Manifest membership does NOT exempt a sentence from the token rule.
        The high-level `detect_uncited_assertions` wrapper must still emit
        a finding for a manifest-bound sentence when the three conditions
        hold.
        """
        sentences = [
            {
                "sentence_text": (
                    "Two-thirds of respondents agreed with the policy proposal."
                ),
                "section_path": "3. Results > 3.1 Survey Outcomes",
                "manifest_claim_id": "C-007",
                "scoped_manifest_id": "M-2026-05-16T00:00:00Z-abcd",
                "upstream_owner_agent": "draft_writer_agent",
            }
        ]
        findings = detect_uncited_assertions(sentences)
        self.assertEqual(
            len(findings),
            1,
            msg="manifest membership must NOT exempt a sentence per D4-c",
        )
        finding = findings[0]
        # Schema U-INV-2: trigger_tokens non-empty.
        self.assertGreater(len(finding["trigger_tokens"]), 0)
        # Spec §3.3 / U-INV-4: manifest_claim_id + scoped_manifest_id are
        # carried through so the finding can be cross-referenced against the
        # active manifest. The detector preserves any caller-provided values.
        self.assertEqual(finding["manifest_claim_id"], "C-007")
        self.assertEqual(
            finding["scoped_manifest_id"], "M-2026-05-16T00:00:00Z-abcd"
        )

    def test_ref_marker_short_circuits_candidate(self) -> None:
        """Sentence with `<!--ref:slug-->` marker → NOT candidate (condition 2).

        Belongs to spec §7.4 coverage (D4-c three-condition rule); the ref
        marker is the only gate distinguishing T-U1 from a properly-cited
        twin. Without this test the detector could silently flag every cited
        sentence and ride T-U1..T-U5 green.
        """
        cited = (
            "Roughly 50% of participants withdrew before week four "
            "<!--ref:smith2026-->."
        )
        is_candidate, _ = detect_uncited(cited)
        self.assertFalse(
            is_candidate, msg="ref marker present must short-circuit candidate"
        )

    def test_ref_marker_accepts_hyphenated_slug_and_finalizer_status(
        self,
    ) -> None:
        """v3.7.3 canonical slug + post-finalizer status tokens → NOT candidate.

        Regression for /simplify P1-1: an earlier `[^-]+` ref-marker probe
        rejected hyphenated slugs (`smith-et-al-2026`) and the post-finalizer
        annotation forms (`<!--ref:slug ok-->`, `<!--ref:slug LOW-WARN-->`,
        `<!--ref:slug ok CONTAMINATED-PREPRINT-->`), silently flagging
        properly-cited prose as uncited. Pins the regex against the
        v3.7.3 canonical slug pattern + 0-2 status-token suffix.
        """
        cited_shapes = [
            "Roughly 50% of cases improved <!--ref:smith-et-al-2026-->.",
            "Roughly 50% of cases improved <!--ref:smith-et-al-2026 ok-->.",
            "Roughly 50% of cases improved <!--ref:smith-2026 LOW-WARN-->.",
            (
                "Roughly 50% of cases improved "
                "<!--ref:smith-2026 ok CONTAMINATED-PREPRINT-->."
            ),
        ]
        for cited in cited_shapes:
            with self.subTest(cited=cited):
                is_candidate, _ = detect_uncited(cited)
                self.assertFalse(
                    is_candidate,
                    msg=(
                        "v3.7.3 canonical ref marker (hyphenated slug + "
                        "0-2 status tokens) must short-circuit candidate"
                    ),
                )

    def test_trigger_tokens_dedup_preserving_document_order(self) -> None:
        """Repeated quantifier/verb tokens emit once each in document order.

        Regression for codex R1 P2-2 and /simplify P1-2: prior implementation
        appended every match into trigger_tokens, then sorted by collection
        order (numeric pass first, then word pass) — producing token lists
        that did not reflect left-to-right document order. The first iteration
        of this test even encoded that bug as the assertion. Now the detector
        sorts by source offset, then dedups preserving the first occurrence.
        Document order matters because (a) passport diffs are more readable
        when token order matches sentence order, and (b) human reviewers
        expect the first token in the list to be the first phrase they hit
        when reading the sentence.
        """
        sentence = (
            "Pilot data showed that 50% of cases showed improvement, "
            "and most studies showed gains."
        )
        _, tokens = detect_uncited(sentence)
        self.assertEqual(
            tokens,
            ["showed", "50%", "most"],
            msg=(
                "trigger_tokens must reflect left-to-right document order "
                f"and dedup the three `showed`s; got {tokens!r}"
            ),
        )

    def test_numeric_quantifier_excludes_year_and_version_strings(self) -> None:
        """Bare years / version triples / section numbers → NOT a quantifier.

        Regression for /simplify P2-1 and codex R1 P1-3: the broad numeric
        regex catches every digit run, but a guard pass rejects shapes that
        identify the match as a year (1900-2099), a version triple
        (X.Y.Z[.W…]), a dotted-pair preceded by a section cue or `v` literal,
        OR a digit-run whose left neighbour is a `.` attached to another
        digit run (handles `v3.7.3` where Python's `\\b` fails between `v`
        and `3` and the regex only captures the tail `7.3`).
        """
        not_quantifier_examples = [
            # codex R1 P2-1 examples: each had a sibling regex bug before
            # the guard branches landed.
            "We follow ARS v3.7.3 in 2026 for the audit.",
            "See section 3.1.2 for the methodology.",
            "The dataset spans years 2018 through 2026.",
            "In section 3.1 we examine completion rates.",
            "Refer to Figure 3.2 for the trend.",
            "Step 4.1 outlines the survey protocol.",
        ]
        for sentence in not_quantifier_examples:
            with self.subTest(sentence=sentence):
                is_candidate, tokens = detect_uncited(sentence)
                self.assertFalse(
                    is_candidate,
                    msg=(
                        "bare years / version strings / section numbers "
                        f"must not fire D4-c condition 1; got {tokens!r}"
                    ),
                )

        # And the canonical quantifier idioms still fire.
        quantifier_examples = [
            ("Roughly 67% withdrew.", "67%"),
            ("Roughly 67 of 100 participants withdrew.", "67 of 100"),
        ]
        for sentence, expected in quantifier_examples:
            with self.subTest(sentence=sentence):
                is_candidate, tokens = detect_uncited(sentence)
                self.assertTrue(
                    is_candidate, msg=f"expected candidate for {sentence!r}"
                )
                self.assertIn(
                    expected,
                    tokens,
                    msg=(
                        f"expected {expected!r} in trigger_tokens for "
                        f"{sentence!r}; got {tokens!r}"
                    ),
                )

    def test_bare_number_quantifier_still_fires(self) -> None:
        """Bare integers and one-decimal numbers fire D4-c condition 1.

        Regression for codex R1 P1-3: spec line 250 lists 「numbers /
        percentages / explicit quantifiers」 — the prior tightening that
        rejected bare integers as a side-effect of removing year/version
        false positives also stripped the spec's first quantifier class.
        Bare numbers are restored with year/version/section guards;
        these examples must fire.
        """
        bare_number_examples = [
            ("The sample included 42 participants.", "42"),
            ("Mean age was 21.4 years.", "21.4"),
            ("We recruited 128 students.", "128"),
        ]
        for sentence, expected in bare_number_examples:
            with self.subTest(sentence=sentence):
                is_candidate, tokens = detect_uncited(sentence)
                self.assertTrue(
                    is_candidate,
                    msg=(
                        f"bare-number quantifier {expected!r} must fire "
                        f"D4-c condition 1 for {sentence!r}; got {tokens!r}"
                    ),
                )
                self.assertIn(expected, tokens)

    def test_detect_uncited_assertions_raises_on_missing_sentence_text(
        self,
    ) -> None:
        """Missing or non-string `sentence_text` raises ValueError.

        Regression for codex R1 P2-3: prior wrapper silently skipped raw
        dicts that lacked `sentence_text`, returning `(False, [])`. Silent
        skip for an audit pipeline is the worst failure mode — upstream
        bugs masquerade as "no findings". The wrapper now raises so the
        caller is forced to surface the bug.
        """
        with self.assertRaises(ValueError):
            detect_uncited_assertions([{"section_path": "1. Intro"}])
        with self.assertRaises(ValueError):
            detect_uncited_assertions([{"sentence_text": 42}])  # type: ignore[list-item]
        # Non-string but truthy types also raise — silent coercion would
        # be worse than a loud crash.
        with self.assertRaises(ValueError):
            detect_uncited_assertions(
                [{"sentence_text": ["This sentence got list-ified somehow."]}]  # type: ignore[list-item]
            )


if __name__ == "__main__":
    unittest.main()
