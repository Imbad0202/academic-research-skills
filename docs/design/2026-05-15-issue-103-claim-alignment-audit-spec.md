# ARS v3.8 — Issue #103 `claim_ref_alignment_audit_agent` Implementation Spec

**Date:** 2026-05-15
**Issue:** [#103](https://github.com/Imbad0202/academic-research-skills/issues/103)
**Companion decision doc:** `2026-05-15-issue-103-claim-alignment-audit-decision.md`
**Target release:** v3.8

This spec implements the eight decisions in the companion decision doc. Read the decision doc first — it carries the load-bearing reasons; this spec carries the executable surface.

---

## 1. In-scope deliverables

Numbered list aligned to the implementation surfaces in #103 issue body + decision-doc adjustments.

1. **`academic-pipeline/agents/claim_ref_alignment_audit_agent.md`** — new agent prompt. Estimated 350-500 lines.
2. **`shared/contracts/passport/claim_audit_result.schema.json`** — per-claim audit result entry schema.
3. **`shared/contracts/passport/claim_intent_manifest.schema.json`** — per-agent-invocation manifest entry schema.
3a. **`shared/contracts/passport/uncited_assertion.schema.json`** — per uncited-sentence finding entry schema (separate from `claim_audit_result` because there's no `ref_slug` to bind).
4. **`academic-pipeline/agents/pipeline_orchestrator_agent.md`** — new §3.6 "Claim-Faithfulness Audit Gate (v3.8)". Dispatch wiring for the new agent. Finalizer integration extended to 7-row + advisory tier.
5. **`academic-paper/agents/formatter_agent.md`** — Cite-Time Provenance Hard Gate extended with HIGH-WARN-CLAIM-NOT-SUPPORTED + HIGH-WARN-NEGATIVE-CONSTRAINT-VIOLATION tiers.
6. **`academic-paper/agents/draft_writer_agent.md`** + **`deep-research/agents/synthesis_agent.md`** + **`deep-research/agents/report_compiler_agent.md`** — new "Claim Intent Manifest Emission (v3.8)" sibling heading following the existing v3.7.3 "Three-Layer Citation Emission" heading. PATTERN PROTECTION (v3.6.7) blocks stay byte-equivalent.
7. **`academic-pipeline/references/claim_audit_calibration_protocol.md`** — new file (modeled on `shared/contracts/reviewer/` calibration convention).
8. **`scripts/check_claim_audit_consistency.py`** — new lint enforcing per-claim invariants (anchor presence, defect_stage presence, precedence rules, audit_status/defect_stage coherence).
9. **CI wiring** — extend `.github/workflows/spec-consistency.yml` (or matching workflow) to call the new lint.
10. **Tests** — `scripts/test_check_claim_audit_consistency.py` (lint coverage), schema validation tests against fixture passports, end-to-end synthetic-paper test (5 citations, 1 intentionally fabricated, audit catches).
11. **CHANGELOG entry** + ROADMAP §3.8 anchor + decision-log entry.

## 2. Out of scope

Restated from decision doc §4, for cross-reference:

- RubricEM reflection meta-policy (post-v3.8)
- Evolving rubric buffer (post-v3.8)
- Rubric discrimination-power audit (→ #89)
- `defect_stage` accuracy measurement (→ #89 / gold fixtures)
- L3-2 contamination signals (→ #105 closed / #102 v3.7.4)
- Cross-paper claim-graph analysis (no issue yet; post-v3.8)

## 3. Schemas

### 3.1 `claim_audit_result.schema.json`

Per-claim audit result. One entry per audited citation in the passport `claim_audit_results[]` aggregate array.

**Required fields:**

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/Imbad0202/academic-research-skills/shared/contracts/passport/claim_audit_result.schema.json",
  "title": "Material Passport Claim Audit Result Entry",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "claim_id",
    "claim_text",
    "ref_slug",
    "anchor_kind",
    "anchor_value",
    "judgment",
    "audit_status",
    "defect_stage",
    "rationale",
    "judge_model",
    "judge_run_at",
    "ref_retrieval_method"
  ],
  "properties": {
    "claim_id": { "type": "string", "pattern": "^C-[0-9]{3,}$" },
    "claim_text": { "type": "string", "minLength": 1, "maxLength": 2000 },
    "ref_slug": { "type": "string", "minLength": 1 },
    "anchor_kind": { "enum": ["quote", "page", "section", "paragraph", "none"] },
    "anchor_value": { "type": "string" },
    "judgment": { "enum": ["SUPPORTED", "UNSUPPORTED", "AMBIGUOUS", "RETRIEVAL_FAILED"] },
    "audit_status": { "enum": ["completed", "inconclusive"] },
    "defect_stage": {
      "enum": [
        "retrieval_existence",
        "metadata",
        "source_description",
        "claim_intent",
        "citation_anchor",
        "synthesis_overclaim",
        "negative_constraint_violation",
        "uncited_assertion",
        "not_applicable",
        null
      ]
    },
    "rationale": { "type": "string", "minLength": 1, "maxLength": 2000 },
    "judge_model": { "type": "string", "minLength": 1 },
    "judge_run_at": { "type": "string", "format": "date-time" },
    "ref_retrieval_method": { "enum": ["api", "manual_pdf", "failed", "not_attempted", "not_found"] },
    "upstream_owner_agent": {
      "enum": [
        "bibliography_agent",
        "synthesis_agent",
        "draft_writer_agent",
        "report_compiler_agent",
        null
      ]
    },
    "violated_constraint_id": {
      "type": ["string", "null"],
      "pattern": "^(NC-C[0-9]{3,}-[0-9]+|MNC-[0-9]+)$"
    },
    "upstream_dispute": {
      "type": ["string", "null"],
      "maxLength": 1000
    },
    "audit_run_id": {
      "type": "string",
      "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z-[0-9a-f]{4}$"
    }
  }
}
```

**Allowed (`judgment`, `audit_status`, `defect_stage`) matrix (enforced in `check_claim_audit_consistency.py`, NOT in schema). Any combination outside the table is a lint violation:**

| `judgment` | `audit_status` | `defect_stage` | Notes |
|---|---|---|---|
| SUPPORTED | completed | `null` | INV-1 |
| AMBIGUOUS | completed | source_description, citation_anchor, synthesis_overclaim, or `null` | drift never AMBIGUOUS; constraints binary |
| UNSUPPORTED | completed | source_description | wrong paraphrase of source content |
| UNSUPPORTED | completed | metadata | reference exists but author/year/title wrong |
| UNSUPPORTED | completed | citation_anchor | source correct, anchor points to wrong passage |
| UNSUPPORTED | completed | synthesis_overclaim | source correct, draft over-strengthens claim |
| UNSUPPORTED | completed | claim_intent | drift from `claim_intent_manifest`; severity tier handled by finalizer mapping (see §5) — schema admits both LOW-WARN-CLAIM-DRIFT and HIGH-WARN-CLAIM-NOT-SUPPORTED outcomes downstream |
| UNSUPPORTED | completed | negative_constraint_violation | INV-8, requires `violated_constraint_id` |
| RETRIEVAL_FAILED | completed | retrieval_existence | reference genuinely does not exist (fabricated) |
| RETRIEVAL_FAILED | inconclusive | not_applicable | covers (a) anchor=none INV-6 and (b) paywalled INV-10 |

**`uncited_assertion` is NOT a `claim_audit_result` row** — uncited claims have no `ref_slug` to populate the required field. They emit into a separate aggregate `uncited_assertions[]` (schema in §3.3 below) and feed the same Stage 4→5 finalizer integration. This sidesteps a schema-vs-required-field deadlock: `claim_audit_result.ref_slug` stays required for citation-bound audits; `uncited_assertions[]` carries its own entry-type schema with no `ref_slug` field.

**Cross-field invariants:**

- INV-1: `judgment=SUPPORTED` → `defect_stage=null` AND `violated_constraint_id=null` AND `audit_status=completed`
- INV-2: `judgment=UNSUPPORTED` → `defect_stage` ∈ `{source_description, metadata, citation_anchor, synthesis_overclaim, claim_intent, negative_constraint_violation}` AND `defect_stage ≠ null` AND `audit_status=completed`
- INV-3: `judgment=AMBIGUOUS` → `defect_stage` ∈ `{source_description, citation_anchor, synthesis_overclaim, null}` AND `audit_status=completed` (drift excluded — drift is unambiguous when manifest exists; metadata excluded — bibliographic correctness is binary; constraint violations excluded — INV-8 binary)
- INV-4: `judgment=RETRIEVAL_FAILED` AND `audit_status=inconclusive` → `defect_stage=not_applicable`
- INV-5: `judgment=RETRIEVAL_FAILED` AND `audit_status=completed` → `defect_stage=retrieval_existence` (reference genuinely does not exist, distinct from tool failure)
- INV-6: `anchor_kind=none` → `judgment=RETRIEVAL_FAILED`, `audit_status=inconclusive`, `defect_stage=not_applicable`, `ref_retrieval_method=not_attempted`, rationale begins with `v3.7.3 R-L3-1-A violation` (per D1)
- INV-7: `defect_stage=negative_constraint_violation` → `violated_constraint_id ≠ null`
- INV-8: `defect_stage=negative_constraint_violation` ↔ `judgment=UNSUPPORTED` (negative-constraint violations are always classified UNSUPPORTED, never AMBIGUOUS — explicit author rules are binary)
- INV-9: `upstream_dispute ≠ null` → `defect_stage ≠ null` AND `defect_stage ≠ not_applicable` (disputes are only meaningful for substantive defect classifications)
- INV-10: `ref_retrieval_method=failed` → `judgment=RETRIEVAL_FAILED` AND `audit_status=inconclusive` AND `defect_stage=not_applicable` (paywall path)
- INV-11: `ref_retrieval_method=not_attempted` ↔ `anchor_kind=none` AND INV-6 holds (anchor=none skips retrieval)
- INV-12: `ref_retrieval_method=not_found` ↔ `judgment=RETRIEVAL_FAILED` AND `audit_status=completed` AND `defect_stage=retrieval_existence` (fabricated reference path)
- INV-13: `defect_stage=metadata` → `judgment=UNSUPPORTED` AND `audit_status=completed` AND `ref_retrieval_method` ∈ `{api, manual_pdf}` (retrieval succeeded but metadata mismatch identified during judging)

### 3.2 `claim_intent_manifest.schema.json`

One entry per generating-agent invocation. Emitted by `synthesis_agent` / `draft_writer_agent` / `report_compiler_agent` after paper-visible context loads but before prose generation.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/Imbad0202/academic-research-skills/shared/contracts/passport/claim_intent_manifest.schema.json",
  "title": "Material Passport Claim Intent Manifest Entry",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "manifest_version",
    "emitted_by",
    "emitted_at",
    "claims",
    "manifest_negative_constraints"
  ],
  "properties": {
    "manifest_version": { "const": "1.0" },
    "emitted_by": { "enum": ["synthesis_agent", "draft_writer_agent", "report_compiler_agent"] },
    "emitted_at": { "type": "string", "format": "date-time" },
    "session_id": { "type": "string" },
    "claims": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["claim_id", "claim_text", "intended_evidence_kind", "planned_refs"],
        "properties": {
          "claim_id": { "type": "string", "pattern": "^C-[0-9]{3,}$" },
          "claim_text": { "type": "string", "minLength": 1, "maxLength": 2000 },
          "intended_evidence_kind": { "enum": ["empirical", "theoretical", "definitional", "normative"] },
          "planned_refs": { "type": "array", "items": { "type": "string" }, "minItems": 0 },
          "negative_constraints": {
            "type": "array",
            "items": {
              "type": "object",
              "additionalProperties": false,
              "required": ["constraint_id", "rule"],
              "properties": {
                "constraint_id": { "type": "string", "pattern": "^NC-C[0-9]{3,}-[0-9]+$" },
                "rule": { "type": "string", "minLength": 1, "maxLength": 500 }
              }
            }
          }
        }
      }
    },
    "manifest_negative_constraints": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": ["constraint_id", "rule"],
        "properties": {
          "constraint_id": { "type": "string", "pattern": "^MNC-[0-9]+$" },
          "rule": { "type": "string", "minLength": 1, "maxLength": 500 }
        }
      }
    }
  }
}
```

**Cross-field invariants** (lint-enforced):
- M-INV-1: `claim_id` uniqueness across all `claims[].claim_id` in one manifest
- M-INV-2: `constraint_id` of `NC-C{n}-{m}` form MUST appear under `claims[]` entry where `claim_id=C-{n}` (i.e., claim-level constraint scoping)
- M-INV-3: `MNC-{m}` constraints in `manifest_negative_constraints` are globally applied; cannot be overridden by claim-level NC (claim-level can ADD, never DROP global)

### 3.3 `uncited_assertion.schema.json`

Per uncited-assertion finding. One entry per sentence in the draft that the D4-c three-condition token rule flagged. Aggregated as `uncited_assertions[]` in the orchestrator passport-tracking, parallel to `claim_audit_results[]`.

The separate schema exists because `uncited_assertion` findings have no `ref_slug` to fill — they describe sentences that *should* have a citation but don't. Embedding them in `claim_audit_result` would either force a sentinel `ref_slug` value or relax the required-field rule, both of which fight the schema's grain.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://github.com/Imbad0202/academic-research-skills/shared/contracts/passport/uncited_assertion.schema.json",
  "title": "Material Passport Uncited Assertion Entry",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "finding_id",
    "sentence_text",
    "section_path",
    "trigger_tokens",
    "detected_at",
    "rule_version"
  ],
  "properties": {
    "finding_id": { "type": "string", "pattern": "^UA-[0-9]{3,}$" },
    "sentence_text": { "type": "string", "minLength": 1, "maxLength": 2000 },
    "section_path": { "type": "string", "minLength": 1, "description": "Hierarchical path from document root to the section containing the sentence, e.g. '2. Methods > 2.3 Sampling'" },
    "trigger_tokens": {
      "type": "array",
      "minItems": 1,
      "items": { "type": "string" },
      "description": "Concrete tokens that matched D4-c condition 1 (quantifiers or empirical-claim verbs). E.g. ['67%', 'showed']."
    },
    "detected_at": { "type": "string", "format": "date-time" },
    "rule_version": { "const": "D4-c-v1" },
    "upstream_owner_agent": {
      "enum": ["synthesis_agent", "draft_writer_agent", "report_compiler_agent", null]
    },
    "manifest_claim_id": {
      "type": ["string", "null"],
      "pattern": "^C-[0-9]{3,}$",
      "description": "When the uncited sentence corresponds to a claim_id in the active claim_intent_manifest. Per D4-c last paragraph: manifest membership does NOT exempt a sentence from being flagged."
    }
  }
}
```

**Cross-field invariants** (lint-enforced in `check_claim_audit_consistency.py`):
- U-INV-1: `finding_id` uniqueness across `uncited_assertions[]` in one passport
- U-INV-2: `trigger_tokens` non-empty (rule fires only when condition 1 matches)
- U-INV-3: `rule_version` must equal `D4-c-v1` for v3.8.0 release; future rule revisions bump the const and require re-lint
- U-INV-4: When `manifest_claim_id ≠ null`, the referenced `C-{n}` MUST exist in the active manifest (cross-array consistency check)

## 4. Agent prompt structure: `claim_ref_alignment_audit_agent.md`

Sections (in order):

1. **Purpose & v3.8 placement** — single paragraph naming L3 audit role, dependency on v3.7.3 anchor input, audit-not-arbitration boundary.
2. **PATTERN PROTECTION (v3.6.7)** — byte-equivalent block to existing audited-agents pattern protection convention. Prevents cascading edits.
3. **Input contract** — exact passport fields read; `claim_audit_config` keys consumed (max_claims_per_paper, judge_model, gold_set_path, cache_dir).
4. **Audit pipeline (6 steps)**:
   - Step 1 — Anchor presence check (D1, INV-6 firm rule).
   - Step 2 — Reference retrieval (`api` → `manual_pdf` → `failed`/`not_found`). LOW-WARN on `failed` (D2 paywall). Sets `ref_retrieval_method` + carries `retrieved_excerpt` forward.
   - Step 3 — Cache lookup keyed by `(claim_text_hash, ref_slug, anchor_kind, anchor_value_hash, retrieved_excerpt_hash, judge_model)`. Lookup runs AFTER retrieval so the cached judgment is bound to the exact source text the judge will see — if the user re-runs after uploading a manual PDF or correcting the corpus entry, the excerpt hash changes and the cache miss forces fresh judging. On hit: return cached judgment + rationale + judge_model + cached_at. On miss: proceed to Step 4-5 then write back.
   - Step 4 — Passage location using anchor_value (quote = exact match; page/section/paragraph = scoped retrieval).
   - Step 5 — Judge invocation with prompt template. Output one of SUPPORTED/UNSUPPORTED/AMBIGUOUS, with rationale.
   - Step 6 — Defect_stage classification (8-category matrix + precedence rules, restated from issue body).
5. **Manifest cross-reference (D6)** — three-set diff: `intended_claims` ∩ `emitted_claims` ∩ `supported_claims`. Drift/dropped/violation classification. Advisory (D4-a).
6. **Uncited-assertion detector (D4-c)** — 3-condition token rule. Pseudocode included.
7. **Output emission** — one `claim_audit_result` entry per audited citation, plus aggregate counts emitted in pipeline-orchestrator Stage 6 reflection report.
8. **Calibration mode** — opt-in flow per `claim_audit_calibration_protocol.md`. Gold-set ingestion → judge run → FNR/FPR computation → user-facing report.
9. **Error handling** — judge timeout / API failure / cache corruption. Fall back to RETRIEVAL_FAILED with rationale.
10. **Cross-references** — Zhao 2026 §1, RubricEM Borrows 1+2, v3.7.3 anchor input contract, v3.6.7 PATTERN PROTECTION convention.

**Judge prompt template** (canonical form, embedded in agent prompt):

> Given this claim from a paper draft and this excerpt from the cited reference, does the reference support the claim?
>
> CLAIM: {claim_text}
> CITED REFERENCE EXCERPT: {retrieved_excerpt}
> ANCHOR KIND: {anchor_kind}
> ANCHOR VALUE: {anchor_value}
>
> Output ONE of:
> - SUPPORTED — the reference directly supports the claim
> - UNSUPPORTED — the reference does NOT support the claim (the cited source says something different or contradictory)
> - AMBIGUOUS — the reference is related but does not clearly support or contradict the claim
>
> Then output ONE SENTENCE rationale.
>
> Format: `JUDGMENT: <one-of>\nRATIONALE: <one sentence>`

**Negative-constraint judge prompt template** (extended form):

> Given this claim and the author's declared negative constraint, does the claim violate the constraint?
>
> CLAIM: {claim_text}
> CONSTRAINT: {constraint_rule}
>
> Output ONE of: VIOLATED, NOT_VIOLATED
> Then output ONE SENTENCE rationale.

VIOLATED → `judgment=UNSUPPORTED, defect_stage=negative_constraint_violation, violated_constraint_id={constraint_id}` per INV-8.

## 5. Orchestrator integration: `pipeline_orchestrator_agent.md` §3.6

New section "Claim-Faithfulness Audit Gate (v3.8)". Mirrors §3.5 Audit Artifact Gate structure but for claim-level audit.

**Trigger boundary:** Stage 4 → Stage 5 transition, in the same handoff slot as the v3.7.1 Cite-Time Provenance Finalizer. The audit dispatches AFTER the Cite-Time Provenance Finalizer pass (which resolves anchor-presence per v3.7.3 §3.1 and the 5-cell matrix) and BEFORE `formatter_agent` runs its hard gate at the start of Stage 5. This ordering mirrors §3.5 v3.6.7 audit gate (audit between deliverable completion and downstream consumption).

**Why not Stage 5→6:** `formatter_agent`'s terminal hard gate runs **during** Stage 5 (per orchestrator §"Cite-Time Provenance Finalizer (v3.7.1)" — formatter consumes finalizer output and refuses on `[UNVERIFIED CITATION ...]`). If the claim audit dispatches at Stage 5→6, `claim_audit_results[]` would be produced after the terminal gate has already passed; HIGH-WARN-CLAIM-NOT-SUPPORTED could not block output. The Stage 4→5 slot is the only place where (a) the draft prose with v3.7.3 anchors exists, (b) the cite finalizer has run so anchor presence is settled, and (c) the formatter hard gate has NOT yet run.

The audit agent receives:
- All in-text citations with their resolved `<!--ref:slug ...-->` + `<!--anchor:...-->` marker pairs (post-finalizer)
- The `claim_intent_manifests[]` aggregate from the writing-stage agents
- The `literature_corpus[]` aggregate (for retrieval)

**Outputs feeding formatter hard gate (same Stage 5 pass):**
- `claim_audit_results[]` array (one per audited citation) — consumed by `formatter_agent`'s extended hard gate
- Per-citation annotations injected adjacent to the existing v3.7.1 finalizer annotations (HIGH-WARN classes block; LOW-WARN advisory passes)

**Outputs feeding Stage 6 self-reflection:**
- Per-stage `defect_stage` histogram appendix (renders when ≥ 5 completed entries) — added to the existing Stage 6 AI Self-Reflection Report after gate pass

**Finalizer matrix extension (7-row):**

Existing v3.7.3 5-cell matrix (anchor presence + 4-cell trust state) gains a new finalizer pass that overlays per-citation audit annotations from `claim_audit_results[]`. Rows are evaluated top-to-bottom, first match wins:

| `judgment` | `defect_stage` | Annotation | Severity Tier | Gate behavior |
|---|---|---|---|---|
| SUPPORTED | `null` | (no annotation) | — | pass |
| AMBIGUOUS | source_description / citation_anchor / synthesis_overclaim / null | `[CLAIM-AUDIT-AMBIGUOUS]` | LOW-WARN advisory | pass |
| UNSUPPORTED | claim_intent | `[LOW-WARN-CLAIM-DRIFT]` | LOW-WARN advisory | pass (per D4-a — manifest drift is advisory, not blocking) |
| UNSUPPORTED | source_description / metadata / citation_anchor / synthesis_overclaim | `[HIGH-WARN-CLAIM-NOT-SUPPORTED]` | HIGH-WARN | gate-refuse |
| UNSUPPORTED | negative_constraint_violation | `[HIGH-WARN-NEGATIVE-CONSTRAINT-VIOLATION ({violated_constraint_id})]` | HIGH-WARN | gate-refuse (per D4-a — explicit author rules are stronger than drift) |
| RETRIEVAL_FAILED | retrieval_existence | `[HIGH-WARN-FABRICATED-REFERENCE]` | HIGH-WARN | gate-refuse (escapes v3.7.4 Vector 3 surfaces here) |
| RETRIEVAL_FAILED | not_applicable | `[CLAIM-AUDIT-UNVERIFIED — REFERENCE FULL-TEXT NOT RETRIEVABLE]` | LOW-WARN advisory | pass |

**`uncited_assertion` entries** (separate aggregate `uncited_assertions[]`) emit at LOW-WARN tier with annotation `[UNCITED-ASSERTION]` next to the offending sentence. Always advisory; gate-refuse reserved for citation-level defects. See §3.3 for entry schema.

**Why claim_intent → LOW-WARN (per D4-a):** The decision doc rejected "manifest authority blocking" because normal drafting routinely refines claims away from manifest, and gate-refusing on drift would block valid revision passes. The matrix preserves that decision: claim_intent defects are detected and annotated (so the user sees them) but never block. Source-level defects (source_description / metadata / citation_anchor / synthesis_overclaim) remain HIGH-WARN because they indicate the prose is misrepresenting the cited source, which is the L3 faithfulness failure the audit exists to catch. Constraint violations remain HIGH-WARN because the author explicitly declared "MUST NOT".

**Uncited-assertion** results emit at LOW-WARN tier with annotation `[UNCITED-ASSERTION]` next to the offending sentence. Always advisory; gate-refuse reserved for citation-level defects.

**`/ars-mark-read` behavior:** Does NOT acknowledge HIGH-WARN-CLAIM-NOT-SUPPORTED or HIGH-WARN-NEGATIVE-CONSTRAINT-VIOLATION. Remediation: user fixes the prose (re-cites, drops claim, revises). Mirrors v3.7.3 R-L3-1-A asymmetry (locator is structural, not evidence-state).

**Mode flag:** Audit agent dispatch is **opt-in** per pipeline run, configurable in `academic-pipeline/SKILL.md` mode flags. Default OFF for v3.8.0; ramp-on plan deferred to post-calibration calibration evidence.

## 6. Lint: `scripts/check_claim_audit_consistency.py`

Coverage:

1. **Schema validation** — `claim_audit_result.schema.json`, `claim_intent_manifest.schema.json`, `uncited_assertion.schema.json` all valid JSON Schema; sample passports validate.
2. **Cross-field invariants INV-1 through INV-13** — one test case per invariant, each with positive + negative fixture.
3. **Manifest invariants M-INV-1 through M-INV-3**.
4. **Uncited-assertion invariants U-INV-1 through U-INV-4** — including cross-array `manifest_claim_id` integrity (uncited entry's referenced C-{n} must exist in active manifest).
5. **Allowed-matrix coverage** — every `(judgment, audit_status, defect_stage)` triple outside §3.1 table rejected; representative disallowed combinations (≥ 5) tested explicitly.
6. **Precedence rules** — negative_constraint_violation > claim_intent (per issue body precedence rule 1); citation_anchor distinct from source_description (rule 2); uncited-sentence cases produce `uncited_assertions[]` entry, not a `claim_audit_result` row (rule 3 — uncited has no ref to evaluate).
7. **Acceptance check** — for any passport with ≥ 1 completed non-SUPPORTED `claim_audit_result`, ALL must emit a `defect_stage` ≠ null AND ≠ not_applicable (100% emission per #103 acceptance criterion).
8. **Coverage check** — sample passport with full 7-row finalizer matrix coverage (per §5); each annotation tier exercised at least once.

Lint exit codes: 0 (pass), 1 (one or more invariant violations; prints which + offending entry).

CI: invoked from `.github/workflows/spec-consistency.yml` (or matching workflow). Failure blocks merge.

## 7. TDD test plan

Tests written BEFORE production code per `superpowers:test-driven-development`. Order:

### 7.1 Schema validation tests (`tests/test_claim_audit_schema.py`)

- T-S1: Valid minimal entry validates (SUPPORTED, all required fields)
- T-S2: Each invariant INV-1..INV-13 covered by paired positive/negative fixture
- T-S3: `anchor_kind=none` entry that doesn't follow INV-6 fails lint (rationale missing prefix; `ref_retrieval_method ≠ not_attempted`)
- T-S4: Manifest M-INV-1 duplicate claim_id rejected
- T-S5: Manifest M-INV-2 dangling NC-C{n}-{m} (no parent claim) rejected
- T-S6: Manifest M-INV-3 claim-level constraint attempting to override MNC rejected
- T-S7: `uncited_assertion` U-INV-1..U-INV-4 covered by paired positive/negative fixture (rule_version literal; trigger_tokens non-empty; cross-array manifest_claim_id integrity)
- T-S8: `(judgment, audit_status, defect_stage)` allowed-matrix exhaustive coverage: each table row in §3.1 has a positive fixture, AND at least 5 representative disallowed combinations rejected (e.g., SUPPORTED + non-null defect_stage; UNSUPPORTED + null defect_stage; RETRIEVAL_FAILED + completed + not_applicable)

### 7.2 Audit-pipeline unit tests (`tests/test_claim_audit_pipeline.py`)

- T-P1: Step 1 — anchor=none input emits RETRIEVAL_FAILED/inconclusive/not_applicable + `ref_retrieval_method=not_attempted` with INV-6 rationale prefix, skips judge
- T-P2: Step 3 — cache hit (with matching `retrieved_excerpt_hash`) returns previously-judged result without invoking judge
- T-P3: Step 3 — cache miss (different `retrieved_excerpt_hash` after user uploads manual PDF) invokes judge then writes back
- T-P4: Step 2 — `ref_retrieval_method=failed` → LOW-WARN advisory path (D2 paywall)
- T-P5: Step 2 — `ref_retrieval_method=manual_pdf` accepted; `not_found` triggers `defect_stage=retrieval_existence`
- T-P6: Step 5 — judge VIOLATED → UNSUPPORTED + defect_stage=negative_constraint_violation + violated_constraint_id populated
- T-P7: Step 6 — 7 in-table defect_stage classifications each have a fixture mapping (`retrieval_existence`, `metadata`, `source_description`, `claim_intent`, `citation_anchor`, `synthesis_overclaim`, `negative_constraint_violation`). `uncited_assertion` is tested separately in §7.4 (it's a separate entry-type, not a defect_stage of `claim_audit_result`); `not_applicable` is tested in T-P1 and T-P4.
- T-P8: Precedence rule 1 — claim that drifts AND violates a constraint → defect_stage=negative_constraint_violation (not claim_intent)
- T-P9: Precedence rule 2 — citation_anchor distinct from source_description (anchor wrong, source description correct)
- T-P10: Precedence rule 3 — sentence that would be both an uncited_assertion AND a drifted manifest claim emits an `uncited_assertions[]` entry (no source-level evaluation, since there's no ref to evaluate). The same sentence may still appear in manifest diff diagnostics but does NOT produce a `claim_audit_result` row.

### 7.3 Manifest tests (`tests/test_claim_intent_manifest.py`)

- T-M1: Three-set diff — emitted ∩ intended ∩ supported, drift detection
- T-M2: Missing manifest → MANIFEST-MISSING advisory + claim-extraction-from-draft fallback, all defect_stages still emit
- T-M3: Constraint inheritance — MNC applies even when not redeclared at claim level

### 7.4 Uncited-assertion tests (`tests/test_uncited_assertion.py`)

- T-U1: Sentence with quantifier + no ref → uncited_assertion candidate
- T-U2: Definition sentence (contains "refers to") → NOT candidate
- T-U3: Methods boilerplate list → NOT candidate
- T-U4: Empirical claim ("showed X%") without ref → candidate
- T-U5: Claim in manifest but no ref → still candidate (D4-c last paragraph)

### 7.5 Finalizer integration tests (`tests/test_claim_audit_finalizer.py`)

- T-F1: 7-row matrix coverage — each (judgment, defect_stage) pair maps to correct annotation
- T-F2: HIGH-WARN-CLAIM-NOT-SUPPORTED triggers terminal gate refuse
- T-F3: `/ars-mark-read` does NOT clear HIGH-WARN-CLAIM-NOT-SUPPORTED (asymmetry preservation)
- T-F4: LOW-WARN-CLAIM-AUDIT-UNVERIFIED passes gate
- T-F5: Stage 6 reflection report renders histogram when ≥ 5 completed entries

### 7.6 End-to-end test (`tests/test_e2e_claim_audit.py`)

Synthetic 5-citation paper:
- Citation 1: real, SUPPORTED → no annotation
- Citation 2: real, AMBIGUOUS → LOW-WARN
- Citation 3: real but misused (source says inverse) → HIGH-WARN-CLAIM-NOT-SUPPORTED, gate refuses
- Citation 4: paywalled, retrieval fails → LOW-WARN-UNVERIFIED, passes gate
- Citation 5: violates declared negative constraint → HIGH-WARN-NEGATIVE-CONSTRAINT-VIOLATION, gate refuses

Test asserts: gate refuses output; only citations 3+5 are blockers; correcting them clears refusal.

### 7.7 Calibration mode test (`tests/test_claim_audit_calibration.py`)

Synthetic 20-tuple gold set covering SUPPORTED/UNSUPPORTED/AMBIGUOUS/violated-constraint judgments. Test asserts FNR < 0.15 and FPR < 0.10 thresholds are reported (not enforced; reporting is the unit of acceptance).

### 7.8 Regression test

Run existing 967+ test baseline (1107 unittest + 201 pytest adapters per session handoff). Zero regression required.

## 8. Cascade impact assessment

Files that may need touch:

| File | Why | Risk |
|---|---|---|
| `academic-pipeline/agents/pipeline_orchestrator_agent.md` | New §3.6 dispatch wiring | HIGH — already 712 lines; PATTERN PROTECTION block must stay byte-equivalent |
| `academic-paper/agents/formatter_agent.md` | Gate matrix extended to 7-row + HIGH-WARN classes | MED — 785 lines; v3.7.3 anchor logic preserved |
| `deep-research/agents/synthesis_agent.md` | New "Claim Intent Manifest Emission" sibling heading | MED — 220 lines; v3.7.3 Three-Layer heading stays |
| `deep-research/agents/report_compiler_agent.md` | Same | MED |
| `academic-paper/agents/draft_writer_agent.md` | Same | MED — 520 lines |
| `shared/contracts/passport/audit_artifact_entry.schema.json` | **NO TOUCH** (D5) | — |
| `shared/contracts/material_passport*` | No root schema exists; aggregate referenced through orchestrator | — |
| `shared/sprint_contract.schema.json` (Schema 13.1) | **NO TOUCH** (D6 zero-touch) | — |
| `scripts/check_audit_artifact_consistency.py` | **NO TOUCH** (D5 — separate lint) | — |
| `README.md` + `README.zh-TW.md` | v3.8 anchor + Zhao 2026 + RubricEM cite | LOW |
| `CHANGELOG.md` | v3.8 entry | LOW |
| `MODE_REGISTRY.md` | New mode flag for opt-in audit | LOW |

Boundary preservation lints (run as part of PR checks):
- `scripts/check_v3_6_7_pattern_protection.py` — verify PATTERN PROTECTION blocks unchanged
- `git diff main..HEAD -- shared/sprint_contract.schema.json` MUST be empty (v3.6.6 zero-touch)
- `git diff main..HEAD -- shared/contracts/passport/audit_artifact_entry.schema.json` MUST be empty (D5)

## 9. Acceptance criteria

Issue body acceptance + decision-doc-derived additions:

- [ ] Agent prompt passes ≥ 5 codex review rounds → 0 P1/P2 (new tool + IO, per harness convergence pattern)
- [ ] Schema + integration passes ≥ 1 gemini cross-model review round (docs-heavy fraction; see Codex 0.130 docs-review broken caveat — verify before invoking)
- [ ] Calibration mode tested with synthetic gold set (≥ 20 tuples) achieving FNR < 0.15 and FPR < 0.10
- [ ] End-to-end test (§7.6 above) passes
- [ ] Zero regression on existing 1107+ unittest + 201 pytest baseline
- [ ] All 13 cross-field invariants (INV-1..INV-13) + 3 manifest invariants (M-INV-1..M-INV-3) + 4 uncited-assertion invariants (U-INV-1..U-INV-4) covered by paired positive/negative fixture
- [ ] Allowed-matrix exhaustive test: every §3.1 table row positive + ≥5 disallowed combinations rejected
- [ ] `claim_intent_manifest` absent → `MANIFEST-MISSING` advisory + fallback flow exercised in test
- [ ] `audit_status=inconclusive` paths emit `defect_stage=not_applicable` (NOT `null`) — INV-4
- [ ] 100% of completed non-SUPPORTED findings emit a `defect_stage` (stage accuracy deferred to #89)
- [ ] Stage 6 reflection report renders per-stage histogram when ≥ 5 completed audit results
- [ ] v3.6.6 Schema 13.1 zero-touch promise verified by git diff lint
- [ ] D5 `audit_artifact_entry.schema.json` zero-touch promise verified by git diff lint
- [ ] Precedence rules (3 rules per issue body) covered by test fixtures
- [ ] Public-repo boundary clean per personal-boundary deny list (run boundary scan before push)

## 10. Risks and open questions

The decision doc closed 8 OQs. Spec-level OQs (resolve during codex rounds, NOT before TDD):

- **S-OQ1** (codex round-1 candidate): cache eviction policy beyond manual rm. Tentative: rely on `judge_model` in cache key — model bumps naturally invalidate; users prune `${ARS_CACHE_DIR}/claim_audit_v1/` as needed.
- **S-OQ2** (codex round-1): retrieval API selection order (Semantic Scholar vs Crossref vs OpenAlex) and fallback ladder. Tentative: SS → Crossref → OpenAlex → manual_pdf, matching v3.6.x convention.
- **S-OQ3** (codex round-2): `claim_id` allocation — sequential per manifest or session-scoped UUID-prefix? Tentative: sequential per manifest (`C-001`, `C-002`...), uniqueness scope = single manifest entry. Cross-manifest collision tolerated (different agent invocations).
- **S-OQ4** (codex round-2): `audit_run_id` collision handling when two audits run within same second. Tentative: 4-hex random suffix (already in schema pattern) gives ~65k uniqueness per second; assume sufficient for ARS scale.
- **S-OQ5** (codex round-2+): manifest emission timing — exact lifecycle hook in `synthesis_agent` and `draft_writer_agent`. Tentative: emit AFTER `literature_corpus[]` consumption, BEFORE first prose block. Confirm during prompt-design rounds.

## 11. Convergence cost projection

Per session handoff harness data:
- doc-only PR = 1 round
- plumbing PR = 3-4 rounds
- new tool + IO PR = **5 rounds**
- scope-frozen follow-up = 3 rounds

#103 is **new tool + IO + new agent + 2 new schemas + new lint + 6 prompt edits**, larger than #105 (which was "new tool + IO migration"). Expected codex rounds: **5-7**.

Strategy: split into two PRs if Round-5 still has open P1/P2:
- PR-A: schemas + lint + agent prompt + tests (no orchestrator/formatter/synthesis_agent touch yet)
- PR-B: orchestrator §3.6 + finalizer 7-row + downstream agent integration

This mirrors #105 → #115 split pattern (production module first, integration follow-up).

## 12. Memory anchors

After ship, update:

- `~/.claude/projects/-Users-imbad/memory/project_ars_106_ai_disclosure_discovery.md` — lesson #22 (8-OQ compressed decision-doc pattern when issue body already has frozen design)
- `~/.claude/projects/-Users-imbad/memory/feedback_codex_round_convergence_by_scope.md` — new memory if not exists, record "new tool + IO + new agent" data point
- Consider new memory `feedback_audit_results_vs_audit_artifact_semantic_split.md` documenting D5 boundary

## 13. Implementation order (TDD-driven)

1. Write schema files (3.1 + 3.2) — these are referenced by all later tests
2. Write `tests/test_claim_audit_schema.py` — failing because schema not yet validated by lint
3. Write `scripts/check_claim_audit_consistency.py` — minimal code to pass schema tests
4. Write `tests/test_claim_audit_pipeline.py` (T-P1..T-P10) — failing, no agent yet
5. Write `claim_ref_alignment_audit_agent.md` Steps 1-6 — minimal text to pass pipeline tests via fixture-driven dispatch
6. Write `tests/test_uncited_assertion.py` + token-rule detector module
7. Write `tests/test_claim_intent_manifest.py` + emission helpers
8. Write `tests/test_claim_audit_finalizer.py` + orchestrator §3.6 + formatter 7-row extension
9. Write `tests/test_e2e_claim_audit.py` + synthetic 5-citation paper fixture
10. Write `tests/test_claim_audit_calibration.py` + calibration protocol doc
11. Regression run on full baseline; zero failures
12. `/simplify` parallel (reuse + quality + efficiency); fix findings
13. `/codex review --base=main`; iterate to 0 P1/P2
14. gemini cross-model round (verify Codex 0.130 docs-heavy caveat first per `feedback_codex_0_130_docs_review_broken.md`)
15. Public-repo boundary scan
16. Squash merge

Steps 4-5 are the highest-risk: agent prompt + pipeline are the load-bearing intersection. Plan for 2-3 codex rounds focused there.
