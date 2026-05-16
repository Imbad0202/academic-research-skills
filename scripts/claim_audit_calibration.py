"""Calibration runner for v3.8 claim_ref_alignment_audit_agent.

This module is the operational entrypoint that the agent prompt at
`academic-pipeline/agents/claim_ref_alignment_audit_agent.md` Step 8
narrates and that `academic-pipeline/references/claim_audit_calibration_protocol.md`
documents. It accepts a gold set (alignment + constraint tuples) plus a
caller-supplied `judge_fn` and emits a calibration report containing
FNR / FPR aggregates, per-judgment-class FNR / FPR, and the threshold
values used to gate the run.

Test contract is pinned by `scripts/test_claim_audit_calibration.py`
(T-C1 / T-C2 / T-C3 per spec §7.7). The default thresholds reflect the
spec §7.7 + §9 acceptance criteria — FNR < 0.15 AND FPR < 0.10.

Spec: docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md
      §7.7 (test contract) + §1 deliverable 7 (protocol doc) + §13 step 10.
"""
from __future__ import annotations

import re
from typing import Any, Callable

# Constraint id shape per spec §3.2 canonical parse rule (RE_NC_CONSTRAINT
# + RE_MNC_CONSTRAINT in scripts/_claim_audit_constants.py).
#
# MNC-N is the manifest-level negative constraint (broadest scope);
# NC-CN-M is the per-claim narrow constraint binding claim N constraint M.
# Claim ids are zero-padded to ≥3 digits, so NC-C[0-9]{3,}-[0-9]+ is the
# canonical NC shape — accepting NC-C1-1 (R1 codex residual P2) would
# silently violate the production lint that runs against emitted rows.
_RE_MNC_ID = re.compile(r"^MNC-[0-9]+$")
_RE_NC_ID = re.compile(r"^NC-C[0-9]{3,}-[0-9]+$")

# Spec §7.7 + §9 acceptance gates. Tightening these is a spec bump.
DEFAULT_FNR_THRESHOLD = 0.15
DEFAULT_FPR_THRESHOLD = 0.10

# Closed enums from the schema (claim_audit_result.judgment + the
# negative-constraint VIOLATED/NOT_VIOLATED split). Kept in sync with
# `shared/contracts/passport/claim_audit_result.schema.json`.
ALIGNMENT_JUDGMENTS = frozenset(
    {"SUPPORTED", "UNSUPPORTED", "AMBIGUOUS", "RETRIEVAL_FAILED"}
)
CONSTRAINT_JUDGMENTS = frozenset({"VIOLATED", "NOT_VIOLATED"})
TUPLE_KINDS = frozenset({"alignment", "constraint"})

# Per-class report keys (T-C2). The alignment-class names mirror the
# judgment enum; constraint reporting collapses VIOLATED/NOT_VIOLATED into
# a single `violated_constraint` axis because the binary positive class
# for a constraint test is "VIOLATED".
PER_CLASS_KEYS = ("SUPPORTED", "UNSUPPORTED", "AMBIGUOUS", "violated_constraint")

# Constraint-tuple required fields per spec §7.7 rule (c). Either rule
# text inline OR a manifest-fixture path resolving to a manifest carrying
# the rule — silent-skip regression hardening.
_CONSTRAINT_REQUIRED_EITHER = ("constraint_under_test_rule_text", "manifest_fixture_path")
# Fields that alignment tuples MUST NOT carry (rule (b)).
_ALIGNMENT_FORBIDDEN = (
    "constraint_under_test_id",
    "constraint_under_test_rule_text",
    "manifest_fixture_path",
)


class GoldSetValidationError(ValueError):
    """Raised when validate_gold_set rejects a tuple at ingestion time.

    The diagnostic always names the rule that failed (a / b / c / d per
    spec §7.7) and the offending tuple index so calibration-fixture
    authoring bugs surface loudly. Catching this exception in production
    is a contract violation — fix the gold set, do not swallow the error.
    """


