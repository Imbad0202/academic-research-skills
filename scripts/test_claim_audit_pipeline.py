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

    def test_anchor_none_pins_empty_sentinel_anchor_value(self) -> None:
        # INV-6 sentinel: even if the caller passes a stale residual anchor_value
        # on an anchor_kind=none citation, the pipeline MUST coerce it to the
        # empty string per the schema contract (Step 13 R1 Gemini finding).
        out = self.run_pipeline(
            citations=[_citation(anchor_kind="none", anchor_value="123")],
            judge_fn=lambda **_kw: {"judgment": "SUPPORTED", "rationale": "n/a"},
        )
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0]["anchor_value"],
            "",
            "anchor_kind=none rows must carry the empty sentinel anchor_value per INV-6",
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
                # Detector-supplied per the v3.8 Step 6 contract: callers
                # must pre-process raw sentences through
                # detect_uncited_assertions (or surface explicit
                # trigger_tokens). _uncited_assertion_entry raises if both
                # the keyword arg and this field are missing.
                "trigger_tokens": ["showed"],
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


# ---------------------------------------------------------------------------
# T-P12 — Judge invocation failure mapping to INV-14 audit_tool_failure rows.
# Spec §4 step 2 + INV-14; Step 13 R1 codex P1 finding (judge errors must not
# abort the audit pass — they MUST surface as MED-WARN audit_tool_failure rows).
# ---------------------------------------------------------------------------


