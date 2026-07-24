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
   severity_scores, clean_control_false_findings: [...concepts...], notes}`, so
   every baseline is auditable and re-adjudicable — the summary table below is
   derived from these records, never the only artifact.

**Acceptance gates for a reviewer-prompt change** (all three, on replicate means):
mean strict recall does not regress (overall AND within the `critical` band);
mean clean-control false-finding count does not increase; mean severity-agreement
score does not regress. "Stricter" alone is not an improvement (#574 rescope,
product outcome).

## Baseline

| Date | Commit | Model | Runs | MS01 recall (strict) | MS02 recall (strict) | Clean-control false findings | Severity agreement | Notes |
|------|--------|-------|------|----------------------|----------------------|------------------------------|--------------------|-------|
| pending | — | — | — | — | — | — | — | Baseline runs happen in fresh sessions on `main` BEFORE the #574 behavior batch lands; re-run, don't reuse, after model upgrades |

## Integrity checking

`scripts/check_seeded_defect_fixtures.py` validates structure only (manifest schema,
closed enums, defect-count agreement, every `anchor_quote` present verbatim exactly
once in its manuscript, clean control free of manifest references). It is a fixture
integrity gate, NOT a behavioral measurer — `run_evals` has no native task for this
set; the behavioral measurement is the manual protocol above.
