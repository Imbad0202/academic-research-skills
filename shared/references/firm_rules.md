# Firm Rules — Canonical Source

This file is the **single source of truth** for firm-rule wording that is otherwise duplicated verbatim across agent prompts. Each block below is the canonical text; the agent prompts listed under "Mirrored in" carry a byte-identical copy (modulo the agent's self-reference noun, where noted). `scripts/check_firm_rules_sync.py` fails CI if any mirror drifts from the canonical block here.

**Why this file exists:** the contamination `R-L3-2-*` wording provably drifted between v3.9.0 (contamination-only) and v3.9.4 (contamination-AND-temporal) drafts before being single-sourced here. Manual 5×-duplication is not enough; the sync lint pins it.

**ID namespaces (do NOT confuse — they were overloaded until v3.10 PR-A):**

- `R-L3-2-*` = **contamination advisory** rules (origin: v3.7.3 spec §3.2 L3-2; extended v3.9.0 §3.3). Original holder of the `R-L3-2` ID.
- `R-CIM-*` = **Claim Intent Manifest emission** rules (origin: #103 claim-alignment spec; the agent prompts borrowed `R-L3-2-A/B/C` until v3.10 PR-A renamed them to remove the collision).
- `R-L3-1-*` = per-citation locator gate (v3.7.3 §3.1). Not mirrored here.

---

## Contamination advisory firm rules (R-L3-2-*)

> **Canonical wording note:** this is the **current (pre-v3.10-reword) wording**. v3.10 PR-B reword of R-L3-2-A to the broad contamination-AND-temporal form lands separately; until then, this is the source of truth and the mirrors match it exactly.

<!-- canonical:R-L3-2-A -->
- **R-L3-2-A (advisory only):** Contamination signals never block emission on their own. The user retains discretion. This follows the v3.5 Collaboration Depth Observer + v3.6.8 LOW-WARN precedent. Hard-gating on contamination would amount to refusing to cite mid-2024+ preprints en masse, which is too coarse.
<!-- /canonical:R-L3-2-A -->

<!-- canonical:R-L3-2-B -->
- **R-L3-2-B (no retroactive computation):** bibliography_agent computes contamination_signals at ingest time, not at audit time. Re-running the check post-hoc on existing entries is a separate batch operation (deferred to user invocation; not part of the cite-time finalizer).
<!-- /canonical:R-L3-2-B -->

<!-- canonical:R-L3-2-C -->
- **R-L3-2-C (triangulation count over present fields):** k is computed over `*_unmatched` fields that are present. Absent fields are excluded from the count and do not default to either `true` or `false`. k_max reflects how many lookups were successfully run; the (k, k_max) pair together determines the annotation tier.
<!-- /canonical:R-L3-2-C -->

<!-- canonical:R-L3-2-D -->
- **R-L3-2-D (no API-inferred classification):** OpenAlex's `primary_location.source.type` and Crossref's `type` fields, even when returned by the APIs for matched entries, MUST NOT be used to derive any classification (venue_type, scope category, hard-block eligibility). The k=3 case makes those classifications structurally unavailable; including them in any classification logic creates fake precision.
<!-- /canonical:R-L3-2-D -->

<!-- canonical:R-L3-2-E -->
- **R-L3-2-E (gate refusal list unchanged by advisory tiers):** All triangulation annotations are advisory. The terminal gate **refusal list** is NOT extended by any advisory marker shape. The gate's **advisory pass-through allowlist** MUST be extended in lockstep with any new advisory suffix so that new advisory suffixes are not accidentally routed through a refusal rule. The fix for a new advisory suffix is pass-through-list expansion, not refusal-list change.
<!-- /canonical:R-L3-2-E -->

**Mirrored in (contamination rules):**

- `academic-paper/agents/formatter_agent.md` — R-L3-2-A + R-L3-2-E (in the contamination pass-through paragraph).
- `deep-research/references/crossref_api_protocol.md` — R-L3-2-A (user-discretion reference).
- `deep-research/references/openalex_api_protocol.md` — R-L3-2-A reference.
- `academic-pipeline/agents/pipeline_orchestrator_agent.md` — R-L3-2-C / R-L3-2-D / R-L3-2-E (finalizer logic).
- `deep-research/agents/bibliography_agent.md` — R-L3-2-B (ingest-time computation).

> These mirrors are prose references, not full-block copies, so the sync lint does NOT wording-check them against the canonical blocks above — it only ID-guards the contamination side (asserting no contamination context reuses an `R-CIM-*` ID, and no claim-manifest surface reuses an `R-L3-2-*` ID). Wording drift on a contamination mirror is therefore NOT caught yet; full-block wording-sync for the contamination side lands with the v3.10 PR-B reword, which makes these mirrors full-block copies. (Wording-sync IS enforced today for the `R-CIM-*` blocks below, whose mirrors are full-block copies.)

---

## Claim Intent Manifest emission firm rules (R-CIM-*)

> Renamed from `R-L3-2-A/B/C` in v3.10 PR-A to remove the ID collision with the contamination rules above. The three writing-stage agents emit a claim intent manifest; the only difference between mirrors is the agent's self-reference noun ("synthesis agent" / "compiler" / "writer"), which the sync lint normalizes before comparison.

<!-- canonical:R-CIM-A -->
- **R-CIM-A (one-shot pre-commitment):** Emit exactly ONE manifest entry per <AGENT> invocation, BEFORE the first prose block. No later mutation, no append, no re-emission within the same invocation. Drafting that introduces a claim not in the manifest produces a `claim_drifts[]` entry with `drift_kind=EMITTED_NOT_INTENDED` downstream — that detection is the design intent (drift is surfaced, not silenced). The manifest is the pre-commitment artifact the audit diffs against; rewriting it mid-draft would hide the signal.
<!-- /canonical:R-CIM-A -->

<!-- canonical:R-CIM-B -->
- **R-CIM-B (no audit responsibility):** The <AGENT> emits manifests; it does NOT detect drift, re-judge supported / unsupported, or read other manifests. The §"Manifest cross-reference (D6)" set-diff lives in `claim_ref_alignment_audit_agent.md`. Mirrors the v3.6.7 partial-inversion discipline: narrative-side emits, audit-side reads.
<!-- /canonical:R-CIM-B -->

<!-- canonical:R-CIM-C -->
- **R-CIM-C (no frontmatter reading):** Generate `claim_text`, `intended_evidence_kind`, `planned_refs`, and any `negative_constraints[].rule` values from the corpus + prompt context already provided. You MUST NOT read entry frontmatter to discover candidate claims — the same partial-inversion rule that gates anchor selection in v3.7.3 R-L3-1-C. The orchestrator allocates a fresh `manifest_id` per invocation (M-INV-4); never copy a `manifest_id` from a sibling manifest.
<!-- /canonical:R-CIM-C -->

**Mirrored in (claim-manifest rules):**

- `deep-research/agents/synthesis_agent.md` (`<AGENT>` = "synthesis agent")
- `deep-research/agents/report_compiler_agent.md` (`<AGENT>` = "compiler"; R-CIM-B carries an extra standalone-mode sentence — see prompt)
- `academic-paper/agents/draft_writer_agent.md` (`<AGENT>` = "writer")
- `shared/contracts/passport/claim_intent_manifest.schema.json` — references `R-CIM-A` by ID in the `claims` field description.

---

## Collision guard

`scripts/check_firm_rules_sync.py` additionally asserts:

1. No `R-L3-2-A/B/C` token appears inside any `## Claim Intent Manifest Emission` prompt section or inside `claim_intent_manifest.schema.json`.
2. No `R-CIM-A/B/C` token appears inside any contamination context (formatter pass-through paragraph, crossref/openalex protocol, finalizer logic, contamination specs).

This pins the v3.10 PR-A disambiguation against regression.