class TP12JudgeFailureAuditToolFailure(_PipelineTestBase):
    """T-P12: judge_fn exceptions / malformed output → audit_tool_failure row."""

    def _run_one(self, judge_fn: Any) -> dict[str, Any]:
        return self.run_pipeline(citations=[_citation()], judge_fn=judge_fn)

    def _assert_audit_tool_failure(self, out: dict[str, Any], expected_tag: str) -> None:
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1, "exactly one row emitted on judge failure")
        e = results[0]
        self.assertEqual(e["judgment"], "RETRIEVAL_FAILED")
        self.assertEqual(e["audit_status"], "inconclusive")
        self.assertEqual(e["defect_stage"], "not_applicable")
        self.assertEqual(e["ref_retrieval_method"], "audit_tool_failure")
        self.assertTrue(
            e["rationale"].startswith(expected_tag + ":"),
            f"rationale must lead with INV-14 fault-class tag {expected_tag!r}; got {e['rationale']!r}",
        )

    def test_timeout_error_becomes_judge_timeout(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            raise TimeoutError("judge call exceeded 30s")

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_timeout")

    def test_value_error_becomes_judge_parse_error(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            raise ValueError("response payload was not parseable")

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_generic_exception_becomes_judge_api_error(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            raise RuntimeError("upstream returned 503")

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_api_error")

    def test_malformed_return_missing_judgment_key(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"rationale": "shaped wrong"}

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_malformed_return_non_dict(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return "this is not a dict"  # type: ignore[return-value]

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_unknown_judgment_value_rejected(self) -> None:
        # Step 13 R2 codex P2: _invoke_judge must validate the judgment enum,
        # not only check key presence. An unknown value MUST map to
        # judge_parse_error rather than reach passport-lint stage.
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"judgment": "MAYBE_SUPPORTED", "rationale": "garbage"}

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_violated_without_constraint_id_rejected(self) -> None:
        # Step 13 R2 codex P2: VIOLATED without a violated_constraint_id would
        # otherwise emit an INV-7-failing negative_constraint_violation row.
        # Reject at invocation boundary instead.
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"judgment": "VIOLATED", "rationale": "missing id"}

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_violated_with_blank_constraint_id_rejected(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {
                "judgment": "VIOLATED",
                "violated_constraint_id": "   ",
                "rationale": "whitespace id",
            }

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_cited_path_rejects_retrieval_failed_verdict(self) -> None:
        # Step 13 R3 codex P2 #2: cited path must not accept RETRIEVAL_FAILED
        # / NOT_VIOLATED — they would crash in _judge_result_entry.
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"judgment": "RETRIEVAL_FAILED", "rationale": "wrong path"}

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_cited_path_rejects_not_violated_verdict(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"judgment": "NOT_VIOLATED", "rationale": "wrong path"}

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_violated_id_outside_active_set_rejected(self) -> None:
        # Step 13 R3 codex P2 #1: VIOLATED with an id the author never declared
        # would otherwise gate-refuse the formatter on a hallucinated rule.
        # The default _citation() has no active constraints, so any nonblank
        # id is outside the active set.
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {
                "judgment": "VIOLATED",
                "violated_constraint_id": "MNC-99",
                "rationale": "hallucinated constraint",
            }

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    # Step 13 R8 codex P2-3 — judgment isinstance(str) guard before set
    # membership. Pre-fix: a malformed return like {"judgment": [1, 2], ...}
    # raised TypeError("unhashable type: 'list'") inside the set membership
    # test, aborting the audit. Post-fix: translation boundary catches it
    # as judge_parse_error → audit_tool_failure (#120 P2-3).

    def test_judgment_non_string_list_becomes_judge_parse_error(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"judgment": [1, 2], "rationale": "unhashable list"}

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")

    def test_judgment_non_string_dict_becomes_judge_parse_error(self) -> None:
        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"judgment": {"nested": "obj"}, "rationale": "unhashable dict"}

        self._assert_audit_tool_failure(self._run_one(judge_fn), "judge_parse_error")


# ---------------------------------------------------------------------------
# T-P14 — retrieve_fn invocation failure mapping to INV-14 retrieval_* tags.
# Spec §4 step 2 + INV-14; Step 13 R2 codex P2 finding (symmetric to TP12 —
# transient retrieval errors must surface as audit_tool_failure rows).
# ---------------------------------------------------------------------------


class TP14RetrieveFailureAuditToolFailure(_PipelineTestBase):
    """T-P14: retrieve_fn exceptions / malformed output → audit_tool_failure row."""

    def _run_one(self, retrieve_fn: Any) -> dict[str, Any]:
        return self.run_pipeline(citations=[_citation()], retrieve_fn=retrieve_fn)

    def _assert_audit_tool_failure(self, out: dict[str, Any], expected_tag: str) -> None:
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1)
        e = results[0]
        self.assertEqual(e["judgment"], "RETRIEVAL_FAILED")
        self.assertEqual(e["audit_status"], "inconclusive")
        self.assertEqual(e["defect_stage"], "not_applicable")
        self.assertEqual(e["ref_retrieval_method"], "audit_tool_failure")
        self.assertTrue(
            e["rationale"].startswith(expected_tag + ":"),
            f"rationale must lead with INV-14 fault-class tag {expected_tag!r}; got {e['rationale']!r}",
        )

    def test_timeout_error_becomes_retrieval_timeout(self) -> None:
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            raise TimeoutError("retrieval exceeded 60s")

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_timeout")

    def test_connection_error_becomes_retrieval_network_error(self) -> None:
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            raise ConnectionError("DNS resolution failed")

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_network_error")

    def test_generic_exception_becomes_retrieval_api_error(self) -> None:
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            raise RuntimeError("upstream returned 503")

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_api_error")

    def test_malformed_return_non_dict(self) -> None:
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            return ["not a dict"]  # type: ignore[return-value]

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_api_error")

    def test_malformed_return_missing_ref_retrieval_method(self) -> None:
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            return {"retrieved_excerpt": "no method key"}

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_api_error")

    def test_malformed_return_unknown_method(self) -> None:
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            return {"ref_retrieval_method": "magic_protocol"}

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_api_error")

    def test_malformed_return_non_string_method(self) -> None:
        # Step 13 R8 codex P2-4: ref_retrieval_method as a list raises
        # TypeError on set membership outside the translation boundary;
        # must surface as retrieval_api_error → audit_tool_failure.
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            return {"ref_retrieval_method": ["api", "manual_pdf"], "retrieved_excerpt": "n/a"}

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_api_error")

    def test_api_method_without_excerpt_rejected(self) -> None:
        # Step 13 R3 codex P2 #3 — api with empty excerpt would let the judge
        # mark SUPPORTED with no source text.
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            return {"ref_retrieval_method": "api", "retrieved_excerpt": ""}

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_api_error")

    def test_manual_pdf_with_none_excerpt_rejected(self) -> None:
        def retrieve_fn(_c: dict[str, Any]) -> dict[str, Any]:
            return {"ref_retrieval_method": "manual_pdf", "retrieved_excerpt": None}

        self._assert_audit_tool_failure(self._run_one(retrieve_fn), "retrieval_api_error")


