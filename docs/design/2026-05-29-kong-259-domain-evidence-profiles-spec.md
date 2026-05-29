# Kong #259 — Discipline-Relative Domain Evidence Profiles

**Status:** prompt + new Schema 13 (standalone) + reference-doc design
**Date:** 2026-05-29
**Issue:** #259 (Tier A, `[ACCEPT-MEDIUM]`; attaches to #244 epic alongside #246)
**Scope:** Let a scholar select a `domain_evidence_profile` at intake so that `source_verification_agent` and `literature_strategist_agent` adjust their evidence checklist / search strategy to the scholar's discipline, instead of applying a single Western evidence-based-medicine (EBM) pyramid to every field. Advisory only, scholar-selected, no auto-detect, override first-class.

**Anchor:** Kong et al. 2026 (arXiv:2605.18661) §7.4.6 (`kong2026_full.txt:L2213-L2227`, PDF p.39): "Extending AI-assisted research to chemistry, biology, medicine, materials science, physics, and social science requires more than retraining on domain papers. These fields differ in evidence standards, experimental infrastructure, safety constraints, data availability, and community norms."

## Boundary

This patch is the **profile-selection** layer. It is a checklist/search adjustment, not an autonomous grading or domain-detection layer.

- **No auto-SELECT.** The scholar selects the `domain_evidence_profile` at intake; nothing auto-selects it. This does NOT prohibit the existing intake behavior of *inferring the discipline* from a deep-research handoff or Step 1 (`intake_agent.md:39`, `:112`) — that inference may be used to *suggest a default* profile to the scholar, but the scholar must confirm. The prohibition is specifically on a profile activating without scholar confirmation. (Kong §7.4.6 anchor rejects domain-*autonomous* judgment, i.e. an agent silently deciding evidence standards; a suggested-then-confirmed default is not autonomous.)
- **Advisory only.** A profile changes which evidence types / provenance an agent *looks for and surfaces*. It does NOT change the A-F Overall Grade, and it does NOT block manuscript ship.
- **Override is first-class.** The scholar may override the profile mid-pipeline; the override is recorded in the Material Passport. The scholar may know their sub-field better than the profile.
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
| Q1 schema placement | A **new standalone Schema 13 `domain_evidence_profile`**, modeled on Schema 10's producer / Material-Passport-carrier / consumer pattern but independent of it. | *(Revised after dual-track R1 P1-A.)* The brainstorm first chose to ride Schema 10, but Schema 10 (Style Profile) has required style fields and intake sets `style_profile: null` when the scholar provides no writing samples (`intake_agent.md:191-196`). A no-sample run would then have nowhere valid to store the profile, or would have to emit an invalid Style Profile. The two configs also have different lifecycles (Style Profile is optional-on-demand; domain profile is asked every run). A standalone Schema 13 keeps each schema's null-behavior independent and its responsibility single. The "ceremony" cost codex first flagged is now justified by a concrete correctness problem. |
| Q2 naming reconciliation | **Replace** the field-centric `Field-Specific Adjustments` table in `source_quality_hierarchy.md` with a profile-centric table, and keep a short legacy mapping note. | Two normative tables (field-centric vs profile-centric) would contradict. Profiles become the active contract; old field labels remain only as a migration/background note. Verified: no production consumer parses the old table's rows (only two reference-pointer mentions: `deep-research/SKILL.md:392`, `source_verification_agent.md:38`). |
| Q3 #246 forward-dependency | Add a **forward-reference note** in the profile section; do NOT pull aggregation into #259, do NOT ship placeholder logic. | #246 (grade aggregation) is unbuilt and the maintainer is doing #259 first. A forward note avoids a dangling cross-link without scope-creeping #259 into #246. |
| Q4 profile granularity | Add a `## Domain Evidence Profiles` section + a 4-row structured table **inside `source_quality_hierarchy.md`**. Do NOT create a `deep-research/references/domain_profiles/` directory of per-profile files. | 4 profiles (3 real, 1 neutral fallback), advisory-only, no aggregation, do not justify a directory of mini-specs. A single dedicated section keeps the agent reading one file while giving enough structure to consume reliably. Split into files only when profiles grow long, are independently maintained, or are reused by tooling. |

