"""Audit-pipeline unit tests for v3.8 claim_ref_alignment_audit_agent (T-P1..T-P11).

Per spec §7.2 in
docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md.

These tests pin the contract of `scripts/claim_audit_pipeline.py`, the
Python module that implements the §4 Step 1-6 pipeline the agent prompt
narrates. Retrieval and judge are dependency-injected so tests can drive
every error path (paywall, audit_tool_failure, not_found, VIOLATED, etc.)
without touching the network or the on-disk cache.

Spec §7 names the test file `tests/test_claim_audit_pipeline.py`. Per
repo convention, tests live under `scripts/test_*.py` (CI uses
`python -m unittest scripts.test_*`); we keep the spec-named stem.

Run:
    python -m unittest scripts.test_claim_audit_pipeline -v
"""
from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any, Callable

try:
    from scripts.claim_audit_pipeline import run_audit_pipeline  # noqa: F401
    _MODULE_IMPORT_ERR: Exception | None = None
except Exception as exc:  # pragma: no cover — import-time error pathway is exercised in RED state
    _MODULE_IMPORT_ERR = exc

    def run_audit_pipeline(*args: Any, **kwargs: Any) -> Any:
        raise _MODULE_IMPORT_ERR  # type: ignore[misc]


MANIFEST_ID = "M-2026-05-15T10:00:00Z-a1b2"
AUDIT_RUN_ID = "2026-05-15T10:10:00Z-9f8e"
NOW = "2026-05-15T10:11:00Z"


def _manifest(
    *,
    claims: list[dict[str, Any]] | None = None,
    mncs: list[dict[str, str]] | None = None,
    manifest_id: str = MANIFEST_ID,
) -> dict[str, Any]:
    return {
        "manifest_version": "1.0",
        "manifest_id": manifest_id,
        "emitted_by": "synthesis_agent",
        "emitted_at": "2026-05-15T09:55:00Z",
        "claims": claims
        if claims is not None
        else [
            {
                "claim_id": "C-001",
                "claim_text": "Sample preprints accounted for 67% of corpus.",
                "intended_evidence_kind": "empirical",
                "planned_refs": ["smith2024preprints"],
            }
        ],
        "manifest_negative_constraints": mncs or [],
    }


def _citation(
    *,
    claim_id: str = "C-001",
    claim_text: str = "Sample preprints accounted for 67% of corpus.",
    ref_slug: str = "smith2024preprints",
    anchor_kind: str = "page",
    anchor_value: str = "12",
    section_path: str = "3. Results > 3.1 Overview",
    scoped_manifest_id: str = MANIFEST_ID,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "scoped_manifest_id": scoped_manifest_id,
        "claim_text": claim_text,
        "ref_slug": ref_slug,
        "anchor_kind": anchor_kind,
        "anchor_value": anchor_value,
        "section_path": section_path,
    }


def _config(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "max_claims_per_paper": 100,
        "judge_model": "gpt-5.5-xhigh",
        "gold_set_path": None,
        "cache_dir": None,  # Inject in-memory cache via run_audit_pipeline kwargs.
    }
    base.update(overrides)
    return base


