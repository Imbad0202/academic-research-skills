# Re-Review Mode (Verification Review)

Re-review mode is the dedicated mode for Pipeline Stage 3', designed to **verify whether revisions address the first-round review comments**.

### How It Works

```
Input:
1. Original Revision Roadmap (Stage 3 output)
2. Revised manuscript
3. Response to Reviewers (optional)
4. Editorial Decision Letter (optional, #539 — its Review Panel Provenance block feeds the Judge Record's Round-1 provenance; absent → "unknown (provenance block absent)")

Phase 0: Reads the Revision Roadmap, builds a checklist
Phase 1: EIC checks each item (other reviewers not activated)
Phase 2: Editorial Synthesis -> New Decision
```

### Verification Logic

```
For each item in the Revision Roadmap:

Priority 1 (Required):
  -> Check each item for corresponding changes in the revised manuscript
  -> Assess revision quality (FULLY_ADDRESSED / PARTIALLY_ADDRESSED / NOT_ADDRESSED / MADE_WORSE)
  -> All Priority 1 items must be FULLY_ADDRESSED for Accept

**Traceability Rule**: For each Priority 1 item, the reviewer MUST:
1. Read the author's claim from the Response to Reviewers
2. Navigate to the stated revision location in the manuscript
3. Independently verify the claim matches the actual change
4. If Author's Claim is empty or vague ("addressed as suggested"), mark Verified? as `🔍 Cannot verify` and flag in Quality Assessment

Priority 2 (Suggested):
  -> Check each item
  -> At least 80% should have a response
  -> NOT_ADDRESSED items require author explanation

Priority 3 (Nice to Fix):
  -> Check but does not affect Decision
```

### Judge Independence (#539)

The re-review judges revisions on the same model family that drove them — an analogous correlated-judge configuration to the one Ren et al. (2026, arXiv:2607.13104 §8.1.2) warn about (their warning addresses the identical evaluation operator driving updates AND reporting final results; here the correlation is family-level), with the same failure direction: the revision loop can converge on "what this judge likes" instead of quality.

**When cross-model verification is active** (configured + consented, same boundary as every cross-model feature): after the re-review's Priority 1 assessments are committed, the dispatching layer (the main session / orchestrator running the mode — per #523 it, not a fenced agent, executes API calls) runs an independent per-item pass using the provider TRANSPORT from § API Call Patterns (endpoint + auth) with a JUDGMENT-specific request — NOT the citation-verification handlers (those hard-code citation prompts, require web grounding, and normalize a different verdict set): no web-search requirement (revision-addressedness is persona judgment, the DA-critique class — compatible providers first-class), a prompt asking only for one verdict from the closed set, and the response parsed against exactly {FULLY_ADDRESSED, PARTIALLY_ADDRESSED, NOT_ADDRESSED, MADE_WORSE} — any non-conforming response maps to `unavailable`, never coerced. No #527 envelope (that grammar is for fenced-owner handoffs; none occurs here). Inputs per item: the roadmap item + the author's claim + the revised passage, personal names/affiliations stripped (the § data-minimization rule), delimited as data, not instructions. The dispatching layer compares mechanically and writes the result into the R&R Traceability Matrix's `Cross-model` column: `agree`, `diverges: <verdict>`, or `unavailable`. A `diverges` cell is a review trigger for the decision-maker's Phase 2 synthesis — never a vote; the primary verdict is never overwritten. `unavailable` (API failure) is a ROW-level status: that row carries the single-family caveat; the run-level disclosure below applies only when the pass was not configured or EVERY item came back unavailable. A mixed run records `partial — N/M items judged` in the Judge Record.

**When not active** (or the pass came back `unavailable`): the re-review proceeds single-family and the Re-Review Output carries the disclosure line verbatim (it is part of the output template below): "This verification round ran on the same model family that drove the revisions; over-optimization to this judge's latent biases is possible (Ren et al. 2026, arXiv:2607.13104 §8.1.2)." Never omit it in single-family runs.

**Judge identity recording (both cases):** the Re-Review Output's Judge Record block (below) records the judge configuration — the verification judge's family/id (the running session knows its own), the Round-1 panel provenance copied seat-level from the Editorial Decision Letter's Review Panel Provenance block (#540; carried into Stage 3' with the letter — no per-seat model id is invented), the prompt/rubric surfaces used, the evidence the judge saw, and the judging budget noted separately from generation. Schema 6 carries these as the optional `judge_record` field.

