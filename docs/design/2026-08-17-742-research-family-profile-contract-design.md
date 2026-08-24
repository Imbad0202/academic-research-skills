# #742 — Research-family workflow profile contract and progressive-disclosure usability protocol

Status: DESIGN FREEZE for the `research-workflow-profile/1.0` contract, the
field-general fallback, and the preregistered usability protocol. This document
authorizes no workflow change, no new prompt on the simple path, and no
default-on behavior. At the 2026-08-17 freeze, no schema file, validator, or
runtime consumer shipped; they were implementation work bounded by this
design. All usability evidence was and remains `NOT_RUN`.

Implementation status (2026-08-24): the bounded implementation now ships the
two closed schemas under `shared/contracts/research_workflow/`, the canonical
`field_general` profile, and the explicit selection/correction runtime at
`scripts/research_workflow_profile.py`. This does not add a pipeline hook or
change a default. Every usability and research-outcome claim remains `NOT_RUN`.

Parent epic: #741. Roadmap: `docs/ROADMAP-v3.20.1-v3.22.md` Phase 1.
Downstream consumers: #743 (branch ledger), #744 (alternative register),
#745 (evidence matrix).

## 1. Scope and claims boundary

A profile declares **stage applicability and vocabulary** for one research
family. It never supplies a quality verdict, a venue-fit judgment, an
acceptance prediction, or an evidence hierarchy claim about any concrete
manuscript. Conformance to this contract establishes only that a declaration
is well-formed, versioned, and either user-confirmed or the visibly active
fallback; it does not establish that the declaration fits the user's actual
research, that the listed stages are sufficient for the field, or that any
workflow built on the profile improves research outcomes.

ARS must not infer a profile from manuscript quality, citation patterns, or
disciplinary stereotypes. The only lawful profile sources are explicit user
selection, explicit user confirmation of a proposed profile, and the automatic
field-general fallback (§4) — and the fallback is itself visible state, never a
silent guess.

## 2. Shared stage and task-family vocabulary

The profile contract and the #745 stage capability matrix consume one closed
task-family id list. A task family is the **evidence-attachment grain**:
deliberately coarser than checkpoint grain, anchored to named ARS pipeline
stages by the frozen mapping below so neither consumer can re-derive its own
stage boundaries. Both columns are frozen; changing either requires a
contract version bump in both consumers in the same commit.

| task_family_id | pipeline_stage_ids (frozen mapping) | Pipeline anchor |
|---|---|---|
| `rq_formation` | `stage_0_socratic` | deep-research socratic / RQ Brief |
| `retrieval` | `stage_1_corpus` | bibliography / corpus intake |
| `methodology` | `stage_1_blueprint` | research_architect blueprint |
| `synthesis` | `stage_1_synthesis` | synthesis_agent / INSIGHT collection |
| `drafting` | `stage_2_draft` | draft_writer / report_compiler |
| `integrity_check` | `stage_2_5_gate`, `stage_4_5_gate` | Stage 2.5 / 4.5 gates |
| `review` | `stage_3_review`, `stage_3p_re_review` | reviewer panel / re-review |
| `revision` | `stage_4_revision` | revision / revision-coach |
| `finalization` | `stage_5_final`, `stage_6_record` | format-convert / Process Record |

`integrity_check` spans both gates and `finalization` spans Stages 5-6 by
design: profile-level applicability does not vary between those checkpoints.
The shipped `stage-capability-matrix/1.0` row shape carries only the task
family; a #745 row that needs checkpoint grain names the `pipeline_stage_id`
in its row text today, and a dedicated field is a coordinated matrix version
bump when checkpoint grain becomes load-bearing. Theory choice, measurement, analysis, and
interpretation are NOT stages in this vocabulary — they are alternative
*categories* carried by #744 within the stages above; adding them here as
stages would smuggle in the universal research ontology the epic rejects.

A profile may mark any `task_family_id` `applicable`, `intentionally_absent`
(with a reason), or `unresolved_fit`; an id it does not mention is
`unresolved_fit`, never implicitly applicable — silence must not widen a
workflow.

## 3. Contract: `research-workflow-profile/1.0`

One profile is one immutable JSON document per `profile_version`: any content
change is a new version; re-publishing different bytes under an existing
version is a contract violation. Frozen field set, with deterministic shapes:

| Field | Req | Shape (deterministic) |
|---|---|---|
| `schema_version` | ✓ | const `research-workflow-profile/1.0` |
| `profile_id` | ✓ | stable slug string, e.g. `quantitative_empirical` |
| `profile_version` | ✓ | semver string of this profile's content |
| `research_family` | ✓ | enum: the seven §5 strata + `field_general` (deliberate v1 restriction, see below) |
| `declared_family_label` | — | free-text family self-description for `user_authored` profiles whose identity the v1 enum cannot express; display-only, never dispatched on |
| `display_name` | ✓ | object `{en: string, zh_TW: string}` |
| `stage_map` | ✓ | object keyed by §2 `task_family_id`; each value is `{state: "applicable"}` \| `{state: "intentionally_absent", reason: string}` \| `{state: "unresolved_fit"}`; unknown keys refused |
| `alternative_categories` | ✓ | object `{state: "declared" \| "unresolved", categories: [...]}` — `categories` drawn from the closed v1 enum `{rival_theory, alternative_design, alternative_measurement, alternative_model, disconfirming_query, boundary_condition}`; `unresolved` requires an empty list; `declared` + empty list is the lawful way to say "no alternative categories apply to this family" |
| `branch_budget` | ✓ | integer ≥ 1; counting semantics in §7 |
| `overflow_behavior` | ✓ | const `ask_merge_park_archive` — the only lawful response to a budget overflow is asking the user; auto-pruning is forbidden, and the overflowing candidate is retained pending the user's disposition, never dropped |
| `evidence_overlays` | — | list of `{name: string, pointer: string}` (e.g. PRISMA for evidence synthesis); pointers only, never a hierarchy ranking claim |
| `authority_points` | ✓ | list of `{task_family: §2 id, authority: string, requirement: string}` (IRB/ethics determination, consent, co-author sign-off); may be empty only when `research_family` is `field_general`, and for EVERY such profile — shipped or `user_authored` — empty deterministically means "unknown; ask the user" (§4), never "not required" |
| `known_exclusions` | ✓ | list of non-empty strings: work this profile is known NOT to fit |
| `unresolved_fit_note` | ✓ | non-empty string naming what remains unvalidated about the profile itself |
| `provenance` | ✓ | `{source: "shipped_default" \| "user_authored" \| "user_modified", source_pointer: string, last_reviewed_at: ISO date, freshness_state: "current" \| "stale" \| "unverified"}` — `source_pointer` names where the profile content came from (a shipped file path, or the user's own declaration); shipped defaults are `current` at release and become `stale` by release policy, never silently |
| `content_sha256` | ✓ | SHA-256 over the profile document in JSON Canonical Form with this field set to the 64-zero placeholder (the Schema 9 `reset_boundary` hashing convention). This is a canonical-content digest, not the raw-file digest (the stored file carries the finalized hash, not zeros). Verification is a fixed procedure: a consumer rejects non-canonically-stored profile files, replaces this field with the placeholder, recomputes, and compares the result against both the embedded value and any receipt; a mismatch anywhere is a refusal |

Closed shape: unknown fields are refused (`additionalProperties: false` when
the schema ships). A profile document carries **no** per-project state — no
selected-by, no branches, no manuscript pointers. Runtime selection state
lives in the selection receipt (§6), so profiles stay shareable and diffable.

`research_family` enum note (v1 restriction, intentional): the seven strata
double as the only nameable families in v1. This is a contract convenience,
not a coverage claim — a `user_authored` profile for an unlisted family
declares the nearest stratum or `field_general` plus `declared_family_label`,
and the enum widens by ordinary contract versioning when a family earns its
own shipped profile.

Vocabulary-only rule, restated as an invariant: nothing in a profile may map
any manuscript property to a score, verdict, ranking, or pass/fail state.
A field whose semantics would require such a mapping is out of contract.

## 4. Field-general fallback

One shipped profile, `field_general` @ `research-workflow-profile/1.0`, is the
mandatory landing state for unsupported, hybrid, ambiguous, or undeclared
work. Within the profile layer it preserves four things — author decision
authority, human/AI provenance, uncertainty disclosure, and optional (never
mandatory) alternatives — and pretends to know nothing field-specific. The
remaining #741 kernel primitives (evidence/evaluation status, branch
lifecycle states, disposition receipts, dependency/invalidation links) are
NOT profile content: they live in the #743/#744 state layers and remain
available under the fallback exactly as under any family profile.

Fallback field values:

- every `task_family_id` is `unresolved_fit` except `integrity_check`
  (`applicable`: the deterministic gates are field-general by construction);
- `alternative_categories` is `{state: "unresolved", categories: []}` —
  explicitly "categories unresolved", never "no alternatives apply";