# ---------------------------------------------------------------------------
# T-P13 — EMITTED_NOT_INTENDED set-dedup per D6 (Step 13 R1 codex P2).
# When the same drifted claim_text carries multiple citation markers (e.g.
# one sentence with two ref slugs), one drift row should emit, not one per
# citation.
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# T-P16 — Uncited stream split (Step 13 R4 codex P1 #2).
# Constraint judging runs over the full uncited set; uncited_assertion[]
# LOW-WARN advisory runs over the D4-c filtered subset.
# ---------------------------------------------------------------------------


class TP21UncitedClaimLevelNC(_PipelineTestBase):
    """T-P21: Step 13 R7 codex P1 — uncited stream (d) must include claim-level
    NC-C constraints when the sentence binds a manifest_claim_id.

    Pre-fix: only manifest_negative_constraints (MNC-) was passed to the
    judge; NC-C... for the bound claim was silently dropped.
    """

    def test_nc_c_included_when_sentence_binds_claim_id(self) -> None:
        manifest = _manifest(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Bound claim.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                    "negative_constraints": [
                        {
                            "constraint_id": "NC-C001-1",
                            "rule": "MUST NOT generalize beyond cohort.",
                        }
                    ],
                }
            ],
            mncs=[],
        )
        sentence = {
            "sentence_text": "All practitioners benefit.",
            "section_path": "Discussion",
            "manifest_claim_id": "C-001",
            "scoped_manifest_id": MANIFEST_ID,
        }
        seen_ids: list[set[str]] = []

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            active = kwargs.get("active_constraints") or []
            seen_ids.append({c["constraint_id"] for c in active})
            return {
                "judgment": "VIOLATED",
                "violated_constraint_id": "NC-C001-1",
                "rationale": "Generalizes beyond cohort.",
            }

        out = self.run_pipeline(
            citations=[],
            manifests=[manifest],
            uncited_sentences=[],
            all_uncited_sentences=[sentence],
            judge_fn=judge_fn,
        )
        self.assertEqual(seen_ids, [{"NC-C001-1"}])
        cv = out["constraint_violations"]
        self.assertEqual(len(cv), 1)
        self.assertEqual(cv[0]["violated_constraint_id"], "NC-C001-1")
        self.assertEqual(cv[0]["scoped_manifest_id"], MANIFEST_ID)


class TP22DuplicateMNCIdAcrossManifests(_PipelineTestBase):
    """T-P22: Step 13 R7 codex P2 — when two manifests use the same MNC id
    string (e.g. both have MNC-1), an uncited violation MUST be attributed
    to the correct manifest. Per-manifest judge calls + scope binding by
    construction (not by first-match-wins lookup).
    """

    def test_violation_attributed_to_correct_manifest(self) -> None:
        manifest_a = _manifest(
            manifest_id="M-2026-05-16T09:00:00Z-a111",
            claims=[],
            mncs=[{"constraint_id": "MNC-1", "rule": "MUST NOT use A-words"}],
        )
        manifest_b = _manifest(
            manifest_id="M-2026-05-16T09:00:00Z-b222",
            claims=[],
            mncs=[{"constraint_id": "MNC-1", "rule": "MUST NOT use B-words"}],
        )
        sentence = {
            "sentence_text": "Uses B-words.",
            "section_path": "Discussion",
        }

        # judge_fn distinguishes by rule text: only violates manifest B's rule.
        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            active = kwargs.get("active_constraints") or []
            for c in active:
                if "B-words" in c.get("rule", ""):
                    return {
                        "judgment": "VIOLATED",
                        "violated_constraint_id": "MNC-1",
                        "rationale": "Uses B-words.",
                    }
            return {"judgment": "NOT_VIOLATED", "rationale": "n/a"}

        out = self.run_pipeline(
            citations=[],
            manifests=[manifest_a, manifest_b],
            uncited_sentences=[],
            all_uncited_sentences=[sentence],
            judge_fn=judge_fn,
        )
        cv = out["constraint_violations"]
        self.assertEqual(len(cv), 1, f"exactly one CV row; got {cv!r}")
        # MUST be attributed to manifest B, NOT manifest A (alphabetic first).
        self.assertEqual(
            cv[0]["scoped_manifest_id"],
            "M-2026-05-16T09:00:00Z-b222",
            f"violation MUST attribute to the manifest whose rule the judge actually violated; got {cv[0]['scoped_manifest_id']!r}",
        )