### Commitment Ledger Verification (Kong A1 / v3.11)

This step runs **for every Schema 11 row** (any priority) that carries a non-empty `commitment_extracted` list from `revision_coach_agent` Step 3.5. It is independent of the Priority 1/2/3 Traceability Rule above — every parsed reviewer comment may produce commitments, and every commitment must be verified, regardless of the parent concern's priority.

For each commitment, verify per-commitment `fulfillment_status`:

- `fulfilled` — the `required_evidence_type` is present and substantively addresses the `commitment_text`. Verification site depends on `required_evidence_type`:
  - For `new_section` / `new_figure` / `new_table` / `new_citation` / `methods_paragraph` / `discussion_paragraph` / `prose_edit` — verify against the **revised manuscript** at `revision_location`. `prose_edit` items (typo fixes, terminology clarifications, equation formatting, citation-style corrections) are sentence- or paragraph-level changes; verify the specific text at `revision_location` rather than expecting a new structural block.
  - For `acknowledgment_only` — verify against the **Response to Reviewers (Schema 8)** instead of the manuscript diff. `acknowledgment_only` items by definition do not require manuscript changes; expecting a manuscript diff would produce false `not-fulfilled` classifications. The response letter must explicitly acknowledge or address the commitment in writing.
  - For `other` — the evidence type is intentionally underspecified (escape hatch for genuinely uncategorizable commitments). Surface a soft **`EVIDENCE_TYPE_UNSPECIFIED`** advisory (advisory only, **not** a hard block): if `revision_location` is empty, prompt the author to specify it so the re-reviewer can verify; if `revision_location` is already populated, the advisory simply flags that the evidence type was left uncategorized — verify at the stated location. This is distinct from `COMMITMENT_GAP` (which fires on missing rationale for a non-`fulfilled` status); `EVIDENCE_TYPE_UNSPECIFIED` fires whenever `required_evidence_type == other`, regardless of `fulfillment_status`.
- `partial` — required evidence exists but does not fully address the commitment (e.g., experiment run on dataset Y when reviewer asked for dataset X; 3-seed std error when 5-seed was requested with rationale provided).
- `not-fulfilled` — required evidence is absent (rationale presence is a separate axis — see `COMMITMENT_GAP` rule below).
- `explicitly-rejected-with-rationale` — author has explicitly declined to address the commitment; status name implies rationale, but `unfulfilled_rationale` is still the field that carries the actual rationale text (per Schema 11 Validation rule).

For any commitment object with `fulfillment_status` ∈ `{partial, not-fulfilled, explicitly-rejected-with-rationale}` where the object's `unfulfilled_rationale` is empty or missing, surface a **`COMMITMENT_GAP`** entry in re-review output (advisory only, **not** a hard block — author retains final responsibility per `POSITIONING.md`). This mirrors the Schema 11 Validation rule: any non-`fulfilled` status requires a rationale on the same commitment object. Because `fulfillment_status` and `unfulfilled_rationale` are nested fields of the commitment object (not separate parallel lists), there is no index-walking step and no way to pair a status with the wrong commitment — the #268 desync failure mode is structurally absent.

