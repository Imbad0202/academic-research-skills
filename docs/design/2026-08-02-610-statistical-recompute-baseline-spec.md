# #610 Statistical Recomputation — Decision and Baseline Specification

Status: **measurement foundation; reviewer behavior unchanged**
Issue: #610 (#574 A4)
Date: 2026-08-02

## 1. Outcome

Adopt a **hybrid, prose-first** architecture:

1. the methodology seat will initially apply bounded prose procedures;
2. every attempted recomputation will emit one machine-parseable arithmetic
   receipt;
3. conformance code will validate receipt shape and finding linkage, but will
   not falsely attest that model arithmetic is deterministic; and
4. a later orchestrator-side calculator may emit the same receipt shape without
   changing the downstream review contract.

This document and fixture v0.2 land **before** any reviewer prompt change. They
freeze what the baseline must measure. No external model fleet is part of this
slice.

## 2. Why prose-first, not script-first

The target is not "trust model arithmetic forever." It is to isolate the first
behavior delta while preserving the current contamination fence.

- `scripts/dispatch_e4_panel.py` runs reviewer calls with `--tools ""`. Giving
  one seat Bash or repository access so it can invoke a calculator would change
  the measured dispatch condition and weaken the held-out fence.
- The repository has no SciPy, NumPy, or statsmodels dependency. A production
  p-value engine would add distribution functions at the same time as a
  manuscript-to-statistic extraction surface, making failures unattributable.
- Existing E4 artifacts show that the methodology seat can sometimes perform
  GRIM, df/N, and t/p checks. The missing mechanism is reliable triggering plus
  an auditable calculation record.
- Script-first still remains the preferred reliability end state. It needs a
  separately reviewed extraction -> calculation -> receipt injection boundary,
  not an implicit tool exception inside the reviewer call.

The stable seam is therefore the receipt, not the calculator implementation.

## 3. What this slice changes — and does not change

This measurement-only slice:

- versions both seeded-defect manifests as v0.2;
- classifies every statistical defect by a closed `statistical_kind`;
- adds one prospective GRIMMER defect to MS01;
- proves that planted SD inconsistency with an independent bounded integer-scale
  oracle in the fixture checker; and
- defines the new-cohort baseline, adjudication, and reporting rules below.

It intentionally does **not** modify:

- `academic-paper-reviewer/agents/methodology_reviewer_agent.md`;
- `academic-paper-reviewer/references/statistical_reporting_standards.md`;
- the canonical sprint prompt, contracts, or phase-conformance grammar; or
- `scripts/dispatch_e4_panel.py`.

Changing any of those before the baseline would erase the pre-#610 condition
that the issue requires.

## 4. Prospective arithmetic receipt contract

The behavior PR that follows the baseline must use this logical record. Its
exact Markdown delimiters belong to that later PR and its grammar tests.

| Field | Contract |
|---|---|
| `receipt_id` | Unique contiguous `AR1..ARn` within the methodology card |
| `procedure_id` | `p_from_test_statistic`, `grim`, `grimmer`, or `n_from_df` |
| `evidence_anchor` | Existing typed anchor grammar; identifies the reported values used |
| `reported_inputs` | Every manuscript value used, including test family, df, N, scale, precision, and tail/SD convention where applicable |
| `assumptions` | Only assumptions licensed by the paper; no silent equal-variance, two-tailed, integer-scale, or sample-SD default |
| `derivation` | The auditable arithmetic or reachability argument |
| `derived_value_or_range` | Derived value, rounding interval, feasible set, or theoretical bound |
| `comparison_rule` | The rounding, inequality, tolerance, or upper-bound rule used |
| `status` | `consistent`, `mismatch`, `not_computable`, or `not_applicable` |
| `not_computable_reason` | Closed reason when status is `not_computable`; absent otherwise |
| `finding_ref` | Required exactly when status is `mismatch`; points to one `W<n>` |

`not_computable_reason` is one of this closed v1 enum (adding a reason is a
versioned contract change):

- `missing_reported_value`
- `test_family_ambiguous`
- `tail_ambiguous`
- `nonstandard_p_procedure`
- `inequality_unresolvable`
- `rounding_rule_ambiguous`
- `rounding_boundary_ambiguous`
- `scale_granularity_unknown`
- `scale_support_unknown`
- `analytic_n_ambiguous`
- `aggregation_or_weighting_unknown`
- `sd_convention_unknown`
- `mean_grim_inconsistent`
- `df_identity_ambiguous`
- `model_correction_or_pooling`
- `reachability_not_completed`

Required invariants:

1. One receipt represents one arithmetic claim. A p mismatch and a df/N
   mismatch cannot share a receipt.
2. Every `mismatch` maps to one weakness, and that weakness maps back to the
   receipt.
3. `consistent`, `not_computable`, and `not_applicable` do not create an
   arithmetic-mismatch finding.
