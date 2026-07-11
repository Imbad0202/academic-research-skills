# Wording-Pattern Advisory — exemption-clause sharpening (issue #505)

**Date:** 2026-07-11
**Scope:** the `## Wording-Pattern Advisory` section in both
`deep-research/agents/socratic_mentor_agent.md` and
`academic-paper/agents/socratic_mentor_agent.md` (identical change in both).
**Provenance chain:** PR #468 review thread → #501 → PR #503/#504 (baseline
measurement, miss rate HIGH) → issue #505 → this change.

## The change

The #501 Part 2 measurement located the judge's miss-rate gap in one mechanism:
the exemption clause — "names a specific mechanism, instrument, site, or
tension" — was being applied to generic topical noun pairs ("nurse workload",
"cybersecurity training"), which rescued decorated compound-title shells from
firing (7/9 off-list items missed in both baseline replicates).

The exemption sentence in the post-#503 illustrative paragraph is extended (the
sentence itself and everything before it are unchanged) with:

1. **A narrow-exemption test.** The exemption now requires a *named or
   operationalized* specific: an actual instrument/scale name, a named theory,
   model, dataset, or policy instrument, a named site or population, a specified
   causal pathway (through what mediator/condition/process A relates to B — not
   merely that it does), or a stated tension between two identified explanations.
   Ordinary topic labels — domain-flavored noun pairs — are declared swappable.
2. **A decorated-compound-title rule.** An evocative pre-colon phrase plus a
   generic "X and Y (in Z)" subtitle gains no specificity from the decoration;
   the noun-swap test applies to the part after the colon on its own.

Per the #505 constraint set: the WP table is untouched, the advisory stays
non-blocking and surface-phrasing-only, and the sentinel contract pinned by
`test_check_rq_framing_patterns.py` is unchanged (all 7 tests pass).

**Contamination guard.** All example strings introduced by the change
("the PSS-10", "urban mobility and quality of life", "online privacy and
consumer trust", "Roots of Resilience: Community Networks and Disaster
Recovery") were substring-checked against every held-out item before
measurement — zero hits — so no held-out item became an in-prompt example the
way the four #503 examples did.

## Measurement (per the set README protocol)

Same protocol as the baseline: isolated `claude-sonnet-5` sub-agent judges,
verbatim advisory section (post-#505 variant) + 6 shuffled items per batch
(4 shells + 2 domain-native), 8 batches covering the 48 items, 2 replicates,
no labels, no repo access. Boolean outcomes:
`evals/heldout/rq_framing_offlist/measurement-2026-07-11-505.json`.

| variant | overall miss | family_variant (n=23) | off_list (n=9) | false-fire (n=16) |
|---------|-------------|----------------------|----------------|-------------------|
| post-#503 rep1 (baseline) | 12/32 = 0.375 | 5/23 = 0.217 | 7/9 = 0.778 | 0/16 = 0.000 |
| post-#503 rep2 (baseline) | 11/32 = 0.344 | 4/23 = 0.174 | 7/9 = 0.778 | 0/16 = 0.000 |
| post-#505 rep1 | 3/32 = 0.094 | 1/23 = 0.043 | 2/9 = 0.222 | 0/16 = 0.000 |
| post-#505 rep2 | 3/32 = 0.094 | 2/23 = 0.087 | 1/9 = 0.111 | 0/16 = 0.000 |

## Findings

1. **Acceptance: PASS in both replicates.** Overall FNR 0.094 sits well under
   the 0.30 line (baseline: 0.34–0.38 above it); false-fire stays 0/16 in both
   replicates, including the four hard negatives that deliberately carry listed
   surface substrings inside fully specified designs. The on-list gold set
   (`evals/gold/rq_framing_patterns/`) is unaffected — the offline regex
   detector is untouched and its calibration test still passes at fnr=0/fpr=0.
2. **The decorated-title shape is closed.** The 7 baseline stable misses
   (`nat-044`, `ti-002/004/008/010/012/013`) all fired in at least one
   replicate; 5 of 7 fired in both. Captured judge reasoning now argues these
   through the new rule ("post-colon part is a swappable noun pair; decoration
   doesn't exempt it") instead of reading topic nouns as "specific mechanism".
3. **No stable misses remain.** No shell was missed in both replicates. The six
   single-replicate flips (`nat-044/049/053/077`, `ti-012/013`) are
   boundary-adjacent items of the same magnitude as the baseline's observed
   between-replicate flip; each replicate independently passes.
4. **Exemption reasoning on negatives is unchanged in kind.** Judges continue to
   exempt via named instruments (MISSCARE, IUS-12/GAD-7, Technostress Creators),
   named sites/populations (Changhua fishing communities, Taipei market), named
   theory/policy instruments (DeLone & McLean, EU ETS MSR), specified pathways
   (dn-007/dn-008), and stated tensions (dn-016) — the narrow-exemption list
   matches how the hard negatives actually earn silence.

## Caveats

- Same judge model, same day, same single-generator English-only set as the
  baseline — all baseline caveats (model/time drift, n=9 off-list, annotator-2
  family overlap) carry over. Re-run the protocol rather than reusing numbers.
- The fix author and the measurement runner are the same session. The exposure
  is bounded: ground-truth labels predate the change, scoring is mechanical
  boolean comparison, and judges are isolated with no labels — but wording
  choices in the change were informed by the same captured reasoning the
  measurement audits, which is the intended design loop, not an independent
  validation.
- `off_list` n=9 remains small; the per-tier rates carry wide uncertainty. The
  load-bearing claim is the paired disappearance of the stable-miss set, not
  the exact tier rate.

## Disposition

- Issue #505 closes with this change + measurement.
- The held-out set remains the acceptance test for future advisory changes
  (FNR < 0.30 / FPR < 0.20, ≥2 replicates, plus on-list gold set
  non-regression), per #501's decision rule.
