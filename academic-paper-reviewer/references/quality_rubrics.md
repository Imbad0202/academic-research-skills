# Criterion-Bound Judgement Rubric for Academic Paper Review

## Purpose

This rubric defines what each reviewer must examine and how to make the basis of a judgement inspectable. It does **not** provide a calibrated quality score, a paper-ranking scale, or an acceptance probability.

## Calibration status

Every review must declare one of these states:

- `NOT_CALIBRATED` — the required default. Use this whenever there is no empirical target profile matched to the current domain, article type, venue criteria, rubric version, reviewer/model configuration, and review mode.
- `PROFILE_MEASURED` — reserved for a package-level resolution backed by a replay-valid, hash-bound empirical target profile whose exact target fields and actual completed-panel `execution_topology_sha256` match. Producing or naming a calibration profile does not by itself authorize this status.

Individual reviewer seats always emit `NOT_CALIBRATED`, because the actual
completed-panel topology (including fallbacks) does not exist until all seats
finish. The current Schema 6 package adapter also remains
`NOT_CALIBRATED`; `PROFILE_MEASURED` must not appear in a live review package
until a closed profile schema and replay validator are shipped. This is an
honest implementation boundary, not evidence that calibration is impossible.

Never describe either state as proof that judgements are consistent or reproducible across papers, sessions, fields, venues, or model versions. A directional calibration readout is not an empirical target profile and leaves the status `NOT_CALIBRATED`.

## Required judgement form

For every applicable dimension, report:

| Field | Required content |
|---|---|
| Criterion source | The target venue criterion, reporting standard, article-type expectation, or reviewer configuration item being applied |
| Judgement | `EXCEEDS` / `MEETS` / `PARTLY_MEETS` / `DOES_NOT_MEET` / `NOT_ASSESSED` |
| Evidence anchors | Specific manuscript locations or bounded absence anchors |
| Rationale | How the cited evidence bears on the named criterion |
| Uncertainty or scope limit | Missing information, domain dependence, or reviewer limitation |
| Decision bearing? | Whether this judgement affects the recommendation, with a reason |

These labels are criterion-bound categories, not numbers. Do not convert them into points, weights, a total, a percentage, or a latent ranking. Do not map any total or count of labels mechanically to Accept, Minor Revision, Major Revision, or Reject.

Editorial recommendations instead follow the applicable contract or the qualitative, evidence-anchored rules in `editorial_decision_standards.md`. The recommendation must identify the particular unresolved criteria that make it appropriate.

---

## Dimension 1: Originality

Judge the claimed contribution against the paper's stated field, article type, and target venue. Examine whether the work identifies a defensible gap; distinguishes its theory, method, evidence, or application from relevant prior work; and avoids overstating novelty. Replication and boundary-testing studies can make an original contribution without introducing a new theory.

## Dimension 2: Methodological Rigor

Judge whether the design can answer the stated research question and whether execution and reporting support the inferences made. Apply paradigm- and design-appropriate criteria, including sampling, measurement, validity threats, analysis choices, uncertainty, transparency, and reproducibility where relevant. A standard applies only when its scope matches the paper.

## Dimension 3: Evidence Sufficiency

Judge whether each material claim has evidence of the right type, quality, relevance, and coverage for that claim and field. Consider counter-evidence, triangulation, source provenance, primary versus secondary evidence, and important omissions where relevant.

There is **no universal minimum source count and no universal peer-reviewed-source ratio**. Literature needs vary by field, article type, claim breadth, evidence base, and venue. A review may apply a numeric requirement only when an identified target venue, reporting standard, or protocol explicitly imposes it; cite that authority and do not generalize it beyond its scope.

## Dimension 4: Argument Coherence

Judge whether the problem, gap, research question, method, findings, and implications form a traceable argument. Identify unsupported logical transitions, conclusions that exceed the evidence, unresolved counterarguments, and contradictions. Do not confuse a familiar rhetorical structure with a sound argument.

## Dimension 5: Writing Quality

Judge whether the manuscript communicates its reasoning precisely enough to be reviewed and used. Separate presentation problems from substantive research quality, and do not penalize non-native phrasing when meaning remains clear. Identify only issues that materially affect interpretation, verification, or venue requirements; route copyediting-level points as minor issues.

## Dimension 6: Literature Integration

Judge whether the manuscript identifies and critically integrates the literature needed to establish its question, conceptual lineage, alternatives, and contribution. Coverage is assessed relative to the claims and field, not by a fixed number of references. Missing work should be named or bounded by a clearly described literature area whenever possible.

## Dimension 7: Significance and Impact

Judge whether the claimed theoretical, empirical, practical, or policy implications follow from the evidence and matter for the stated audience. Separate demonstrated significance from speculative future impact; do not require cross-field reach when the target criterion values a focused contribution.

---

## Narrative synthesis

The synthesis must preserve disagreements and non-compensatory weaknesses. A strong judgement on one criterion cannot numerically cancel a failure on another. Report:

1. criteria positively verified;
2. unresolved decision-bearing criteria, with evidence anchors;
3. repairability and the work needed to satisfy each criterion;
4. material uncertainty or reviewer-scope limitations; and
5. the resulting recommendation under the applicable decision standard.

If the evidence does not support a judgement, use `NOT_ASSESSED` or state the uncertainty. Do not manufacture precision by selecting a midpoint or averaging reviewers.
