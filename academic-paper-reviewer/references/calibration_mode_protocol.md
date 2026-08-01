# Calibration Mode Protocol

**Status**: v3.2 with #611 tier extension (2026-08-01)
**Parent skill**: `academic-paper-reviewer`
**Mode name**: `calibration`
**Purpose**: Either measure this reviewer's own false-negative rate (FNR), false-positive rate (FPR), balanced accuracy, and **severity-miscalibration rate** (#215) with the full tier, or obtain a low-cost directional signal at the Minor/Major boundary with the 3-paper tier. Only the full tier produces a measured error profile; both tiers attach an honestly scoped confidence disclosure to subsequent reviews in the same session.

---

## Why this mode exists

A single LLM reviewer produces an absolute 0-100 rubric score, but that score is weakly interpretable without knowing the reviewer's error profile. Two reviewers could give the same paper a 65, yet one might systematically over-score weak methodology papers and the other might systematically under-score cross-disciplinary work. Absolute scores don't reveal this.

Lu et al. (2026, Nature 651:914-919) demonstrated in Table 1 that an LLM-based Automated Reviewer can approach human balanced accuracy (0.65 vs human 0.67-0.73 on 500 ICLR 2022 papers) while having a dramatically different error profile: FNR 0.17 vs human 0.52, at the cost of FPR 0.50 vs human 0.17-0.34. Under that paper's positive=`Accept` convention, human reviewers over-reject acceptable papers more often (high FNR), while the Automated Reviewer lets reject-worthy papers through more often (high FPR). The class convention matters; reversing it reverses the prose interpretation even when the formulas stay unchanged.

Ren et al. (2026, arXiv:2607.13104, §8.1.2) frame the judge side of the same problem: a system optimized against the same judge that reports its results over-optimizes to that judge's latent biases, so rigorous protocols should enforce evaluator independence and transparency about the judge's identity, rubric, and budget; reliability can additionally be supported by repeated runs with variance estimates, aggregation across judge instances, and **calibration against a verifiable subset** via metric-based checks or targeted human review. Calibration mode instantiates that last safeguard: the user's gold set — papers with known outcomes — is the verifiable subset.

Translation for ARS: **our reviewer has an error profile too, and an ordinary review does not measure it.** Opt-in calibration mode closes that gap. It does not try to make the reviewer perfect; it makes the reviewer's imperfections legible.

---

## Inputs

1. **Calibration tier**: `full` by default. Use `directional` only when the user explicitly selects `directional`; never silently substitute it because the full tier is expensive.

2. **Gold-standard set**:
   - **Full tier**: 5-20 papers; recommended 10-15.
   - **Directional tier**: exactly 3 papers — one `minor_revision`, one `major_revision`, and one extreme anchor (`accept` or `reject`). `borderline` is not allowed in this tier.

   Each entry:
   - Paper file path or text
   - Ground-truth label: `accept`, `minor_revision`, `major_revision`, `reject`, or legacy `borderline`
   - Venue context (journal/conference, tier)
   - Optional: human reviewer scores for qualitative comparison
   - Optional per paper: `per_dimension_gold_scores`, an adjudicated 0-100 gold score for each of the seven rubric dimensions. In a completed full-tier attempt, `N` is the number of gold papers and `annotated_n` is the dimension-specific count whose entries supply that adjudicated score. Compute each dimension's error only over its `annotated_n` papers. Without this mapping, per-dimension calibration error is `NOT COMPUTABLE`; do not print an `±X` claim or imply that score error was measured. Every reported dimension error must include `annotated_n=<n>/<N>` and `missing=<N-n>`; `annotated_n=0` is `NOT COMPUTABLE`. Never present a subset-derived `±X` as a gold-set-wide estimate.

   **Gold-label isolation:** ground-truth labels, human scores, expected outcomes, `per_dimension_gold_scores`, and any gold rationale MUST NOT enter any field-analyst, reviewer, or synthesizer context. Join them to the completed panel outputs only after the final verdict is frozen. This applies to both tiers.

