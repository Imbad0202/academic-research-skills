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
| MS00 — clean control (educational technology survey, deliberately sound at its scale) | `manuscripts/ms00_clean_control.md` | none — zero planted defects; every asserted defect-class finding against it is a false positive |

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs. Defect classes: `statistical`, `inference`,
`citation_claim_mismatch`, `methods`, `ethics`, `internal_consistency`, `overclaim`,
`qual_rigor`. Each manifest row carries a verbatim `anchor_quote` (unique in its
manuscript) so adjudication is anchored, not vibes.

## Measurement protocol

1. **Fresh session per manuscript.** Run `academic-paper-reviewer` full mode on the
   manuscript alone. The `manifests/` files are held-out ground truth — they must
   NEVER enter a review session's context (contamination voids the run).
2. **Collect** the five reviewer reports + the Editorial Decision Letter.
3. **Adjudicate per seeded defect** (maintainer, against the manifest):
   - `DETECTED` — any seat names the defect substantively (overlaps the anchor or
     an equivalent description of the same flaw);
   - `PARTIAL` — the symptom is noticed but misdiagnosed, or severity is off by
     more than one band;
   - `MISSED` — no seat surfaces it.
4. **Clean control:** count findings that assert a concrete defect that is not there
   (fabricated flaw, invented inconsistency, hallucinated statistical error).
   Style/preference suggestions and hedged "consider…" advice do not count.
5. **Record** per run: model id, suite version/commit, date, per-defect verdicts,
   severity agreement for detected defects, clean-control false-finding count.

Primary metrics: seeded-defect recall (overall and by expected_severity),
clean-control false-finding count, severity agreement. A prompt change is acceptable
when recall does not regress AND clean-control false findings do not increase —
"stricter" alone is not an improvement (#574 rescope, product outcome).

## Baseline

| Date | Commit | Model | MS01 recall | MS02 recall | Clean-control false findings | Notes |
|------|--------|-------|-------------|-------------|------------------------------|-------|
| pending | — | — | — | — | — | Baseline run happens in a fresh session on `main` BEFORE the #574 behavior batch lands; re-run, don't reuse, after model upgrades |

## Integrity checking

`scripts/check_seeded_defect_fixtures.py` validates structure only (manifest schema,
closed enums, defect-count agreement, every `anchor_quote` present verbatim exactly
once in its manuscript, clean control free of manifest references). It is a fixture
integrity gate, NOT a behavioral measurer — `run_evals` has no native task for this
set; the behavioral measurement is the manual protocol above.
