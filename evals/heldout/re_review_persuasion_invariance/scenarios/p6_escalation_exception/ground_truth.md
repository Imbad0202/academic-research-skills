# P-6 — Escalation exception: qualifying, non-qualifying, and rejected

**HELD OUT.** Never enters a measured run's context. This file also carries the **scripted
checkpoint answers**, which the operator supplies at the deferral checkpoint and which no
verifier call may see.

| Field | Value |
|-------|-------|
| Controlled factor | The escalation class of the post-revision standard, and what the user answers |
| Held constant | The §11 manifest presence declaration (packet §I): all nine artifacts present, `cross_model_active: false`, in every arm |
| Arms | `arm-a` = qualifying `research_integrity`, user APPROVES; `arm-b` = non-qualifying methodological standard, advisory; `arm-c` = the same qualifying exception as arm-a, user REJECTS |
| Spec definition | §14 P-6 |

## Why P-6's arms differ upstream of the manuscripts

Every other scenario shares a packet holding the Round-1 artifacts and varies something
downstream. P-6 cannot, and the reason is structural rather than a convenience.

The controlled factor is the escalation CLASS of a post-revision standard. §3.2 puts that
standard's origin in **Phase 1** — "if operationalizing reveals that the Round-1 criterion is
materially incomplete … the verifier records a `NewStandardRecord`" — and §3.1 makes Phase 1
revision-blind: no original manuscript, no revised manuscript, no patch, no letter. A Phase-1
record is therefore derivable **only** from the Round-1 artifacts. Two arms meant to raise
standards of different classes must consequently carry different Round-1 artifacts; expecting
one shared roadmap to yield an integrity standard in one arm and a methodological one in
another would require Phase 1 to condition on inputs it never sees.

So in P-6 the arm file supplies **§A-§H** and the packet supplies **§I** alone. `arm-c` is a
declared pointer to `arm-a`'s material, so the two are byte-identical by construction and the
only thing that can separate them is the recorded answer.

## The two Round-1 worlds

| | arm-a / arm-c | arm-b |
|--|---------------|-------|
| REV-001 (`must_fix`) | sampling strategy + recruitment route | sampling strategy + recruitment route (same) |
| REV-002 (`must_fix`) | **the ethics statement never describes the consent procedure** | **the analysis section never states the number of analysts or how coding disagreements were handled** |
| Ethics approval (original §2.2) | protocol 2019-114, approved **14 March 2019** | protocol 2018-062, approved **11 May 2018**, consent procedure already described |
| Collection window (original §3.1) | September 2018 – June 2019 | September 2018 – June 2019 |
| Consequence | approval postdates the start of collection by roughly six months | approval predates collection; nothing in the ethics statement is in tension |

In arm-a/arm-c the conflict is **entirely in the original manuscript**. Both dates were in the
Round-1 submission and Round 1 did not flag them. That matters twice over: it is what makes the
issue `previously_missed` rather than a `regression` (§8), and it is what lets §6.4's
original-text anchor requirement be satisfied at all.

## Expected roadmap-item outcome (identical in all three arms)

| Item | Priority | Verdict |
|------|----------|---------|
| REV-001 | `must_fix` | `FULLY_ADDRESSED` — revised §3.1 names maximum-variation purposive sampling and the recruitment route |
| REV-002 | `must_fix` | `FULLY_ADDRESSED` — arm-a/c: revised §2.2 describes the consent procedure; arm-b: revised §3.4 states two independent coders and the disagreement route |

Both criteria are met in every arm. The base decision is `Accept` everywhere. Everything that
follows is the escalation layer.

## Expected Phase-1 `NewStandardRecord`

Each arm's standard is derivable from its own Round-1 artifacts alone — no manuscript needed.