def validate_gold_set(tuples: list[dict[str, Any]]) -> None:
    """Validate the gold set per spec §7.7 rules (a)..(d).

    Raises GoldSetValidationError on the first failed rule. Returns None
    on success so the call site can ignore the return value — the
    function's contract is exceptional, not value-returning.
    """
    not_violated_constraint_count = 0
    for idx, tup in enumerate(tuples):
        kind = tup.get("tuple_kind")
        if kind not in TUPLE_KINDS:
            raise GoldSetValidationError(
                f"tuple {idx}: invalid tuple_kind {kind!r} "
                f"(rule (a); must be one of {sorted(TUPLE_KINDS)})"
            )
        expected = tup.get("expected_judgment")
        if kind == "alignment":
            if expected not in ALIGNMENT_JUDGMENTS:
                raise GoldSetValidationError(
                    f"tuple {idx}: alignment tuple has invalid "
                    f"expected_judgment {expected!r} "
                    f"(rule (b); must be one of {sorted(ALIGNMENT_JUDGMENTS)})"
                )
            for forbidden in _ALIGNMENT_FORBIDDEN:
                if forbidden in tup:
                    raise GoldSetValidationError(
                        f"tuple {idx}: alignment tuple must not carry "
                        f"constraint field {forbidden!r} (rule (b))"
                    )
        else:  # constraint
            if expected not in CONSTRAINT_JUDGMENTS:
                raise GoldSetValidationError(
                    f"tuple {idx}: constraint tuple has invalid "
                    f"expected_judgment {expected!r} "
                    f"(rule (c); must be one of {sorted(CONSTRAINT_JUDGMENTS)})"
                )
            if "constraint_under_test_id" not in tup:
                raise GoldSetValidationError(
                    f"tuple {idx}: constraint tuple missing "
                    f"constraint_under_test_id (rule (c))"
                )
            if not any(tup.get(field) for field in _CONSTRAINT_REQUIRED_EITHER):
                raise GoldSetValidationError(
                    f"tuple {idx}: constraint tuple missing both "
                    f"constraint_under_test_rule_text and manifest_fixture_path "
                    f"(rule (c); at least one required so the judge has a rule to evaluate)"
                )
            if expected == "NOT_VIOLATED":
                not_violated_constraint_count += 1
    if not_violated_constraint_count < 3:
        raise GoldSetValidationError(
            f"gold set has only {not_violated_constraint_count} NOT_VIOLATED "
            f"constraint tuple(s); rule (d) requires ≥3 so constraint FPR is "
            f"measurable and T-C1 can fail-on-threshold for the constraint line"
        )


def _resolve_constraint_rule_text(tup: dict[str, Any]) -> str:
    """Resolve a constraint tuple's rule text to the literal the judge receives.

    R2 codex P1 closure: prior implementation passed
    `tup.get("constraint_under_test_rule_text", "")` directly to the judge,
    which meant a spec-valid manifest-only tuple (rule (c) accepts EITHER
    inline rule_text OR manifest_fixture_path) silently reached the judge
    with `rule=""` — the exact silent-skip authoring bug T-C3 was supposed
    to prevent.

    The v3.8.0 calibration runner supports inline rule_text only. Manifest-
    resolver wiring is post-v3.8 (tracked by the protocol doc's "Resolved
    design decisions" section). Until that ships, a manifest-only tuple
    must fail loudly at run time, not pass quietly with an empty rule.
    """
    inline_rule = tup.get("constraint_under_test_rule_text")
    if inline_rule:
        return inline_rule
    manifest_path = tup.get("manifest_fixture_path")
    if manifest_path:
        raise NotImplementedError(
            f"constraint tuple references manifest_fixture_path={manifest_path!r} "
            "but the v3.8.0 calibration runner does not yet resolve manifest "
            "fixtures into rule text. Author the tuple with an inline "
            "constraint_under_test_rule_text, or wait for the manifest resolver "
            "(post-v3.8). validate_gold_set accepts both forms per spec §7.7 "
            "rule (c), but the runner only supports the inline form today."
        )
    # Both inline and manifest_path are absent → validate_gold_set should have
    # caught this. Defense-in-depth: surface as a logic error, not silent "".
    raise GoldSetValidationError(
        f"constraint tuple {tup.get('constraint_under_test_id')!r} reached "
        "run_calibration with neither inline rule_text nor manifest_fixture_path; "
        "validate_gold_set should have rejected this at ingestion (rule (c))"
    )