## Change set (5 edits)

### A. New Schema 13 — `shared/handoff_schemas.md`

Add a **new standalone Schema 13 `domain_evidence_profile`** (NOT a block on Schema 10 — see Q1 rationale). Producer: `intake_agent` (new step, Change B). Carrier: `academic-pipeline` Material Passport as an optional field, exactly as Schema 10 is carried (does not affect integrity/review stages). Consumers: `source_verification_agent`, `literature_strategist_agent`.

The schema is a **single append-only event ledger** — there is no separate mutable `selected` scalar to drift out of sync with history (dual-track R1 P1-B). The active profile is *derived*, not stored.

```yaml
domain_evidence_profile:
  selections:                          # append-only ledger; >= 1 entry once intake runs. Absence of the whole schema = neutral pre-#259 behavior.
    - at: 2026-05-29T09:00:00Z
      stage: "intake"
      requested: cs_ml                 # what the scholar asked for (may be a reserved value)
      effective: cs_ml                 # what actually applies after the reserved-fallback rule
      fallback_reason: null            # null unless requested ∈ reserved; then effective MUST be unknown_user_defined and this names the requested reserved value
    - at: 2026-05-29T11:00:00Z          # a later mid-pipeline override is just another appended entry
      stage: "2"
      requested: humanities_interpretive
      effective: humanities_interpretive
      fallback_reason: null
```

**Active-profile resolution rule (the load-bearing definition):** the active profile is the `effective` value of the **last** `selections[]` entry. Consumers MUST resolve via "last entry's `effective`" — they MUST NOT read any other field as the active profile. This single rule resolves both R1 P1-B sub-problems: an override is just an appended entry (no scalar to contradict), and a reserved-fallback is captured per-entry (the `requested`/`effective`/`fallback_reason` triple travels together, so history is never lost and never contradicts the active value).

Field rules (prose validation, mirroring Schema 10/11 style — NO separate JSON Schema file):

- `effective` MUST be one of the 4 enum values. `requested` MAY be a reserved value.
- Reserved-fallback (per entry): if `requested` ∈ {`clinical`, `wet_lab`, `materials_physics`, `legal_case_based`, `education`}, then `effective` MUST be `unknown_user_defined` and `fallback_reason` MUST be a non-null string naming the requested reserved value. Otherwise `fallback_reason` is `null`.
- `selections[]` is append-only: never reorder, never overwrite, never delete an entry (mirrors `reset_boundary[]` / `compliance_history[]`).

### B. Intake production — `academic-paper/agents/intake_agent.md`

Add a **new intake step** (numbered after the current Step 11 Funding, e.g. **Step 12: Domain Evidence Profile**). It is NOT folded into Step 10 Style Calibration: Step 10 is writing-sample calibration that the scholar frequently declines (`style_profile: null`), whereas the domain profile is asked every run. They are separate concerns with separate lifecycles.

- Present the 4 ship-ready profiles as an explicit choice; `unknown_user_defined` is the default if the scholar does not pick or is unsure.
- List the 5 reserved profiles with the explicit note that selecting one records `requested: <reserved>`, `effective: unknown_user_defined`, a non-null `fallback_reason`, **and surfaces an advisory** ("this domain has no profile yet — falling back to neutral evidence standards").
- The agent MAY *suggest* a default profile inferred from the deep-research handoff / Step 1 discipline, but the scholar MUST confirm; nothing auto-activates (see Boundary "No auto-SELECT").
- Write the result as the first `selections[]` entry of the Schema 13 ledger, attached to the Paper Configuration Record (same home as `style_profile`).

### C. Profile definitions — `deep-research/references/source_quality_hierarchy.md`

Three edits:

