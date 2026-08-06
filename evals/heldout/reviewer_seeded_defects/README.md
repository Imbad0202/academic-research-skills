# Reviewer Seeded-Defect Set (#574 E4 / #610, v0.2 prospective)

Held-out acceptance instrument for reviewer-prompt changes: synthetic manuscripts with
planted, ground-truthed quality defects plus a clean control, so that any change to the
review stage's prompts (the #574 behavior batch first — quota removal, typed evidence
anchors, severity transport, register/severity separation) is measured against a
baseline instead of shipped on intuition. Same discipline as
`evals/heldout/revision_claim_drift/` (#569/#570): measure the CURRENT model first,
then change the prompt, then measure again.

**Version boundary:** v0.2 is the prospective #610 measurement foundation. It
adds one GRIMMER case and a checked statistical-procedure projection before a
new baseline is collected. Every committed 2026-07-24/25/27 run below remains a
v0.1 artifact tied to its historical `suite_commit`; no historical denominator,
verdict, or table value is retroactively recomputed.

## Epistemic status

This is a **directional smoke tier, not a calibration set** (the #574 rescope's scaled
form of the E5 decision). n = 2 defective manuscripts (20 seeded defects) + 1 clean
control, labels adjudicated by the maintainer, not a blinded expert panel. It supports
"recall did not regress / clean-paper false findings did not increase" statements about
a specific model + prompt pair; it makes NO distributional FNR/FPR claim. Scope per
repo convention: state what was measured, nothing more.

## Contents

| Fixture | File | Ground truth |
|---------|------|--------------|
| MS01 — quantitative (educational technology, cross-sectional survey + LMS logs) | `manuscripts/ms01_quant_defective.md` | `manifests/ms01_quant.defects.json` (11 defects; v0.2 adds prospective GRIMMER SD-11) |
| MS02 — qualitative/mixed (higher-education policy, interviews + small survey) | `manuscripts/ms02_qual_defective.md` | `manifests/ms02_qual.defects.json` (9 defects) |
| MS00 — clean control (educational technology survey, deliberately sound at its scale) | `manuscripts/ms00_clean_control.md` | none — zero planted defects; findings against it are scored per protocol step 5 (only factually-false assertions count as false findings) |

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs. Defect classes: `statistical`, `inference`,
`citation_claim_mismatch`, `methods`, `ethics`, `internal_consistency`, `overclaim`,
`qual_rigor`. Each manifest row carries a verbatim `anchor_quote` (unique in its
manuscript) so adjudication is anchored, not vibes.

### #610 statistical projection (v0.2)

Every `statistical` row carries a closed `statistical_kind`. The #610
recomputation denominator is exactly MS01 SD-01 `grim`, SD-02 `n_from_df`,
SD-03 `p_from_test_statistic`, and SD-11 `grimmer`. MS02 SD-07 is
`reporting_only`: it tests whether an unsupported significance claim is noticed,
not whether arithmetic is recomputed, so it appears only in class-wide
statistical recall. The checker pins this mapping and independently exhausts the
small integer-scale state space behind SD-11; a coordinated relabel, deletion,
or reachable replacement SD fails CI.

The architecture decision, arithmetic-receipt shape, undecidable boundaries,
and cohort order are frozen in
`docs/design/2026-08-02-610-statistical-recompute-baseline-spec.md`.

## Measurement protocol

1. **Blinded, isolated run per manuscript.** Copy the single manuscript to a
   NEUTRAL filename (`manuscript.md`) in an empty directory OUTSIDE this
   repository checkout, and run `academic-paper-reviewer` full mode there in a
   fresh session. The checked-in filenames (`_defective`, `_clean_control`) and
   this directory's name leak the condition; a repo-enabled session can also read
   the sibling manifests. The `manifests/` files are held-out ground truth — they
   must NEVER enter a review session's context (contamination voids the run).
   **Dispatch shape (frozen 2026-07-24):** full mode must be executed with the
   sprint contract's physically separated calls (`sprint_contract_protocol.md`
   §2) — each seat's Phase 1 produced by a clean, paper-blind call receiving only
   the contract + title/field/word_count, Phase 2 by a separate paper-visible
   call, structural §§4-5 lints enforced at dispatch. Single-context whole-panel
   simulation observably leaks manuscript content into the "blind" Phase 1
   (see `runs/superseded/2026-07-24-in-context-dispatch/`) and is NOT the
   measured condition; post-change runs must use the same isolated dispatch.
   **Isolation mechanism note:** once a baseline exists, any orchestrating
   session is manifest-aware by construction, so contamination isolation rests
   on the dispatch fence — review/synthesis agents receive only the
   neutral-named manuscript path, the reviewer skill files, the contract, and
   prior-phase outputs as delimited data, with `evals/` reads forbidden and no
   defect-related vocabulary in any prompt — never on orchestrator ignorance.
   Record the fence in the run records.
2. **Replicates.** At least **2 independent runs per manuscript per condition**
   (baseline and post-change). Full-mode output is stochastic; a single run's
   recall moves ~10 points on one defect flip. Report each run; gates use the
   mean across replicates.