3. **Domain specification**: the user's target field, used to seed `field_analyst_agent`. Calibration for "machine learning venues" is not valid for "qualitative education research" — error profiles are domain-specific.

4. **Session persistence**: the full error profile or directional readout is cached for the **current session only**. No cross-session caching, no `~/.ars_calibration_cache/` directory. Calibration is explicitly opt-in per the v3.2 design decision: the user decides when to spend tokens on calibration, and a new session starts fresh. If the user wants to reuse a result across sessions, they re-run calibration or paste a prior report as a session prompt.

---

## Process

### Phase 0: Intake

- **Full tier:** verify 5-20 papers and at least one positive-side label (`accept` or `minor_revision`) plus one negative-side label (`major_revision` or `reject`); otherwise FNR or FPR is undefined. Legacy `borderline` entries remain allowed but are excluded from the binary matrix. Warn if n < 10: "Calibration with fewer than 10 papers produces wide confidence intervals. Results should be treated as directional, not conclusive."
- **Directional tier:** verify exactly 3 papers with one `minor_revision`, one `major_revision`, and one extreme anchor (`accept` or `reject`). Refuse any `borderline`, duplicate required slot, fourth paper, or missing slot. Display: "Directional tier: n=3, one run each, not ensembled; this is not an error-rate estimate."
- Never auto-select a tier from paper count. A three-paper request without an explicit tier choice requires clarification rather than silent downgrade.

### Phase 1: Run `full` panels under the selected tier

Both tiers reuse the same existing calibration-mode panel engine, reviewer prompts, and five-seat/synthesizer semantics that calibration used before #611. This extension changes only paper-count validation, replicate count, and reporting. It does not opt calibration into the v3.6.2 sprint contract and does not change ordinary `full` mode.

**Full tier.** Select `runs_per_paper` from `{3, 5}` (default 5; 3 is the existing budget override). For each paper, run that many fresh-context calibration panels (default ensembling follows Lu 2026 Methods A.1.1). Aggregate:
- Median rubric score per dimension
- Variance across the selected 3 or 5 runs (reported as a stability indicator)
- Editorial decision (majority vote across the selected 3 or 5 runs)

**Directional tier.** Run the same calibration panel engine once per paper in a fresh context: exactly 3 papers × 1 panel = 3 panels total. Do not ensemble, majority-vote, or manufacture variance from one draw. Preserve the synthesizer's exact four-value panel verdict and the four standard-format scoring-seat `Weighted Average` values exactly as emitted: Journal-Fit Reviewer, R1, R2, and R3. The Devil's Advocate's dedicated standard-mode format emits no 0-100 rubric score. Do not average, median, select, or otherwise collapse those four values into a singular panel score, and do not mint a score for the Devil's Advocate.

**Cross-model verification**: In calibration mode, `ARS_CROSS_MODEL` is **default-on** rather than opt-in. Follow `shared/cross_model_verification.md` § Calibration transport exception: before the first scored panel, create an `attempt_id` and lock one `substrate_plan` without consulting gold material. When cross-model is configured, consented, and preflight-available, apply the calibration-specific non-sprint Reviewer 2 transport in **every panel**; otherwise lock every seat to the primary family before the schedule begins and disclose why. The plan stays identical for every paper and every replicate in either tier; varying substrate by gold label or run would confound calibration. A mid-attempt cross-model failure invalidates the whole attempt: no completed panel enters an aggregate, and any result-producing all-primary retry uses a new attempt, an empty aggregate, and restarts from paper 1 / replicate 1. Never emit a report, readout, or session disclosure from an incomplete or mixed-substrate attempt. Provider consent and manuscript-privacy rules remain unchanged; ordinary `reviewer_full` keeps its existing per-seat disclosed fallback.

### Phase 2: Build the full-tier confusion matrix

This phase applies to `full` only. Compare the reviewer's majority-vote decision against the user's ground-truth label.