def _retrieval_ok(
    *,
    excerpt: str = "The cited page reports the 67% figure verbatim.",
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    def fn(citation: dict[str, Any]) -> dict[str, Any]:
        return {
            "ref_retrieval_method": "api",
            "retrieved_excerpt": excerpt,
        }

    return fn


def _judge_supported() -> Callable[..., dict[str, Any]]:
    def fn(**kwargs: Any) -> dict[str, Any]:
        return {
            "judgment": "SUPPORTED",
            "rationale": "Cited page contains the 67% figure verbatim.",
        }

    return fn


def _judge_unsupported(*, defect_stage: str = "source_description") -> Callable[..., dict[str, Any]]:
    def fn(**kwargs: Any) -> dict[str, Any]:
        return {
            "judgment": "UNSUPPORTED",
            "rationale": f"Source describes a different population than the claim asserts.",
            "defect_stage_hint": defect_stage,
        }

    return fn


def _judge_violated(*, violated_constraint_id: str) -> Callable[..., dict[str, Any]]:
    def fn(**kwargs: Any) -> dict[str, Any]:
        return {
            "judgment": "VIOLATED",
            "violated_constraint_id": violated_constraint_id,
            "rationale": "Constraint forbids unqualified causal language.",
        }

    return fn


class _PipelineTestBase(unittest.TestCase):
    """Skip the entire pipeline suite cleanly when the module is missing.

    During the RED phase (Step 4 of the TDD plan in spec §13), the module
    `scripts/claim_audit_pipeline.py` does not exist yet — these tests
    document the wished-for API. Once Step 5 lands the module, they will
    flip from skipped (RED-as-skip) to executed pass/fail.
    """

    @classmethod
    def setUpClass(cls) -> None:
        if _MODULE_IMPORT_ERR is not None:
            raise unittest.SkipTest(
                f"scripts.claim_audit_pipeline not importable yet: {_MODULE_IMPORT_ERR!r} "
                "(expected during RED phase — implementation lands in spec §13 step 5)"
            )

    def run_pipeline(self, **kwargs: Any) -> dict[str, list[dict[str, Any]]]:
        defaults: dict[str, Any] = {
            "manifests": [_manifest()],
            "corpus": [],
            "config": _config(),
            "audit_run_id": AUDIT_RUN_ID,
            "now_iso": NOW,
            "retrieve_fn": _retrieval_ok(),
            "judge_fn": _judge_supported(),
        }
        defaults.update(kwargs)
        return run_audit_pipeline(**defaults)


# ---------------------------------------------------------------------------
# T-P1 — Step 1 anchor=none short-circuit.
# ---------------------------------------------------------------------------


class TP1AnchorNoneShortCircuit(_PipelineTestBase):
    """T-P1: anchor=none input emits the canonical RETRIEVAL_FAILED triple and skips the judge."""

    def test_anchor_none_skips_judge(self) -> None:
        invocations: list[Any] = []

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            invocations.append(kwargs)
            return {"judgment": "SUPPORTED", "rationale": "should not be called"}

        out = self.run_pipeline(
            citations=[_citation(anchor_kind="none", anchor_value="")],
            judge_fn=judge_fn,
        )
        self.assertEqual(invocations, [], "judge MUST NOT be invoked for anchor=none rows")
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1)
        e = results[0]
        self.assertEqual(e["judgment"], "RETRIEVAL_FAILED")
        self.assertEqual(e["audit_status"], "inconclusive")
        self.assertEqual(e["defect_stage"], "not_applicable")
        self.assertEqual(e["ref_retrieval_method"], "not_attempted")
        self.assertTrue(
            e["rationale"].startswith("v3.7.3 R-L3-1-A violation"),
            f"rationale must start with INV-6 firm-rule prefix; got {e['rationale']!r}",
        )


# ---------------------------------------------------------------------------
# T-P2 / T-P3 — Step 3 cache hit / miss.
# ---------------------------------------------------------------------------


class TP2P3CacheBehavior(_PipelineTestBase):
    """T-P2/T-P3: cache keyed by (claim, ref, anchor, retrieved_excerpt_hash, constraint_set, judge_model)."""

    def test_p2_cache_hit_skips_judge(self) -> None:
        cache: dict[str, Any] = {}
        invocations: list[Any] = []

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            invocations.append(kwargs)
            return {"judgment": "SUPPORTED", "rationale": "judge ran"}

        # First run populates the cache.
        self.run_pipeline(
            citations=[_citation()],
            judge_fn=judge_fn,
            cache=cache,
        )
        self.assertEqual(len(invocations), 1, "first run must invoke judge")

        # Second run with same inputs MUST hit cache.
        self.run_pipeline(
            citations=[_citation()],
            judge_fn=judge_fn,
            cache=cache,
        )
        self.assertEqual(len(invocations), 1, "second run with identical inputs must NOT re-invoke judge")

    def test_p3_cache_miss_after_manual_pdf_uploaded(self) -> None:
        cache: dict[str, Any] = {}
        invocations: list[Any] = []

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            invocations.append(kwargs)
            return {"judgment": "SUPPORTED", "rationale": "judge ran"}

        # First run with API retrieval.
        self.run_pipeline(
            citations=[_citation()],
            judge_fn=judge_fn,
            retrieve_fn=_retrieval_ok(excerpt="api-served excerpt"),
            cache=cache,
        )
        # Second run with manual_pdf uploading a different excerpt -> retrieved_excerpt_hash changes
        # -> cache MUST miss and re-invoke the judge.

        def manual_pdf_retrieval(citation: dict[str, Any]) -> dict[str, Any]:
            return {
                "ref_retrieval_method": "manual_pdf",
                "retrieved_excerpt": "different excerpt from manual PDF upload",
            }

        self.run_pipeline(
            citations=[_citation()],
            judge_fn=judge_fn,
            retrieve_fn=manual_pdf_retrieval,
            cache=cache,
        )
        self.assertEqual(
            len(invocations),
            2,
            "manual PDF excerpt with different hash MUST force a fresh judge invocation",
        )


