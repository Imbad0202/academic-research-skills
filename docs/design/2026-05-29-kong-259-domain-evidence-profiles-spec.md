# Kong #259 — Discipline-Relative Domain Evidence Profiles

**Status:** prompt + Schema 10 extension + reference-doc design
**Date:** 2026-05-29
**Issue:** #259 (Tier A, `[ACCEPT-MEDIUM]`; attaches to #244 epic alongside #246)
**Scope:** Let a scholar select a `domain_evidence_profile` at intake so that `source_verification_agent` and `literature_strategist_agent` adjust their evidence checklist / search strategy to the scholar's discipline, instead of applying a single Western evidence-based-medicine (EBM) pyramid to every field. Advisory only, scholar-selected, no auto-detect, override first-class.

**Anchor:** Kong et al. 2026 (arXiv:2605.18661) §7.4.6 (`kong2026_full.txt:L2213-L2227`, PDF p.39): "Extending AI-assisted research to chemistry, biology, medicine, materials science, physics, and social science requires more than retraining on domain papers. These fields differ in evidence standards, experimental infrastructure, safety constraints, data availability, and community norms."

## Boundary

This patch is the **profile-selection** layer. It is a checklist/search adjustment, not an autonomous grading or domain-detection layer.

- **No auto-detect.** The scholar selects the profile at intake. The agents never infer the discipline. (Kong §7.4.6 anchor explicitly rejects domain-autonomous judgment.)
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
| Q1 schema placement | Append an optional `domain_evidence_profile` block to **Schema 10 Style Profile** (do NOT create a new Schema 13). | Both are intake-time discipline config with the same producer / Material-Passport-carrier / agent-consumer pattern. Schema 10 already encodes "Discipline conventions = Priority 1 HARD". A new schema is ceremony; a bare Passport field underspecifies override semantics. |
| Q2 naming reconciliation | **Replace** the field-centric `Field-Specific Adjustments` table in `source_quality_hierarchy.md` with a profile-centric table, and keep a short legacy mapping note. | Two normative tables (field-centric vs profile-centric) would contradict. Profiles become the active contract; old field labels remain only as a migration/background note. Verified: no production consumer parses the old table's rows (only two reference-pointer mentions: `deep-research/SKILL.md:392`, `source_verification_agent.md:38`). |
| Q3 #246 forward-dependency | Add a **forward-reference note** in the profile section; do NOT pull aggregation into #259, do NOT ship placeholder logic. | #246 (grade aggregation) is unbuilt and the maintainer is doing #259 first. A forward note avoids a dangling cross-link without scope-creeping #259 into #246. |
| Q4 profile granularity | Add a `## Domain Evidence Profiles` section + a 4-row structured table **inside `source_quality_hierarchy.md`**. Do NOT create a `deep-research/references/domain_profiles/` directory of per-profile files. | 4 profiles (3 real, 1 neutral fallback), advisory-only, no aggregation, do not justify a directory of mini-specs. A single dedicated section keeps the agent reading one file while giving enough structure to consume reliably. Split into files only when profiles grow long, are independently maintained, or are reused by tooling. |

## Change set (5 edits)

### A. Schema 10 extension — `shared/handoff_schemas.md`

Add an **optional** `domain_evidence_profile` block to Schema 10 (currently at §"Schema 10: Style Profile", line ~671). Shape:

```yaml
domain_evidence_profile:
  selected: general_social_science   # enum: general_social_science | cs_ml | humanities_interpretive | unknown_user_defined
  fallback_reason: null              # string | null. Non-null ONLY when a reserved profile was requested and fell back. e.g. "requested 'wet_lab' (reserved, not in enum) — fell back to unknown_user_defined"
  override_history:                  # list, append-only. Empty at intake. One entry per mid-pipeline override.
    - changed_at: 2026-05-29T10:00:00Z
      from: unknown_user_defined
      to: cs_ml
      stage: "1"
      reason: "Scholar clarified this is an ML systems paper."
```

Field rules (prose validation, mirroring Schema 10/11 style — NO separate JSON Schema file):

