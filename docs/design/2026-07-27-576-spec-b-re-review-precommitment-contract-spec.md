# #576 Spec B — Re-review pre-commitment contract: three-gate evidence-before-persuasion verification (design)

- **Status**: design (pre-implementation)
- **Issue**: #576 (tracks #574 items E1 + the goalpost half of E2; #574 is the umbrella)
- **Governing inputs**: the #576 issue body (2026-07-23), the repository-wide acceptance review (issue comment, 2026-07-24), and the rescope decision (issue comment, 2026-07-24). Where they conflict, the rescope decision governs.
- **Prior art**: Spec A (`2026-07-25-574-spec-a-role-scoped-scoring-decision-contract-spec.md`) for the executable-conformance and witness-test conventions this spec mirrors.
- **Target**: next minor suite release. Additive; default behavior changes ONLY at Stage 3' re-review dispatch (see §12 legacy boundary).

---

## 1. Problem

Re-review is Pipeline Stage 3' — the gate that decides whether revisions pass, the single decision the revision loop converges on — and it is the only reviewing mode with no pre-commitment protection (`references/sprint_contract_protocol.md` §7 marks `reviewer_re_review` "not shipped in v3.6.2; continues pre-v3.6.2 behaviour"; `academic-paper-reviewer/SKILL.md` carries the same reserved-modes note).

Three properties make this the worst place to lack pre-commitment:

1. **It is the accept gate.** Anti-pattern #4 ("rubber-stamp re-review") is documented in SKILL.md, but the structural defense that exists for first-round scoring — commit the yardstick before seeing the object — is absent exactly where rubber-stamping pays off most.
2. **The read-then-rationalize channel is stronger here, and adversarial.** The current Traceability Rule (`re_review_mode_protocol.md` § Verification Logic) *instructs* the verifier to read the author's claim FIRST ("1. Read the author's claim from the Response to Reviewers → 2. Navigate to the stated revision location → 3. Independently verify"). The Response to Reviewers is a document written to persuade the verifier. Reading it before fixing what would count as addressed invites claim-anchored verification: checking whether the author's story is coherent instead of whether the manuscript change satisfies the original concern.
3. **Downstream machinery assumes committed verdicts.** The #539 cross-model judge pass runs after Priority 1 assessments are committed, but nothing pins what those assessments were committed *against*. A pre-committed per-item criteria set gives the independent judge a fixed reference instead of a moving one.

The 2026-07-24 acceptance review rejected the original two-phase sketch on three grounds, all adopted here: (a) revealing the revised manuscript and the Response Letter together still lets the author narrative anchor evidence perception — the gates must separate evidence from persuasion, not just criteria from paper; (b) Phase 1 must inherit the author-visible yardstick (Schema 7 `verification_criteria`, `handoff_schemas.md:443`; decision-letter Acceptance criteria, `templates/editorial_decision_template.md:118`), never invent a hidden one after the author has revised; (c) dynamic per-roadmap-item verification is structurally incompatible with the Schema 13 machinery and needs dedicated artifacts, not an enum branch.

### 1.1 What already shipped (PR 0, with #574)

The plumbing the rescope decision ordered ahead of this spec is in place and is a dependency, not a deliverable, here:

