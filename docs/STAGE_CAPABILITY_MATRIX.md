# ARS Stage Capability / Evidence Matrix

<!-- GENERATED FILE — do not edit by hand. -->
<!-- Source: shared/contracts/capability/stage_capability_matrix.json -->
<!-- Regenerate: python3 scripts/check_stage_capability_matrix.py --render -->

Machine-readable source of record for what evidence exists per pipeline
stage and the maximum claim that evidence licenses (#745). A row is an
index entry, not an endorsement: DESIGNED and NOT_RUN mean exactly that,
and no consumer may state more than the row's recorded claim ceiling.

## `rq_formation`

### rq_formation.wording_advisory

- **Mechanism**: Socratic RQ wording-pattern advisory (#501/#503/#505): noun-swap judgment over illustrative WP shells, off-list shells may fire at the same confidence bar
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_rq_framing_patterns.py; scripts/test_check_rq_framing_patterns.py)
- **Behavioral evidence**: MEASURED — post-#505 overall miss 0.094 across both replicates (baseline 0.344-0.375); false-fire 0/16 preserved (evals/heldout/rq_framing_offlist; model claude-sonnet-5 (runtime judge); population 48-item held-out off-list shell + domain-native negative set, en; 2026-07-11) — report: evals/heldout/rq_framing_offlist/measurement-2026-07-11-505.json
- **External/human outcome evidence**: none
- **Known exclusions**: wording only: no judgment of idea quality, novelty, feasibility, or contribution; judgments are model- and time-specific; re-run rather than reuse the numbers
- **Transport limits**: single judge model (claude-sonnet-5), single language (en), one measurement date
- **Claim anchors**: README.md — "held-out miss rate 0.34–0.38 → 0.094 with false-fire 0/16 preserved"
- **Maximum licensed claim**: On the recorded held-out set and judge model, the advisory's miss rate was 0.094 with zero false fires; no claim beyond that set or model.
- **Next required evaluation**: re-run the held-out set on the current session model family; extend to zh-TW shells

### rq_formation.ideation_diversity

- **Mechanism**: Within-session ideation-diversity measurement design (#659): two Layer-1 Socratic mechanisms, scholar-owned breadth vs AI-surfaced facet follow-through
- **Mechanism status**: DESIGNED / deterministic conformance: CI_GATED (pinned by scripts/validate_ideation_diversity_assets.py; scripts/test_validate_ideation_diversity_assets.py)
- **Behavioral evidence**: DESIGNED
- **External/human outcome evidence**: none
- **Known exclusions**: does not measure idea quality, novelty, cross-user homogenization, or real scholars' creativity; synthetic scholar roles only; real-scholar study requires a new protocol and consent
- **Transport limits**: no-call envelope only: no subject, judge, or adjudicator session has been authorized
- **Maximum licensed claim**: A frozen measurement design and offline validation assets exist; no breadth or diversity claim is computable.
- **Next required evaluation**: dispatch the frozen Phase-2 envelope with two blinded human judges and an arm-blind adjudicator (#659)

### rq_formation.research_workflow_profile

- **Mechanism**: research_workflow_profile @ research-workflow-profile/1.0 (#742): explicit user selection or visible field-general fallback, canonical-content binding, and append-only correction receipts with non-destructive stale marks
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/research_workflow_profile.py::validate_profile; scripts/test_research_workflow_profile.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: registered under rq_formation only because selection or confirmation occurs there; the profile governs every downstream stage and this single row is not a stage-coverage claim; profiles declare applicability and vocabulary only; they do not judge manuscript quality, venue fit, acceptance likelihood, or evidence rank
- **Transport limits**: explicit-selection offline runtime only; no default workflow integration or manuscript-based profile inference ships; the preregistered usability protocol has not run with human participants
- **Maximum licensed claim**: Closed schemas, canonical-content validation, a field-general fallback, and append-only correction receipts exist; no usability or research-outcome claim.
- **Next required evaluation**: complete the section 8-A pre-recruitment amendment, then run the frozen paired human-participant protocol separately by family and experience stratum (#742)

### rq_formation.inquiry_branch_ledger

- **Mechanism**: opt-in inquiry_branch_ledger @ inquiry-branch-ledger/1.0 (#743): event-sourced branch origin labels, author disposition, profile-bound live-budget replay, and a compact Stage 1 design-freeze summary
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/inquiry_branch_ledger.py::replay_ledger; scripts/test_inquiry_branch_ledger.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: the ledger preserves recorded alternatives and recovery state; it does not establish novelty, correctness, usefulness, or research value; the simple path remains unchanged: the feature is opt-in and does not materialize state or show a summary with fewer than two recorded branches
- **Transport limits**: opt-in alpha behind ARS_INQUIRY_LEDGER=1; author events are within-session attestations, not authenticated identity; no paired usability or research-family evaluation has run
- **Maximum licensed claim**: An opt-in, profile-bound ledger can preserve and replay recorded alternatives and their disposition history; no novelty, correctness, value, or usability claim.
- **Next required evaluation**: run the #742 section 8 paired protocol for breadth, wrong-turn recovery, burden, time, and abandonment, stratified by family and experience (#743/#659)

## `retrieval`

### retrieval.citation_existence_gate

- **Mechanism**: Deterministic four-index citation-existence verification gate (v3.11, #182): Semantic Scholar + OpenAlex + Crossref + arXiv, per-citation lookup_verified status, opt-in terminal policy
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/test_transport_fixture_citation_gate.py; scripts/check_v3_9_0_triangulation.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: existence-only: verifying that a citation resolves does not verify that it supports the claim citing it; the gold citation_extraction harness pins the reducer's own classification, not an independent ground truth of hallucination catch rate
- **Transport limits**: resolver coverage varies by field and language; legitimately-unindexed work stays unresolvable by design (precision-over-recall)
- **Claim anchors**: README.md — "deterministic citation-existence verification gate"
- **Maximum licensed claim**: A deterministic lookup gate exists and its classification logic is CI-pinned; no measured hallucinated-citation catch rate is claimed.
- **Next required evaluation**: an independently-authored ground-truth set (not derived from the reducer) measuring end-to-end catch and false-block rates

### retrieval.claim_standing_probe

- **Mechanism**: Claim-standing probe (#655): consent-gated, advisory-only retrieval of candidate evidence for one high-impact claim with stance classification substrate
- **Mechanism status**: PARTIAL / deterministic conformance: CI_GATED (pinned by scripts/check_claim_standing_candidate_ledger_integration.py)
- **Behavioral evidence**: DESIGNED
- **External/human outcome evidence**: none
- **Known exclusions**: STANCE CLASSIFICATION UNMEASURED: no live stance provider, expert labels, or baseline row exists; advisory-only: never part of Phase E verification or the integrity result
- **Transport limits**: no live index, model, or judge has run through the probe path
- **Maximum licensed claim**: A contained, consent-gated probe substrate with deterministic gates exists; no accuracy, usefulness, or coverage claim.
- **Next required evaluation**: live stance-provider adapter + expert ground truth + the #655 baseline measurement row under the heldout-measurement contract

## `methodology`

### methodology.blueprint

- **Mechanism**: research_architect_agent methodology blueprint (paradigm, method, data strategy) with blind design-freeze disagreement checkpoint (#518)
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_cross_model_handoff_contract.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: no evaluation measures blueprint quality, method-fit, or downstream effect of the blind checkpoint
- **Transport limits**: prompt-contract layer; behavior varies with the session model
- **Maximum licensed claim**: A structured blueprint contract and a blind cross-model disagreement checkpoint exist; no methodology-quality claim.
- **Next required evaluation**: matched stage-substitution comparison on identical upstream artifacts (#745 evaluation program)

## `synthesis`

### synthesis.cross_source

- **Mechanism**: synthesis_agent cross-source integration with v3.6.7 pattern protection and cross-paper tension inventory (#262)
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_v3_6_7_pattern_protection.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: cross-paper contradiction inventory carries a mandatory recall-limitation coverage note: assessed pairs only; no evaluation measures synthesis faithfulness or contradiction-detection recall
- **Transport limits**: prompt-contract layer; behavior varies with the session model
- **Maximum licensed claim**: Pattern-protection contracts and an enumerable tension inventory exist; no synthesis-quality or recall claim.
- **Next required evaluation**: seeded-contradiction detection eval over a synthetic corpus with known ground truth

## `drafting`

### drafting.citation_emission

- **Mechanism**: Three-layer citation emission (v3.7.3) + anti-leakage protocol: ref markers, typed locator anchors, session-material precedence
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_v3_7_3_three_layer_citation.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: locator presence is enforced deterministically; locator correctness (does the page/quote support the claim) is checked at Phase E, not at emission
- **Transport limits**: prompt-contract layer; behavior varies with the session model
- **Maximum licensed claim**: Deterministic emission-format gates exist; no measured claim about drafting quality or anchor accuracy.
- **Next required evaluation**: anchor-accuracy audit on a real pipeline run's draft (locator resolves and supports the sentence citing it)

## `integrity_check`

### integrity_check.claim_verification

- **Mechanism**: Phase E claim verification with schema-valid Claim Registry, risk-stratified selection (#549), byte-bound coverage replay (#737), and evidence-row persistence (#656)
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/test_claim_registry_coverage.py; scripts/test_claim_verification_coverage_contract.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: semantic extraction completeness is unknown by contract: the coverage diff detects only two mechanically detectable candidate classes; no evaluation measures how often Phase E catches a genuinely unsupported claim
- **Transport limits**: verification judgment is model-mediated; deterministic layers pin format and replay, not truth
- **Maximum licensed claim**: Registered claims are verified under a replayable deterministic envelope; the registry's semantic completeness and the checker's catch rate are unmeasured.
- **Next required evaluation**: seeded unsupported-claim detection eval (planted claim-source mismatches with known ground truth)

### integrity_check.tortured_phrase_screen

- **Mechanism**: Deterministic tortured-phrase screening runtime (#660): Cabanac-anchored pattern grammar over own-draft and cited-source text
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_tortured_phrase_screening_integration.py)
- **Behavioral evidence**: MEASURED — mechanical conformance 190/190 tests passed (rate 1.0) at the frozen commit; contextual validity and real-world FP/FN remain unmeasured (evals/heldout/tortured_phrase_conformance; model none (deterministic runtime; judge_plan.exception mechanical_suite); population repository-owned synthetic expected-match corpus; 2026-08-10) — report: evals/heldout/tortured_phrase_conformance/measurement-2026-08-10.json
- **External/human outcome evidence**: none
- **Known exclusions**: cannot certify clean text or infer paper-mill origin, AI origin, misconduct, contamination, or quality; no real manuscripts and no native PPS importer were involved
- **Transport limits**: synthetic conformance only; single frozen run at one commit
- **Maximum licensed claim**: The deterministic screen conforms to its own synthetic expected-match grammar (190/190); real-world false-positive/negative performance is unmeasured.
- **Next required evaluation**: real-corpus FP/FN measurement against independently labeled tortured-phrase instances

### integrity_check.inquiry_branch_ledger

- **Mechanism**: opt-in inquiry_branch_ledger @ inquiry-branch-ledger/1.0 (#743): first-degree stale-cause replay and compact summaries at the Stage 2.5 and Stage 4.5 mandatory checkpoints
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/inquiry_branch_ledger.py::replay_ledger; scripts/test_inquiry_branch_ledger.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: invalidation is first-degree over author-recorded downstream references; no transitive artifact-dependency claim; a stale mark never rewrites, deletes, regenerates, or judges an artifact
- **Transport limits**: opt-in alpha behind ARS_INQUIRY_LEDGER=1; checkpoint summaries are deterministic views over caller-supplied, digest-bound state; no paired usability or research-family evaluation has run
- **Maximum licensed claim**: Recorded first-degree dependencies can be marked visibly stale and resolved without silent mutation; no completeness, correctness, or usability claim.
- **Next required evaluation**: run the #742 section 8 paired protocol for recovery, burden, time, abandonment, and family fit before any promotion beyond opt-in (#743)

## `review`

### review.seeded_defect_panel

- **Mechanism**: Reviewer panel on seeded-defect manuscripts (#574/#608/#610/#644 line): isolated per-seat dispatch, arithmetic receipts, recompute gate
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_panel_synthesis.py)
- **Behavioral evidence**: MIXED — post-#644 row: defect recall 1.00/1.00 both replicates, receipt-backed recompute recall 4/4 both replicates, clean-control false findings 0; severity agreement 0.607 vs 0.672 baseline - a frozen-measured REGRESSION, so the full gate set does not clear (evals/heldout/reviewer_seeded_defects; model claude-opus-5 (effort xhigh, isolated per-seat dispatch); population 2 seeded-defect manuscripts + 1 clean control, maintainer-adjudicated (directional smoke tier); 2026-08-06)
- **External/human outcome evidence**: none
- **Known exclusions**: directional smoke tier, not a calibration set: n=2 defective manuscripts, maintainer adjudication, no distributional FNR/FPR claim; seat-level severity-band anchoring residual open (#574 B1, #648)
- **Transport limits**: single model family and dispatch harness; numbers are commit-frozen and re-measured per change
- **Maximum licensed claim**: On the recorded seeded-defect tier, recall and clean-control behavior pass and severity agreement currently fails its frozen gate; no calibration or field-general review-quality claim.
- **Next required evaluation**: severity-band anchoring decision (#648) and the first reviewer calibration run (#653)

### review.calibration

- **Mechanism**: Reviewer calibration mode (v3.2 protocol + #653 public-corpus manifest instruments): FNR/FPR/balanced-accuracy against ground-truth-bearing public reviews
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_calibration_tiers.py; scripts/test_check_calibration_tiers.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: the calibration protocol has never been executed: no gold-corpus run exists in the repo; LLM-as-judge leniency direction documented (FARS anchor) but unquantified for ARS
- **Transport limits**: first run blocked on external corpus access (OpenReview account approval)
- **Maximum licensed claim**: A calibration protocol and reproducible corpus manifest exist; no error-profile numbers exist yet.
- **Next required evaluation**: #653 first measured error profile on the public-corpus manifest

## `revision`

### revision.claim_drift_guard

- **Mechanism**: Revision claim-drift guard text (#569/#570 line): a guard block condensed from the shipped draft_writer_agent revision-mode ladder rules plus a token-conservation line, measured in-window (#652); the shipped pipeline wiring and the deterministic check_revision_token_conservation.py checker are the production carriers
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/test_check_revision_token_conservation.py)
- **Behavioral evidence**: MEASURED — guarded arm claim-strength/hedge drift 1/16 item-replicates vs 7/16 unguarded in-window; unauthorized numeric/citation drift 0/16 guarded; drift not eliminated; the row measures the condensed guard-block prompt, not the shipped pipeline path, and baseline-vs-post comparison is descriptive only (no causal claim) (evals/heldout/revision_claim_drift; model claude-fable-5 subject; codex gpt-5.6-sol judge; population 8-item revision set (6 pressure items + 2 clean controls), en; 2026-08-07) — report: evals/heldout/revision_claim_drift/measurement-2026-08-07.json
- **External/human outcome evidence**: none
- **Known exclusions**: single replicate baseline retained no raw prompts; cross-row comparison is descriptive; prospective subject-context-isolation protocol (#679) designed, not run
- **Transport limits**: one subject model, one judge model, en-only pressure set
- **Claim anchors**: README.md — "a deterministic numeric/citation token-conservation checker"
- **Maximum licensed claim**: In the recorded window, the condensed guard-block prompt showed 1/16 drift against 7/16 unguarded; no claim transfers to the shipped pipeline wiring as-wired, and no causal or cross-model claim is made.
- **Next required evaluation**: #679 subject-context-isolation re-run producing a causally interpretable comparison row

## `finalization`

### finalization.format_and_disclosure

- **Mechanism**: Formatter stamp-only hard gates (refusal rules, pass-through allowlists), disclosure mode, and Stage 5/6 boundary semantics with content locks (#528)
- **Mechanism status**: IMPLEMENTED / deterministic conformance: CI_GATED (pinned by scripts/check_pipeline_boundary_semantics.py)
- **Behavioral evidence**: NOT_RUN
- **External/human outcome evidence**: none
- **Known exclusions**: no evaluation measures formatter refusal correctness under adversarial or malformed inputs beyond the pinned lint fixtures
- **Transport limits**: prompt-contract refusal layer; deterministic locks pin the protocol text, not the runtime behavior
- **Maximum licensed claim**: Deterministic boundary-semantics locks and stamp-only gate contracts exist; no behavioral refusal-correctness measurement.
- **Next required evaluation**: include finalization refusal surfaces in a pipeline_behavior_robustness run
