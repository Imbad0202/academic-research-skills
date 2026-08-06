# #610 Step 5 — Script Adapter: Isolated Numeric Input Surface

Status: **design approved 2026-08-06; orchestration change measured as its own
delta**
Issue: #610 (§8 step 5 of the 2026-08-02 spec)
Parent spec: `docs/design/2026-08-02-610-statistical-recompute-baseline-spec.md`
Date: 2026-08-06

## 1. Outcome

Implement §8 step 5 of the parent spec: *"design an isolated numeric input
surface and emit the same receipt. Measure that orchestration change as its
own delta."*

The methodology seat's arithmetic moves from the model to a deterministic
stdlib-only calculator, without changing the downstream review contract:

1. a new paper-visible **extraction call** has the methodology seat transcribe
   manuscript-reported values into a closed, typed `## Recompute Extraction`
   grammar — no arithmetic, no judgment;
2. a new **calculator** (`scripts/recompute_receipts.py`) computes every
   receipt deterministically from the extraction alone — it never sees the
   manuscript — and emits the exact `## Arithmetic Receipts` grammar the #644
   conformance gate already pins;
3. the seat's Phase 2 call receives the computed receipts and must reproduce
   them **verbatim**, adding only the `finding_ref:` linkage lines the
   mismatch receipts require; a byte-identity gate enforces the copy.

The seam frozen by the parent spec — the receipt — is unchanged. Synthesis,
adjudication verdicts (`recompute_adjudication`), promotion, and every
non-methodology seat are untouched.

## 2. Why this shape

- **The contamination fence is preserved.** The reviewer call still runs with
  `--tools ""`; the calculator runs in the dispatching layer, exactly the
  "separately reviewed extraction -> calculation -> receipt injection
  boundary" the parent spec §2 names as the preferred end state, not a tool
  exception inside the reviewer call.
- **Failure attribution becomes separable.** Extraction infidelity (wrong
  number transcribed) is a model failure adjudication can see against the
  manifest; arithmetic is script-owned and pinned by tests; linkage and
  composition failures are conformance aborts. The post cohort's residual
  audit burden — hand-verifying model arithmetic — collapses to verifying
  transcription.
- **Determinism replaces a model-state-dependent 4/4.** The 2026-08-05/06
  post row's recompute gate passed on claude-opus-5 @ xhigh; nothing prevents
  a weaker model or a future drift from silently regressing arithmetic while
  receipts still look complete. After step 5, `arithmetic_correct` is
  structural for every receipt the calculator emits.

## 3. The isolated numeric input surface

### 3.1 Extraction call

A new dispatch call for the methodology seat only, between Phase 1 and
Phase 2 (three calls total; every other seat keeps two). Paper-visible; the
prompt is the seat's `### Phase 2E — Numeric extraction (script-adapter
dispatch)` agent section plus the delimited manuscript. The response must
consist of exactly one `## Recompute Extraction` H2 section whose content
lines are machine lines only (same two-decoration tolerance and
fence-transparent reading as the receipt grammar), holding either:

- one `### RR<n>` subsection per distinct arithmetic claim (contiguous
  `RR1..RRn`), or
- exactly one `no_recomputable_statistics: <basis>` attestation line — the
  same declaration-only semantics as #644.

### 3.2 RR field grammar (closed; v1)

Common to every RR, each exactly once:

| Field | Value |
|---|---|
| `procedure_id` | `p_from_test_statistic` \| `grim` \| `grimmer` \| `n_from_df` |
| `evidence_anchor` | existing six-type anchor grammar |
| `reported_inputs` | single-line prose: every manuscript value used, verbatim |
| `assumptions` | single-line prose: only paper-licensed assumptions |

Per-procedure typed fields (each exactly once; `unavailable` is an explicit
sentinel — the calculator, not the model, decides what it makes
non-computable):