class TP20UncitedSentenceWithoutScope(_PipelineTestBase):
    """T-P20: Step 13 R6 codex P1 — sentences in the documented all_uncited_sentences
    shape (sentence_text + section_path + optional adjacent_text only, NO
    scoped_manifest_id) MUST still trigger the constraint judge.

    Pre-fix: the loop required sentence.get("scoped_manifest_id") to resolve
    constraints, so orchestrator callers following the contract never saw the
    HIGH-WARN-CONSTRAINT-VIOLATION-UNCITED gate fire. The runtime now applies
    every manifest-level MNC when no caller scope is provided; constraint
    violation rows derive their scoped_manifest_id from the violated_constraint_id
    ↔ source-manifest mapping.
    """

    def test_uncited_sentence_no_scope_triggers_mnc_judge(self) -> None:
        manifest = _manifest(
            claims=[],
            mncs=[
                {
                    "constraint_id": "MNC-1",
                    "rule": "MUST NOT use causal language",
                }
            ],
        )
        sentence = {
            "sentence_text": "The program caused outcome improvement.",
            "section_path": "Discussion",
            # No scoped_manifest_id — documented Stage 4 sentence shape.
        }
        out = self.run_pipeline(
            citations=[],
            manifests=[manifest],
            uncited_sentences=[],  # not D4-c-flagged
            all_uncited_sentences=[sentence],
            judge_fn=lambda **kw: {
                "judgment": "VIOLATED",
                "violated_constraint_id": "MNC-1",
                "rationale": "Causal language.",
            },
        )
        cv = out["constraint_violations"]
        self.assertEqual(
            len(cv),
            1,
            f"R6 P1: uncited sentence without scope must reach MNC judge; got {cv!r}",
        )
        # Schema requires concrete scoped_manifest_id matching the M-pattern.
        self.assertEqual(cv[0]["scoped_manifest_id"], MANIFEST_ID)
        self.assertEqual(cv[0]["violated_constraint_id"], "MNC-1")

    def test_caller_provided_scope_restricts_mnc_set(self) -> None:
        # When the caller pins scoped_manifest_id, only that manifest's MNCs
        # apply (cross-manifest leakage prevented).
        manifest_a = _manifest(
            manifest_id="M-aaaa-A",
            claims=[],
            mncs=[{"constraint_id": "MNC-1", "rule": "MUST NOT use A-words"}],
        )
        manifest_b = _manifest(
            manifest_id="M-bbbb-B",
            claims=[],
            mncs=[{"constraint_id": "MNC-2", "rule": "MUST NOT use B-words"}],
        )
        # Sentence pinned to manifest A — judge should only see MNC-1.
        sentence = {
            "sentence_text": "Uses A-words.",
            "section_path": "Discussion",
            "scoped_manifest_id": "M-aaaa-A",
        }
        seen_constraint_ids: list[set[str]] = []

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            active = kwargs.get("active_constraints") or []
            seen_constraint_ids.append({c["constraint_id"] for c in active})
            return {"judgment": "NOT_VIOLATED", "rationale": "n/a"}

        self.run_pipeline(
            citations=[],
            manifests=[manifest_a, manifest_b],
            uncited_sentences=[],
            all_uncited_sentences=[sentence],
            judge_fn=judge_fn,
        )
        self.assertEqual(
            seen_constraint_ids,
            [{"MNC-1"}],
            "caller-provided scope must restrict judge to that manifest's MNCs",
        )