# ---------------------------------------------------------------------------
# T-P4 — Step 2 ref_retrieval_method=failed → LOW-WARN paywall path.
# ---------------------------------------------------------------------------


class TP4FailedRetrievalPaywall(_PipelineTestBase):
    """T-P4: paywall path produces (RETRIEVAL_FAILED, inconclusive, not_applicable, failed)."""

    def test_paywall_triple(self) -> None:
        def paywall(citation: dict[str, Any]) -> dict[str, Any]:
            return {"ref_retrieval_method": "failed", "retrieved_excerpt": None}

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            raise AssertionError("judge MUST NOT be called on paywall path")

        out = self.run_pipeline(
            citations=[_citation()],
            retrieve_fn=paywall,
            judge_fn=judge_fn,
        )
        self.assertEqual(len(out["claim_audit_results"]), 1)
        e = out["claim_audit_results"][0]
        self.assertEqual(e["judgment"], "RETRIEVAL_FAILED")
        self.assertEqual(e["audit_status"], "inconclusive")
        self.assertEqual(e["defect_stage"], "not_applicable")
        self.assertEqual(e["ref_retrieval_method"], "failed")


# ---------------------------------------------------------------------------
# T-P5 — Step 2 manual_pdf accepted; not_found triggers retrieval_existence.
# ---------------------------------------------------------------------------


class TP5RetrievalPathways(_PipelineTestBase):
    """T-P5: manual_pdf accepted; not_found triggers defect_stage=retrieval_existence."""

    def test_manual_pdf_accepted(self) -> None:
        def manual_pdf(citation: dict[str, Any]) -> dict[str, Any]:
            return {"ref_retrieval_method": "manual_pdf", "retrieved_excerpt": "user-uploaded excerpt"}

        out = self.run_pipeline(citations=[_citation()], retrieve_fn=manual_pdf)
        e = out["claim_audit_results"][0]
        self.assertEqual(e["ref_retrieval_method"], "manual_pdf")
        self.assertEqual(e["judgment"], "SUPPORTED")

    def test_not_found_triggers_retrieval_existence(self) -> None:
        def not_found(citation: dict[str, Any]) -> dict[str, Any]:
            return {"ref_retrieval_method": "not_found", "retrieved_excerpt": None}

        out = self.run_pipeline(citations=[_citation()], retrieve_fn=not_found)
        e = out["claim_audit_results"][0]
        self.assertEqual(e["judgment"], "RETRIEVAL_FAILED")
        self.assertEqual(e["audit_status"], "completed")
        self.assertEqual(e["defect_stage"], "retrieval_existence")
        self.assertEqual(e["ref_retrieval_method"], "not_found")


# ---------------------------------------------------------------------------
# T-P6 — Step 5 judge VIOLATED routes to negative_constraint_violation.
# ---------------------------------------------------------------------------


class TP6ConstraintViolation(_PipelineTestBase):
    """T-P6: cited claim with VIOLATED judge verdict emits claim_audit_result with negative_constraint_violation."""

    def test_violated_routes_to_claim_audit_result(self) -> None:
        manifest = _manifest(
            mncs=[{"constraint_id": "MNC-1", "rule": "No causal language without RCT."}],
        )
        out = self.run_pipeline(
            citations=[_citation()],
            manifests=[manifest],
            judge_fn=_judge_violated(violated_constraint_id="MNC-1"),
        )
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1)
        e = results[0]
        self.assertEqual(e["judgment"], "UNSUPPORTED")
        self.assertEqual(e["defect_stage"], "negative_constraint_violation")
        self.assertEqual(e["violated_constraint_id"], "MNC-1")
        self.assertEqual(out["constraint_violations"], [], "cited violation MUST emit into claim_audit_results, not constraint_violations")