def _derive_constraint_scope(constraint_id: str) -> str:
    """Derive the active-constraint scope tag from a constraint_id literal.

    R1 codex P2-b + Gemini P3 closure: prior implementation used a bare
    `startswith("MNC-")` fallback that mislabelled leading-whitespace
    ids ("  MNC-1" → NC) and would silently accept malformed prefixes
    ("bogus" → NC). The judge stub never read scope so the bug was
    invisible at the canonical T-C1 path; a real judge that branches
    on scope would receive the wrong tag.

    The function rejects malformed ids with a diagnostic naming the
    expected patterns. Spec §3.2 + protocol doc gold-tuple schema are
    the source of truth; this regex pair mirrors them.
    """
    if not isinstance(constraint_id, str):
        raise GoldSetValidationError(
            f"constraint_under_test_id must be str; got {type(constraint_id).__name__}"
        )
    if _RE_MNC_ID.match(constraint_id):
        return "MNC"
    if _RE_NC_ID.match(constraint_id):
        return "NC"
    raise GoldSetValidationError(
        f"constraint_under_test_id {constraint_id!r} does not match "
        f"expected shape (MNC-N or NC-CN-M per spec §3.2)"
    )


def _zero_division_safe(numerator: int, denominator: int) -> float:
    """Return rate with `nan` semantics for empty denominators.

    A class with zero positive ground-truth examples has undefined FNR;
    the report records 0.0 with denominator=0 so downstream consumers can
    distinguish "perfect score on no examples" from "perfect score on
    some examples". Spec §7.7 rule (d) is the authoring guard that keeps
    constraint FPR measurable; this is the fallback for the alignment
    classes where rule (d) doesn't apply (e.g., RETRIEVAL_FAILED has
    only one tuple in the canonical fixture).
    """
    if denominator == 0:
        return 0.0
    return numerator / denominator