- `p_from_test_statistic`: `test_family:` (`t`\|`z`\|`F`\|`chi_square`\|`unavailable`),
  `statistic_value:` (decimal \| `unavailable`), `df:` (integer \| `int,int`
  for F \| `none` for z \| `unavailable`), `reported_p_comparator:`
  (`equals`\|`less_than`\|`less_than_or_equal`\|`greater_than`\|`greater_than_or_equal`),
  `reported_p_value:` (decimal), `tail_convention:`
  (`two-tailed`\|`one-tailed`\|`upper-tail`\|`unstated` — what the paper states).
- `grim`: `n:` (integer \| `unavailable`), `reported_mean:` (decimal; its
  digit string fixes the reported precision), `scale_min:` / `scale_max:`
  (integers \| `unavailable`; v1 covers single items with integer
  granularity), `rounding_rule:` (`half-up`\|`half-even`\|`truncation`\|`unstated`).
- `grimmer`: every `grim` field plus `reported_sd:` (decimal) and
  `sd_convention:` (`sample`\|`population`\|`unstated`).
- `n_from_df`: `df_reported:` (integer), `df_identity_candidate:`
  (`df=N-1`\|`df=N1+N2-2`\|`other_or_corrected`\|`unavailable`), `stated_n:`
  (integer \| `unavailable`), `stated_n_relation:`
  (`equals`\|`at_most`\|`at_least`\|`unavailable`).

The conformance gate (new `--extraction` stage in
`check_phase_conformance.py`) validates shape, enums, numeric parses, the
per-procedure field matrix, and the anchor grammar. Whether the transcription
is FAITHFUL to the manuscript is adjudicated, not machine-checked — the same
epistemic split as #644's attestation.

### 3.3 Deterministic verdict logic

The calculator maps extraction to receipts with no discretion:

- **Sentinel mapping** (fixed first-match order per procedure):
  `test_family: unavailable` → `test_family_ambiguous`; missing
  statistic/df/stated-n inputs → `missing_reported_value`; `n: unavailable` →
  `analytic_n_ambiguous`; scale bounds unavailable → `scale_support_unknown`;
  `df_identity_candidate: other_or_corrected` → `model_correction_or_pooling`,
  `unavailable` → `df_identity_ambiguous`.
- **`p_from_test_statistic`**: t/F/chi-square/z tail probabilities via
  stdlib-only regularized incomplete beta/gamma (continued-fraction forms) and
  `math.erfc`; F and chi-square are upper-tail by family; under `unstated`
  tail both labeled values are computed and shown (§5.1), verdict `mismatch`
  only when BOTH tails fail, `consistent` when both pass, and a tail-dependent
  verdict is `not_computable: tail_ambiguous`. Equality comparisons use the
  reported value's rounding interval; a derived value within 1e-9 of an
  interval endpoint or inequality threshold is `rounding_boundary_ambiguous` /
  `inequality_unresolvable`, never a coin-flip.
- **`grim`**: exact rational arithmetic (`fractions.Fraction`, no floats):
  reachability of the reported mean as `s/n` over integer sums in the scale
  range, evaluated under the stated rounding rule, or under BOTH `half-up` and
  `half-even` when `unstated` — agreement yields the verdict,
  disagreement `rounding_rule_ambiguous`. Emits the §5.2 `rounding_interval`
  and `nearest_achievable` conditional lines.
- **`grimmer`**: GRIM-gate the mean first (failure →
  `mean_grim_inconsistent`); then exhaustively enumerate attainable
  sum-of-squares over count vectors with the mean-compatible sums (exact
  rational; SD compared via its square, so no square roots enter the
  decision), under both SD conventions when `unstated` (disagreement →
  `sd_convention_unknown`). An enumeration whose bound exceeds the
  documented iteration budget is `reachability_not_completed` — never an
  approximation.
- **`n_from_df`**: implied N from the closed identity set (`df=N-1`,
  `df=N1+N2-2`), compared under `stated_n_relation`; the Welch ceiling
  argument from §5.4 backs the `at_most` derivation prose.
- The calculator emits `consistent` / `mismatch` / `not_computable` only;
  `not_applicable` remains grammar-legal but is never script-emitted (an RR
  is by construction an applicability claim).

