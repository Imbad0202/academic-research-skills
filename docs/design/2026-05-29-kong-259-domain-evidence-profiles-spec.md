# Kong #259 — Discipline-Relative Domain Evidence Profiles

**Status:** prompt + new Schema 13 (standalone) + reference-doc design
**Date:** 2026-05-29
**Issue:** #259 (Tier A, `[ACCEPT-MEDIUM]`; attaches to #244 epic alongside #246)
**Scope:** Let a scholar select a `domain_evidence_profile` at the **pipeline entry point** so that `source_verification_agent` and `literature_strategist_agent` adjust their evidence checklist / search strategy to the scholar's discipline, instead of applying a single Western evidence-based-medicine (EBM) pyramid to every field. Advisory only, scholar-selected, no auto-detect, override first-class.

**Selection point (revised after dual-track R2 P0-1):** the profile is selected at the **pipeline entry**, before Stage 1 (RESEARCH / deep-research) runs — produced by `pipeline_orchestrator_agent` in its INTAKE & DETECTION step, NOT by `academic-paper`'s `intake_agent`. R2 found that `source_verification_agent` runs inside deep-research (Stage 1, Phase 2), strictly *before* `academic-paper`'s intake (Stage 2), so a profile produced at academic-paper intake is structurally invisible to that consumer (a producer↔consumer ordering cycle). Producing the profile at the orchestrator's pre-Stage-1 window — the same window that already gates Budget Transparency (`academic-pipeline/SKILL.md:399-401`) and confirms the entry point (`:221-240`) — makes the ledger present before *either* consumer runs. The orchestrator is also already the agent that writes the Material Passport, so it is the natural producer. **Standalone deep-research** (invoked directly, not through the pipeline) has no orchestrator and no intake; in that case no ledger is produced and both consumers run the neutral `unknown_user_defined` fallback. This standalone degradation is intentional and is stated explicitly in the Boundary section below.

**Anchor:** Kong et al. 2026 (arXiv:2605.18661) §7.4.6 (`kong2026_full.txt:L2213-L2227`, PDF p.39): "Extending AI-assisted research to chemistry, biology, medicine, materials science, physics, and social science requires more than retraining on domain papers. These fields differ in evidence standards, experimental infrastructure, safety constraints, data availability, and community norms."

## Boundary

This patch is the **profile-selection** layer. It is a checklist/search adjustment, not an autonomous grading or domain-detection layer.