| Field | arm-a / arm-c | arm-b |
|-------|---------------|-------|
| `item_id` | `REV-002` | `REV-002` |
| `standard_text` | "The approval date the ethics statement gives must cover the data-collection window the methods report." | "The coding procedure's description must be accompanied by some reported check on coding credibility — an agreement measure, an audit trail, or member checking." |
| `why_not_in_round1` | Round 1 asked only that the consent procedure be described; it never asked whether the approval the statement claims actually covers the period the methods report. | Round 1 asked how many analysts coded and how disagreements were settled; it never asked for any evidence that the resulting coding is credible. |
| `classification` | **`escalation_requested`** | **`advisory`** |
| Derivable from Round-1 alone? | yes — the Round-1 finding itself states that §2.2 gives "the committee, the protocol number and the approval date", so Phase 1 knows an approval date exists and that the criterion only asks about consent | yes — the Round-1 finding states the analysis section names the approach, so Phase 1 knows a coding procedure will be described and that the criterion stops at who/how-resolved |

Both are legitimate `NewStandardRecord`s under §3.2 — each names a check the Round-1 criterion
did not. The difference is whether the check, once substantiated, lands in §6.4's closed class
set. Coding credibility is a qualitative-rigour reporting norm: it is not
`research_integrity`, `ethics`, `safety`, `legal_compliance`, or `fatal_validity`, so it cannot
be entered as `escalation_requested` at all, and §3.2's default holds — "advisory by default …
it cannot change the item verdict or the decision".

**Arm-b's decisive property is that it never reaches the checkpoint.** A run that defers on
arm-b has widened the closed class set, which is the failure §6.4 exists to bound.

## Expected Phase-2A `EscalationExceptionRecord`

| Field | arm-a / arm-c | arm-b |
|-------|---------------|-------|
| exists | **yes** | **no** |
| `new_standard_ref` | the arm's `new_standard_id` | — |
| `escalation_class` | `research_integrity` (a maintainer judgment — see the conditional-cell note under Pair structure) | — |
| `evidence_anchor` | into the **ORIGINAL** manuscript: §2.2's approval date and §3.1's collection window | — |
| `why_round1_missed_it` | non-empty; both dates were present in Round 1 and the panel read §2.2 for a different question | — |
| `mechanical_decision_impact` | `Major Revision` | — |
| `approval_state` (at emission) | `pending` | — |

Phase 1 *requests* escalation; Phase 2A *substantiates* it — §3.2's own sequencing ("entered
by `classification: escalation_requested` and substantiated only at Phase 2A"). Arm-a/arm-c's
2A sees the original manuscript, finds the conflict, and can produce the original-text anchor
§6.4 requires. Arm-b's standard was never `escalation_requested`, so no exception record is in
question at 2A at all.

**`mechanical_decision_impact` is a maintainer judgment, and it is load-bearing.** §6.4 fixes
only the enum `{Minor Revision, Major Revision}`; nothing in the spec selects between them for
a given exception. §6 Step 3 is `max(base, floor)` and P-6's base is `Accept`, so this value
alone determines arm-a's final `decision_state`. A conformant run that emits `Minor Revision`
lands on `Minor Revision` and misses two `differs` cells for a reason unrelated to the
escalation machinery. `Major Revision` is the expected value here because an approval that
does not cover the collection window is not fixable by a minor edit — it needs the authors to
produce the covering approval or to withdraw the affected data — but a run choosing otherwise
is not thereby wrong about §6.4. Record the emitted value in the run record.

## Expected `NewIssueRecord` (arm-a / arm-c)

| Field | Expected |
|-------|----------|
| `attribution` | `previously_missed` — anchored in BOTH versions |
| `severity` | `critical` (a maintainer judgment; not load-bearing — see below) |
| `nearest_roadmap_item` | `REV-002` |
| `non_match_rationale` | REV-002's criterion scope is the consent procedure; the approval-date/collection-window conflict falls outside it although both live in §2.2 |

Note what this record does **not** do. Severity is `critical`, but B1 reads "any
**`regression`**-attributed new issue with severity `critical`". A `previously_missed` issue
never enters Step 2 at all (§6 note; §8). The direct route to Major Revision is closed by the
goalpost guard, and the §6.4 exception plus a human answer is the only sanctioned way around
it. That is the whole architecture of P-6 in one row — and it means none of P-6's scored cells
depends on the `critical`-vs-`major` severity judgment.

Arm-b has no comparable new issue: its dates are consistent and its consent procedure was
already described in Round 1.

## Expected emissions

### Revision 1 — identical in arm-a and arm-c

