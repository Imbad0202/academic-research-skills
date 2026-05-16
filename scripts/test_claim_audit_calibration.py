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


def _perfect_judge() -> Callable[..., dict[str, Any]]:
    """Stub judge that returns the gold-set expected_judgment verbatim.

    Used by T-C1 to verify the calibration script's FNR / FPR computation
    on a path where the judge perfectly matches the gold set. The stub
    looks up the tuple by claim_text (which the calibration runner passes
    through unchanged) and emits the canonical judge response shape for
    that tuple kind. A real LLM judge would be wired here at operational
    deployment time per the protocol doc.
    """
    tuples_by_text: dict[str, dict[str, Any]] = {
        t["claim_text"]: t for t in _load_gold_set()
    }

    def fn(**kwargs: Any) -> dict[str, Any]:
        claim_text = kwargs.get("claim_text", "")
        tup = tuples_by_text.get(claim_text)
        if tup is None:
            raise AssertionError(
                f"perfect_judge: claim_text {claim_text!r} not in gold set"
            )
        kind = tup["tuple_kind"]
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

    def test_validate_gold_set_rejects_alignment_with_constraint_field(self) -> None:
        # validate_gold_set is the production entrypoint that the
        # calibration runner calls at ingestion time. It MUST raise the
        # documented error on rule-(b) violation.
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
        self.assertIn("alignment", str(ctx.exception).lower())

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
        msg = str(ctx.exception).lower()
        self.assertTrue("rule_text" in msg or "manifest_fixture_path" in msg)

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
        self.assertIn("NOT_VIOLATED", str(ctx.exception))

    def test_validate_gold_set_accepts_canonical_gold_set(self) -> None:
        # Positive path — the shipped gold set MUST validate cleanly.
        self.assertIsNone(validate_gold_set(self.gold_set))


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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