1. **Replace** the `## Field-Specific Adjustments` table (lines ~132-143) with a profile-centric framing. To avoid silently dropping the existing per-field guidance (dual-track R1 P1-D), the new profile table MUST **carry forward the substance** of the existing rows: the `general_social_science`, `cs_ml`, `humanities_interpretive` profiles absorb the Social Science / Technology / Humanities rows respectively. The Medicine/Health and Education rows map to **reserved** profiles (`clinical`, `education`) that fall back to neutral — so their existing adjustment text MUST be **preserved verbatim in the legacy mapping note** (not deleted) and explicitly labeled "applies until the `clinical` / `education` profile ships; current behavior = neutral `unknown_user_defined`." Net: no discipline loses guidance it has today.

   Legacy mapping (old field label → nearest profile):
   - Social Science → `general_social_science` *(substance folded into profile row)*
   - Technology → `cs_ml` *(substance folded into profile row)*
   - Humanities → `humanities_interpretive` *(substance folded into profile row)*
   - Policy → `general_social_science` *(closest ship-ready; policy has no dedicated profile)*
   - Medicine/Health → `clinical` *(reserved; existing row text preserved in legacy note, behavior = neutral until profile ships)*
   - Education → `education` *(reserved; existing row text preserved in legacy note, behavior = neutral until profile ships)*

2. **Add** a `## Domain Evidence Profiles` section with a 4-row table. Columns: `Profile` / `Standard evidence types` / `Common provenance requirements` / `Critical gaps to surface` / `Reserved-note`. (The gaps column is named "Critical gaps to surface" — NOT "disqualifying" — because the profile is advisory: it tells the agent what weaknesses to *flag*, it never disqualifies a source or changes the grade. Dual-track R1 P2.) Plus a separate short list of the 5 reserved profiles with the "not in enum" note.

3. **Add** a `#246` forward-reference note: "Discipline-relative *grade aggregation* (how these evidence expectations roll up into an Overall Grade) is tracked separately in #246 and is not yet implemented; until then the A-F Overall Grade lookup above applies unchanged."

### D. source_verification consumption — `deep-research/agents/source_verification_agent.md`

In `## Verification Procedures` (line ~50), add a **Step 0: Resolve `domain_evidence_profile`**:

- Resolve the active profile = last `selections[]` entry's `effective` (Change A rule). If present and ≠ `unknown_user_defined`, adjust the verification checklist per that profile's `Standard evidence types` / `Common provenance requirements` / `Critical gaps to surface` from `source_quality_hierarchy.md`.
- **Graceful fallback (each case explicitly defined):** apply the current neutral 7-level-pyramid behavior unchanged when ANY of: (a) the Schema 13 ledger is absent; (b) the resolved `effective` is `unknown_user_defined`; (c) the ledger is malformed OR the resolved value is not one of the 4 enum values (e.g. a hallucinated profile name) — in case (c) also emit a one-line `[PROFILE-UNRESOLVED]` advisory. No case blocks.
- The profile adjusts what the agent *surfaces*; it does NOT change the A-F grade and does NOT block (advisory).

### E. literature_strategist consumption — `academic-paper/agents/literature_strategist_agent.md`

A profile must influence BOTH retrieval AND the post-retrieval screening gates, otherwise the existing gates silently neutralize a profile-specific search (dual-track R1 P1-C). Four sub-edits, all profile-aware and all reverting to current behavior when the profile is absent / `unknown_user_defined`:

1. **Search strategy** (`### Step 2: Database Selection`, `### Step 3: Search String Construction`, ~lines 45-57): bias database + search strings toward the profile's `Standard evidence types` (e.g. `cs_ml` → arXiv / ACL Anthology / proceedings; `humanities_interpretive` → monographs / archival / primary sources).
2. **Screening decision tree** (`### Literature Screening Decision Tree`, ~line 413): the current tree excludes non-peer-reviewed unless gov/white-paper gray literature, which would drop `cs_ml` preprints and `humanities_interpretive` archival/primary sources. Add a profile-aware branch so the profile's standard evidence types are admissible (e.g. preprints includable under `cs_ml`, primary/archival sources includable under `humanities_interpretive`), tagged by type rather than excluded.
3. **Quality quick-assessment checklist** (`### Literature Quality Quick Assessment Checklist`, ~line 436): the journal-ranking-weighted scoring penalizes preprints/archival. Note that under a non-neutral profile, the scoring uses the profile's evidence-type expectations rather than journal ranking alone.
4. **Quality gates** (`## Quality Gates`, ~line 468): the `>= 70% peer-reviewed` (line 479) and `>= 50% currency` (line 480) pass criteria contradict `humanities_interpretive` (primary/older canonical texts) and `cs_ml` (preprints). Make these gates profile-relative: under a non-neutral profile, the peer-reviewed/currency thresholds are interpreted against the profile's standard evidence mix (e.g. preprints count toward the `cs_ml` admissible ratio; canonical texts do not fail `humanities_interpretive` currency).

This composes with the existing `## Distributional Skew Advisory (Kong #257)` section without contradicting it (skew advisory measures distribution; profile sets admissibility — orthogonal).

## Acceptance mapping (incl. deliberate divergences)

| Issue acceptance criterion | How this spec satisfies it | Divergence |
|----------------------------|----------------------------|------------|
| #1 Intake adds `domain_evidence_profile` with enum = 4 ship-ready values + default `unknown_user_defined` | Change A (new Schema 13 ledger) + Change B (new intake Step 12) | aligned |
| #2 `deep-research/references/domain_profiles/` directory + 4 profile md files | **Changed to** a `## Domain Evidence Profiles` section + 4-row table inside `source_quality_hierarchy.md` (Change C) | **DIVERGES** — maintainer-approved (Q4): single dedicated section, not a directory, since 4 advisory profiles with no aggregation do not justify a mini-spec directory. To be noted on #259 at close. |
| #3 Reserved profile list documented with "not in enum yet" note | Change A (block rules) + Change C (reserved-note column + reserved list) | aligned |
| #4 `source_verification_agent.md` + `literature_strategist_agent.md` consume the profile | Changes D + E | aligned |
| #5 #246 cross-links to relevant profiles | **Changed to** a forward-reference note (Change C.3), because #246 is not yet implemented | **DIVERGES** — maintainer-approved (Q3): forward-reference note instead of a live cross-link, to avoid a dangling reference. The live cross-link lands when #246 ships. |
| #6 User can override profile mid-pipeline, recorded in Material Passport | Schema 13 append-only `selections[]` ledger; an override is an appended entry; active = last entry's `effective` (Change A) | aligned |

## INVARIANTS

1. **Enum cardinality.** The ship-ready enum (`effective` values) is exactly 4 (`general_social_science`, `cs_ml`, `humanities_interpretive`, `unknown_user_defined`); the 5 reserved values (`clinical`, `wet_lab`, `materials_physics`, `legal_case_based`, `education`) are NOT in the `effective` enum (they may appear only as `requested`).
2. **Reserved fallback (per entry).** A `selections[]` entry with `requested` ∈ reserved → `effective: unknown_user_defined` + non-null `fallback_reason` naming the requested value + an explicit intake advisory. No reserved profile ever silently activates a checklist.
3. **Active-profile resolution.** The active profile is the `effective` value of the LAST `selections[]` entry — nothing else. An override is a new appended entry; there is no mutable scalar that can drift from history. (Closes R1 P1-B.)
4. **Graceful fallback.** Absent ledger / resolved value not in the 4 enum (incl. hallucinated names) / `unknown_user_defined` → consuming agents apply the current neutral single-pyramid behavior, unchanged, with no block; case (c) also emits `[PROFILE-UNRESOLVED]`.
5. **Advisory only.** A profile never changes the A-F Overall Grade and never blocks manuscript ship. In `literature_strategist`, profile-relative gates only *admit* evidence types the neutral gates would wrongly exclude; they never tighten a gate to exclude something currently admitted.
6. **No auto-SELECT.** No agent activates a `domain_evidence_profile` without scholar confirmation. Existing discipline *inference* (handoff / Step 1) MAY suggest a default, but the scholar confirms. (Distinct from prohibiting discipline inference outright — R1 P2.)
7. **No discipline loses existing guidance.** Replacing the field-centric table MUST preserve every existing field row's substance: three fold into ship-ready profiles; Medicine/Health + Education are preserved verbatim in the legacy note with neutral current behavior until their reserved profiles ship. (Closes R1 P1-D.)
8. **#246 boundary.** #259 references grade aggregation as a forward dependency only; it ships no aggregation logic and no placeholder aggregation code.
9. **Single normative profile table.** After Change C, `source_quality_hierarchy.md` has exactly one normative profile table; the old field-centric table is reduced to a non-normative legacy mapping note (which still carries the preserved Medicine/Education text per INVARIANT 7).

