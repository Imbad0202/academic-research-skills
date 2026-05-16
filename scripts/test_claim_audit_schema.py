"""Schema-validation tests for v3.8 claim_ref_alignment_audit_agent (T-S1..T-S8).

Per spec §7.1 in
docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md.

The test plan section §7.1 lists T-S1..T-S8 keyed to claim_audit_result
(§3.1) and claim_intent_manifest (§3.2) and uncited_assertion (§3.3).
§6 lint coverage is broader: it includes claim_drift D-INV-1..4 (§3.4),
constraint_violation CV-INV-1..4 (§3.5) and audit_sampling_summary
S-INV-1..4 (§4 step 3). This file follows §6 because that is the lint
contract under test — drift / constraint-violation / sampling
invariants get their own pos/neg fixtures alongside INV / M-INV / U-INV
so the lint's full 38-invariant surface is covered before the agent
prompt ships in Step 5.

Spec §7 names the test file `tests/test_claim_audit_schema.py`. This
repo's CI workflows discover tests under `scripts/test_*.py` and the
30+ existing test files all live there; we honor the repo convention
and keep the spec name's stem (`test_claim_audit_schema`) so anyone
greppping the spec lands at the right file.

Run:
    python -m unittest scripts.test_claim_audit_schema -v
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from typing import Any

from scripts._test_helpers import (
    build_schema_validator,
    load_json_schema,
    run_script,
)

REPO = Path(__file__).resolve().parent.parent
PASSPORT = REPO / "shared/contracts/passport"
LINT = REPO / "scripts/check_claim_audit_consistency.py"

SCHEMA_PATHS: dict[str, Path] = {
    "claim_audit_result": PASSPORT / "claim_audit_result.schema.json",
    "claim_intent_manifest": PASSPORT / "claim_intent_manifest.schema.json",
    "uncited_assertion": PASSPORT / "uncited_assertion.schema.json",
    "claim_drift": PASSPORT / "claim_drift.schema.json",
    "constraint_violation": PASSPORT / "constraint_violation.schema.json",
}


# ---------------------------------------------------------------------------
# Canonical fixture builders. Each helper returns a fresh dict so individual
# tests can mutate one field without leaking to siblings.
# ---------------------------------------------------------------------------

MANIFEST_ID = "M-2026-05-15T10:00:00Z-a1b2"
MANIFEST_ID_OTHER = "M-2026-05-15T10:05:00Z-c3d4"
SENTINEL_MANIFEST_ID = "M-0000-00-00T00:00:00Z-0000"
AUDIT_RUN_ID = "2026-05-15T10:10:00Z-9f8e"


def supported_entry() -> dict[str, Any]:
    """Minimal SUPPORTED row — INV-1 positive baseline."""
    return {
        "claim_id": "C-001",
        "scoped_manifest_id": MANIFEST_ID,
        "claim_text": "Sample preprints accounted for 67% of corpus.",
        "ref_slug": "smith2024preprints",
        "anchor_kind": "page",
        "anchor_value": "12",
        "judgment": "SUPPORTED",
        "audit_status": "completed",
        "defect_stage": None,
        "rationale": "The cited page reports the 67% figure verbatim.",
        "judge_model": "gpt-5.5-xhigh",
        "judge_run_at": "2026-05-15T10:11:00Z",
        "ref_retrieval_method": "api",
        "audit_run_id": AUDIT_RUN_ID,
    }


def manifest_entry(
    manifest_id: str = MANIFEST_ID,
    *,
    emitted_by: str = "synthesis_agent",
    claims: list[dict[str, Any]] | None = None,
    mncs: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Build a minimal claim_intent_manifest entry."""
    return {
        "manifest_version": "1.0",
        "manifest_id": manifest_id,
        "emitted_by": emitted_by,
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


def uncited_assertion_entry() -> dict[str, Any]:
    """Minimal U-INV-* positive baseline."""
    return {
        "finding_id": "UA-001",
        "sentence_text": "Half of all submissions showed positive results.",
        "section_path": "3. Results > 3.1 Overview",
        "trigger_tokens": ["50%", "showed"],
        "detected_at": "2026-05-15T10:12:00Z",
        "rule_version": "D4-c-v1",
    }


def claim_drift_entry(*, drift_kind: str = "EMITTED_NOT_INTENDED") -> dict[str, Any]:
    """Minimal D-INV-* positive baseline."""
    base: dict[str, Any] = {
        "finding_id": "CD-001",
        "drift_kind": drift_kind,
        "claim_text": "Drifted prose sentence the writer added without manifesting.",
        "detected_at": "2026-05-15T10:13:00Z",
        "rule_version": "D4-a-v1",
    }
    if drift_kind == "EMITTED_NOT_INTENDED":
        base["section_path"] = "4. Discussion > 4.2 Implications"
        base["manifest_claim_id"] = None
        base["scoped_manifest_id"] = None
    else:  # INTENDED_NOT_EMITTED
        base["manifest_claim_id"] = "C-001"
        base["scoped_manifest_id"] = MANIFEST_ID
    return base


def constraint_violation_entry(
    *,
    constraint_id: str = "MNC-1",
    manifest_claim_id: str | None = None,
) -> dict[str, Any]:
    """Minimal CV-INV-* positive baseline."""
    return {
        "finding_id": "CV-001",
        "claim_text": "We observed causality between A and B.",
        "section_path": "4. Discussion > 4.3 Limitations",
        "violated_constraint_id": constraint_id,
        "scoped_manifest_id": MANIFEST_ID,
        "manifest_claim_id": manifest_claim_id,
        "judge_verdict": "VIOLATED",
        "rationale": "The MNC bars causal language without RCT evidence.",
        "judge_model": "gpt-5.5-xhigh",
        "judge_run_at": "2026-05-15T10:14:00Z",
        "rule_version": "D4-a-v1",
    }


def sampling_summary_entry(
    *,
    total: int = 150,
    cap: int = 100,
) -> dict[str, Any]:
    """Minimal S-INV-* positive baseline (sampled run)."""
    audited = list(range(0, total, max(1, total // cap)))[:cap]
    return {
        "audit_run_id": AUDIT_RUN_ID,
        "max_claims_per_paper": cap,
        "total_citation_count": total,
        "audited_count": len(audited),
        "audited_indices": audited,
        "sampling_strategy": "stratified_buckets_v1",
        "emitted_at": "2026-05-15T10:15:00Z",
    }


def build_passport(
    *,
    manifests: list[dict[str, Any]] | None = None,
    results: list[dict[str, Any]] | None = None,
    uncited: list[dict[str, Any]] | None = None,
    drifts: list[dict[str, Any]] | None = None,
    violations: list[dict[str, Any]] | None = None,
    samplings: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a minimal passport JSON wrapping the six aggregates the lint reads."""
    return {
        "claim_intent_manifests": manifests if manifests is not None else [manifest_entry()],
        "claim_audit_results": results or [],
        "uncited_assertions": uncited or [],
        "claim_drifts": drifts or [],
        "constraint_violations": violations or [],
        "audit_sampling_summaries": samplings or [],
    }


def write_passport(tmp: Path, body: dict[str, Any]) -> Path:
    path = tmp / "passport.json"
    path.write_text(json.dumps(body, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def run_lint(passport: Path) -> tuple[int, str, str]:
    """Invoke the lint subprocess; returns (exit_code, stdout, stderr)."""
    proc = run_script(
        LINT,
        "--passport",
        str(passport),
        extra_env={"PYTHONPATH": str(REPO)},
    )
    return proc.returncode, proc.stdout, proc.stderr


# ---------------------------------------------------------------------------
# T-S1: Schema-shape only — minimal SUPPORTED entry validates against the
# claim_audit_result schema. No lint invocation; pure Draft 2020-12 validate.
# ---------------------------------------------------------------------------

class TS1ValidMinimalEntry(unittest.TestCase):
    """T-S1: Valid minimal entry validates (SUPPORTED, all required fields)."""

    def test_supported_entry_validates(self) -> None:
        schema = load_json_schema(SCHEMA_PATHS["claim_audit_result"])
        validator = build_schema_validator(schema)
        errors = list(validator.iter_errors(supported_entry()))
        self.assertEqual(errors, [], msg=f"unexpected validation errors: {errors}")

    def test_all_five_schemas_parse_as_draft_2020_12(self) -> None:
        for name, path in SCHEMA_PATHS.items():
            with self.subTest(schema=name):
                load_json_schema(path)


# ---------------------------------------------------------------------------
# Lint-driven invariant tests share a base that writes a tmp passport,
# invokes the lint subprocess, and asserts findings.
# ---------------------------------------------------------------------------

class _LintTestBase(unittest.TestCase):
    def setUp(self) -> None:
        # Each test owns its tmpdir so concurrent unittest runners don't collide.
        import tempfile

        self._tmp_obj = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp_obj.cleanup)
        self.tmp = Path(self._tmp_obj.name)

    def assertLintFinds(
        self,
        passport_body: dict[str, Any],
        *,
        invariant: str,
        msg: str | None = None,
    ) -> tuple[int, str]:
        """Assert lint exits non-zero AND stdout contains `invariant` tag."""
        path = write_passport(self.tmp, passport_body)
        code, out, err = run_lint(path)
        full_msg = (
            f"\nexpected lint to flag {invariant}\n"
            f"--- exit={code} ---\nstdout:\n{out}\nstderr:\n{err}\n"
        )
        self.assertEqual(code, 1, msg=full_msg)
        self.assertIn(invariant, out, msg=full_msg)
        return code, out

    def assertLintClean(
        self,
        passport_body: dict[str, Any],
        *,
        msg: str | None = None,
    ) -> None:
        """Assert lint exits 0 (no findings) on a passport that should pass."""
        path = write_passport(self.tmp, passport_body)
        code, out, err = run_lint(path)
        self.assertEqual(
            code,
            0,
            msg=(msg or "")
            + f"\nexpected lint clean\nexit={code}\nstdout:\n{out}\nstderr:\n{err}\n",
        )


# ---------------------------------------------------------------------------
# T-S2: INV-1..INV-18 paired positive + negative fixtures (claim_audit_result).
# Each invariant is one subTest; baseline = SUPPORTED entry, negative cases
# mutate the field combination the invariant forbids.
# ---------------------------------------------------------------------------

class TS2ClaimAuditInvariants(_LintTestBase):
    """T-S2: each INV-N paired positive/negative fixture."""

    # ----- Positive: every INV holds when the canonical SUPPORTED row stands.
    def test_inv_baseline_positive(self) -> None:
        self.assertLintClean(build_passport(results=[supported_entry()]))

    # ----- Negative cases per invariant.
    def test_inv_1_supported_with_non_null_defect(self) -> None:
        # INV-1: SUPPORTED -> defect_stage=null AND violated_constraint_id=null
        e = supported_entry()
        e["defect_stage"] = "source_description"
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-1")

    def test_inv_2_unsupported_with_null_defect(self) -> None:
        # INV-2: UNSUPPORTED -> defect_stage != null
        e = supported_entry()
        e["judgment"] = "UNSUPPORTED"
        e["defect_stage"] = None
        e["rationale"] = "Mismatch found in source description."
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-2")

    def test_inv_3_ambiguous_with_disallowed_defect(self) -> None:
        # INV-3: AMBIGUOUS -> defect_stage NOT in {metadata, negative_constraint_violation}
        e = supported_entry()
        e["judgment"] = "AMBIGUOUS"
        e["defect_stage"] = "metadata"
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-3")

    def test_inv_4_retrieval_failed_inconclusive_wrong_defect(self) -> None:
        # INV-4: RETRIEVAL_FAILED + inconclusive -> defect_stage=not_applicable
        e = supported_entry()
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "inconclusive"
        e["defect_stage"] = "retrieval_existence"
        e["ref_retrieval_method"] = "failed"
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-4")

    def test_inv_5_retrieval_failed_completed_wrong_defect(self) -> None:
        # INV-5: RETRIEVAL_FAILED + completed -> defect_stage=retrieval_existence
        e = supported_entry()
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "completed"
        e["defect_stage"] = "source_description"
        e["ref_retrieval_method"] = "not_found"
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-5")

    def test_inv_6_anchor_none_without_rationale_prefix(self) -> None:
        # INV-6: anchor_kind=none -> rationale starts with the canonical prefix
        e = supported_entry()
        e["anchor_kind"] = "none"
        e["anchor_value"] = ""
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "inconclusive"
        e["defect_stage"] = "not_applicable"
        e["ref_retrieval_method"] = "not_attempted"
        e["rationale"] = "anchor missing for this claim"  # no v3.7.3 prefix
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-6")

    def test_inv_6_anchor_none_with_non_empty_anchor_value(self) -> None:
        # INV-6: anchor_kind=none MUST carry empty sentinel anchor_value.
        # A stale residual value (e.g. "123") violates the schema contract.
        # Step 13 R1 Gemini finding (a832d3f).
        e = supported_entry()
        e["anchor_kind"] = "none"
        e["anchor_value"] = "123"  # stale residual — must be rejected
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "inconclusive"
        e["defect_stage"] = "not_applicable"
        e["ref_retrieval_method"] = "not_attempted"
        e["rationale"] = (
            "v3.7.3 R-L3-1-A violation: cited claim C-001 carries anchor=none; "
            "v3.7.3 finalizer should have gate-refused upstream."
        )
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-6")

    def test_inv_7_constraint_violation_without_violated_id(self) -> None:
        # INV-7: negative_constraint_violation -> violated_constraint_id != null
        e = supported_entry()
        e["judgment"] = "UNSUPPORTED"
        e["defect_stage"] = "negative_constraint_violation"
        e["rationale"] = "Violated declared negative constraint."
        e["violated_constraint_id"] = None
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-7")

    def test_inv_8_constraint_violation_wrong_judgment(self) -> None:
        # INV-8: negative_constraint_violation -> judgment=UNSUPPORTED
        e = supported_entry()
        e["judgment"] = "AMBIGUOUS"
        e["defect_stage"] = "negative_constraint_violation"
        e["violated_constraint_id"] = "MNC-1"
        e["rationale"] = "Ambiguous violation of MNC-1."
        # INV-3 also fires here; we assert INV-8 specifically.
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-8")

    def test_inv_9_dispute_on_not_applicable(self) -> None:
        # INV-9: upstream_dispute != null -> defect_stage NOT in {null, not_applicable}
        e = supported_entry()
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "inconclusive"
        e["defect_stage"] = "not_applicable"
        e["ref_retrieval_method"] = "failed"
        e["rationale"] = "Paywalled."
        e["upstream_dispute"] = "Author disputes this paywall classification."
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-9")

    def test_inv_10_failed_method_wrong_state(self) -> None:
        # INV-10: ref_retrieval_method=failed -> RETRIEVAL_FAILED + inconclusive + not_applicable
        e = supported_entry()
        e["ref_retrieval_method"] = "failed"
        # judgment still SUPPORTED -> INV-10 violation
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-10")

    def test_inv_11_not_attempted_without_anchor_none(self) -> None:
        # INV-11: ref_retrieval_method=not_attempted iff anchor_kind=none
        e = supported_entry()
        e["ref_retrieval_method"] = "not_attempted"
        # anchor_kind still page -> INV-11 violation
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-11")

    def test_inv_12_not_found_wrong_state(self) -> None:
        # INV-12: ref_retrieval_method=not_found iff fabricated-reference triple
        e = supported_entry()
        e["ref_retrieval_method"] = "not_found"
        # judgment still SUPPORTED -> INV-12 violation
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-12")

    def test_inv_13_metadata_wrong_method(self) -> None:
        # INV-13: defect_stage=metadata -> ref_retrieval_method in {api, manual_pdf}
        e = supported_entry()
        e["judgment"] = "UNSUPPORTED"
        e["defect_stage"] = "metadata"
        e["rationale"] = "Author/year mismatch."
        e["ref_retrieval_method"] = "failed"
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-13")

    def test_inv_14_audit_tool_failure_without_fault_class_prefix(self) -> None:
        # INV-14: ref_retrieval_method=audit_tool_failure -> rationale begins with fault-class tag
        e = supported_entry()
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "inconclusive"
        e["defect_stage"] = "not_applicable"
        e["ref_retrieval_method"] = "audit_tool_failure"
        e["rationale"] = "Something went wrong."  # missing tag
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-14")

    def test_inv_15_dangling_scoped_manifest_id(self) -> None:
        # INV-15: (scoped_manifest_id, claim_id) must resolve in some manifest entry
        e = supported_entry()
        e["scoped_manifest_id"] = "M-2099-01-01T00:00:00Z-dead"  # not in manifests
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-15")

    def test_inv_15_sentinel_manifest_permitted(self) -> None:
        # INV-15 sentinel positive case — MANIFEST-MISSING fallback row.
        e = supported_entry()
        e["scoped_manifest_id"] = SENTINEL_MANIFEST_ID
        passport = build_passport(manifests=[], results=[e])
        self.assertLintClean(
            passport,
            msg="sentinel scoped_manifest_id must be accepted in MANIFEST-MISSING fallback",
        )

    def test_inv_16_empty_anchor_value_with_non_none_kind(self) -> None:
        # INV-16: anchor_kind != none -> anchor_value non-empty after strip
        e = supported_entry()
        e["anchor_value"] = "   "  # whitespace only
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-16")

    def test_inv_16_url_encoded_whitespace_does_not_bypass(self) -> None:
        # INV-16: URL-encoded whitespace (%20, %09) must NOT bypass the firm
        # rule — docstring + schema both require non-empty *after* URL-decode.
        # Step 13 R1 Gemini finding (a832d3f).
        e = supported_entry()
        e["anchor_value"] = "%20%20%09"
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-16")

    def test_inv_16_url_encoded_non_whitespace_passes(self) -> None:
        # INV-16: URL-encoded printable content must still satisfy the rule.
        e = supported_entry()
        e["anchor_kind"] = "quote"
        e["anchor_value"] = "ten%20cited%20words"  # 'ten cited words' after decode
        self.assertLintClean(build_passport(results=[e]))

    def test_inv_17_constraint_id_inner_hyphen_form(self) -> None:
        # INV-17: NC-C{n}-{m} parse rule — NO inner hyphen between C and digits
        manifest = manifest_entry(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Causal claim.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                    "negative_constraints": [
                        {
                            # malformed: NC-C-001-1 instead of NC-C001-1
                            "constraint_id": "NC-C-001-1",
                            "rule": "Must not claim causality without RCT.",
                        }
                    ],
                }
            ],
        )
        # Schema pattern itself rejects this — lint surfaces INV-17 explicitly.
        passport = build_passport(manifests=[manifest], results=[])
        self.assertLintFinds(passport, invariant="INV-17")

    def test_inv_18_inconclusive_not_applicable_wrong_method(self) -> None:
        # INV-18: (RETRIEVAL_FAILED, inconclusive, not_applicable) -> method in
        # {not_attempted, failed, audit_tool_failure}. `api` is forbidden.
        e = supported_entry()
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "inconclusive"
        e["defect_stage"] = "not_applicable"
        e["ref_retrieval_method"] = "api"
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-18")


# ---------------------------------------------------------------------------
# T-S3: anchor_kind=none + INV-6 violation paths.
# ---------------------------------------------------------------------------

class TS3AnchorNoneInv6(_LintTestBase):
    """T-S3: anchor=none entries that miss rationale prefix or use wrong method."""

    def _none_entry(self) -> dict[str, Any]:
        e = supported_entry()
        e["anchor_kind"] = "none"
        e["anchor_value"] = ""
        e["judgment"] = "RETRIEVAL_FAILED"
        e["audit_status"] = "inconclusive"
        e["defect_stage"] = "not_applicable"
        e["ref_retrieval_method"] = "not_attempted"
        e["rationale"] = "v3.7.3 R-L3-1-A violation: no anchor on cited claim."
        return e

    def test_anchor_none_positive_baseline(self) -> None:
        # Canonical INV-6 compliant row should pass.
        self.assertLintClean(build_passport(results=[self._none_entry()]))

    def test_anchor_none_missing_rationale_prefix(self) -> None:
        e = self._none_entry()
        e["rationale"] = "anchor missing"  # no prefix
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-6")

    def test_anchor_none_wrong_retrieval_method(self) -> None:
        e = self._none_entry()
        e["ref_retrieval_method"] = "failed"  # should be not_attempted
        # INV-11 ↔ INV-6 mismatch — either fires; spec couples the firm rule via INV-6/11.
        self.assertLintFinds(build_passport(results=[e]), invariant="INV-6")


# ---------------------------------------------------------------------------
# T-S4: M-INV-1 duplicate claim_id within ONE manifest.
# ---------------------------------------------------------------------------

class TS4ManifestInv1(_LintTestBase):
    """T-S4: duplicate claim_id within one manifest is rejected; cross-manifest collision permitted."""

    def test_duplicate_claim_id_within_one_manifest_rejected(self) -> None:
        manifest = manifest_entry(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "First claim.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                },
                {
                    "claim_id": "C-001",  # duplicate within ONE manifest
                    "claim_text": "Second collision.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                },
            ],
        )
        self.assertLintFinds(
            build_passport(manifests=[manifest]),
            invariant="M-INV-1",
        )

    def test_cross_manifest_claim_id_collision_permitted(self) -> None:
        manifest_a = manifest_entry(manifest_id=MANIFEST_ID)
        manifest_b = manifest_entry(
            manifest_id=MANIFEST_ID_OTHER,
            emitted_by="draft_writer_agent",
        )
        self.assertLintClean(
            build_passport(manifests=[manifest_a, manifest_b]),
            msg="cross-manifest C-001 collision MUST be permitted (joinable pair)",
        )

    def test_m_inv_4_duplicate_manifest_id_across_passport_rejected(self) -> None:
        manifest_a = manifest_entry(manifest_id=MANIFEST_ID)
        manifest_b = manifest_entry(
            manifest_id=MANIFEST_ID,  # collides with manifest_a
            emitted_by="draft_writer_agent",
        )
        self.assertLintFinds(
            build_passport(manifests=[manifest_a, manifest_b]),
            invariant="M-INV-4",
        )


# ---------------------------------------------------------------------------
# T-S5: M-INV-2 dangling NC-C{n}-{m} (no parent claim with C-{n}).
# ---------------------------------------------------------------------------

class TS5ManifestInv2(_LintTestBase):
    """T-S5: NC-C{n}-{m} must scope under a claims[] entry with claim_id=C-{n}."""

    def test_dangling_claim_level_nc(self) -> None:
        manifest = manifest_entry(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "First claim.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                    "negative_constraints": [
                        {
                            # NC scoped to C-002, but no C-002 claim exists.
                            "constraint_id": "NC-C002-1",
                            "rule": "Mismatched parent.",
                        }
                    ],
                }
            ],
        )
        self.assertLintFinds(
            build_passport(manifests=[manifest]),
            invariant="M-INV-2",
        )


# ---------------------------------------------------------------------------
# T-S6: M-INV-3 claim-level NC attempting to override MNC.
# ---------------------------------------------------------------------------

class TS6ManifestInv3(_LintTestBase):
    """T-S6: claim-level NC cannot DROP a global MNC; ADD is permitted."""

    def test_claim_level_nc_collides_with_mnc_id(self) -> None:
        # M-INV-3 — claim-level constraint reusing an MNC-* id is the override
        # signature the lint must reject (claim level can ADD via fresh NC-C{n}-{m}
        # ids, never via re-using an MNC-* id).
        manifest = manifest_entry(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Causal claim.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                    "negative_constraints": [
                        {
                            "constraint_id": "MNC-1",  # disallowed at claim level
                            "rule": "Trying to override.",
                        }
                    ],
                }
            ],
            mncs=[
                {
                    "constraint_id": "MNC-1",
                    "rule": "Must not claim causality.",
                }
            ],
        )
        self.assertLintFinds(
            build_passport(manifests=[manifest]),
            invariant="M-INV-3",
        )


# ---------------------------------------------------------------------------
# T-S7: U-INV-1..U-INV-4 paired positive/negative.
# ---------------------------------------------------------------------------

class TS7UncitedAssertionInvariants(_LintTestBase):
    """T-S7: U-INV-1..U-INV-4 paired pos/neg fixtures."""

    def test_u_baseline_positive(self) -> None:
        self.assertLintClean(build_passport(uncited=[uncited_assertion_entry()]))

    def test_u_inv_1_duplicate_finding_id(self) -> None:
        a = uncited_assertion_entry()
        b = uncited_assertion_entry()  # same UA-001
        self.assertLintFinds(
            build_passport(uncited=[a, b]),
            invariant="U-INV-1",
        )

    def test_u_inv_2_empty_trigger_tokens(self) -> None:
        e = uncited_assertion_entry()
        e["trigger_tokens"] = []
        # Schema also rejects (minItems=1); lint surfaces U-INV-2 specifically.
        self.assertLintFinds(
            build_passport(uncited=[e]),
            invariant="U-INV-2",
        )

    def test_u_inv_3_wrong_rule_version(self) -> None:
        e = uncited_assertion_entry()
        e["rule_version"] = "D4-c-v0"
        # Schema const rejects; lint surfaces U-INV-3 specifically.
        self.assertLintFinds(
            build_passport(uncited=[e]),
            invariant="U-INV-3",
        )

    def test_u_inv_4_orphan_manifest_pointer(self) -> None:
        # manifest_claim_id set without matching manifest entry -> U-INV-4
        e = uncited_assertion_entry()
        e["manifest_claim_id"] = "C-999"
        e["scoped_manifest_id"] = MANIFEST_ID
        self.assertLintFinds(
            build_passport(uncited=[e]),
            invariant="U-INV-4",
        )

    def test_u_inv_4_null_manifest_id_with_set_claim_id(self) -> None:
        # manifest_claim_id != null requires scoped_manifest_id != null.
        e = uncited_assertion_entry()
        e["manifest_claim_id"] = "C-001"
        e["scoped_manifest_id"] = None
        self.assertLintFinds(
            build_passport(uncited=[e]),
            invariant="U-INV-4",
        )


# ---------------------------------------------------------------------------
# T-S8: (judgment, audit_status, defect_stage) matrix exhaustive coverage.
# Spec §3.1 table: 9 positive rows, lint rejects every (j, a, d) triple
# outside the table; ≥5 disallowed combinations exercised explicitly.
# ---------------------------------------------------------------------------

class TS8AllowedMatrix(_LintTestBase):
    """T-S8: every allowed triple validates; ≥5 disallowed combinations rejected."""

    # Positive matrix rows — each is a self-contained passport fragment.
    ALLOWED_ROWS = [
        # (judgment, audit_status, defect_stage, ref_retrieval_method overrides)
        ("SUPPORTED", "completed", None, {"ref_retrieval_method": "api"}),
        ("AMBIGUOUS", "completed", "source_description", {"ref_retrieval_method": "api"}),
        ("AMBIGUOUS", "completed", "citation_anchor", {"ref_retrieval_method": "api"}),
        ("AMBIGUOUS", "completed", "synthesis_overclaim", {"ref_retrieval_method": "api"}),
        ("AMBIGUOUS", "completed", None, {"ref_retrieval_method": "api"}),
        ("UNSUPPORTED", "completed", "source_description", {"ref_retrieval_method": "api"}),
        ("UNSUPPORTED", "completed", "metadata", {"ref_retrieval_method": "api"}),
        ("UNSUPPORTED", "completed", "citation_anchor", {"ref_retrieval_method": "api"}),
        ("UNSUPPORTED", "completed", "synthesis_overclaim", {"ref_retrieval_method": "api"}),
        (
            "UNSUPPORTED",
            "completed",
            "negative_constraint_violation",
            {
                "ref_retrieval_method": "api",
                "violated_constraint_id": "MNC-1",
            },
        ),
        (
            "RETRIEVAL_FAILED",
            "completed",
            "retrieval_existence",
            {"ref_retrieval_method": "not_found"},
        ),
        (
            "RETRIEVAL_FAILED",
            "inconclusive",
            "not_applicable",
            {"ref_retrieval_method": "failed"},
        ),
    ]

    # Negative cases — ≥5 representative disallowed combinations.
    DISALLOWED_ROWS = [
        # (judgment, audit_status, defect_stage, overrides, expected_invariant)
        (
            "SUPPORTED",
            "completed",
            "source_description",
            {"ref_retrieval_method": "api"},
            "INV-1",
        ),
        (
            "UNSUPPORTED",
            "completed",
            None,
            {"ref_retrieval_method": "api"},
            "INV-2",
        ),
        (
            "RETRIEVAL_FAILED",
            "completed",
            "not_applicable",
            {"ref_retrieval_method": "api"},
            "matrix",
        ),
        (
            "SUPPORTED",
            "inconclusive",
            None,
            {"ref_retrieval_method": "api"},
            "matrix",
        ),
        (
            "AMBIGUOUS",
            "completed",
            "metadata",
            {"ref_retrieval_method": "api"},
            "INV-3",
        ),
        (
            "AMBIGUOUS",
            "inconclusive",
            None,
            {"ref_retrieval_method": "api"},
            "matrix",
        ),
    ]

    def _build_row(self, j: str, a: str, d: Any, overrides: dict[str, Any]) -> dict[str, Any]:
        e = supported_entry()
        e["judgment"] = j
        e["audit_status"] = a
        e["defect_stage"] = d
        if d == "negative_constraint_violation":
            e["rationale"] = "Violated declared negative constraint."
        elif d == "retrieval_existence":
            e["rationale"] = "Reference does not exist."
        elif d == "not_applicable":
            e["rationale"] = "Paywall — full text not retrievable."
        elif d is not None:
            e["rationale"] = f"Defect at {d}."
        e.update(overrides)
        return e

    def test_every_allowed_row_passes(self) -> None:
        for j, a, d, overrides in self.ALLOWED_ROWS:
            with self.subTest(judgment=j, audit_status=a, defect_stage=d):
                e = self._build_row(j, a, d, overrides)
                self.assertLintClean(
                    build_passport(results=[e]),
                    msg=f"row ({j}, {a}, {d}) should pass",
                )

    def test_disallowed_rows_rejected(self) -> None:
        for j, a, d, overrides, invariant in self.DISALLOWED_ROWS:
            with self.subTest(judgment=j, audit_status=a, defect_stage=d):
                e = self._build_row(j, a, d, overrides)
                self.assertLintFinds(
                    build_passport(results=[e]),
                    invariant=invariant,
                )


# ---------------------------------------------------------------------------
# Spec §6 lint 4a — D-INV-1..D-INV-4 claim_drift cross-array integrity.
# Not labelled T-Sx in spec §7.1 but mandatory per §6.4a. Paired pos/neg.
# ---------------------------------------------------------------------------

class TSDDriftInvariants(_LintTestBase):
    """Spec §6.4a: claim_drift D-INV-1..D-INV-4."""

    def test_d_baseline_emitted_not_intended(self) -> None:
        self.assertLintClean(build_passport(drifts=[claim_drift_entry()]))

    def test_d_baseline_intended_not_emitted(self) -> None:
        drift = claim_drift_entry(drift_kind="INTENDED_NOT_EMITTED")
        self.assertLintClean(build_passport(drifts=[drift]))

    def test_d_inv_1_duplicate_finding_id(self) -> None:
        a = claim_drift_entry()
        b = claim_drift_entry()  # CD-001 collides
        self.assertLintFinds(build_passport(drifts=[a, b]), invariant="D-INV-1")

    def test_d_inv_2_intended_not_emitted_missing_manifest_pointer(self) -> None:
        drift = claim_drift_entry(drift_kind="INTENDED_NOT_EMITTED")
        drift["manifest_claim_id"] = None  # MUST be non-null for INTENDED_NOT_EMITTED
        drift["scoped_manifest_id"] = None
        self.assertLintFinds(build_passport(drifts=[drift]), invariant="D-INV-2")

    def test_d_inv_2_emitted_not_intended_with_manifest_pointer(self) -> None:
        drift = claim_drift_entry(drift_kind="EMITTED_NOT_INTENDED")
        drift["manifest_claim_id"] = "C-001"  # MUST be null for EMITTED_NOT_INTENDED
        drift["scoped_manifest_id"] = MANIFEST_ID
        self.assertLintFinds(build_passport(drifts=[drift]), invariant="D-INV-2")

    def test_d_inv_2_dangling_intended_not_emitted_pair(self) -> None:
        drift = claim_drift_entry(drift_kind="INTENDED_NOT_EMITTED")
        drift["manifest_claim_id"] = "C-999"  # no such claim in manifest
        drift["scoped_manifest_id"] = MANIFEST_ID
        self.assertLintFinds(build_passport(drifts=[drift]), invariant="D-INV-2")

    def test_d_inv_3_wrong_rule_version(self) -> None:
        drift = claim_drift_entry()
        drift["rule_version"] = "D4-a-v0"
        self.assertLintFinds(build_passport(drifts=[drift]), invariant="D-INV-3")

    def test_d_inv_4_uncited_and_drift_collision(self) -> None:
        # A single sentence appears in both uncited_assertions[] and claim_drifts[].
        sentence = "Half of submissions showed positive results."
        uncited = uncited_assertion_entry()
        uncited["sentence_text"] = sentence
        drift = claim_drift_entry()
        drift["claim_text"] = sentence
        self.assertLintFinds(
            build_passport(uncited=[uncited], drifts=[drift]),
            invariant="D-INV-4",
        )


# ---------------------------------------------------------------------------
# Spec §6.4b — CV-INV-1..CV-INV-4 constraint_violation cross-array integrity.
# ---------------------------------------------------------------------------

class TSCVConstraintViolationInvariants(_LintTestBase):
    """Spec §6.4b: constraint_violation CV-INV-1..CV-INV-4."""

    def _manifest_with_mnc_and_nc(self) -> dict[str, Any]:
        return manifest_entry(
            claims=[
                {
                    "claim_id": "C-001",
                    "claim_text": "Causal claim.",
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                    "negative_constraints": [
                        {
                            "constraint_id": "NC-C001-1",
                            "rule": "No causal language without RCT.",
                        }
                    ],
                }
            ],
            mncs=[{"constraint_id": "MNC-1", "rule": "Global rule."}],
        )

    def test_cv_baseline_mnc_violation(self) -> None:
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[constraint_violation_entry()],
        )
        self.assertLintClean(passport)

    def test_cv_baseline_nc_violation(self) -> None:
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[
                constraint_violation_entry(
                    constraint_id="NC-C001-1",
                    manifest_claim_id="C-001",
                )
            ],
        )
        self.assertLintClean(passport)

    def test_cv_inv_1_duplicate_finding_id(self) -> None:
        a = constraint_violation_entry()
        b = constraint_violation_entry()
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[a, b],
        )
        self.assertLintFinds(passport, invariant="CV-INV-1")

    def test_cv_inv_2_dangling_mnc(self) -> None:
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[constraint_violation_entry(constraint_id="MNC-99")],
        )
        self.assertLintFinds(passport, invariant="CV-INV-2")

    def test_cv_inv_2_dangling_nc(self) -> None:
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[
                constraint_violation_entry(
                    constraint_id="NC-C999-1",
                    manifest_claim_id="C-999",
                )
            ],
        )
        self.assertLintFinds(passport, invariant="CV-INV-2")

    def test_cv_inv_3_mnc_with_set_manifest_claim_id(self) -> None:
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[
                constraint_violation_entry(
                    constraint_id="MNC-1",
                    manifest_claim_id="C-001",  # MUST be null for MNC
                )
            ],
        )
        self.assertLintFinds(passport, invariant="CV-INV-3")

    def test_cv_inv_3_nc_polarity_mismatch(self) -> None:
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[
                constraint_violation_entry(
                    constraint_id="NC-C001-1",
                    manifest_claim_id="C-002",  # MUST match the C-001 in NC id
                )
            ],
        )
        self.assertLintFinds(passport, invariant="CV-INV-3")

    def test_cv_inv_4_duplicate_per_constraint(self) -> None:
        # Two violations for (same sentence, same constraint) -> dedup rule.
        a = constraint_violation_entry()
        b = constraint_violation_entry()
        b["finding_id"] = "CV-002"  # avoid CV-INV-1 collision
        passport = build_passport(
            manifests=[self._manifest_with_mnc_and_nc()],
            violations=[a, b],
        )
        self.assertLintFinds(passport, invariant="CV-INV-4")


# ---------------------------------------------------------------------------
# Spec §6.4c — S-INV-1..S-INV-4 audit_sampling_summary invariants.
# ---------------------------------------------------------------------------

class TSSamplingInvariants(_LintTestBase):
    """Spec §6.4c: audit_sampling_summary S-INV-1..S-INV-4."""

    def test_s_baseline(self) -> None:
        self.assertLintClean(build_passport(samplings=[sampling_summary_entry()]))

    def test_s_inv_1_count_vs_indices_mismatch(self) -> None:
        e = sampling_summary_entry()
        e["audited_count"] = e["audited_count"] - 1  # off-by-one
        self.assertLintFinds(build_passport(samplings=[e]), invariant="S-INV-1")

    def test_s_inv_2_count_exceeds_cap(self) -> None:
        e = sampling_summary_entry(total=50, cap=10)
        e["audited_count"] = 20
        e["audited_indices"] = list(range(20))
        self.assertLintFinds(build_passport(samplings=[e]), invariant="S-INV-2")

    def test_s_inv_2_count_exceeds_total(self) -> None:
        e = sampling_summary_entry(total=10, cap=100)
        e["audited_count"] = 20
        e["audited_indices"] = list(range(20))
        self.assertLintFinds(build_passport(samplings=[e]), invariant="S-INV-2")

    def test_s_inv_4_non_ascending_indices(self) -> None:
        e = sampling_summary_entry(total=20, cap=10)
        e["audited_indices"] = [5, 3, 7, 9, 11, 13, 15, 17, 19, 2]
        e["audited_count"] = 10
        self.assertLintFinds(build_passport(samplings=[e]), invariant="S-INV-4")

    def test_s_inv_4_duplicate_indices(self) -> None:
        e = sampling_summary_entry(total=20, cap=10)
        e["audited_indices"] = [0, 1, 1, 3, 4, 5, 6, 7, 8, 9]
        e["audited_count"] = 10
        self.assertLintFinds(build_passport(samplings=[e]), invariant="S-INV-4")


# ---------------------------------------------------------------------------
# T-S9: Defensive guard against malformed passports.
# Step 13 R4 codex P2 #4 — malformed aggregates (non-list / non-dict entries)
# must surface as schema findings rather than crash the lint with an
# AttributeError traceback.
# ---------------------------------------------------------------------------


class TS9MalformedPassportGuard(_LintTestBase):
    """T-S9: passport with malformed aggregate yields schema finding, not crash."""

    def test_claim_audit_results_with_non_dict_entry(self) -> None:
        # Pre-R4: list of non-dict in claim_audit_results raised AttributeError
        # because dict-only invariant loops ran .get() before noticing the shape.
        body = build_passport()
        body["claim_audit_results"] = ["this should be an object, not a string"]
        path = write_passport(self.tmp, body)
        code, out, err = run_lint(path)
        self.assertEqual(
            code,
            1,
            msg=f"expected clean lint failure on malformed aggregate; got exit={code}\nstderr:\n{err}",
        )
        self.assertNotIn(
            "Traceback",
            err,
            msg=f"lint must not raise — got traceback:\n{err}",
        )
        self.assertIn("schema", out, msg=f"expected schema finding tag in stdout:\n{out}")

    def test_claim_intent_manifests_as_dict_instead_of_list(self) -> None:
        body = build_passport()
        body["claim_intent_manifests"] = {"oops": "should be a list"}
        path = write_passport(self.tmp, body)
        code, out, err = run_lint(path)
        self.assertEqual(code, 1, msg=f"expected exit=1; got {code}\nstderr:\n{err}")
        self.assertNotIn("Traceback", err, msg=f"lint must not raise:\n{err}")
        self.assertIn("schema", out)

    def test_non_object_passport_body_yields_clean_finding(self) -> None:
        # Step 13 R7 codex P3: `[]`, `null`, scalar top-level JSON would
        # previously crash with AttributeError on `.get()`. Validate that
        # each surfaces as a schema finding without traceback.
        for malformed_body in ([], None, 42, "passport"):
            with self.subTest(body=malformed_body):
                path = self.tmp / f"malformed_{type(malformed_body).__name__}.json"
                path.write_text(json.dumps(malformed_body), encoding="utf-8")
                code, out, err = run_lint(path)
                self.assertEqual(
                    code,
                    1,
                    msg=f"expected exit=1 for body={malformed_body!r}; got {code}\nstderr:\n{err}",
                )
                self.assertNotIn(
                    "Traceback",
                    err,
                    msg=f"lint must not raise for body={malformed_body!r}:\n{err}",
                )
                self.assertIn("schema", out, msg=f"expected schema finding:\n{out}")

    def test_falsey_malformed_aggregate_does_not_bypass_schema(self) -> None:
        # Step 13 R5 codex P2 #1: `body.get(k, []) or []` would silently
        # convert a malformed `{}` / `null` / `0` / `""` value to an empty
        # list and skip schema validation. Each falsey-but-malformed shape
        # must surface as a schema finding.
        for malformed in ({}, None, 0, ""):
            with self.subTest(malformed=malformed):
                body = build_passport()
                body["claim_audit_results"] = malformed
                path = write_passport(self.tmp, body)
                code, out, err = run_lint(path)
                self.assertEqual(
                    code,
                    1,
                    msg=f"expected exit=1 for malformed={malformed!r}; got {code}\nstdout:\n{out}\nstderr:\n{err}",
                )
                self.assertIn("schema", out, msg=f"expected schema finding for malformed={malformed!r}:\n{out}")
                self.assertNotIn("Traceback", err, msg=f"lint must not raise for malformed={malformed!r}:\n{err}")


if __name__ == "__main__":
    unittest.main()
