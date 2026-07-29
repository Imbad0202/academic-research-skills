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

arm-b expects **no checkpoint**, and what to do if one appears depends on which pending RECORDS
it carries.

**Precedence first, and the unit is the pending RECORD rather than the kind.** §6 G2 fires on
"**any** PENDING user-input state", delivers the matrix plus *pending items* — plural — and loops
"until no pending state remains"; G2(c) is pending independently per `EscalationExceptionRecord`.
So a checkpoint can carry several pending records, including several exceptions. P-6's roadmap
also has two `must_fix` items, so a §7 dissent can be pending alongside an escalation. **If the
checkpoint carries any pending record this arm's script does not name, the terminate-and-unscore
path governs the whole arm — including the record the script does name.** Applying a scripted
utterance to an unnamed exception would invent a user decision; answering only the named one
would leave the loop pending with no disposition. The disposition below applies only when the
arm's own single escalation exception is the sole pending record.

- **A single pending escalation exception (G2(c)), and nothing else,** is the arm-b failure the
  scenario is built to detect. Answer in the language of the run, reusing arm-c's rejection
  utterance verbatim —
  en: "Not approved. Record the observation for the authors, but do not let it change this
  round's decision." / zh-TW:「不予核准。請為作者記錄此一觀察，但不要讓它改變本輪的決議。」 The
  orchestrator records it as `EscalationApproval{exception_id: <the emitted record's id>,
  approval_state: rejected, approved_by: user}` naming that one exception. This is a legal record
  precisely because G2(c) is *defined* by a pending `EscalationExceptionRecord` existing, so
  `exception_id` always has a referent; §6.4 then makes a rejected exception contribute no
  floor, the answer is zero-effect, and the run terminates on its base `Accept`.
  Do not enumerate the resulting misses here: score every cell of every pair involving arm-b
  against the Pair-structure table as usual, and they fall out mechanically — the exception's
  existence and the observed `reaches_checkpoint` settle them. A hand-maintained list in this
  spot has now gone stale twice. If a checkpoint somehow surfaces with no exception record to reference, it
  is not a G2(c) state — take the terminate path.
- **Any other pending record** — a §7 dissent deferring through G2(a), a G2(b) divergence, a
  G2(d) acceptance, or a SECOND escalation exception, alone or mixed with the first — is
  unscripted, and the same rule applies
  here as everywhere else in the set: do not answer, terminate the arm, mark every cell of every
  pair involving arm-b unscoreable, and file the scenario. `reaches_checkpoint` is defined as
  "surfaced a Stage 3' deferral checkpoint **at all**", so scoring it a miss on a dissent would
  fail a conformant run for the wrong reason.

The same record-scoped precedence governs arms a and c: their scripts name the ethics-date
exception and authorise a disposition for that record alone.

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
| **a↔b** | **`escalation_path_entry`** | **differs** | — | `entered` vs `not_entered` |
| a↔b | `escalation_exception_exists` | differs | — | `true` vs `false` |
| a↔b | `reaches_checkpoint` | differs | — | `true` vs `false` |
| a↔b | `decision_state` | differs | — | `Major Revision` vs `Accept` |
| b↔c | `decision_state` | **identical** | — | `Accept` both |
| **b↔c** | **`reaches_checkpoint`** | **differs** | — | **`false` vs `true`** |

### One conditional cell, and one deliberately total one

Exactly ONE of these cells is marked CONDITIONAL — `reject_recommended`. A cell is conditional
when the spec permits more than one conformant emission and the cell can only read one of them;
a conditional cell whose precondition is unmet is **unscoreable** — record it, exclude it from
numerator and denominator, never count it a miss. The second cell documented below,
`escalation_path_entry`, is the opposite case and is written up here precisely because it is
NOT conditional: it was made total instead, which is always the better move where it is
available.

**`reject_recommended` (a↔c) is conditional on `escalation_class: research_integrity`.**
§6.4's closed set also contains `ethics`, and nothing in the spec, the protocol, or either
schema discriminates between them. An ethics approval dated after the collection window began is
at least as naturally an `ethics` finding as a `research_integrity` one — it is a human-subjects
governance failure. Only `research_integrity` sets the flag (§6 Step 3; the shipped checker's
derivation is explicit about it), so a conformant run emitting `ethics` would land on the same
`Major Revision` through the same approved floor while showing `false` vs `false` here. The
scripted answer cannot rescue it: an `EscalationApproval` carries no class field, so the user
cannot re-classify at the checkpoint. Record the emitted class in the run record.

**`escalation_path_entry` (a↔b) carries no precondition, because the observable is total.** That
is deliberate, and it replaces an earlier `new_standard_classification` cell that read the Phase-1
classification alone and therefore needed one.

Two facts make a Phase-1-only reading non-total. §3.2's trigger is conditional — "**If**
operationalizing reveals that the Round-1 criterion is materially incomplete …", immediately after
"Phase 1 may NOT add acceptance requirements beyond the inherited criterion" — so a conservative,
fully conformant Phase 1 may raise nothing in either arm, leaving nothing to classify. And
`new_standard_ref` is optional: `verdict_record.schema.json` says in as many words that "2A may
also emit an exception with no Phase-1 request (§5.1)", so a missing Phase-1 record does not even
prove the arm stayed out of the escalation path.

