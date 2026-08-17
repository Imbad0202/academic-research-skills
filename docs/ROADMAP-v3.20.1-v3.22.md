# ARS Post-v3.20 through v3.22 Development Roadmap

**Status:** PLAN OF RECORD — implementation order is committed; structural defaults remain evidence-gated.
**Date:** 2026-08-15.
**Scope source:** reproducible post-release repository contract audit plus reconciliation with the public issue backlog.
**Tracking epics:** #734 (immediate contract honesty) and #741 (adaptive inquiry-state architecture).

## Outcome

The next releases will first make current claims match current mechanisms. Only then will ARS add richer inquiry state, and that state will remain bounded, optional, and research-type aware until comparative evidence shows that it helps without imposing unacceptable burden.

The roadmap deliberately separates four things:

1. **correctness fixes** that can ship now;
2. **structural mechanisms** that can be engineered but may add user burden;
3. **effectiveness questions** that require controlled evaluation;
4. **intrinsic limits** that ARS must disclose rather than promise to solve.

## Delivery order

| Phase | Target | Goal | Default behavior |
|---|---|---|---|
| 0 | next patch | Correct contract, status, and claims-language mismatches | Hardened immediately |
| 1 | following patch design/eval | Freeze research-family profiles and usability thresholds | No workflow expansion |
| 2 | v3.21 alpha | Add a bounded inquiry branch ledger | Opt-in; simple path unchanged |
| 3 | v3.21 beta | Carry relevant alternatives across later stages | Opt-in and profile-specific |
| 4 | v3.21-v3.22 | Bind criteria and publish stage-level evidence ceilings | Generated evidence view; no inflated claim |
| 5 | v3.22+ | Execute outcome-level study | No effectiveness claim before results |

Dates are intentionally not promised for human-participant evaluation. Release order and gates take precedence over calendar targets.

## Phase 0 — next-patch contract-honesty hardening

Parent: #734.

1. **#735 — Socratic research-question boundary.** The default non-convergence path may summarize scholar-originated directions and offer continued dialogue or literature exploration. It may generate candidates only after an explicit user request and a visible exit from the non-generative Socratic contract.
2. **#737 — coverage-bounded verification language.** Use `100% of registered claims`, name the denominator, keep semantic extraction coverage unknown, and distinguish replayable deterministic checks from generative reproducibility.
3. **#736 — author disposition for detected claim-strength drift.** Replace default-open routing with `restore`, `authorize_with_reason`, or `pause`; bind every choice at build and replay to explicitly named run-local raw event bytes while keeping paths and messages out of the durable sidecar.
4. **#738 — user-attested reading state.** Unknown/legacy scope remains `coverage_unknown` and can never become `ok` for an anchored claim.
5. **#739 — reviewer score honesty.** Generic 0-100 summaries are `NOT_CALIBRATED`; no field-general score-to-editorial-decision mapping or universal reference-count threshold.
6. **#740 — typed review provenance.** Report role, context, peer-output, model-family, provider, and human separation independently; do not infer independent error processes from personas.

### Next-patch ship gates

- Every changed behavior has a regression test that fails on its v3.20 form.
- Command, skill, agent, schema, renderer, and maintained documentation surfaces agree.
- Unknown/unmeasured states fail visibly.
- Release notes describe corrections, not improved research outcomes.
- The existing full deterministic suite remains green.

## Phase 1 — research-family profiles and a complexity budget

Issue: #742. This phase changes the design substrate, not the default workflow.

### Minimal universal kernel

ARS may treat the following as broadly reusable governance primitives:

- author versus AI provenance and decision authority;
- evidence and evaluation status;
- active, parked, rejected, reopened, and stale state;
- explicit adoption/disposition receipts;
- dependency and invalidation links.

These primitives do not imply that the same research stages, alternative types, evidence hierarchy, or review standards apply everywhere.

### Research-family overlays

A user-confirmed, versioned profile declares applicable stages, vocabulary, alternative categories, reporting/design overlays, institutional authority points, exclusions, and unresolved fit. Initial evaluation strata may include quantitative empirical, qualitative, theoretical/conceptual, interpretive/humanities, evidence synthesis, computational, and clinical/human-subjects work. They are test strata, not an exhaustive taxonomy or a coverage claim.

Unsupported or hybrid work receives the minimal kernel and an explicit fallback state. ARS must not silently infer a profile from manuscript quality or disciplinary stereotypes.

### Complexity budget

- The current simple path remains available and receives no new mandatory branch prompt.
- Rich state appears only at consequential or hard-to-reverse decisions.
- Default views use one compact summary; the underlying graph is progressively disclosed.
- Each profile freezes a live-branch budget plus merge, park, and archive behavior.
- Every added interaction offers `skip`, `off`, and reset-to-simple-path behavior without discarding scholar-owned work.
- Novice and experienced users are evaluated separately.
- Task completion, unnecessary prompts, time, abandonment, perceived control, wrong-profile recovery, and decision usefulness remain separate outcomes.
- No default-on change is licensed by an average improvement that hides a material burden or authority regression in one research family.
- Default-on authorization is specific to an exact research-family profile and release: positive evidence in one family or version cannot authorize another.
- Before implementation, #742 preregisters the maximum added interaction/time budget and non-inferiority guardrails for completion, abandonment, and perceived control in every research-family × experience stratum; a failed stratum cannot be rescued by a pooled average.