3. **Collect** the five reviewer reports + the Editorial Decision Letter.
4. **Adjudicate per seeded defect** (maintainer, against the manifest):
   - `DETECTED` — any seat names the defect substantively (overlaps the anchor or
     an equivalent description of the same flaw);
   - `PARTIAL` — the symptom is noticed but misdiagnosed;
   - `MISSED` — no seat surfaces it.
   **Recall is strict**: numerator counts `DETECTED` only (`PARTIAL` contributes
   0 and is reported separately). Severity agreement is scored over `DETECTED`
   defects using the highest-severity assessment among the seats that detected
   it: exact band = 1, adjacent band = 0.5, further = 0, averaged.
   **Severity-source ladder (frozen 2026-07-24, applies identically to baseline
   and post-change runs):** a seat's severity is its explicit per-finding tag
   (the DA always carries one; other seats only when their report happens to tag
   the finding — pre-A3 they usually don't). When NO detecting seat carries an
   explicit tag, fall back to the Editorial Decision Letter's severity for the
   matching roadmap item (`Critical`/`Major` words; where a letter gives only
   priorities, P1 → major, P2/P3 → minor), and record the fallback in the run
   record. Rationale: before the #574 A3 change the non-DA seats emit no
   per-finding severity, so the "highest among detecting seats" rule is not
   fully computable from seat output alone; the ladder is the deterministic
   proxy that keeps baseline and post-change severity numbers comparable —
   post-change runs MUST use the same ladder (a post-A3 run will simply hit the
   fallback rung less often, which is itself part of what A3 is buying).
5. **Clean control — what counts as a false finding.** Count only findings that
   assert a defect that is FACTUALLY NOT PRESENT (fabricated flaw, invented
   inconsistency, mis-recomputed statistic). Deduplicate by defect concept
   across seats and the letter: the same false flaw claimed by three seats and
   repeated in the letter counts ONCE. Explicitly NOT false findings:
   style/preference suggestions, hedged "consider…" advice, and **true
   observations about genuine absences** (the control is sound at its scale,
   not perfect — a correct observation is a legitimate finding, never a false
   positive, and also not a seeded-defect detection).
   **Scoring exclusion:** citation-existence complaints about the synthetic
   references (`10.5555/…` reserved-prefix DOIs, fictional authors) are
   excluded from all counts by design — the reviewer is right that they don't
   resolve, but citation existence is the v3.11 gate's jurisdiction, not this
   set's measurand, and the fixtures cannot carry real citations.
6. **Record per run** (committed): write `runs/<date>-<fixture>-<baseline|post>-r<k>.json`
   with `{model_id, suite_commit, date, condition, per_defect: {SD-xx: verdict},
   severity_scores, clean_control_false_findings: [...concepts...], notes}`, AND
   commit the run's complete raw panel output (all reviewer reports + the
   Editorial Decision Letter) under `runs/raw/<same-stem>.review.md` for a
   hand-dispatched run, or as the bundle directory `runs/raw/<same-stem>/`
   for a harness-dispatched run (see § Dispatch harness) — verdicts
   without the underlying reports are not re-adjudicable (DETECTED/PARTIAL
   reclassification, severity recomputation, and clean-control zero-false-finding
   verification all need the full text). The summary table below is derived from
   these records, never the only artifact. Under
   `reviewer-e4/2026-07-27`, also commit every model response that a checker
   rejected before a retry plus that checker's output. A re-dispatch after a
   transport, quota, or session failure that produced no model response has no
   rejected response or checker output to preserve; disclose the no-response
   event in `notes`, but it is not a retry-evidence violation.

   Every normal or blocked record governed by this contract MUST carry
   `"evidence_contract": "reviewer-e4/2026-07-27"` (or a named later contract
   that retains at least the same retry-evidence requirement), plus these
   closed machine fields: `measurement_status` is `completed` or `blocked`;
   `provenance_status` is `valid` or
   `invalid_incomplete_retry_evidence`; `panel_completion_status` is
   `completed` or `aborted`; and `score_eligible` is Boolean. A normal scored
   record uses `completed` / `valid` / `completed` / `true`; every blocked
   record uses `measurement_status: blocked` and `score_eligible: false` while
   the other two fields state its independent provenance and completion facts.
   `provenance_status` is scoped only to retry-evidence completeness under the
   named evidence contract: `valid` does not attest contamination isolation,
   dispatch blindness, panel completeness, or any other provenance axis.
   The `invalid_incomplete_retry_evidence` downgrade is also the emitter's
   terminal fallback when ANY named location still fails to resolve at
   emission time (a terminal abort artifact is rewritten once from its own
   diagnostic before this fallback fires), so a downgraded record means
   "some named evidence location could not be made to resolve", not
   necessarily that a retry occurred.
   The closed
   grandfathered records and every artifact under `runs/superseded/` are frozen
   under their historical status and MUST NOT be backfilled with this contract
   label. A governed record with any retry MUST enumerate every event in its
   stage-specific retry list (for example, `phase1_retries`) and declare
   `rejected_response_preserved` plus `checker_output_preserved`. Whenever
   `rejected_response_preserved` is `true`, the same event MUST name a
   record-relative `rejected_response_location`, and that path MUST resolve.
   Every stored diagnostic, including a terminal abort diagnostic outside a
   retry list, MUST carry `diagnostic_form: "verbatim"` or
   `diagnostic_form: "normalized"` and name a record-relative
   `checker_output_location`; that path MUST resolve.
   `verbatim` is byte-for-byte checker output; `normalized` means absolute
   run-root prefixes were removed — the leading artifact path for checker
   output, and any registered run root wherever it appears for
   harness-assembled diagnostics (an OSError spells its path mid-sentence)
   — with every remaining character verbatim. The named checker-output
   artifact remains authoritative.

   **Blocked-run separation:** if a fail-loud checker stops the panel before all
   five cards and synthesis exist, or any checker-rejected response followed by
   a retry or its checker output is not preserved, do not write a normal
   scored-run record. Preserve the available
   evidence under `runs/raw/blocked/<same-stem>/` and a status record under
   `runs/blocked/<same-stem>.json`. A completed final panel with incomplete retry
   provenance is still invalid for scoring because paper blindness and retry
   eligibility are no longer independently re-adjudicable. Blocked attempts are
   operational evidence, not zero-valued measurements: exclude them from all means,
   do not impute missing responses or seats, and do not launch a replacement draw to
   conceal the abort.

   **Prospective retry-evidence boundary (adopted 2026-07-27):** only the new
   requirement to preserve every checker-rejected response followed by a retry
   and its checker output has a grandfathered exception. Every other
   blocked-run rule above — complete panel requirement, exclusion from means,
   no imputation, and no replacement draw that conceals an abort — applies to
   every attempt regardless of date.
   The exception is a closed artifact set of exactly 18 normal scored records:
   the 6 already committed as `runs/2026-07-24-*.json` and the 12 already
   committed as `runs/2026-07-25-*.json`, together with the accepted final
   panels they reference, remain governed by the earlier collection contract.
   No other pre-adoption abort, raw root, or unregistered attempt may be
   promoted into the scored namespace.

   That earlier contract required the five accepted final reviewer reports plus
   the Editorial Decision Letter. It permitted a multi-dissent restart but did
   not require the rejected response or its checker transcript to be retained.
   This is protocol versioning, not evidence reconstruction: the preserved
   accepted outputs remain re-adjudicable for the recorded recall, severity,
   and false-finding measurands, while the grandfathered rows make no
   independent claim that retry eligibility or the rejected response's paper
   blindness can now be re-adjudicated. Applying a new evidence requirement
   after observing the registered baseline and post-change outcomes would
   itself change the comparison set post hoc. Every non-grandfathered attempt,
   including both conditions after a model upgrade, uses
   `reviewer-e4/2026-07-27` or a named later contract that preserves this
   fail-closed minimum.

   **Contract-sensitivity disclosure:** the 2026-07-24 MS01 baseline r1,
   2026-07-24 MS02 baseline r1, and 2026-07-25 MS02 baseline r1 would not be
   score-eligible if dispatched under `reviewer-e4/2026-07-27`; each remains
   eligible only under its governing earlier contract. The 2026-07-24 MS01
   synthesis retry preserved its checker-rejected model response under
   `runs/raw/voided/`, but not the exact checker output, so it fails the strict
   current artifact pair. Any new or amended citation on or after 2026-07-27 of
   the registered 2026-07-25 gate verdicts MUST carry that non-attestation.
   Pre-adoption historical text is not retroactively rewritten, but quoting or
   reusing it in a current decision triggers the disclosure. Moving an
   Unreleased pre-adoption claim into a numbered release counts as current
   reuse, so the release notes must carry the disclosure before tagging.

   As diagnostics only, omitting both affected 2026-07-24 panels changes that
   row's severity agreement from 0.625 to
   `(0.667 + 0.500) / 2 = 0.584`; omitting the affected 2026-07-25 panel
   changes its baseline severity agreement from 0.663 to
   `(0.650 + 0.611 + 0.722) / 3 = 0.661`, still above the post-change 0.536,
   so the registered severity direction remains a regression. In the 2026-07-24
   counterfactual, MS01 recall remains 0.90 and MS02 recall remains 1.00 on one
   retained replicate each; in the 2026-07-25 counterfactual, MS02 recall
   remains 1.00 on its single retained replicate. Clean controls are
   unaffected, but the two-replicate requirement is broken; neither
   sensitivity is a recomputed formal gate.
   The disclosed no-response transport re-dispatches in the 2026-07-25 post
   records produced no checker-rejected response, so they do not create a
   symmetric missing-artifact exposure.

