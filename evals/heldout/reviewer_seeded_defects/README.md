# Reviewer Seeded-Defect Set (#574 E4, v0.1)

Held-out acceptance instrument for reviewer-prompt changes: synthetic manuscripts with
planted, ground-truthed quality defects plus a clean control, so that any change to the
review stage's prompts (the #574 behavior batch first — quota removal, typed evidence
anchors, severity transport, register/severity separation) is measured against a
baseline instead of shipped on intuition. Same discipline as
`evals/heldout/revision_claim_drift/` (#569/#570): measure the CURRENT model first,
then change the prompt, then measure again.

## Epistemic status

This is a **directional smoke tier, not a calibration set** (the #574 rescope's scaled
form of the E5 decision). n = 2 defective manuscripts (19 seeded defects) + 1 clean
control, labels adjudicated by the maintainer, not a blinded expert panel. It supports
"recall did not regress / clean-paper false findings did not increase" statements about
a specific model + prompt pair; it makes NO distributional FNR/FPR claim. Scope per
repo convention: state what was measured, nothing more.

## Contents

| Fixture | File | Ground truth |
|---------|------|--------------|
| MS01 — quantitative (educational technology, cross-sectional survey + LMS logs) | `manuscripts/ms01_quant_defective.md` | `manifests/ms01_quant.defects.json` (10 defects) |
| MS02 — qualitative/mixed (higher-education policy, interviews + small survey) | `manuscripts/ms02_qual_defective.md` | `manifests/ms02_qual.defects.json` (9 defects) |
| MS00 — clean control (educational technology survey, deliberately sound at its scale) | `manuscripts/ms00_clean_control.md` | none — zero planted defects; findings against it are scored per protocol step 5 (only factually-false assertions count as false findings) |

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs. Defect classes: `statistical`, `inference`,
`citation_claim_mismatch`, `methods`, `ethics`, `internal_consistency`, `overclaim`,
`qual_rigor`. Each manifest row carries a verbatim `anchor_quote` (unique in its
manuscript) so adjudication is anchored, not vibes.

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
   Editorial Decision Letter) under `runs/raw/<same-stem>.review.md` — verdicts
   without the underlying reports are not re-adjudicable (DETECTED/PARTIAL
   reclassification, severity recomputation, and clean-control zero-false-finding
   verification all need the full text). The summary table below is derived from
   these records, never the only artifact.

**Acceptance gates for a reviewer-prompt change** (all three, on replicate means):
mean strict recall does not regress (overall AND within the `critical` band);
mean clean-control false-finding count does not increase; mean severity-agreement
score does not regress. "Stricter" alone is not an improvement (#574 rescope,
product outcome).

## Baseline

| Date | Commit | Model | Runs | MS01 recall (strict) | MS02 recall (strict) | Clean-control false findings | Severity agreement | Notes |
|------|--------|-------|------|----------------------|----------------------|------------------------------|--------------------|-------|
| 2026-07-24 | 307ef24 | claude-opus-4-8 (reasoning effort xhigh; isolated per-seat two-phase dispatch per the frozen dispatch shape) | 2 per fixture (6) | **0.90** (9/10 both replicates; critical band 0.75 — SD-01 GRIM = PARTIAL in both, the only non-detection across all MS01 runs in both dispatch designs) | **1.00** (9/9 both replicates; critical band 1.00 — both panels explicitly name the absent interview protocol) | **0** (both replicates; decisions Minor Revision / "Major Revision gated on citation verification" — the latter driven entirely by the excluded-by-design synthetic-DOI class, see run notes) | **0.611** (per-run 0.667 / 0.667 / 0.611 / 0.500) | Recall losses are recompute-class only (GRIM); severity-agreement losses are DA band placement — the same defects swing a full band across replicates and seats (#574 A3/A4/B1 targets). Two protocol events, both recovered per protocol: one PANEL-SHRUNK abort (DA multi-dissent, §5 retry) and one voided-and-retried synthesis (§8.1 duplicate emission pair, voided output preserved in `runs/raw/voided/`). Records in `runs/2026-07-24-*.json` + `runs/raw/`; the superseded single-context attempt (near-identical numbers — the leak did not inflate recall) in `runs/superseded/` |
| pending (post-change) | — | — | — | — | — | — | — | Re-measure after the #574 behavior batch (A1/A2/A3/B1); re-run, don't reuse, after model upgrades |

## Integrity checking

`scripts/check_seeded_defect_fixtures.py` validates structure only (manifest schema,
closed enums, defect-count agreement, every `anchor_quote` present verbatim exactly
once in its manuscript, clean control free of manifest references). It is a fixture
integrity gate, NOT a behavioral measurer — `run_evals` has no native task for this
set; the behavioral measurement is the manual protocol above.
