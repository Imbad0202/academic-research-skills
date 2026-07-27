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

**`new_standard` boundary (SD-2):** Phase 1 may NOT add acceptance requirements beyond the inherited criterion. If operationalizing reveals that the Round-1 criterion is materially incomplete (e.g., it never named a check the concern obviously requires), the verifier records a `NewStandardRecord` (§5.1). Advisory by default — it cannot change the item verdict or the decision. The sole escalation path is §6.4 (integrity/ethics/safety/legal-compliance/fatal-validity, human checkpoint mandatory), entered by `classification: escalation_requested` and substantiated only at Phase 2A (§5.1).

**Retry:** one Phase 1 retry on lint failure, with the specific lint gap hinted in the system prompt — the actual v3.6.2 rule (`sprint_contract_protocol.md` §4); safe here for the same reason it is safe there (Phase 1 sees no manuscript, so the hint can leak nothing). Second failure → `[RE-REVIEW-ABORT: phase1_lint_failed]`, fail closed.

### 3.3 Phase 2A — evidence verdict (persuasion-blind)

Inputs add the original manuscript, the revised manuscript, and the patch/apply report(s); the Phase 1 output rides fenced as `<phase1_output>` (data, not instructions). The Response Letter is still withheld.

Per item, the verifier commits a verdict record (schema, §5.2):

- `verdict` ∈ `{FULLY_ADDRESSED, PARTIALLY_ADDRESSED, NOT_ADDRESSED, MADE_WORSE, CANNOT_VERIFY}` — assigned strictly against the Phase-1 operationalization, or through an explicit dissent record (§7), never silently off-criterion.
- `evidence_anchor` — typed anchor(s) into the REVISED manuscript (Schema 6 anchor grammar) for every verdict except `CANNOT_VERIFY`; `CANNOT_VERIFY` instead carries `cannot_verify_reason` (e.g., evidence surface inaccessible, criterion requires an artifact not in the input set).
- `change_summary` — what actually changed relative to the original manuscript (from diff/apply report + comparison), one sentence.
- `residual_gap` — REQUIRED for `PARTIALLY_ADDRESSED`: the concrete missing part, with a `residual_magnitude` ∈ `{must_fix, should_fix, consider}` re-grading of what remains (feeds the §6 decision derivation).

New issues discovered while reading the revised manuscript are recorded as new-issue records with attribution (§8) — also before the letter is read, because attribution must not be colored by the author's framing of what they changed. The new-issue SET — each record's id, attribution, and severity — **freezes at `[EVIDENCE-COMMITTED]`**: Phase 2B may not add, remove, or reclassify new issues (§5.3 carries the frozen copy; §13 witnesses byte-level id/attribution/severity equality). Anything noticed only after the letter is read goes to the decision-inert `post_letter_observations[]` list (§5.3), seeding the next round.

**Prohibitions:** no reference to the Response Letter (it is absent); no verdict revision after emission (2A output is committed — the orchestrator persists it before dispatching 2B). Ends with `[EVIDENCE-COMMITTED]`.

**No retry.** The v3.6.2 no-Phase-2-retry discipline (`sprint_contract_protocol.md` §5) applies unchanged once the revised manuscript has been seen: a lint-guided regeneration after evidence exposure is exactly the channel the no-retry rule closes. A 2A lint failure → `[RE-REVIEW-ABORT: phase2a_lint_failed]`, fail closed. Phase 2B lint failure likewise aborts without retry (`phase2b_lint_failed`).

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
| `scope_correction` | either direction | The letter reveals the 2A reading misidentified the item's target (wrong section/claim); re-verification against the correct target, manuscript-side anchor |
| `cross_model_adjudication` | either direction | A §9 resolution concluded `primary_revised`, or a §7 dissent adjudication concluded `original_upheld` and re-applying the ORIGINAL criterion changed the verdict (`replacement_approved` keeps the 2A verdict, which was already made under the replacement criterion — no adjustment exists); `source_ref` names the §5.3 record. Outcome compatibility is checker-enforced (§13): `resolution:<item_id>` must resolve to `primary_revised`, `adjudication:<dissent_id>` must resolve to `original_upheld` |

Commitment-axis outcomes (Kong A1 — including the `acknowledgment_only` evidence class) are recorded ONLY in the commitment fields (`fulfillment_status` etc.) and NEVER produce an AdjustmentRecord: the verdict axis is untouched, so the §5.3 biconditional is not triggered — the two axes stay orthogonal (§15).