- `borderline` ground truth papers are excluded from the binary confusion matrix but reported separately (see Phase 3).
- Map `Accept` and `Minor Revision` reviewer decisions → positive. Map `Major Revision` and `Reject` → negative. This follows Lu 2026 Table 1's binarization.
- With that fixed positive class, **FNR is the over-harsh error rate**: a gold `accept`/`minor_revision` paper predicted as Major/Reject. **FPR is the lenient error rate**: a gold `major_revision`/`reject` paper predicted as Accept/Minor. Never describe FNR as missed rejects or FPR as over-rejection.

Compute:

| Metric | Formula | Report with |
|---|---|---|
| Balanced accuracy | (TPR + TNR) / 2 | 95% CI via bootstrap (1000 resamples) |
| FNR (over-harsh) | FN / (FN + TP) | Same |
| FPR (lenient) | FP / (FP + TN) | Same |
| AUC | ROC over rubric-score threshold | Same |
| Calibration error | Mean &#124;median rubric score - `per_dimension_gold_scores[dimension]`&#124; over annotated papers only | Per dimension, include `annotated_n=<n>/<N>` and `missing=<N-n>`; `annotated_n=0` is `NOT COMPUTABLE` |

### Phase 2.5: Minor/Major boundary sub-matrix (both tiers)

This is the highest-traffic boundary that the binary matrix collapses. Whenever the gold set contains both `minor_revision` and `major_revision`, add this raw-count sub-matrix. It keeps every predicted overshoot by using decision sides, while the per-paper table preserves the exact predicted verdict.

| Gold \ predicted side | Accept + Minor | Major + Reject |
|---|---:|---:|
| Minor Revision | stayed minor-side | harsh crossing |
| Major Revision | lenient crossing | stayed major-side |

For a full tier lacking either Minor or Major gold examples, print `NOT ESTIMABLE — gold set lacks both sides of the Minor/Major boundary`; never render an all-zero table as evidence of no confusion. The directional composition always makes the matrix estimable.

### Phase 2.6: Directional-tier reporting boundary

For `directional`, report only:

- the exact gold label, exact panel verdict, and four raw scoring-seat weighted averages (Journal-Fit Reviewer, R1, R2, R3) for each of the 3 papers;
- raw `lenient` / `exact` / `harsh` counts under the ordered ladder `Accept < Minor Revision < Major Revision < Reject`;
- the four raw cells of the Phase 2.5 Minor/Major matrix; and
- raw `low` / `med` / `high` severity-miscalibration-risk counts from Phase 3.5.

The directional tier **MUST NOT report** balanced accuracy, FNR, FPR, AUC, bootstrap confidence intervals, ensemble stability, per-dimension mean absolute calibration error, Lu numeric comparisons, or any claim that it measured the reviewer's error profile. Three single draws cannot support those estimates.

### Phase 3: Borderline handling

This phase applies to the full tier only. Borderline papers don't enter the binary matrix but are useful for rubric-score calibration. For each borderline paper, report:
- The reviewer's rubric score
- The reviewer's decision
- Whether the reviewer's decision respects the user's "this is borderline" signal (i.e., did it correctly land in Major Revision rather than confidently Accept or Reject?)

A reviewer that confidently Accepts or Rejects borderline papers has a "confidence miscalibration" problem even if its binary accuracy looks fine.

### Phase 3.5: Severity-miscalibration measurement (#215)

The binary confusion matrix (Phase 2) measures decision-level error (FNR/FPR). It does **not** capture the paper's largest documented AI-reviewer failure: a finding that is content-correct but **severity-miscalibrated** — either a field-norm boundary error (Kim et al. 2026, W1, n=54) or the "would addressing this change the core result?" significance-boundary error (Kim §F.3.4, 56 errors). A reviewer can have a clean FNR/FPR and still systematically over- or under-rate the severity of individual findings.

For each weakness the reviewer emitted across the gold runs, classify its **severity-miscalibration risk** as `low` / `med` / `high`:

- **`high`** — the finding's severity rests on a field norm or the "core result" formula, AND the reviewer asserted the severity **without** grounding the norm in an external checkable source (the W1 / §F.3.4 failure shape).
- **`med`** — severity depends on a field norm but the reviewer gave partial or weak grounding (named a standard but did not establish it applies to this subfield).
- **`low`** — severity does not depend on a field norm, OR the norm is grounded in an external checkable source per the domain-reviewer Field-Norm Severity Discipline (Step 5).

