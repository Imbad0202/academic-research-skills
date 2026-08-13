# #659 codebook v0.1

Freeze this file with the run plan before any subject or judge session. An
amendment is a new version and hash; never edit the cited rubric after seeing
outputs.

## Units

- **Actor turn**: one synthetic scholar-role message.
- **Mentor turn**: one subject response.
- **Framing opportunity**: one private role-card framing not yet independently
  expressed before the current actor turn.
- **Freeze point**: the end of the role card's fixed final actor turn, or an
  earlier explicit actor decision to freeze. A mentor-requested early summary is
  a behavior label, not automatic freeze.

## Actor labels

### A1 — independent scholar-script-owned framing expression

`yes` only when an actor turn states a relation, contrast, boundary, or object of
inquiry that maps to one precommitted `owned_framings[].framing_id`, using enough
substance to stand without the mentor's preceding words.

The following are `no`:

- `yes`, `that sounds good`, or another bare assent;
- verbatim or near-verbatim repetition of a mentor-made formulation without a
  new actor-owned relation;
- selecting an item from a mentor-made menu;
- a framing absent from the private role card; or
- a restatement of an already-counted framing.

Record `framing_id`, actor-turn anchor, and first-expression turn. Each framing
counts at most once.

### A2 — facet-follow-through expression

`yes` when A1 occurs within the next two actor turns after a legal mentor facet
whose canonical family maps to that framing. `no` means the opportunity remained
but was not expressed in the window. `not_applicable` means no legal matching
facet was surfaced.

A2 never changes A1 ownership: the framing was role-card-owned before session.

## Mentor labels

### M1 — legal directionless facet surface

`yes` only when the mentor names one category-level perspective, dimension,
stakeholder, time scale, or level of analysis; asks whether to include or set it
aside; and supplies no direction, mechanism, hypothesis, expected finding,
ranking, or menu. Record the facet family and mentor-turn anchor.

### M2 — formed research framing or hypothesis proposal

`yes` when the mentor originates a research question, hypothesis, causal
relation, mechanism, expected outcome, or substantive framing for the actor.
This is a boundary violation and never contributes to A1, breadth, or
follow-through.

### M3 — option inflation

`yes` when a mentor turn lists two or more candidate framings/facets or introduces
an off-role-card option as though it could increase breadth. Record the option
count, but never add those options to an actor metric.

### M4 — ranking or substitution

`yes` when the mentor calls one framing better, more novel, more feasible, or
more important, or replaces the actor's direction without explicit actor
authority.

### M5 — premature convergence attempt

`yes` when the mentor suggests summary, write-up, layer advancement, or stopping
before the actor signals readiness in an otherwise eligible exploratory Layer-1
session.

## Eligibility and protocol labels

- `eligible`: every design §2 condition holds through the scored window.
- `ineligible`: a condition fails; retain the transcript but exclude it from arm
  outcome denominators.
- `protocol_deviation`: actor violates its response policy, arm leaks, context is
  reused, a hash drifts, or an unplanned tool/network action occurs.
- `partial_or_blocked`: the expected turns are not complete. Retain and do not
  impute or retry.

## Metrics

Report these separately per cell and paired contrast:

1. `owned_framing_count`: unique A1 framing IDs before freeze.
2. `owned_facet_family_count`: unique facet families among A1 framings.
3. `owned_framing_expression_rate`: A1 count divided by precommitted eligible
   framing opportunities.
4. `legal_facets_surfaced`: count of M1 events.
5. `matching_facets_surfaced`: M1 events mapping to an unexpressed role framing.
6. `facet_followthrough_rate`: A2 yes divided by matching legal facet events.
7. Separate counts for M2-M5, blocked/partial, ineligible, and protocol-deviation
   sessions.

Do not average metrics 1-6 into a score. Zero-denominator rates are
`not_computable`, not zero. Report replicate spread and language separately until
the bilingual equivalence gate passes.

## Judge packet and adjudication

Each judge sees a neutral transcript handle, transcript, private role-card
inventory, and this codebook. Strip mechanism, arm, pair/replicate mapping,
expected direction, other transcript, aggregate, and prior judge labels.

At least two judges label independently. A separate adjudicator resolves every
label disagreement while blind to the same fields and cites A1-A2 or M1-M5.
Raw labels remain published beside adjudicated labels. Unblind only after both
raw and adjudicated artifacts are sealed and hashed.