- **No auto-SELECT.** The scholar selects the `domain_evidence_profile` at the pipeline entry; nothing auto-selects it. The orchestrator MAY *infer the discipline* (from a deep-research handoff, the user's opening request, or the entry-point detection) to *suggest a default* profile, but the scholar must confirm. The prohibition is specifically on a profile activating without scholar confirmation. (Kong §7.4.6 anchor rejects domain-*autonomous* judgment, i.e. an agent silently deciding evidence standards; a suggested-then-confirmed default is not autonomous.) `intake_agent` does not select the profile; it detects the orchestrator-produced ledger and re-displays it for confirmation (Change B2).
- **Advisory only.** A profile changes which evidence types / provenance an agent *looks for and surfaces*. It does NOT change the A-F Overall Grade, and it does NOT block manuscript ship.
- **Override is first-class.** The scholar may override the profile mid-pipeline. The override is produced by `pipeline_orchestrator_agent` — the agent that owns stage transitions and writes the Material Passport — which appends a new `selections[]` entry recording the override (Change A / INVARIANT 3). The scholar may know their sub-field better than the profile.
- **Standalone deep-research degrades to neutral.** When `deep-research` is invoked directly (not through `academic-pipeline`), there is no orchestrator to produce the ledger and no intake step. Both consumers then run the neutral `unknown_user_defined` fallback (INVARIANT 4 case (a) — absent ledger). This is intentional: a direct deep-research user has not entered the paper pipeline, so neutral evidence standards are the safe default. The scholar can still get a profile by running through the pipeline (or `academic-paper`, where intake confirms an orchestrator-produced profile). The Boundary claim "asked once at entry" therefore holds *for pipeline / academic-paper runs*; standalone deep-research is the explicit exception.
- **#246 is a forward dependency, not part of this patch.** #259 defines discipline-relative *evidence expectations* (what counts as good evidence per domain). #246 will later define discipline-relative *grade aggregation* (how the six criteria combine into an Overall Grade, e.g. so humanities is not structurally capped at Grade B). #259 ships a forward-reference note where aggregation would plug in; it does NOT import aggregation logic.
- **Conservative default.** The default profile `unknown_user_defined` is the neutral, pre-#259 single-pyramid behavior. Selecting an unimplemented (reserved) profile hard-falls back to `unknown_user_defined` with an explicit advisory, to prevent *false rigor* from a profile that does not exist yet.

## Profiles

### Ship-ready enum (exactly 4)

```
general_social_science | cs_ml | humanities_interpretive | unknown_user_defined
```

`unknown_user_defined` is the **default** and the neutral fallback. The other three are real, populated profiles.

### Reserved (documented, NOT in enum)

```
clinical | wet_lab | materials_physics | legal_case_based | education
```

Reserved profiles are named in the reference doc with a "not in enum yet — selecting this falls back to `unknown_user_defined`" note. They ship per demand in later releases. They are deliberately kept OUT of the enum so that intake cannot select a profile whose checklist does not exist (which would manufacture false rigor).

## Design decisions (settled in brainstorm 2026-05-29)

Four trade-offs were resolved against the maintainer's "no unrequested abstraction" discipline, with an independent codex (gpt-5.5 xhigh) consult. The resolutions deliberately diverge from two of the issue's literal acceptance criteria; §"Acceptance mapping" records each divergence and its reason.

| # | Decision | Rationale |
|---|----------|-----------|
| Q1 schema placement | A **new standalone Schema 13 `domain_evidence_profile`**, modeled on Schema 10's Material-Passport-carrier / consumer pattern but independent of it, and **produced by `pipeline_orchestrator_agent` at the pipeline entry** (revised after R2 — see Selection point + Change A/B). | *(Revised after dual-track R1 P1-A, then R2 P0-1.)* R1: the brainstorm first chose to ride Schema 10, but Schema 10 (Style Profile) has required style fields and intake sets `style_profile: null` when the scholar provides no writing samples (`intake_agent.md:195-196`). A no-sample run would then have nowhere valid to store the profile, or would have to emit an invalid Style Profile. A standalone Schema 13 keeps each schema's null-behavior independent and its responsibility single. R2: the *producer* also had to move — R1 placed it at `academic-paper` intake (Stage 2), but `source_verification_agent` (a consumer) runs in deep-research at Stage 1, before that intake, so the profile was structurally invisible to it. The producer is now `pipeline_orchestrator_agent`'s pre-Stage-1 INTAKE step, which already writes the Material Passport and already has a user-facing entry window. The two configs still have different lifecycles (Style Profile is optional-on-demand at academic-paper intake; domain profile is selected once at pipeline entry). |
| Q2 naming reconciliation | **Replace** the field-centric `Field-Specific Adjustments` table in `source_quality_hierarchy.md` with a profile-centric table, and keep a short legacy mapping note. | Two normative tables (field-centric vs profile-centric) would contradict. Profiles become the active contract; old field labels remain only as a migration/background note. Verified: no production consumer parses the old table's rows (only two reference-pointer mentions: `deep-research/SKILL.md:392`, `source_verification_agent.md:38`). |
| Q3 #246 forward-dependency | Add a **forward-reference note** in the profile section; do NOT pull aggregation into #259, do NOT ship placeholder logic. | #246 (grade aggregation) is unbuilt and the maintainer is doing #259 first. A forward note avoids a dangling cross-link without scope-creeping #259 into #246. |
| Q4 profile granularity | Add a `## Domain Evidence Profiles` section + a 4-row structured table **inside `source_quality_hierarchy.md`**. Do NOT create a `deep-research/references/domain_profiles/` directory of per-profile files. | 4 profiles (3 real, 1 neutral fallback), advisory-only, no aggregation, do not justify a directory of mini-specs. A single dedicated section keeps the agent reading one file while giving enough structure to consume reliably. Split into files only when profiles grow long, are independently maintained, or are reused by tooling. |

## Change set (6 edits)

> R2 P0-1 split the original "B. Intake production" into **B1 (orchestrator produces the profile at pipeline entry)** + **B2 (intake confirms it)**, because the producer had to move upstream of the Stage-1 consumer. The other four edits (A, C, D, E) keep their letters.

### A. New Schema 13 — `shared/handoff_schemas.md`

Add a **new standalone Schema 13 `domain_evidence_profile`** (NOT a block on Schema 10 — see Q1 rationale). **Producer: `pipeline_orchestrator_agent`** (at the pre-Stage-1 INTAKE & DETECTION window, `academic-pipeline/SKILL.md:221-240`; revised from R1's intake placement per R2 P0-1). **Carrier: `academic-pipeline` Material Passport** as an optional field, exactly as Schema 10 is carried (`shared/handoff_schemas.md:675`; does not affect integrity/review stages). This Material Passport is the **single canonical home**; if the profile is also surfaced in the academic-paper Paper Configuration Record, that is a *display/summary* echo only (mirroring how `Style Profile` appears as a PCR row at `intake_agent.md:238` while the authoritative Schema 10 lives in the passport) — consumers MUST read the passport ledger, never the PCR row (closes R2 P1-1). Consumers: `source_verification_agent` (Stage 1, deep-research), `literature_strategist_agent` (Stage 2, academic-paper). Because the producer runs before Stage 1, the ledger is present before *either* consumer executes.

The schema is a **single append-only event ledger** — there is no separate mutable `selected` scalar to drift out of sync with history (dual-track R1 P1-B). The active profile is *derived*, not stored.

```yaml
domain_evidence_profile:
  selections:                          # append-only ledger; >= 1 entry once the orchestrator runs its INTAKE step. Whole-schema absence OR an empty selections[] array = neutral pre-#259 behavior (see resolution rule case).
    - at: 2026-05-29T09:00:00Z
      stage: "0"                       # pipeline entry (pre-Stage-1); orchestrator INTAKE step
      requested: cs_ml                 # what the scholar asked for (one of the 4 ship-ready or 5 reserved values)
      effective: cs_ml                 # what actually applies after the reserved-fallback rule
      fallback_reason: null            # null unless requested ∈ reserved; then effective MUST be unknown_user_defined and this names the requested reserved value
    - at: 2026-05-29T11:00:00Z          # a later mid-pipeline override is just another appended entry, produced by the orchestrator
      stage: "2"
      requested: humanities_interpretive
      effective: humanities_interpretive
      fallback_reason: null
```

**Active-profile resolution rule (the load-bearing definition):** the active profile is the `effective` value of the **last `selections[]` entry whose `stage` is ≤ the consumer's current pipeline stage** (treat the pre-Stage-1 entry, `stage: "0"`, as ≤ every stage). In a normal forward run this is simply the last entry. The stage bound matters only under reset/resume to an *earlier* stage: a mid-pipeline override appended at a later stage MUST NOT retroactively apply to a consumer re-running at an earlier stage (closes R2 P1-7 — the append-only ledger is never truncated on resume, so an unbounded "last entry" would leak a future override backward). If **no** entry satisfies the bound, or the ledger / `selections[]` is absent or empty, the consumer applies the neutral `unknown_user_defined` fallback (INVARIANT 4). Consumers MUST resolve via this rule — they MUST NOT read any other field, and MUST NOT read the PCR display row, as the active profile.

Field rules (prose validation, mirroring Schema 10/11 style — NO separate JSON Schema file):

- `requested` MUST be one of the 4 ship-ready values OR one of the 5 reserved values — nothing else (closes R2 P1-2: a free-form or off-list `requested` is invalid).
- `effective` MUST be one of the 4 ship-ready enum values.
- **`requested`/`effective` coherence (closes R2 P1-2):** if `requested` is a ship-ready value, `effective` MUST equal `requested` and `fallback_reason` MUST be `null`. If `requested` ∈ {`clinical`, `wet_lab`, `materials_physics`, `legal_case_based`, `education`} (reserved), then `effective` MUST be `unknown_user_defined` and `fallback_reason` MUST be a non-null string naming the requested reserved value. No other `requested`/`effective` combination is valid (this forbids e.g. `requested: general_social_science, effective: cs_ml`, which would silently override the scholar's confirmed selection).
- `selections[]` is append-only: never reorder, never overwrite, never delete an entry (mirrors `reset_boundary[]` / `compliance_history[]`).
- **Malformed-ledger carve-out (closes R2 P1-8):** the general handoff convention (`shared/handoff_schemas.md:7-9`) is that a consumer validating a schema violation requests re-generation / raises `HANDOFF_INCOMPLETE`. Schema 13 **explicitly overrides** that convention: a malformed Schema 13 ledger, or a resolved `effective` outside the 4 enum values (e.g. a hallucinated name), MUST NOT block or trigger `HANDOFF_INCOMPLETE` — the consumer falls back to neutral `unknown_user_defined` and emits a one-line `[PROFILE-UNRESOLVED]` advisory (INVARIANT 4 case (c)). This is the advisory-only contract; a domain-profile defect must never halt the pipeline.

### B1. Profile production — `academic-pipeline/agents/pipeline_orchestrator_agent.md` (+ `academic-pipeline/SKILL.md`)

The **producer** of the Schema 13 ledger. Add a profile-selection step to the orchestrator's **INTAKE & DETECTION** stage (`SKILL.md:221-240`), in the same pre-Stage-1 window that already runs Budget Transparency (`SKILL.md:399-401`). This runs *before* Stage 1, so the ledger is in the Material Passport before either consumer executes.

- Present the 4 ship-ready profiles as an explicit choice; `unknown_user_defined` is the default if the scholar does not pick or is unsure.
- List the 5 reserved profiles with the explicit note that selecting one records `requested: <reserved>`, `effective: unknown_user_defined`, a non-null `fallback_reason`, **and surfaces an advisory** ("this domain has no profile yet — falling back to neutral evidence standards").
- The orchestrator MAY *suggest* a default profile inferred from the user's opening request / entry-point detection / a deep-research handoff if one is already present, but the scholar MUST confirm; nothing auto-activates (see Boundary "No auto-SELECT").
- Write the result as the first `selections[]` entry of the Schema 13 ledger in the Material Passport (`stage: "0"`).
- **Mid-pipeline override:** at any later stage transition where the scholar requests a different profile, the orchestrator appends a new `selections[]` entry tagged with the current stage (closes R2 P1-6 — the override now has a concrete producer and execution path).
- **plan-mode / standalone exemptions:** see Change B2 (plan mode) and the Boundary "Standalone deep-research" bullet (direct deep-research has no orchestrator → no ledger → neutral fallback).

### B2. Profile confirmation — `academic-paper/agents/intake_agent.md`

`intake_agent` is **not** the producer. It detects the orchestrator-produced ledger and re-displays it for scholar confirmation, folding into the existing **Deep Research Handoff Detection** flow (`intake_agent.md:23-59`), which already auto-populates and re-confirms fields like discipline.

- If a Schema 13 ledger is present in the passport, display the active profile (resolved per the Change A rule) and ask the scholar to confirm or override. An override here is just another appended entry (produced via the orchestrator path, B1).
- Do NOT add a fresh selection questionnaire and do NOT fold into Step 10 Style Calibration (Step 10 is writing-sample calibration the scholar frequently declines, `style_profile: null`; profile confirmation is a different concern).
- **plan mode is exempt (closes R2 P2-2):** the plan-mode simplified 3-question intake (`intake_agent.md:95-104`, `:263`) does NOT run profile confirmation. A plan-mode run that did not pass through an orchestrator profile step simply has no ledger, and consumers run the neutral `unknown_user_defined` fallback. (plan mode is a lightweight structure-planning mode; domain evidence-standard tuning has low value there and the simplified intake stays simple.)
- The active profile MAY be echoed as a Paper Configuration Record display row (like `Style Profile`), but the authoritative copy is the Material Passport ledger (Change A) — the PCR row is never the source of truth for consumers.

### C. Profile definitions — `deep-research/references/source_quality_hierarchy.md`

Three edits:

1. **Replace** the `## Field-Specific Adjustments` table (lines ~132-143; it has **6 rows** — Medicine/Health, Education, Social Science, Policy, Humanities, Technology) with a profile-centric framing. To avoid silently dropping the existing per-field guidance (dual-track R1 P1-D), **every one of the 6 rows** must be carried forward — three fold their substance into ship-ready profile rows; the other three are preserved in a legacy note. Specifically:
   - `general_social_science`, `cs_ml`, `humanities_interpretive` profile rows **absorb the substance of** the Social Science / Technology / Humanities rows respectively. The **Policy** row's substance is folded into the `general_social_science` profile row as well (Policy has no dedicated profile; its expert-panel/context-dependent guidance is merged into `general_social_science`'s notes — closes R2 P1-4, which found Policy was the one row neither folded nor preserved).
   - The Medicine/Health and Education rows map to **reserved** profiles (`clinical`, `education`). Their existing adjustment text MUST be **preserved verbatim in the legacy mapping note** (not deleted).
   - **Preservation is historical / non-normative (closes R2 P1-3).** The legacy note records what the field-centric table used to say, for reference and for the eventual `clinical` / `education` profiles. It does NOT change runtime behavior: until those reserved profiles ship, Medicine/Health and Education runs use the neutral `unknown_user_defined` pyramid, exactly as every other unmapped selection does. Label the note "**historical reference — non-normative; current behavior for these domains is neutral `unknown_user_defined` until the `clinical` / `education` profile ships.**" (This removes the R1 contradiction where the note was simultaneously called "applies until" — normative — and "neutral" / non-normative per INVARIANT 9.)

   Legacy mapping (old field label → disposition):
   - Social Science → substance folded into `general_social_science` profile row *(normative, via the profile)*
   - Technology → substance folded into `cs_ml` profile row *(normative, via the profile)*
   - Humanities → substance folded into `humanities_interpretive` profile row *(normative, via the profile)*
   - Policy → substance folded into `general_social_science` profile row *(normative, via the profile; no dedicated Policy profile)*
   - Medicine/Health → text preserved verbatim in the historical/non-normative legacy note; runtime behavior = neutral `unknown_user_defined` until the reserved `clinical` profile ships
   - Education → text preserved verbatim in the historical/non-normative legacy note; runtime behavior = neutral `unknown_user_defined` until the reserved `education` profile ships

2. **Add** a `## Domain Evidence Profiles` section with a 4-row table. Columns: `Profile` / `Standard evidence types` / `Common provenance requirements` / `Critical gaps to surface` / `Reserved-note`. (The gaps column is named "Critical gaps to surface" — NOT "disqualifying" — because the profile is advisory: it tells the agent what weaknesses to *flag*, it never disqualifies a source or changes the grade. Dual-track R1 P2.) Plus a separate short list of the 5 reserved profiles with the "not in enum" note.

3. **Add** a `#246` forward-reference note: "Discipline-relative *grade aggregation* (how these evidence expectations roll up into an Overall Grade) is tracked separately in #246 and is not yet implemented; until then the A-F Overall Grade lookup above applies unchanged."

### D. source_verification consumption — `deep-research/agents/source_verification_agent.md`

In `## Verification Procedures` (line ~50), add a **Step 0: Resolve `domain_evidence_profile`**:

- Resolve the active profile per the Change A rule (last `selections[]` entry whose `stage` ≤ this agent's current stage; read the Material Passport ledger, never a PCR display row). If present and ≠ `unknown_user_defined`, adjust the verification checklist per that profile's `Standard evidence types` / `Common provenance requirements` / `Critical gaps to surface` from `source_quality_hierarchy.md`.
- **Graceful fallback (each case explicitly defined):** apply the current neutral 7-level-pyramid behavior unchanged when ANY of: (a) the Schema 13 ledger is absent OR `selections[]` is empty OR no entry satisfies the stage bound; (b) the resolved `effective` is `unknown_user_defined`; (c) the ledger is malformed OR the resolved value is not one of the 4 enum values (e.g. a hallucinated profile name) — in case (c) also emit a one-line `[PROFILE-UNRESOLVED]` advisory. No case blocks (Schema 13 malformed carve-out, Change A).
- The profile adjusts what the agent *surfaces*; it does NOT change the A-F grade and does NOT block (advisory).

### E. literature_strategist consumption — `academic-paper/agents/literature_strategist_agent.md`

A profile must influence BOTH retrieval AND the post-retrieval screening gates, otherwise the existing gates silently neutralize a profile-specific search (dual-track R1 P1-C). `literature_strategist` resolves the active profile exactly as Change D does — the same Change A rule (last `selections[]` entry whose `stage` ≤ current stage; read the passport ledger, not a PCR row) **and the same three graceful-fallback cases**: (a) ledger absent / `selections[]` empty / no entry satisfies the stage bound; (b) resolved `effective` = `unknown_user_defined`; (c) ledger malformed OR resolved value not one of the 4 enum values — case (c) emits a one-line `[PROFILE-UNRESOLVED]` advisory; no case blocks (closes R2 P1-5, which found Change E omitted the malformed/non-enum case + advisory that Change D specifies).

**Loosen-only / additive contract (closes R2 P2-1, realizes INVARIANT 5).** Every sub-edit below is *monotonic admit-only*: under a non-neutral profile a gate may **admit an evidence type it would otherwise wrongly exclude**, but it MUST NOT exclude, down-rank, or fail any source that the neutral gate currently admits. Where a gate combines neutral and profile criteria, combine by **OR (union of admissible)**, never by replacement. The four sub-edits, all reverting to current behavior under fallback cases (a)/(b)/(c):

1. **Search strategy** (`### Step 2: Database Selection`, `### Step 3: Search String Construction`, ~lines 45-57): **add** profile-relevant databases + search strings (e.g. `cs_ml` → also query arXiv / ACL Anthology / proceedings; `humanities_interpretive` → also query monographs / archival / primary sources). Additive — never drops a database the neutral strategy would have queried.
2. **Screening decision tree** (`### Literature Screening Decision Tree`, ~line 413): the current tree excludes non-peer-reviewed unless gov/white-paper gray literature, which would drop `cs_ml` preprints and `humanities_interpretive` archival/primary sources. Add a profile-aware branch so the profile's standard evidence types are **additionally admissible** (preprints includable under `cs_ml`, primary/archival sources includable under `humanities_interpretive`), tagged by type rather than excluded. The branch only *adds* admit paths; nothing the neutral tree admits becomes excluded.
3. **Quality quick-assessment checklist** (`### Literature Quality Quick Assessment Checklist`, ~line 436): the journal-ranking-weighted scoring penalizes preprints/archival. Under a non-neutral profile, a source passes if it **meets the neutral journal-ranking bar OR meets the profile's evidence-type expectations** (union, not replacement — closes R2 P2-1, which flagged the R1 "rather than journal ranking" wording as a tightening risk: a high-ranking source that does not match the profile must still pass on the neutral bar).
4. **Quality gates** (`## Quality Gates`, ~line 468): the `>= 70% peer-reviewed` (line 479) and `>= 50% currency` (line 480) pass criteria contradict `humanities_interpretive` (primary/older canonical texts) and `cs_ml` (preprints). Make these gates profile-relative **in the loosening direction only**: under a non-neutral profile the admissible set *expands* (preprints count toward the `cs_ml` peer-reviewed-equivalent ratio; canonical texts do not count against `humanities_interpretive` currency). The thresholds are never raised, and a corpus that passes the neutral gate always passes the profile-relative gate.

This composes with the existing `## Distributional Skew Advisory (Kong #257)` section without contradicting it (skew advisory measures distribution; profile sets admissibility — orthogonal).

## Acceptance mapping (incl. deliberate divergences)

| Issue acceptance criterion | How this spec satisfies it | Divergence |
|----------------------------|----------------------------|------------|
| #1 Intake adds `domain_evidence_profile` with enum = 4 ship-ready values + default `unknown_user_defined` | Change A (new Schema 13 ledger) + Change B1 (orchestrator produces it at pipeline entry) + Change B2 (intake confirms it) | aligned in substance; **selection point moved from academic-paper intake to the pipeline-entry orchestrator** (R2 P0-1 — necessary so the Stage-1 consumer can see it). To be noted on #259 at close. |
| #2 `deep-research/references/domain_profiles/` directory + 4 profile md files | **Changed to** a `## Domain Evidence Profiles` section + 4-row table inside `source_quality_hierarchy.md` (Change C) | **DIVERGES** — maintainer-approved (Q4): single dedicated section, not a directory, since 4 advisory profiles with no aggregation do not justify a mini-spec directory. To be noted on #259 at close. |
| #3 Reserved profile list documented with "not in enum yet" note | Change A (block rules) + Change C (reserved-note column + reserved list) | aligned |
| #4 `source_verification_agent.md` + `literature_strategist_agent.md` consume the profile | Changes D + E (both resolve via the Change A stage-bound rule from the Material Passport) | aligned. Note: `source_verification_agent` only receives a non-neutral profile on a **pipeline / academic-paper** run; on a standalone deep-research run it correctly falls back to neutral (Boundary "Standalone deep-research"). |
| #5 #246 cross-links to relevant profiles | **Changed to** a forward-reference note (Change C.3), because #246 is not yet implemented | **DIVERGES** — maintainer-approved (Q3): forward-reference note instead of a live cross-link, to avoid a dangling reference. The live cross-link lands when #246 ships. |
| #6 User can override profile mid-pipeline, recorded in Material Passport | Schema 13 append-only `selections[]` ledger; an override is an appended entry produced by the orchestrator (Change B1); active = last entry's `effective` bounded by current stage (Change A) | aligned |

## INVARIANTS

1. **Enum cardinality.** The ship-ready enum (`effective` values) is exactly 4 (`general_social_science`, `cs_ml`, `humanities_interpretive`, `unknown_user_defined`); the 5 reserved values (`clinical`, `wet_lab`, `materials_physics`, `legal_case_based`, `education`) are NOT in the `effective` enum (they may appear only as `requested`).
2. **Reserved fallback (per entry).** A `selections[]` entry with `requested` ∈ reserved → `effective: unknown_user_defined` + non-null `fallback_reason` naming the requested value + an explicit intake advisory. No reserved profile ever silently activates a checklist.
3. **Active-profile resolution.** The active profile is the `effective` value of the last `selections[]` entry **whose `stage` is ≤ the consumer's current pipeline stage** (the pre-Stage-1 entry, `stage: "0"`, counts as ≤ every stage). An override is a new appended entry; there is no mutable scalar that can drift from history. The stage bound prevents a later-stage override from leaking backward to a consumer re-running at an earlier stage after reset/resume. (Closes R1 P1-B + R2 P1-7.)
4. **Graceful fallback.** Absent ledger / empty `selections[]` / no entry within the stage bound / resolved value not in the 4 enum (incl. hallucinated names) / `unknown_user_defined` → consuming agents apply the current neutral single-pyramid behavior, unchanged, with no block; the malformed/non-enum case also emits `[PROFILE-UNRESOLVED]`. Schema 13 explicitly overrides the general `HANDOFF_INCOMPLETE` convention so a profile defect never blocks. (Incorporates R2 P1-8 + empty-array R2 P2-4.)
5. **Advisory only.** A profile never changes the A-F Overall Grade and never blocks manuscript ship. In `literature_strategist`, profile-relative gates are **monotonic admit-only**: they only *admit* evidence types the neutral gates would wrongly exclude (combining by OR / union), and never exclude, down-rank, or fail any source the neutral gate currently admits. (R2 P2-1 hardened the wording.)
6. **No auto-SELECT.** No agent activates a `domain_evidence_profile` without scholar confirmation. The producer is `pipeline_orchestrator_agent` (pipeline entry); discipline *inference* MAY suggest a default, but the scholar confirms. `intake_agent` only confirms/displays an orchestrator-produced profile, it does not select. (Distinct from prohibiting discipline inference outright — R1 P2; producer relocated — R2 P0-1.)
7. **No discipline loses existing guidance.** Replacing the 6-row field-centric table MUST account for every row: Social Science / Technology / Humanities / **Policy** fold their substance into ship-ready profile rows (Policy → `general_social_science`); Medicine/Health + Education are preserved verbatim in a **historical, non-normative** legacy note whose runtime behavior is neutral `unknown_user_defined` until their reserved profiles ship. No row is dropped, and the preserved note is non-normative (no "applies until" normative claim). (Closes R1 P1-D + R2 P1-3 + R2 P1-4.)
8. **#246 boundary.** #259 references grade aggregation as a forward dependency only; it ships no aggregation logic and no placeholder aggregation code.
9. **Single normative profile table.** After Change C, `source_quality_hierarchy.md` has exactly one normative profile table; the old field-centric table is reduced to a non-normative legacy mapping note (which still carries the preserved Medicine/Education text per INVARIANT 7).
10. **Single canonical carrier.** The Material Passport Schema 13 ledger is the one authoritative home for the active profile. Any Paper Configuration Record echo is display-only; consumers MUST read the passport ledger, never the PCR row. (Closes R2 P1-1.)
11. **Standalone deep-research degrades to neutral.** A direct `deep-research` invocation (no orchestrator, no intake) produces no ledger; both consumers run neutral `unknown_user_defined` (INVARIANT 4 case (a)). The "selected once at entry" guarantee holds for pipeline / academic-paper runs only; standalone deep-research is the explicit, documented exception. (R2 P0-1 a-ii resolution.)
12. **`requested`/`effective` coherence.** Every `selections[]` entry has `requested` ∈ {4 ship-ready ∪ 5 reserved}; if ship-ready, `effective == requested` and `fallback_reason` is null; if reserved, `effective == unknown_user_defined` with non-null `fallback_reason`. No other combination is valid — a clean-resolving entry can never silently differ from the scholar's confirmed selection. (Closes R2 P1-2.)

## Test strategy

Prose schema (mirrors Schema 10 / #256 commitment ledger — no JSON Schema file). The checker is **honest about its reach**: a markdown structural checker verifies *documentation surface* (presence/shape of required text), NOT runtime semantics. Dual-track R1 P2 flagged that several INVARIANTS are semantic; the split below makes that explicit.

**`scripts/check_domain_evidence_profile.py` — documentation-surface checks (deterministic):**

1. Schema 13 documents exactly the 4 `effective` enum values + the 5 reserved values; the active-profile resolution rule text (last entry's `effective` **bounded by stage**) is present; the `requested`/`effective` coherence rule and the malformed-ledger carve-out text are present (INVARIANTS 1, 3, 4, 12).
2. `source_quality_hierarchy.md` has a `## Domain Evidence Profiles` section with a 4-profile table whose gaps column is "Critical gaps to surface" (NOT "disqualifying"), plus the 5 reserved names with the "not in enum" note (INVARIANTS 1, 2, 5).
3. Both consumer agents contain a "resolve `domain_evidence_profile`" instruction AND all three graceful-fallback cases (absent/empty/out-of-stage-bound / non-enum incl. hallucinated / `unknown_user_defined`) (INVARIANT 4).
4. `source_quality_hierarchy.md` carries the advisory-only statement + the #246 forward-reference note (INVARIANTS 5, 8).
5. The old field-centric table is demoted to a legacy note that is labeled non-normative AND still contains the preserved Medicine/Health + Education text; the `general_social_science` profile row references the folded **Policy** substance (INVARIANTS 7, 9 — Policy guard added per R2 P1-4).
6. Schema 13 names `pipeline_orchestrator_agent` as producer + Material Passport as the single canonical carrier (INVARIANTS 6, 10).

**Negative fixtures + mutation test (`scripts/test_check_domain_evidence_profile.py`):** deliberately (a) add a 5th `effective` enum value, (b) rename the gaps column back to "disqualifying", (c) strip one graceful-fallback case, (d) delete the preserved Medicine/Education text, (e) **remove the malformed-ledger carve-out text**, (f) **remove the Policy fold reference** — each must make the checker FAIL (so it cannot trivially accept-all). Wired into `.github/workflows/spec-consistency.yml`.

**Out of the checker's reach — relies on plan-stage review + worked example:** INVARIANT 2's runtime reserved-fallback behavior; INVARIANT 5's no-grade/no-block runtime behavior **and its monotonic admit-only ("never tighten") half** (a markdown surface checker cannot verify that a gate only loosens); INVARIANT 6's no-auto-SELECT; INVARIANT 8's no-aggregation-logic; INVARIANT 11's standalone-degradation runtime path. These are agent-prompt semantics. The implementation plan MUST include worked examples exercising (i) a reserved-fallback, (ii) a mid-pipeline override, and (iii) a reset/resume to an earlier stage that must NOT inherit a later override; the dual-track reviewers verify the prompt text — the linter does not claim to enforce these.

## Out of scope (forward work)

- **#246** discipline-relative grade aggregation (Overall Grade formula). #259 only forward-references it.
- Reserved profiles (`clinical` / `wet_lab` / `materials_physics` / `legal_case_based` / `education`) ship per demand in later releases.
- `citation_compliance_agent` profile integration (consistent with the v3.6.5 deferral of corpus integration for that agent).
- No JSON Schema file for `domain_evidence_profile` (Schema 13 is a prose schema, mirroring the Schema 10 / #256 commitment-ledger convention).
- Profile-relative grade aggregation (#246) — only forward-referenced; the A-F lookup is unchanged.
- Passport reset/resume semantics for the Schema 13 ledger are **handled by the stage-bound resolution rule** (Change A / INVARIANT 3), NOT left unhandled. R1 claimed "no special-casing needed" by reasoning only about forward replay; R2 P1-7 found that case insufficient — a resume to an *earlier* stage would otherwise inherit a later-stage override because the append-only ledger is never truncated. The stage bound ("last entry whose `stage` ≤ current stage") resolves this without truncating the ledger: a forward run still resolves to the last entry, while an earlier-stage re-run ignores entries appended at later stages. No ledger mutation on reset; the bound does the work. A reset that starts a genuinely fresh run with no carried passport simply has no ledger and re-selects at the orchestrator entry. (Closes dual-track R1 P2 passport-reset + R2 P1-7.)