4. A missing report element may still support a separate `absence:` finding;
   it never licenses an invented numeric result.
5. A mismatch without inputs, assumptions, derivation, comparison rule, and a
   typed anchor is non-conforming.
6. Receipt conformance proves auditability, not arithmetic truth. Behavioral
   adjudication still checks whether the arithmetic itself is correct.
7. The formal `AR<n>` wrapper is required only after the behavior PR. A
   baseline free-form derivation may satisfy the same logical receipt fields,
   but it receives no credit merely for naming an impossible-looking value.

## 5. Bounded procedures and worked cases

### 5.1 `p_from_test_statistic`

Prerequisites are a named test family, statistic, required df, reported p, and
tail rule where it matters. F and chi-square are upper-tail tests; t/z results
must not silently become two-tailed.

MS01 example: `t(140) = 1.31, p = .008`. The two-tailed value is approximately
.192 and the one-tailed value approximately .096. The reported .008 is
compatible with neither, so the receipt may be `mismatch` even though the paper
does not state a tail. The receipt must show both comparisons.

Use `not_computable` when a required family/statistic/df is absent; an adjusted,
bootstrap, permutation, or exact p is reported without its procedure; a tail
choice would change the verdict; an inequality cannot be resolved; or rounding
intervals cross the decision boundary.

### 5.2 `grim`

Apply only to an unweighted mean of values with known discrete granularity,
known item-specific analytic N, and a stated precision/rounding rule.

MS01 example: a single 1-5 integer item has `N=87` and `M=3.847`. A value that
rounds to 3.847 at three decimals would require an integer sum within the
corresponding rounding interval. The adjacent sums give `334/87 = 3.839...`
and `335/87 = 3.850...`; neither rounds to 3.847, so the mean is impossible.

Use `not_computable` for continuous, weighted, imputed, transformed, composite,
or item-averaged values unless their exact granularity is known; ambiguous
analytic N; or a rounding/truncation ambiguity that changes reachability.

### 5.3 `grimmer`

GRIMMER inherits every GRIM prerequisite and additionally requires the SD
convention, reported precision, and finite discrete support. A mismatch needs a
completed reachability proof; intuition that an SD "looks too small" is not a
procedure.

Prospective MS01 v0.2 example: a 1-5 integer item has `N=10`, `M=3.00`, and
sample `SD=0.10`. The mean fixes the response sum at 30. If every response is
3, sample SD is 0. Otherwise integer deviations summing to zero require at
least +1 and -1, so the squared-deviation sum is at least 2 and the minimum
nonzero sample SD is `sqrt(2/9) = 0.471...`. No attainable sample SD rounds to
0.10. The fixture checker independently exhausts the bounded response states
and pins this result.

Use `not_computable` when the mean itself is GRIM-inconsistent; sample versus
population SD is unknown; scale support, N, or precision is ambiguous; or the
feasible-value search was not completed.

### 5.4 `n_from_df`

The derivation must name the test-specific identity. Examples include
`df=N-1` for one-sample/paired t and `df=N1+N2-2` for an equal-variance
independent t. The identity is not universal.

MS01 example: the manuscript says the independent-groups analytic sample is at
most 142 but reports `t(156)`. An ordinary two-group t requires total `N=158`;
Welch-Satterthwaite df cannot exceed the ordinary total-df ceiling. All stated
variants therefore exceed the available N, so this is a mismatch.

Use `not_computable` for Welch/Satterthwaite, Kenward-Roger, corrected
repeated-measures, multiple-imputation, mixed/clustered/robust/survey-weighted
analyses unless their required inputs are present; unknown per-test missingness;
or missing group/parameter/pair counts. Chi-square df usually encode table
dimensions and cannot be inverted to N.

## 6. Fixture v0.2 projection

Historical run records remain tied to the v0.1 bytes named by their
`suite_commit`; their denominators and published table values are not rewritten.
All future #610 baseline/post records use v0.2 and must say so in their notes.

| Fixture / defect | `statistical_kind` | #610 recompute denominator |
|---|---|---|
| MS01 SD-01 | `grim` | yes |
| MS01 SD-02 | `n_from_df` | yes |
| MS01 SD-03 | `p_from_test_statistic` | yes |
| MS01 SD-11 | `grimmer` | yes |
| MS02 SD-07 | `reporting_only` | no; class-wide statistical metric only |

The exact projection is a checker invariant. `reporting_only` prevents an
absence-of-test-information defect from inflating recomputation recall.

Primary method references:

- Brown & Heathers (2017), GRIM,
  <https://doi.org/10.1177/1948550616673876>
- Anaya (2016), GRIMMER,
  <https://doi.org/10.7287/peerj.preprints.2400v1>

## 7. New-cohort baseline and post measurement

