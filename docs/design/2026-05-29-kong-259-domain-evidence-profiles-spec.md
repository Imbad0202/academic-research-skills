# Kong #259 — Discipline-Relative Domain Evidence Profiles

**Status:** prompt + new Schema 13 (standalone) + reference-doc design
**Date:** 2026-05-29
**Issue:** #259 (Tier A, `[ACCEPT-MEDIUM]`; attaches to #244 epic alongside #246)
**Scope:** Let a scholar select a `domain_evidence_profile` at **paper intake** so that `literature_strategist_agent` adjusts its search strategy / screening gates to the scholar's discipline, instead of applying a single Western evidence-based-medicine (EBM) pyramid to every field. Advisory only, scholar-selected, no auto-detect, override first-class.

**Single consumer = `literature_strategist_agent` (revised after dual-track R2 P0-1 + R4 P0-2; maintainer-approved option c).** The profile is produced by `academic-paper`'s `intake_agent` and consumed only by `literature_strategist_agent` — both in `academic-paper` Stage 2, with intake (Phase 0) running before literature_strategist (Phase 1). **`source_verification_agent` is NOT a consumer.** Why this changed across rounds:

- R1 placed the producer at `intake_agent` and listed *two* consumers (`source_verification_agent` + `literature_strategist_agent`).
- R2 P0-1 found `source_verification_agent` runs inside deep-research (Stage 1, Phase 2), strictly *before* `academic-paper`'s intake (Stage 2) — a producer↔consumer ordering cycle. The fix attempted was to move the producer upstream to `pipeline_orchestrator_agent`'s pre-Stage-1 window (R3).
- R4 P0-2 found that relocation only moved the gap: the Material Passport "accompanies every artifact as it passes between stages" (`shared/handoff_schemas.md:481-483`) and the orchestrator writes it at *handoffs*, not at a pre-Stage-1 moment — so the passport may not even exist before Stage 1, and the Stage-1 consumer still could not be served without re-architecting the passport lifecycle.
- **Resolution (option c, maintainer-approved 2026-05-29):** drop `source_verification_agent` from the consumer set. With `literature_strategist_agent` as the sole consumer, producer and consumer are both in `academic-paper` Stage 2 (intake first), the passport already exists at that point, and no cross-skill carrier hop is needed. This is a deliberate divergence from issue acceptance #4 (which named two consumers); see Acceptance mapping. `source_verification_agent`'s domain-aware verification (IRB checks, reagent provenance, etc.) is deferred to a future release that can address the deep-research carrier lifecycle — noted in Out of scope.

A direct `academic-paper` run, a mid-entry pipeline start, or a standalone `deep-research` run that does not pass through `intake_agent` simply produces no ledger; `literature_strategist_agent` (if it runs at all) takes the neutral `unknown_user_defined` fallback. See the Boundary "No ledger ⇒ neutral" bullet.

**Anchor:** Kong et al. 2026 (arXiv:2605.18661) §7.4.6 (`kong2026_full.txt:L2213-L2227`, PDF p.39): "Extending AI-assisted research to chemistry, biology, medicine, materials science, physics, and social science requires more than retraining on domain papers. These fields differ in evidence standards, experimental infrastructure, safety constraints, data availability, and community norms."

## Boundary

This patch is the **profile-selection** layer. It is a checklist/search adjustment, not an autonomous grading or domain-detection layer.