**Grounding discipline (do not repeat the failure you are measuring).** The classifier persona **MUST NOT** guess whether a norm is right from its own model knowledge — that is exactly the W1 behaviour under audit. It rates *whether the reviewer supplied external grounding*, not *whether the reviewer's norm is factually correct*. The reference shapes are anchored to the first-party regression fixture at `evals/gold/field_norm_severity/` (W1 + §F.3.4 cases extracted verbatim from Kim et al. 2026); a finding that matches a fixture shape but lacks grounding is `high`.

For the full tier, this produces a low/med/high histogram with counts and shares reported alongside FNR/FPR in Phase 4. For the directional tier, report raw counts only — no share-based calibration claim from three single panels. Either form is a severity-risk signal the binary matrix cannot show.

### Phase 4: Produce the Calibration Report

The **full-tier** output document is structured as:

```
# Calibration Report for <Reviewer Instance>
Tier: full
Domain: <domain>
Gold set: n=<N> (accept=<a>, minor_revision=<m>, major_revision=<M>, reject=<r>, borderline=<b>)
Runs per paper: <3|5> (ensembled)
Cross-model: <yes/no, model families used>

## Summary metrics
- Balanced accuracy: 0.XX [95% CI: 0.XX - 0.XX]
- FNR: 0.XX [95% CI ...]
- FPR: 0.XX [95% CI ...]
- AUC: 0.XX
- Ensemble stability: <mean std of rubric scores across runs>

## Comparison to Lu 2026 Table 1 baselines
<show the numeric table only for an all-binary accept/reject gold set in the
same ML-venue setting; otherwise print `NOT DIRECTLY COMPARABLE — this gold set
uses revision labels and/or a different domain` and treat Lu only as context>
| Metric | This reviewer | Lu 2026 Automated Reviewer | Lu 2026 Human |
|---|---|---|---|
| Balanced accuracy | X | 0.65 | 0.67-0.73 |
| FNR | X | 0.17 | 0.52 |
| FPR | X | 0.50 | 0.17-0.34 |

(Note: even when shown, Lu 2026 values are descriptive external context, not a benchmark target.)

## Per-dimension calibration error
<table of 7 review dimensions with columns for mean absolute calibration error,
annotated_n, and missing; report `annotated_n=<n>/<N>` and `missing=<N-n>` for every dimension.
Compute each error only over papers where that dimension's `per_dimension_gold_scores`
entry exists; `annotated_n=0` is `NOT COMPUTABLE — adjudicated per-dimension gold
scores were not supplied for this dimension`.>

## Minor/Major boundary sub-matrix
<the Phase 2.5 raw-count matrix, or NOT ESTIMABLE with the missing-side reason>

## Severity-miscalibration histogram (#215)
<low/med/high counts over all emitted weaknesses, e.g.>
| Risk | Count | Share |
|---|---|---|
| low | XX | XX% |
| med | XX | XX% |
| high | XX | XX% |
<A high `high`-share means the reviewer frequently asserts field-norm / "core result" severities without external grounding — the W1 / §F.3.4 failure shape. This is a SEPARATE signal from FNR/FPR: a reviewer can pass the binary gate and still carry a high severity-miscalibration rate. Grounded per Phase 3.5; classifies grounding, not norm-correctness.>

## Systematic biases detected
<natural-language narrative identifying patterns, e.g.
 "Reviewer tends to over-score originality on cross-disciplinary papers"
 "Reviewer under-scores qualitative methodology by ~8 points vs ground truth (annotated_n=<n>/<N>, missing=<N-n>)"
Any quantified score bias must name one dimension and carry that dimension's coverage;
never generalize its observed error to unannotated papers or other dimensions.
>

## Recommendations for session use
- For each dimension with `annotated_n>0`: report only that dimension's observed mean absolute calibration error as `±X points (annotated_n=<n>/<N>, missing=<N-n>)`
- For each dimension with `annotated_n=0`: report `NOT COMPUTABLE (annotated_n=0/<N>, missing=<N>)`; no ±X claim is available
- FNR X% means X% of acceptable-side gold papers were judged too harshly
- FPR X% means X% of reject-side gold papers were judged too leniently
- For decisions near the accept/reject boundary, escalate to human judgement
```