There is no usable post-Spec-A baseline today. The 2026-07-27 attempt contains
two blocked MS00 post panels, zero score-eligible records, and no MS01/MS02
runs. The #608 harness also changes the dispatch condition relative to the
2026-07-24/25 hand-dispatched rows, so those rows cannot be reused.

After this measurement-only slice is merged:

1. Freeze its clean merge SHA as the v0.2 baseline prompt/fixture state.
2. With explicit model-cost authorization, run one harness smoke panel, then
   two independent baseline replicates for MS00, MS01, and MS02 (2 x 3).
3. Record the exact model ID, clean reproducible suite commit, evidence
   contract, and v0.2 fixture note. Blocked panels remain unscored and are not
   replaced to hide an abort.
4. Only after a score-eligible baseline exists, land the methodology
   prose/receipt behavior PR.
5. Re-run the same 2 x 3 fleet as `post` with the same exact model and dispatch
   shape. A model change requires re-running both conditions.

`condition` is metadata, not a prompt selector: baseline and post must come
from their respective clean checkouts. Never label two runs from one prompt
state as opposite conditions.

### 7.1 Required reporting

Retain every existing E4 gate and additionally report:

- receipt-backed strict recompute recall: `VERIFIED / 4` over MS01
  SD-01/02/03/11, distinct from ordinary seeded-defect DETECTED/PARTIAL recall;
- one row per recompute procedure (one seeded case each; directional, not a
  calibrated rate);
- class-wide statistical recall over the four recompute cases plus MS02 SD-07,
  reported separately and never substituted for recompute recall;
- arithmetic-receipt presence, shape completeness, and arithmetic correctness
  for each seeded recompute case;
- clean-control numeric false findings, especially any mis-recomputed statistic,
  separated from narrative false findings; and
- conformance-abort rate, because a new mandatory Phase 2 grammar can reduce
  score-eligible panels even when the surviving cards look better.

After maintainer adjudication, each score-eligible MS01 run records this closed
projection in `recompute_adjudication`:

| Verdict | Meaning | #610 numerator |
|---|---|---|
| `VERIFIED` | The defect is substantively detected and the raw output contains all logical receipt fields with correct arithmetic and comparison | 1 |
| `CLAIM_ONLY` | The defect is named, but inputs, assumptions, derivation, derived value/range, or comparison is absent | 0 |
| `MISCOMPUTED` | A complete-looking attempt uses incorrect arithmetic, an unsupported assumption/procedure, or an incorrect comparison/tolerance, even if the final suspicion happens to point at the seeded defect | 0 |
| `MISSED` | No substantive detection or recomputation | 0 |

Each row also records `procedure_id`, the raw `evidence_location`, logical
receipt-field presence, `assumptions_supported`, `procedure_application_correct`,
`arithmetic_correct`, and `comparison_correct`. Precedence when both triggers
hold: a receipt that omits a logical field AND rests on an unsupported
assumption or incorrect comparison is `MISCOMPUTED`, not `CLAIM_ONLY` — a
complete-looking attempt is classified by its procedural defect, not by the
gap that defect leaves behind (adjudicated first on the 2026-08-04/05 baseline
cohort's SD-01/SD-03 cells). Existing `per_defect` may
still call a claim-only case DETECTED under the historical content-level rule;
that does not promote it to `VERIFIED`. For baseline, prose can supply the
logical fields without `AR<n>` labels. For post, the formal receipt grammar and
linkage are mandatory.

The #610 delta passes only if the existing overall/critical recall,
clean-control false-finding, and severity-agreement gates still pass; recompute
strict recall does not regress; numeric false findings do not increase; and
every one of the four computable seeded opportunities is `VERIFIED` in each
score-eligible post MS01 replicate. Thus post receipt opportunity coverage and
arithmetic correctness are both 1.00 per replicate; a conspicuous-value claim
without arithmetic cannot pass. A stricter-looking report is not a substitute.

## 8. Follow-on implementation order

1. **This PR:** fixture v0.2, decision, oracle, metrics; no behavior change.
2. **Authorized baseline:** new harness cohort at the clean v0.2 merge SHA.
3. **Behavior PR:** add the methodology-only Phase 2 procedure/receipt slot to
   the canonical sprint source, synced agent prompt, statistical reference,
   protocol, conformance checker, and mutation tests. Phase 1 and other seats
   must not receive it.
4. **Authorized post fleet:** same model, fixtures, harness, and replicates.
5. **Script adapter PR:** design an isolated numeric input surface and emit the
   same receipt. Measure that orchestration change as its own delta.

Section 4's `inconsistent effect sizes` red flag is not silently declared
solved by these four procedures. The behavior PR must classify every arithmetic
red-flag row as covered, reporting-only, direct-threshold, or explicitly
`not_computable`; a future effect-size consistency procedure is a separate
bounded addition.