- **No auto-SELECT.** The scholar selects the `domain_evidence_profile` at intake; nothing auto-selects it. `intake_agent` MAY *infer the discipline* (from a deep-research handoff or its Step 1 topic interview) to *suggest a default* profile, but the scholar must confirm. The prohibition is specifically on a profile activating without scholar confirmation. (Kong §7.4.6 anchor rejects domain-*autonomous* judgment, i.e. an agent silently deciding evidence standards; a suggested-then-confirmed default is not autonomous.)
- **Advisory only.** A profile changes which evidence types / provenance the literature search *looks for and admits*. It does NOT change the A-F Overall Grade, and it does NOT block manuscript ship.
- **Override is first-class.** The scholar may override the profile mid-pipeline. `intake_agent` appends a new `selections[]` entry recording the override (Change A / INVARIANT 3); on a fresh `academic-paper` invocation that re-runs intake, the override is just the next intake entry. The scholar may know their sub-field better than the profile.
- **No ledger ⇒ neutral (the only fallback shape).** Any run that does not pass through `intake_agent` produces no Schema 13 ledger: a standalone `deep-research` run, a mid-entry pipeline start (e.g. user enters at Stage 2.5 with an existing draft), or any path that skips intake. In every such case `literature_strategist_agent`, if it runs, takes the neutral `unknown_user_defined` fallback (INVARIANT 4 case (a) — absent ledger). This is intentional and safe: with no scholar-confirmed profile, neutral evidence standards are the conservative default. The profile is therefore "asked at intake when intake runs" — there is no claim that every possible entry path asks for it.
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
| Q1 schema placement | A **new standalone Schema 13 `domain_evidence_profile`**, modeled on Schema 10's Material-Passport-carrier / consumer pattern but independent of it, and **produced by `intake_agent`** (see Change A/B). | *(Revised after dual-track R1 P1-A, R2 P0-1, R4 P0-2.)* R1: the brainstorm first chose to ride Schema 10, but Schema 10 (Style Profile) has required style fields and intake sets `style_profile: null` when the scholar provides no writing samples (`intake_agent.md:195-196`). A no-sample run would then have nowhere valid to store the profile, or would have to emit an invalid Style Profile. A standalone Schema 13 keeps each schema's null-behavior independent and its responsibility single. R2→R4 producer journey: R2 found the R1 intake producer was upstream-invisible to the Stage-1 consumer `source_verification_agent`, and R3 moved the producer to the orchestrator's pre-Stage-1 window; but R4 P0-2 found the Material Passport does not exist pre-Stage-1, so that relocation could not actually serve a Stage-1 consumer. The resolution (option c) was to drop `source_verification_agent` as a consumer — which removes the reason to move the producer at all — so the producer **returns to `intake_agent`**, now with `literature_strategist_agent` (same skill, later phase) as the sole, correctly-ordered consumer. The two configs still have different lifecycles (Style Profile is optional-on-demand; domain profile is asked at intake when intake runs). |
| Q2 naming reconciliation | **Replace** the field-centric `Field-Specific Adjustments` table in `source_quality_hierarchy.md` with a profile-centric table, and keep a short legacy mapping note. | Two normative tables (field-centric vs profile-centric) would contradict. Profiles become the active contract; old field labels remain only as a migration/background note. Verified: no production consumer parses the old table's rows (only two reference-pointer mentions: `deep-research/SKILL.md:392`, `source_verification_agent.md:38`). |
| Q3 #246 forward-dependency | Add a **forward-reference note** in the profile section; do NOT pull aggregation into #259, do NOT ship placeholder logic. | #246 (grade aggregation) is unbuilt and the maintainer is doing #259 first. A forward note avoids a dangling cross-link without scope-creeping #259 into #246. |
| Q4 profile granularity | Add a `## Domain Evidence Profiles` section + a 4-row structured table **inside `source_quality_hierarchy.md`**. Do NOT create a `deep-research/references/domain_profiles/` directory of per-profile files. | 4 profiles (3 real, 1 neutral fallback), advisory-only, no aggregation, do not justify a directory of mini-specs. A single dedicated section keeps the agent reading one file while giving enough structure to consume reliably. Split into files only when profiles grow long, are independently maintained, or are reused by tooling. |

## Change set (4 edits)

> Round history: R2 P0-1 / R3 split this into 6 edits (orchestrator producer + two consumers). R4 P0-2 + option-c resolution collapsed it back: `source_verification_agent` is no longer a consumer (so old **Change D** is dropped), and the producer returns to `intake_agent` (so the R3 **B1/B2** split collapses back to a single **Change B**). Net: **A (schema), B (intake produces), C (profile definitions), E (literature_strategist consumes)**. There is no Change D.