The **directional-tier** output is a separate, deliberately non-metric readout:

```
# Directional Calibration Readout for <Reviewer Instance>
Tier: directional
Domain: <domain>
Gold set: n=3 (minor_revision=1, major_revision=1, extreme_anchor=<accept|reject>=1)
Runs per paper: 1 (not ensembled)
Cross-model: <yes/no, model families used>

## Exact per-paper results
| Paper | Gold exact verdict | Panel exact verdict | Journal-Fit weighted average | R1 weighted average | R2 weighted average | R3 weighted average | Direction |
|---|---|---|---:|---:|---:|---:|---|
| <id> | <Accept/Minor/Major/Reject> | <Accept/Minor/Major/Reject> | <0-100> | <0-100> | <0-100> | <0-100> | <lenient/exact/harsh> |

## Directional raw counts
- lenient: <n>
- exact: <n>
- harsh: <n>

## Minor/Major boundary sub-matrix
<the Phase 2.5 four raw cells>

## Severity-miscalibration risk counts (#215)
| Risk | Raw count |
|---|---:|
| low | <n> |
| med | <n> |
| high | <n> |

## Interpretation boundary
Directional evidence only: n=3, one run each, not ensembled. This readout is
not an error-rate estimate and does not measure balanced accuracy, FNR/FPR,
AUC, calibration error, or stability.
```

### Phase 5: Session attachment

If session persistence is enabled, the result is attached to every subsequent review in the same session as a **confidence disclosure header**. A full-tier disclosure appears before the verdict as:

```
> **Reviewer Confidence Disclosure (from calibration session <id>):**
> This reviewer has measured balanced accuracy 0.XX, FNR 0.XX, FPR 0.XX on a
> gold set of <N> papers in <domain>. Per-dimension score error is disclosed
> separately for each dimension with `annotated_n>0` as
> `<dimension>: ±X points (annotated_n=<n>/<N>, missing=<N-n>)`; list every
> dimension with no annotated gold as
> `<dimension>: NOT COMPUTABLE (annotated_n=0/<N>, missing=<N>)`. A subset-derived error is not a
> gold-set-wide estimate. Treat borderline
> decisions with human judgement.
```

A directional result MUST use this different disclosure and must not borrow the measured-profile wording:

```
> **Directional Reviewer Calibration Disclosure (session <id>):**
> This is directional evidence from exactly 3 gold papers, one run each and
> not ensembled. It observed <lenient/exact/harsh> raw counts and the
> Minor/Major boundary cells shown in the attached readout. It is not an
> error-rate estimate; balanced accuracy, FNR/FPR, AUC, calibration error, and
> stability were not measured. Escalate boundary decisions to human judgement.
```

A later full-tier report replaces the directional disclosure for that domain/session; the reverse never happens silently.

This is non-negotiable in calibration-enabled sessions: the user cannot hide or overstate the disclosure. The point of calibration is to make uncertainty legible; suppressing a full profile or presenting a directional readout as one defeats the mode.

---

## Ensembling methodology notes

Lu 2026 Methods A.1.1 describes reviewer ensembling across 5 independent runs with majority voting. The full tier's default five-run path follows that spec with two changes; the three-run budget override uses the same aggregation over three fresh contexts:

1. **Median instead of mean for rubric scores**: mean is vulnerable to single-run outliers (e.g., a run that hallucinates a methodological flaw); median is robust.
2. **Fresh context per run**: Lu 2026 allowed within-session memory across runs. ARS uses fresh context to prevent cascading errors from a single run's misreading.