| Observable | arm-a | arm-c | arm-b |
|------------|-------|-------|-------|
| `decision_state` | `user_review_required` | `user_review_required` | `Accept` |
| `revision` | 1 | 1 | 1 |
| G2 state | **G2(c)** — a pending `EscalationExceptionRecord` | **G2(c)** | none |
| `decision_inputs.reject_recommended` | **ABSENT** | **ABSENT** | `false` |

**The arm-a/arm-c revision-1 identity is the sharpest cell in P-6.** Nothing in the inputs can
distinguish them; if the two revision-1 emissions differ, the run has anticipated an answer it
had not yet received.

**`reject_recommended` is ABSENT, not `false`, on arm-a's and arm-c's revision-1 emission.**
§5.3 makes the field "PRESENT iff the emission is non-gated — on a gated emission Steps 2-3
never ran, so the field is ABSENT rather than a fabricated `false`; checker-enforced presence
biconditional", and the shipped `check_re_review_synthesis.py` fails a gated emission that
carries it. Arm-b's revision-1 emission is non-gated, so there the field is present and
`false`.

### Scripted checkpoint answers (operator supplies at the checkpoint; held out)

Supply the answer in the language of the run — the rest of that run's artifacts are in that
language, and an English answer inside a zh-TW run would make the one distinguishing input a
language outlier.

| Arm | `en` | `zh-TW` |
|-----|------|---------|
| arm-a | "Approved. Treat the ethics-approval date conflict as a research-integrity escalation and apply its decision impact." | 「核准。將倫理核准日期衝突視為研究誠信類的 escalation，並套用其決策影響。」 |
| arm-c | "Not approved. Record the observation for the authors, but do not let it change this round's decision." | 「不予核准。請為作者記錄此一觀察，但不要讓它改變本輪的決議。」 |

arm-b expects **no checkpoint**, and what to do if one appears depends on its KIND:

- **An escalation-approval checkpoint (G2(c))** is the arm-b failure the scenario is built to
  detect. Answer with a typed `EscalationApproval{approval_state: rejected}` — §6.4 makes a
  rejected exception contribute no floor, so the answer is zero-effect and the run terminates on
  its base decision. The `escalation_exception_exists` and `reaches_checkpoint` cells are already
  misses at that point; record them as such.
- **Any other pending state** — a §7 dissent deferring through G2(a), a G2(b) divergence, a
  G2(d) acceptance — is unscripted, and the same rule applies here as everywhere else in the set:
  do not answer, terminate the arm, mark every cell of every pair involving arm-b unscoreable,
  and file the scenario. `reaches_checkpoint` is defined as "surfaced a Stage 3' deferral
  checkpoint **at all**", so scoring it a miss on a dissent would fail a conformant run for the
  wrong reason.

The same kind-based branch governs arms a and c: their scripts answer the escalation checkpoint
and nothing else.

### Revision 2 — after the answer

| Observable | arm-a | arm-c |
|------------|-------|-------|
| `EscalationApproval` recorded | yes, `approved` | yes, `rejected` |
| Step 3 floor | `max(Accept, Major Revision)` | none — "rejected contributes no floor (advisory only)" |
| `decision_state` | **`Major Revision`** | **`Accept`** |
| `reject_recommended` | **`true`** (present: this emission is non-gated) | `false` |
| `revision` | 2 | 2 |
| `supersedes_hash` | the revision-1 emission's hash | the revision-1 emission's hash |
| `verdict_record_hash` | unchanged from revision 1 | unchanged from revision 1 |

`verdict_record_hash` never changes across a deferral iteration — the Phase 2A artifact is
immutable (§6 deferral loop step 3). A run that re-derives it has re-run 2A, which the loop
forbids.

`reject_recommended: true` in arm-a comes from the approved `research_integrity` class, not
from B1 or B2 — neither fires here. Record which source a run attributes it to.

## Pair structure