### A. New Schema 13 — `shared/handoff_schemas.md`

Add a **new standalone Schema 13 `domain_evidence_profile`** (NOT a block on Schema 10 — see Q1 rationale). **Producer: `intake_agent`** (`academic-paper` Stage 2, new Step 12, Change B). **Carrier: `academic-pipeline` Material Passport** as an optional field, exactly as Schema 10 is carried (`shared/handoff_schemas.md:675`; does not affect integrity/review stages). This Material Passport is the **single canonical home**; if the profile is also surfaced in the academic-paper Paper Configuration Record, that is a *display/summary* echo only (mirroring how `Style Profile` appears as a PCR row at `intake_agent.md:238` while the authoritative Schema 10 lives in the passport) — the consumer MUST read the passport ledger, never the PCR row (closes R2 P1-1). **Sole consumer: `literature_strategist_agent`** (`academic-paper` Stage 2, Phase 1). Producer (intake, Phase 0) runs before the consumer (Phase 1) within the same skill; the passport already exists at intake time. `source_verification_agent` is NOT a consumer (R4 option c — see Scope).

The schema is a **single append-only event ledger** — there is no separate mutable `selected` scalar to drift out of sync with history (dual-track R1 P1-B). The active profile is *derived*, not stored.

```yaml
domain_evidence_profile:
  selections:                          # append-only ledger; >= 1 entry once intake (Step 12) runs. Whole-schema absence OR an empty selections[] array = neutral pre-#259 behavior (see resolution rule).
    - at: 2026-05-29T09:00:00Z
      stage: "intake"                  # the producing step (academic-paper intake, Step 12)
      requested: cs_ml                 # what the scholar asked for (one of the 4 ship-ready or 5 reserved values)
      effective: cs_ml                 # what actually applies after the reserved-fallback rule
      fallback_reason: null            # null unless requested ∈ reserved; then effective MUST be unknown_user_defined and this names the requested reserved value
    - at: 2026-05-29T09:05:00Z          # a scholar override before Phase 1 is just another appended entry, also written by intake
      stage: "intake"
      requested: humanities_interpretive
      effective: humanities_interpretive
      fallback_reason: null
```

`stage` is a free-text provenance label (which step recorded the entry), NOT an ordering key — resolution does not compare `stage` values (R4 P0-1: ARS stages like `2.5` / `3'` / `RE-REVIEW` have no total order, so any stage-comparison rule would be unimplementable).

**Active-profile resolution rule (the load-bearing definition):** the active profile is the `effective` value of the **last (most recently appended) `selections[]` entry**. If the ledger / `selections[]` is absent or empty, the consumer applies the neutral `unknown_user_defined` fallback (INVARIANT 4). The consumer MUST resolve via "last entry's `effective`" — it MUST NOT read any other field, and MUST NOT read the PCR display row, as the active profile.

*Why "last entry" is safe here (R4 P1-7 follow-up):* the R3 stage-bound rule existed only to stop a later-stage override from leaking backward to a Stage-1 consumer on reset/resume. With `source_verification_agent` removed, the sole consumer `literature_strategist_agent` runs once in Phase 1, and the `academic-paper revision` loop is `8→5→6` (`academic-paper/SKILL.md:270`) — it does **not** re-run Phase 1. So no consumer ever re-executes at a point earlier than an override, and "last entry" cannot leak a future selection backward. **Forward note:** if a future release re-adds an earlier-running consumer (e.g. restores `source_verification_agent`, or a mode that re-runs Phase 1 after a later-stage override), the reset/resume leak (R2 P1-7) must be re-evaluated and a deterministic ordering key (e.g. a monotonic `sequence` integer per entry) introduced then. It is deliberately omitted now as unneeded complexity for a single Phase-1 consumer.