class TP19ConstraintAbsorptionFullManifestScope(_PipelineTestBase):
    """T-P19: Step 13 R5 codex P3 — when a citation in manifest M violates a
    negative constraint, ALL of M's drift findings are absorbed, including
    same-manifest citations whose claim_id is NOT in M's declared claim set.

    Pre-fix: pair-level absorption (M, cid_in_manifest) plus the violating
    citation's own pair. A different same-manifest emitted citation with
    claim_id=C-999 (drifted) still produced EMITTED_NOT_INTENDED — that
    contradicted the "absorbed in full" precedence rule.
    """

    def test_drifted_claim_id_in_same_manifest_as_violation_absorbed(self) -> None:
        manifest = _manifest(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Manifest claim about X.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
            ],
            mncs=[
                {
                    "constraint_id": "MNC-1",
                    "rule": "MUST NOT use causal language",
                }
            ],
        )
        # Citation 1 violates the MNC on a declared claim_id (C-001).
        violating = _citation(
            claim_id="C-001",
            claim_text="Manifest claim about X.",
            ref_slug="ref-violator",
        )
        # Citation 2 is in the SAME manifest but has a drifted (non-manifest)
        # claim_id. Pre-fix: produced an extra EMITTED_NOT_INTENDED row.
        drifted_sibling = _citation(
            claim_id="C-999",
            claim_text="Sibling claim with drifted id.",
            ref_slug="ref-sibling",
        )

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            ct = kwargs.get("claim_text", "")
            if "X" in ct:
                return {
                    "judgment": "VIOLATED",
                    "violated_constraint_id": "MNC-1",
                    "rationale": "Causal language violates MNC-1.",
                }
            return {"judgment": "SUPPORTED", "rationale": "Cited page supports."}

        out = self.run_pipeline(
            citations=[violating, drifted_sibling],
            manifests=[manifest],
            judge_fn=judge_fn,
        )
        drifts = [d for d in out["claim_drifts"] if d["drift_kind"] == "EMITTED_NOT_INTENDED"]
        self.assertEqual(
            drifts,
            [],
            f"Same-manifest drifted claim_id MUST be absorbed alongside the constraint violation; got {len(drifts)} drift row(s): {drifts!r}",
        )
        # The constraint violation itself still emits.
        cv = [
            r for r in out["claim_audit_results"]
            if r.get("defect_stage") == "negative_constraint_violation"
        ]
        self.assertEqual(len(cv), 1, "constraint violation row MUST emit")

    def test_drift_in_other_manifest_not_absorbed_by_violation_in_first(self) -> None:
        # Cross-manifest absorption is forbidden — manifest A violation MUST
        # NOT silence drift in manifest B.
        manifest_a = _manifest(
            manifest_id="M-aaaa-A",
            claims=[],
            mncs=[
                {"constraint_id": "MNC-1", "rule": "MUST NOT use causal language"}
            ],
        )
        manifest_b = _manifest(
            manifest_id="M-bbbb-B",
            claims=[
                {
                    "claim_id": "C-100",
                    "claim_text": "Manifest B intended claim.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
            ],
        )
        violating_a = _citation(
            claim_id="C-001",
            scoped_manifest_id="M-aaaa-A",
            claim_text="Causal claim in A.",
        )

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            ct = kwargs.get("claim_text", "")
            if "A" in ct:
                return {
                    "judgment": "VIOLATED",
                    "violated_constraint_id": "MNC-1",
                    "rationale": "Causal.",
                }
            return {"judgment": "SUPPORTED", "rationale": "ok"}

        out = self.run_pipeline(
            citations=[violating_a],
            manifests=[manifest_a, manifest_b],
            judge_fn=judge_fn,
        )
        # Manifest B's C-100 is NOT emitted → INTENDED_NOT_EMITTED MUST still fire.
        intended_drift_b = [
            d for d in out["claim_drifts"]
            if d["drift_kind"] == "INTENDED_NOT_EMITTED" and d.get("scoped_manifest_id") == "M-bbbb-B"
        ]
        self.assertEqual(
            len(intended_drift_b),
            1,
            "manifest B drift MUST NOT be absorbed by violation in manifest A",
        )


class TP18ManifestMissingNoSpuriousDrift(_PipelineTestBase):
    """T-P18: MANIFEST-MISSING run (manifests=[]) produces no claim_drifts[]
    rows. There's no pre-commitment baseline to diff against; emitting
    EMITTED_NOT_INTENDED for every citation would be spurious noise on top
    of the MANIFEST-MISSING advisory the formatter already surfaces.
    Step 13 R5 codex P2 #2.
    """

    def test_no_manifest_no_drift_rows(self) -> None:
        from scripts._claim_audit_constants import SENTINEL_MANIFEST_ID

        citation = {
            "claim_id": "C-001",
            "scoped_manifest_id": SENTINEL_MANIFEST_ID,
            "claim_text": "Some supported claim.",
            "ref_slug": "ref-1",
            "anchor_kind": "page",
            "anchor_value": "10",
            "section_path": "Discussion",
        }
        out = self.run_pipeline(
            citations=[citation],
            manifests=[],
            judge_fn=_judge_supported(),
        )
        self.assertEqual(
            out["claim_drifts"],
            [],
            f"MANIFEST-MISSING run must not emit drift rows; got {out['claim_drifts']!r}",
        )
        # Audit row still emits — the fallback is audit-only, not no-op.
        self.assertEqual(len(out["claim_audit_results"]), 1)

    def test_manifest_present_but_empty_claims_no_drift(self) -> None:
        # A manifest with zero claims is equivalent to no baseline; drift
        # detection should still short-circuit.
        empty_manifest = _manifest(claims=[])
        citation = _citation(claim_text="Drifted claim text.")
        out = self.run_pipeline(
            citations=[citation],
            manifests=[empty_manifest],
            judge_fn=_judge_supported(),
        )
        self.assertEqual(out["claim_drifts"], [])


class TP17ManifestMissingSentinelFallback(_PipelineTestBase):
    """T-P17: MANIFEST-MISSING fallback path must not KeyError when caller
    omits scoped_manifest_id from the citation dict.

    Step 13 R4 codex P2 #3 — row builders previously did
    `citation["scoped_manifest_id"]` directly; the caller's _written_scope_for
    helper would default to SENTINEL_MANIFEST_ID but only AFTER row
    construction, so the index lookup crashed before the sentinel could be
    applied. Row builders now use .get(SENTINEL_MANIFEST_ID) so the fallback
    path works end-to-end.
    """

    def test_citation_without_scoped_manifest_id_emits_sentinel_row(self) -> None:
        citation = {
            "claim_id": "C-001",
            "claim_text": "Manifest-missing test claim.",
            "ref_slug": "ref-1",
            "anchor_kind": "page",
            "anchor_value": "10",
            # scoped_manifest_id deliberately omitted (MANIFEST-MISSING caller).
        }
        out = self.run_pipeline(
            citations=[citation],
            manifests=[],
            judge_fn=_judge_supported(),
        )
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1, "fallback row must emit, not KeyError")
        # The caller's _written_scope_for would default to SENTINEL_MANIFEST_ID
        # because no manifest binds this claim_id.
        from scripts._claim_audit_constants import SENTINEL_MANIFEST_ID

        self.assertEqual(results[0]["scoped_manifest_id"], SENTINEL_MANIFEST_ID)