**A populated `residual_action` alongside one or more commitment objects with `fulfillment_status: fulfilled` is not a contradiction.** `residual_action` operates at the concern level (forward-looking: what still remains for the whole concern), while `fulfillment_status` is per-commitment (carried on each commitment object). A concern can have some commitments fully fulfilled and still carry a concern-level residual action (e.g., the core ablation was added but the concern's broader generalization claim still needs a follow-up experiment flagged in `residual_action`). Do **not** raise a gap or inconsistency flag merely because `residual_action` is non-empty while one or more commitments are `fulfilled` — see `shared/handoff_schemas.md` Schema 11 `residual_action` convention (a).

This section is the verification analog of `revision_coach_agent` Step 3.5 (Kong A1). Per-commitment lifecycle gating is what closes the Kong §7.4.3 commitment-fulfillment gap.

### New Issue Detection

```
In addition to checking old items, EIC also scans for:
- Whether content added during revision introduces new problems
- Whether newly added references are correct (but deep verification is left to Stage 4.5 integrity check)
- Whether revisions cause inconsistencies
```

### Socratic Guidance After Re-Review

```
If Re-Review Decision = Major Revision:
  -> Activate Residual Coaching (residual issue guidance)
  -> EIC guides user through Socratic dialogue:
    1. Gap analysis — "How many issues did the first round of revisions resolve? Why are the remaining ones hard to address?"
    2. Root cause diagnosis — "Is it insufficient evidence, unclear argumentation, or a structural problem?"
    3. Trade-off decisions — "Which ones can be marked as research limitations?"
    4. Action plan — Plan revision approach for each residual issue
  -> Maximum 5 rounds of dialogue
  -> User can say "just fix it" to skip guidance
```

### Re-Review Output Format

```markdown
# Verification Review Report

## Judge Record (#539)

- **Verification judge**: [model family/id running this re-review — the session's own]
- **Round-1 panel provenance**: [copied seat-level from the Editorial Decision Letter's Review Panel Provenance block (#540); "unknown (provenance block absent)" when absent — record the reason when known, e.g. "guided-mode Round 1 (no letter emitted)" or "pre-#540 letter"]
- **Independent cross-model pass**: [ran — [family/id], see the Cross-model matrix column / partial — N/M items judged, [family/id] / not_configured / failed — [reason]; not_configured and failed apply the run-level single-family disclosure, partial applies it per unavailable row]
- **Prompt/rubric surfaces**: [the re-review protocol + verification-logic sections used, by file reference; rubric/contract version]
- **Evidence seen by the judge**: [revised manuscript + Response to Reviewers + Revision Roadmap / list deviations]
- **Judging budget**: [approx. calls/tokens spent on verification, separate from generation]

[Single-family runs: include the disclosure line verbatim here — "This verification round ran on the same model family that drove the revisions; over-optimization to this judge's latent biases is possible (Ren et al. 2026, arXiv:2607.13104 §8.1.2)."]

## Decision
[Accept / Minor Revision / Major Revision]

## Revision Response Checklist

### Priority 1 — Required Revisions

| # | Original Review Comment | Author's Claim | Response Status | Revision Location | Verified? | Cross-model (#539) | Quality Assessment |
|---|------------------------|---------------|-----------------|-------------------|-----------|--------------------|--------------------|
| R1 | [Original text] | [What the author claims to have done in Response to Reviewers] | FULLY_ADDRESSED | Section X.X | ✅ Yes | agree | Adequately addressed; newly added content effectively resolves the issue |
| R2 | [Original text] | [Author's stated change] | PARTIALLY_ADDRESSED | Section Y.Y | ⚠️ Partial | diverges: NOT_ADDRESSED | Partially addressed, but still missing [specific gap] |

Cross-model cell vocabulary (Priority 1 rows only — the pass does not evaluate Priority 2/3, whose tables omit the column): `agree` / `diverges: <verdict>` / `unavailable` (dispatch failed — single-family disclosure applies) / `not_configured` (cross-model not active — every Priority 1 row carries it, single-family disclosure applies).

### Priority 2 — Suggested Revisions

| # | Original Review Comment | Response Status | Notes |
|---|------------------------|-----------------|-------|
| S1 | [Original text] | FULLY_ADDRESSED | -- |
| S2 | [Original text] | NOT_ADDRESSED | Author explanation: [reason] |

### Priority 3 — Nice to Fix

| # | Original Review Comment | Response Status |
|---|------------------------|-----------------|
| N1 | [Original text] | FULLY_ADDRESSED |

## New Issues (Discovered During Revision)

| # | Type | Location | Description |
|---|------|----------|-------------|
| NEW-1 | [Type] | Section X.X | [Description] |

## Decision Rationale
[Rationale based on the checklist]

## Residual Issues (If Any)
[List unresolved items, suggest marking as Acknowledged Limitations]
```

## v3.6.2 sprint contract status

v3.6.2 introduces sprint contracts for `reviewer_full` and `reviewer_methodology_focus` only. A template for this mode will follow in a subsequent patch release. Until then, this mode runs without contract enforcement and retains its pre-v3.6.2 behaviour.