Full-tier users with token budget concerns can reduce `runs_per_paper` to 3. Below 3, ensembling is meaningless — do not allow 1 or 2 in the full tier. The directional tier's one run per paper is an explicit non-ensemble exception and therefore never reports ensemble metrics.

---

## Failure cases this mode does NOT fix

Full calibration reports this reviewer's error profile on a **specific** gold set in a **specific** domain; directional calibration reports only a three-paper signal. Neither tier:

- Predict performance on papers outside that domain
- Detect frame-lock within a single paper review (that's `devils_advocate_reviewer` territory)
- Catch implementation-bug-as-finding cases (that's the AI Research Failure Mode Checklist, ROADMAP_v3.2.md item 2)
- Replace the `re-review` mode for revision verification

If the user's gold set is itself biased (e.g., all papers from one lab, all from one year), full calibration reports a biased profile and directional calibration reports a biased signal. Emit a warning during intake if papers share obvious metadata clusters.

### Same-family / rubric-aware judging — read the numbers as a possible under-estimate

There is a second reason a measured profile can be optimistic, independent of the gold set. It belongs to the broader **same-source evaluation risk**, which has two forms:

- **Factual form** — *same-source hallucination*: when the model that wrote the work and the model verifying it share training data, a fabricated reference that "feels right" passes undetected. This is the citation-integrity risk documented in the Anti-Hallucination Mandate (`academic-pipeline/agents/integrity_verification_agent.md`), countered there by independent reference lookup.
- **Behavioral form** — *same-family rubric optimization* (rubric-aware judging): an evaluator may, to some degree, optimize toward *what the rubric appears to reward* rather than toward the correct judgment. When the produced-work model and the evaluator model are from the same family and may be rubric-aware, the calibration error you measure can be **optimistic — read it as a possible under-estimate of the true error, not a ceiling.**

This is an interpretive caveat only. ARS does **not** detect, prevent, or correct rubric-aware judging — the behavior can be unverbalized and is not reliably visible in chain-of-thought. The note changes how you *read* the numbers; it does not change any threshold or gate.

**Cross-model evaluation — stronger evidence where available.** Running the evaluation across model families provides **stronger evidence** than a same-family-only run; it still does **not** detect or rule out rubric-aware judging. Positioning:

- In ordinary reviewer / judge paths, cross-model is **opt-in, "for best results"** — the citation-claim alignment judge already supports a non-default judge model, and the suite is designed to work single-model.
- **Calibration mode is the exception**: calibration itself is opt-in, but once invoked `ARS_CROSS_MODEL` is **default-on** (see "Cross-model verification" under Phase 1). When configured and consented, the #540 Reviewer-2 substrate swap is used consistently in every panel; it is never varied by paper or replicate.
- Absent cross-model is **warn-and-continue**, never a gate.
- Sending a user's manuscript to another provider still requires the explicit consent / privacy step in `shared/cross_model_verification.md` — this recommendation does not weaken that boundary.

**A single-model spot-check (weak, optional).** With no second model, you can reword the rubric and re-judge, then check whether the verdict changed. Be clear about what this does: it only tells you whether a *change of wording* shifts the judgment — surface wording sensitivity. It does **not** reveal whether the model is quietly optimizing toward the grader (that can be unverbalized), and a verdict that survives rewording is **not** evidence the judgment is correct — only that it is stable to that paraphrase. It is one model checking itself, so its power against grader-awareness is limited. No score, no threshold, no gate.

### Directional prior: assume leniency relative to human expert review (FARS external anchor)

Beyond the same-family optimism above, there is a citable **directional** prior on the sign of the error: when the simulated 5-reviewer panel's output is read as a pass/fail signal, assume it runs **lenient relative to human expert review** until your own full-tier calibration measurement shows otherwise. FARS (Tang et al. 2026, arXiv:2606.31651) provides a deployment-scale external anchor: on the FARS deployment corpus, an ICLR-style automated reviewer (Stanford Agentic Reviewer) averaged 5.00 over the 165 papers it reviewed, while the paper-level mean from 282 human expert reviews covering 140 of those papers was 3.23 on the same 0-10 scale — a ~1.8-point gap (a descriptive difference between overlapping-but-unequal paper sets, not a paired estimate), and the automated score never functioned as an acceptance probability, only as a relative ranking.

How to use this prior:

- The **direction** is a working prior, not a law: FARS measured one setup (ICLR-style ML reviewing, one reviewer system), so carrying its sign to other domains, rubrics, or this panel is a heuristic extrapolation — which is exactly why it lands as a default-until-measured assumption rather than a fact. Under this prior, a panel "accept" is weaker evidence than a panel "reject", and a panel score is better read as a relative ranking within a batch than as an acceptance probability.
- The **magnitude** (~1.8 points) is **NOT portable** across domains, rubrics, or model setups. Never apply it as a correction factor, threshold shift, or score adjustment — if you need a number for your setup, measure it with the full tier (Phases 2/4, using the optional human reviewer scores in the gold set).
- This is an interpretive caveat only: no behavior, schema, gate, or threshold changes. The simulated panel remains advisory infrastructure behind human checkpoints — the caveat is about how to read its output, not about its authority. In particular it is a **measurement-reading prior for calibration**, not a decision rule: at decision time the symmetric evidence standards of `editorial_decision_standards.md` § Decision Symmetry and Register Independence (#574 B1) govern, and no verdict is shaded stricter on this prior's account.

---

## Integration with existing modes

| Existing mode | Interaction with calibration |
|---|---|
| `full` | Full calibration runs the existing calibration panel engine 5x per gold paper (3x budget override); directional runs the same engine once on each of exactly 3 papers. No change to ordinary `full` mode itself. |
| `re-review` | The tier-appropriate calibration disclosure attaches to re-review decisions. |
| `quick` | The tier-appropriate disclosure attaches. A full profile notes that `quick` has additional uncalibrated error; a directional readout makes no error-rate claim. |
| `methodology-focus` | Calibration should ideally be run with methodology-heavy gold papers if this mode is the user's target. |
| `guided` | Not applicable — guided mode is Socratic dialogue, rubric scores are not the primary output. |

---

## Resolved design decisions (2026-04-09)

- **Activation**: opt-in only. User invokes `calibration` mode explicitly. ARS does not auto-calibrate on first use in a new domain.
- **Tier default (#611, 2026-08-01)**: `full` remains the default. The 3-paper `directional` tier requires an explicit user selection and never impersonates a measured error profile.
- **Persistence**: session-scoped only. No cross-session caching of profiles, no `~/.ars_calibration_cache/`, no privacy questions about storing paper content on disk.
- **Shipped gold sets**: not planned for v3.2. Users bring their own gold set. Shipping a built-in ML gold set was considered and rejected to avoid domain-coverage bias and staleness.
- **Continuous/self-calibration**: rejected. Using the reviewer's own historical decisions as pseudo-ground-truth is circular and would make the error profile look better over time without actually improving accuracy.

---

## References

- Lu, C. et al. (2026). Towards end-to-end automation of AI research. *Nature* 651, 914-919. doi:10.1038/s41586-026-10265-5 — Table 1 (reviewer validation), Methods A.1.1 (ensembling).
- Tang, Q., Hu, X., Liu, X., Chen, Y. & Shao, Y. (2026). FARS: A fully automated research system deployed at scale. arXiv:2606.31651 — deployment-scale automated-vs-human reviewer comparison (automated mean over 165 papers; 282 human expert reviews over 140 papers); source of the leniency-direction anchor above.
- Efron, B. & Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall/CRC — bootstrap CI methodology.
- ARS `shared/cross_model_verification.md` — cross-model reviewer integration.
- ARS `academic-paper-reviewer/references/quality_rubrics.md` — scoring rubric definitions.

## v3.6.2 sprint contract status

v3.6.2 introduces sprint contracts for `reviewer_full` and `reviewer_methodology_focus` only. Calibration remains outside that contract and retains its existing panel engine and prompt semantics. The #611 tier extension changes only intake shape, replicate count, and reporting boundaries; it does not alter reviewer or synthesizer behavior.