class TP16UncitedStreamSplit(_PipelineTestBase):
    """T-P16: constraint stream (d) sees full uncited set; LOW-WARN sees D4-c only."""

    def _build_manifest_with_mnc(self) -> dict[str, Any]:
        return _manifest(
            claims=[],
            mncs=[
                {
                    "constraint_id": "MNC-1",
                    "rule": "MUST NOT use causal language",
                }
            ],
        )

    def test_constraint_violation_outside_d4c_trigger_still_emitted(self) -> None:
        # Sentence violates MNC ("caused improvement") but lacks D4-c trigger
        # tokens (no quantifier, no "%", no "p<"). Pre-R4 the constraint stream
        # would never see it.
        manifest = self._build_manifest_with_mnc()
        full_uncited = [
            {
                "sentence_text": "The program caused improvement.",
                "section_path": "Discussion",
                "scoped_manifest_id": MANIFEST_ID,
            }
        ]
        d4c_uncited: list[dict[str, Any]] = []  # detector filtered this out

        out = self.run_pipeline(
            citations=[],
            manifests=[manifest],
            uncited_sentences=d4c_uncited,
            all_uncited_sentences=full_uncited,
            judge_fn=lambda **kw: {
                "judgment": "VIOLATED",
                "violated_constraint_id": "MNC-1",
                "rationale": "Uses causal language 'caused'.",
            },
        )
        cv = out["constraint_violations"]
        self.assertEqual(len(cv), 1, "constraint judging must run over full uncited set")
        self.assertEqual(cv[0]["violated_constraint_id"], "MNC-1")
        # The LOW-WARN uncited_assertion is NOT emitted because the sentence
        # was outside D4-c trigger filter.
        self.assertEqual(out["uncited_assertions"], [])

    def test_d4c_positive_emits_both_streams(self) -> None:
        # Sentence is BOTH D4-c-positive AND violates MNC → both rows emit
        # (CV-INV-4 explicitly permits the dual presence).
        manifest = self._build_manifest_with_mnc()
        d4c_sentence = {
            "sentence_text": "The program caused 95% improvement.",
            "section_path": "Discussion",
            "scoped_manifest_id": MANIFEST_ID,
            "trigger_tokens": ["95%"],
        }
        out = self.run_pipeline(
            citations=[],
            manifests=[manifest],
            uncited_sentences=[d4c_sentence],
            all_uncited_sentences=[d4c_sentence],
            judge_fn=lambda **kw: {
                "judgment": "VIOLATED",
                "violated_constraint_id": "MNC-1",
                "rationale": "Causal claim.",
            },
        )
        self.assertEqual(len(out["constraint_violations"]), 1)
        self.assertEqual(len(out["uncited_assertions"]), 1)

    def test_backwards_compat_when_all_uncited_omitted(self) -> None:
        # Legacy caller passes only uncited_sentences (the D4-c subset). The
        # pipeline falls back to using that subset for stream (d) too — the
        # constraint check is narrower than the R4 expansion, but the API
        # surface still works.
        manifest = self._build_manifest_with_mnc()
        d4c_sentence = {
            "sentence_text": "The program caused improvement (p<0.01).",
            "section_path": "Discussion",
            "scoped_manifest_id": MANIFEST_ID,
            "trigger_tokens": ["p<0.01"],
        }
        out = self.run_pipeline(
            citations=[],
            manifests=[manifest],
            uncited_sentences=[d4c_sentence],
            # all_uncited_sentences intentionally omitted — defaults to
            # uncited_sentences for backwards compat.
            judge_fn=lambda **kw: {
                "judgment": "VIOLATED",
                "violated_constraint_id": "MNC-1",
                "rationale": "Causal claim.",
            },
        )
        self.assertEqual(len(out["constraint_violations"]), 1)
        self.assertEqual(len(out["uncited_assertions"]), 1)