Every receipt carries the eight canonical #644 lines plus its conditional
lines; `derivation` and `comparison_rule` are script-generated auditable
sentences; `reported_inputs`, `assumptions`, and `evidence_anchor` are copied
from the RR byte-for-byte. `finding_ref:` is **never** script-emitted.

## 4. Injection and the identity gate

The Phase 2 user message gains a `<computed_receipts>` block holding the full
`## Arithmetic Receipts` section. The canonical `methodology-receipt`
fragment becomes conditional:

- **Block present (script-adapter dispatch):** reproduce the section verbatim
  as the final section of the card; add exactly one `finding_ref: W<n>` line
  to each `mismatch` receipt, plus the existing `**Arithmetic Receipt**:
  AR<n>` back-reference in the linked weakness; add, remove, or alter nothing
  else.
- **Block absent (every other orchestrator, including runtime-Bash-denied
  sessions):** the #644 self-compute behavior applies unchanged — graceful
  degradation, no second philosophy.

`check_phase_conformance.py` gains `--injected-receipts <file>` (valid only
with `--phase2`): after the existing receipt-grammar gate, the card's receipt
section — read through the same fence-transparent view — must equal the
injected section line-for-line once canonical `finding_ref:` lines are
removed; decorated re-spellings of injected lines fail the identity, loudly.
Mismatch receipts still require their `finding_ref:` via the existing gate,
so "copy verbatim and add nothing" cannot be satisfied by dropping linkage.

## 5. Dispatch orchestration (`dispatch_e4_panel.py`)

- Methodology seat: Phase 1 → extraction → calculator → Phase 2.
- The extraction call gets **one structural retry** (same class and evidence
  contract as the Phase 1 structural retry; a new `extraction_retries` record
  group — a new retry class gets its own list). Phase 2 retry policy is
  unchanged.
- The calculator runs as a supervised subprocess over bundle artifacts
  (extraction in, `methodology.receipts.md` out). A nonzero exit after a
  gate-passed extraction is a **harness infra fault**: the panel is recorded
  BLOCKED, never counted as a conformance abort and never silently retried.
- `EVIDENCE_CONTRACT` bumps to `reviewer-e4/2026-08-06` (three-call
  methodology shape + extraction retry class + receipts artifact are contract
  content).
- The harness at this SHA always runs the three-call shape; `condition`
  remains a record label, never a prompt selector. Baseline/post shapes live
  at their frozen SHAs.

## 6. Measurement — the step-5 delta

Separately authorized (not part of this PR): smoke + 2 x 3 fleet
(`--condition script_adapter`), same model (claude-opus-5 @ xhigh), same
fixtures v0.2, frozen clean checkout of the step-5 merge SHA. **Comparison
row: the 2026-08-05/06 post cohort (305884b)** — this measures the
orchestration change, not the receipt grammar again.

Gates (vs the post row): recompute strict recall stays 4/4 per score-eligible
MS01 replicate with coverage and arithmetic correctness 1.00; overall and
critical-band recall do not regress; clean-control numeric false findings do
not increase; severity agreement reported under the frozen measure with the
honest-FAIL precedent (#645) if it moves; conformance-abort rate reported
against post's 0/6 — the extraction grammar is a new abort surface and its
first-fleet behavior is a finding, not a footnote.

New reporting rows: per-RR extraction fidelity (adjudicated against the
manifest), and the calculator's `not_computable` reason distribution.

## 7. Non-goals and boundaries

- No new bounded procedure; the §8 note on effect-size consistency stands.
- No SciPy/NumPy dependency; accuracy is pinned by tests against the parent
  spec's worked cases and published distribution tables.
- The calculator never reads the manuscript, the fixture manifests, or the
  repo — its entire input is the extraction artifact (that is what makes the
  surface "isolated").
- Real-reviewer (non-harness) sessions keep #644 behavior until an
  orchestrator that can execute scripts opts in; nothing degrades for
  Bash-denied environments.
- Historical rows are not rewritten; this SHA's records carry the new
  evidence contract string.