- `selected` is required-within-the-block and MUST be one of the 4 enum values. The whole `domain_evidence_profile` block is optional on Schema 10; its absence = neutral pre-#259 behavior.
- `fallback_reason` is `null` unless a reserved profile was requested at intake; then `selected` MUST be `unknown_user_defined` and `fallback_reason` MUST be a non-null string naming the requested reserved profile.
- `override_history` is append-only, empty at intake, one entry per override (mirrors the append-only ledger pattern used by `reset_boundary[]` / `compliance_history[]`).

This block is carried by `academic-pipeline` Material Passport exactly as Style Profile is (optional field, does not affect integrity/review stages).

### B. Intake production — `academic-paper/agents/intake_agent.md`

Inside **Step 10: Style Calibration (Optional)** (line ~204 — already the discipline-conventions step), add a `domain_evidence_profile` selection sub-step:

- Present the 4 ship-ready profiles as a choice, with `unknown_user_defined` as default if the scholar does not pick.
- List the 5 reserved profiles with the explicit note that selecting one falls back to `unknown_user_defined` + records `fallback_reason`.
- NO auto-detect: the agent presents the choice; it never guesses from the topic/RQ.
- Record the result into the Schema 10 `domain_evidence_profile` block.

### C. Profile definitions — `deep-research/references/source_quality_hierarchy.md`

Three edits:

1. **Replace** the `## Field-Specific Adjustments` table (lines ~132-143) with a profile-centric framing. Keep a **legacy mapping note** so existing references stay intelligible. Explicit mapping (old field label → nearest profile):
   - Social Science → `general_social_science`
   - Technology → `cs_ml`
   - Humanities → `humanities_interpretive`
   - Medicine/Health → `clinical` *(reserved — falls back to `unknown_user_defined`)*
   - Education → `education` *(reserved — falls back to `unknown_user_defined`)*
   - Policy → `general_social_science` *(closest ship-ready; policy has no dedicated profile)*

   The note must state that field labels mapping to reserved profiles currently resolve to the neutral `unknown_user_defined` behavior until those profiles ship.
2. **Add** a `## Domain Evidence Profiles` section with a 4-row table. Columns: `Profile` / `Standard evidence types` / `Common provenance requirements` / `Disqualifying gaps` / `Reserved-note`. Plus a separate short list of the 5 reserved profiles with the "not in enum" note.
3. **Add** a `#246` forward-reference note: "Discipline-relative *grade aggregation* (how these evidence expectations roll up into an Overall Grade) is tracked separately in #246 and is not yet implemented; until then the A-F Overall Grade lookup above applies unchanged."

### D. source_verification consumption — `deep-research/agents/source_verification_agent.md`

In `## Verification Procedures` (line ~50), add a **Step 0: Read `domain_evidence_profile`**:

- If a profile is present (via Material Passport Schema 10 block), adjust the verification checklist per the profile's `Standard evidence types` / `Common provenance requirements` / `Disqualifying gaps` from `source_quality_hierarchy.md`.
- If the profile is absent, unparseable, or `unknown_user_defined`, apply the current neutral 7-level-pyramid behavior unchanged (graceful fallback, no block).
- The profile adjusts what the agent *surfaces*; it does NOT change the A-F grade and does NOT block (advisory).

### E. literature_strategist consumption — `academic-paper/agents/literature_strategist_agent.md`

In `### Step 2: Database Selection` / `### Step 3: Search String Construction` (lines ~45-57), add profile-aware adjustment:

- If a profile is present, bias database selection + search strategy toward the profile's `Standard evidence types` (e.g. `cs_ml` → arXiv / ACL Anthology / proceedings weighting; `humanities_interpretive` → primary sources / monographs / archival weighting).
- If absent / `unknown_user_defined`, current neutral behavior unchanged.
- This composes with the existing `## Distributional Skew Advisory (Kong #257)` section without contradicting it.

## Acceptance mapping (incl. deliberate divergences)