**Acceptance gates for a reviewer-prompt change** (all three, on replicate means):
mean strict recall does not regress (overall AND within the `critical` band);
mean clean-control false-finding count does not increase; mean severity-agreement
score does not regress. "Stricter" alone is not an improvement (#574 rescope,
product outcome).

**#610 v0.2 extension:** retain all three gates and separately adjudicate each
of the four MS01 recompute cases as `VERIFIED`, `CLAIM_ONLY`, `MISCOMPUTED`, or
`MISSED`. Receipt-backed strict recompute recall is `VERIFIED / 4`: ordinary
`per_defect: DETECTED` credit does not enter this numerator unless the raw output
also supplies the reported inputs, assumptions, derivation, derived value/range,
comparison rule, and correct arithmetic. Baseline prose may satisfy those
logical fields without the not-yet-shipped `AR<n>` wrapper; post output must use
the formal receipt grammar. Record the closed verdict, procedure id, raw evidence
location, field presence, supported-assumption verdict, procedure-application
verdict, arithmetic correctness, and comparison correctness under
`recompute_adjudication`. `MISCOMPUTED` covers an arithmetic error, unsupported
assumption/procedure, or wrong comparison/tolerance; a numerically correct line
with an invalid test identity is not `VERIFIED`.

Also report each procedure separately; class-wide statistical recall including
MS02's reporting-only row; numeric clean-control false findings (especially a
mis-recomputed statistic) separate from narrative false findings; and
conformance-abort rate. The #610 delta cannot pass if receipt-backed recall
regresses or numeric false findings increase, and every computable seeded case
must be `VERIFIED` in each score-eligible post MS01 replicate (receipt coverage
and arithmetic correctness both 1.00). A conspicuous-value claim without its
arithmetic cannot pass. A procedure-specific row is one seeded case, a
directional witness, not a calibrated per-procedure rate.

The v0.2 baseline is the 2026-08-04/05 corrected cohort at the frozen post-#638
SHA 112a869, collected with the #608 harness and adjudicated by the maintainer
(see its run-history row below). Only now may the receipt/prompt behavior
change land, followed by the same-model, same-harness 2 x 3 post fleet.
The `condition` CLI argument is a record label, not a prompt selector: baseline
and post must come from their respective clean checkouts.

## Baseline

The 2026-07-24 and 2026-07-25 table rows are the closed grandfathered set
described above. In particular, the 2026-07-24 row's PANEL-SHRUNK re-dispatch
and synthesis void-and-retry, plus the 2026-07-25 MS02 r1 multi-dissent retry,
were accepted under that earlier contract; neither row claims those recovery
events would be eligible under `reviewer-e4/2026-07-27`.

