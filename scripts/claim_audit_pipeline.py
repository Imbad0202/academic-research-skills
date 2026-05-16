"""claim_audit_pipeline — Python implementation of the §4 Step 1-6 pipeline.

This module is the executable face of `claim_ref_alignment_audit_agent.md`.
The agent prompt narrates the pipeline contract; this module runs it
under test so cross-field invariants and emission routing can be pinned
without dispatching the agent to a live model.

Retrieval and judge invocation are dependency-injected (`retrieve_fn` /
`judge_fn`) so tests can drive every error and decision path — paywall,
audit_tool_failure, not_found, SUPPORTED, UNSUPPORTED with each
defect_stage hint, VIOLATED. Production callers wire these to real
retrieval/judge clients in their own dispatch layer.

The full spec is in
docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md §4-§5.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable

# Allow both CLI invocations (`python3 scripts/claim_audit_pipeline.py`) AND
# package-style invocations (`python -m unittest scripts.test_*`) to resolve
# the shared constants module via the same import.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _claim_audit_constants import (  # noqa: E402
    DRIFT_RULE_VERSION,
    INV6_RATIONALE_PREFIX,
    RE_NC_CONSTRAINT,
    SAMPLING_STRATEGY,
    SENTINEL_MANIFEST_ID,
    UNCITED_RULE_VERSION,
)

# Permitted UNSUPPORTED defect_stages for non-constraint paths (§3.1 matrix).
_UNSUPPORTED_NON_CONSTRAINT_DEFECTS = {
    "source_description",
    "metadata",
    "citation_anchor",
    "synthesis_overclaim",
}

# Permitted AMBIGUOUS defect_stages (§3.1 matrix).
_AMBIGUOUS_DEFECTS = {"source_description", "citation_anchor", "synthesis_overclaim", None}


# ---------------------------------------------------------------------------
# Cache helpers.
# ---------------------------------------------------------------------------


def _stable_json(value: Any) -> str:
    """JCS-style canonicalization sufficient for cache-key hashing."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _hash_text(text: str | None) -> str:
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()