# ---------------------------------------------------------------------------
# T-P7 — Step 6 defect_stage classification fixtures.
# ---------------------------------------------------------------------------


class TP7DefectStageClassification(_PipelineTestBase):
    """T-P7: each of 6 substantive defect_stages has a fixture mapping."""

    DEFECT_STAGES_TO_TEST = [
        ("retrieval_existence", "not_found"),
        ("metadata", "api"),
        ("source_description", "api"),
        ("citation_anchor", "api"),
        ("synthesis_overclaim", "api"),
        ("negative_constraint_violation", "api"),
    ]

    def test_each_defect_stage_mappable(self) -> None:
        for defect_stage, method in self.DEFECT_STAGES_TO_TEST:
            with self.subTest(defect_stage=defect_stage):
                # Each defect_stage corresponds to a distinct pipeline path; we
                # exercise the dispatch by configuring retrieval + judge to that
                # combination, then assert the emitted entry carries the right
                # defect_stage tag.
                if defect_stage == "retrieval_existence":
                    out = self.run_pipeline(
                        citations=[_citation()],
                        retrieve_fn=lambda c: {"ref_retrieval_method": "not_found", "retrieved_excerpt": None},
                    )
                elif defect_stage == "negative_constraint_violation":
                    manifest = _manifest(
                        mncs=[{"constraint_id": "MNC-1", "rule": "Rule."}],
                    )
                    out = self.run_pipeline(
                        citations=[_citation()],
                        manifests=[manifest],
                        judge_fn=_judge_violated(violated_constraint_id="MNC-1"),
                    )
                else:
                    out = self.run_pipeline(
                        citations=[_citation()],
                        judge_fn=_judge_unsupported(defect_stage=defect_stage),
                    )
                results = out["claim_audit_results"]
                self.assertEqual(len(results), 1, msg=f"expected 1 row for {defect_stage}")
                self.assertEqual(results[0]["defect_stage"], defect_stage)


# ---------------------------------------------------------------------------
# T-P8 — Precedence rule 1: drift + constraint violation → constraint absorbs drift.
# ---------------------------------------------------------------------------


class TP8DriftConstraintPrecedence(_PipelineTestBase):
    """T-P8: a claim that drifts AND violates a constraint emits only the constraint_audit_result row."""

    def test_constraint_absorbs_drift(self) -> None:
        # Manifest mentions one claim; the prose drifts AND violates.
        manifest = _manifest(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Sample preprints accounted for 67% of corpus.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
            ],
            mncs=[{"constraint_id": "MNC-1", "rule": "Rule."}],
        )
        # The emitted citation is for a different claim_text (drifted) AND triggers VIOLATED.
        drifted_cite = _citation(
            claim_id="C-002",  # not in manifest
            claim_text="We observed causality between A and B.",
        )
        out = self.run_pipeline(
            citations=[drifted_cite],
            manifests=[manifest],
            judge_fn=_judge_violated(violated_constraint_id="MNC-1"),
        )
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1, "must emit claim_audit_result")
        self.assertEqual(results[0]["defect_stage"], "negative_constraint_violation")
        drifts = out["claim_drifts"]
        self.assertEqual(
            drifts,
            [],
            "constraint violation MUST absorb drift signal — no companion claim_drifts[] entry per T-P8",
        )


# ---------------------------------------------------------------------------
# T-P9 — Precedence rule 2: citation_anchor distinct from source_description.
# ---------------------------------------------------------------------------


class TP9AnchorVsDescription(_PipelineTestBase):
    """T-P9: anchor-wrong + description-correct => defect_stage=citation_anchor (not source_description)."""

    def test_anchor_wrong_description_correct(self) -> None:
        out = self.run_pipeline(
            citations=[_citation()],
            judge_fn=_judge_unsupported(defect_stage="citation_anchor"),
        )
        e = out["claim_audit_results"][0]
        self.assertEqual(e["defect_stage"], "citation_anchor")
        self.assertNotEqual(e["defect_stage"], "source_description")


# ---------------------------------------------------------------------------
# T-P10 — Precedence rule 3: uncited + manifest-claim sentence => uncited_assertion only.
# ---------------------------------------------------------------------------