| Date | Commit | Model | Runs | MS01 recall (strict) | MS02 recall (strict) | Clean-control false findings | Severity agreement | Notes |
|------|--------|-------|------|----------------------|----------------------|------------------------------|--------------------|-------|
| 2026-07-24 | 307ef24 | claude-opus-4-8 (reasoning effort xhigh; isolated per-seat two-phase dispatch per the frozen dispatch shape) | 2 per fixture (6) | **0.90** (9/10 both replicates; critical band 0.75 — SD-01 GRIM = PARTIAL in both, the only non-detection across all MS01 runs in both dispatch designs) | **1.00** (9/9 both replicates; critical band 1.00 — both panels explicitly name the absent interview protocol) | **0** (both replicates; decisions Minor Revision / "Major Revision gated on citation verification" — the latter driven entirely by the excluded-by-design synthetic-DOI class, see run notes) | **0.625** (per-run 0.722 / 0.667 / 0.611 / 0.500) | Recall losses are recompute-class only (GRIM); severity-agreement losses split between DA band placement (dominant; same defects swing a full band across replicates/seats) and three letter-fallback 0.5-losses where no seat carried a tag — both halves of the #574 A3 gap (A4/B1 also evidenced). Two protocol events, both recovered per protocol: one PANEL-SHRUNK abort (DA multi-dissent, §5 retry) and one voided-and-retried synthesis (§8.1 duplicate emission pair, voided output preserved in `runs/raw/voided/`). Records in `runs/2026-07-24-*.json` + `runs/raw/`; the superseded single-context attempt (near-identical numbers — the leak did not inflate recall) in `runs/superseded/` |
| 2026-07-25 | f7d9d07 (prompt state; fixtures v0.1 unchanged) | claude-opus-5 (effort xhigh, thinking enabled; isolated per-seat two-phase headless-CLI dispatch per the frozen dispatch shape) | 2 per fixture (6) | **0.95** (10/10 + 9/10; critical band 0.875 — r1 is the first observed full-GRIM detection across any run of this set (R1 performs the achievability recompute verbatim); r2 = PARTIAL on SD-01, the A4 recompute class) | **1.00** (9/9 both replicates; critical band 1.00) | **4 / 2** (decisions reject_or_major_revision on both clean runs; all six counted findings are narrative-logic fabrications — invented contradictions or facts asserted without textual basis — with no mis-recomputed statistic anywhere; synthetic-DOI class excluded by design) | **0.663** (per-run 0.650 / 0.611 / 0.667 / 0.722; non-DA seats emit zero per-finding tags pre-A3; 4 letter-fallback cells — both MS02 SD-01 severities ride the letter because the seats that substantively detect the missing instrument are untagged and the DA tag covers only the label-contradiction symptom) | Model-upgrade re-measurement: the `opus` dispatch alias moved from claude-opus-4-8 to claude-opus-5 on 2026-07-25, so BOTH conditions were re-measured per this protocol's re-run-don't-reuse rule — this row (not 2026-07-24) is the operative baseline for the #581 acceptance gates. The opus-5 register is markedly harsher than opus-4-8 on the clean control (0 → 4/2 false findings; Minor Revision → reject_or_major_revision), so cross-model rows must never be compared. One §5 multi-dissent recovery (MS02 r1, Perspective seat), accepted under the pre-2026-07-27 evidence contract; its rejected first response was not then a required artifact and is not used to claim retry re-adjudicability. Records in `runs/2026-07-25-*-baseline-r*.json` + `runs/raw/` |
| 2026-07-25 | ad81b2e (#581 behavior batch A1/A2/A3/B1) | claude-opus-5 (same dispatch) | 2 per fixture (6) | **1.00** (10/10 both replicates; critical band 1.00 — SD-01 GRIM detected with the full achievability arithmetic in BOTH replicates, by R1 and the DA independently) | **1.00** (9/9 both replicates; critical band 1.00) | **2 / 1** (mean 1.5 vs baseline 3.0; the baseline's logical-foreclosure / inoculation / recruitment-channel-as-fact fabrications do not recur — the dedup-vs-anonymity invented incompatibility is the one concept surviving in both post replicates (r1 adds one DA mis-absence claim); r1 is the ONLY run of all twelve whose clean-control decision avoided reject_or_major_revision: major_revision, no F1 fired) | **0.536** (per-run 0.600 / 0.600 / 0.500 / 0.444) — a REGRESSION on the frozen highest-tagged-seat ladder | **Gate verdicts vs the 2026-07-25 baseline row**: strict recall PASS (improved, overall and critical band); clean-control false findings PASS (decreased); severity agreement FAIL as frozen-measured. Diagnostic decomposition (recorded, not a gate substitute): DA-only agreement is flat-to-up (0.621 → 0.644; post MS02-r2's 0.75 is the best of all twelve runs), letter-fallback cells drop 4 → 0, and per-finding tag coverage goes 0 → 100% on the non-DA formal registers (A3's transport goal achieved) — the frozen max rule now aggregates four newly-tagged seats whose tag distributions skew critical (one Domain seat tagged 7/7 critical), i.e. the metric can now SEE cross-seat band inflation the baseline could not express. Open residual: seat-level severity-band anchoring (#574 B1 follow-up). Records in `runs/2026-07-25-*-post-r*.json` + `runs/raw/` |
| 2026-07-27 | 19bc872 (Spec A implementation, including terminal DA-contract correction) | claude-opus-5 (effort xhigh, thinking enabled; same isolated per-seat two-phase dispatch) | **BLOCKED:** 2 clean panels launched; r1 reached synthesis but has incomplete retry provenance; r2 has incomplete Phase 1 retry evidence and conformance-aborted; **0 score-eligible runs**; MS01/MS02 not launched | **NOT COMPUTABLE** | **NOT COMPUTABLE** | r1 unscored observation: **1**, panel decision `major_revision`; replicate mean **NOT COMPUTABLE** | **NOT COMPUTABLE** | Formal Spec-A E4 attempt produced no score-eligible run. r1's first malformed methodology Phase 1 response was overwritten by its permitted structural retry, so the completed final panel cannot prove paper blindness or retry eligibility and is namespaced under `runs/blocked/`. r2's first malformed Methodology and Perspective Phase 1 responses were also overwritten; their exact checker diagnostics survive, but the rejected responses do not, so r2 is independently provenance-invalid. Its Perspective Phase 2 then emitted an empty `## Scoring Plan Dissent` section and failed `[DISSENT-GRAMMAR: dissent section must name dimension_id]`; Phase 2 retry is permitted only for multi-dissent, so DA and synthesis were not run. Observed clean-cohort provenance-invalid rate **2/2 = 1.00** and conformance-abort rate **1/2 = 0.50**, the latter versus the Spec-A diagnostic expectation of approximately zero. Required 2 × 3 fleet and all acceptance gates are **BLOCKED / NOT COMPUTABLE**, not pass or fail. No replacement draw, missing-value imputation, or reconstruction of missing retry output was used. |
| pending (corrective iteration) | — | — | — | — | — | — | — | A future full 2 × 3 measurement must start as a new cohort after the conformance-abort cause is corrected; compare with the newest same-model baseline and re-run both conditions after model upgrades |
| 2026-08-03 | b97628f (frozen v0.2 merge SHA; fixtures v0.2) | claude-opus-5 (effort xhigh, thinking enabled; #608-harness isolated per-seat two-phase dispatch via `claude -p --bare`, `--tools ""`, API-key auth) | **3/6 score-eligible** (MS00 r1/r2, MS02 r2); MS01 r1/r2 and MS02 r1 blocked; smoke panel ms00 r99 score-eligible | NOT COMPUTABLE (MS01 has zero score-eligible runs) | NOT COMPUTABLE (single replicate; fleet not score-complete) | not adjudicated (fleet cannot serve as the v0.2 baseline without MS01) | NOT COMPUTABLE | First authorized #610 §7 step-2 attempt. Conformance-abort rate 3/6 = 0.50; provenance valid on all seven panels (the #608 evidence contract held end-to-end). **Every panel that reached synthesis (6/6, smoke included) failed its first attempt with `[SYNTHESIS-PARSE: found 0]`** — the model fenced the four mechanical audit lines; four panels recovered on the plain-text a2 retry, ms02_qual r1 re-fenced and ms01_quant r2 inline-code-wrapped the a2 and aborted. ms01_quant r1 aborted earlier at `domain.phase2` on a self-superseding double Severity declaration (`[FINDING-GRAMMAR]`, panel shrunk 4/5). Root cause and verbatim diagnostics: #637; checker-tolerance fix: #638. Blocked panels are recorded, not replaced. Records in `runs/2026-08-03-*.json` + `runs/blocked/` + `runs/raw/`. |
| 2026-08-04 (+ 2026-08-05 supplementary replicates) | 112a869 (frozen v0.2 corrected-cohort SHA, post-#638; fixtures v0.2) | claude-opus-5 (effort xhigh, thinking enabled; #608-harness isolated per-seat two-phase dispatch via `claude -p --bare`, `--tools ""`, API-key auth) | **7/9 score-eligible** — smoke ms00 r99 + 2 × 3 fleet on 2026-08-04 (eligible: MS00 r1/r2, MS01 r1, MS02 r2; blocked: MS01 r2, MS02 r1), plus two authorized supplementary replicates on 2026-08-05 (MS01 r3, MS02 r3, both eligible) to satisfy the two-replicate rule | **1.00** (11/11 both replicates, prospective SD-11 GRIMMER included; critical band 1.00; receipt-backed strict recompute recall **3/4 (r1) / 2/4 (r3)** — SD-02 `n_from_df` and SD-11 `grimmer` VERIFIED in both replicates; SD-01 `grim` VERIFIED in r1 but MISCOMPUTED in r3 (integer-product argument without the rounding-interval reachability check §5.2 requires); SD-03 `p_from_test_statistic` MISCOMPUTED in both (two-tailed-only comparison where §5.1 requires both tails shown when the paper states none) — content-level detection is unaffected, prose receipts per the baseline provision, recorded under `recompute_adjudication` in both MS01 records) | **1.00** (9/9 both replicates; critical band 1.00) | **0** (all three clean panels — 0 numeric / 0 narrative; decisions major_revision / major_revision, smoke r99 reject) | **0.672** (per-run MS01 r1 0.682 / MS01 r3 0.727 / MS02 r2 0.611 / MS02 r3 0.667) | **This row is the adjudicated #610 v0.2 baseline.** Class-wide statistical recall 5/5 in both replicates (the four MS01 recompute rows plus MS02 SD-07 `reporting_only`). Conformance-abort rate 2/6 = 0.33 (attempt fleet: 0.50). The #637 Markdown-decoration family did not recur: zero `[SYNTHESIS-PARSE: found 0]` events fleet-wide (attempt fleet: 6/6 first-attempt failures); the only two synthesis retries were `[DELIVERABLE-MISSING]` with a2 convergence — the #638 tolerance fix held. Residual aborts are a different, single-seat content-grammar family, both in non-retryable Phase 2 segments (panel shrunk 4/5): MS01 r2 `domain.phase2` `[ANCHOR-INVALID]` (absence anchor missing `<where>`), MS02 r1 `da.phase2` `[DA-MAJOR-PARSE]` (table not outer-piped). Supplementary panels take fresh replicate numbers (r3); blocked panels are recorded, not replaced. Provenance valid on all nine panels. Adjudicated 2026-08-04/05 by the maintainer against the held-out manifests outside any session. Records in `runs/2026-08-04-*.json` + `runs/2026-08-05-*.json` + `runs/blocked/` + `runs/raw/`. |
| 2026-08-05 (+ 2026-08-06 completions) | 305884b (#644 formal `AR<n>` receipt-grammar behavior SHA; fixtures v0.2) | claude-opus-5 (effort xhigh, thinking enabled; #608-harness isolated per-seat two-phase dispatch via `claude -p --bare`, `--tools ""`, API-key auth) | **6/7 score-eligible** — smoke ms00 r99 + 2 × 3 fleet (eligible: MS00 r2, MS01 r1/r2, MS02 r1/r2; MS00 r1 blocked at synthesis dispatch by `[TRANSPORT: exit 1]` with all five seats complete — a transport failure recorded under `runs/blocked/`, not a conformance abort) | **1.00** (11/11 both replicates; critical band 1.00; **receipt-backed strict recompute recall 4/4 in BOTH replicates** — SD-01 `grim`, SD-02 `n_from_df`, SD-03 `p_from_test_statistic`, SD-11 `grimmer` all `VERIFIED` under the mandatory formal `AR<n>` grammar, receipt coverage and arithmetic correctness 1.00 per replicate; baseline was 3/4 / 2/4 on prose receipts) | **1.00** (9/9 both replicates; critical band 1.00) | **0** (both eligible clean panels — 0 numeric / 0 narrative; decisions reject (smoke r99) / major_revision (r2), no worse than the baseline panels') | **0.607** (per-run MS01 r1 0.682 / MS01 r2 0.636 / MS02 r1 0.556 / MS02 r2 0.556) — a REGRESSION as frozen-measured | **First #610 post row (§7 steps 4-5).** Gate verdicts vs the 2026-08-04/05 baseline row: strict recall PASS (1.00 flat, overall and critical band); clean-control false findings PASS (0, unchanged); **#610 recompute gate PASS — every computable seeded case `VERIFIED` in each score-eligible post MS01 replicate; the two adjudicated baseline drop points (SD-03's both-tails display; SD-01's rounding-interval reachability) are now carried in the raw output, and SD-11 carries its required formal reachability fields as well**; severity agreement FAIL as frozen-measured (0.672 → 0.607), so the #610 delta does not clear the full pre-existing gate set. Adjudication-consistency note: first-pass post scoring gave MS01 SD-01 a 1.0 on the same highest-tag-Major evidence the baseline had scored 0.5; the pre-merge cross-review caught the inconsistency and the maintainer re-scored SD-01 to 0.5 in both post replicates before promotion, matching the baseline application of the frozen ladder. Decomposition (recorded, not a gate substitute): MS01 drops 0.705 → 0.659 (its movement is SD-08 and SD-09, one band in one replicate each) and MS02 drops 0.639 → 0.556 (the MS02 movement is one band each on its SD-03/SD-04/SD-08/SD-09 with SD-07 improving one band); the MS02 receipts yield no computable mismatch signal (predominantly `not_computable`), so no direct receipt-verdict linkage is evident, but causal attribution for the severity drop remains unresolved — the pattern is consistent with the open #574 A3/B1 band-scatter residual. Class-wide statistical recall 5/5 both replicates. Conformance-abort rate **0/6 with zero retries fleet-wide** (baseline 2/6) — the mandatory Phase 2 receipt grammar cost no abort rate. The clean condition carries two eligible panels (r99 + r2) against the baseline's three: the smoke panel is a full-shape clean panel under the same dispatch contract (it counted in the baseline row's clean cells too), and the transport-blocked r1 — `[TRANSPORT: exit 1]` at synthesis dispatch with all five seats complete and the severed partial preserved as `synthesis.partial-response.md` — is recorded, not replaced; accepted by the maintainer. Adjudicated 2026-08-06 by the maintainer against the held-out manifests outside any session. Records in `runs/2026-08-05-*.json` + `runs/2026-08-06-*.json` + `runs/blocked/` + `runs/raw/`. |

## Dispatch harness (#608)

`scripts/dispatch_e4_panel.py` launches one panel and makes the evidence
contract structural instead of aspirational. Hand dispatch lost retry
provenance on both panels of the 2026-07-27 fleet because a retry wrote over
the response it was retrying, and that is not a discipline problem: the
preservation step sat at the exact moment the operator was trying to get the
run to proceed.

```
python3 scripts/dispatch_e4_panel.py --fixture ms01_quant --condition post \
    --replicate 1 --date 2026-08-01 --work-dir /tmp/e4-ms01-post-r1
```

**Operational precondition:** the calls run `claude -p --bare`, which skips
CLAUDE.md auto-discovery, hooks, plugins and auto-memory so that no context
outside the allowlist reaches a prompt. `--bare` authenticates strictly through
`ANTHROPIC_API_KEY` (or `apiKeyHelper` via `--settings`); OAuth and keychain are
never read, so export the key before launching a fleet. Before a fleet, run
ONE single-panel smoke test: the `--tools ""` shutoff and the
`--bare` + `--effort xhigh` + `MAX_THINKING_TOKENS` interaction have not been
exercised with a live call, and either failing would fail fleet-wide —
recoverably (blocked records, no evidence loss), but at the cost of the run.

What it changes, and why each is a property rather than a step:

- **A response is written to a path that cannot be overwritten, before any
  checker is allowed to judge it.** Attempts are numbered in the filename
  (`methodology.phase1.a1.md`, `…a2.md`) and the write uses `O_EXCL`, so
  preservation precedes the decision to retry instead of depending on it.
- **Each checker invocation's own bytes are stored** next to the response it
  judged (`…a1.gate.log`). Checkers run from inside the bundle with relative
  paths, so no absolute prefix has to be stripped and every stored diagnostic
  is `verbatim`.
- **Paper-blind and paper-visible calls get separate whitelisted sandboxes.**
  The blind sandbox does not contain the manuscript at all, so blindness is a
  filesystem fact rather than the seat's restraint; hand dispatch put every
  artifact in one directory. `evals/` is outside both, so no call can reach
  the manifests. The CLI's own built-in tools are shut off per call with the
  whitelist spelling (`--tools ""` — the seats' task is pure text and needs
  none), so the fence does not rest on headless permission defaults — the
  checkout is public, and an enabled WebSearch could otherwise retrieve a
  manuscript's held-out siblings with no tool-use audit trail in a text
  response. Under an emptied whitelist a tool added by a later CLI is closed
  by default, the property a deny list can never have; a `--disallowedTools`
  deny list rides behind it as depth only.
- **The contamination fence is a path allowlist, not a word denylist.** The
  harness may read only the contract, the seven agent files, and the three
  manuscripts; a manifest is not readable, and a future held-out artifact is
  not readable by default either — the property a denylist can never have. A
  word denylist was written first and measured to be worse than the failure it
  guarded: `manifest` and `seeded` are ordinary review vocabulary ("Where it
  manifests"; "how far the themes were seeded by the questions") and **5 of
  the 18 committed real panels of this set contain one**, so gating assembled
  prompts on them would abort roughly a quarter of panels after all five cards
  existed, with no replacement draw permitted. Ground-truth tokens appearing in
  model output are now recorded as an advisory `leak_canary_hits` field for the
  maintainer, never as a panel-killing gate: output cannot carry ground truth
  the model was never given, and a true hit is not repaired by aborting.
- **The seat set is derived from the contract**, ordered by the frozen dispatch
  order, with `panel_size` asserted — so a mode or `panel_size` change cannot
  leave the harness dispatching yesterday's panel while both sides of the
  synthesis check agree with each other and disagree with the contract.
- **Only a reviewer-conformance exit is retried.** §11 routes every exit-2
  class (contract, metadata, IO, role binding) to abort-no-retry, and retrying
  one would also file a `phase1_retries` event for something the evidence
  contract does not classify as a retry at all. Retry eligibility for the one
  permitted Phase 2 recovery is read from the checker's own
  `[PROTOCOL-VIOLATION: multi_dissent=true]` line, pinned by the checker's
  tests so a reword fails CI instead of silently killing a fleet.
- **The four closed status fields are derived**, and `provenance_status` is
  derived by checking that each named location still resolves rather than by
  trusting the write path.
- **The work directory mirrors this tree**, so promoting a run is a copy:
  `runs/<stem>.json` beside `runs/raw/<stem>/`, or the blocked namespace for
  an aborted panel, with every `*_location` already record-relative. Nothing
  has to be rewritten at commit time — that rewrite is what previously turned
  a verbatim diagnostic into a paraphrase.
- **Every emission freezes a recovery event ledger before installing the
  record.** `recovery-state.json` stays inside the raw bundle, never enters a
  model sandbox or prompt, and contains no closed status field. It records the
  invocation context, the dispatch/retry/abort event ledger, and a path/type/
  SHA-256 manifest of the preserved bundle. Normal emission and recovery both
  feed that ledger back through the same status derivation and record builder.
- **A completed panel carries `adjudication.status: "pending"`.** The harness
  cannot adjudicate `per_defect` — that needs the held-out manifest, which must
  never enter a session — so the maintainer fills the verdicts before the
  record is committed when the record enters the scored run history. An
  attempt-documentation cohort recorded under the corrective-iteration rule —
  one whose run-history row is marked not adjudicated / NOT COMPUTABLE and
  whose panels are never reused as baseline replicates (the 2026-08-03
  attempt) — commits with the pending status and its explanatory note intact:
  filling verdicts for panels that will never enter baseline/gate scoring
  would blur the boundary between dispatch facts and maintainer
  adjudication.
- **The delivered prompts are dispatched whole where the protocol does not
  narrow them.** §2 names a subsection only for the five seats; the field
  analyst and the synthesizer get their full agent files. Sending the
  synthesizer just its sprint-contract block produced panels with no Editorial
  Decision Letter and no Revision Roadmap while the arithmetic checker still
  passed, which no gate would have caught.
- **A synthesis-layer failure is voided and re-run once** with the checker
  diagnostics appended as delimited data, per §8.1; exit 2 and exit 3 abort
  with no re-run. Aborting on any nonzero blocked valid panels on ordinary
  stochastic formatting.
- **A no-response transport event is durable but is not a retry.** A timeout or
  a missing binary writes its exact bytes and blocks the run, without filing a
  retry event — which is what the contract says a re-dispatch that produced no
  response is.
- **`--date` and `--fixture` are validated before they name anything.** They
  become path components, and one separator relocated the evidence bundle,
  filed a blocked run under the scored namespace, or lost the record entirely.
- **Prompt material may not be reached through a link.** An allowlist over
  names would otherwise authorize whatever a name points at, so one symlink in
  `manuscripts/` could make a manifest readable while the fence still reported
  itself intact.
- **A committed record carries no absolute local path.** Blocked records are
  committed to a public repo, so the `diagnostic` field is stripped rather than
  left to a hand pass at commit time.
- **A work directory inside this repository is refused outright**, with no
  record written, because writing one there is the thing being refused. The
  same applies to an unnameable run: a malformed `--date` or an unknown
  `--fixture` is refused before anything is written, because the record's own
  name is built from them. An
  internal preservation fault produces a blocked record rather than a
  traceback: losing the record is the one failure mode this mechanism cannot
  afford.

Records and bundles land in the work directory, never straight into the repo;
committing them stays a deliberate step.

### #610 step 5: three-call methodology shape (`reviewer-e4/2026-08-06`)

From the step-5 merge SHA onward the harness dispatches the methodology seat
as three calls — Phase 1, a paper-visible **numeric extraction** call, and
Phase 2 — under the successor contract `reviewer-e4/2026-08-06`, which
preserves every `reviewer-e4/2026-07-27` obligation and adds:

- **The extraction call is gated** (`--extraction` stage of
  `scripts/check_phase_conformance.py`: exactly one `## Recompute Extraction`
  section of typed machine lines, or the attestation) **and carries one
  structural retry** of the Phase 1 evidence class, recorded under its own
  `extraction_retries` list with the rejected response and gate log
  preserved.
- **Arithmetic is computed by the harness, not the model.**
  `scripts/recompute_receipts.py` — deterministic, stdlib-only, tested
  against the #610 spec's worked cases — turns the gated extraction into the
  `## Arithmetic Receipts` section (`methodology.receipts.md` +
  `methodology.recompute.log` in the bundle). A calculator refusal of a
  gate-passed extraction is a harness infra fault: the panel blocks
  (exit-2 class), it is never a conformance abort and never retried.
- **The methodology Phase 2 receives the computed receipts** as a
  `<computed_receipts>` block and must reproduce them verbatim, adding only
  the `finding_ref:` linkage lines on mismatch receipts; the
  `--injected-receipts` identity gate fails the seat on any other edit.
  Extraction fidelity — whether the transcribed numbers are the manuscript's
  — remains a maintainer-adjudicated question against the held-out manifest,
  exactly like the attestation's truth.

`condition` remains a record label: a `script_adapter` cohort must be
dispatched from a frozen clean checkout at or after the step-5 merge SHA and
compared against the newest same-model post row, because the measured
condition (dispatch shape + prompt state) differs from both the baseline and
the post rows. Fleet execution stays a separately authorized step.

**Comparability:** the harness changes the dispatched condition relative to
the 2026-07-24/25 hand-dispatched rows — `--bare` removes the operator's
user-level context, each seat receives only its own configuration card,
instructions and data travel as separate system and user halves, blind and
visible calls get separate sandboxes, and the contract is stamped and
validated before call one. Harness-dispatched runs therefore form a new
cohort: never compare them against the hand-dispatched rows above, and
re-measure BOTH conditions under the harness per this protocol's
re-run-don't-reuse rule before reading any gate. One provenance bound is
declared rather than detected: `suite_commit_reproducible` compares the
checkout state before and after the panel, so an edit made DURING a gate
and reverted before the end probe is not caught — prompt material is
snapshotted at dispatch and is immune, but the checkers load from the
repository at each gate, so do not modify the checkout while a panel
runs.

**Emission-failure recovery.** The record install is staged-then-atomic
and rolls the raw bundle back on failure, so a transient filesystem
fault after the panel completes leaves one of two recoverable states,
neither of them silent. (1) Any staged-write or install failure: the
staged temp file is removed, the bundle is rolled back into the work
directory, no record exists, and the identity is NOT consumed — the
evidence is intact at `<work-dir>/bundle`. (2) Rollback failure on top
of (1): the bundle stays under its canonical `runs/raw/<stem>` or
`runs/raw/blocked/<stem>` path with no record beside it; the console
names the fault. In either state, re-emit without a model call:

```bash
python3 scripts/resume_e4_record.py \
  --work-dir /tmp/e4-run \
  --bundle /tmp/e4-run/bundle
```

For state (2), pass that canonical raw-bundle path to `--bundle` instead.
The command accepts no fixture, condition, replicate, status, diagnostic, or
provenance override: it reads them from `recovery-state.json`, verifies the
bundle manifest, the append-only completion/retry/abort journal witnesses, and
the already-preserved checker PASS markers, then calls the original atomic
emission path. It refuses missing, inserted, changed, symlinked, ambiguous,
already-recorded, non-canonical, or internally inconsistent evidence. It is
record re-emission after a completed dispatch/abort only — never continuation
of an interrupted panel, transport retry, checker re-run, or manual
reconstruction. Bundles created before `recovery-state.json` shipped are not
recoverable by this command and fail closed.

**Promotion-time copy check.** After copying the one record and its raw bundle
from a work directory into this set, verify the copy before staging it:

```bash
python3 scripts/check_e4_promotion.py \
  --source-root /tmp/e4-run \
  --destination-root evals/heldout/reviewer_seeded_defects \
  --stem 2026-08-01-ms00_clean-post-r1
```

The checker requires the canonical scored/blocked layout, exactly one record
namespace, a complete and identical relative path/type set, SHA-256 identity
for the record and every raw file, and safe record-relative resolution of
`raw_bundle` plus every `*_location`. It rejects missing, extra, changed,
redirected, symlinked, or unresolved promoted artifacts. It validates only the
copy boundary; it never reinterprets model output, checker verdicts,
adjudication, or closed status fields.

## Integrity checking

`scripts/check_seeded_defect_fixtures.py` validates structure only (manifest schema,
closed enums, defect-count agreement, every `anchor_quote` present verbatim exactly
once in its manuscript, clean control free of manifest references, the exact v0.2
statistical-kind projection, and the prospective GRIMMER oracle). It is a fixture
integrity gate, NOT a behavioral measurer — `run_evals` has no native task for this
set; the behavioral measurement is the manual protocol above.

## Measurement contract (#654)

New scored rows opt into the `heldout-measurement/1.0` envelope
(`evals/heldout/MEASUREMENT_CONTRACT.md`, `suite_class: seeded_manifest_adjudicated`
per `evals/heldout/suite_registry.json`). The E4 machinery in this README — the
`reviewer-e4/*` evidence contract, blocked-run separation, closed record status
fields, replicate discipline, raw-output preservation — remains the normative layer
and is unchanged. The adoption surface is the **cohort roll-up row**: a
`measurement-<date>.json` summary in envelope form whose `raw_outputs.paths`
reference the per-run records under `runs/`; per-run record shapes emitted by
`dispatch_e4_panel.py` do not change. Existing rows are never retrofitted.