A `to_verdict` upgrade with basis `valid_rebuttal` on an item whose Round-1 severity is `critical` additionally requires the §9 cross-model adjudication when active, else a decision-letter disclosure line. An assertion in the letter with no locatable manuscript evidence changes nothing. Ends with `[MATRIX-COMMITTED]`.

### 3.5 Abort taxonomy

`[RE-REVIEW-ABORT: <reason>]` with closed reasons: `phase1_lint_failed`, `phase2a_lint_failed`, `phase2b_lint_failed`, `manifest_incomplete`, `manifest_hash_mismatch`, `criteria_drift` (§7), `synthesis_mismatch` (§13). This bracketed form is the single canonical machine-consumed marker grammar — §13's recomputation failure emits `[RE-REVIEW-ABORT: synthesis_mismatch]`, not a separate token. Every abort is fail-closed: no decision is emitted, the pipeline surfaces the abort to the user at the Stage 3' checkpoint. Distinct from aborts, `decision_state: user_review_required` (§6 G2) is a DEFERRED outcome — the matrix is delivered, the decision is not.

---

## 4. Criterion inheritance chain

The yardstick, in precedence order — each level only OPERATIONALIZES the level above, never extends it:

1. Schema 7 RoadmapItem `verification_criteria` (`handoff_schemas.md:443`) — author-visible since Round 1.
2. The Editorial Decision Letter's per-item **Acceptance criteria** field (`templates/editorial_decision_template.md:118`) — author-visible.
3. The driving finding's severity + typed `evidence_anchor` + raising reviewer(s) (Schema 7 transported fields + the required `reviewer` field, #574 A2/A3) — fixes WHAT the concern was about and WHO raised it.
4. The Round-1 Reviewer Configuration Cards + target venue (frozen; § Yardstick Continuity) — fixes the field/venue standard the criteria were written under.

A Phase-1 operationalization that cannot be traced to levels 1-4 for its item is a `new_standard` (§3.2), advisory. The checker (§13) verifies binding: every pre-commitment record quotes its level-1 criterion verbatim and the quote must match the roadmap (hash-bound via the §11 manifest).

---

## 5. Artifacts

All new artifacts live under `shared/contracts/re_review/` (schemas) and are runtime-emitted per re-review round (instances travel in the Material Passport like other Schema 9 cargo). NOT part of `sprint_contract.schema.json` — see §5.4.

### 5.1 `precommitment.schema.json`

Top-level: `{contract_version, round_id, input_manifest_hash, items: [PrecommitmentRecord], new_standards: [NewStandardRecord]}`.

`PrecommitmentRecord`: `{item_id (Schema 7 id, e.g. REV-001), priority, inherited_criterion {roadmap_text, letter_text?}, operationalization {fully_addressed, partially_addressed, made_worse_discriminator}, expected_change_surface, equivalence_policy: "allowed", source_reviewer}`. `source_reviewer` is a VERBATIM copy of the Schema 7 item's required `reviewer` field (a free-text STRING, e.g. `"R1, R3"`) — no new Schema 7 fields exist or are added. The emitter ALSO produces `source_reviewer_labels: list[string]` by the §10 normalization grammar (closed vocabulary `{EIC, R1, R2, R3, DA}`; possibly empty); routing consumes ONLY the normalized list. (Schema 7's `type` field is the revision-MAGNITUDE label `Major|Minor|Editorial` and is NOT a competence key — it plays no routing role.) Priority 2 lighter form: `operationalization.fully_addressed` only. Priority 3 (`consider`) items get NO pre-commitment record (§5.2 `not_precommitted`).

`NewStandardRecord`: `{item_id | "global", standard_text, why_not_in_round1, classification: "advisory" | "escalation_requested"}`. An `escalation_requested` entry is only a REQUEST — the substantiating `EscalationExceptionRecord` (§5.2) is created at Phase 2A (its original-manuscript anchor cannot exist earlier: Phase 1 withholds both manuscripts) and points back via `new_standard_ref`; a request never substantiated at 2A lapses to advisory. 2A may also emit an exception with no Phase-1 request (discovered only on reading the manuscripts).

### 5.2 `verdict_record.schema.json` (Phase 2A)

Top-level: `{round_id, precommitment_hash, items: [VerdictRecord], new_issues: [NewIssueRecord], dissents: [DissentRecord], escalation_exceptions: [EscalationExceptionRecord]}`.

`VerdictRecord`: `{item_id, verdict, evidence_anchor[] | cannot_verify_reason, change_summary, residual_gap? {text, residual_magnitude}, verified_by (§10), applied_criterion: "precommitted" | "dissented:<dissent_id>" | "not_precommitted"}`. `not_precommitted` is valid ONLY for `priority: consider` items (which have no Phase-1 record, §3.2); a P1/P2 item carrying it fails the checker.