| Issue acceptance criterion | How this spec satisfies it | Divergence |
|----------------------------|----------------------------|------------|
| #1 Intake adds `domain_evidence_profile` with enum = 4 ship-ready values + default `unknown_user_defined` | Change A (Schema 10 block) + Change B (intake Step 10) | aligned |
| #2 `deep-research/references/domain_profiles/` directory + 4 profile md files | **Changed to** a `## Domain Evidence Profiles` section + 4-row table inside `source_quality_hierarchy.md` (Change C) | **DIVERGES** — maintainer-approved (Q4): single dedicated section, not a directory, since 4 advisory profiles with no aggregation do not justify a mini-spec directory. To be noted on #259 at close. |
| #3 Reserved profile list documented with "not in enum yet" note | Change A (block rules) + Change C (reserved-note column + reserved list) | aligned |
| #4 `source_verification_agent.md` + `literature_strategist_agent.md` consume the profile | Changes D + E | aligned |
| #5 #246 cross-links to relevant profiles | **Changed to** a forward-reference note (Change C.3), because #246 is not yet implemented | **DIVERGES** — maintainer-approved (Q3): forward-reference note instead of a live cross-link, to avoid a dangling reference. The live cross-link lands when #246 ships. |
| #6 User can override profile mid-pipeline, recorded in Material Passport | Schema 10 block `override_history[]` (Change A) | aligned |

## INVARIANTS

1. **Enum cardinality.** The ship-ready enum is exactly 4 values (`general_social_science`, `cs_ml`, `humanities_interpretive`, `unknown_user_defined`); the 5 reserved values (`clinical`, `wet_lab`, `materials_physics`, `legal_case_based`, `education`) are NOT in the enum.
2. **Reserved fallback.** Requesting a reserved profile at intake → `selected: unknown_user_defined` + non-null `fallback_reason` + an explicit advisory. No reserved profile ever silently activates a checklist.
3. **Graceful fallback.** Absent / unparseable / `unknown_user_defined` profile → consuming agents apply the current neutral single-pyramid behavior, unchanged, with no block.
4. **Advisory only.** A profile never changes the A-F Overall Grade and never blocks manuscript ship.
5. **No auto-detect.** The discipline is scholar-selected; agents never infer it. Override is first-class and recorded in `override_history[]`.
6. **#246 boundary.** #259 references grade aggregation as a forward dependency only; it ships no aggregation logic and no placeholder aggregation code.
7. **Single normative profile table.** After Change C, `source_quality_hierarchy.md` has exactly one normative profile table; the old field-centric table is reduced to a non-normative legacy mapping note.

## Test strategy

Prose schema (mirrors Schema 10 / #256 commitment ledger — no JSON Schema file). A lightweight markdown structural checker `scripts/check_domain_evidence_profile.py` enforces:

1. Schema 10 `domain_evidence_profile` block documents exactly the 4 enum values + `unknown_user_defined` default (INVARIANT 1).
2. `source_quality_hierarchy.md` has a `## Domain Evidence Profiles` section with a table covering all 4 profiles + the 5 reserved names with the "not in enum" note (INVARIANTS 1, 2).
3. Both consumer agents (`source_verification_agent.md`, `literature_strategist_agent.md`) contain a "read `domain_evidence_profile`" instruction AND the graceful-fallback clause (INVARIANT 3).
4. `source_quality_hierarchy.md` carries the advisory-only statement + the #246 forward-reference note (INVARIANTS 4, 6).
5. The old field-centric table is gone or demoted to a legacy note (INVARIANT 7).

Plus a **mutation test** (`scripts/test_check_domain_evidence_profile.py`): deliberately drop one enum value / drop a reserved-note / strip a graceful-fallback clause and assert the checker FAILs (so the checker cannot trivially accept-all). Wired into `.github/workflows/spec-consistency.yml`.

## Out of scope (forward work)

- **#246** discipline-relative grade aggregation (Overall Grade formula). #259 only forward-references it.
- Reserved profiles (`clinical` / `wet_lab` / `materials_physics` / `legal_case_based` / `education`) ship per demand in later releases.
- `citation_compliance_agent` profile integration (consistent with the v3.6.5 deferral of corpus integration for that agent).
- No JSON Schema file for `domain_evidence_profile` (prose schema mirrors Schema 10).
