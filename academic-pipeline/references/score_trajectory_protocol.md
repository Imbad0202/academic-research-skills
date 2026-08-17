# Criterion Trajectory Protocol

**Compatibility filename**: `score_trajectory_protocol.md`
**Status**: design contract, not wired to a current machine producer
**Current runtime**: `pipeline_orchestrator_agent` performs the narrative,
criterion-local regression check below; it does not emit a trajectory object
**Future carrier**: Stage 3' Schema 6 field or a closed, validated sidecar

## Purpose

Tracks whether a revision improved, preserved, or weakened each named review criterion. The protocol compares evidence-anchored categorical judgements; it does not calculate rubric scores, numerical deltas, or a paper-quality ranking.

## Comparison rule

In a future typed implementation, compare the previous and current record for every applicable universal dimension:

| Field | Allowed values / content |
|---|---|
| previous_judgement | `EXCEEDS`, `MEETS`, `PARTLY_MEETS`, `DOES_NOT_MEET`, or `NOT_ASSESSED` |
| current_judgement | same enum |
| change | `IMPROVED`, `UNCHANGED`, `REGRESSED`, or `NOT_COMPARABLE` |
| previous_evidence | anchors supporting the earlier judgement |
| current_evidence | anchors supporting the current judgement |
| rationale | why the criterion is improved, unchanged, regressed, or not comparable |
| decision_bearing | whether the change affects the current recommendation, with a reason |

`change` is a reasoned, criterion-local comparison. Do not infer it by assigning hidden numbers to judgement labels. Use `NOT_COMPARABLE` when criteria, target venue, article type, manuscript scope, or available evidence changed materially.

## Regression handling

A `REGRESSED` item triggers a MANDATORY checkpoint when it is decision-bearing or when its evidence shows a new material weakness. Present:

1. the criterion and previous/current evidence;
2. the rationale for regression and its decision impact;
3. whether the change was an intentional trade-off; and
4. options to proceed with an explicit limitation, make a targeted fix, or restore the affected revision.

No fixed numerical tolerance determines regression. A presentation-only change must not be promoted into a substantive regression, and a newly exposed core flaw must not be softened because other criteria improved.

## Early stopping

Early stopping is eligible only when:

- no P0 issue remains;
- no unresolved decision-bearing regression remains;
- no applicable criterion has a substantive status change requiring another revision; and
- the author has no outstanding required action under the active revision contract.

The orchestrator must explain these conditions narratively. Label counts and reviewer agreement counts are not substitutes for that explanation.

## Proposed Stage 6 reporting (not current output)

```markdown
### Criterion Trajectory

| Dimension | Previous judgement | Current judgement | Change | Evidence and rationale | Decision bearing? |
|---|---|---|---|---|---|
| Originality | PARTLY_MEETS | MEETS | IMPROVED | <anchors and reason> | no |
| Methodological Rigor | MEETS | PARTLY_MEETS | REGRESSED | <anchors and reason> | yes |
| ... | ... | ... | ... | ... | ... |

Unresolved decision-bearing regressions: <list or none>
Early-stop eligible: <yes/no, with criterion-bound explanation>
```

## Compatibility

No current producer emits `criterion_trajectory`. A legacy `score_trajectory`
or experimental `criterion_trajectory` field may be preserved when reading an
older artifact, but it is historical metadata only: do not recompute it,
compare it with current judgements, map it to a decision, or emit it as a
current workflow result. Current checkpoints compare named criteria
narratively and use `NOT_COMPARABLE` whenever a valid comparison cannot be
made.

## Reference

This replaces the former score-delta adaptation of PaperOrchestra's refinement loop. The useful idea retained is explicit regression checking; numerical accept/revert thresholds are not adopted.