- Stage 4→3' handoff transfers the Revised Draft, Response to Reviewers, Editorial Decision Letter, Round-1 Revision Roadmap, apply report(s), and Round-1 Reviewer Configuration Cards (`pipeline_orchestrator_agent.md` § Handoff material transfer rules, Stage 4 -> 3' row).
- `ars_apply_revision_patch.py` emits `output_draft_hash` (12-hex) in the apply report; the handoff row instructs verifying it against the Revised Draft.
- Yardstick Continuity: `field_analyst` is NOT re-run at Stage 3'; the Round-1 cards are reused, with the `[YARDSTICK-REGENERATED: …]` marked fallback (`re_review_mode_protocol.md` § Yardstick Continuity).
- Author-authored inputs are already declared UNTRUSTED data (#574 A6) in the protocol's input list.

The **consumer-side runtime witness** for `output_draft_hash` (owner note in the rescope decision) lands HERE, in `check_re_review_synthesis.py` (§13), so emit-now/verify-later does not rot.

---

## 2. Settled decisions

| ID | Decision | Source |
|----|----------|--------|
| SD-1 | Three gates, not two: Phase 1 criteria commitment → Phase 2A evidence verdict (before the Response Letter is revealed) → Phase 2B claim matching (letter revealed; may add context, never silently relax) | rescope §"Three gates" |
| SD-2 | Criterion inheritance, not invention: Phase 1 operationalizes the author-visible Schema 7 `verification_criteria` + Round-1 severity/evidence anchors + the Round-1 criteria snapshot (config cards). Post-revision new standards are `new_standard`, advisory by default, with a restricted escalation exception + human checkpoint | rescope §"Criterion inheritance" |
| SD-3 | Dedicated machine-readable artifacts + a dedicated checker — NOT a Schema 13 enum branch. Four structural incompatibilities: paper-blind premise meaningless for re-review; `panel_size=1` collapses the cross-reviewer quantifier grammar and trips SC-11 noise; FULLY/PARTIALLY/NOT_ADDRESSED/MADE_WORSE vs `block\|warn\|pass` vocabulary mismatch; frozen-contract vs per-round `field_analyst` regeneration | rescope §"Dedicated artifacts" |
| SD-4 | Complete verdict→decision truth table including `CANNOT_VERIFY` / `INDETERMINATE`, valid-rebuttal / equivalent-fix acceptance, regression vs previously-missed vs indeterminate attribution, fail-closed on missing provenance | rescope §"Complete verdict→decision truth table" |
| SD-5 | Structured dissent records with proportion bounds; independent adjudication for P1 or excessive dissent | acceptance review #7 |
| SD-6 | Cross-model divergence gains a `primary_upheld \| primary_revised \| user_review_required` resolution gate before Accept | acceptance review #8 |
| SD-7 | Item-centric competence routing; EIC integrates, does not personally validate every methods/domain correction | acceptance review #9 |
| SD-8 | `[LEGACY-NO-CONTRACT]` explicit fallback replaces silent byte-equivalence claims | acceptance review #10 |
| SD-9 | All required inputs hash-bound and freshness-checked; missing/non-comparable provenance yields `indeterminate` / fail-closed, never pretended causal attribution | acceptance review #4 |
| SD-10 | `expected_change_surface` is a navigation hypothesis, not a mandatory location: equivalent fixes and evidence-backed disagreement can count as fully addressed | acceptance review #2 |
| SD-11 | The persuasion-invariance behavioral eval joins the #574 E4 harness as paired controls, not a separate suite | rescope, final paragraph |
| SD-12 | E2 score trajectory is repair-and-wire, tracked under #574's backlog — OUT of this spec | rescope §"Also accepted" |

---

## 3. Three-gate orchestration

Three sequential fenced calls, dispatched by the orchestrating layer (main session / pipeline orchestrator — per #523 the dispatching layer, not a fenced agent, executes any API calls). Each gate's output is validated (schema + lint) before the next gate is dispatched. Phase-numbered data delimiters mirror the v3.6.2 `<phase1_output>` pattern.

### 3.1 Gate inputs and withholding matrix

| Input | Phase 1 | Phase 2A | Phase 2B |
|-------|---------|----------|----------|
| Round-1 Revision Roadmap (Schema 7) | ✅ | ✅ | ✅ |
| Round-1 Editorial Decision Letter (incl. per-item Acceptance criteria) | ✅ | ✅ | ✅ |
| Round-1 review findings (Schema 6 reports / findings referenced by roadmap items) | ✅ | ✅ | ✅ |
| Round-1 Reviewer Configuration Cards (frozen criteria snapshot) | ✅ | ✅ | ✅ |
| Revised-manuscript METADATA only (title, length, section list — no body) | ✅ | — | — |
| Original (pre-revision) manuscript | ❌ | ✅ | ✅ |
| Revised manuscript (full body) | ❌ | ✅ | ✅ |
| Revision patch / diff + apply report(s) | ❌ | ✅ | ✅ |
| Response to Reviewers | ❌ | ❌ | ✅ |
| Input manifest (§11) verification result | ✅ | ✅ | ✅ |

Rationale for the row that moved since the issue sketch: the original manuscript joins Phase 2A because `regression | previously_missed` attribution (§8) requires comparing against the pre-revision text, and because "what changed" must be established from the diff/apply report, not from the author's narrative.

### 3.2 Phase 1 — criteria commitment (revision-blind)

For each Priority 1 (`must_fix`) roadmap item — and each Priority 2 (`should_fix`) item in lighter form — the verifier emits a pre-commitment record (schema, §5.1) that OPERATIONALIZES the inherited criterion:

- `inherited_criterion` — the Schema 7 `verification_criteria` text (verbatim) + the decision letter's Acceptance-criteria text when present. This is the author-visible yardstick; the record binds to it by item id.
- `operationalization.fully_addressed` — the concrete manuscript evidence pattern that satisfies the inherited criterion (not "the author says so").
- `operationalization.partially_addressed` — what a genuine-but-incomplete fix looks like.
- `operationalization.made_worse_discriminator` — what distinguishes a regression on this item.
- `expected_change_surface` — where the fix is EXPECTED to manifest (section/analysis/table). Navigation hypothesis only (SD-10): a fix elsewhere that satisfies `operationalization.fully_addressed` counts; the surface exists so a cosmetic edit at the expected location cannot satisfy the item by position alone.
- `equivalence_policy: allowed` — constant in v1; records that equivalent fixes and evidence-backed disagreement are admissible (SD-10).

**Prohibitions (mirror v3.6.2 Phase 1):** no speculation about what the revision did, no verdicts, no reading of any withheld input. The operationalization must be derivable from Round-1 artifacts alone; a record whose operationalization references revision content fails lint. Ends with `[CONTRACT-ACKNOWLEDGED]`.

**`new_standard` boundary (SD-2):** Phase 1 may NOT add acceptance requirements beyond the inherited criterion. If operationalizing reveals that the Round-1 criterion is materially incomplete (e.g., it never named a check the concern obviously requires), the verifier records a `new_standard` entry: `{item_id, standard_text, why_not_in_round1, classification: advisory}`. Advisory by default — it cannot change the item verdict or the decision. The sole escalation path is §6.4 (integrity/ethics/safety/legal-compliance/fatal-validity, human checkpoint mandatory).

**Retry:** one Phase 1 retry on lint failure (fresh call, no failure details beyond the lint tag — same discipline as v3.6.2). Second failure → `[RE-REVIEW-ABORT: phase1_lint_failed]`, fail closed.

### 3.3 Phase 2A — evidence verdict (persuasion-blind)

Inputs add the original manuscript, the revised manuscript, and the patch/apply report(s); the Phase 1 output rides fenced as `<phase1_output>` (data, not instructions). The Response Letter is still withheld.

Per item, the verifier commits a verdict record (schema, §5.2):

- `verdict` ∈ `{FULLY_ADDRESSED, PARTIALLY_ADDRESSED, NOT_ADDRESSED, MADE_WORSE, CANNOT_VERIFY}` — assigned strictly against the Phase-1 operationalization, or through an explicit dissent record (§7), never silently off-criterion.
- `evidence_anchor` — typed anchor(s) into the REVISED manuscript (Schema 6 anchor grammar) for every verdict except `CANNOT_VERIFY`; `CANNOT_VERIFY` instead carries `cannot_verify_reason` (e.g., evidence surface inaccessible, criterion requires an artifact not in the input set).
- `change_summary` — what actually changed relative to the original manuscript (from diff/apply report + comparison), one sentence.
- `residual_gap` — REQUIRED for `PARTIALLY_ADDRESSED`: the concrete missing part, with a `residual_magnitude` ∈ `{must_fix, should_fix, consider}` re-grading of what remains (feeds the §6 decision derivation).

New issues discovered while reading the revised manuscript are recorded as new-issue records with attribution (§8) — also before the letter is read, because attribution must not be colored by the author's framing of what they changed.

**Prohibitions:** no reference to the Response Letter (it is absent); no verdict revision after emission (2A output is committed — the orchestrator persists it before dispatching 2B). Ends with `[EVIDENCE-COMMITTED]`.

**No retry** once the revised manuscript has been seen (same taint logic as the v3.6.2 no-Phase-2-retry rule); a 2A lint failure → single fresh-call retry from Phase 2A with the SAME `<phase1_output>` (the criteria are already committed and clean); second failure → `[RE-REVIEW-ABORT: phase2a_lint_failed]`.

### 3.4 Phase 2B — claim matching (letter revealed)

Inputs add the Response to Reviewers, fenced as UNTRUSTED author-authored persuasion (#574 A6 class). The committed 2A verdicts ride as `<phase2a_output>`.

Phase 2B produces the final traceability matrix (Schema 11 + machine-readable sidecar, §5.3). It may:

- fill `authors_claim` per item and check claim-vs-manuscript consistency;
- run the Commitment Ledger Verification pass (Kong A1 / v3.11 — unchanged, `re_review_mode_protocol.md` § Commitment Ledger Verification), including the `acknowledgment_only` evidence class whose evidence IS the letter;
- record valid-rebuttal claims: an evidence-backed author disagreement (REVIEWER_DISAGREE) is admissible and can raise an item to `FULLY_ADDRESSED` **via an adjustment record**, never silently;
- locate evidence 2A missed when the author's pointer leads to a REAL manuscript change satisfying the Phase-1 operationalization — again only via an adjustment record whose `evidence_anchor` is manuscript-side.

**The relaxation boundary (SD-1):** every difference between a 2A committed verdict and the final matrix verdict MUST be carried by a typed adjustment record (§5.3). Admissible bases (closed set):

| `basis` | Direction | Evidence requirement |
|---------|-----------|----------------------|
| `author_pointer_located_evidence` | upgrade | Manuscript-side typed anchor satisfying the Phase-1 operationalization; the letter told the verifier WHERE to look, the manuscript is what satisfies |
| `valid_rebuttal` | upgrade to `FULLY_ADDRESSED` (marker `addressed_by_rebuttal: true`) | The rebuttal's evidence (citations, derivations, data in the manuscript or letter) rebuts the original finding on the merits; record the counter-evidence anchor |
| `acknowledgment_only_commitment` | resolves the commitment axis only (Kong A1) | Letter-side, per the existing narrow exception |
| `scope_correction` | either direction | The letter reveals the 2A reading misidentified the item's target (wrong section/claim); re-verification against the correct target, manuscript-side anchor |

A `to_verdict` upgrade with basis `valid_rebuttal` on an item whose Round-1 severity is `critical` additionally requires the §9 cross-model adjudication when active, else a decision-letter disclosure line. An assertion in the letter with no locatable manuscript evidence changes nothing. Ends with `[MATRIX-COMMITTED]`.

### 3.5 Abort taxonomy

`[RE-REVIEW-ABORT: <reason>]` with closed reasons: `phase1_lint_failed`, `phase2a_lint_failed`, `phase2b_lint_failed`, `manifest_incomplete`, `manifest_hash_mismatch`, `criteria_drift` (§7), `synthesis_mismatch` (§13). Every abort is fail-closed: no decision is emitted, the pipeline surfaces the abort to the user at the Stage 3' checkpoint.

---

## 4. Criterion inheritance chain

The yardstick, in precedence order — each level only OPERATIONALIZES the level above, never extends it:

1. Schema 7 RoadmapItem `verification_criteria` (`handoff_schemas.md:443`) — author-visible since Round 1.
2. The Editorial Decision Letter's per-item **Acceptance criteria** field (`templates/editorial_decision_template.md:118`) — author-visible.
3. The driving finding's severity + typed `evidence_anchor` + originating dimension (Schema 7 transported fields, #574 A2/A3) — fixes WHAT the concern was about.
4. The Round-1 Reviewer Configuration Cards + target venue (frozen; § Yardstick Continuity) — fixes the field/venue standard the criteria were written under.

A Phase-1 operationalization that cannot be traced to levels 1-4 for its item is a `new_standard` (§3.2), advisory. The checker (§13) verifies binding: every pre-commitment record quotes its level-1 criterion verbatim and the quote must match the roadmap (hash-bound via the §11 manifest).

---

## 5. Artifacts

All new artifacts live under `shared/contracts/re_review/` (schemas) and are runtime-emitted per re-review round (instances travel in the Material Passport like other Schema 9 cargo). NOT part of `sprint_contract.schema.json` — see §5.4.

### 5.1 `precommitment.schema.json`

Top-level: `{contract_version, round_id, input_manifest_hash, items: [PrecommitmentRecord], new_standards: [NewStandardRecord]}`.

`PrecommitmentRecord`: `{item_id (Schema 7 id, e.g. REV-001), priority, inherited_criterion {roadmap_text, letter_text?}, operationalization {fully_addressed, partially_addressed, made_worse_discriminator}, expected_change_surface, equivalence_policy: "allowed", source_dimension?, source_reviewer?}`. Priority 2 lighter form: `operationalization.fully_addressed` only.

`NewStandardRecord`: `{item_id | "global", standard_text, why_not_in_round1, classification: "advisory" | "escalation_requested"}` — `escalation_requested` valid only with an `escalation_class` from the §6.4 closed set.

### 5.2 `verdict_record.schema.json` (Phase 2A)

Top-level: `{round_id, precommitment_hash, items: [VerdictRecord], new_issues: [NewIssueRecord], dissents: [DissentRecord]}`.

`VerdictRecord`: `{item_id, verdict, evidence_anchor[] | cannot_verify_reason, change_summary, residual_gap? {text, residual_magnitude}, verified_by (§10), applied_criterion: "precommitted" | "dissented:<dissent_id>"}`.

`NewIssueRecord` and `DissentRecord`: §8 / §7.

### 5.3 `traceability.schema.json` (Phase 2B — machine-readable Schema 11 sidecar)

Top-level: `{round_id, verdict_record_hash, rows: [MatrixRow], adjustments: [AdjustmentRecord], decision_inputs: DecisionInputs}`.

`MatrixRow`: the Schema 11 required fields (`concern_id`, `priority`, `original_comment`, `authors_claim`, `revision_location`, `verified`, `status`, `quality_assessment`) plus `final_verdict`, `phase2a_verdict`, `adjustment_id?`, `addressed_by_rebuttal?`, `cross_model_status?` / `cross_model_verdict?` (#539 fields, unchanged semantics). Invariant: `final_verdict != phase2a_verdict ⟺ adjustment_id` present. Schema 11 prose (`handoff_schemas.md` § Schema 11) remains the human surface; the sidecar is what the checker recomputes from — no index-walking (rows carry ids, mirroring the #268-desync-free convention).

`AdjustmentRecord`: `{adjustment_id, item_id, from_verdict, to_verdict, basis (closed set §3.4), evidence_anchor, rationale}`.

`DecisionInputs`: the mechanically-derived aggregates the §6 table consumes (counts per verdict class per priority, regression list with severities, dissent proportions, cross-model resolution states) — emitted so the checker recomputes the decision from the same numbers the synthesizer used.

### 5.4 Schema 13 disposition

`reviewer_re_review` is REMOVED from the `sprint_contract.schema.json` `mode` enum (present today at `shared/sprint_contract.schema.json:25`, never had a template — the acceptance review's point that "schema accepts mode" is vacuously satisfiable). The §7 panel-mapping table in `sprint_contract_protocol.md` changes the `reviewer_re_review` row to point at THIS contract family; `check_sprint_contract.py` needs no new gating (the mode value no longer validates), and one regression test pins that a Schema 13 contract claiming `mode: reviewer_re_review` now FAILS validation with a pointer to `shared/contracts/re_review/`. `reviewer_calibration` / `reviewer_guided` stay reserved in the enum (still planned as Schema 13-shaped).

---

## 6. Verdict → decision truth table

Inputs: per-item final verdicts (P1 = `must_fix`, P2 = `should_fix`, P3 = `consider`), `residual_magnitude` re-grades, new-issue records with attribution + severity, dissent aggregates, cross-model resolution states, manifest status. Output: exactly one of `Accept | Minor Revision | Major Revision | Reject`, or a fail-closed abort. Evaluate rules in order; FIRST match wins.

| # | Condition | Outcome |
|---|-----------|---------|
| T0 | Input manifest incomplete or hash-mismatched (§11) | `[RE-REVIEW-ABORT: manifest_incomplete \| manifest_hash_mismatch]` — no decision |
| T1 | Any P1 row where `final_verdict != phase2a_verdict` without an `adjustment_id`, or any dissent bound tripped (§7) | `[RE-REVIEW-ABORT: criteria_drift]` |
| T2 | Unresolved §9 cross-model gate on any P1 item (state not in `{primary_upheld, primary_revised}`) | `user_review_required` — decision deferred to the user checkpoint; the matrix is delivered without a decision line |
| T3 | Approved §6.4 escalation exception active | The exception record's `mechanical_decision_impact` applies as a FLOOR over T4-T9's result (never below it), then continue |
| T4 | Any P1 `MADE_WORSE` with driving-finding severity `critical`, OR any `regression`-attributed new issue with severity `critical` (fatal-validity class) | **Reject** (Stage 3' Reject → the existing user restructure/abandon checkpoint) |
| T5 | ≥ 50% of P1 items in `{NOT_ADDRESSED, MADE_WORSE}` | **Reject** |
| T6 | Any P1 in `{NOT_ADDRESSED, MADE_WORSE}`, OR any P1 `CANNOT_VERIFY`, OR any `regression`-attributed new issue with severity `major` | **Major Revision** |
| T7 | Any P1 `PARTIALLY_ADDRESSED` with `residual_magnitude: must_fix` | **Major Revision** |
| T8 | Any P1 `PARTIALLY_ADDRESSED` with `residual_magnitude: should_fix \| consider`, OR P2 response rate < 80% (existing threshold, unchanged), OR any `regression`-attributed new issue with severity `minor` | **Minor Revision** |
| T9 | All P1 `FULLY_ADDRESSED` (including `addressed_by_rebuttal`), P2 response rate ≥ 80%, no decision-affecting regressions | **Accept** |

Notes:

- `CANNOT_VERIFY` on a P1 caps the decision at Major (T6): acceptance requires positive verification, and fail-closed beats benefit-of-the-doubt. On P2/P3 it is recorded, not decision-driving.
- `previously_missed` and `indeterminate` new issues NEVER appear in T4-T8 (goalpost guard, §8) — they are reported and routed, but only `regression` attribution can move the decision.
- The existing P2 80% / P3 no-effect semantics are preserved (this spec makes them mechanical, it does not change the thresholds — the "thresholds unchanged" non-goal survives in this narrowed form; the acceptance review's objection was to leaving the table incomplete, which T0-T9 closes).
- Every valid input state maps to exactly one row: T9 is the residual (checker-enforced totality, §13).

### 6.4 Escalation exception (the ONLY path around the goalpost guard and `new_standard` advisory default)

Closed class set: `{research_integrity, ethics, safety, legal_compliance, fatal_validity}`. An exception record requires ALL of: `escalation_class`, `reason_code`, original-text evidence anchor (into the ORIGINAL manuscript — proving it existed in Round 1 — or into revision-introduced content, which makes it a `regression` instead and T4-T6 already handle it), `why_round1_missed_it`, `mechanical_decision_impact` (one of the four decisions, as a floor), and a **mandatory human checkpoint**: the user must explicitly approve the exception at the Stage 3' checkpoint before it takes effect; unapproved exceptions revert to advisory. Stage 4.5's integrity gate independently sees the exception record (it travels in the passport).

---

## 7. Dissent records and bounds

A dissent is the Phase 2A discovery that a pre-committed operationalization cannot be applied as written. It is NOT a verdict-relaxation channel — it swaps the criterion, visibly, before the verdict.

`DissentRecord`: `{dissent_id, item_id, criterion_hash (of the Phase-1 record), reason_code ∈ {criterion_ambiguous, criterion_infeasible_as_written, evidence_surface_moved, criterion_error}, original_operationalization, replacement_operationalization, evidence, decision_impact_note}`. The item's verdict record then carries `applied_criterion: "dissented:<dissent_id>"`.

**Bounds (SD-5):** dissent on a P1 item, or dissents on > ⌈N/3⌉ of all items (N = total roadmap items), triggers independent adjudication BEFORE the verdicts stand: when cross-model is active, the §9 judge blind-applies the ORIGINAL Phase-1 criterion first, then separately adjudicates the replacement; when not active, `[RE-REVIEW-ABORT: criteria_drift]` is avoided only by surfacing the dissent(s) at a user checkpoint (the user approves or rejects the replacement). Exceeding the bound without adjudication = T1 abort. This keeps dissent from becoming a quiet goalpost-reset channel while leaving a legitimate path for genuinely broken criteria.

Unlike the v3.6.2 one-dimension-per-reviewer cap (built for 5-7 fixed dimensions), the bound is proportional because roadmap item counts vary widely.

---

## 8. New-issue attribution and the goalpost guard

Every issue found during Phase 2A that is not traceable to a roadmap item gets a `NewIssueRecord`: `{new_issue_id, description, location_anchor, severity (Schema 6 vocabulary), attribution, attribution_evidence}`.

`attribution` (closed):

- `regression` — introduced by the revision. Evidence: the anchored content is in the revised manuscript but not the original (diff/apply-report-supported). MAY affect the decision (T4/T6/T8).
- `previously_missed` — present in the original manuscript; Round 1 missed it. Evidence: anchored in BOTH versions. Reported, CANNOT escalate the decision (only §6.4 overrides). Routed forward: if the round's decision is Major Revision, it enters the new Stage 3' → 4' Roadmap as an `advisory`-priority item; otherwise it enters the Stage 4.5 handoff as an exception-log entry for the final integrity check. Both destinations exist in the current state machine — no new transition is created (the `Stage 4' → 3'` prohibition, `pipeline_state_machine.md` § Prohibited Transitions, is untouched).
- `indeterminate` — provenance cannot be established (original manuscript unavailable, non-comparable formats, manifest gaps). Treated as `previously_missed` for decision purposes (cannot escalate) and flagged `[ATTRIBUTION-INDETERMINATE]` in the report — never silently promoted to `regression` (SD-9).

The guard is enforceable exactly because Phase 1 fixed the item baseline: "not traceable to a pre-committed item" is now a mechanical check (no matching `item_id`), not a judgment call.

---

## 9. Cross-model resolution gate (#539 upgrade)

The existing #539 per-item pass (transport, verdict set, data-fencing, name-stripping — `re_review_mode_protocol.md` § Judge Independence) is reused with three changes:

1. **Input**: the judge receives the Phase-1 pre-committed criterion for the item (data-fenced) and judges "does the revision meet the committed criterion" — not "is the primary's verdict agreeable". The Judge Record gains a `precommitment_hash` line.
2. **Resolution gate (SD-6):** a `diverges` cell on a P1 item must resolve to `primary_upheld` (primary re-examined, verdict stands, one-line rationale) or `primary_revised` (verdict changes via an adjustment record with basis `scope_correction` or a §7 adjudication) before the decision derivation runs; anything unresolved → T2 `user_review_required`. `agree` / `unavailable` / `not_configured` resolve implicitly (unavailable/not_configured keep the existing single-family disclosure).
3. **Dissent adjudication order:** when the primary dissented from a criterion (§7), the judge FIRST blind-applies the original criterion (without seeing the dissent), THEN separately adjudicates the replacement — two calls, so the replacement cannot anchor the original's application.

Consent boundary unchanged: cross-model runs only when configured + consented; nothing here makes it default-on. Single-family runs satisfy the gate trivially (every state is `not_configured`) but carry the disclosure — the gate adds protection when the machinery exists, it does not manufacture a dependency.

---

## 10. Verifier routing (SD-7)

Items are verified by competence, not by a single EIC persona (`eic_agent.md` scopes EIC as bird's-eye editorial, not deep methods verification):

- Each pre-commitment record carries `source_dimension` / `source_reviewer` (transported from Schema 7 — present since #574 A3; absent on legacy roadmaps).
- Phase 2A dispatch: items whose `source_dimension` maps to a Round-1 specialist seat (methodology, domain, perspective — from the frozen cards) are verified under that seat's persona; the `verified_by` field records the seat. Editorial/writing items and legacy items (no source fields) default to EIC. The DA seat is not a verification persona (its Round-1 role is adversarial challenge, not fix verification); DA-sourced items route to the dimension-matching specialist, else EIC.
- EIC (or the synthesizer) integrates: builds the matrix, runs Phase 2B, derives the decision. It never overrides a specialist verdict except through the §3.4 / §7 recorded channels.
- Seat-agnostic by construction (#574 D1 compat): criteria attach to ITEMS; any future seat activation inherits its items' pre-commitments unchanged. D1 is not a dependency.
- Degradation: cards unavailable → the existing `[YARDSTICK-REGENERATED]` fallback governs configuration; routing then defaults to EIC-verifies-all with a `[ROUTING-DEGRADED: no round-1 cards]` line in the Judge Record.

---

## 11. Input manifest (hash-bound, freshness-checked)

Schema: `input_manifest.schema.json` — `{round_id, artifacts: {original_manuscript, revised_manuscript, revision_roadmap, editorial_decision_letter, response_to_reviewers, apply_reports[], round1_findings, round1_config_cards}, each: {path_or_passport_ref, sha256, present: bool}}`.

Rules:

- Emitted by the dispatching layer BEFORE Phase 1; its hash rides in every phase artifact (`input_manifest_hash`, `precommitment_hash`, `verdict_record_hash` chain), so the checker can prove all three gates saw the same inputs.
- `apply_reports[].output_draft_hash` must equal the manifest's revised-manuscript hash prefix (the 12-hex `base_draft_hash` format from `ars_apply_revision_patch.py`) — the consumer-side witness (§1.1). Mismatch = the draft was rewritten after apply → `manifest_hash_mismatch`, T0 abort (the untouched-block evidence is stale).
- Required-set policy: `revised_manuscript`, `revision_roadmap` are hard-required (absent → T0). `original_manuscript` absent → attribution capability degrades: every new issue is `indeterminate` (§8), never a guess. `response_to_reviewers` absent → Phase 2B runs claim-matching-empty (matrix `authors_claim` = "—"; commitments with `acknowledgment_only` evidence become `CANNOT_VERIFY` on the commitment axis). `round1_config_cards` absent → `[YARDSTICK-REGENERATED]` path. Every degradation is a visible marker, not a silent downgrade.
- Freshness: the manifest records the passport `version_label` / `origin_date` of each artifact; a roadmap older than the letter it should pair with, or an apply report not matching any manifest revision, fails closed.

---

## 12. Legacy boundary (SD-8)

Once this contract family ships, contract-governed re-review IS Stage 3' default: the orchestrator emits the manifest, runs the three gates, and aborts fail-closed on missing/invalid artifacts. The pre-v3.6.2 single-pass behavior survives ONLY behind `ARS_RE_REVIEW_LEGACY=1`, and every legacy-mode output carries `[LEGACY-NO-CONTRACT]` at the top of the Verification Review Report. No silent fallback: absent the flag, a run that cannot satisfy the contract prerequisites aborts with the specific T0 reason instead of quietly running legacy.

"Byte-equivalent fallback" claims are NOT made for LLM prose (the acceptance review's point); the legacy flag preserves ORCHESTRATION shape (one call, old template), nothing stronger. Standalone invocation outside the pipeline (user runs re-review directly with partial materials) follows the same rule: the mode asks for the missing required artifacts or the explicit legacy flag.

---

## 13. Checker: `scripts/check_re_review_synthesis.py`

Stdlib-only, same architecture class as `check_panel_synthesis.py` (#510: recompute both layers from primary artifacts; mismatch fails). Responsibilities:

1. Schema-validate the three phase artifacts + manifest (self-contained validators, no jsonschema dependency — repo convention).
2. Hash-chain: `input_manifest_hash` → `precommitment_hash` → `verdict_record_hash` verbatim binding; every pre-commitment `inherited_criterion.roadmap_text` matches the manifest's roadmap content.
3. Consumer-side `output_draft_hash` witness (§11).
4. Recompute invariants: every P1 roadmap item has exactly one pre-commitment record, one verdict record, one matrix row; `final_verdict != phase2a_verdict ⟺ adjustment` with closed-set basis; dissent bounds (§7); attribution evidence rules (§8); totality + first-match of T0-T9 — recompute the decision from `DecisionInputs` AND from the raw records, both must equal the emitted decision. Mismatch → `[SYNTHESIS-MISMATCH]`, exit 1 (voids the synthesis, parity with #510).
5. Goalpost witness: no `previously_missed` / `indeterminate` issue appears in the recomputed decision path.

Wired into `spec-consistency.yml` + the pytest manifest with a mutation-test suite (each invariant has a fixture that violates exactly it — Spec A §13 witness convention).

---

## 14. Persuasion-invariance eval (SD-11)

Paired-control scenarios joining `evals/heldout/` alongside the #574 E4 harness design (E4's formal-gate machinery is reused; its NOT COMPUTABLE 2026-07-27 outcome is a cohort result, not a harness defect):

- P-1: identical revision, strong vs weak Response-Letter rhetoric → verdicts must be identical.
- P-2: identical letter, substantive vs cosmetic manuscript change → verdicts must differ in the right direction.
- P-3: genuine regression vs previously-missed vs indeterminate-provenance triples → attribution + decision-impact must follow §8.
- P-4: valid evidence-backed rebuttal vs assertion-only rebuttal → only the former reaches `addressed_by_rebuttal`.
- P-5: fix at expected_change_surface vs equivalent fix elsewhere vs cosmetic edit AT the expected surface → equivalent fix accepted, location-only fix rejected.

Scoring: pairwise-consistency (the paired runs' delta is the metric), which is robust to single-run noise. Ground truth documented per scenario; zh-TW + en variants follow the #550 eval convention.

---

## 15. Interactions and boundaries

- **#539**: upgraded per §9; Judge Record gains `precommitment_hash`; consent boundary untouched.
- **#574 D1**: item-centric routing is D1-compatible by construction (§10); D1 remains not-a-dependency.
- **v3.11 commitment ledger (Kong A1)**: author-side commitments verify orthogonally; sidecar columns are distinct (`fulfillment_status` vs `final_verdict`), no collision.
- **E2 score trajectory**: OUT (SD-12); tracked under #574 backlog as repair-and-wire.
- **`reviewer_guided` / `reviewer_calibration`**: remain reserved, out of scope.
- **State machine**: no new transitions; `Stage 4' → 3'` prohibition untouched (§8 routes previously-missed forward, not backward).

## 16. Delivery-surface map

| Surface | Change |
|---------|--------|
| `shared/contracts/re_review/{precommitment,verdict_record,traceability,input_manifest}.schema.json` | NEW (§5) |
| `scripts/check_re_review_synthesis.py` + `scripts/test_check_re_review_synthesis.py` | NEW (§13) |
| `academic-paper-reviewer/references/re_review_mode_protocol.md` | Three-gate orchestration section replaces the read-letter-first Traceability Rule steps; verdict vocabulary + T-table; goalpost/dissent/adjustment sections; legacy flag |
| `academic-paper-reviewer/references/sprint_contract_protocol.md` | §7 table: `reviewer_re_review` row → dedicated contract family pointer |
| `academic-paper-reviewer/SKILL.md` | Reserved-modes note updated; re-review mode row gains contract dispatch |
| `shared/sprint_contract.schema.json` + `scripts/check_sprint_contract.py` tests | Enum removal + rejection regression test (§5.4) |
| `academic-pipeline/agents/pipeline_orchestrator_agent.md` | Stage 3' dispatch: manifest emission + three-call orchestration + abort surfacing |
| `shared/handoff_schemas.md` | Schema 11 sidecar note (points at `traceability.schema.json`) |
| `evals/heldout/` | P-1..P-5 paired controls (§14) |
| `.github/workflows/spec-consistency.yml` + pytest manifest | Checker + tests wired |

## 17. Implementation plan

- **PR-B1 (schemas + checker):** §5 schemas, §13 checker + mutation tests, CI wiring. No behavior change yet (nothing emits the artifacts).
- **PR-B2 (protocol + orchestration):** protocol/SKILL/orchestrator surfaces, three-gate grammar, legacy flag. Turns the contract ON as Stage 3' default.
- **PR-B3 (evals):** §14 paired controls + ground-truth docs.
- Landing order strict: B1 → B2 → B3. Each PR runs the standing three-track review gate (codex + dual Opus, exact-head 0/0).

## 18. Acceptance (replacement set, from the 2026-07-24 review)

- [ ] Phase 2A commits evidence/verdict before Response-Letter reveal (orchestration + persisted artifact ordering, checker-verified)
- [ ] Phase 2B cannot silently relax a committed verdict (adjustment-record invariant, checker-enforced)
- [ ] Re-review uses the exact author-visible Roadmap criterion + Round-1 criteria digest (§4 chain, hash-bound)
- [ ] `new_standard` exceptions explicit, restricted, checkpointed (§3.2/§6.4)
- [ ] All required artifacts hash-bound + freshness-checked; missing provenance → `indeterminate`/fail-closed (§11)
- [ ] Equivalent fixes and justified disagreement accepted on outcome-criterion merit (§3.4/SD-10)
- [ ] Dedicated schemas/checker validate item-level precommitment, dissent, traceability, decision (§5/§13)
- [ ] Exhaustive T0-T9 decision table; every valid input → exactly one outcome; invalid/incomplete → fail-closed (§6)
- [ ] Verifier routing follows item competence (§10)
- [ ] Cross-model divergence resolves (`primary_upheld | primary_revised | user_review_required`) before Accept (§9)
- [ ] Previously-missed routing destination is real and state-machine-legal (§8)
- [ ] Persuasion-invariance paired controls ship with documented ground truth (§14)

## 19. Non-goals

- No change to the P2 80% / P3 no-effect thresholds (made mechanical, not changed); the verdict VOCABULARY gains only `CANNOT_VERIFY` at the item level (already present in Schema 11 `verified`).
- No cross-model default-on.
- `reviewer_guided` / `reviewer_calibration` contracts remain future work.
- Round-1→Round-2 score-delta table (E2) stays in #574's backlog.
- No new pipeline state-machine transitions.