`EscalationExceptionRecord` (§6.4): `{exception_id, new_standard_ref?, escalation_class (§6.4 closed set), reason_code, evidence_anchor (original-manuscript-side), why_round1_missed_it, mechanical_decision_impact: "Minor Revision" | "Major Revision", approval_state: "pending"}` — emitted at 2A with `pending`; approval happens only in §5.3 `escalation_approvals`.

`NewIssueRecord` and `DissentRecord`: §8 / §7.

### 5.3 `traceability.schema.json` (Phase 2B — machine-readable Schema 11 sidecar)

Top-level: `{round_id, verdict_record_hash, rows: [MatrixRow], adjustments: [AdjustmentRecord], new_issues: [NewIssueRecord], post_letter_observations: [], dissent_adjudications: [DissentAdjudication], cross_model_resolutions: [CrossModelResolution], escalation_approvals: [EscalationApproval], decision_inputs: DecisionInputs, decision_state, abort_reason?}`.

`MatrixRow`: `item_id` (the Schema 7 roadmap id, e.g. `REV-001` — the JOIN KEY every §13 invariant uses; `concern_id` remains Schema 11's human numbering `R1/S1/N1` and is never used for joins) + the Schema 11 required fields (`concern_id`, `priority`, `original_comment`, `authors_claim`, `revision_location`, `verified`, `status`, `quality_assessment`) plus `final_verdict`, `phase2a_verdict`, `adjustment_id?`, `addressed_by_rebuttal?`, `cross_model_status?` / `cross_model_verdict?` (#539 fields, unchanged semantics). EVERY Schema 7 roadmap item, all priorities, has exactly one row (Schema 11's completeness rule, `handoff_schemas.md` § Validation). Invariant: `final_verdict != phase2a_verdict ⟺ adjustment_id` present — ALL rows, every priority. Derived Schema 11 fields are mechanical: `status` maps 1:1 from `final_verdict` (for `CANNOT_VERIFY` via the §16 `status` enum extension), and `verified` maps 5→4: `FULLY_ADDRESSED → YES`, `PARTIALLY_ADDRESSED → PARTIAL`, `NOT_ADDRESSED → NO`, `MADE_WORSE → NO` (the concern stands unresolved — verification happened, outcome negative), `CANNOT_VERIFY → CANNOT_VERIFY`. This derivation REPLACES the letter-driven `verified` rule (`handoff_schemas.md` Schema 11 Validation: empty `authors_claim` → `CANNOT_VERIFY`) under contract mode — letter absence is carried by the §11 degradation markers, not by `verified`; §16 schedules that validation-rule rewrite. Schema 11 prose remains the human surface; the sidecar is what the checker recomputes from — no index-walking (rows carry ids, mirroring the #268-desync-free convention).

`AdjustmentRecord`: `{adjustment_id, item_id, from_verdict, to_verdict, basis (closed set §3.4), evidence_anchor, rationale, source_ref?}`. `source_ref` is REQUIRED iff `basis = cross_model_adjudication`, with the closed grammar `"adjudication:<dissent_id>"` (a `DissentAdjudication`) or `"resolution:<item_id>"` (a `CrossModelResolution`; item_id is its unique key). Referential integrity (§13): `from_verdict` equals the item's `phase2a_verdict`, `to_verdict` equals its `final_verdict`, ids unique, and every `source_ref` resolves to an existing record of the named kind AND the compatible outcome (`resolution:* → primary_revised`; `adjudication:* → original_upheld` — §3.4).

`new_issues`: the FROZEN 2A set, copied verbatim (id, attribution, severity, anchors byte-identical to §5.2 — §13 witness). `post_letter_observations[]`: free-form advisory entries noticed only after letter reveal; decision-inert; next-round seed.

`DissentAdjudication`: `{dissent_id, adjudicator: "cross_model" | "user", outcome: "replacement_approved" | "original_upheld", rationale}` (§7).

`CrossModelResolution`: `{item_id, state: "primary_upheld" | "primary_revised", rationale}` — REQUIRED for every P1 row whose `cross_model_status = diverges`; no record exists (or is needed) for `agree` / `unavailable` / `not_configured` rows (§9).

`EscalationApproval`: `{exception_id, approval_state: "approved" | "rejected", approved_by: "user"}` — recorded from the Stage 3' checkpoint outcome (§6.4).

`DecisionInputs`: the mechanically-derived aggregates §6 consumes — counts per final-verdict class per priority; `p2_addressed_rate {numerator, denominator}` (§6 definition); regression list with severities; frozen non-regression new-issue ids; dissent-bound state + adjudication summary; per-P1-item cross-model resolution summary; approved escalation floors; `reject_recommended: bool` — emitted so the checker recomputes the decision from the same numbers the synthesizer used.

`decision_state`: `"Accept" | "Minor Revision" | "Major Revision" | "user_review_required" | "aborted"` — the emitted outcome §13 compares against; `abort_reason` (from the §3.5 closed set) REQUIRED iff `aborted`.

### 5.4 Schema 13 disposition

`reviewer_re_review` is REMOVED from the `sprint_contract.schema.json` `mode` enum (present today at `shared/sprint_contract.schema.json:25`, never had a template — the acceptance review's point that "schema accepts mode" is vacuously satisfiable). The §7 panel-mapping table in `sprint_contract_protocol.md` changes the `reviewer_re_review` row to point at THIS contract family; `check_sprint_contract.py` needs no new gating (the mode value no longer validates), and one regression test pins that a Schema 13 contract claiming `mode: reviewer_re_review` now FAILS validation with a pointer to `shared/contracts/re_review/`. `reviewer_calibration` / `reviewer_guided` stay reserved in the enum (still planned as Schema 13-shaped).

---

## 6. Verdict → decision derivation

Inputs: per-item final verdicts (P1 = `must_fix`, P2 = `should_fix`, P3 = `consider`), `residual_magnitude` re-grades, the frozen new-issue records (attribution + severity), dissent-bound state + adjudication records, cross-model resolution records, approved escalation floors, manifest status. Output domain: `decision_state ∈ {Accept, Minor Revision, Major Revision, user_review_required}` or a fail-closed abort (§3.5) — **`Reject` is NOT a Stage 3' decision** (the state machine gives Stage 3' exactly two exits: Accept/Minor → 4.5, Major → 4'; `pipeline_state_machine.md` § State Transition Rules); severity-flagged cases set `reject_recommended` instead (below). Declared decision order for floor arithmetic: `Accept < Minor Revision < Major Revision`.

**`p2_addressed_rate` definition (mechanizing the previously-prose 80% rule):** numerator = |P2 items with `final_verdict ∈ {FULLY_ADDRESSED, PARTIALLY_ADDRESSED}`|; denominator = |P2 items|; zero P2 items → rate is vacuously 100%. Computed over FINAL (post-2B) verdicts at decision time — a §3.4-adjusted verdict counts, which is safe because every adjustment is typed and evidence-bound, so a letter assertion alone still cannot move the rate. This deliberately REPLACES the ambiguous "should have a response" reading of `re_review_mode_protocol.md` § Verification Logic: a numerator counting author explanations would let a persuasive letter buy the rate without manuscript change — the exact channel §1 exists to close. A `NOT_ADDRESSED` item's author explanation is still recorded in the matrix; it does not count toward the rate.

Derivation runs in three ordered steps; within each step, FIRST match wins.

**Step 1 — gates (abort / defer):**

| # | Condition | Outcome |
|---|-----------|---------|
| G0 | Input manifest incomplete or hash-mismatched (§11) | `[RE-REVIEW-ABORT: manifest_incomplete \| manifest_hash_mismatch]` |
| G1 | Any row (any priority) where `final_verdict != phase2a_verdict` without an `adjustment_id`, OR a §7 dissent bound tripped with no covering `dissent_adjudications` record | `[RE-REVIEW-ABORT: criteria_drift]` |
| G2 | Any P1 row with `cross_model_status = diverges` and no `cross_model_resolutions` record (§9) | `decision_state: user_review_required` — matrix delivered, decision deferred to the user checkpoint |

Rows with `cross_model_status ∈ {agree, unavailable, not_configured}` need no resolution record and never trigger G2 (§9 disclosure rules apply instead).

**Step 2 — base decision (first match; total by construction):**

| # | Condition | Base |
|---|-----------|------|
| B1 | Any P1 `MADE_WORSE` with driving-finding severity `critical`, OR any `regression`-attributed new issue with severity `critical` (fatal-validity class) | **Major Revision** + `reject_recommended: true` |
| B2 | ≥ 50% of P1 items in `{NOT_ADDRESSED, MADE_WORSE}` | **Major Revision** + `reject_recommended: true` |
| B3 | Any P1 in `{NOT_ADDRESSED, MADE_WORSE, CANNOT_VERIFY}`, OR any `regression`-attributed new issue with severity `major` | **Major Revision** |
| B4 | Any P1 `PARTIALLY_ADDRESSED` with `residual_magnitude: must_fix` | **Major Revision** |
| B5 | Any P1 `PARTIALLY_ADDRESSED` with `residual_magnitude: should_fix \| consider`, OR `p2_addressed_rate < 80%`, OR any P2 `MADE_WORSE`, OR any `regression`-attributed new issue with severity `minor` | **Minor Revision** |
| B6 | Residual (provably: all P1 `FULLY_ADDRESSED` incl. `addressed_by_rebuttal`; `p2_addressed_rate ≥ 80%`; no P2 `MADE_WORSE`; no regression-attributed new issues) | **Accept** |

**Step 3 — floors:** `decision_state = max(base, every approved EscalationApproval's mechanical_decision_impact)` under the declared order. Pending or rejected approvals contribute nothing.

`reject_recommended: true` (B1/B2, or a `research_integrity`-class approved exception) rides in `DecisionInputs` and the report: it tells the user at the Stage 3' checkpoint that severity warrants considering abandonment — abandonment is the standing any-stage user exception (`pipeline_orchestrator_agent.md` § Exception Handling), not a state-machine transition, so §15's no-new-transitions holds.

Notes:

- `CANNOT_VERIFY` on a P1 caps the decision at Major (B3): acceptance requires positive verification, and fail-closed beats benefit-of-the-doubt. On P2 it counts against `p2_addressed_rate`; on P3 it is recorded, not decision-driving.
- `MADE_WORSE` per priority: P1 → B1/B3; P2 → B5 Minor floor (and it counts against `p2_addressed_rate`); P3 → recorded, next-round seed, no decision effect. Damage that exceeds the item's own scope is item-verdict-visible here AND, when it manifests outside any roadmap item's surface, separately becomes a `regression` new issue (§8) — the two channels are not mutually exclusive.
- `previously_missed` and `indeterminate` new issues NEVER appear in Step 2 (goalpost guard, §8) — only `regression` attribution can move the decision.
- P3 items never affect any step (existing semantics, unchanged).
- Totality: B1-B5's negations jointly force B6's parenthetical, and Schema 6's closed severity set (`critical`/`major`/`minor`) is covered by B1/B3/B5 — checker-enforced (§13).

### 6.4 Escalation exception (the ONLY path around the goalpost guard and `new_standard` advisory default)

Closed class set: `{research_integrity, ethics, safety, legal_compliance, fatal_validity}`. The `EscalationExceptionRecord` (§5.2, emitted at Phase 2A with `approval_state: pending`) requires ALL of: `escalation_class`, `reason_code`, original-text evidence anchor (into the ORIGINAL manuscript — proving it existed in Round 1; revision-introduced content is a `regression` instead, already handled by B1/B3/B5), `why_round1_missed_it`, and `mechanical_decision_impact ∈ {Minor Revision, Major Revision}` (a Step-3 floor; Reject is not a Stage 3' decision — a `research_integrity`-class exception additionally sets `reject_recommended`). **Mandatory human checkpoint:** the user must explicitly approve at the Stage 3' checkpoint; the outcome is recorded as an `EscalationApproval` (§5.3) and the derivation re-runs with it — `pending`/`rejected` contribute no floor (advisory only). Stage 4.5's integrity gate independently sees the exception record (it travels in the passport).

---

## 7. Dissent records and bounds

A dissent is the Phase 2A discovery that a pre-committed operationalization cannot be applied as written. It is NOT a verdict-relaxation channel — it swaps the criterion, visibly, before the verdict.

`DissentRecord`: `{dissent_id, item_id, criterion_hash (of the Phase-1 record), reason_code ∈ {criterion_ambiguous, criterion_infeasible_as_written, evidence_surface_moved, criterion_error}, original_operationalization, replacement_operationalization, evidence, decision_impact_note}`. The item's verdict record then carries `applied_criterion: "dissented:<dissent_id>"`.

**Bounds (SD-5):** dissent on a P1 item, or dissents on > ⌈N/3⌉ of all items (N = total roadmap items), triggers independent adjudication BEFORE the verdicts stand: when cross-model is active, the §9 judge blind-applies the ORIGINAL Phase-1 criterion first, then separately adjudicates the replacement; when not active, the dissent(s) surface at a user checkpoint (the user approves or rejects the replacement). Every adjudication outcome is recorded as a `DissentAdjudication` (§5.3) — `replacement_approved` lets the dissented criterion stand; `original_upheld` re-applies the original criterion, and any resulting verdict change rides an adjustment record with basis `cross_model_adjudication`. A tripped bound with no covering adjudication record = G1 abort. This keeps dissent from becoming a quiet goalpost-reset channel while leaving a legitimate path for genuinely broken criteria.

Unlike the v3.6.2 one-dimension-per-reviewer cap (built for 5-7 fixed dimensions), the bound is proportional because roadmap item counts vary widely.

---

## 8. New-issue attribution and the goalpost guard

Every issue found during Phase 2A that is not traceable to a roadmap item gets a `NewIssueRecord`: `{new_issue_id, description, location_anchor, severity (Schema 6 vocabulary), attribution, attribution_evidence}`.

`attribution` (closed):

- `regression` — introduced by the revision. Evidence: the anchored content is in the revised manuscript but not the original (diff/apply-report-supported). MAY affect the decision (T4/T6/T8).
- `previously_missed` — present in the original manuscript; Round 1 missed it. Evidence: anchored in BOTH versions. Reported, CANNOT escalate the decision (only §6.4 overrides). Routed forward: when `decision_state` is Major Revision, it enters the new Stage 3' → 4' Roadmap as a `priority: consider` item whose `description` carries the `[PREVIOUSLY-MISSED: NEW-<n>]` prefix (Schema 7's closed priority enum is untouched — `consider` already has no decision effect, matching the non-escalation rule; the prefix preserves provenance); when `decision_state` is Accept or Minor Revision, the frozen `NewIssueRecord`s reach the Stage 4.5 final integrity check as Material Passport cargo (the traceability sidecar, §5.3). NOTE the transition geometry: Accept/Minor at Stage 3' goes DIRECTLY to 4.5 (no Stage 4' between), so the orchestrator's handoff table needs a **Stage 3' → 4.5 row** (new row, existing legal transition) carrying the sidecar; the separate Stage 4/4' → 4.5 row is extended for the Major path (sidecar rides through 4' with the roadmap). Both rows plus `integrity_verification_agent`'s input list are scheduled in §16, and PR-B2 ships one fixture per path (Accept-direct and Major-via-4') proving the records arrive at the gate. No new artifact, no new transition. `decision_state: user_review_required` defers routing along with the decision. Both destinations exist in the current state machine — no new transition is created (the `Stage 4' → 3'` prohibition, `pipeline_state_machine.md` § Prohibited Transitions, is untouched).
- `indeterminate` — provenance cannot be established (original manuscript unavailable, non-comparable formats, manifest gaps). Treated as `previously_missed` for decision purposes (cannot escalate) and flagged `[ATTRIBUTION-INDETERMINATE]` in the report — never silently promoted to `regression` (SD-9).

The guard is enforceable exactly because Phase 1 fixed the item baseline: "not traceable to a pre-committed item" is now a mechanical check (no matching `item_id`), not a judgment call.

---

## 9. Cross-model resolution gate (#539 upgrade)

The existing #539 per-item pass (transport, verdict set, data-fencing, name-stripping — `re_review_mode_protocol.md` § Judge Independence) is reused with three changes:

1. **Input**: the judge receives the Phase-1 pre-committed criterion for the item (data-fenced) and judges "does the revision meet the committed criterion" — not "is the primary's verdict agreeable". The Judge Record gains a `precommitment_hash` line.
2. **Resolution gate (SD-6):** a `diverges` cell on a P1 item must resolve before the decision derivation runs, and the resolution is RECORDED as a `CrossModelResolution` (§5.3): `primary_upheld` (primary re-examined, verdict stands, one-line rationale) or `primary_revised` (verdict changes via an adjustment record with basis `cross_model_adjudication`). A `diverges` row with no record → G2 `user_review_required`. `agree` / `unavailable` / `not_configured` rows need no record and resolve implicitly (unavailable/not_configured keep the existing single-family disclosure).
3. **Dissent adjudication order:** when the primary dissented from a criterion (§7), the judge FIRST blind-applies the original criterion (without seeing the dissent), THEN separately adjudicates the replacement — two calls, so the replacement cannot anchor the original's application.

Consent boundary unchanged: cross-model runs only when configured + consented; nothing here makes it default-on. Single-family runs satisfy the gate trivially (every state is `not_configured`) but carry the disclosure — the gate adds protection when the machinery exists, it does not manufacture a dependency.

---

## 10. Verifier routing (SD-7)

Items are verified by competence, not by a single EIC persona (`eic_agent.md` scopes EIC as bird's-eye editorial, not deep methods verification):

- Each pre-commitment record carries `source_reviewer` (verbatim Schema 7 string) + `source_reviewer_labels` (normalized, §5.1); no Schema 7 change is needed and none is scheduled.
- **Normalization grammar (emitter-side, mechanical):** split `source_reviewer` on the separator set `{",", "/", ";", " and ", "&"}`; trim whitespace; case-fold. A token normalizes to a canonical label by: `EIC` / `Editor-in-Chief` → `EIC`; `R<n>` / `Reviewer <n>` / `Peer Reviewer <n>` (with or without a trailing ` — <specialty>` suffix) → `R<n>`; `DA` / `Devil's Advocate` (any parenthetical suffix) → `DA`. Unrecognized tokens are DROPPED (never guessed). The result, in original order and deduplicated, is `source_reviewer_labels`; the checker validates it against the closed vocabulary.
- **Card-side mapping:** each Round-1 Configuration Card's `Role` line is normalized by the SAME token grammar to declare which canonical label its seat answers to. An item routes to the seat of the FIRST label in `source_reviewer_labels` that maps to a non-DA scoring seat; if none does (empty list, DA-only items, `source_kind` items with editorial provenance), it routes to EIC. Seat personas come from the frozen cards; the `verified_by` field records the seat. The DA seat is never a verification persona (its Round-1 role is adversarial challenge, not fix verification) — the map contains no DA target.
- EIC (or the synthesizer) integrates: builds the matrix, runs Phase 2B, derives the decision. It never overrides a specialist verdict except through the §3.4 / §7 recorded channels.
- Seat-agnostic by construction (#574 D1 compat): criteria attach to ITEMS; any future seat activation inherits its items' pre-commitments unchanged. D1 is not a dependency.
- Degradation: cards unavailable → the existing `[YARDSTICK-REGENERATED]` fallback governs configuration; routing then defaults to EIC-verifies-all with a `[ROUTING-DEGRADED: no round-1 cards]` line in the Judge Record.

---

## 11. Input manifest (hash-bound, freshness-checked)

Schema: `input_manifest.schema.json` — `{round_id, artifacts: {original_manuscript, revised_manuscript, revision_roadmap, editorial_decision_letter, response_to_reviewers, apply_reports[], round1_findings, round1_config_cards}, each: {path_or_passport_ref, sha256, present: bool, version_label: string|null, origin_date: string|null}}` — the two freshness fields are copied from the artifact's Material Passport entry when it is passport-tracked, else `null` (a `null` on a passport-tracked artifact fails the checker; `null` on a loose file is a visible degradation, freshness rules skip it).

Rules:

- Emitted by the dispatching layer BEFORE Phase 1; its hash rides in every phase artifact (`input_manifest_hash`, `precommitment_hash`, `verdict_record_hash` chain), so the checker can prove all three gates saw the same inputs.
- `apply_reports[].output_draft_hash` must equal the manifest's revised-manuscript hash prefix (the 12-hex `base_draft_hash` format from `ars_apply_revision_patch.py`) — the consumer-side witness (§1.1). Mismatch = the draft was rewritten after apply → `manifest_hash_mismatch`, T0 abort (the untouched-block evidence is stale).
- Required-set policy: `revised_manuscript`, `revision_roadmap` are hard-required (absent → T0). `original_manuscript` absent → attribution capability degrades: every new issue is `indeterminate` (§8), never a guess. `response_to_reviewers` absent → Phase 2B runs claim-matching-empty (matrix `authors_claim` = "—"); commitments whose evidence class is `acknowledgment_only` keep their author-declared `fulfillment_status` UNCHANGED (the closed Schema 11 enum gains no value) but cannot be independently confirmed, so each affected commitment carries the report-level advisory flag `[COMMITMENT-EVIDENCE-ABSENT: acknowledgment_only — no response letter]`; the existing `COMMITMENT_GAP` rule applies unchanged. `round1_config_cards` absent → `[YARDSTICK-REGENERATED]` path. Every degradation is a visible marker, not a silent downgrade.
- Freshness: consumed from the per-artifact `version_label` / `origin_date` fields above; a roadmap older than the letter it should pair with, or an apply report not matching any manifest revision, fails closed.

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
4. Recompute invariants: EVERY roadmap item, all priorities, has exactly one matrix row; every P1/P2 item has exactly one pre-commitment record and one verdict record; every P3 verdict record carries `applied_criterion: not_precommitted` (and only P3 may); `final_verdict != phase2a_verdict ⟺ adjustment` with closed-set basis and referential integrity (`from_verdict` = `phase2a_verdict`, `to_verdict` = `final_verdict`, unique resolvable ids); tripped dissent bounds have covering adjudication records (§7); every P1 `diverges` row has a `CrossModelResolution` (§9); escalation floors applied iff `approval_state: approved` (§6.4); attribution evidence rules (§8); Step 1→2→3 of §6 recomputed from `DecisionInputs` AND independently from the raw records — both must equal the emitted `decision_state` (+ `abort_reason` when aborted). Mismatch → `[RE-REVIEW-ABORT: synthesis_mismatch]`, exit 1 (voids the synthesis, parity with #510).
5. Goalpost witness: no `previously_missed` / `indeterminate` issue appears in the recomputed decision path; the §5.3 `new_issues` set is byte-identical (ids, attributions, severities, anchors) to the frozen §5.2 set — any 2B-side add/drop/reclassification fails.

**Execution timing — runtime first, CI additionally (mirroring #510's protocol-wired precedent):** the orchestrator invokes the checker as a MANDATORY Stage 3' step, immediately after the Phase 2B artifacts are persisted and BEFORE the decision is surfaced to the user — this is where the §5.3 invariants (including the all-rows ⟺ biconditional and the new-issue freeze witness) actually bite; a CI-only wiring would leave them unenforced in real runs. Graded exit codes: `0` pass; `1` recomputation mismatch → `[RE-REVIEW-ABORT: synthesis_mismatch]`; `2` schema/manifest/reference invalid → the matching §3.5 abort reason. The §1.1 `output_draft_hash` consumer witness runs in the same invocation. CI wiring (`spec-consistency.yml` + the pytest manifest) is additive: a mutation-test suite where each invariant has a fixture violating exactly it (Spec A §13 witness convention), plus the two §8 routing fixtures.

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
| `academic-paper-reviewer/references/re_review_mode_protocol.md` | Three-gate orchestration section replaces the read-letter-first Traceability Rule steps; verdict vocabulary + §6 derivation; goalpost/dissent/adjustment sections; legacy flag |
| `academic-paper-reviewer/references/sprint_contract_protocol.md` | §7 table: `reviewer_re_review` row → dedicated contract family pointer |
| `academic-paper-reviewer/SKILL.md` | Reserved-modes note updated; re-review mode row gains contract dispatch |
| `shared/sprint_contract.schema.json` + `scripts/check_sprint_contract.py` tests | Enum removal + rejection regression test (§5.4) |
| `academic-pipeline/agents/pipeline_orchestrator_agent.md` | Stage 3' dispatch: manifest emission + three-call orchestration + mandatory §13 checker invocation before the decision surfaces + abort surfacing; NEW Stage 3' → 4.5 handoff row (Accept/Minor direct path) + extended Stage 4/4' → 4.5 row (Major path), both forwarding the sidecar's frozen `previously_missed`/`indeterminate` records (§8) |
| `academic-pipeline/agents/integrity_verification_agent.md` (Stage 4.5 input list) | Consumes the forwarded previously-missed records as integrity-check input (§8) |
| `shared/handoff_schemas.md` | Schema 11 sidecar note (points at `traceability.schema.json`) + Schema 11 `status` enum gains `CANNOT_VERIFY` + the Validation rule "empty `authors_claim` → `verified: CANNOT_VERIFY`" is scoped to legacy mode (contract mode derives `verified` from `final_verdict`, §5.3) |
| `shared/contracts/README.md` | Reserved-modes sentence updated (`reviewer_re_review` leaves the Schema 13 enum for the dedicated family; `reviewer_calibration`/`reviewer_guided` stay) |
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
- [ ] Exhaustive G0-G2/B1-B6/floor derivation; every valid input → exactly one `decision_state`; invalid/incomplete → fail-closed (§6)
- [ ] Verifier routing follows item competence (§10)
- [ ] Cross-model divergence resolves (`primary_upheld | primary_revised | user_review_required`) before Accept (§9)
- [ ] Previously-missed routing destination is real and state-machine-legal (§8)
- [ ] Persuasion-invariance paired controls ship with documented ground truth (§14)

## 19. Non-goals

- The P2 80% threshold value and the P3 no-effect rule are unchanged; what changes is that the 80% rule's operands are now DEFINED (§6 `p2_addressed_rate`, manuscript-side by deliberate choice) and Schema 11's `status` enum gains `CANNOT_VERIFY` (§16; the `verified` field already carried it).
- No cross-model default-on.
- `reviewer_guided` / `reviewer_calibration` contracts remain future work.
- Round-1→Round-2 score-delta table (E2) stays in #574's backlog.
- No new pipeline state-machine transitions.