class TP10UncitedOverDrift(_PipelineTestBase):
    """T-P10: a sentence that is BOTH uncited AND a drifted manifest claim emits only uncited_assertions[]."""

    def test_uncited_takes_precedence_over_drift(self) -> None:
        manifest = _manifest()
        # The emitted draft contains an uncited sentence (no ref) AND it differs from manifest -> drift.
        uncited_sentences = [
            {
                "sentence_text": "Half of all submissions showed positive results.",
                "section_path": "3. Results",
                "manifest_claim_id": None,
            }
        ]
        out = self.run_pipeline(
            citations=[],  # no citation -> no claim_audit_result row
            manifests=[manifest],
            uncited_sentences=uncited_sentences,
        )
        self.assertEqual(out["claim_audit_results"], [], "uncited sentence has no ref -> no claim_audit_result row")
        self.assertEqual(len(out["uncited_assertions"]), 1, "uncited entry MUST emit")
        # Sentence is not in manifest, and a companion claim_drifts[] entry would
        # also be a natural drift signal — but precedence rule 3 forbids the drift
        # row when uncited fires for the same sentence.
        same_text_drift = [d for d in out["claim_drifts"] if d.get("claim_text") == uncited_sentences[0]["sentence_text"]]
        self.assertEqual(
            same_text_drift,
            [],
            "no companion claim_drifts[] entry for the same sentence per T-P10 / D-INV-4",
        )


# ---------------------------------------------------------------------------
# T-P11 — Cap sampling behavior.
# ---------------------------------------------------------------------------


class TP11CapSampling(_PipelineTestBase):
    """T-P11: N>cap emits stratified summary; N<=cap emits no summary OR telemetry summary; cap=0 rejected."""

    def test_large_n_emits_stratified_summary(self) -> None:
        # 150 citations, cap=100 -> exactly 1 sampling summary, audited_count=100.
        citations = [
            _citation(
                claim_id=f"C-{i:03d}",
                ref_slug=f"ref-{i:03d}",
                scoped_manifest_id=MANIFEST_ID,
            )
            for i in range(1, 151)
        ]
        # Manifest carries 150 claims to satisfy INV-15 cross-array integrity.
        big_manifest = _manifest(
            claims=[
                {
                    "claim_id": f"C-{i:03d}",
                    "claim_text": f"Claim {i}.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
                for i in range(1, 151)
            ],
        )
        out = self.run_pipeline(
            citations=citations,
            manifests=[big_manifest],
            config=_config(max_claims_per_paper=100),
        )
        samplings = out["audit_sampling_summaries"]
        self.assertEqual(len(samplings), 1)
        s = samplings[0]
        self.assertEqual(s["audited_count"], 100)
        self.assertEqual(s["total_citation_count"], 150)
        self.assertEqual(s["max_claims_per_paper"], 100)
        self.assertEqual(s["sampling_strategy"], "stratified_buckets_v1")
        indices = s["audited_indices"]
        self.assertEqual(len(indices), 100)
        self.assertEqual(sorted(set(indices)), indices, "audited_indices strictly ascending and unique")

    def test_small_n_no_summary_or_telemetry(self) -> None:
        # 50 citations, cap=100 -> no summary OR summary with audited_count == total.
        citations = [_citation(claim_id=f"C-{i:03d}", ref_slug=f"ref-{i:03d}") for i in range(1, 51)]
        manifest = _manifest(
            claims=[
                {
                    "claim_id": f"C-{i:03d}",
                    "claim_text": f"Claim {i}.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
                for i in range(1, 51)
            ],
        )
        out = self.run_pipeline(citations=citations, manifests=[manifest], config=_config(max_claims_per_paper=100))
        samplings = out["audit_sampling_summaries"]
        # Two valid outcomes per spec §4 step 3: zero summaries OR exactly one
        # telemetry-mode summary where audited_count == total_citation_count.
        if samplings:
            self.assertEqual(len(samplings), 1)
            self.assertEqual(samplings[0]["audited_count"], 50)
            self.assertEqual(samplings[0]["total_citation_count"], 50)

    def test_cap_zero_rejected(self) -> None:
        with self.assertRaises((ValueError, AssertionError)):
            self.run_pipeline(
                citations=[_citation()],
                config=_config(max_claims_per_paper=0),
            )


if __name__ == "__main__":
    unittest.main()
