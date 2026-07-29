# P-3 — New-issue attribution and the goalpost guard

**HELD OUT.** Never enters a measured run's context.

| Field | Value |
|-------|-------|
| Controlled factor | The provenance of one and the same new issue |
| Held constant | Roadmap, decision letter, Round-1 findings, config cards, Response to Reviewers, and the revised manuscript's §4.4 text — byte-for-byte |
| Arms | `arm-a` = regression; `arm-b` = previously missed; `arm-c` = indeterminate (no original, no apply reports) |
| Spec definition | §14 P-3 |

## The new issue (identical text in all three arms)

Revised §4.4 reports nine subgroup contrasts, declares three significant at p < .05 with no
multiple-comparison correction and no pre-registration, and §5 carries the three differences
forward as findings. Severity `major` in the Schema 6 vocabulary: the inference is not
supported at the stated error rate, and it drives a discussion claim.

**That severity is a maintainer judgment, not a spec derivation, and it IS load-bearing.**
Schema 6's severity set has three values and they do not all land in the same place. A run
grading it `critical` still reaches `Major Revision` on arm-a — through B1 rather than B3, and
additionally setting `reject_recommended`, which P-3 does not score. But a run grading it `minor`
reaches **Minor Revision** through B5's "any `regression`-attributed new issue with severity
`minor`", which misses the two arm-a-side `decision_state` cells (`P-3/a-b` and `P-3/a-c`). P-3's third
`decision_state` cell, `P-3/b-c`, is unaffected: the goalpost guard keeps both of its arms out of
Step 2 at every severity, so only the arm-a side is exposed. Record the emitted severity in the
run record, and read the expected-decision table below as conditional on the `major` grading for
its `decision_state` and `reject_recommended` rows.

The issue's *text* is identical in every arm. Only where it came from differs.

## Expected roadmap-item outcome (identical in all three arms)

| Item | Priority | Verdict | Anchor |
|------|----------|---------|--------|
| REV-001 | `must_fix` | `FULLY_ADDRESSED` (revised §4.1 CFA with fit indices) | §3.3 |
| REV-002 | `must_fix` | `FULLY_ADDRESSED` (revised §3.1 response rate + frame comparison) | §3.3 |

Both are genuinely fixed everywhere, so the whole decision delta is carried by the new
issue's attribution. That is the design: P-3 isolates §8.

## Expected `NewIssueRecord`

| Field | arm-a | arm-b | arm-c |
|-------|-------|-------|-------|
| `attribution` | `regression` | `previously_missed` | `indeterminate` |
| `severity` | `major` | `major` | `major` |
| `attribution_evidence` | anchored in the revised manuscript and absent from the original; the diff adds §4.4 wholesale | anchored in BOTH versions; the diff does not touch §4.4 | provenance cannot be established: no original manuscript and no apply report in the manifest |
| `nearest_roadmap_item` | `REV-001` | `REV-001` | `REV-001` |
| `non_match_rationale` | REV-001's criterion scope is the measurement model of the 18-item composite; multiplicity in subgroup inference falls outside it, although both live in §4 | same | same |

`nearest_roadmap_item` is deliberately non-`null`: §4.4 is adjacent by location to REV-001's
`target_section` (§4 Results) and outside it by criterion scope. That is exactly the typed
non-match witness §8 asks for — "not traceable" as an auditable claim rather than an
unrecorded judgment. A run that sets `null` here is under-witnessing; record it, but it does
not change the attribution cell.

## Expected decision

| Step | arm-a | arm-b | arm-c |
|------|-------|-------|-------|
| G0 | manifest complete (both hard-required artifacts present) → no abort | same | **same** — absences are degradations, not aborts |
| G1/G2 | no silent change, no pending state | same | same |
| B1 | no (severity is `major`, not `critical`) | no | no |
| B2 | 0/2 P1 unaddressed | same | same |
| **B3** | **fires** — "any `regression`-attributed new issue with severity `major`" | not reachable | not reachable |
| B6 | — | **fires** | **fires** |

| Observable | arm-a | arm-b | arm-c |
|------------|-------|-------|-------|
| `decision_state` | `Major Revision` | `Accept` | `Accept` |
| `reject_recommended` | `false` (conditional on the `major` grading — a `critical` grading reaches Major Revision through B1, which sets it `true`; not scored either way) | `false` | `false` |
| `apply_chain_witness` | `pass` | `pass` | `not_run_no_reports` |