# ---------------------------------------------------------------------------
# T-P15 — Malformed cache hit → cache_corruption audit_tool_failure row.
# Step 13 R3 codex P2 #4: persistent or injected cache entries can carry
# malformed values; revalidate every hit before routing.
# ---------------------------------------------------------------------------


class TP15CacheCorruption(_PipelineTestBase):
    """T-P15: cache hit re-validated through _validate_judge_dict."""

    def test_missing_judgment_key_in_cache(self) -> None:
        # Pre-seed cache with a malformed entry that lacks `judgment`.
        cache = {}
        # First populate using a valid run so we know the key shape works.
        invoked: list[Any] = []

        def judge_fn(**kwargs: Any) -> dict[str, Any]:
            invoked.append(kwargs)
            return {"judgment": "SUPPORTED", "rationale": "fresh"}

        # Run once to capture the cache_key the pipeline computes.
        self.run_pipeline(citations=[_citation()], judge_fn=judge_fn, cache=cache)
        self.assertEqual(len(cache), 1)
        cache_key = next(iter(cache))

        # Corrupt the cached value to simulate a stale / partial dump.
        cache[cache_key] = {"rationale": "but no judgment key"}

        out = self.run_pipeline(
            citations=[_citation()],
            judge_fn=lambda **_kw: {"judgment": "SUPPORTED", "rationale": "should not be called"},
            cache=cache,
        )
        results = out["claim_audit_results"]
        self.assertEqual(len(results), 1)
        e = results[0]
        self.assertEqual(e["ref_retrieval_method"], "audit_tool_failure")
        self.assertTrue(
            e["rationale"].startswith("cache_corruption:"),
            f"cache hit failure must use INV-14 cache_corruption tag; got {e['rationale']!r}",
        )

    def test_unknown_judgment_in_cache(self) -> None:
        cache = {}

        def judge_fn(**_kw: Any) -> dict[str, Any]:
            return {"judgment": "SUPPORTED", "rationale": "fresh"}

        self.run_pipeline(citations=[_citation()], judge_fn=judge_fn, cache=cache)
        cache_key = next(iter(cache))
        cache[cache_key] = {"judgment": "GIBBERISH", "rationale": "stale"}

        out = self.run_pipeline(
            citations=[_citation()],
            judge_fn=lambda **_kw: {"judgment": "SUPPORTED", "rationale": "n/a"},
            cache=cache,
        )
        results = out["claim_audit_results"]
        self.assertTrue(results[0]["rationale"].startswith("cache_corruption:"))


