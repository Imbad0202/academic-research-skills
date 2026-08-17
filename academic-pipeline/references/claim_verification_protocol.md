# Claim Verification Protocol (Phase E)

## Purpose
Assesses whether registered quantitative and factual claims in the paper are accurately supported by the cited source material available to the run. Phase A-D check bounded reference/source properties; Phase E checks claim-source alignment for the registered population. Neither layer certifies semantic extraction completeness, underlying data truth, or actual research execution.

## Target population
E1 is instructed to register each detected instance in these classes, while its
semantic extraction completeness remains unknown:

- numerical claims (percentages, counts, effect sizes, p-values)
- categorical assertions ("X is the largest...", "Y was the first to...")
- trend claims ("increasing", "declining", "stable")
- causal claims ("X causes Y", "X leads to Y")

## E1: Claim Extraction
- Scan the paper for quantitative/factual claims and build the registered population. This is a semantic, model-mediated extraction step: do not describe the resulting registry as mechanically complete.
- For each claim, assign a stable `claim_id` and emit the closed `claim-registry/1.0` artifact defined by `shared/contracts/evidence/claim_registry.schema.json`. Every row records exact UTF-8 draft byte span + equal `claim_text`, claim kind(s), cited source(s) by `ref_slug`, writer anchors, paper section, and selection tier (#549 — Mode 1: `HIGH-IMPACT` / `RANDOM` / `TOP-UP` / `NOT-SELECTED`; Mode 2: `ALL`). The registry binds `draft_raw_sha256`; duplicate IDs/spans and stale or unequal spans are invalid.
- For a claim that satisfies the high-impact definition, the registry row also records WHICH of the five criteria fired (`high_impact_basis` ⊆ {headline_conclusion, numerical, causal, methods_critical, disputed}) — an optional `claim-registry/1.0` row field: the tier says that it is high-impact, the basis says why; the #655 claim-standing probe offer below consumes the recorded basis
- Expected output: a schema-valid Claim Registry artifact. A rendered table is a view, not the machine contract.

### E1.1: Mechanically detectable coverage diff (#737)

After E1, run `scripts/claim_registry_coverage.py` on the exact raw draft bytes
and exact serialized `claim-registry/1.0` bytes. The deterministic report checks
only bounded lexical candidates: citation-bearing sentences and quantitative
sentences. Citation surfaces include Markdown links, numeric brackets,
parenthetical or narrative author-year forms, Pandoc citation keys, and inline
reference markers; quantitative surfaces include unit-bearing numbers,
p-values, `N=...`, and common effect-size/ratio notation. This is a finite
lexical grammar, not semantic claim detection. For each candidate it also
records the exact spans of the finite lexical triggers that caused detection.
It joins only validated UTF-8 byte spans; fuzzy or substring matching is not
evidence of coverage. A candidate is `registry_span_matched` only when one
registered span equals the full candidate sentence and every lexical trigger
is contained in a registered span. A same-sentence mix, an uncovered trigger,
or a registry span narrower than the candidate is
`mixed_or_partial_registry_coverage`; a candidate with no matched registry span
is `candidate_unregistered`. Both non-clean states contribute to
`candidate_unregistered_count` and return to E1 for inspection. The report also
records registered claims outside those two candidate classes, while fixing
`semantic_extraction_coverage: not_machine_detectable`.

Persist the exact report and put its path, raw SHA-256, exact draft/registry raw
SHA-256 bindings, status, and candidate-gap count in Integrity Report Schema 5.
Before rendering or routing, replay it with `--validate-report`. `not_run`, a
missing pointer, a stale binding, or replay failure becomes
`E1-COVERAGE-UNRESOLVED` and closes the current integrity checkpoint; it can
never be rendered as zero gaps.

Every non-clean candidate row returns to E1 for human/model inspection; it is
not automatically a claim. Trigger spans are lexical witnesses, not semantic
subclaim boundaries. A clean replay-valid report proves only that
these two mechanically detectable candidate classes have no unregistered exact
span. Semantic or uncited qualitative claims can remain undetected, so no
consumer may turn a clean report into “all substantive claims extracted.”

## E2: Source Tracing
- For each SELECTED claim (Mode 1: the #549 risk-stratified selection — tiers `HIGH-IMPACT` / `RANDOM` / `TOP-UP`; Mode 2: every claim in the registry), locate the specific passage in the cited source that supports it
- Use WebSearch + DOI lookup to find the original source during the producer's verification work. Any retrieved text must become explicit session-held source material before evidence-row construction; the evidence-row builder and report renderer never follow a URL, DOI, `source_pointer`, or path to fill a gap
- If source is behind paywall, note as UNVERIFIABLE_ACCESS

## E3: Cross-Referencing
- Compare claim text vs source text
- Check: exact numbers, date ranges, population descriptions, methodology descriptions
- Flag any discrepancies

## E3.1: Evidence-Row Persistence (#656)

The current producer MUST use `scripts/evidence_rows.py` to build and validate
the Phase E evidence rows against
`shared/contracts/evidence/evidence_row.schema.json`. The generic contract is
`schema_version: evidence-row/1.0`; every V1 row carries
`surface: phase_e_claim_verification`. The schema and runtime own the closed
row shape, exact-match rules, evidence-state vocabulary, escaping, hashes, and
cache replay. Do not duplicate or infer those rules in a prompt or rendered
table.

For every selected claim, persist one row per
`(claim_id, ref_slug, anchor)` tuple in
`phases.E_claims.evidence_rows[]`. A multi-source claim has multiple rows rather
than one flattened source cell; an anchorless tuple still has one explicit
empty-state row. `NOT-SELECTED` registry entries remain visible in the Claim
Registry but are not selected evidence rows. Preserve every emitted row in
document order: there is no total row cap, deduplication, reordering, or silent
truncation.

The builder accepts source text only as explicit session-held input. A missing,
anchorless, access-failed, retrieval-failed, unchecked, or mismatched source
state never fabricates an excerpt, and a claim verdict never upgrades excerpt
provenance. Persist the validated row objects, not rendered Markdown or HTML.
Building or rendering evidence rows does not mark a source as human-read and
does not write or infer `human_read_log` state. Evidence rows do not change the
verdict taxonomy, severity, issue counts, or Pass/Fail Criteria below.

## E4: Scope-Conformance Advisory (#547 — advisory-only)

**Inputs**: the RQ Brief `scope` object (E4's one required input), plus two optional refinements — `sub_question_bindings` and the outline's section→sub-question map — carried in the integrity dispatch context per the pipeline handoff table (Stage 2→2.5 / Stage 4→4.5). SKIP E4 with `[E4-SKIPPED: no scope context]` ONLY when the parent `scope` object itself is unavailable (standalone runs with no RQ Brief) — never reconstruct or guess one. Absent bindings or section map (pre-#547 artifacts): compare every section's claims against the full parent `scope` — that is the documented fallback, not a skip.

Compare each audited claim's population, timeframe, geography, and domain against the **effective scope** the claim's section inherits:

1. Resolve the section's effective scope (section → serves sub-question → bindings; fall back to the whole `scope` object when no bindings exist). Axes named in `inherits` use those values; omitted axes inherit the parent `scope` value; each recorded user-approved deviation REPLACES the bound on its axis — so an already-approved extension is never re-flagged.
2. Flag claims whose stated scope exceeds the effective scope on any axis as `SCOPE-BROADENED`, recording: claim location, effective scope, drafted scope, broadened axis.
3. ADVISORY ONLY: `SCOPE-BROADENED` rows never change Phase E verdicts and never gate PASS/FAIL — they are not issues, do not enter the gate's issue count, and may remain open when the gate passes. Each row carries a stable ID `ADV-E4-<n>` and is recorded in the Integrity Report's advisory table. Checkpoint options per row: **proceed open** (default, recorded) or **accept the broadening** (with a note to justify it in the text; recorded). E4 defines no reword route and places no obligation on any downstream agent: a user who wants wording narrowed asks for it as an ordinary revision instruction in the normal flow — the advisory table is visible wherever the Integrity Report travels (it accompanies the Stage 2.5→3 handoff materials), so rows can be cited by their ADV-E4 IDs when doing so. Rows still open at Stage 4.5 simply remain recorded in the Final Integrity Report deliverable. No automatic rewriting, no new dispatch path.

External motivation: Ren et al. (2026, arXiv:2607.13104 §5.1) — decomposition-based generation becomes vulnerable when sub-problems stop preserving the constraints of the original task (design inference: a drafted claim is the last link in that chain).

## E5: Novelty-Claim Classification (#548 — advisory-only)

E1 already extracts categorical assertions of primacy ("Y was the first to..."). Such claims assert the ABSENCE of prior literature, so E2/E3 source-tracing structurally cannot verify them — there is no cited source to trace. Classify them against the documented search (Schema 2 `search_strategy`) instead:

| Classification | Definition |
|----------------|------------|
| `SUPPORTED_WITHIN_SEARCH` | Wording is search-bounded ("to our knowledge, based on searches of [databases] covering [date_range], as of [last_searched_at]...") AND the named databases + date range match the documented `search_strategy` exactly AND `last_searched_at` is recorded — a bound with no search-execution date is not verifiable and classifies `UNRESOLVED` with the note "record last_searched_at to resolve"; the nearest prior work (bibliography `relevance: core` on the same phenomenon, tie-broken by `relevance_score`, then `supporting`) is acknowledged where it exists, or its absence within the search is stated explicitly |
| `UNRESOLVED` | Absolute wording ("first", "no prior work", "only") without a search bound, OR the stated bound does not match the documented `search_strategy`, OR `last_searched_at` is not recorded, OR no documented search basis exists |

Never emit a "globally verified" novelty verdict — a search-bounded claim is verified WITHIN its search, nothing more.

ADVISORY ONLY: `UNRESOLVED` rows never change Phase E verdicts and never gate PASS/FAIL — they are not issues, stay outside the gate's issue count, and may remain open when the gate passes. Each row carries a stable ID `ADV-E5-<n>` and is recorded in the Integrity Report's advisory table. Checkpoint options per row: **proceed open** (default; the decision lives in the checkpoint conversation record, not in a report field) or **explicitly confirm the absolute form** (same recording; when the user later generates the AI-usage disclosure, they carry confirmed-absolute claims into it). E5 defines no reword route and places no obligation on any downstream agent: a user who wants the bounded rewording asks for it as an ordinary revision instruction — the advisory table is visible wherever the Integrity Report travels, rows citable by their ADV-E5 IDs. Rows still open at Stage 4.5 simply remain recorded in the Final Integrity Report deliverable. No new dispatch path.

External motivation: Ren et al. (2026, arXiv:2607.13104 §7.4) — discovery agents cannot easily verify novelty on their own and may exploit weak proxies.

## E6: Claim-Strength Drift (#569 — non-verdict, checkpoint-closing, revision rounds)

**Runs only** at a Stage 4.5 (or Stage 2.5 re-verification) invocation that follows a revision round. This phase is the epistemic complement to the deterministic numeric/citation conservation check (`scripts/check_revision_token_conservation.py`, #570): that script conserves tokens; E6 covers what token-matching cannot see — whether a claim's epistemic strength moved along the ladder.

**Inputs (artifact-based, graceful — mirrors E4's scope-absence handling).** E6 consumes the **revision-evidence bundle** the orchestrator names in the dispatch context (§ Revision-Evidence Bundle in `pipeline_orchestrator_agent.md`): the per-round revision patch sidecars (`phase6_*/revision_patch_round<N>.json`, each carrying its ops' `old`/`new_text` + `roadmap_item_ids`), the pre-round anchored draft(s), and the round's Revision Roadmap (or the integrity-correction Issue List on a FAIL-correction round). The patch sidecars are the primary source — each op already records exactly which block changed, its before/after text, and the roadmap items it claims, so E6 needs no separate prior-draft diff when they are present. Reference: `shared/references/claim_strength_ladder.md`.

- **No revision evidence in context** (bundle absent — a first-pass audit, or a standalone run with no patch chain): SKIP with `[E6-SKIPPED: no revision evidence]`. Never reconstruct a prior draft or guess a roadmap.
- **Multiple revision rounds before this gate** (e.g. the Stage 3→4→3' Major→4' path reaches the single Stage 4.5 after rev0→rev1 and rev1→rev2): consume **every** round's patch sidecar in the bundle, not only the latest. A drift introduced in an earlier round and carried unchanged into the current draft is still unauthorized; auditing only the last pair would miss it. Report each round's rows under the same `ADV-E6-<n>` sequence (the row names the round).

For each claim-bearing op across the consumed rounds, compare its ladder rung (and its load-bearing hedges / null results / limitations / causal caveats) between the op's `old` and `new_text`:

1. If the rung moved (either direction) or a hedge/null/caveat was dropped, check whether a roadmap item authorized *that strength change* (not merely touching the block). An authorized move is recorded and closed.
2. Flag an unauthorized move as `STRENGTH-DRIFTED`, recording: claim location, prior rung → current rung (or the dropped qualifier), the roadmap items the op claimed, and the direction (up / down).
3. `STRENGTH-DRIFTED` rows do not change the Phase E verdict and do not enter its issue count: a report may still say PASS on source/claim verification. They are nevertheless **checkpoint-closing**. A detected row may not remain open, inherit a default, or be cleared by a generic confirmation. Before any next-stage transition, the author must explicitly choose exactly one disposition for every row: **`restore`**, **`authorize_with_reason`**, or **`pause`**. `authorize_with_reason` requires a non-blank reason. There is no `proceed open` choice.

### E6 structured findings and author disposition

The producer persists the complete ordered E6 result as a companion
`claim-strength-drift-findings/1.0` artifact validated against
`shared/contracts/revision/claim_strength_drift_findings.schema.json`. The
Integrity Report carries that artifact's exact SHA-256 pointer and renders its
rows; it does not maintain a second hand-authored E6 list. On a revision gate,
`status=completed` binds the exact final-draft and Revision-Evidence Bundle
SHA-256 values, records detector kind/id plus the protocol hash, and contains
the exact `ADV-E6-1..N` sequence. With no revision evidence, emit
`status=skipped_no_revision_evidence`, a null bundle hash, and `findings=[]`.

When one or more findings exist, retain one explicitly named local raw
session-event artifact and one explicit choice per row in
`claim-strength-drift-disposition-input/1.0`, then run
`scripts/claim_strength_drift_disposition.py build`. Each transient input row
contains an absolute artifact path and its declared raw SHA-256. Keep those raw
event files in run-local storage outside the repository. The deterministic
builder safely opens each exact regular non-symlink file, recomputes its digest,
requires ordered one-to-one event/disposition coverage, and emits the hash-bound
`claim-strength-drift-disposition/1.0` sidecar. A supplied 64-hex digest without
matching raw bytes cannot authorize continuation. The sidecar omits the paths
and raw messages and derives one closed pipeline action:

- any `pause` -> `paused`; save state and do not advance;
- otherwise any `restore` -> `restore_required`; route the cited row back for
  restoration, then rerun integrity/E6 on the new exact draft before advancing;
- only when every row is `authorize_with_reason` ->
  `authorized_to_continue`; preserve every reason in the sidecar.

```bash
python scripts/claim_strength_drift_disposition.py build \
  --finding-set <claim-strength-drift-findings.json> \
  --author-input <explicit-author-dispositions.json> \
  --final-draft <exact-revised-draft> \
  --revision-evidence-bundle <exact-revision-evidence-bundle.json> \
  --output <claim-strength-drift-disposition.json>

python scripts/claim_strength_drift_disposition.py validate \
  --finding-set <claim-strength-drift-findings.json> \
  --sidecar <claim-strength-drift-disposition.json> \
  --final-draft <exact-revised-draft> \
  --revision-evidence-bundle <exact-revision-evidence-bundle.json> \
  --event-artifact 'ASSERTED-EVENT-e6-1=/absolute/run-local/event-1.raw' \
  [--event-artifact 'ASSERTED-EVENT-e6-N=/absolute/run-local/event-N.raw' ...]
```

The sidecar travels with the final Integrity Report. A `restore` record is an
auditable request, not authority for the drifted bytes; a prior sidecar cannot
be replayed against a changed finding set, draft, or revision bundle. Silence,
an omitted row, a missing/unknown/duplicate event mapping, a generic `continue`, or a
free-form acceptance outside the sidecar leaves the checkpoint unresolved.

**Event and detection boundary.** Build and `validate` both receive explicitly
named raw session-event bytes and recompute their SHA-256; validation requires
a repeatable exact event-id-to-path mapping, so the durable sidecar's digest
alone is insufficient for replay. This proves byte identity only. The runtime
does not authenticate that the bytes came from a session user, interpret their
meaning, or prove the asserted actor identity. E6 classification remains
semantic and may be model-mediated. Schema/validator success proves only that
every *reported* finding is byte-bound and explicitly disposed. It does not
prove complete recall, semantic correctness, author identity authentication,
or scientific warrant for an authorized strength move. If the transient raw
event artifact is unavailable, replay fails closed. An empty finding set is
therefore “none detected by the recorded review,” never a deterministic
no-drift certificate.

External motivation: DELEGATE-52 (arXiv:2604.15597) — round-trip editing corrupts content by subtle modification; the #390 patch confines exposure to touched blocks but does not check their epistemic interior. Baseline evidence that the drift is real on the current frontier model: `evals/heldout/revision_claim_drift/` (2026-07-22: 2/8 under hedge-drop / null-reframe pressure). Mechanism shape borrowed from Yila-AI/sci-ssci-skills (@MissOrangePeel).

## Claim-Standing Probe Offer (#655 — opt-in, advisory-only)

After E1 has emitted the Claim Registry at a Stage 2.5 or Stage 4.5 integrity checkpoint, the user MAY request the search-bounded claim-standing probe on individual registry rows. The probe is an additional user-requested view. It is NOT part of Phase E verification and NOT part of the integrity result: it never changes a Phase E verdict, severity, issue count, checkpoint result, correction route, formatter refusal, or Stage transition, and it never writes read-ledger or manuscript state (`layer = LLM-ADVISORY`, `gate_effect = none`, `read_ledger_effect = none`, `manuscript_mutation = none`).

**Trigger (design §3.1, gate 1 — enforced by `scripts/build_claim_standing_query_plan.py`):**

- Stage 2.5: only registry rows recorded `HIGH-IMPACT` are eligible — the recorded tier is the registry witness. `RANDOM`, `TOP-UP`, and `NOT-SELECTED` rows are never eligible — the random sentinel and top-up floor are Phase E quality controls, not consent to expand the probe. When the registry recorded the tier but not the five-part basis, the row stays eligible by tier; the basis the probe's plan requires then comes from a recorded researcher confirmation.
- Stage 4.5: `ALL` is not permission to probe every claim. A row is eligible only when the registry records the same five-part high-impact classification (headline conclusion / numerical / causal / methods-critical / disputed) for it; a basis-less row is ambiguous and stays ineligible until the researcher confirms the classification.
- Researcher confirmations (and the basis provenance — registry vs researcher confirmation) are recorded in the probe's own artifacts and never written back to the registry.

**Consent (design §3.2, gate 2):** Eligibility never dispatches anything. Before any query planner, index, or model receives claim text, the researcher sees and affirmatively accepts a closed consent surface (`propose` → `bind` in `scripts/build_claim_standing_query_plan.py`) whose hash binds the complete consentable-plan projection; absence of that acceptance, any post-proposal change (claim, query, provider, filter, cap, stance plan, persistence), or an explicit cancel produces an explicit local `not_checked` declination record (`consent_absent` / `consent_invalidated` / `consent_cancelled`) and no network or model call. Retrieval, stance classification, freshness (`scripts/check_claim_standing_freshness.py`), and per-event transmission accounting (`scripts/check_claim_standing_transmissions.py`) are specified in `shared/references/claim_standing_candidate_ledger_protocol.md`. Every probe surface carries `STANCE CLASSIFICATION UNMEASURED` until the #655 baseline measurement row exists.

## Verdict Taxonomy

| Verdict | Definition | Severity | Example |
|---------|-----------|----------|---------|
| VERIFIED | Claim matches source exactly or within rounding tolerance | None | Paper: "15.2%"; Source: "15.2%" |
| MINOR_DISTORTION | Claim paraphrases source but meaning is preserved | MINOR | Paper: "about 15%"; Source: "15.2%" |
| MAJOR_DISTORTION | Claim oversimplifies, exaggerates, or misrepresents source | SERIOUS | Paper: "declined sharply"; Source: "declined by 2.1%" |
| UNVERIFIABLE | Source doesn't contain the claimed information | SERIOUS | Paper cites Smith (2020) for a claim, but Smith (2020) doesn't discuss this topic |
| UNVERIFIABLE_ACCESS | Source exists but full text not accessible for verification | MEDIUM | Paywalled journal article |

## Sampling Strategy
- Mode 1 (pre-review) — risk-stratified (#549, mirroring the #518 reference-verification tiers):
  - HIGH-IMPACT claims — verify 100%, no cap. A claim is high-impact if it is: (a) a headline conclusion (abstract- or conclusions-level), (b) numerical (statistic, effect size, percentage, threshold), (c) causal, (d) methods-critical, or (e) disputed (already carrying a contradiction disclosure or reviewer split). Same definition family as `shared/cross_model_verification.md` step 2.
  - RANDOM sentinel — 10% of the non-high-impact remainder, rounded up (minimum 3, maximum 10; fewer than 3 in the remainder → all of it), preserving unbiased drift detection.
  - Floor: if the two tiers together select fewer than min(10, total claims), top up at random from the remainder; a paper with fewer than 10 claims total is audited in full (preserves the pre-#549 minimum).
  - Record each claim's tier in the Claim Registry (`HIGH-IMPACT` / `RANDOM` / `TOP-UP` for selected claims; `NOT-SELECTED` for the rest) so coverage is inspectable. Cost scales with the count of high-impact claims — a results-dense paper approaches 100% coverage at Stage 2.5, which is the point: consequential distortions surface BEFORE the review stage instead of at the Stage 4.5 backstop.
- Mode 2 (final-check): 100% of **registered claims**. The denominator is the E1 Claim Registry; semantic extraction completeness remains unknown and is reported separately by E1.1.

External motivation: Ren et al. (2026, arXiv:2607.13104): §3.3 frames active data-acquisition as targeting frequent failure modes and verifier disagreement; §9.2 frames improvement as resource optimization (gating expensive evaluations, penalizing waste). The high-impact-first allocation here is ARS's design inference from those principles, mirroring #518's reference-verification shift.

## Output Format

### Claim Verification Report

The machine artifact is the complete ordered
`phases.E_claims.evidence_rows[]` array. Render its human-facing table only with
`scripts/evidence_rows.py`. The default and maximum page size are 25. Render
only the requested page and show deterministic previous/next or explicit-page
navigation; never concatenate all pages into one checkpoint output. There is no
`--all` mode and no total row cap. Successive valid page requests preserve row
order and can reach each persisted `row_id` exactly once.

The renderer requires the explicit in-memory session source map and
replay-validates every source-bound persisted row before display. It performs no
display-time retrieval, ambient filesystem/network/API/model call, extraction,
state derivation, or cache lookup. Replay may recompute the strict once-decode
and hashes, but never decodes stored display text again or changes the row. The
Claim Registry (E1) still records the tier for EVERY claim, including
`NOT-SELECTED`, so exact tuple coverage remains auditable without treating
rendered markup as a handoff artifact.

A positively identified pre-#656 Schema 5 report that has no `evidence_rows`
MUST be rendered only with explicit `--allow-legacy-absence`, displaying
`LEGACY — EVIDENCE ROWS UNAVAILABLE`. Missing shape alone is not legacy proof;
without the flag render fails. Absence is not a successful or empty evidence
check, does not manufacture excerpts, and does not retroactively alter the
report's historical Phase E verdict. A current producer always persists the
field (`[]` only when no tuple was selected); omission or a missing selected row
is a contract failure and the compatibility flag is forbidden. For a current report, distinct row claim count must equal
`E_claims.checked`, distinct `VERIFIED` claim count must equal
`E_claims.verified`, and all rows for one claim must agree on claim metadata and
verdict.

### Summary
- Total registered claims checked: [N] of [registry total] — Mode 1: tiers HIGH-IMPACT: [N] (100% of tier), RANDOM: [N], TOP-UP: [N], NOT-SELECTED: [N]. Mode 2: ALL REGISTERED: [N]. Semantic extraction coverage: `not_machine_detectable`; mechanically detectable candidate gaps: [N].
- VERIFIED: [N]
- MINOR_DISTORTION: [N]
- MAJOR_DISTORTION: [N] (must be 0 for PASS)
- UNVERIFIABLE: [N] (must be 0 for PASS)
- UNVERIFIABLE_ACCESS: [N] (noted but does not block PASS)

## Pass/Fail Criteria
- PASS: Zero MAJOR_DISTORTION + Zero UNVERIFIABLE
- FAIL: Any MAJOR_DISTORTION or UNVERIFIABLE
- PASS_WITH_NOTES: Only MINOR_DISTORTION and/or UNVERIFIABLE_ACCESS