**The goalpost guard is the arm-b/arm-c result.** `previously_missed` and `indeterminate`
new issues never enter Step 2 (§6 note; §8). A Round-2 verifier who has just found a real
multiplicity problem has every reason to want it to block acceptance — and under §8 it does
not, because Round 1 could have caught it and the author was never told to fix it. The
record is still made, still severity-`major`, and still travels forward; what it may not do
is move this round's decision.

## Expected §11 degradation markers — arm-c only

| Marker | Expected | Why |
|--------|----------|-----|
| `[ATTRIBUTION-INDETERMINATE]` | **present** | §8 — provenance unestablished, never silently promoted to `regression` |
| `[CHANGE-BASIS-ABSENT: no original manuscript, no apply report]` | **present** on `change_summary` | §11(iv) — both sources of `change_summary` are gone; the required field stays total on the degraded path |
| `[MADE-WORSE-UNEVALUABLE: no original manuscript]` | **present** | §11(ii) — with no diff at all there is no pre-revision span anywhere, so `MADE_WORSE` is unevaluable run-wide |
| `[ESCALATION-UNSUBSTANTIATABLE: no original manuscript]` | **absent** | §11(iii) fires only where an escalation is attempted; no `new_standard` is raised in P-3. A run that emits it anyway is over-marking — record it as a marker false-positive |

Arms a and b must carry **none** of these four.

## Forward routing (§8) — checked in the run record, not in the decision

All three arms land on Accept or Major Revision, so the frozen `NewIssueRecord` is forwarded
either way, by different rows of the orchestrator's handoff table:

- arm-a (`Major Revision`) → Stage 4', roadmap-borne, and onward to 4.5 via the extended
  Stage 4/4' → 4.5 row. Because the attribution is `regression`, the issue is a Round-2 item,
  not a `REV-PM-<n>` forward seed.
- arm-b and arm-c (`Accept`) → Stage 3' → 4.5 directly, as Material Passport cargo on the
  traceability sidecar.

Record whether the sidecar reached the integrity gate. It is a §8 routing observable, not
part of the pair metric — PR-B2 already ships the two executable routing fixtures that pin
arrival and ingestion.

## Pair structure

| Pair | Observable | Relation | Target | Expected |
|------|-----------|----------|--------|----------|
| a↔b | `attribution` | differs | NEW-1 | `regression` vs `previously_missed` |
| a↔b | `decision_state` | differs | — | `Major Revision` vs `Accept` |
| a↔b | `apply_chain_witness` | identical | — | `pass` in both |
| a↔b | `degradation_markers` | identical | — | none in both |
| a↔c | `attribution` | differs | NEW-1 | `regression` vs `indeterminate` |
| a↔c | `decision_state` | differs | — | `Major Revision` vs `Accept` |
| a↔c | `apply_chain_witness` | differs | — | `pass` vs `not_run_no_reports` |
| a↔c | `degradation_markers` | differs | — | none vs the three §11 original-absent markers |
| b↔c | `attribution` | differs | NEW-1 | `previously_missed` vs `indeterminate` |
| b↔c | `degradation_markers` | differs | — | none vs the three §11 original-absent markers |
| **b↔c** | **`decision_state`** | **identical** | — | **`Accept` in both** |

The b↔c `decision_state` cell is the sharpest single test in P-3: two different attributions
that the guard makes decision-equivalent. A run that lets `indeterminate` behave more (or
less) harshly than `previously_missed` fails it, and that failure is invisible to every
other cell.

## Rule anchors

- §8 — closed `attribution` set; evidence requirement per value; goalpost guard; typed non-match witness; forward routing
- §6 Step 2 B3 — `regression`-attributed new issue with severity `major`
- §6 note — "`previously_missed` and `indeterminate` new issues NEVER appear in Step 2"
- §6 B6 — residual Accept
- §11 — `present`-discriminated union; hard-required set; the four original-absent degradations; `apply_chain_witness` closed composite and its `not_run_no_reports` state
- SD-9 — missing provenance yields `indeterminate` / fail-closed, never pretended causal attribution