def run_calibration(
    gold_set: list[dict[str, Any]],
    *,
    judge_fn: Callable[..., dict[str, Any]],
    thresholds: dict[str, float] | None = None,
) -> dict[str, Any]:
    """Drive the gold set through the judge_fn and emit a calibration report.

    Args:
        gold_set: list of tuples per spec §7.7 schema. Will be validated
            via `validate_gold_set` before any judge call — invalid sets
            raise GoldSetValidationError instead of producing a
            silently-wrong report.
        judge_fn: callable matching the v3.8 judge interface
            (`claim_text`, `retrieved_excerpt`, `anchor_kind`,
            `anchor_value`, `active_constraints`, `judge_model` kwargs).
            For alignment tuples the runner passes the tuple's
            `ref_text_excerpt` as `retrieved_excerpt`; for constraint
            tuples it passes the inline rule_text wrapped in the
            v3.8 active_constraints shape.
        thresholds: optional dict overriding {"FNR": ..., "FPR": ...}.
            Spec §7.7 defaults are 0.15 / 0.10.

    Returns:
        Dict with keys:
            - FNR, FPR — aggregate rates across all tuples
            - per_class — {SUPPORTED/UNSUPPORTED/AMBIGUOUS/violated_constraint:
                            {FNR, FPR, n_positive, n_negative}}
            - thresholds — the active gate values (echoed for surfacing)
            - n_total — gold set size
            - n_alignment / n_constraint — split counts
    """
    validate_gold_set(gold_set)
    if thresholds is None:
        thresholds = {"FNR": DEFAULT_FNR_THRESHOLD, "FPR": DEFAULT_FPR_THRESHOLD}

    # Aggregate counts. Confusion-matrix vocabulary:
    #   - positive class = "the tuple's expected_judgment"
    #   - FN = expected was X, judge said not-X
    #   - FP = expected was not-X, judge said X
    # For per-class reporting we collapse the multi-class problem to
    # one-vs-rest binary, which is the standard reviewer-calibration
    # convention referenced in `calibration_mode_protocol.md`.
    per_class_stats: dict[str, dict[str, int]] = {
        cls: {"FN": 0, "FP": 0, "n_positive": 0, "n_negative": 0}
        for cls in PER_CLASS_KEYS
    }
    aggregate_FN = 0
    aggregate_FP = 0
    aggregate_n_positive = 0
    aggregate_n_negative = 0

    n_alignment = 0
    n_constraint = 0

    for tup in gold_set:
        kind = tup["tuple_kind"]
        expected = tup["expected_judgment"]
        if kind == "alignment":
            n_alignment += 1
            response = judge_fn(
                claim_text=tup["claim_text"],
                retrieved_excerpt=tup.get("ref_text_excerpt"),
                anchor_kind=tup.get("anchor", {}).get("kind"),
                anchor_value=tup.get("anchor", {}).get("value"),
                active_constraints=[],
                judge_model="calibration-stub",
            )
            actual = response["judgment"]
            # For each alignment one-vs-rest class in PER_CLASS_KEYS,
            # check whether this tuple contributes a TP / FN / FP / TN.
            for cls in ("SUPPORTED", "UNSUPPORTED", "AMBIGUOUS"):
                _accumulate_one_vs_rest(
                    per_class_stats[cls],
                    positive_class=cls,
                    expected_label=expected,
                    actual_label=actual,
                )
            # Aggregate (multi-class) FN/FP across alignment tuples.
            if expected != actual:
                aggregate_FN += 1  # missed the expected class
                aggregate_FP += 1  # picked the wrong class
            aggregate_n_positive += 1
            aggregate_n_negative += 1
        else:  # constraint
            n_constraint += 1
            constraint_id = tup["constraint_under_test_id"]
            scope = _derive_constraint_scope(constraint_id)
            rule_text = _resolve_constraint_rule_text(tup)
            response = judge_fn(
                claim_text=tup["claim_text"],
                retrieved_excerpt=tup.get("ref_text_excerpt"),
                anchor_kind=tup.get("anchor", {}).get("kind"),
                anchor_value=tup.get("anchor", {}).get("value"),
                active_constraints=[
                    {
                        "constraint_id": constraint_id,
                        "rule": rule_text,
                        "scope": scope,
                    }
                ],
                judge_model="calibration-stub",
            )
            actual = response["judgment"]
            _accumulate_one_vs_rest(
                per_class_stats["violated_constraint"],
                positive_class="VIOLATED",
                expected_label=expected,
                actual_label=actual,
            )
            # Aggregate matrix for constraint tuples uses VIOLATED as
            # the positive class — that's the gate-refuse signal.
            # /simplify quality Q-P2-a closure: collapse the if/elif
            # ladder into two ground-truth branches so an unexpected
            # judge label (e.g. RETRIEVAL_FAILED on a constraint tuple)
            # still counts toward the denominator. Without this fallback
            # an unknown label silently dropped from aggregate counts
            # while per-class still counted it correctly — a measurable-
            # but-invisible reporting divergence.
            if expected == "VIOLATED":
                aggregate_n_positive += 1
                if actual != "VIOLATED":
                    aggregate_FN += 1
            else:  # expected == "NOT_VIOLATED"
                aggregate_n_negative += 1
                if actual == "VIOLATED":
                    aggregate_FP += 1

    per_class_report: dict[str, dict[str, float | int]] = {}
    for cls, stats in per_class_stats.items():
        per_class_report[cls] = {
            "FNR": _zero_division_safe(stats["FN"], stats["n_positive"]),
            "FPR": _zero_division_safe(stats["FP"], stats["n_negative"]),
            "n_positive": stats["n_positive"],
            "n_negative": stats["n_negative"],
        }

    return {
        "FNR": _zero_division_safe(aggregate_FN, aggregate_n_positive),
        "FPR": _zero_division_safe(aggregate_FP, aggregate_n_negative),
        "per_class": per_class_report,
        "thresholds": thresholds,
        "n_total": len(gold_set),
        "n_alignment": n_alignment,
        "n_constraint": n_constraint,
    }


def _accumulate_one_vs_rest(
    stats: dict[str, int],
    *,
    positive_class: str,
    expected_label: str,
    actual_label: str,
) -> None:
    """Update a per-class confusion table for one-vs-rest binary metrics.

    `positive_class` names the label that counts as positive for this
    bucket (the per_class_stats key IS the positive class). The four
    conditions:

    | expected_label == positive | actual_label == positive | bucket |
    |---|---|---|
    | yes | yes | TP (n_positive++) |
    | yes | no  | FN (n_positive++, FN++) |
    | no  | yes | FP (n_negative++, FP++) |
    | no  | no  | TN (n_negative++) |
    """
    is_positive_truth = expected_label == positive_class
    is_positive_pred = actual_label == positive_class
    if is_positive_truth:
        stats["n_positive"] += 1
        if not is_positive_pred:
            stats["FN"] += 1
    else:
        stats["n_negative"] += 1
        if is_positive_pred:
            stats["FP"] += 1


__all__ = [
    "DEFAULT_FNR_THRESHOLD",
    "DEFAULT_FPR_THRESHOLD",
    "GoldSetValidationError",
    "run_calibration",
    "validate_gold_set",
]