class TP13EmittedNotIntendedDedupe(_PipelineTestBase):
    """T-P13: D6 set semantics — one drift row per drifted claim_text."""

    def test_intended_not_emitted_text_match_under_renumbered_claim_id(self) -> None:
        # Step 13 R2 codex P2: when the draft carries the manifest claim_text
        # but under a different claim_id (claim_id was renumbered), the
        # INTENDED_NOT_EMITTED side MUST use the same set-of-text semantics
        # as the EMITTED_NOT_INTENDED side. Otherwise a benign renumbering
        # produces false LOW-WARN drift findings.
        manifest = _manifest(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Renumbered manifest claim about Y.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
            ]
        )
        # Drafter emits the same claim_text but assigns claim_id C-999 (e.g.
        # the manifest was authored, then claim_ids reshuffled before prose).
        citations = [
            _citation(
                claim_id="C-999",
                claim_text="Renumbered manifest claim about Y.",
                ref_slug="ref-a",
            )
        ]
        out = self.run_pipeline(citations=citations, manifests=[manifest])
        intended_not_emitted = [
            d for d in out["claim_drifts"] if d["drift_kind"] == "INTENDED_NOT_EMITTED"
        ]
        self.assertEqual(
            intended_not_emitted,
            [],
            "claim_text-match must short-circuit INTENDED_NOT_EMITTED per D6 set semantics",
        )

    def test_two_refs_one_drift(self) -> None:
        # Manifest pre-commits to C-001 only; the drafter emits a different
        # claim_text twice, once per citation marker (typical for a sentence
        # like "X is correlated with Y (Ref1, Ref2)" where the drafter chose
        # not to add this claim to the manifest).
        manifest = _manifest(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Manifest-intended claim about X.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
            ]
        )
        drifted_text = "This claim was never in the manifest."
        citations = [
            _citation(
                claim_id="C-001",
                claim_text=drifted_text,
                ref_slug="ref-a",
                anchor_value="10",
            ),
            _citation(
                claim_id="C-001",
                claim_text=drifted_text,
                ref_slug="ref-b",
                anchor_value="20",
            ),
        ]
        out = self.run_pipeline(citations=citations, manifests=[manifest])
        drifts = [d for d in out["claim_drifts"] if d["drift_kind"] == "EMITTED_NOT_INTENDED"]
        self.assertEqual(
            len(drifts),
            1,
            f"D6 Emitted is a set of claim_text — one drifted text + two refs MUST yield 1 drift row; got {len(drifts)}",
        )
        self.assertEqual(drifts[0]["claim_text"], drifted_text)


if __name__ == "__main__":
    unittest.main()
