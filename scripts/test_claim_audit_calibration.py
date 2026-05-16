"""Calibration-mode test for v3.8 claim_ref_alignment_audit_agent (T-C1..T-C3).

Per spec §7.7 in
docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md.

Three-tier acceptance:

- T-C1: FNR < 0.15 AND FPR < 0.10 against the synthetic 20-tuple gold set.
  Threshold failures are CI gates, not advisory.
- T-C2: per-class FNR/FPR (SUPPORTED / UNSUPPORTED / AMBIGUOUS /
  violated-constraint) appear in the calibration report.
- T-C3: gold-set shape integrity — each tuple has tuple_kind ∈ {alignment,
  constraint}, alignment tuples carry expected_judgment ∈ {SUPPORTED,
  UNSUPPORTED, AMBIGUOUS, RETRIEVAL_FAILED} with no constraint fields,
  constraint tuples carry expected_judgment ∈ {VIOLATED, NOT_VIOLATED} +
  constraint_under_test_id + (constraint_under_test_rule_text OR
  manifest_fixture_path), and the gold set has ≥3 NOT_VIOLATED constraint
  tuples (else constraint FPR is unmeasurable).

Why three tiers:
- T-C2 catches calibration tooling regressions (script doesn't compute or
  doesn't write report) distinct from gold-set degradation.
- T-C3 catches gold-set authoring bugs (missing required rule text /
  insufficient NOT_VIOLATED count) before they silently bypass T-C1.
- T-C1 catches model/judge quality regression.

Spec § 7 writes `tests/test_claim_audit_calibration.py`; repo convention
is `scripts/test_*.py` per spec §13 step 9 path-mapping rule. CI uses
`python -m unittest scripts.test_*`.

Run:
    python -m unittest scripts.test_claim_audit_calibration -v
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any, Callable

from scripts.claim_audit_calibration import (
    GoldSetValidationError,
    run_calibration,
    validate_gold_set,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLD_SET_PATH = REPO_ROOT / "scripts" / "fixtures" / "claim_audit_calibration" / "gold_set.json"


def _load_gold_set() -> list[dict[str, Any]]:
    with GOLD_SET_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def _tuple_lookup_key(tup: dict[str, Any]) -> tuple[str, str, str | None]:
    """Composite lookup key so identical claim_text on different tuple_kind /
    constraint_id pairs disambiguate (R1 Gemini P2-b closure).

    The canonical gold set currently has unique claim_text per tuple, but
    future gold sets may evaluate the same claim under different MNC ids
    (e.g. one alignment tuple + one constraint tuple sharing prose). A
    claim_text-only key would silently overwrite earlier entries and
    cause _perfect_judge to return the wrong stub response, falsely
    triggering T-C1 failures.
    """
    return (
        tup["tuple_kind"],
        tup["claim_text"],
        tup.get("constraint_under_test_id"),
    )


def _perfect_judge() -> Callable[..., dict[str, Any]]:
    """Stub judge that returns the gold-set expected_judgment verbatim.

    Used by T-C1 to verify the calibration script's FNR / FPR computation
    on a path where the judge perfectly matches the gold set. The stub
    looks up the tuple by composite key (tuple_kind, claim_text,
    constraint_under_test_id) so duplicate claim_text under different
    constraint scopes does not collapse. The dispatch infers tuple kind
    from kwargs: a non-empty `active_constraints` list means the runner
    is on the constraint code path. A real LLM judge wires here at
    operational deployment per the protocol doc.
    """
    tuples_by_key: dict[tuple[str, str, str | None], dict[str, Any]] = {
        _tuple_lookup_key(t): t for t in _load_gold_set()
    }

    def fn(**kwargs: Any) -> dict[str, Any]:
        claim_text = kwargs.get("claim_text", "")
        active = kwargs.get("active_constraints") or []
        constraint_id = active[0]["constraint_id"] if active else None
        kind = "constraint" if active else "alignment"
        tup = tuples_by_key.get((kind, claim_text, constraint_id))
        if tup is None:
            raise AssertionError(
                f"perfect_judge: no gold tuple for kind={kind!r} "
                f"claim_text={claim_text!r} constraint_id={constraint_id!r}"
            )
        expected = tup["expected_judgment"]
        if kind == "alignment":
            return {"judgment": expected, "rationale": "perfect-judge stub"}
        # constraint tuple
        if expected == "VIOLATED":
            return {
                "judgment": "VIOLATED",
                "violated_constraint_id": tup["constraint_under_test_id"],
                "rationale": "perfect-judge stub",
            }
        return {
            "judgment": "NOT_VIOLATED",
            "rationale": "perfect-judge stub",
        }

    return fn


_BAD_JUDGE_FLIP_ALIGNMENT: dict[str, str] = {
    "SUPPORTED": "UNSUPPORTED",
    "UNSUPPORTED": "SUPPORTED",
    "AMBIGUOUS": "UNSUPPORTED",
    "RETRIEVAL_FAILED": "SUPPORTED",
}


def _bad_judge() -> Callable[..., dict[str, Any]]:
    """Stub judge that intentionally returns wrong labels to drive non-zero
    FNR/FPR (R1 Gemini P1 / codex P2 closure on tautological T-C1).

    Used by `TC1ThresholdEnforcementBadJudge` to verify that
    `run_calibration` accurately COMPUTES FNR/FPR and that the threshold
    gate WOULD fire when the judge degrades. Without this companion test
    T-C1 only proves tooling correctness on a perfect-mirror stub;
    pairing both proves tooling correctness AND threshold-gate
    enforceability.

    Strategy: flip every alignment expected label to its opposite class
    and flip every VIOLATED expected to NOT_VIOLATED. Drives every tuple
    into FN/FP territory so aggregate FNR + FPR both massively exceed
    the thresholds.

    R2 Gemini P3 closure: lookup tables are built ONCE at factory time
    (not per fn() call) so the gold set isn't re-read from disk for every
    judge invocation. Both alignment and constraint paths use the
    composite key from `_tuple_lookup_key` so duplicate claim_text under
    different (tuple_kind, constraint_id) never silently collapses
    — same hardening _perfect_judge already carries.
    """
    tuples_by_key: dict[tuple[str, str, str | None], dict[str, Any]] = {
        _tuple_lookup_key(t): t for t in _load_gold_set()
    }

    def fn(**kwargs: Any) -> dict[str, Any]:
        claim_text = kwargs.get("claim_text", "")
        active = kwargs.get("active_constraints") or []
        constraint_id = active[0]["constraint_id"] if active else None
        kind = "constraint" if active else "alignment"
        tup = tuples_by_key.get((kind, claim_text, constraint_id))
        if tup is None:
            raise AssertionError(
                f"bad_judge: no gold tuple for kind={kind!r} "
                f"claim_text={claim_text!r} constraint_id={constraint_id!r}"
            )
        if kind == "alignment":
            return {
                "judgment": _BAD_JUDGE_FLIP_ALIGNMENT[tup["expected_judgment"]],
                "rationale": "bad-judge stub (flipped)",
            }
        # Constraint path — flip VIOLATED ↔ NOT_VIOLATED.
        if tup["expected_judgment"] == "VIOLATED":
            return {"judgment": "NOT_VIOLATED", "rationale": "bad-judge flip"}
        return {
            "judgment": "VIOLATED",
            "violated_constraint_id": constraint_id,
            "rationale": "bad-judge flip",
        }

    return fn


# ---------------------------------------------------------------------------
# T-C3 — Gold-set shape integrity.
# ---------------------------------------------------------------------------


class TC3GoldSetShape(unittest.TestCase):
    """T-C3 catches gold-set authoring bugs before T-C1 can silently bypass them.

    Spec §7.7 list (a)-(d):
      (a) every tuple has tuple_kind ∈ {alignment, constraint}
      (b) alignment tuples → expected_judgment in 4-alignment-judgment set,
          NO constraint fields
      (c) constraint tuples → expected_judgment ∈ {VIOLATED, NOT_VIOLATED}
          AND constraint_under_test_id AND
          (constraint_under_test_rule_text OR manifest_fixture_path)
      (d) ≥3 NOT_VIOLATED constraint tuples (else FPR is unmeasurable)

    Any violation is rejected at calibration ingestion with a diagnostic
    naming the rule that failed.
    """

    def setUp(self) -> None:
        self.gold_set = _load_gold_set()

    def test_a_every_tuple_has_valid_tuple_kind(self) -> None:
        # All 20 tuples must declare tuple_kind ∈ {alignment, constraint}.
        # Spec §7.7 rule (a).
        for idx, tup in enumerate(self.gold_set):
            self.assertIn(
                tup.get("tuple_kind"),
                {"alignment", "constraint"},
                f"tuple {idx} has invalid tuple_kind {tup.get('tuple_kind')!r}",
            )

    def test_b_alignment_tuples_shape_pinned(self) -> None:
        # Alignment tuples carry expected_judgment in 4-judgment set AND
        # MUST NOT carry constraint fields. Spec §7.7 rule (b).
        alignment_set = {"SUPPORTED", "UNSUPPORTED", "AMBIGUOUS", "RETRIEVAL_FAILED"}
        constraint_fields = (
            "constraint_under_test_id",
            "constraint_under_test_rule_text",
            "manifest_fixture_path",
        )
        for idx, tup in enumerate(self.gold_set):
            if tup.get("tuple_kind") != "alignment":
                continue
            self.assertIn(
                tup.get("expected_judgment"),
                alignment_set,
                f"alignment tuple {idx} carries invalid expected_judgment "
                f"{tup.get('expected_judgment')!r}",
            )
            for field in constraint_fields:
                self.assertNotIn(
                    field,
                    tup,
                    f"alignment tuple {idx} must not carry constraint field {field!r}",
                )

    def test_c_constraint_tuples_have_required_fields(self) -> None:
        # Constraint tuples carry expected_judgment ∈ {VIOLATED, NOT_VIOLATED}
        # AND constraint_under_test_id AND
        # (constraint_under_test_rule_text OR manifest_fixture_path). Spec §7.7 rule (c).
        for idx, tup in enumerate(self.gold_set):
            if tup.get("tuple_kind") != "constraint":
                continue
            self.assertIn(
                tup.get("expected_judgment"),
                {"VIOLATED", "NOT_VIOLATED"},
                f"constraint tuple {idx} carries invalid expected_judgment "
                f"{tup.get('expected_judgment')!r}",
            )
            self.assertIn(
                "constraint_under_test_id",
                tup,
                f"constraint tuple {idx} missing constraint_under_test_id",
            )
            has_rule_text = bool(tup.get("constraint_under_test_rule_text"))
            has_manifest_path = bool(tup.get("manifest_fixture_path"))
            self.assertTrue(
                has_rule_text or has_manifest_path,
                f"constraint tuple {idx} missing both "
                f"constraint_under_test_rule_text and manifest_fixture_path",
            )

    def test_d_at_least_three_not_violated_constraint_tuples(self) -> None:
        # ≥3 NOT_VIOLATED constraint tuples — without them constraint FPR
        # is unmeasurable and T-C1 cannot fail-on-threshold on the
        # constraint line. Spec §7.7 rule (d).
        not_violated = [
            t for t in self.gold_set
            if t.get("tuple_kind") == "constraint"
            and t.get("expected_judgment") == "NOT_VIOLATED"
        ]
        self.assertGreaterEqual(
            len(not_violated),
            3,
            f"gold set must include ≥3 NOT_VIOLATED constraint tuples; "
            f"got {len(not_violated)}",
        )

    def test_validate_gold_set_rejects_invalid_tuple_kind(self) -> None:
        # Rule (a) negative ingestion test — R1 codex P3 + Gemini P2
        # closure on T-C3 rule coverage. Diagnostic must name rule (a).
        broken = [
            {
                "tuple_kind": "comparison",  # not in {alignment, constraint}
                "claim_text": "broken",
                "expected_judgment": "SUPPORTED",
            }
        ]
        with self.assertRaises(GoldSetValidationError) as ctx:
            validate_gold_set(broken)
        msg = str(ctx.exception)
        self.assertIn("rule (a)", msg, f"diagnostic must name rule (a); got {msg!r}")
        self.assertIn("tuple 0", msg, f"diagnostic must name offending index; got {msg!r}")

    def test_validate_gold_set_rejects_alignment_with_constraint_field(self) -> None:
        # validate_gold_set is the production entrypoint that the
        # calibration runner calls at ingestion time. It MUST raise the
        # documented error on rule-(b) violation. R1 codex P3 closure:
        # also assert rule (b) name in diagnostic.
        broken = [
            {
                "tuple_kind": "alignment",
                "claim_text": "broken",
                "expected_judgment": "SUPPORTED",
                "constraint_under_test_id": "MNC-1",  # forbidden on alignment
            }
        ]
        with self.assertRaises(GoldSetValidationError) as ctx:
            validate_gold_set(broken)
        msg = str(ctx.exception)
        self.assertIn("rule (b)", msg, f"diagnostic must name rule (b); got {msg!r}")
        self.assertIn("alignment", msg.lower())

    def test_validate_gold_set_rejects_constraint_without_rule_text(self) -> None:
        # Rule (c) — constraint tuple missing both rule_text AND
        # manifest_fixture_path. Most common silent-skip authoring bug.
        broken = [
            {
                "tuple_kind": "constraint",
                "claim_text": "broken",
                "expected_judgment": "VIOLATED",
                "constraint_under_test_id": "MNC-1",
                # neither rule_text nor manifest_fixture_path
            }
        ]
        with self.assertRaises(GoldSetValidationError) as ctx:
            validate_gold_set(broken)
        msg = str(ctx.exception)
        self.assertIn("rule (c)", msg, f"diagnostic must name rule (c); got {msg!r}")
        msg_lower = msg.lower()
        self.assertTrue("rule_text" in msg_lower or "manifest_fixture_path" in msg_lower)

    def test_validate_gold_set_rejects_under_three_not_violated(self) -> None:
        # Rule (d) — fewer than 3 NOT_VIOLATED constraint tuples.
        broken: list[dict[str, Any]] = [
            {
                "tuple_kind": "constraint",
                "claim_text": f"v{i}",
                "expected_judgment": "VIOLATED",
                "constraint_under_test_id": "MNC-1",
                "constraint_under_test_rule_text": "no causal language",
            }
            for i in range(5)
        ] + [
            {
                "tuple_kind": "constraint",
                "claim_text": "nv1",
                "expected_judgment": "NOT_VIOLATED",
                "constraint_under_test_id": "MNC-1",
                "constraint_under_test_rule_text": "no causal language",
            }
        ]  # only 1 NOT_VIOLATED, need ≥3
        with self.assertRaises(GoldSetValidationError) as ctx:
            validate_gold_set(broken)
        msg = str(ctx.exception)
        self.assertIn("rule (d)", msg, f"diagnostic must name rule (d); got {msg!r}")
        self.assertIn("NOT_VIOLATED", msg)

    def test_validate_gold_set_accepts_canonical_gold_set(self) -> None:
        # Positive path — the shipped gold set MUST validate cleanly.
        self.assertIsNone(validate_gold_set(self.gold_set))

    def test_run_calibration_rejects_manifest_only_constraint_tuple(self) -> None:
        # R2 codex P1 closure: validate_gold_set accepts EITHER inline
        # rule_text OR manifest_fixture_path per spec §7.7 rule (c), but
        # the v3.8.0 runner only supports the inline form. A manifest-only
        # tuple validating clean but reaching the judge with rule="" is
        # exactly the silent-skip authoring bug T-C3 is supposed to
        # prevent. The runner MUST raise NotImplementedError at run time
        # rather than pass the empty rule through to the judge. We pin
        # this against a minimal synthetic set (no stub lookup needed
        # because run_calibration raises before any judge invocation
        # for the constraint tuples).
        def _never_called_judge(**kwargs: Any) -> dict[str, Any]:
            raise AssertionError("judge MUST NOT be called when manifest_only tuple raises")

        manifest_only = [
            # constraint tuple using manifest_fixture_path only (rule (c)
            # second branch). Validates clean but runner must refuse.
            {
                "tuple_kind": "constraint",
                "claim_text": "manifest-only constraint",
                "ref_text_excerpt": None,
                "anchor": {"kind": "page", "value": "1"},
                "expected_judgment": "VIOLATED",
                "constraint_under_test_id": "MNC-3",
                "manifest_fixture_path": "scripts/fixtures/claim_audit_calibration/nonexistent.json",
            },
            # Three NOT_VIOLATED constraint tuples to satisfy rule (d).
            # Use inline rule_text so validate_gold_set passes; the
            # NotImplementedError fires on the FIRST manifest-only
            # tuple it encounters, before any of these run.
            *[
                {
                    "tuple_kind": "constraint",
                    "claim_text": f"nv-filler-{i}",
                    "ref_text_excerpt": None,
                    "anchor": {"kind": "page", "value": "1"},
                    "expected_judgment": "NOT_VIOLATED",
                    "constraint_under_test_id": "MNC-3",
                    "constraint_under_test_rule_text": "filler rule",
                }
                for i in range(3)
            ],
        ]
        # Step 1: validate_gold_set MUST accept the manifest-only tuple
        # (spec §7.7 rule (c) second branch).
        self.assertIsNone(validate_gold_set(manifest_only))
        # Step 2: run_calibration MUST refuse it at run time.
        with self.assertRaises(NotImplementedError) as ctx:
            run_calibration(manifest_only, judge_fn=_never_called_judge)
        msg = str(ctx.exception)
        self.assertIn("manifest_fixture_path", msg)
        self.assertIn("post-v3.8", msg.lower())


# ---------------------------------------------------------------------------
# T-C2 — Per-class FNR/FPR reporting.
# ---------------------------------------------------------------------------


class TC2PerClassReport(unittest.TestCase):
    """T-C2 catches calibration tooling regressions (script doesn't compute /
    doesn't write report) distinct from gold-set or model degradation.

    Spec §7.7: 'FNR/FPR are computed AND surfaced per judgment-class
    (SUPPORTED vs UNSUPPORTED, AMBIGUOUS, violated-constraint) in the
    calibration report output.'
    """

    def setUp(self) -> None:
        self.gold_set = _load_gold_set()
        self.report = run_calibration(self.gold_set, judge_fn=_perfect_judge())

    def test_report_has_per_class_block(self) -> None:
        # Report must surface a per_class section keyed by judgment-class.
        self.assertIn("per_class", self.report)
        per_class = self.report["per_class"]
        self.assertIsInstance(per_class, dict)

    def test_per_class_includes_four_judgment_classes(self) -> None:
        # Spec §7.7 enumerates SUPPORTED, UNSUPPORTED, AMBIGUOUS, and
        # violated-constraint as the four classes that must appear.
        per_class = self.report["per_class"]
        for cls in ("SUPPORTED", "UNSUPPORTED", "AMBIGUOUS", "violated_constraint"):
            self.assertIn(cls, per_class, f"per_class missing class {cls!r}")

    def test_each_class_exposes_fnr_and_fpr(self) -> None:
        # Per-class reporting must include both FNR and FPR (not just one).
        # Reviewer asymmetry — missing FPR on UNSUPPORTED was the
        # historical hole reviewer-calibration_mode_protocol referenced.
        per_class = self.report["per_class"]
        for cls, payload in per_class.items():
            self.assertIn("FNR", payload, f"class {cls!r} missing FNR")
            self.assertIn("FPR", payload, f"class {cls!r} missing FPR")

    def test_each_class_exposes_denominators(self) -> None:
        # Protocol doc Phase 4 contract: each class entry carries
        # n_positive + n_negative so 0.0 FNR on 0 positives is
        # distinguishable from 0.0 FNR on N positives. R1 codex P3 +
        # Gemini P3 closure — earlier test only asserted FNR/FPR keys.
        per_class = self.report["per_class"]
        for cls, payload in per_class.items():
            self.assertIn("n_positive", payload, f"class {cls!r} missing n_positive")
            self.assertIn("n_negative", payload, f"class {cls!r} missing n_negative")

    def test_canonical_denominators_match_gold_set(self) -> None:
        # Pin the expected one-vs-rest denominators against the canonical
        # 12-alignment + 8-constraint gold set. R1 codex P3 closure on
        # T-C2 contract pinning — without this a future gold-set
        # rebalance could silently shift class distributions away from
        # the documented Phase 4 example.
        per_class = self.report["per_class"]
        # Alignment gold set: 5 SUPPORTED + 3 UNSUPPORTED + 3 AMBIGUOUS
        # + 1 RETRIEVAL_FAILED; one-vs-rest counts the SUPPORTED-as-
        # positive case against the other 7 alignment tuples.
        self.assertEqual(per_class["SUPPORTED"]["n_positive"], 5)
        self.assertEqual(per_class["SUPPORTED"]["n_negative"], 7)
        self.assertEqual(per_class["UNSUPPORTED"]["n_positive"], 3)
        self.assertEqual(per_class["UNSUPPORTED"]["n_negative"], 9)
        self.assertEqual(per_class["AMBIGUOUS"]["n_positive"], 3)
        self.assertEqual(per_class["AMBIGUOUS"]["n_negative"], 9)
        # Constraint gold set: 5 VIOLATED + 3 NOT_VIOLATED.
        self.assertEqual(per_class["violated_constraint"]["n_positive"], 5)
        self.assertEqual(per_class["violated_constraint"]["n_negative"], 3)


# ---------------------------------------------------------------------------
# T-C1 — Threshold enforcement.
# ---------------------------------------------------------------------------


class TC1ThresholdEnforcement(unittest.TestCase):
    """T-C1 catches model/judge quality regression.

    Spec §7.7: 'FNR < 0.15 AND FPR < 0.10 against the synthetic gold set.
    Test FAILS when either threshold is exceeded. CI fails — author must
    either curate a better gold set, tighten judge prompts, or update
    judge_model.'

    The synthetic gold set is paired with a perfect-judge stub so the
    test exercises the threshold gate AND the calibration tooling
    end-to-end without requiring a live LLM call. Production deployment
    plugs a real judge_fn in place of the stub.
    """

    def setUp(self) -> None:
        self.gold_set = _load_gold_set()
        self.report = run_calibration(self.gold_set, judge_fn=_perfect_judge())

    def test_fnr_below_threshold(self) -> None:
        # Spec §7.7 gate: FNR < 0.15. Perfect-judge stub yields FNR = 0.
        self.assertLess(
            self.report["FNR"],
            0.15,
            f"FNR threshold violation: {self.report['FNR']!r} ≥ 0.15",
        )

    def test_fpr_below_threshold(self) -> None:
        # Spec §7.7 gate: FPR < 0.10. Perfect-judge stub yields FPR = 0.
        self.assertLess(
            self.report["FPR"],
            0.10,
            f"FPR threshold violation: {self.report['FPR']!r} ≥ 0.10",
        )

    def test_report_records_thresholds_used(self) -> None:
        # Operational concern: when CI fails on T-C1, the report MUST
        # surface the threshold values it was checked against so the
        # operator can distinguish a regression (judge degraded) from a
        # threshold tightening (spec bump). Spec §7.7 + §9 acceptance.
        self.assertEqual(self.report["thresholds"]["FNR"], 0.15)
        self.assertEqual(self.report["thresholds"]["FPR"], 0.10)


class TC1ThresholdEnforcementBadJudge(unittest.TestCase):
    """T-C1 companion — proves the threshold gate accurately fires on a
    degraded judge.

    R1 dual-track Gemini P1 / codex P2 closure: the canonical T-C1
    perfect-judge path only proves tooling CORRECTNESS (FNR/FPR
    computation works), not the threshold's ENFORCEABILITY (the gate
    fires when the judge degrades). Without this companion, T-C1 could
    silently pass on a future regression where the perfect-judge stub
    decoupled from the real judge_fn signature and the gate became
    structurally unreachable.

    The bad-judge stub flips every gold-set expected_label to its
    wrong-class counterpart so FNR + FPR both vastly exceed the spec
    §7.7 thresholds (0.15 / 0.10). The test asserts run_calibration's
    output is what an operator running CI on a degraded judge would
    see: FNR ≥ 0.15 AND FPR ≥ 0.10. Operational deployment swaps
    _bad_judge for a real judge_fn; the gate semantics are identical.
    """

    def setUp(self) -> None:
        self.gold_set = _load_gold_set()
        self.report = run_calibration(self.gold_set, judge_fn=_bad_judge())

    def test_bad_judge_drives_fnr_over_threshold(self) -> None:
        # Bad judge flips every alignment expected → opposite class +
        # every VIOLATED → NOT_VIOLATED. Aggregate FNR must be >= 0.15.
        self.assertGreaterEqual(
            self.report["FNR"],
            0.15,
            f"bad_judge should drive FNR over threshold; got {self.report['FNR']!r}",
        )

    def test_bad_judge_drives_fpr_over_threshold(self) -> None:
        # Same logic for FPR. The mirror-flip on alignment + the
        # NOT_VIOLATED → VIOLATED flip on constraints both contribute.
        self.assertGreaterEqual(
            self.report["FPR"],
            0.10,
            f"bad_judge should drive FPR over threshold; got {self.report['FPR']!r}",
        )

    def test_bad_judge_per_class_fnr_non_zero(self) -> None:
        # Per-class reporting must surface non-zero FNR on the flipped
        # classes — confirms the per_class accumulator is wired to the
        # judge output (not hardcoded zero) and would expose which
        # class drove a real-judge regression.
        per_class = self.report["per_class"]
        for cls in ("SUPPORTED", "UNSUPPORTED", "violated_constraint"):
            self.assertGreater(
                per_class[cls]["FNR"],
                0.0,
                f"bad-judge flip should drive non-zero FNR on {cls!r}; "
                f"got {per_class[cls]!r}",
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