Field rules (prose validation, mirroring Schema 10/11 style — NO separate JSON Schema file):

- `requested` MUST be one of the 4 ship-ready values OR one of the 5 reserved values — nothing else (closes R2 P1-2: a free-form or off-list `requested` is invalid).
- `effective` MUST be one of the 4 ship-ready enum values.
- **`requested`/`effective` coherence (closes R2 P1-2):** if `requested` is a ship-ready value, `effective` MUST equal `requested` and `fallback_reason` MUST be `null`. If `requested` ∈ {`clinical`, `wet_lab`, `materials_physics`, `legal_case_based`, `education`} (reserved), then `effective` MUST be `unknown_user_defined` and `fallback_reason` MUST be a non-null string naming the requested reserved value. No other `requested`/`effective` combination is valid (this forbids e.g. `requested: general_social_science, effective: cs_ml`, which would silently override the scholar's confirmed selection).
- `selections[]` is append-only: never reorder, never overwrite, never delete an entry (mirrors `reset_boundary[]` / `compliance_history[]`).
- **Malformed-ledger carve-out (closes R2 P1-8):** the general handoff convention (`shared/handoff_schemas.md:7-9`) is that a consumer validating a schema violation requests re-generation / raises `HANDOFF_INCOMPLETE`. Schema 13 **explicitly overrides** that convention: a malformed Schema 13 ledger, or a resolved `effective` outside the 4 enum values (e.g. a hallucinated name), MUST NOT block or trigger `HANDOFF_INCOMPLETE` — the consumer falls back to neutral `unknown_user_defined` and emits a one-line `[PROFILE-UNRESOLVED]` advisory (INVARIANT 4 case (c)). This is the advisory-only contract; a domain-profile defect must never halt the pipeline.

### B. Intake production — `academic-paper/agents/intake_agent.md`

`intake_agent` is the **producer** of the Schema 13 ledger. Add a profile-selection step as a **new intake step** (numbered after the current Step 11 Funding, e.g. **Step 12: Domain Evidence Profile**). intake (Phase 0) runs before the sole consumer `literature_strategist_agent` (Phase 1), and the Material Passport already exists at intake time, so producer and consumer are correctly ordered within `academic-paper` with no cross-skill carrier hop (this is what option c buys — R4 P0-2 is gone, not merely mitigated).

- Present the 4 ship-ready profiles as an explicit choice; `unknown_user_defined` is the default if the scholar does not pick or is unsure.
- List the 5 reserved profiles with the explicit note that selecting one records `requested: <reserved>`, `effective: unknown_user_defined`, a non-null `fallback_reason`, **and surfaces an advisory** ("this domain has no profile yet — falling back to neutral evidence standards").
- `intake_agent` MAY *suggest* a default profile inferred from a deep-research handoff or its Step 1 topic interview, but the scholar MUST confirm; nothing auto-activates (see Boundary "No auto-SELECT").
- It is NOT folded into Step 10 Style Calibration (Step 10 is writing-sample calibration the scholar frequently declines, `style_profile: null`; the domain profile is a separate concern with a separate lifecycle).
- Write the result as the first `selections[]` entry of the Schema 13 ledger in the Material Passport. The active profile MAY also be echoed as a Paper Configuration Record display row (like `Style Profile`), but the authoritative copy is the passport ledger (Change A) — the PCR row is never the source of truth for the consumer (INVARIANT 10).
- **Mid-pipeline override:** if the scholar later changes the profile (e.g. on a fresh `academic-paper` invocation that re-runs intake, or an in-session correction before Phase 1), `intake_agent` appends a new `selections[]` entry. Because the only consumer runs once in Phase 1 after intake, the override is visible to it whenever it is recorded before Phase 1 (closes R2 P1-6 — the override has a concrete producer, `intake_agent`, and a concrete execution path).
- **plan mode is exempt (closes R2 P2-2):** the plan-mode simplified 3-question intake (`intake_agent.md:95-104`, `:263`) does NOT run Step 12. A plan-mode run produces no ledger; `literature_strategist_agent`, if reached, takes the neutral `unknown_user_defined` fallback. (plan mode is a lightweight structure-planning mode; domain evidence-standard tuning has low value there and the simplified intake stays simple.)

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

### E. literature_strategist consumption — `academic-paper/agents/literature_strategist_agent.md`

`literature_strategist_agent` is the **sole consumer** of the profile (R4 option c). A profile must influence BOTH retrieval AND the post-retrieval screening gates, otherwise the existing gates silently neutralize a profile-specific search (dual-track R1 P1-C). It resolves the active profile per the Change A rule (the active profile = `effective` of the last `selections[]` entry; read the Material Passport ledger, not a PCR row) with three graceful-fallback cases: (a) ledger absent OR `selections[]` empty; (b) resolved `effective` = `unknown_user_defined`; (c) ledger malformed OR resolved value not one of the 4 enum values OR the resolved entry violates `requested`/`effective` coherence (INVARIANT 12) — case (c) emits a one-line `[PROFILE-UNRESOLVED]` advisory; no case blocks (closes R2 P1-5 + R4 P1-4, the latter adding the coherence check the consumer must perform rather than trusting the producer).

**Loosen-only / additive contract (closes R2 P2-1, realizes INVARIANT 5).** Every sub-edit below is *monotonic admit-only*: under a non-neutral profile a gate may **admit an evidence type it would otherwise wrongly exclude**, but it MUST NOT exclude, down-rank, or fail any source that the neutral gate currently admits. Where a gate combines neutral and profile criteria, combine by **OR (union of admissible)**, never by replacement. The four sub-edits, all reverting to current behavior under fallback cases (a)/(b)/(c):

1. **Search strategy** (`### Step 2: Database Selection`, `### Step 3: Search String Construction`, ~lines 45-57): **add** profile-relevant databases + search strings (e.g. `cs_ml` → also query arXiv / ACL Anthology / proceedings; `humanities_interpretive` → also query monographs / archival / primary sources). Additive — never drops a database the neutral strategy would have queried.
2. **Screening decision tree** (`### Literature Screening Decision Tree`, ~line 413): the current tree excludes non-peer-reviewed unless gov/white-paper gray literature, which would drop `cs_ml` preprints and `humanities_interpretive` archival/primary sources. Add a profile-aware branch so the profile's standard evidence types are **additionally admissible** (preprints includable under `cs_ml`, primary/archival sources includable under `humanities_interpretive`), tagged by type rather than excluded. The branch only *adds* admit paths; nothing the neutral tree admits becomes excluded.
3. **Quality quick-assessment checklist** (`### Literature Quality Quick Assessment Checklist`, ~line 436): the existing 5-item quick-assessment total score penalizes preprints/archival. Under a non-neutral profile, a source passes if it **meets the neutral quick-assessment outcome OR meets the profile's evidence-type expectations** (union, not replacement — closes R2 P2-1 + R4 P2-6: the wording says "neutral quick-assessment outcome", not "journal-ranking bar", because the existing gate is a multi-item score not a journal-ranking gate; a source that passes the neutral score must still pass even if it does not match the profile).
4. **Quality gates** (`## Quality Gates`, ~line 468): the `>= 70% peer-reviewed` (line 479) and `>= 50% currency` (line 480) pass criteria contradict `humanities_interpretive` (primary/older canonical texts) and `cs_ml` (preprints). Make these gates profile-relative **in the loosening direction only**: under a non-neutral profile the admissible set *expands* (preprints count toward the `cs_ml` peer-reviewed-equivalent ratio; canonical texts do not count against `humanities_interpretive` currency). The thresholds are never raised, and a corpus that passes the neutral gate always passes the profile-relative gate.

This composes with the existing `## Distributional Skew Advisory (Kong #257)` section without contradicting it (skew advisory measures distribution; profile sets admissibility — orthogonal).

## Acceptance mapping (incl. deliberate divergences)

| Issue acceptance criterion | How this spec satisfies it | Divergence |
|----------------------------|----------------------------|------------|
| #1 Intake adds `domain_evidence_profile` with enum = 4 ship-ready values + default `unknown_user_defined` | Change A (new Schema 13 ledger) + Change B (intake Step 12 produces it) | aligned |
| #2 `deep-research/references/domain_profiles/` directory + 4 profile md files | **Changed to** a `## Domain Evidence Profiles` section + 4-row table inside `source_quality_hierarchy.md` (Change C) | **DIVERGES** — maintainer-approved (Q4): single dedicated section, not a directory, since 4 advisory profiles with no aggregation do not justify a mini-spec directory. To be noted on #259 at close. |
| #3 Reserved profile list documented with "not in enum yet" note | Change A (block rules) + Change C (reserved-note column + reserved list) | aligned |
| #4 `source_verification_agent.md` + `literature_strategist_agent.md` consume the profile | **Only `literature_strategist_agent` consumes it** (Change E). `source_verification_agent` is dropped from the consumer set. | **DIVERGES** — maintainer-approved (R4 option c, 2026-05-29): `source_verification_agent` runs in deep-research (Stage 1), upstream of the producer (intake, Stage 2), and serving it would require re-architecting the Material Passport lifecycle (R4 P0-2). Its domain-aware verification is deferred (see Out of scope). To be noted on #259 at close. |
| #5 #246 cross-links to relevant profiles | **Changed to** a forward-reference note (Change C.3), because #246 is not yet implemented | **DIVERGES** — maintainer-approved (Q3): forward-reference note instead of a live cross-link, to avoid a dangling reference. The live cross-link lands when #246 ships. |
| #6 User can override profile mid-pipeline, recorded in Material Passport | Schema 13 append-only `selections[]` ledger; an override is an appended entry written by `intake_agent` (Change B); active = last entry's `effective` (Change A) | aligned |

## INVARIANTS

1. **Enum cardinality.** The ship-ready enum (`effective` values) is exactly 4 (`general_social_science`, `cs_ml`, `humanities_interpretive`, `unknown_user_defined`); the 5 reserved values (`clinical`, `wet_lab`, `materials_physics`, `legal_case_based`, `education`) are NOT in the `effective` enum (they may appear only as `requested`).
2. **Reserved fallback (per entry).** A `selections[]` entry with `requested` ∈ reserved → `effective: unknown_user_defined` + non-null `fallback_reason` naming the requested value + an explicit intake advisory. No reserved profile ever silently activates a checklist.
3. **Active-profile resolution.** The active profile is the `effective` value of the **last (most recently appended) `selections[]` entry** — nothing else. An override is a new appended entry; there is no mutable scalar that can drift from history. `stage` is a provenance label, not an ordering key (R4 P0-1). Safe because the sole consumer runs once in Phase 1 and the revision loop does not re-run Phase 1, so no consumer re-executes earlier than an override; a forward note in Change A flags re-evaluation if a future earlier-running consumer is added. (Closes R1 P1-B; supersedes the R3 stage-bound rule per R4 P0-1 + P1-7-followup.)
4. **Graceful fallback.** Absent ledger / empty `selections[]` / resolved value not in the 4 enum (incl. hallucinated names) / a resolved entry that violates `requested`/`effective` coherence (INVARIANT 12) / `unknown_user_defined` → the consumer applies the current neutral single-pyramid behavior, unchanged, with no block; the malformed/non-enum/incoherent case also emits `[PROFILE-UNRESOLVED]`. Schema 13 explicitly overrides the general `HANDOFF_INCOMPLETE` convention so a profile defect never blocks. (Incorporates R2 P1-8 + empty-array R2 P2-4 + coherence-check R4 P1-4.)
5. **Advisory only.** A profile never changes the A-F Overall Grade and never blocks manuscript ship. In `literature_strategist`, profile-relative gates are **monotonic admit-only**: they only *admit* evidence types the neutral gates would wrongly exclude (combining by OR / union), and never exclude, down-rank, or fail any source the neutral gate currently admits. (R2 P2-1 hardened the wording.)
6. **No auto-SELECT.** No agent activates a `domain_evidence_profile` without scholar confirmation. The producer is `intake_agent`; discipline *inference* (deep-research handoff or Step 1 topic interview) MAY suggest a default, but the scholar confirms. (Distinct from prohibiting discipline inference outright — R1 P2.)
7. **No discipline loses existing guidance.** Replacing the 6-row field-centric table MUST account for every row: Social Science / Technology / Humanities / **Policy** fold their substance into ship-ready profile rows (Policy → `general_social_science`); Medicine/Health + Education are preserved verbatim in a **historical, non-normative** legacy note whose runtime behavior is neutral `unknown_user_defined` until their reserved profiles ship. No row is dropped, and the preserved note is non-normative (no "applies until" normative claim). (Closes R1 P1-D + R2 P1-3 + R2 P1-4.)
8. **#246 boundary.** #259 references grade aggregation as a forward dependency only; it ships no aggregation logic and no placeholder aggregation code.
9. **Single normative profile table.** After Change C, `source_quality_hierarchy.md` has exactly one normative profile table; the old field-centric table is reduced to a non-normative legacy mapping note (which still carries the preserved Medicine/Education text per INVARIANT 7).
10. **Single canonical carrier.** The Material Passport Schema 13 ledger is the one authoritative home for the active profile. Any Paper Configuration Record echo is display-only; the consumer MUST read the passport ledger, never the PCR row. (Closes R2 P1-1.)
11. **No intake ⇒ no ledger ⇒ neutral.** Any run that does not pass through `intake_agent` — a standalone `deep-research` run, a mid-entry pipeline start (e.g. entering at Stage 2.5 with an existing draft), or any path skipping intake — produces no ledger; `literature_strategist_agent`, if it runs, takes the neutral `unknown_user_defined` fallback (INVARIANT 4 case (a)). The profile is "asked at intake when intake runs"; there is no claim that every entry path asks for it. (R4 P1-3 generalized the R3 deep-research-only exception to every intake-skipping path.)
12. **`requested`/`effective` coherence.** Every `selections[]` entry has `requested` ∈ {4 ship-ready ∪ 5 reserved}; if ship-ready, `effective == requested` and `fallback_reason` is null; if reserved, `effective == unknown_user_defined` with non-null `fallback_reason`. No other combination is valid — a clean-resolving entry can never silently differ from the scholar's confirmed selection. The consumer also re-checks this coherence and treats a violation as a fallback case (INVARIANT 4), so a producer bug cannot smuggle an incoherent-but-enum-valid `effective` past the gate. (Closes R2 P1-2 + R4 P1-4.)

## Test strategy

Prose schema (mirrors Schema 10 / #256 commitment ledger — no JSON Schema file). The checker is **honest about its reach**: a markdown structural checker verifies *documentation surface* (presence/shape of required text), NOT runtime semantics. Dual-track R1 P2 flagged that several INVARIANTS are semantic; the split below makes that explicit.

**`scripts/check_domain_evidence_profile.py` — documentation-surface checks (deterministic):**

1. Schema 13 documents exactly the 4 `effective` enum values + the 5 reserved values; the active-profile resolution rule text ("last entry's `effective`") is present; the `requested`/`effective` coherence rule and the malformed-ledger carve-out text are present (INVARIANTS 1, 3, 4, 12).
2. `source_quality_hierarchy.md` has a `## Domain Evidence Profiles` section with a 4-profile table whose gaps column is "Critical gaps to surface" (NOT "disqualifying"), plus the 5 reserved names with the "not in enum" note (INVARIANTS 1, 2, 5).
3. The consumer agent (`literature_strategist_agent`) contains a "resolve `domain_evidence_profile`" instruction AND the graceful-fallback cases (absent/empty / non-enum incl. hallucinated / incoherent / `unknown_user_defined`) (INVARIANT 4). It also confirms `source_verification_agent` is NOT given a profile-resolution step (option c).
4. `source_quality_hierarchy.md` carries the advisory-only statement + the #246 forward-reference note (INVARIANTS 5, 8).
5. The old field-centric table is demoted to a legacy note that is labeled non-normative AND still contains the preserved Medicine/Health + Education text; the `general_social_science` profile row references the folded **Policy** substance (INVARIANTS 7, 9 — Policy guard added per R2 P1-4).
6. Schema 13 names `intake_agent` as producer + Material Passport as the single canonical carrier + `literature_strategist_agent` as sole consumer (INVARIANTS 6, 10).

**Negative fixtures + mutation test (`scripts/test_check_domain_evidence_profile.py`):** deliberately (a) add a 5th `effective` enum value, (b) rename the gaps column back to "disqualifying", (c) strip one graceful-fallback case, (d) delete the preserved Medicine/Education text, (e) **remove the malformed-ledger carve-out text**, (f) **remove the Policy fold reference** — each must make the checker FAIL (so it cannot trivially accept-all). Wired into `.github/workflows/spec-consistency.yml`.

**Out of the checker's reach — relies on plan-stage review + worked example:** INVARIANT 2's runtime reserved-fallback behavior; INVARIANT 5's no-grade/no-block runtime behavior **and its monotonic admit-only ("never tighten") half** (a markdown surface checker cannot verify that a gate only loosens); INVARIANT 6's no-auto-SELECT; INVARIANT 8's no-aggregation-logic; INVARIANT 11's no-intake-no-profile runtime path. These are agent-prompt semantics. The implementation plan MUST include worked examples exercising (i) a reserved-fallback and (ii) a scholar override at intake; the dual-track reviewers verify the prompt text — the linter does not claim to enforce these.

## Out of scope (forward work)

- **#246** discipline-relative grade aggregation (Overall Grade formula). #259 only forward-references it.
- Reserved profiles (`clinical` / `wet_lab` / `materials_physics` / `legal_case_based` / `education`) ship per demand in later releases.
- **`source_verification_agent` domain-aware verification (deferred — R4 option c).** Making `source_verification_agent` profile-aware (IRB checks for clinical, reagent-provenance for wet-lab, primary-source verification for humanities, etc.) requires the profile to be available in deep-research at Stage 1, which the current Material Passport lifecycle does not support (the passport accompanies artifacts between stages and is written at handoffs, not pre-Stage-1 — R4 P0-2). A future release can address this by either re-architecting the passport's pre-Stage-1 existence or producing a deep-research-stage profile. Until then, only `literature_strategist_agent` is profile-aware. If that future work lands, re-evaluate the reset/resume ordering (the forward note in Change A).
- `citation_compliance_agent` profile integration (consistent with the v3.6.5 deferral of corpus integration for that agent).
- No JSON Schema file for `domain_evidence_profile` (Schema 13 is a prose schema, mirroring the Schema 10 / #256 commitment-ledger convention).
- Profile-relative grade aggregation (#246) — only forward-referenced; the A-F lookup is unchanged.
- Passport reset/resume semantics for the Schema 13 ledger need no special-casing **for the current single Phase-1 consumer**: the active profile is "last appended entry", and the only consumer (`literature_strategist_agent`, Phase 1) runs once before any later-stage override and is not re-run by the revision loop (`8→5→6`), so it can never observe a future override. The R3 stage-bound rule (added for the now-removed Stage-1 consumer) is therefore dropped as unimplementable-and-unneeded (R4 P0-1). **Forward note:** re-introducing an earlier-running consumer reopens the R2 P1-7 reset/resume leak and would require a deterministic ordering key (e.g. a monotonic `sequence` per entry) at that time.