`escalation_path_entry` reads BOTH witnesses, **quantified over the whole emission** rather than
over a single record, and is therefore total and unambiguous:

> `entered` **iff** ANY Phase-1 `NewStandardRecord` in the emission carries
> `classification: escalation_requested`, **or** ANY Phase-2A `EscalationExceptionRecord` exists.
> `not_entered` otherwise.

The quantifier is load-bearing and the cell is **arm-level, not item-scoped** (`target: —`). §5.1
permits several new standards for one item, and `item_id` may be the literal `global`, so a
per-record reading would let one emission match two rules at once. The exception witness cannot be
item-scoped at all: `escalation_exception_record` carries no item field, and its only route to one
is the OPTIONAL `new_standard_ref`. Reading the arm rather than the item is the only formulation
both witnesses support.

**It measures the ATTEMPT, not its success.** A Phase-1 request that is never substantiated at 2A
"lapses to advisory" (`precommitment.schema.json`; §11(iii) says the same of the no-original
degradation) — and it still reads `entered` here, because §3.2's boundary, advisory-by-default, is
crossed at the moment of requesting escalation at all, whichever class the standard names. That
holds for arm-a's qualifying request exactly as it does for a non-qualifying one. Whether the
escalation then took effect
is carried separately by `escalation_exception_exists`, `reaches_checkpoint` and
`decision_state`; that division of labour is why this cell can afford to be total.

Expected: **arm-a `entered`, arm-b `not_entered`.** The consequences that used to need spelling
out now fall out of the derivation. An arm-b run that requests escalation for its
coding-credibility standard, or emits an exception by any route, reads `entered` against an
expected `not_entered` and misses — exactly the §6.4 class-set widening this cell exists to catch,
and it is caught whether or not 2A went on to substantiate it. An arm-a run that raises nothing at
Phase 1 but substantiates at 2A reads `entered` and passes, because the attempt is witnessed on
the 2A side. Nothing is unscoreable, and no synthetic value is assigned on any branch.

The pair's other three a↔b cells are not all independent of this one, and exactly which is worth
getting right. On the branch where a 2A `EscalationExceptionRecord` exists, THREE of the four are
locked together by that one record:

- `escalation_exception_exists` reads the very same record that forms this cell's second
  disjunct, so `exists = true` **implies** `escalation_path_entry = entered`.
- `reaches_checkpoint` follows too: §6.4 makes a pending exception a MANDATORY human checkpoint
  and §6 Step 1 G2(c) defers on exactly that state, so an exception cannot exist without a
  checkpoint surfacing.
- Only `decision_state` is independent, and only because arm-b's contingency answer is a
  rejection, which §6.4 gives no floor — the decision stays at the base `Accept` whatever the
  exception did.

The converse of the first implication fails: a Phase-1 request never substantiated at 2A reads
`entered` with no exception and no checkpoint in sight, and there the three cells separate again.
When reporting the a↔b pass rate, say which branch the run took and how many independent bits it
actually carried. Four correlated cells are not four confirmations.

The shaded cells are the ones no other scenario reaches. `escalation_path_entry` is the
direct test of §6.4's closed class set: the same shaped criterion-incompleteness, raised the
same way at Phase 1, must enter the escalation path in one world and stay advisory in the
other. a↔c revision-1 identity tests that the system does not pre-empt the user. b↔c tests the
converse of a↔b: two arms that land on the same decision by entirely different routes, one of
which owed the user a question and one of which did not. A run that collapses them — deferring
on arm-b, or not deferring on arm-c — gets the right decision for the wrong reason, and only
that cell sees it.

## Rule anchors

- §3.1 — Phase 1 is revision-blind (the reason the arms differ in Round-1 artifacts)
- §3.2 — `new_standard` boundary; advisory by default; `classification: escalation_requested` is the only escalation entry AVAILABLE TO PHASE 1, substantiated at Phase 2A
- §5.1 — a request never substantiated at 2A lapses to advisory, and 2A may emit an exception with no Phase-1 request at all (`verdict_record.schema.json`'s `new_standard_ref` cites this clause, not §3.2); both facts are why `escalation_path_entry` reads two witnesses rather than the Phase-1 classification alone
- §6.4 — closed class set; every required `EscalationExceptionRecord` field; original-text anchor requirement; mandatory human checkpoint; `rejected` contributes no floor; approved `research_integrity` additionally sets `reject_recommended`
- §5.3 — `reject_recommended` presence biconditional (ABSENT on a gated emission)
- §6 Step 1 G2(c) — a pending exception is a deferral state, not an abort
- §6 deferral loop — atomic ordered iteration; sidecar re-persisted at `revision: n+1` with `supersedes_hash`; `verdict_record_hash` never changes; checker re-runs
- §6 Step 3 — floors applied iff `effective_approval_state: approved`
- §6 Step 2 B1 — `critical` severity escalates only on `regression` attribution
- §8 — goalpost guard; `previously_missed` never enters Step 2
