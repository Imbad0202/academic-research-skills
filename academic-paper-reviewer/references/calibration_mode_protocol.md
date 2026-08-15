# Calibration Mode Protocol

**Parent skill**: `academic-paper-reviewer`
**Mode name**: `calibration`
**Purpose**: Measure a bounded decision-error profile against a user-adjudicated target set, or obtain a cheaper directional readout. This protocol never turns criterion judgements into an absolute quality score.

## Epistemic status

An ordinary review has `calibration_status: NOT_CALIBRATED`. Its categorical judgements are tied to named criteria and evidence in one manuscript; they do not establish a stable interval scale, paper ranking, acceptance probability, or cross-session reproducibility.

The full tier may produce a candidate empirical target profile only after completing the protocol against the current domain, article type, venue criteria, rubric version, review mode, and exact replay-derived `execution_topology_sha256`. `PROFILE_MEASURED` means only that errors were measured on that bounded target set. It is not a claim of universal calibration and must not be transported to a materially different target or review topology.

**Current application boundary:** candidate profile production and live-review
profile application are separate operations. Until a closed, hash-bound target
profile schema plus replay validator is shipped, reviewer seats and the current
Schema 6 package adapter emit `calibration_status: NOT_CALIBRATED`; a prose
profile ID or apparent topology match cannot upgrade them. The full-tier report
may describe its measured candidate profile, but must label it
`application_status: NOT_WIRED_TO_LIVE_REVIEW`.

The directional tier always reports `calibration_status: NOT_CALIBRATED`. Three single panels provide directional observations, not an error profile.

## Inputs

1. **Tier**: `full` by default. Use `directional` only when explicitly selected.
2. **Empirical target set**:
   - Full: 5–20 user-adjudicated papers, preferably 10–15, with at least one acceptable-side and one reject-side label.
   - Directional: exactly three papers—one `minor_revision`, one `major_revision`, and one extreme anchor (`accept` or `reject`).
3. **Per-paper fields**:
   - manuscript path or text;
   - adjudicated verdict: `accept`, `minor_revision`, `major_revision`, `reject`, or legacy `borderline` in the full tier only;
   - venue, domain, and article-type context;
   - optional `per_dimension_gold_judgements`, using the same criterion-bound categories as `quality_rubrics.md`, with the criterion source and adjudication rationale.
4. **Target-profile identity**: domain, article type, venue criteria/version, rubric version, review mode, target-set identifier, adjudication date, and one exact `execution_topology_sha256` derived from actual completed panel provenance. A prose configuration label or intended route is not a match key.
5. **Session persistence**: session-only. Do not cache manuscripts or profiles across sessions.

### Gold-label isolation

Gold verdicts, dimension judgements, rationales, and human assessments must not enter field-analyst, reviewer, or synthesizer context. Join them only after a panel verdict is frozen. The substrate plan must also be fixed without consulting gold material.

This isolation applies to transport as well as prompt construction: no gold
verdict, dimension judgement, rationale, human assessment, or target-set
outcome may enter a provider payload or determine the substrate plan. The join
is post-freeze only, and joined material cannot be fed back into another panel
within the same attempt.

## Process

### Phase 0: Intake

- Full tier: verify 5–20 papers and both sides of the binary decision boundary. Warn that small or clustered target sets yield uncertain, non-transportable estimates. Legacy `borderline` papers are reported separately and excluded from binary metrics.
- Directional tier: verify exactly the required three-paper composition, one run per paper, and no `borderline` item. State that the result remains `NOT_CALIBRATED`.
- Never infer the tier from paper count; ask when the user's selection is missing.

### Phase 1: Run panels

**Full tier.** Run 3 or 5 panel replicates per paper (default 5), then derive the panel verdict by majority vote. Within each replicate, the five seats must have distinct recorded invocation-context IDs. The current provenance artifact checks only that within-panel separation; it does not compare IDs against earlier replicates and therefore does not establish cross-replicate freshness or independent error processes. Preserve each seat's criterion-bound judgements and evidence; do not convert them to numbers or average them. Report exact-agreement and disagreement patterns for a dimension only when the matching gold judgement exists.

**Directional tier.** Run one panel per paper with distinct recorded invocation-context IDs among its five seats. Preserve the exact panel verdict and each scoring seat's categorical dimension judgements as emitted. Do not ensemble, manufacture variance, combine labels into a panel score, or rank the papers.

**Cross-model verification and actual provenance.** `ARS_CROSS_MODEL` is
default-on for calibration mode. Follow
`shared/cross_model_verification.md` § Calibration transport exception. Before
any provider call, run its closed calibration data-fence collision preflight
independently on the raw reviewer-configuration bytes and raw manuscript bytes.
A collision refuses the entire attempt before transport: do not send either
payload and do not escape, strip, rewrite, truncate, switch delimiters, or
silently fall back.