def _active_constraints_for_claim(
    *,
    scoped_manifest_id: str,
    claim_id: str,
    claim_by_mc_id: dict[tuple[str, str], dict[str, Any]],
    mncs_by_manifest_id: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Return the manifest-scoped + claim-scoped negative-constraint set for a citation.

    Reads from pre-built indexes (built once per audit run in
    `run_audit_pipeline`) instead of rescanning the manifest tree per
    citation — at realistic workloads (~150 citations × ~100 manifest
    claims) that saves ~30k Python ops per run with no behavioral delta.
    """
    constraints: list[dict[str, Any]] = []
    for mnc in mncs_by_manifest_id.get(scoped_manifest_id, []):
        constraints.append({"constraint_id": mnc["constraint_id"], "rule": mnc["rule"], "scope": "MNC"})
    claim = claim_by_mc_id.get((scoped_manifest_id, claim_id))
    if claim is not None:
        for nc in claim.get("negative_constraints", []) or []:
            constraints.append(
                {"constraint_id": nc["constraint_id"], "rule": nc["rule"], "scope": "NC"}
            )
    constraints.sort(key=lambda c: c["constraint_id"])
    return constraints


def _cache_key(
    *,
    claim_text: str,
    ref_slug: str,
    anchor_kind: str,
    anchor_value: str,
    retrieved_excerpt: str | None,
    active_constraints: list[dict[str, Any]],
    judge_model: str,
) -> str:
    payload = {
        "claim_text_hash": _hash_text(claim_text),
        "ref_slug": ref_slug,
        "anchor_kind": anchor_kind,
        "anchor_value_hash": _hash_text(anchor_value),
        "retrieved_excerpt_hash": _hash_text(retrieved_excerpt),
        "active_constraints_hash": _hash_text(
            _stable_json([{"constraint_id": c["constraint_id"], "rule": c["rule"]} for c in active_constraints])
        ),
        "judge_model": judge_model,
    }
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Emission helpers — each builds one entry dict.
# ---------------------------------------------------------------------------


def _anchorless_entry(citation: dict[str, Any], *, audit_run_id: str, now_iso: str, judge_model: str) -> dict[str, Any]:
    """§4 Step 1: anchor=none short-circuits to RETRIEVAL_FAILED+inconclusive+not_applicable+not_attempted."""
    return {
        "claim_id": citation["claim_id"],
        "scoped_manifest_id": citation["scoped_manifest_id"],
        "claim_text": citation["claim_text"],
        "ref_slug": citation["ref_slug"],
        "anchor_kind": "none",
        "anchor_value": citation.get("anchor_value", ""),
        "judgment": "RETRIEVAL_FAILED",
        "audit_status": "inconclusive",
        "defect_stage": "not_applicable",
        "rationale": (
            f"{INV6_RATIONALE_PREFIX}: cited claim {citation['claim_id']} carries anchor=none; "
            "v3.7.3 finalizer should have gate-refused upstream — defense-in-depth row."
        ),
        "judge_model": judge_model,
        "judge_run_at": now_iso,
        "ref_retrieval_method": "not_attempted",
        "upstream_owner_agent": citation.get("upstream_owner_agent"),
        "audit_run_id": audit_run_id,
    }


def _retrieval_failure_entry(
    citation: dict[str, Any],
    *,
    method: str,
    audit_run_id: str,
    now_iso: str,
    judge_model: str,
    fault_class: str | None = None,
) -> dict[str, Any]:
    """§4 Step 2: retrieval-side failure routes that skip the judge."""
    if method == "failed":
        # D2 paywall — LOW-WARN advisory; INV-10.
        entry = {
            "judgment": "RETRIEVAL_FAILED",
            "audit_status": "inconclusive",
            "defect_stage": "not_applicable",
            "rationale": "Reference full text not retrievable (paywall / license-restricted access).",
        }
    elif method == "not_found":
        # Fabricated reference — HIGH-WARN; INV-12.
        entry = {
            "judgment": "RETRIEVAL_FAILED",
            "audit_status": "completed",
            "defect_stage": "retrieval_existence",
            "rationale": "Retrieval API reports the cited reference does not exist (suspected fabrication).",
        }
    elif method == "audit_tool_failure":
        # Transient infrastructure outage — MED-WARN; INV-14.
        tag = fault_class or "retrieval_api_error"
        entry = {
            "judgment": "RETRIEVAL_FAILED",
            "audit_status": "inconclusive",
            "defect_stage": "not_applicable",
            "rationale": f"{tag}: transient audit-infrastructure failure during retrieval; retry on next pipeline pass.",
        }
    else:  # pragma: no cover — should be unreachable given Step 2 caller dispatch
        raise ValueError(f"_retrieval_failure_entry called with non-failure method={method!r}")

    return {
        "claim_id": citation["claim_id"],
        "scoped_manifest_id": citation["scoped_manifest_id"],
        "claim_text": citation["claim_text"],
        "ref_slug": citation["ref_slug"],
        "anchor_kind": citation["anchor_kind"],
        "anchor_value": citation.get("anchor_value", ""),
        "judgment": entry["judgment"],
        "audit_status": entry["audit_status"],
        "defect_stage": entry["defect_stage"],
        "rationale": entry["rationale"],
        "judge_model": judge_model,
        "judge_run_at": now_iso,
        "ref_retrieval_method": method,
        "upstream_owner_agent": citation.get("upstream_owner_agent"),
        "audit_run_id": audit_run_id,
    }


def _judge_result_entry(
    citation: dict[str, Any],
    *,
    judge_result: dict[str, Any],
    ref_retrieval_method: str,
    audit_run_id: str,
    now_iso: str,
    judge_model: str,
) -> dict[str, Any]:
    """§4 Steps 5-6: route judge verdict to the right (judgment, defect_stage) row."""
    verdict = judge_result["judgment"]
    rationale = judge_result.get("rationale", "")

    if verdict == "SUPPORTED":
        judgment, defect_stage, violated_id = "SUPPORTED", None, None
    elif verdict == "AMBIGUOUS":
        hint = judge_result.get("defect_stage_hint")
        if hint not in _AMBIGUOUS_DEFECTS:
            hint = None  # AMBIGUOUS+disallowed defect → coerce to null (INV-3 protection)
        judgment, defect_stage, violated_id = "AMBIGUOUS", hint, None
    elif verdict == "UNSUPPORTED":
        hint = judge_result.get("defect_stage_hint") or "source_description"
        if hint not in _UNSUPPORTED_NON_CONSTRAINT_DEFECTS:
            hint = "source_description"
        judgment, defect_stage, violated_id = "UNSUPPORTED", hint, None
    elif verdict == "VIOLATED":
        # Cited constraint violation — INV-7/INV-8 path.
        judgment = "UNSUPPORTED"
        defect_stage = "negative_constraint_violation"
        violated_id = judge_result.get("violated_constraint_id")
    else:
        raise ValueError(f"unknown judge verdict: {verdict!r}")

    entry: dict[str, Any] = {
        "claim_id": citation["claim_id"],
        "scoped_manifest_id": citation["scoped_manifest_id"],
        "claim_text": citation["claim_text"],
        "ref_slug": citation["ref_slug"],
        "anchor_kind": citation["anchor_kind"],
        "anchor_value": citation.get("anchor_value", ""),
        "judgment": judgment,
        "audit_status": "completed",
        "defect_stage": defect_stage,
        "rationale": rationale or "(no rationale provided)",
        "judge_model": judge_model,
        "judge_run_at": now_iso,
        "ref_retrieval_method": ref_retrieval_method,
        "upstream_owner_agent": citation.get("upstream_owner_agent"),
        "audit_run_id": audit_run_id,
    }
    if violated_id is not None:
        entry["violated_constraint_id"] = violated_id
    return entry


def _constraint_violation_entry(
    *,
    sentence: dict[str, Any],
    judge_result: dict[str, Any],
    scoped_manifest_id: str,
    finding_id: str,
    judge_model: str,
    now_iso: str,
) -> dict[str, Any]:
    """§3.5 / §5 stream (d): uncited claim with VIOLATED judge verdict."""
    violated_id = judge_result.get("violated_constraint_id")
    manifest_claim_id = None
    if violated_id:
        nc_match = RE_NC_CONSTRAINT.match(violated_id)
        if nc_match:
            manifest_claim_id = f"C-{nc_match.group(1)}"
    return {
        "finding_id": finding_id,
        "claim_text": sentence["sentence_text"],
        "section_path": sentence.get("section_path", ""),
        "violated_constraint_id": violated_id,
        "scoped_manifest_id": scoped_manifest_id,
        "manifest_claim_id": manifest_claim_id,
        "judge_verdict": "VIOLATED",
        "rationale": judge_result.get("rationale", "Constraint violated by uncited claim."),
        "judge_model": judge_model,
        "judge_run_at": now_iso,
        "rule_version": DRIFT_RULE_VERSION,
        "upstream_owner_agent": sentence.get("upstream_owner_agent"),
    }


def _uncited_assertion_entry(
    *,
    sentence: dict[str, Any],
    finding_id: str,
    now_iso: str,
    trigger_tokens: list[str] | None = None,
) -> dict[str, Any]:
    # Resolve trigger_tokens with strict semantics: prefer the explicit
    # keyword arg, fall back to the sentence dict, and raise if both are
    # absent. The prior `["uncited"]` sentinel passed U-INV-2 minItems=1
    # but carried no semantic content — callers who skipped the detector
    # silently emitted meaningless tokens into the passport. Raise instead
    # so the contract is enforced at write-time, not discovered at audit-
    # read-time (per codex R1 P1-4).
    tokens = trigger_tokens or sentence.get("trigger_tokens")
    if not tokens:
        raise ValueError(
            f"_uncited_assertion_entry: finding_id={finding_id!r} has no "
            "trigger_tokens. Caller must pre-process draft sentences "
            "through detect_uncited_assertions (or supply trigger_tokens "
            "explicitly); the schema's U-INV-2 minItems=1 invariant is "
            "an audit-quality contract, not a placeholder slot."
        )
    manifest_claim_id = sentence.get("manifest_claim_id")
    # Step 7 codex R1 CO-3 / U-INV-4 pair rule: scoped_manifest_id is the
    # disambiguator for a specific manifest claim. When no claim_id is bound
    # (the uncited sentence is in scope for a manifest-level MNC but is NOT
    # itself a manifest claim — runtime contract for stream-d uncited
    # constraint-violation routing), the uncited_assertion row MUST drop the
    # manifest scope. The companion constraint_violations[] row owns the
    # manifest pointer in that case; carrying scope on both rows would fail
    # U-INV-4 (manifest_claim_id null ↔ scoped_manifest_id null).
    scoped_manifest_id = (
        sentence.get("scoped_manifest_id") if manifest_claim_id is not None else None
    )
    return {
        "finding_id": finding_id,
        "sentence_text": sentence["sentence_text"],
        "section_path": sentence.get("section_path", ""),
        "trigger_tokens": tokens,
        "detected_at": now_iso,
        "rule_version": UNCITED_RULE_VERSION,
        "upstream_owner_agent": sentence.get("upstream_owner_agent"),
        "manifest_claim_id": manifest_claim_id,
        "scoped_manifest_id": scoped_manifest_id,
    }


def _claim_drift_entry(
    *,
    drift_kind: str,
    claim_text: str,
    finding_id: str,
    now_iso: str,
    manifest_claim_id: str | None = None,
    scoped_manifest_id: str | None = None,
    section_path: str | None = None,
) -> dict[str, Any]:
    entry = {
        "finding_id": finding_id,
        "drift_kind": drift_kind,
        "claim_text": claim_text,
        "detected_at": now_iso,
        "rule_version": DRIFT_RULE_VERSION,
        "manifest_claim_id": manifest_claim_id,
        "scoped_manifest_id": scoped_manifest_id,
        "section_path": section_path,
    }
    return entry


# ---------------------------------------------------------------------------
# Sampling helper.
# ---------------------------------------------------------------------------


def _stratified_bucket_indices(total: int, cap: int) -> list[int]:
    """Pick `cap` indices in [0, total) via stratified buckets in document order.

    Divides [0, total) into `cap` equal-ish buckets and picks the first index of
    each bucket. The result is strictly ascending and has length min(cap, total).

    Why two-stage fill: a naive `int(i * width)` for `width = total / cap`
    silently collapses adjacent picks when `total/cap < 2` (e.g. N=101,
    cap=100 → `int(99 * 1.01) == int(100 * 1.0)`-class duplicates after
    dedup). The S-INV-1 invariant ties `audited_count` to `len(audited_indices)`
    so a silent dedup would shrink audited_count below cap with no surface.
    We dedup first, then fill the remaining slots from un-picked indices in
    ascending document order — keeping the bucket-first-pick bias for spread
    while honoring the contract that `audited_count == min(cap, N)` whenever
    that is achievable.
    """
    if total <= 0 or cap <= 0:
        return []
    k = min(cap, total)
    width = total / k
    picks: set[int] = set()
    for i in range(k):
        picks.add(int(i * width))
    # Fill missing slots from un-picked indices in ascending order so the
    # final result is exactly k strictly-ascending unique picks whenever
    # k ≤ total (which is guaranteed by `k = min(cap, total)`).
    if len(picks) < k:
        for j in range(total):
            if j not in picks:
                picks.add(j)
                if len(picks) == k:
                    break
    return sorted(picks)


# ---------------------------------------------------------------------------
# Drift detection (manifest set-diff).
# ---------------------------------------------------------------------------


def _detect_drifts(
    *,
    manifests: list[dict[str, Any]],
    emitted_citations: list[dict[str, Any]],
    uncited_sentence_texts: set[str],
    constraint_absorbed_claim_ids: set[tuple[str, str]],
    now_iso: str,
    next_finding_id: Callable[[], str],
) -> list[dict[str, Any]]:
    """§4 step 5 manifest set-diff producing claim_drift entries.

    Precedence:
      - T-P8: constraint-violation absorbs drift — no companion drift entry for
        (scoped_manifest_id, claim_id) pairs already in
        `constraint_absorbed_claim_ids`.
      - T-P10 / D-INV-4: uncited sentence takes precedence over drift — no
        drift entry whose claim_text matches an uncited sentence_text.
    """
    drifts: list[dict[str, Any]] = []

    # Index emitted citations by (scoped_manifest_id, claim_id) — these are
    # the "supported" set candidates the prose actually produced.
    emitted_pairs: set[tuple[str, str]] = {
        (c["scoped_manifest_id"], c["claim_id"]) for c in emitted_citations
    }
    emitted_texts = {c["claim_text"] for c in emitted_citations}

    # INTENDED_NOT_EMITTED — manifest claims missing from emitted set.
    for m in manifests:
        mid = m.get("manifest_id")
        for claim in m.get("claims", []) or []:
            cid = claim.get("claim_id")
            claim_text = claim.get("claim_text", "")
            if (mid, cid) in emitted_pairs:
                continue
            if (mid, cid) in constraint_absorbed_claim_ids:
                continue
            if claim_text in uncited_sentence_texts:
                # Step 7 codex R1 CO-1 / D-INV-4 cross-aggregate exclusivity:
                # when a manifest claim appears as an uncited sentence in the
                # draft, the uncited_assertion row takes priority. Emitting an
                # INTENDED_NOT_EMITTED drift alongside would fail the D-INV-4
                # consistency lint (one finding per sentence across both
                # aggregates). Mirrors the EMITTED_NOT_INTENDED skip in the
                # loop below.
                continue
            drifts.append(
                _claim_drift_entry(
                    drift_kind="INTENDED_NOT_EMITTED",
                    claim_text=claim_text,
                    finding_id=next_finding_id(),
                    now_iso=now_iso,
                    manifest_claim_id=cid,
                    scoped_manifest_id=mid,
                    section_path=None,
                )
            )

    # EMITTED_NOT_INTENDED — emitted citations whose claim_text is not in any
    # manifest's claim_text set.
    all_manifest_texts: set[str] = set()
    for m in manifests:
        for claim in m.get("claims", []) or []:
            text = claim.get("claim_text")
            if text:
                all_manifest_texts.add(text)

    for c in emitted_citations:
        text = c.get("claim_text", "")
        if text in all_manifest_texts:
            continue
        if (c["scoped_manifest_id"], c["claim_id"]) in constraint_absorbed_claim_ids:
            continue
        if text in uncited_sentence_texts:
            # Precedence rule 3 / D-INV-4 — uncited takes priority.
            continue
        drifts.append(
            _claim_drift_entry(
                drift_kind="EMITTED_NOT_INTENDED",
                claim_text=text,
                finding_id=next_finding_id(),
                now_iso=now_iso,
                manifest_claim_id=None,
                scoped_manifest_id=None,
                section_path=c.get("section_path", "unknown"),
            )
        )

    return drifts


# ---------------------------------------------------------------------------
# Public entry point.
# ---------------------------------------------------------------------------


def run_audit_pipeline(
    *,
    citations: list[dict[str, Any]],
    manifests: list[dict[str, Any]],
    # Reserved for the production retrieval-driver wiring per spec §4 step 2.
    # The current implementation injects retrieval via `retrieve_fn` so the
    # corpus is read inside that callback; keeping the parameter on the
    # signature lets the orchestrator pass corpus through without changing
    # the public API when the production retrieve_fn lands.
    corpus: list[dict[str, Any]] | None = None,
    config: dict[str, Any],
    retrieve_fn: Callable[[dict[str, Any]], dict[str, Any]],
    judge_fn: Callable[..., dict[str, Any]],
    audit_run_id: str,
    now_iso: str,
    cache: dict[str, Any] | None = None,
    uncited_sentences: list[dict[str, Any]] | None = None,
) -> dict[str, list[dict[str, Any]]]:
    """Run §4 Step 1-6 + manifest set-diff over caller-supplied inputs.

    The uncited token-rule detector (`scripts/uncited_assertion_detector.py`,
    §"Uncited-assertion detector (D4-c)" in claim_ref_alignment_audit_agent.md)
    is NOT invoked here. Callers are responsible for pre-processing raw
    draft sentences through `detect_uncited_assertions` BEFORE passing the
    candidate list to this function as `uncited_sentences`. This split is
    intentional: the pipeline owns the cited / drift / constraint-violation
    routing, the detector owns the D4-c three-condition classification
    (including the optional `adjacent_text` surrounding-clause filter
    added in Step 9). `scripts/test_e2e_claim_audit.py` exercises the full
    detector → pipeline → finalizer chain end-to-end.

    `uncited_sentences` items must be dicts with at least `sentence_text`,
    `section_path`, and `trigger_tokens` (non-empty per U-INV-2); when the
    caller has run them through `detect_uncited_assertions`, every required
    field is already populated.

    Returns:
        dict with six aggregate arrays keyed by passport-aggregate name:
        claim_audit_results, uncited_assertions, claim_drifts,
        constraint_violations, audit_sampling_summaries, plus
        claim_intent_manifests (echoed for downstream consumption).

    Raises:
        ValueError: when config validation fails (e.g. max_claims_per_paper <= 0).
    """
    # Intentional no-op: `corpus` is reserved for the production retrieval-driver
    # wiring (spec §4 step 2). Mark as read so static analysers (ruff ARG002,
    # mypy strict unused-arg) do not flag the forward-compat parameter.
    _ = corpus

    # ---- Config sanity ----
    cap = config.get("max_claims_per_paper", 100)
    if not isinstance(cap, int) or cap <= 0:
        raise ValueError(
            f"max_claims_per_paper must be positive integer; got {cap!r} "
            "(spec §4 step 3 + S-INV-2 / T-P11 cap=0 rejected)"
        )
    judge_model = config.get("judge_model", "gpt-5.5-xhigh")

    # Build the three lookup indexes once per run. Used by per-citation
    # constraint resolution + manifest-level absorption + drift detection.
    manifests_by_id: dict[str, dict[str, Any]] = {
        m["manifest_id"]: m for m in manifests if m.get("manifest_id")
    }
    claim_by_mc_id: dict[tuple[str, str], dict[str, Any]] = {
        (m["manifest_id"], claim["claim_id"]): claim
        for m in manifests
        if m.get("manifest_id")
        for claim in (m.get("claims") or [])
        if claim.get("claim_id")
    }
    mncs_by_manifest_id: dict[str, list[dict[str, Any]]] = {
        m["manifest_id"]: list(m.get("manifest_negative_constraints") or [])
        for m in manifests
        if m.get("manifest_id")
    }
    cache = cache if cache is not None else {}
    uncited_sentences = uncited_sentences or []

    # ---- Sampling decision ----
    total = len(citations)
    if total > cap:
        sampled_indices = _stratified_bucket_indices(total, cap)
        audited_citations = [citations[i] for i in sampled_indices]
        sampling_summaries = [
            {
                "audit_run_id": audit_run_id,
                "max_claims_per_paper": cap,
                "total_citation_count": total,
                "audited_count": len(sampled_indices),
                "audited_indices": sampled_indices,
                "sampling_strategy": SAMPLING_STRATEGY,
                "emitted_at": now_iso,
            }
        ]
    else:
        audited_citations = list(citations)
        sampling_summaries = []

    # ---- Per-citation §4 Step 1-6 ----
    claim_audit_results: list[dict[str, Any]] = []
    constraint_violations: list[dict[str, Any]] = []
    constraint_absorbed_claim_ids: set[tuple[str, str]] = set()

    def _written_scope_for(citation: dict[str, Any]) -> str:
        """Return the scoped_manifest_id that goes onto the claim_audit_result row.

        Step 7 codex R1 CO-2: a drifted-cited citation's `claim_id` is not in
        any manifest, but the citation still arrives with the active
        `scoped_manifest_id` for runtime constraint resolution (so global MNCs
        still apply per M-INV-3). The row written to the passport, however,
        MUST carry the sentinel manifest id whenever the (scope, claim_id)
        pair is not present in the manifest index — otherwise INV-15 dangling
        check rejects the passport. Runtime constraint lookup stays untouched
        (it reads citation.scoped_manifest_id directly); only the persisted
        row is normalized.
        """
        runtime_scope = citation.get("scoped_manifest_id", SENTINEL_MANIFEST_ID)
        cid = citation.get("claim_id")
        if runtime_scope == SENTINEL_MANIFEST_ID:
            return SENTINEL_MANIFEST_ID
        if (runtime_scope, cid) in claim_by_mc_id:
            return runtime_scope
        return SENTINEL_MANIFEST_ID

    for citation in audited_citations:
        anchor_kind = citation.get("anchor_kind")
        scoped_manifest_id = citation.get("scoped_manifest_id", SENTINEL_MANIFEST_ID)
        claim_id = citation.get("claim_id")
        written_scope = _written_scope_for(citation)

        # Step 1 — anchor=none firm-rule short-circuit.
        if anchor_kind == "none":
            entry = _anchorless_entry(
                citation,
                audit_run_id=audit_run_id,
                now_iso=now_iso,
                judge_model=judge_model,
            )
            entry["scoped_manifest_id"] = written_scope
            claim_audit_results.append(entry)
            continue

        # Step 2 — retrieval.
        retrieval = retrieve_fn(citation)
        method = retrieval["ref_retrieval_method"]
        excerpt = retrieval.get("retrieved_excerpt")

        if method in {"failed", "not_found", "audit_tool_failure"}:
            entry = _retrieval_failure_entry(
                citation,
                method=method,
                audit_run_id=audit_run_id,
                now_iso=now_iso,
                judge_model=judge_model,
                fault_class=retrieval.get("fault_class"),
            )
            entry["scoped_manifest_id"] = written_scope
            claim_audit_results.append(entry)
            continue

        if method not in {"api", "manual_pdf"}:
            raise ValueError(f"unexpected ref_retrieval_method: {method!r}")

        # Step 3 — cache lookup. Active constraints scoped by (manifest, claim).
        active_constraints = _active_constraints_for_claim(
            scoped_manifest_id=scoped_manifest_id,
            claim_id=claim_id,
            claim_by_mc_id=claim_by_mc_id,
            mncs_by_manifest_id=mncs_by_manifest_id,
        )
        key = _cache_key(
            claim_text=citation["claim_text"],
            ref_slug=citation["ref_slug"],
            anchor_kind=anchor_kind,
            anchor_value=citation.get("anchor_value", ""),
            retrieved_excerpt=excerpt,
            active_constraints=active_constraints,
            judge_model=judge_model,
        )
        cached = cache.get(key)
        if cached is not None:
            judge_result = cached
        else:
            # Step 4-5 — passage location is implicit (excerpt is the located passage);
            # invoke judge.
            judge_result = judge_fn(
                claim_text=citation["claim_text"],
                retrieved_excerpt=excerpt,
                anchor_kind=anchor_kind,
                anchor_value=citation.get("anchor_value", ""),
                active_constraints=active_constraints,
                judge_model=judge_model,
            )
            cache[key] = judge_result

        # Step 6 — defect_stage routing + emission.
        entry = _judge_result_entry(
            citation,
            judge_result=judge_result,
            ref_retrieval_method=method,
            audit_run_id=audit_run_id,
            now_iso=now_iso,
            judge_model=judge_model,
        )
        entry["scoped_manifest_id"] = written_scope
        claim_audit_results.append(entry)

        # Precedence rule 1: cited constraint violation absorbs the drift signal.
        # Spec §6 lint rule 6 + §7.2 T-P8: when a citation in this manifest
        # judges VIOLATED, that manifest's drift findings are absorbed in
        # full — the constraint violation has already surfaced the L3
        # faithfulness failure at HIGH-WARN, so layering LOW-WARN drift
        # noise on top of it just reports the same paper-level problem twice.
        # Absorption is manifest-scoped (not global) so VIOLATED in
        # manifest A does NOT silence legitimate drift signal in manifest B.
        if entry["defect_stage"] == "negative_constraint_violation":
            manifest = manifests_by_id.get(scoped_manifest_id)
            if manifest is not None:
                for claim in manifest.get("claims", []) or []:
                    cid_in_manifest = claim.get("claim_id")
                    if cid_in_manifest:
                        constraint_absorbed_claim_ids.add(
                            (scoped_manifest_id, cid_in_manifest)
                        )
            # Also absorb the emitted citation's own (manifest, claim) pair
            # so a drifted-yet-violated citation does not produce a
            # companion EMITTED_NOT_INTENDED row.
            constraint_absorbed_claim_ids.add((scoped_manifest_id, claim_id))

    # ---- Uncited assertion + uncited constraint-violation routing ----
    uncited_assertions: list[dict[str, Any]] = []
    ua_counter = 1
    cv_counter = 1
    uncited_sentence_texts: set[str] = set()

    for sentence in uncited_sentences:
        uncited_sentence_texts.add(sentence["sentence_text"])

        # Step 5 stream (d) — uncited claim AND MNC/NC scope match → run judge.
        scoped_manifest_id_for_sentence = sentence.get("scoped_manifest_id")
        applicable_constraints: list[dict[str, Any]] = []
        if scoped_manifest_id_for_sentence:
            applicable_constraints = _active_constraints_for_claim(
                scoped_manifest_id=scoped_manifest_id_for_sentence,
                claim_id=sentence.get("manifest_claim_id", ""),
                claim_by_mc_id=claim_by_mc_id,
                mncs_by_manifest_id=mncs_by_manifest_id,
            )

        if applicable_constraints:
            judge_result = judge_fn(
                claim_text=sentence["sentence_text"],
                retrieved_excerpt=None,
                anchor_kind=None,
                anchor_value=None,
                active_constraints=applicable_constraints,
                judge_model=judge_model,
            )
            if judge_result.get("judgment") == "VIOLATED":
                constraint_violations.append(
                    _constraint_violation_entry(
                        sentence=sentence,
                        judge_result=judge_result,
                        scoped_manifest_id=scoped_manifest_id_for_sentence,
                        finding_id=f"CV-{cv_counter:03d}",
                        judge_model=judge_model,
                        now_iso=now_iso,
                    )
                )
                cv_counter += 1

        # Always emit uncited_assertion (LOW-WARN advisory). CV-INV-4 explicitly
        # permits a sentence to appear in both uncited_assertions[] and
        # constraint_violations[] simultaneously.
        uncited_assertions.append(
            _uncited_assertion_entry(
                sentence=sentence,
                finding_id=f"UA-{ua_counter:03d}",
                now_iso=now_iso,
            )
        )
        ua_counter += 1

    # ---- Manifest set-diff drift detection ----
    cd_counter = 1

    def _next_cd() -> str:
        nonlocal cd_counter
        out = f"CD-{cd_counter:03d}"
        cd_counter += 1
        return out

    # Step 7 codex R1 CO-4: drift detection's emitted-side index MUST use
    # the FULL citation list, not the sampled subset. Sampling caps judge
    # invocations (spec §4 step 3) — it does NOT shrink the prose visible to
    # the manifest set-diff. Passing audited_citations here made every
    # unsampled-but-present citation look dropped from manifest, producing
    # false INTENDED_NOT_EMITTED rows in proportion to (total - cap).
    claim_drifts = _detect_drifts(
        manifests=manifests,
        emitted_citations=citations,
        uncited_sentence_texts=uncited_sentence_texts,
        constraint_absorbed_claim_ids=constraint_absorbed_claim_ids,
        now_iso=now_iso,
        next_finding_id=_next_cd,
    )

    return {
        "claim_intent_manifests": manifests,
        "claim_audit_results": claim_audit_results,
        "uncited_assertions": uncited_assertions,
        "claim_drifts": claim_drifts,
        "constraint_violations": constraint_violations,
        "audit_sampling_summaries": sampling_summaries,
    }