## Phase 2 — bounded inquiry branch ledger

Issue: #743; ideation-measurement dependency: #659.

The versioned ledger records stable branch/parent ids, author versus AI-facet provenance, assumptions, evidence sought, status, disposition reason, reopen conditions, and downstream invalidation links. Only author-expressed or explicitly adopted framings become scholarly branches.

The alpha remains opt-in. A branch summary appears at a consequential freeze or when evidence satisfies a reopen condition. Reopening marks dependent artifacts stale; it never silently mutates them. The ledger may show that alternatives were preserved and recoverable, but not that they were novel, correct, or valuable.

Before the #743 alpha ships, it must register its exact mechanism version, `DESIGNED` / `NOT_RUN` evidence state, transport limits, and claim ceiling in a minimal #745-compatible evidence-matrix scaffold. Structural code may not precede the record that bounds what can be claimed about it.

Promotion beyond opt-in requires paired evidence on recovery, breadth, burden, time, abandonment, and research-family fit.

## Phase 3 — cross-stage alternative register

Issue: #744.

Profile-relevant alternatives may be carried through theory, design, measurement, analysis, synthesis, interpretation, drafting, and review. Each profile decides which stages and categories apply. `not_applicable` is lawful and visible; more alternatives are not treated as inherently better.

The register must track evidence, author disposition, unresolved state, reopen conditions, and dependent artifacts. Evaluation must report useful follow-through separately from irrelevant-alternative inflation and user burden. It stays opt-in until the Phase 1 gates pass.

## Phase 4 — criteria, capability evidence, and claim ceilings

1. **#575/#684 — target criteria.** Complete a bounded set of source-backed venue × track × contribution-type profiles with author confirmation, freshness governance, and constructive-value evaluation. No venue fit score becomes an acceptance prediction.
2. **#745 — stage capability/evidence matrix.** Publish one machine-readable source for mechanism status, conformance evidence, behavioral evidence, model/version/population, transport limits, claim ceiling, and next evaluation.
3. **#582 — role topology utility.** Compare panels with matched solo/minimal baselines; role count is never competence evidence.
4. **#659 — within-session ideation breadth.** Keep scholar-originated framings separate from AI-surfaced facets and report burden separately.
5. **#684 — criteria usefulness.** Execute the frozen evaluation rather than treating a registered profile as evidence of constructive review.

The evidence matrix must preserve at least `DESIGNED`, `NOT_RUN`, `MEASURED`, `MIXED`, `OUT_OF_SCOPE`, and stale/transport-limited states. README and release-note claims cannot exceed the recorded ceiling.

## Phase 5 — outcome-level study

Issue: #746; governing frozen design: #658.

Engineering can build schemas, validators, packet manifests, assignment and masking records, judge assignment, and deterministic scoring replay. It cannot substitute simulated participants or ARS reviewer agents for recruitment and independent external judging.

A pilot establishes feasibility only. The full study must follow the preregistered estimand, governance, intervention version, active-control parity, masking, stopping rules, and result-publication commitment. A positive result may support a bounded manuscript/process-quality claim; it cannot establish that underlying procedures were executed, raw data are true, results reproduce, or scientific conclusions are valid.

## What is and is not portable across research domains

| Layer | Reasonably field-general | Must be profile-specific or externally governed |
|---|---|---|
| Authority | The author adopts, rejects, or reopens scholarly choices | Institutional authority, co-author roles, community-specific consent |
| Provenance | Human/AI/source origin and version can be recorded | What counts as adequate evidence or expertise |
| State | Alternatives can be active, parked, rejected, or stale | Which alternatives are meaningful and when they should appear |
| Workflow | Dependencies and invalidation can be explicit | Stage order, optional/absent stages, iteration patterns |
| Review | Findings can carry criteria, anchors, uncertainty, and provenance | Venue, genre, method, and interpretive standards |
| Evaluation | Mechanism, behavior, and outcome evidence can remain separate | Gold standards, judges, utility measures, and acceptable burden |

Therefore the proposed architecture is not universally applicable in one fixed form. The universal claim is limited to a small governance kernel; all substantive workflow content requires demonstrated profile fit or an explicit fallback.

## Intrinsic limits

No roadmap item can make ARS independently establish:

- whether reported procedures were actually performed;
- whether raw data are authentic or complete;
- whether results reproduce in the world;
- whether a research question is important, original, or worth pursuing;
- whether persona-separated reviewers have independent error processes;
- tacit editorial judgment or future acceptance decisions;
- suitability for every discipline, genre, jurisdiction, or institutional setting.

ARS can make these boundaries, decisions, evidence, and uncertainty more inspectable. External experts, institutions, replications, and empirical studies remain necessary.

## Repository data boundary

- Committed tests and examples use synthetic fixtures or materials with explicit public/redistribution permission.
- Confidential correspondence, unpublished research artifacts, and maintainer-local screenshots or working documents do not belong in issues, commits, fixtures, examples, or pull-request descriptions.
- Maintainer-local `deliverables/` is ignored at repository root.
- A release candidate receives a **manual** changed-file privacy/provenance scan in addition to ordinary tests until an automated gate ships.

## Decision rule

Correctness and honesty fixes ship when their contracts and regression tests pass. Structural features ship opt-in when their schemas and state transitions pass. A structural feature becomes a default only after its usability and research-family evaluations support that exact change without hiding subgroup harm. Effectiveness language changes only after the relevant preregistered study is complete.