- `branch_budget` is 3 (§7 counting semantics; the smallest value that still
  permits one committed line plus two live alternatives under comparison);
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
usability protocol**, not a discipline taxonomy and not a coverage claim
(§3's enum note records the deliberate v1 identity restriction). Only
profiles that pass authoring review ship; a stratum without a shipped
profile simply falls back per §4. The initial shipped set may be smaller than
seven; it must include at least one non-empirical family before any usability
run (protocol requirement, §8).

## 6. Selection, confirmation, correction

- Selection is recorded in a **selection receipt** (runtime state, outside the
  profile document): profile id + version + `content_sha256` (binding the
  exact canonical content in force, verified by the §3 recompute procedure),
  `selected_by: user_explicit |
  user_confirmed_proposal | fallback_automatic`, the ARS suite version at
  selection time, a timestamp, and the correction chain (next point).
- Correction is a first-class operation at any time and never restarts the
  project: the receipt appends the new selection and every stage output
  produced under the prior profile is marked **stale**
  (`profile_context_changed` — visible, non-destructive; scholar-owned
  content is never discarded or rewritten). Stale artifacts remain readable,
  but where the new profile declares an authority point the prior profile
  lacked (e.g. switching into clinical/human-subjects), dependent artifacts
  must pass that authority check before authority-sensitive reuse; ARS
  surfaces the unmet gate rather than silently carrying the artifact
  forward.
- ARS may *propose* a profile only when the user has described their research
  in their own words, and the proposal must present the fallback as an equally
  available choice. Declining a proposal lands on the fallback, silently
  costs nothing, and is never re-asked within the same stage.

## 7. Complexity budget (consumed by #743/#744)

The profile is the single carrier of **branch-budget** policy:
`branch_budget` binds every #743 branch surface. Its
`overflow_behavior: ask_merge_park_archive` also freezes the shared
author-disposition vocabulary consumed by #744. It does not prohibit #744's
separately versioned companion map from declaring an independent per-stage
`alternative_budget`; that number bounds alternative rows, is never derived
from `branch_budget`, and does not alter #743 replay.

**Counting semantics (frozen).** The budget bounds **live** branches — status
`active` or `reopened` in the #743 lifecycle — visible on one surface at one
decision point. `parked`, `rejected`, `merged`, and archived branches never
count. The budget is a display/attention bound per surface, not a cap on
total recorded state: the ledger retains everything regardless. When an
action would raise the live count above the budget, the surface must obtain a
user disposition (merge, park, or archive — `overflow_behavior`) before
showing the enlarged set; the overflowing candidate is retained pending that
disposition.

Frozen interaction rules, restated from the roadmap as contract obligations
on future consumers:

- the simple path receives **zero** new mandatory prompts from this contract;
- rich state may appear only at consequential or hard-to-reverse decisions;
- every added interaction offers `skip`, `off`, and reset-to-simple-path
  without discarding scholar-owned work;
- default views are one compact summary; graphs are progressively disclosed.

Budget rationale: 3 for the fallback (one committed line plus two live
alternatives) errs small on purpose — raising a budget is an evidence-gated
profile edit; shipping a large default and relying on users to cope is
exactly the burden failure mode the usability protocol exists to catch.

## 8. Preregistered usability protocol (NOT_RUN)

Design: paired comparison of (A) the current simple path against (B)
profile-aware progressive disclosure, on matched task sets, stratified by
research family × experience (novice / experienced), with each stratum
evaluated separately. Requires human participants; nothing in this repository
simulates them, and no ARS agent may act as a participant or judge. The
evaluated intervention is version-frozen: each run records the exact ARS
suite version, profile ids + versions + content hashes, and model/provider
under test.

**Operational definitions (frozen).**

- *Novice*: has completed fewer than 2 research projects to submission in the
  studied family; *experienced*: 2 or more. Self-reported at intake.
- *Task completion*: the participant reaches the task's pre-declared end
  state (each task card names it) within the session.
- *Abandonment*: the participant quits the task or the tool before the end
  state, by their own statement or by session timeout.
- *Unnecessary prompt*: any ARS-initiated interaction the participant
  dismisses without changing any input, judged from logs by a rater blind to
  arm.
- *Wrong-profile recovery*: given a seeded wrong profile, whether the
  participant detects it and reaches the correct profile via §6 correction,
  without restarting. This outcome exists only in arm B (arm A has no
  profile to recover from), so it is gated against an absolute criterion
  frozen at the §8-A amendment, not against arm A.
- *Consequential decision*: a decision recorded at a MANDATORY or FULL
  pipeline checkpoint or at the Stage 1 design freeze — the same boundary
  the #743 ledger uses for its summary moments.
- *Simple-path task card*: a task card authored to be completable without
  any profile or branch interaction, labeled `simple_path` at task-authoring
  time; the labeled set is frozen at the §8-A amendment.
- *Safety/authority regression*: any stratum in which arm B reaches a task
  end state with an authority-point requirement unmet that arm A surfaced
  (or that the task card's ground truth requires), plus any additional
  rubric the §8-A amendment freezes.

Outcomes, reported separately and never collapsed into one score:
task completion, unnecessary-prompt count, time on task, abandonment,
perceived control, wrong-profile recovery (detection + correction success),
and independently judged decision usefulness.

**Preregistered budgets and guardrails (v0.1).**

| Guardrail | Frozen threshold |
|---|---|
| Max added interactions (B vs A) | ≤ 2 added prompts per consequential decision AND ≤ 6 added prompts per task; 0 added on the simple path |
| Simple-task isolation | on simple-path task cards, arm B opens zero branch-management surfaces — measured directly as an outcome, not inferred from the prompt count |
| Time non-inferiority margin | B ≤ A × 1.10 per stratum (task time) |
| Abandonment non-inferiority | B ≤ A + 5 percentage points per stratum |
| Completion non-inferiority | B ≥ A − 5 percentage points per stratum |
| Perceived control | B not worse than A per stratum on the instrument chosen at the §8-A amendment, by more than the margin that amendment freezes alongside the instrument |
| Stratum rule | a failed stratum fails the gate; no rescue by pooled average |
| Family scope rule | evidence in one family × version authorizes only that family × version |

**Pre-recruitment amendment gate (§8-A, frozen).** Analysis unit, summary
statistics and confidence procedure, sample size and allocation /
counterbalancing plan, missing-data rule and session-timeout value, the
perceived-control instrument and its margin, the decision-usefulness
instrument/rubric and its margin, the absolute wrong-profile-recovery
criterion, the frozen `simple_path` task-card set, any additional
safety/authority-regression rubric, and rater training for the
"unnecessary prompt" and "decision usefulness" judgments are NOT yet
specified. Freezing invented
values now would be fake precision; instead this gate is itself frozen: **no
participant session may begin until a recorded amendment to this document
supplies every item in this paragraph.** The amendment must precede
recruitment, not follow it.

**Default-on decision rule (complete).** A default-on proposal for one exact
family × release requires ALL of: every guardrail row above passes in that
stratum; wrong-profile recovery in arm B meets the §8-A-frozen absolute
criterion in that stratum; decision usefulness in arm B is not worse than
arm A in that stratum on the §8-A-frozen instrument and margin; no safety or
authority regression in any stratum (a single stratum regression vetoes,
even if pooled results improve); and ≥ 3 materially different families with
usability evidence, at least one non-empirical. Mixed evidence on any outcome, or a materially risen burden
on any outcome, keeps the default unchanged. Evidence in one family or
version never authorizes another.

**Data boundary.** Committed task fixtures are synthetic or carry explicit
public/redistribution permission. Raw participant records, recordings, and
any unpublished manuscript material participants bring stay outside the
repository; only aggregate or de-identified evidence rows may be committed,
per the roadmap's repository data boundary.

## 9. Evidence-state registration (#745 hook)

At the 2026-08-17 design freeze, the planned #745 registration was:
mechanism `research_workflow_profile` @ contract `research-workflow-profile/1.0`,
one row under `rq_formation` (the task family where selection/confirmation
occurs, with a known-exclusion noting the profile governs every downstream
stage — the shipped matrix row shape requires exactly one task family),
initial status `DESIGNED`, behavioral evidence `NOT_RUN`, and claim ceiling: "a
design freeze for a versioned profile declaration exists; no schema, profile
instance, or runtime consumer ships yet, and no usability or outcome claim is
licensed". The #743 alpha's own registration requirement (roadmap Phase 2)
is unaffected.

The 2026-08-24 implementation advances that same matrix row's mechanism status
to `IMPLEMENTED` and its deterministic conformance to `CI_GATED`; behavioral
evidence stays `NOT_RUN`, and the claim ceiling names only the schema,
validator, fallback, and correction-receipt substrate.

## 10. Acceptance mapping

| Issue #742 acceptance item | Where addressed |
|---|---|
| user-confirmed, correctable selection | §6 + selection-receipt schema/runtime (shipped 2026-08-24) |
| explicit fallback, no silent inference | §1, §4 + canonical `field_general` profile/runtime (shipped 2026-08-24) |
| ≥ 3 families incl. one non-empirical with usability evidence | §8 (protocol frozen; evidence NOT_RUN — not satisfied) |
| no family-level regression hidden by average | §8 stratum rule + default-on rule |
| simple tasks never open branch surfaces | §7, §8 simple-task isolation outcome |
| mixed evidence ⇒ default unchanged | §8 default-on decision rule |

The three evidence-dependent rows stay open until the protocol runs; this
freeze makes them *checkable*, not checked.

## 11. Non-goals

No exhaustive discipline taxonomy; no journal-acceptance prediction; no claim
that shipped profiles cover academic research; no venue criteria (that is
#575/#684); no AI ranking of author-owned branches; no default-on change of
any kind from this document.

## 12. Deferred

Every §8-A amendment-gate item and all usability evidence remain deferred
(blocking recruitment, per §8-A — deferred does not mean optional). Family
profiles beyond the field-general fallback remain subject to the authoring
review in §5; the implementation does not fabricate them from the seven test
strata.
