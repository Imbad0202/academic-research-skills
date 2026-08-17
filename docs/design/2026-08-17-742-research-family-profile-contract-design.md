# #742 — Research-family workflow profile contract and progressive-disclosure usability protocol

Status: DESIGN FREEZE for the `research-workflow-profile/1.0` contract, the
field-general fallback, and the preregistered usability protocol. This document
authorizes no workflow change, no new prompt on the simple path, and no
default-on behavior. No schema file, validator, or runtime consumer ships with
this freeze; they are implementation work bounded by this design. All usability
evidence is `NOT_RUN`.

Parent epic: #741. Roadmap: `docs/ROADMAP-v3.20.1-v3.22.md` Phase 1.
Downstream consumers: #743 (branch ledger), #744 (alternative register),
#745 (evidence matrix).

## 1. Scope and claims boundary

A profile declares **stage applicability and vocabulary** for one research
family. It never supplies a quality verdict, a venue-fit judgment, an
acceptance prediction, or an evidence hierarchy claim about any concrete
manuscript. Conformance to this contract establishes only that a declaration
is well-formed, user-confirmed, and versioned; it does not establish that the
declaration fits the user's actual research, that the listed stages are
sufficient for the field, or that any workflow built on the profile improves
research outcomes.

ARS must not infer a profile from manuscript quality, citation patterns, or
disciplinary stereotypes. The only lawful profile sources are explicit user
selection, explicit user confirmation of a proposed profile, and the automatic
field-general fallback (§4) — and the fallback is itself visible state, never a
silent guess.

## 2. Shared stage and task-family vocabulary

The profile contract and the #745 stage capability matrix consume one closed
task-family id list, frozen here so the two surfaces cannot drift apart:

| task_family_id | Pipeline anchor |
|---|---|
| `rq_formation` | deep-research socratic / RQ Brief |
| `retrieval` | bibliography / corpus intake |
| `methodology` | research_architect blueprint |
| `synthesis` | synthesis_agent / INSIGHT collection |
| `drafting` | draft_writer / report_compiler |
| `integrity_check` | Stage 2.5 / 4.5 gates |
| `review` | academic-paper-reviewer panel |
| `revision` | revision / revision-coach |
| `finalization` | format-convert / Stage 5–6 |

Additions require a contract version bump in both consumers. A profile may
mark any id `applicable`, `intentionally_absent` (with a reason), or
`unresolved_fit`; an id it does not mention is `unresolved_fit`, never
implicitly applicable — silence must not widen a workflow.

## 3. Contract: `research-workflow-profile/1.0`

One profile is one JSON document. Frozen field set:

| Field | Req | Semantics |
|---|---|---|
| `schema_version` | ✓ | const `research-workflow-profile/1.0` |
| `profile_id` | ✓ | stable slug, e.g. `quantitative_empirical` |
| `profile_version` | ✓ | semver of this profile's content |
| `research_family` | ✓ | one of the seven test strata (§5) or `field_general` |
| `display_name` | ✓ | short human label, en + zh-TW |
| `stage_map` | ✓ | per §2: each named `task_family_id` → `applicable` \| `intentionally_absent` + `reason` \| `unresolved_fit` |
| `alternative_categories` | ✓ | closed list of admissible alternative kinds for #743/#744 (e.g. `rival_theory`, `alternative_design`, `alternative_measurement`, `alternative_model`, `disconfirming_query`, `boundary_condition`); may be empty for a family where the category question is unresolved |
| `branch_budget` | ✓ | max live (non-parked, non-archived) branches any surface may show before requiring a merge/park/archive decision; integer ≥ 1 |
| `overflow_behavior` | ✓ | const `ask_merge_park_archive` — the only lawful response to a budget overflow is asking the user; auto-pruning is forbidden |
| `evidence_overlays` | — | family-specific evidence/reporting vocabulary pointers (e.g. PRISMA for evidence synthesis); pointers only, never a hierarchy ranking claim |
| `authority_points` | ✓ | stages at which human/institutional authority is required (IRB/ethics determination, consent, co-author sign-off); may be empty only for `field_general` |
| `known_exclusions` | ✓ | work this profile is known NOT to fit |
| `unresolved_fit_note` | ✓ | free text naming what remains unvalidated about the profile itself |
| `provenance` | ✓ | `{source: shipped_default \| user_authored \| user_modified, last_reviewed_at: date}` |

Closed shape: unknown fields are refused (`additionalProperties: false` when
the schema ships). A profile document carries **no** per-project state — no
selected-by, no branches, no manuscript pointers. Runtime selection state
lives in the selection receipt (§6), so profiles stay shareable and diffable.

Vocabulary-only rule, restated as an invariant: nothing in a profile may map
any manuscript property to a score, verdict, ranking, or pass/fail state.
A field whose semantics would require such a mapping is out of contract.

## 4. Field-general fallback

One shipped profile, `field_general` @ `research-workflow-profile/1.0`, is the
mandatory landing state for unsupported, hybrid, ambiguous, or undeclared
work. It preserves exactly four things — author decision authority, human/AI
provenance, uncertainty disclosure, and optional (never mandatory)
alternatives — and pretends to know nothing field-specific:

- every `task_family_id` is `unresolved_fit` except `integrity_check`
  (`applicable`: the deterministic gates are field-general by construction);
- `alternative_categories` is empty;
- `branch_budget` is 3 (the smallest value that still permits one active line
  plus two parked alternatives; see §7 rationale);