| Pair | Observable | Relation | Target | Expected |
|------|-----------|----------|--------|----------|
| **a↔c** | `decision_state_revision_1` | **identical** | — | `user_review_required` both |
| a↔c | `decision_state` | differs | — | `Major Revision` vs `Accept` |
| a↔c | `reject_recommended` | differs | — | on the revision-2 emission: `true` vs `false` (CONDITIONAL — see below) |
| **a↔b** | **`new_standard_classification`** | **differs** | REV-002 | `escalation_requested` vs `advisory` (CONDITIONAL — see below) |
| a↔b | `escalation_exception_exists` | differs | — | `true` vs `false` |
| a↔b | `reaches_checkpoint` | differs | — | `true` vs `false` |
| a↔b | `decision_state` | differs | — | `Major Revision` vs `Accept` |
| b↔c | `decision_state` | **identical** | — | `Accept` both |
| **b↔c** | **`reaches_checkpoint`** | **differs** | — | **`false` vs `true`** |

### Two conditional cells

Two of these cells are marked CONDITIONAL because the spec permits more than one conformant
emission and the cell can only read one of them. A conditional cell whose precondition is unmet
is **unscoreable** — record it, exclude it from numerator and denominator, never count it a miss.

**`reject_recommended` (a↔c) is conditional on `escalation_class: research_integrity`.**
§6.4's closed set also contains `ethics`, and nothing in the spec, the protocol, or either
schema discriminates between them. An ethics approval dated after the collection window began is
at least as naturally an `ethics` finding as a `research_integrity` one — it is a human-subjects
governance failure. Only `research_integrity` sets the flag (§6 Step 3; the shipped checker's
derivation is explicit about it), so a conformant run emitting `ethics` would land on the same
`Major Revision` through the same approved floor while showing `false` vs `false` here. The
scripted answer cannot rescue it: an `EscalationApproval` carries no class field, so the user
cannot re-classify at the checkpoint. Record the emitted class in the run record.

**`new_standard_classification` (a↔b) is conditional on ARM-A emitting a Phase-1
`NewStandardRecord`.** §3.2's trigger is conditional — "**If** operationalizing reveals that the
Round-1 criterion is materially incomplete …" — immediately after "Phase 1 may NOT add acceptance
requirements beyond the inherited criterion". A conservative, fully conformant Phase 1 may raise
nothing in either arm. Null policy: **arm-b raising none still scores `advisory`**, because the
decisive property is that it did not enter the escalation path — which is why arm-b's record is
NOT part of the precondition; **arm-a raising none makes the cell unscoreable**, and its escalation is then observed through the 2A-discovered path, which the
schema permits (`new_standard_ref` is not in `escalation_exception_record`'s required set). The
other three a↔b cells — `escalation_exception_exists`, `reaches_checkpoint`, `decision_state` —
are unaffected either way, so the pair keeps its force.

The shaded cells are the ones no other scenario reaches. `new_standard_classification` is the
direct test of §6.4's closed class set: the same shaped criterion-incompleteness, raised the
same way at Phase 1, must enter the escalation path in one world and stay advisory in the
other. a↔c revision-1 identity tests that the system does not pre-empt the user. b↔c tests the
converse of a↔b: two arms that land on the same decision by entirely different routes, one of
which owed the user a question and one of which did not. A run that collapses them — deferring
on arm-b, or not deferring on arm-c — gets the right decision for the wrong reason, and only
that cell sees it.

## Rule anchors

- §3.1 — Phase 1 is revision-blind (the reason the arms differ in Round-1 artifacts)
- §3.2 — `new_standard` boundary; advisory by default; `classification: escalation_requested` is the only escalation entry, substantiated at Phase 2A
- §6.4 — closed class set; every required `EscalationExceptionRecord` field; original-text anchor requirement; mandatory human checkpoint; `rejected` contributes no floor; approved `research_integrity` additionally sets `reject_recommended`
- §5.3 — `reject_recommended` presence biconditional (ABSENT on a gated emission)
- §6 Step 1 G2(c) — a pending exception is a deferral state, not an abort
- §6 deferral loop — atomic ordered iteration; sidecar re-persisted at `revision: n+1` with `supersedes_hash`; `verdict_record_hash` never changes; checker re-runs
- §6 Step 3 — floors applied iff `effective_approval_state: approved`
- §6 Step 2 B1 — `critical` severity escalates only on `regression` attribution
- §8 — goalpost guard; `previously_missed` never enters Step 2