Create an `attempt_id`, lock one `substrate_plan` before any gold material is
consulted, and use the same transport and substrate for every paper and
replicate. For every completed panel, build and replay-validate
`review-panel-provenance/1.0` from actual seat executions. All result-producing
panels in one calibration attempt MUST have one identical
`execution_topology_sha256`; every artifact must derive `fresh_context: true`
under its fixed `within_panel_attempt_only` scope. The builder receives no
attempt-history ledger: even if invocation-context IDs differ within each
artifact, it cannot detect reuse across papers or replicates. Every candidate
profile and readout must disclose that cross-replicate freshness is unverified
and must not describe the repeated panels as independent. If consent, configuration, or
non-content transport preflight is unavailable before the attempt begins, lock
all seats to the primary family and execute the complete schedule on that
homogeneous plan.

A mid-attempt dispatch or substrate failure, topology mismatch, unknown
required provenance observation, within-panel context reuse, or invalid provenance
artifact invalidates the whole attempt. Every completed panel becomes
diagnostic-only and must not enter any aggregate. The only result-producing
retry uses a new `attempt_id`, an empty aggregate, and restarts at paper 1 /
replicate 1 on one homogeneous plan. Never resume the failed attempt, mix
transports or substrates, or emit a profile or directional readout from an
incomplete, mixed-substrate, mixed-topology, or provenance-unresolved attempt.

### Phase 2: Full-tier decision-error profile

Map adjudicated and panel verdicts as follows: Accept/Minor Revision are the acceptable side; Major Revision/Reject are the reject side. With positive meaning acceptable:

| Metric | Meaning | Reporting boundary |
|---|---|---|
| Balanced accuracy | Mean of sensitivity on the two sides | Point estimate plus bootstrap interval |
| FNR | Acceptable-side papers judged Major/Reject (over-harsh) | Point estimate plus bootstrap interval |
| FPR | Reject-side papers judged Accept/Minor (too lenient) | Point estimate plus bootstrap interval |
| Exact four-label agreement | Exact verdict matches | Count and share, with target-set size |

Do not report AUC: there is no continuous rubric score. Do not infer an ordinal paper ranking from the four editorial labels.

For each dimension with adjudicated gold judgements, report a categorical agreement table and `annotated_n=<n>/<N>, missing=<N-n>`. With no annotated gold for a dimension, report `NOT COMPUTABLE`. Do not assign distances between categories, average the labels, or claim a gold-set-wide dimension result from a subset.

### Phase 2.5: Minor/Major boundary (both tiers)

When both `minor_revision` and `major_revision` gold examples exist, report raw counts:

| Gold \ predicted side | Accept + Minor | Major + Reject |
|---|---:|---:|
| Minor Revision | stayed minor-side | harsh crossing |
| Major Revision | lenient crossing | stayed major-side |

If either side is absent in a full-tier target set, report `NOT ESTIMABLE — target set lacks both sides of the Minor/Major boundary`. Never render an all-zero table as evidence of no confusion.

### Phase 2.6: Directional reporting boundary

The directional readout may report only:

- each paper's exact gold verdict, exact panel verdict, per-seat categorical criterion judgements, and `lenient` / `exact` / `harsh` direction;
- raw direction counts;
- the raw Minor/Major boundary cells; and
- raw low/med/high severity-grounding-risk counts from Phase 3.5.

It must not report balanced accuracy, FNR, FPR, AUC, confidence intervals, stability, per-dimension error rates, numeric baseline comparisons, or any measured-profile claim.

### Phase 3.5: Severity-miscalibration measurement (#215)

Decision-level error does not capture findings whose severity relies on an asserted field norm. Classify the grounding risk of each emitted weakness:

- **`high`**: severity depends on a field norm or core-result boundary, but the reviewer supplied no applicable external grounding;
- **`med`**: the reviewer named a possible standard but did not establish its applicability;
- **`low`**: severity does not depend on a field norm, or the applicable norm is externally grounded.

The classifier evaluates whether grounding was supplied, not whether its own model knowledge says the norm is correct. It **MUST NOT** guess norm-correctness from model memory. Measurement labels must be adjudicated against the separately maintained `evals/gold/field_norm_severity` asset; the pointer is an anti-circularity boundary, not permission to expose gold material to a review run. Full tier reports counts and target-set-local shares; directional tier reports raw counts only. This is separate from FNR/FPR and does not create a quality score.

### Phase 4: Outputs

The full-tier report uses this structure:

```text
# Empirical Target Profile for <Reviewer Instance>
calibration_status: PROFILE_MEASURED
application_status: NOT_WIRED_TO_LIVE_REVIEW
profile_id: <id>
target_match: <domain; article type; venue criteria/version; rubric version;
               review mode; execution_topology_sha256>
calibration_panel_provenance: <ordered normalized_manifest_sha256 values for
                               every replay-valid measurement panel>
Gold set: n=<N>
Runs per paper: <3|5>
Cross-model: <yes/no; configuration and fallback disclosure>

## Decision-error metrics
- Balanced accuracy: <estimate and interval>
- FNR (over-harsh): <estimate and interval>
- FPR (too lenient): <estimate and interval>
- Exact four-label agreement: <count>/<N>

## Per-dimension categorical agreement
| Dimension | Agreement/confusion counts | annotated_n | missing |
| ... |

## Minor/Major boundary
<raw cells or NOT ESTIMABLE with reason>

## Severity-grounding risk
<low/med/high counts and target-set-local shares>

## Scope and transport warning
This is a measured profile on the identified target set and exact execution
topology, not universal calibration. A mismatch in any target-match field restores NOT_CALIBRATED. The current run's replay-derived
execution_topology_sha256 is one such field and must match exactly.
```

The directional report uses this structure:

```text
# Directional Calibration Readout for <Reviewer Instance>
calibration_status: NOT_CALIBRATED
Tier: directional
Gold set: n=3
Runs per paper: 1

| Paper | Gold verdict | Panel verdict | Per-seat categorical judgements | Direction |
| ... |

<raw direction counts>
<raw Minor/Major boundary cells>
<raw severity-grounding-risk counts>

Interpretation: directional observations only; no error profile, calibration,
stability, score, ranking, or transport claim is available.
```

### Phase 5: Session disclosure

A subsequent live review currently begins with this header, including after a
directional or full-tier measurement run:

```text
> calibration_status: NOT_CALIBRATED
> application_status: NOT_WIRED_TO_LIVE_REVIEW
> Live profile application is not implemented in the current release; a
> candidate profile, profile identifier, or apparent target/topology match
> cannot upgrade this live review.
> Criterion judgements are evidence-anchored but have no measured error profile.
```

The following is a **future application example only** and is not emitted by
the current Schema 6 adapter:

```text
> calibration_status: PROFILE_MEASURED
> profile_id: <id>
> profile_artifact_sha256: <raw profile digest>
> execution_topology_sha256: <profile digest, exactly equal to current replay-derived digest>
> Decision errors were measured on <N> adjudicated papers matching <target>.
> This bounded profile is not universal calibration; any target mismatch restores
> NOT_CALIBRATED. See the attached uncertainty intervals and coverage counts.
```

The current disclosure cannot be hidden or upgraded. Full-tier measurement may
produce a candidate profile, but a candidate cannot be applied to a live review
until the closed profile schema and exact-match replay validator exist. A later
directional result never replaces a full-tier candidate; neither may be reused
outside its target identity.

## Ensembling and interpretation notes

- Full-tier repeats require within-panel context separation and use majority voting for the final categorical verdict. Cross-replicate context freshness is not mechanically verified, so reports label that limitation and never infer independent repeated error processes. Per-dimension categorical agreement is reported as counts, not averaged labels.
- Directional tier is an explicit one-run exception and cannot report stability.
- Same-family evaluation can understate error. Cross-model evaluation provides stronger evidence when consented and available, but does not prove evaluator independence or correctness.
- External studies can motivate hypotheses about leniency or harshness, but their numeric gaps must not be imported as correction factors, thresholds, or target-profile measurements.
- Neither tier predicts performance outside its target identity, detects every within-paper framing failure, or replaces human editorial judgement.

## Integration with existing modes

| Mode | Interaction |
|---|---|
| `full` | Ordinary full review remains criterion-bound and defaults to `NOT_CALIBRATED`; calibration runs a separate measurement workflow. |
| `re-review` | Emit `NOT_CALIBRATED`; re-review decision rules remain unchanged. |
| `quick` | Emit `NOT_CALIBRATED` and state that reduced scope has no measured live error profile. |
| `methodology-focus` | Emit `NOT_CALIBRATED`; candidate profile application is not wired. |
| `guided` | No calibration profile is inferred from dialogue. |

## References

- Lu, C. et al. (2026). Towards end-to-end automation of AI research. *Nature* 651, 914–919. Decision-level validation motivates reporting explicit class conventions and error profiles; its numeric results are not ARS thresholds.
- Ren et al. (2026). Evaluator-independence and verifiable-subset guidance. Target-set comparison is bounded evidence, not universal calibration.
- `shared/cross_model_verification.md` — calibration transport and consent rules.
- `quality_rubrics.md` — criterion-bound judgement contract.