- `authority_points` is empty — absence of a declared authority point in the
  fallback means "unknown", and consumers must treat unknown as
  "ask the user", never as "not required".

Selecting no profile ≡ selecting `field_general`. The fallback state is shown
to the user whenever it is active; a session must never behave as if a family
profile were selected when only the fallback is.

## 5. Initial family strata

Seven candidate strata (from #741): quantitative empirical, qualitative,
theoretical/conceptual, interpretive/humanities, evidence synthesis,
computational, clinical/human-subjects. These are **test strata for the
usability protocol**, not a discipline taxonomy and not a coverage claim.
Only profiles that pass authoring review ship; a stratum without a shipped
profile simply falls back per §4. The initial shipped set may be smaller than
seven; it must include at least one non-empirical family before any usability
run (protocol requirement, §7).

## 6. Selection, confirmation, correction

- Selection is recorded in a **selection receipt** (runtime state, outside the
  profile document): profile id + version, `selected_by: user_explicit |
  user_confirmed_proposal | fallback_automatic`, timestamp, and the
  correction chain (see next point).
- Correction is a first-class operation at any time and never restarts the
  project: the receipt appends the new selection, prior stage outputs are
  marked `profile_context_changed` (visible, advisory) rather than invalidated,
  and nothing scholar-owned is discarded.
- ARS may *propose* a profile only when the user has described their research
  in their own words, and the proposal must present the fallback as an equally
  available choice. Declining a proposal lands on the fallback, silently
  costs nothing, and is never re-asked within the same stage.

## 7. Complexity budget (consumed by #743/#744)

The profile is the single carrier of branch-budget policy so that no surface
invents its own: `branch_budget` + `overflow_behavior` bind every #743/#744
surface. Frozen interaction rules, restated from the roadmap as contract
obligations on future consumers:

- the simple path receives **zero** new mandatory prompts from this contract;
- rich state may appear only at consequential or hard-to-reverse decisions;
- every added interaction offers `skip`, `off`, and reset-to-simple-path
  without discarding scholar-owned work;
- default views are one compact summary; graphs are progressively disclosed.

Budget rationale: 3 for the fallback (one active + two parked) errs small on
purpose — raising a budget is an evidence-gated profile edit; shipping a large
default and relying on users to cope is exactly the burden failure mode the
usability protocol exists to catch.

## 8. Preregistered usability protocol (NOT_RUN)

Design: paired comparison of (A) the current simple path against (B)
profile-aware progressive disclosure, on matched task sets, stratified by
research family × experience (novice / experienced), with each stratum
evaluated separately. Requires human participants; nothing in this repository
simulates them, and no ARS agent may act as a participant or judge.

Outcomes, reported separately and never collapsed into one score:
task completion, unnecessary-prompt count, time on task, abandonment,
perceived control, wrong-profile recovery (detection + correction success),
and independently judged decision usefulness.

Preregistered budgets and guardrails (v0.1 — amendable only before any
participant session, by recorded amendment in this document's history):

| Guardrail | Frozen threshold |
|---|---|
| Max added interactions (B vs A) | ≤ 2 added prompts per consequential decision; 0 added on the simple path |
| Time non-inferiority margin | B ≤ A × 1.10 per stratum (task time) |
| Abandonment non-inferiority | B ≤ A + 5 percentage points per stratum |
| Completion non-inferiority | B ≥ A − 5 percentage points per stratum |
| Perceived control | B not worse than A at the stratum level on the preregistered instrument |
| Stratum rule | a failed stratum fails the gate; no rescue by pooled average |
| Family scope rule | evidence in one family × version authorizes only that family × version |

Minimum evidence before ANY default-on proposal (restating the issue's
acceptance): ≥ 3 materially different families with usability evidence, at
least one non-empirical; no material safety/authority regression hidden by an
average; mixed evidence or materially risen burden ⇒ default unchanged.

## 9. Evidence-state registration (#745 hook)

On the day a #745 matrix scaffold exists, this mechanism registers as:
mechanism `research_workflow_profile` @ contract `research-workflow-profile/1.0`,
status `DESIGNED`, behavioral evidence `NOT_RUN`, claim ceiling: "a versioned,
user-confirmed declaration exists; no usability or outcome claim". The #743
alpha's own registration requirement (roadmap Phase 2) is unaffected.

## 10. Acceptance mapping

| Issue #742 acceptance item | Where satisfied |
|---|---|
| user-confirmed, correctable selection | §6 |
| explicit fallback, no silent inference | §1, §4 |
| ≥ 3 families incl. one non-empirical with usability evidence | §8 (protocol frozen; evidence NOT_RUN) |
| no family-level regression hidden by average | §8 stratum rule |
| simple tasks never open branch surfaces | §7 |
| mixed evidence ⇒ default unchanged | §8 |

The three evidence-dependent boxes stay unchecked until the protocol runs;
this freeze makes them *checkable*, not checked.

## 11. Non-goals

No exhaustive discipline taxonomy; no journal-acceptance prediction; no claim
that shipped profiles cover academic research; no venue criteria (that is
#575/#684); no AI ranking of author-owned branches; no default-on change of
any kind from this document.

## 12. Deferred

Schema + validator + shipped profile files (implementation PR bounded by this
freeze); zh-TW display-name authoring; the usability instrument for perceived
control (chosen at protocol execution planning, before recruitment, as a
preregistered amendment).