## Test strategy

Prose schema (mirrors Schema 10 / #256 commitment ledger — no JSON Schema file). The checker is **honest about its reach**: a markdown structural checker verifies *documentation surface* (presence/shape of required text), NOT runtime semantics. Dual-track R1 P2 flagged that several INVARIANTS are semantic; the split below makes that explicit.

**`scripts/check_domain_evidence_profile.py` — documentation-surface checks (deterministic):**

1. Schema 13 documents exactly the 4 `effective` enum values + the 5 reserved values, and the active-profile resolution rule text ("last `selections[]` entry's `effective`") is present (INVARIANTS 1, 3).
2. `source_quality_hierarchy.md` has a `## Domain Evidence Profiles` section with a 4-profile table whose gaps column is "Critical gaps to surface" (NOT "disqualifying"), plus the 5 reserved names with the "not in enum" note (INVARIANTS 1, 2, 5).
3. Both consumer agents contain a "resolve `domain_evidence_profile`" instruction AND all three graceful-fallback cases (absent / non-enum incl. hallucinated / `unknown_user_defined`) (INVARIANT 4).
4. `source_quality_hierarchy.md` carries the advisory-only statement + the #246 forward-reference note (INVARIANTS 5, 8).
5. The old field-centric table is demoted to a legacy note AND that note still contains the preserved Medicine/Health + Education text (INVARIANTS 7, 9).

**Negative fixtures + mutation test (`scripts/test_check_domain_evidence_profile.py`):** deliberately (a) add a 5th `effective` enum value, (b) rename the gaps column back to "disqualifying", (c) strip one graceful-fallback case, (d) delete the preserved Medicine/Education text — each must make the checker FAIL (so it cannot trivially accept-all). Wired into `.github/workflows/spec-consistency.yml`.

**Out of the checker's reach — relies on plan-stage review + worked example:** INVARIANT 2's runtime reserved-fallback behavior, INVARIANT 5's no-grade/no-block runtime behavior, INVARIANT 6's no-auto-SELECT, INVARIANT 8's no-aggregation-logic. These are agent-prompt semantics. The implementation plan MUST include a worked example exercising a reserved-fallback and a mid-pipeline override, and the dual-track reviewers verify the prompt text — the linter does not claim to enforce these.

## Out of scope (forward work)

- **#246** discipline-relative grade aggregation (Overall Grade formula). #259 only forward-references it.
- Reserved profiles (`clinical` / `wet_lab` / `materials_physics` / `legal_case_based` / `education`) ship per demand in later releases.
- `citation_compliance_agent` profile integration (consistent with the v3.6.5 deferral of corpus integration for that agent).
- No JSON Schema file for `domain_evidence_profile` (Schema 13 is a prose schema, mirroring the Schema 10 / #256 commitment-ledger convention).
- Profile-relative grade aggregation (#246) — only forward-referenced; the A-F lookup is unchanged.
- Passport reset/resume semantics for the Schema 13 ledger: because `selections[]` is append-only and the active profile is "last entry's `effective`", a resume that replays the passport sees the same active profile; a reset that starts fresh re-asks at intake (consistent with how `style_profile` is re-derived). No special-casing needed — called out here so the implementation plan does not invent reset logic. (Closes dual-track R1 P2 passport-reset.)
