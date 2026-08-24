# Handoff Schemas — Cross-Skill Data Contracts

## Purpose

Defines the exact data structure for every artifact passed between pipeline stages.
All agents that produce or consume these artifacts MUST conform to these schemas.
Consuming agents should validate input and request re-generation if schema violations are found.

> **Convention**: All schemas use Markdown-based structured output. Agents MUST validate required fields before accepting a handoff. Missing required fields trigger a `HANDOFF_INCOMPLETE` failure path.

> **#673 activity exclusion:** adjudication activity is not handoff cargo.
> the #673 activity projection of the terminal state root `run_id`,
> `pending_adjudication_activity_bindings[]`, sealed
> `adjudication_activity_sources`, selected-store information, store records,
> renderer output, and activity diagnostics remain only in the state tracker's
> local advisory side channel. They MUST NOT be added to any numbered schema,
> Material Passport, stage transfer, gate/verdict/checkpoint input, Process
> Record, or model/observer/compliance input. See
> `academic-pipeline/agents/state_tracker_agent.md` §
> "Adjudication-activity metadata". This exclusion does not remove or alter any
> existing schema-owned `run_id` field used by another contract.

---

## Schema 1: RQ Brief (deep-research -> academic-paper)

**Producer**: `deep-research/research_question_agent` | `deep-research/socratic_mentor_agent`
**Consumer**: `deep-research/research_architect_agent` | `academic-paper/intake_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `research_question` | string | The finalized research question (single sentence, interrogative form) |
| `sub_questions` | list[string] | 2-5 decomposed sub-questions |
| `finer_scores` | object | `{feasible: 1-10, interesting: 1-10, novel: 1-10, ethical: 1-10, relevant: 1-10}` |
| `scope` | object | `{in_scope: list[string], out_of_scope: list[string], domain: string, timeframe: string, geography: string, population: string}` |
| `methodology_type` | enum | `"qualitative"` / `"quantitative"` / `"mixed"` |
| `theoretical_framework` | string | Name of the selected or emergent theoretical framework |
| `keywords` | list[string] | 5-10 search terms for literature search |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `socratic_insights` | list[string] | Key insights from Socratic dialogue (if socratic mode) |
| `hypothesis` | string | Preliminary hypothesis (if applicable) |
| `exclusion_criteria` | list[string] | What is explicitly out of scope |
| `sub_question_bindings` | list[object] | Per-sub-question inherited scope constraints (#547): `{sub_question: 1-based index, inherits: subset of scope keys (population/timeframe/geography/domain) with values, deviations: list[string] of user-approved divergences (default empty)}`. Effective-scope semantics: axes named in `inherits` use those values; omitted axes inherit the parent `scope` value; each approved deviation replaces the bound on its axis. Absent field = every sub-question inherits the full `scope` object unchanged. External motivation: Ren et al. arXiv:2607.13104 §5.1 (decomposition that stops preserving the parent task's constraints). |
| `stakeholders` | list[string] | Key stakeholders affected by the research |
| `ethical_flags` | list[string] | Preliminary ethical considerations |

### Example

```markdown
## RQ Brief

**Research Question**: How does AI-assisted formative assessment affect undergraduate learning outcomes in STEM courses at Taiwanese universities?

**Sub-Questions**:
1. What types of AI-assisted formative assessment tools are currently used in Taiwan HEI STEM courses?
2. What measurable learning outcome improvements have been documented?
3. What student and faculty perceptions exist regarding AI-assisted assessment?

**Sub-Question Bindings** (#547, optional):
1. inherits: population=Undergraduate STEM students; timeframe=2018-2025; geography=Taiwan — deviations: none
2. inherits: same as parent scope — deviations: none
3. inherits: same as parent scope — deviations: extends population to faculty (user-approved)

**FINER Scores**: Feasible: 8, Interesting: 9, Novel: 7, Ethical: 9, Relevant: 10

**Scope**:
- In scope: AI-assisted formative assessment, STEM undergraduate courses, Taiwan HEIs, 2018-2025
- Out of scope: K-12 education, summative assessment only, non-STEM disciplines
- Domain: Higher Education, Educational Technology
- Timeframe: 2018-2025
- Geography: Taiwan (with international comparisons)
- Population: Undergraduate STEM students

**Methodology Type**: Mixed methods (quasi-experimental + survey)

**Theoretical Framework**: Technology Acceptance Model (TAM) + Hattie's Feedback Framework

**Keywords**: AI assessment, formative assessment, STEM education, Taiwan higher education, learning outcomes, educational technology, automated feedback
```

---

## Schema 2: Bibliography (deep-research -> academic-paper)

**Producer**: `deep-research/bibliography_agent`
**Consumer**: `deep-research/synthesis_agent` | `deep-research/source_verification_agent` | `academic-paper/literature_strategist_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `sources` | list[Source] | All identified sources (minimum 15 for full mode, 5 for quick mode) |
| `search_strategy` | object | `{databases: list[string], keywords: list[string], inclusion_criteria: list[string], exclusion_criteria: list[string], date_range: string, last_searched_at?: ISO date (#548 — when the search was last executed; producers SHOULD record it: E5 requires it for SUPPORTED_WITHIN_SEARCH, and the search-bounded novelty template consumes it)}` |
| `coverage_assessment` | string | Self-assessment of literature coverage completeness |
| `minimum_sources` | integer | 15 (full mode), 5 (quick mode) |

### Source Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `[S01]`) |
| `title` | string | Yes | Source title |
| `authors` | string | Yes | Author(s) |
| `year` | integer | Yes | Publication year |
| `doi` | string | Yes* | DOI if available (*required for journal articles) |
| `citation` | string | Yes | Full APA 7 citation |
| `type` | enum | Yes | `journal_article` / `book` / `chapter` / `conference` / `report` / `thesis` / `preprint` / `web` |
| `evidence_tier` | integer | Yes | 1-7 (1 = systematic review/meta-analysis, 7 = expert opinion) |
| `quality_tier` | enum | Yes | `tier_1` (peer-reviewed top journal) / `tier_2` (peer-reviewed) / `tier_3` (other academic) / `tier_4` (grey literature) |
| `relevance` | enum | Yes | `core` (directly addresses RQ) / `supporting` (provides context) / `peripheral` (tangential) |
| `relevance_score` | integer | Yes | 1-10 relevance to the research question |
| `annotation` | string | Yes | 2-3 sentence summary of key findings and relevance |
| `verified` | boolean | No | Whether DOI/existence has been verified |
| `retraction_check` | boolean | No | Deprecated, read-only. Legacy execution attestation: whether a Retraction Watch check was reportedly run, **not** its result. New producers write only the v1.1 `bibliographic_integrity_signals[].retraction_status` authority; see `shared/bibliographic_integrity_signals.md`. `true` never means “not retracted” or otherwise clean and cannot drive terminal policy. |
| `semantic_scholar_id` | string / null | No | Semantic Scholar paper ID (v3.3). Null if S2 lookup failed or API unavailable. Used for deduplication and re-verification. |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `prisma_counts` | object | `{identified: int, screened: int, eligible: int, included: int}` (if systematic review) |

### Example

```markdown
## Bibliography

**Search Strategy**:
- Databases: Scopus, Web of Science, ERIC, Airiti Library
- Keywords: "AI assessment" AND "higher education" AND "Taiwan"; "formative assessment" AND "artificial intelligence"
- Inclusion: Peer-reviewed, English or Chinese, empirical or review, 2018-2025
- Exclusion: K-12, non-STEM, editorials
- Date Range: 2018-2025

**Coverage Assessment**: Strong coverage of English-language literature. Moderate coverage of Chinese-language sources (Airiti). Gap: limited grey literature from Taiwan MOE reports.

**Coverage requirement**: Each material claim and planned conceptual/methodological role has fit-for-purpose support, or the bounded gap is disclosed. No universal source-count or peer-reviewed-ratio threshold applies.

### Sources

[S01] Wang, L., & Chen, H. (2023). AI-powered formative assessment in undergraduate physics... *Computers & Education*, 195, 104721. https://doi.org/10.xxxx
- Type: journal_article | Evidence Tier: 2 | Quality: tier_1 | Relevance: core | Score: 9
- Annotation: RCT with 240 students showing 15% improvement in exam scores with AI feedback. Directly addresses RQ sub-question 2.
```

---

## Schema 3: Synthesis Report (deep-research -> academic-paper)

**Producer**: `deep-research/synthesis_agent`
**Consumer**: `deep-research/report_compiler_agent` | `academic-paper/argument_builder_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `themes` | list[Theme] | 3-7 synthesized themes (NOT per-source summaries) |
| `research_gaps` | list[string] | What the literature does NOT address |
| `key_debates` | list[Debate] | Where sources disagree, with analysis |
| `methodology_recommendations` | list[string] | Recommended methodological approaches based on gaps |
| `theoretical_implications` | list[string] | How the synthesis informs theoretical understanding |
| `consensus_areas` | list[string] | Where sources agree |

### Theme Object

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Theme label |
| `description` | string | 3-5 sentence synthesis across multiple sources |
| `supporting_sources` | list[string] | Source IDs that contribute to this theme |
| `contradicting_sources` | list[string] | Source IDs that challenge this theme (if any) |
| `strength` | enum | `strong` (5+ sources) / `moderate` (3-4) / `emerging` (1-2) |

### Debate Object

| Field | Type | Description |
|-------|------|-------------|
| `position_a` | string | First position |
| `position_b` | string | Opposing position |
| `sources_a` | list[string] | Source IDs supporting position A |
| `sources_b` | list[string] | Source IDs supporting position B |
| `evidence_balance` | string | Analysis of which position has stronger evidence and why |

### Example

```markdown
## Synthesis

### Theme 1: Immediate Feedback Loop as Primary Mechanism
AI-assisted assessment's primary advantage lies in the immediacy of feedback, reducing the gap between student action and corrective input. Multiple studies [S01, S04, S07, S12] converge on feedback latency as the key variable, with effect sizes ranging from d=0.3 to d=0.8. This aligns with Hattie's (2009) feedback framework...

**Strength**: Strong (5 sources)
**Supporting**: [S01, S04, S07, S12, S15]
**Contradicting**: [S09] (argues quality matters more than speed)

### Research Gaps
1. No longitudinal studies (>1 year) in Taiwan context
2. Limited data on AI assessment in laboratory courses

### Key Debates
| Position A | Position B | Evidence Balance |
|------------|------------|-----------------|
| AI feedback improves all STEM equally [S01, S04] | Effects concentrated in math/physics, weaker in biology [S08, S11] | Position B has stronger evidence; likely due to assessment type differences |
```

---

## Schema 4: Paper Draft (academic-paper -> integrity/reviewer)

**Producer**: `academic-paper/draft_writer_agent`
**Consumer**: `academic-pipeline/integrity_verification_agent` | `academic-paper-reviewer/*`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Paper title |
| `abstract` | object | `{english: string, chinese: string}` (chinese is required only if bilingual) |
| `authors` | list[Author] | Author information with CRediT roles |
| `keywords` | object | `{en: list[string], zh_tw: list[string]}` bilingual keywords (3-6 each) |
| `sections` | list[Section] | Ordered paper sections |
| `references` | list[Reference] | Full reference list with cross-referencing |
| `total_word_count` | integer | Total word count (excluding references) |
| `citation_format` | enum | `"APA7"` / `"Chicago"` / `"MLA"` / `"IEEE"` / `"Vancouver"` |
| `structure_type` | enum | `"IMRaD"` / `"literature_review"` / `"theoretical"` / `"case_study"` / `"policy_brief"` / `"conference"` |

### Section Object

| Field | Type | Description |
|-------|------|-------------|
| `heading` | string | Section heading |
| `level` | integer | Heading level (1-4) |
| `content` | string | Full section text |
| `word_count` | integer | Word count for this section |
| `citation_count` | integer | Number of in-text citations in this section |
| `argument_strength` | enum | `compelling` / `strong` / `adequate` / `weak` (see argument_builder scoring) |

### Reference Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique reference ID (e.g., `[R01]`) |
| `full_citation` | string | Full formatted citation |
| `doi` | string | DOI if available |
| `cited_in_sections` | list[string] | Section headings where this reference is cited |

### Author Object

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Full name |
| `affiliation` | string | Institution |
| `email` | string | Contact email (corresponding author only) |
| `credit_roles` | list[string] | CRediT taxonomy roles |
| `corresponding` | boolean | Is corresponding author |

---

## Schema 5: Integrity Report (integrity_verification_agent -> pipeline)

**Producer**: `academic-pipeline/integrity_verification_agent`
**Consumer**: `academic-pipeline/pipeline_orchestrator_agent` | `academic-paper/draft_writer_agent` (for revision)

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `verdict` | enum | `"PASS"` / `"PASS_WITH_CONDITIONS"` / `"FAIL"` |
| `mode` | enum | `"pre-review"` / `"final-check"` |
| `phases` | object | See Phase Structure below |
| `overall_issues` | object | `{SERIOUS: integer, MEDIUM: integer, MINOR: integer}` |
| `citation_integrity_score` | float | 0.0-1.0 score for citation accuracy |
| `fabrication_risk_score` | float | 0.0-1.0 score (0 = no risk detected) |
| `timestamp` | string | ISO 8601 timestamp of verification |

### Phase Structure

```
phases: {
  A_references: {
    checked: integer,
    passed: integer,
    failed: integer,
    issues: [{ref_id: string, issue_type: string, severity: enum, detail: string}]
  },
  B_citation_context: {
    sampled: integer,
    verified: integer,
    issues: [{ref_id: string, section: string, issue: string}]
  },
  C_data: {
    claims_checked: integer,
    verified: integer,
    issues: [{claim: string, expected: string, actual: string, severity: enum}]
  },
  D_originality: {
    checked: boolean,
    issues: [{type: string, severity: enum, detail: string}]
  },
  E_claims: {
    checked: integer,
    verified: integer,
    distortions: [{claim: string, source: string, verdict: string, detail: string}],
    claim_registry_coverage: {
      status: "completed" | "not_run" | "invalid",
      registry_schema_version: "claim-registry/1.0" | null,
      report_path: string | null,
      report_sha256: sha256 | null,
      draft_raw_sha256: sha256 | null,
      registry_raw_sha256: sha256 | null,
      candidate_unregistered_count: integer | null, // all non-clean candidates, including mixed/partial
      semantic_extraction_coverage: "not_machine_detectable"
    },
    evidence_rows: [EvidenceRow],
    claim_strength_drift_findings: {
      schema_version: "claim-strength-drift-findings/1.0",
      artifact_path: string,
      artifact_sha256: sha256
    }
  }
}
```

#### Phase E Claim Registry coverage (#737)

Current producers MUST populate `phases.E_claims.claim_registry_coverage`.
`status: completed` is lawful only when the pointed
`claim-registry-coverage/1.0` bytes have been replay-validated against the exact
raw draft and exact serialized `claim-registry/1.0` named by its two hashes;
the summary count must equal the replayed report. `not_run`, `invalid`, missing
pointer/hash, stale binding, or replay failure emits
`E1-COVERAGE-UNRESOLVED` and closes the integrity checkpoint. These states do
not mean zero candidates. Historical reports may lack the field, but absence is
legacy/unknown rather than current conformance. Even a completed zero-gap row
retains `semantic_extraction_coverage: not_machine_detectable`.

#### Phase E Evidence Rows (#656)

`phases.E_claims.evidence_rows[]` is the persisted Phase E evidence view. Each
item MUST validate against
`shared/contracts/evidence/evidence_row.schema.json` with
`schema_version: evidence-row/1.0` and
`surface: phase_e_claim_verification`. The current
`integrity_verification_agent` producer MUST use `scripts/evidence_rows.py` to
build and validate the rows; prompts and consumers MUST NOT hand-author a
parallel row shape or provenance vocabulary.

Emit one persisted row per `(claim_id, ref_slug, anchor)` tuple selected by
Phase E. A claim with multiple cited sources therefore emits multiple rows, and
an anchorless selected tuple emits its explicit empty-state row. Preserve the
producer's complete row order: there is no total row cap, silent truncation,
deduplication, or conversion of row counts into distinct-claim counts.
`E_claims.checked`, `E_claims.verified`, `distortions[]`, Phase E verdicts, and
the existing integrity gate remain claim-level and unchanged.

For reports produced after #656, the producer always emits `evidence_rows`;
when no tuple was selected, the explicit value is `[]`. Current-producer
omission is a contract failure. A positively identified pre-#656 Schema 5 report
may omit the field only for explicit legacy read compatibility; consumers use
`--allow-legacy-absence` and display
`LEGACY — EVIDENCE ROWS UNAVAILABLE`. Missing shape alone is not legacy proof,
and render fails without the flag. Legacy absence is not an empty successful
check, MUST NOT manufacture an excerpt, and does not retroactively alter the
historical verdict or gate result. Current producers may never use the flag.

The full array travels inside the existing Integrity Report handoff. Rendering
requires the explicit in-memory session source map to replay-validate every
source-bound persisted row; the default and maximum page size are 25,
there is no `--all` mode, and a checkpoint request renders only its requested
page with deterministic page navigation. There is no total row cap. Rendering
performs no display-time retrieval, ambient filesystem/network/API/model call,
extraction, state derivation, or cache lookup. Replay may recompute the strict
once-decode and hashes, but never decodes stored display text again or changes
the row. Building, validating, persisting, or
rendering these rows does not write or infer `human_read_log` state.

For current reports, distinct row `claim_id` count equals `E_claims.checked`,
distinct claims with verdict `VERIFIED` equal `E_claims.verified`, and every row
for one claim repeats the same claim object and verdict. The E1 Claim Registry
remains authoritative for exact selected-tuple completeness.

#### Phase E6 Claim-Strength Drift Findings and Disposition

`phases.E_claims.claim_strength_drift_findings` is a pointer, not a second copy
of E6 rows. Its exact local artifact validates against
`shared/contracts/revision/claim_strength_drift_findings.schema.json`; the
consumer reopens only the named file, verifies `artifact_sha256`, and then
validates its exact final-draft and Revision-Evidence Bundle bindings. A current
producer emits the companion even when E6 is legitimately skipped for lack of
revision evidence (`status=skipped_no_revision_evidence`, null bundle hash,
empty findings). Pre-contract reports may lack the pointer only as explicit
legacy history; absence must not be interpreted as a completed no-drift check.

When the finding set contains one or more `ADV-E6-*` rows, the Stage 2.5/4.5
checkpoint also produces a separate
`claim-strength-drift-disposition/1.0` sidecar using
`scripts/claim_strength_drift_disposition.py`. The sidecar binds the exact
finding-set bytes, draft, and revision bundle and records one action plus
one runtime-recomputed raw session-event digest per row. The transient input
names one absolute run-local event-artifact path per disposition; those files
stay outside the repository. Build and replay validation safely reopen the
exact regular non-symlink files. The sidecar carries event ids, digests, and
honest unauthenticated provenance, but no path or raw message. It travels with
the Integrity Report but does not mutate the report or producer-owned finding set.
`pipeline_action=authorized_to_continue` is legal only when every row is
`authorize_with_reason`; `restore_required` and `paused` do not authorize the
current draft to advance. No generic checkpoint confirmation or ordinary
advisory default substitutes for this sidecar.

The contracts make reported E6 rows, artifact bindings, one-to-one event
references, and disposition routing replayable. A 64-hex assertion alone is
insufficient: build and `validate` both recompute SHA-256 from explicitly named
raw event bytes, and missing, changed, symlinked, duplicate, or extra mappings
fail closed. This is byte identity, not event authenticity. The runtime cannot
authenticate the source, interpret what the bytes mean, or prove who produced
them. E6 detection remains semantic and may be model-mediated; neither schema
nor validator proves complete detection, semantic correctness, author identity,
or scientific warrant.

### Deferred Criterion Trajectory Structure (not a current Schema 5 field)

The integrity agent does not judge manuscript quality and MUST NOT mint a
criterion trajectory. The shape below is retained as a design target for a
future Stage 3' Schema 6 field or separately validated re-review sidecar. No
current producer emits it, and current consumers must not treat its absence as
an empty or successful comparison. Stage 3' continues to use its existing
item-level traceability contract and the orchestrator's explicit narrative
regression check.

```
criterion_trajectory: {
  round: integer,          // revision round number (1 or 2)
  dimensions: {
    <dimension>: {
      previous_judgement: enum,  // EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED
      current_judgement: enum,
      change: enum,              // IMPROVED/UNCHANGED/REGRESSED/NOT_COMPARABLE
      previous_evidence: list[evidence_anchor],
      current_evidence: list[evidence_anchor],
      rationale: string,
      decision_bearing: boolean
    }
  },
  unresolved_decision_bearing_regressions: list[string],
  early_stop_eligible: boolean,
  early_stop_rationale: string
}
```

**Compatibility**: readers may preserve an older `score_trajectory` or
experimental `criterion_trajectory` object as opaque historical metadata, but
current producers must not emit or interpret it. The orchestrator performs a
criterion-local narrative regression check and uses `NOT_COMPARABLE` when the
criteria or evidence base changed; it does not fabricate this machine object.

### Issue Severity Levels

| Severity | Meaning | Pipeline Impact |
|----------|---------|-----------------|
| `SERIOUS` | Fabricated reference, falsified data, gross distortion | Blocks pipeline; MUST fix |
| `MEDIUM` | Wrong DOI, incorrect page number, misattribution | Blocks pipeline; MUST fix |
| `MINOR` | Missing co-author, formatting inconsistency | Does NOT block; advisory |

---

## Schema 6: Review Report (academic-paper-reviewer -> pipeline)

**Producer**: `academic-paper-reviewer/editorial_synthesizer_agent`
**Consumer**: `academic-pipeline/pipeline_orchestrator_agent` | `academic-paper/draft_writer_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `editorial_decision` | enum | `"Accept"` / `"Minor Revision"` / `"Major Revision"` / `"Reject"` |
| `reviewer_reports` | list[ReviewerReport] | Individual review reports |
| `consensus` | enum | `"CONSENSUS-4"` / `"CONSENSUS-3"` / `"SPLIT"` / `"DA-CRITICAL"` |
| `revision_roadmap` | object | Non-ranking immutable roadmap core; current machine form is `revision-roadmap/1.0` |
| `calibration_status` | const | Current Schema 6 producer emits `NOT_CALIBRATED`. `PROFILE_MEASURED` is reserved until a closed, hash-bound empirical-profile contract and replay validator can prove an exact target/topology match; a profile name or prose claim cannot upgrade this field. |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `confidence_score` | integer | *(legacy/read-only)* Historical 0-100 editorial-confidence field. Current producers do not emit it; consumers cannot use it for ranking, weighting, calibration, or decision derivation. |
| `review_panel_provenance` | closed union | REQUIRED for current `reviewer_full` output; every other closed mode omits it. The exact machine contract is [`contracts/reviewer/review_panel_provenance_carrier.schema.json`](contracts/reviewer/review_panel_provenance_carrier.schema.json). Valid form: `{schema_version: "review-panel-provenance-carrier/1.0", status: "valid", review_mode: "reviewer_full", artifact_path, artifact_sha256, normalized_manifest_sha256, execution_topology_sha256, fresh_context_scope: "within_panel_attempt_only", axes}` only after exact raw-byte digest verification and deterministic replay. Invalid form: `{schema_version: "review-panel-provenance-carrier/1.0", status: "invalid", review_mode: "reviewer_full", reason: "absent"|"unreachable"|"digest_mismatch"|"schema_invalid"|"replay_invalid", fresh_context_scope: "within_panel_attempt_only", axes: {all six fields: "unknown"}}`; it carries no path or digest that could look verified. `scripts/review_panel_provenance.py validate-schema6` enforces required presence for `reviewer_full`, omission for the other closed modes, raw artifact digest, artifact replay, and both embedded digests. No other members are admitted. `fresh_context` never claims freshness across attempts. Never reconstruct either form from letter prose, persona labels, or intended routing. |
| `judge_record` | object | #539/#740 judge transparency: `{verification_judge, round1_panel_provenance, cross_model_pass: "ran"|"partial"|"not_configured"|"failed", cross_model_items_judged?: int, cross_model_items_total?: int (required when partial), cross_model_id?, failure_reason?, prompt_rubric_surfaces, reviewer_configuration?, evidence_seen, judging_budget_note, precommitment_hash?, routing_status?, apply_chain_witness?}`. Current `round1_panel_provenance` copies the closed Schema 6 carrier including its schema/mode/scope fields: a replay-valid reference plus raw `artifact_sha256`, `normalized_manifest_sha256`, `execution_topology_sha256`, and six axes, or an invalid state with reason `absent|unreachable|digest_mismatch|schema_invalid|replay_invalid` and six unknown axes. It never reconstructs seat identity from letter prose. Legacy strings remain read-only input. `cross_model_pass` is one typed execution fact, not a binary independence claim. `reviewer_configuration` (optional, #574/#576 pre-work) records yardstick continuity: `"round1_cards_reused"` or the verbatim `[YARDSTICK-REGENERATED: <original|revised> manuscript — <reason>]` marker per `re_review_mode_protocol.md` § Yardstick Continuity; absent = pre-yardstick-continuity report. Three #576 optional fields (absent = pre-#576 report): `precommitment_hash` (sha256 of the Phase-1 pre-commitment artifact the verdicts were committed against — the judge's fixed reference); `routing_status` (`oneOf`: the three CONSTANTS `"card_mapped"` / `"[ROUTING-DEGRADED: cards unparsable]"` / `"[ROUTING-DEGRADED: no round-1 cards]"` + one PATTERN for the parameterized unmapped-labels form `[ROUTING-DEGRADED: unmapped labels — <payload>]` per the §10 payload grammar — the payload is accountability content, never collapsed to a bare enum; `reviewer_configuration` is untouched and keeps its own two values); `apply_chain_witness` (current #576 1.1: `"pass"` / `"fail"` / `"not_run_no_reports"`; archived 1.0 alone retains `"first_link_not_run"`). Emitted by re-review (Stage 3'); absent = pre-#539 report. External motivation: Ren et al. arXiv:2607.13104 §8.1.2. |

### ReviewerReport Object

| Field | Type | Description |
|-------|------|-------------|
| `reviewer_id` | string | Reviewer identifier (e.g., `EIC`, `R1`, `R2`, `R3`, `DA`) |
| `role` | string | Reviewer role description |
| `criterion_judgements` | list[CriterionJudgement] | Current evidence-anchored judgements. Each applicable criterion appears once with `{criterion_id, criterion_source, judgement_scale, judgement, evidence_anchors, rationale, uncertainty_or_scope_limit, decision_bearing, decision_bearing_reason}`. Narrative reports use `judgement_scale: narrative` with `EXCEEDS` / `MEETS` / `PARTLY_MEETS` / `DOES_NOT_MEET` / `NOT_ASSESSED`. Sprint-contract reports use `judgement_scale: sprint_contract` and copy the contract's `block` / `warn` / `pass` / `not_assessed` value and criterion source exactly. Producers never translate between the two scales. The list is never totaled, weighted, averaged, or mechanically mapped to a decision. |
| `strengths` | list[string \| Strength] | Paper strengths identified. Current-format cards emit Strength objects `{description: string, evidence_anchor: object}` — the same typed-anchor shape as Weakness, since A2's every-finding rule covers both polarities (#574 A2; a section-level locator suffices for a strength). A bare string = legacy card (consumers treat it as description-only). |
| `weaknesses` | list[Weakness] | Paper weaknesses identified |
| `questions` | list[string] | Questions for the authors |
| `coverage_receipt` | object | *(conditional, #574 A1)* REQUIRED when `strengths` or `weaknesses` is EMPTY: `{covers: "strengths" \| "weaknesses" \| "both", rows: [{dimension: string, checked: string, basis: string}]}` — preserves the reviewer's Coverage Receipt so consumers can distinguish a reviewed-empty list from a thin or truncated review. Absent with empty lists = legacy/invalid current-format card |
| `reviewer_confidence` | integer | *(optional, #574 A3)* The reviewer's report-level Confidence Score, 1-5 (template § Confidence Score) — self-reported uncertainty/scope metadata and the legacy-card fallback source when a weakness lacks per-finding `confidence` (`[CONFIDENCE-SOURCE: report-level]`). It never weights, excludes, or resolves a finding. |
| `dimension_scores` | object | *(legacy/read-only)* Historical field name and sprint-contract compatibility input. Current narrative-review producers do not emit it. If a current sprint-contract adapter carries categorical `block` / `warn` / `pass` / `not_assessed` values under this legacy name, consumers may transport them but never interpret them as numbers. Historical numeric values cannot feed current synthesis, trajectory, or calibration. |

### Weakness Object

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | What the weakness is |
| `severity` | enum | `critical` / `major` / `minor` — the CANONICAL single source for finding severity across the reviewer stack (#574 A3). Reviewer cards and templates carry it explicitly per finding (title-case `Critical`/`Major`/`Minor` on prose surfaces maps to this enum; the DA's `OBSERVATION` category is a non-defect channel that never enters `weaknesses[]`). Consumers transport it, never re-derive it; a legacy card without per-finding tags is marked `[SEVERITY-SOURCE: letter-fallback]` by the synthesizer. |
| `type` | enum | `methodology` / `theory` / `evidence` / `writing` / `structure` / `ethics` |
| `evidence_anchor` | object | *(optional, #574 A2)* Typed anchor: `{anchor_type: "text" \| "table" \| "figure" \| "equation" \| "dataset" \| "absence", locator: string, quote: string, absence_scope: string, check_performed: string}`. Conditional members: `quote` (≤ 25 words) is REQUIRED when `anchor_type = "text"`; `absence_scope` and `check_performed` are REQUIRED when `anchor_type = "absence"`; all three are omitted for other types. Critical/major weaknesses are expected to carry an adequate, applicable anchor; absent field = legacy card. |
| `confidence` | integer | *(optional, #574 A3)* Per-finding self-reported uncertainty/scope confidence 1-5 from the reporting reviewer. Absent = legacy card; consumers may display the report-level fallback with `[CONFIDENCE-SOURCE: report-level]`, but neither value may change consensus counts, severity, decision bearing, or arbitration. |
| `competence_basis` | string | *(optional, #574 A3)* One-phrase basis for `confidence` (e.g. `"core expertise: psychometrics"`, `"adjacent field: applying general standards"`). |

---

## Schema 7: Revision Roadmap (reviewer -> academic-paper revision)

**Producer**: `academic-paper-reviewer/editorial_synthesizer_agent`
**Consumer**: `academic-paper/draft_writer_agent` | `academic-pipeline/pipeline_orchestrator_agent`

### Current machine family (#670)

The immutable reviewer-owned core MUST validate against
[`contracts/revision/revision_roadmap.schema.json`](contracts/revision/revision_roadmap.schema.json)
with `schema_version: revision-roadmap/1.0`. It binds the exact base draft and
block manifest, carries recomputable counts, and keeps `items[]` in deterministic
source-traceability order. It contains no author decision and no user view.

Every item separates:

- transported reviewer `severity`;
- editorial `obligation_class: must_fix | should_fix | consider`;
- typed `cost_scope` (sentence/section/re-analysis/new-data/other surface, never
  hours or a deadline);
- a closed bounded `consequence` code plus typed target; and
- exact `proposed_targets[]` block/operation scopes.

Transported finding metadata remains a distinct current-contract surface.
Unless `source_kind` marks a question/editorial item with no driving finding,
the roadmap schema conditionally requires the driving finding's severity,
anchor, confidence, and competence basis.

| Field | Type | Description |
|-------|------|-------------|
| `severity` | enum | *(optional, #574 A3)* Transported Schema 6 finding severity (`critical`/`major`/`minor`) of the driving sub-claim; conditionally required when `source_kind` is absent |
| `severity_source` | string | *(optional, #574 A3)* Fallback provenance for `severity` — the verbatim tag, e.g. `[SEVERITY-SOURCE: letter-fallback]`; absent means the per-finding seat tag was direct |
| `evidence_anchor` | object | *(optional, #574 A2)* The driving finding's typed anchor — same shape as the Schema 6 Weakness `evidence_anchor`; conditionally required when `source_kind` is absent |
| `confidence` | integer | *(optional, #574 A3)* The driving finding's per-finding confidence 1-5; conditionally required when `source_kind` is absent |
| `competence_basis` | string | *(optional, #574 A3)* One-phrase basis for the transported confidence; conditionally required when `source_kind` is absent |
| `confidence_source` | string | *(optional, #574 A3)* Fallback provenance for `confidence` — the verbatim tag, e.g. `[CONFIDENCE-SOURCE: report-level]` |
| `corroborating_sources` | list[object] | *(optional, #574 A2/A3)* Remaining corroborating findings with their own reviewer, severity, anchor, confidence, basis, and fallback provenance; nothing is dropped or merged |
| `source_kind` | enum | *(optional, #574 A3)* `question` / `editorial`; when present, all transported finding fields are forbidden because no driving finding exists |

`source_refs[]` are the mechanical order key. `R<n>` is derived from that
immutable order filtered to `must_fix`; it is a transport reference, never a
rank. Current artifacts reject legacy `priority`, `type`, and
`deadline_suggestion` fields. Historical artifacts remain historical and are
not silently upgraded.

### Author-owned sidecar

Explicit author choices live separately in
[`contracts/revision/author_adjudication.schema.json`](contracts/revision/author_adjudication.schema.json).
The deterministic builder consumes only
[`contracts/revision/author_adjudication_input.schema.json`](contracts/revision/author_adjudication_input.schema.json)
plus the exact roadmap/base/claim-surface artifacts. It records one
`author_triage: will_address | wont_address | not_on_point` per item, decline
reasons, exact authorized targets, exact registered-claim replacements, and
exact declined-overlap collateral authority. No choice is inferred.

`display_order` is a full presentation-only permutation. It never changes the
roadmap array, `R<n>`, patch authority, or re-review arithmetic.

Registered claim surfaces use
[`contracts/revision/claim_surface_manifest.schema.json`](contracts/revision/claim_surface_manifest.schema.json).
Every surface binds an exact `(scoped_manifest_id, claim_id)`, raw UTF-8 span,
block, original text/hash, and current rung. The protected `original_text` must
equal the referenced ClaimIntent `claim_text` byte-for-byte; pairing a valid
claim id with unrelated prose is invalid. A normal accepted edit grants no
claim-strength move; an exact author authorization is additionally required.

### Integrity-correction author sidecar

`integrity-correction-list/1.0` carries proposal-only `proposed_targets`; it is
never write authority. The author input contains one `authorize` or
`stop_without_write` decision per issue and the exact `revision_patch_sha256`
the author approved. The deterministic builder copies that digest and adds
only exact base/list/round bindings in
[`contracts/revision/integrity_correction_authorization.schema.json`](contracts/revision/integrity_correction_authorization.schema.json).
Apply requires both `--integrity-issue-list` and
`--integrity-authorization`; a changed `new_text`, stopped issue, scope
widening, missing decision, or producer-computed replacement digest fails
before writing.

### Revision-Evidence Bundle

The complete continuous chain MUST validate against
[`contracts/revision/revision_evidence_bundle.schema.json`](contracts/revision/revision_evidence_bundle.schema.json).
It begins from an exact integrity-PASS draft and carries every review write,
all-declined no-op, or integrity-correction round through the exact final draft.
Current review writes use patch format 1.1 and apply-report format 1.3;
integrity rounds additionally carry the exact author patch-authorization
sidecar.
Consumers must hash-load every named artifact, rerun the current pure patch
validator/splicer for each write round, and require byte-exact replay output to
equal the carried post draft; matching reported hashes alone are insufficient.

---

## Schema 8: Response to Reviewers (academic-paper revision -> reviewer re-review)

**Producer**: `academic-paper/draft_writer_agent` (revision mode)
**Consumer**: `academic-paper-reviewer/editorial_synthesizer_agent` (re-review)

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `revision_round` | integer | Which revision round (1, 2, ...) |
| `items` | list[ResponseItem] | Response to each revision roadmap item |
| `summary` | object | `{resolved: integer, limitations: integer, unresolvable: integer, disagreed: integer}` |
| `word_count_delta` | integer | Net word count change (positive = added, negative = removed) |
| `new_references_added` | integer | Count of new references added during revision |
| `summary_of_changes` | string | High-level summary of all modifications |
| `new_content_highlight` | list[string] | Sections with substantial new content |

### ResponseItem Object

| Field | Type | Description |
|-------|------|-------------|
| `roadmap_item_id` | string | Corresponds to RoadmapItem.id (e.g., `REV-001`) |
| `reviewer_comment` | string | Original reviewer comment (quoted) |
| `author_response` | string | Detailed response to the reviewer |
| `change_location` | string | Where in the paper the change was made (section + paragraph) |
| `change_block_ids` | list[string] | *(optional, #390 patch-mode rounds)* Block IDs the change landed in (`B0042`-form), the machine-checkable sibling of the free-text `change_location` — cross-checkable against the apply report's op list. **Populated by the orchestrator from the apply report, never by the writer** (spec §3.5 role split: inserted blocks get fresh IDs only at apply time, so the writer cannot know them; it emits provisional response items and the orchestrator completes the mechanical fields). Absent field = pre-patch-era or escalated full re-emission round (valid). |
| `status` | enum | `"RESOLVED"` / `"DELIBERATE_LIMITATION"` / `"UNRESOLVABLE"` / `"REVIEWER_DISAGREE"` |
| `decline_justification` | string | Required if status is `DELIBERATE_LIMITATION`, `UNRESOLVABLE`, or `REVIEWER_DISAGREE`; must cite evidence |

### Example

```markdown
## Response to Reviewers — Round 1

**Summary**: We have addressed all 12 revision items. 10 were fully addressed, 1 marked as deliberate limitation with explanation, and 1 respectfully declined with justification.

**Word Count Delta**: +420 words
**New References Added**: 3

### REV-001 (R1, R2 — CONSENSUS-3, must_fix)
**Reviewer Comment**: "The sample size justification is insufficient for the claimed effect size."
**Status**: RESOLVED
**Response**: We have added a formal power analysis (G*Power 3.1) in Section 3.2, paragraph 2. The analysis confirms that our sample of N=240 provides 0.85 power to detect a medium effect (d=0.5) at alpha=0.05...
**Changes**: Section 3.2 paragraph 2 (new content, +180 words)

### REV-007 (DA — DA-CRITICAL, must_fix)
**Reviewer Comment**: "Selective reporting of outcomes suggests confirmation bias."
**Status**: RESOLVED
**Response**: We acknowledge this valid concern. We have now reported ALL pre-registered outcomes including the two non-significant results (peer interaction frequency, self-efficacy subscale)...
**Changes**: Section 4.1 Table 3 (expanded), Section 5 paragraph 4 (new discussion of null results)
```

---

## Schema 9: Material Passport (cross-stage metadata)

**Purpose**: Accompanies every artifact as it passes between stages, providing provenance and verification tracking.

The #673 activity fields named in the top-level exclusion are deliberately not
Schema 9 fields. In particular, the #673 projection of the terminal state
file's root `run_id` plus sealed root `adjudication_activity_sources` are
activity source/run authority; copying either activity projection into a
passport would create an unauthorized second authority. Existing independently
schema-owned `run_id` fields are unaffected.

### Separately named review-target authority (#683/#684)

`ReviewTargetContext`, its rendered Target Criteria Brief, and
`ReviewCriteriaBindingManifest` are separately named handoff artifacts, not
Material Passport fields. The binding manifest is the single pointer/receipt
authority for one `target_review_id`; a passport or state record may name its
portable reference but must not copy or independently reconstruct its selected
criteria, hashes, digest, conflict groups, or receipts.

The three receipt consumers are `formative_planning` (`FORMATIVE`),
`internal_evaluator` (`INTERNAL`), and `external_panel` (exactly `EIC`, `R1`,
`R2`, `R3`, `DA`). External and internal Phase 1 calls are manuscript-blind;
applicability is assessed only after the paper-visible boundary. A changed
target/profile requires a new non-comparable target review id. Skipped or
mid-entry stages never receive fabricated receipts.

Critical/Major criteria-aware findings use the separately named
`constructive-review-findings/1.0` sidecar. Its validation is handoff
conformance, not a manuscript verdict or integrity/checkpoint input. See
`shared/references/review_criteria_consumer_protocol.md` and the schemas under
`shared/contracts/review_target/`.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `origin_skill` | string | Which skill produced this artifact (e.g., `deep-research`, `academic-paper`) |
| `origin_mode` | string | Which mode was used (e.g., `full`, `socratic`, `pre-review`) |
| `origin_date` | string | ISO 8601 timestamp of production |
| `verification_status` | enum | `"VERIFIED"` / `"UNVERIFIED"` / `"STALE"` |
| `version_label` | string | Version identifier (e.g., `v1.0`, `v1.1-revised`, `paper_draft_v2`) |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `integrity_pass_date` | string | ISO 8601 timestamp of last integrity verification pass (if applicable) |
| `content_hash` | string | SHA-256 hash of the content (for change detection) |
| `upstream_dependencies` | list[string] | Version labels of artifacts this one depends on |
| `repro_lock` | object \| null | configuration lockfile for artifact reproducibility. See [`artifact_reproducibility_pattern.md`](artifact_reproducibility_pattern.md). `null` = honest opt-out. Required from v3.3.5+ — omitted key fails lint. |
| `compliance_history` | list[object] | Append-only audit trail of `compliance_report` entries (Schema 12). Added v3.4.0+. See [Schema 12](#schema-12--compliance-report-v340) and [`shared/compliance_report.schema.json`](compliance_report.schema.json). |
| `reset_boundary` | list[object] | Append-only ledger. Two entry kinds: `boundary` (recorded at FULL checkpoints when `ARS_PASSPORT_RESET=1`) and `resume` (recorded when `resume_from_passport` consumes a boundary). Added v3.6.3+. Entry shape: [`shared/contracts/passport/reset_ledger_entry.schema.json`](contracts/passport/reset_ledger_entry.schema.json). See [`academic-pipeline/references/passport_as_reset_boundary.md`](../academic-pipeline/references/passport_as_reset_boundary.md). |
| `inquiry_ledger_ref` | object | Optional pointer to the separate opt-in `inquiry-branch-ledger/1.0` user-project artifact. Closed shape: `{ledger_path, ledger_version, content_sha256}` per [`shared/contracts/passport/inquiry_ledger_ref.schema.json`](contracts/passport/inquiry_ledger_ref.schema.json). It carries no branch copy. A missing or digest-mismatched target is `LEDGER-BINDING-BROKEN`; a file without this pointer is ignored with a visible notice. Added #743. |
| `literature_corpus` | list[object] | Optional append-friendly literature corpus. Each entry conforms to [`shared/contracts/passport/literature_corpus_entry.schema.json`](contracts/passport/literature_corpus_entry.schema.json). Produced by user-written adapters (see [`academic-pipeline/references/adapters/overview.md`](../academic-pipeline/references/adapters/overview.md)); ARS does not produce these entries itself. Added v3.6.4+. |
| `audit_artifact` | list[object] | Optional append-only ledger of cross-model audit runs for v3.6.7 downstream-agent deliverables. Each entry conforms to [`shared/contracts/passport/audit_artifact_entry.schema.json`](contracts/passport/audit_artifact_entry.schema.json). Produced by the pipeline orchestrator after Layer 2 + Layer 3 verification of wrapper-emitted proposal entries; only `persisted` entries are stored here. Added v3.6.7+. |
| `slr_lineage` | boolean | Run-level provenance flag set by `pipeline_orchestrator_agent` at the Stage 1 → Stage 2 handoff. `true` iff any stage in this run history was produced by `deep-research` in systematic-review mode. Consumed by `disclosure` mode renderer (`--policy-anchor=prisma-trAIce` track gate per `policy_anchor_disclosure_protocol.md` §3.1). Absence = `false` = cold-start path (renderer requires explicit `mode=` per §4.3 G2 invariant fallback rule). Added v3.7.4+. See [Run-level lineage signal (v3.7.4)](#run-level-lineage-signal-v374) below. |
| `experiment_intake_declaration` | object | Passport-level intake decision (#260, D7). `status` ∈ `{experiments_declared, no_experiments_declared, legacy_unknown}` + `declared_at` + `declared_by: scholar`. Set by whichever agent owns Stage 1 intake (the intake/orchestrator layer — NOT the three manifest writers). **Fail-closed**: a passport treated-as-post-#260 (the default — only a `repro_lock.ars_version` proven `< the #260 constant` is `legacy_unknown`) with this field ABSENT is a gate FAIL. Even a literature-only run must carry `{status: no_experiments_declared}`. EP-INV-4 enforces declaration↔provenance symmetry. See [Experiment Provenance Intake (#260)](#experiment-provenance-intake-260) below. |
| `experiment_provenance` | list[object] | Optional scholar-entered ledger of experiments run EXTERNALLY (#260, D1). Each entry conforms to [`shared/contracts/passport/experiment_provenance_entry.schema.json`](contracts/passport/experiment_provenance_entry.schema.json) — `experiment_id` (passport-flat, frozen at intake) + nested `repro_lock` + `planned_vs_executed[]` + `negative_results[]` + `known_limitations[]`. ARS does not run experiments, does not auto-fill provenance, does not judge experiment correctness. Joined from claims via `claim_intent_manifest.planned_experiment_ids[]`. Gated at the integrity verification stage (Stage 2.5/4.5, D6). Added #260. |
| `experiment_alignment_results` | list[object] | Optional aggregate of claim→experiment alignment verdicts (#260, D4) — the FOURTH ref_slug-less claim-finding aggregate (alongside `uncited_assertions` / `claim_drifts` / `constraint_violations`). Each entry conforms to [`shared/contracts/passport/experiment_alignment_result.schema.json`](contracts/passport/experiment_alignment_result.schema.json); `alignment_verdict` ∈ `{ALIGNED, OVERSTATED, NOT_SUPPORTED_BY_PROVENANCE, PROVENANCE_INSUFFICIENT}`. **Produced by the integrity verification agent AT the gate** (mirrors #261 C3), NOT by the claim-alignment audit agent. EA-INV-1/2 enforce id-uniqueness + reference resolution. Carried forward by `pipeline_orchestrator_agent`'s aggregate hand-off. Added #260. |

### Example

```markdown
## Material Passport

- Origin Skill: academic-paper
- Origin Mode: full
- Origin Date: 2026-03-08T14:30:00Z
- Verification Status: VERIFIED
- Version Label: paper_draft_v2
- Integrity Pass Date: 2026-03-08T15:45:00Z
- Content Hash: a3f2b7c9...
- Upstream Dependencies: [research_v1, bibliography_v1, synthesis_v1]
```

### Inquiry Branch Ledger Pointer Extension (#743)

When `ARS_INQUIRY_LEDGER=1` and a second branch is recorded, Schema 9 may gain
one `inquiry_ledger_ref`. The ledger itself stays beside the passport as a
canonical JSON user-project artifact; the passport carries only its
workspace-relative path, exact contract version, and SHA-256 over the complete
canonical ledger bytes. Profile documents named by the ledger's bindings are
separate exact inputs and must be supplied to replay—this pointer does not
silently select a current profile.

The runtime in `scripts/inquiry_branch_ledger.py` holds a stable sidecar lock
and uses a durable recovery journal when publishing ledger and passport bytes.
Cooperating loads recover a valid pending transaction before checking the
pointer. Without a valid journal, pointer/file mismatch fails visibly and an
unpointed candidate is ignored. Neither the pointer nor the ledger changes an
integrity verdict, authenticates an author, or licenses a quality claim.

### Reset Boundary Extension (v3.6.3)

When `ARS_PASSPORT_RESET=1`, Schema 9 gains an append-only `reset_boundary[]` ledger with two entry kinds: `boundary` (recorded at FULL checkpoints) and `resume` (recorded when a boundary is consumed):

```yaml
reset_boundary:
  # Kind 1: boundary entry at Stage 2 FULL checkpoint
  - kind: boundary
    hash: a3f2b7c9d0e1
    stage: "2"
    next: "2.5"
    generated_at: 2026-04-23T14:00:00Z
    session_marker: sess-20260423-1a2b
    version_label: paper_draft_v1
    mode: full
    verification_status: VERIFIED

  # Kind 1 with pending_decision: Stage 3 rejection case
  - kind: boundary
    hash: b4c2d8e7f0a1
    stage: "3"
    next: "4"
    generated_at: 2026-04-24T10:00:00Z
    session_marker: sess-20260424-3c4d
    version_label: paper_draft_v2
    mode: full
    pending_decision:
      question: "Stage 3 reviewer decision"
      options:
        - value: revise
          next_stage: "4"
          next_mode: revision
        - value: restructure
          next_stage: "2"
          next_mode: plan
        - value: abort
          next_stage: null   # null = terminate pipeline

  # Kind 2: resume event consuming the first boundary (Stage 2 → 2.5)
  - kind: resume
    consumes_hash: a3f2b7c9d0e1
    generated_at: 2026-04-23T15:00:00Z
    session_marker: sess-20260423-5e6f
  # append-only; never overwrite, never reorder
```

Consumers match `resume_from_passport=<hash>` against `boundary` entries. A `boundary` is **awaiting resume** iff no later `resume` entry carries `consumes_hash == <boundary hash>`. Hash mismatch on resume is a hard error.

See [`academic-pipeline/references/passport_as_reset_boundary.md`](../academic-pipeline/references/passport_as_reset_boundary.md) for the full protocol.

### Literature Corpus Input Port (v3.6.4)

The optional `literature_corpus[]` field is Schema 9's input port for user-owned literature. Each entry is a bibliographic record conforming to `literature_corpus_entry.schema.json` (CSL-JSON author format, β required set).

ARS does not produce these entries. User-written adapters read their own corpus source (Zotero, Obsidian, folder, Notion, etc.) and emit a passport with `literature_corpus[]` populated. Three reference adapters ship with v3.6.4 under [`scripts/adapters/`](../scripts/adapters/).

Consumer integration ships in v3.6.5: `bibliography_agent` (deep-research, Phase 1) and `literature_strategist_agent` (academic-paper, Phase 1) read `literature_corpus[]` via the corpus-first, search-fills-gap flow. See [`academic-pipeline/references/literature_corpus_consumers.md`](../academic-pipeline/references/literature_corpus_consumers.md) for the full consumer protocol, the four Iron Rules, and per-consumer reading instructions.

See [`academic-pipeline/references/adapters/overview.md`](../academic-pipeline/references/adapters/overview.md) for the adapter contract.

### Tortured-Phrase Advisory Extension (#660)

An entry's existing optional `bibliographic_integrity_signals[]` carrier may
hold `bibliographic-integrity-signal/1.2` tortured-phrase rows. When the local
check is invoked, there is one current row for `cited_title` and one for
`cited_abstract`; the surfaces never share a rolled-up status. A missing
abstract is retained as `not_checked` / `unresolved` with
`ABSTRACT_MISSING`; a present whitespace-only abstract uses `ABSTRACT_EMPTY`.
A checked zero-match row reports only no observed match on
the exact hash-bound surface and is not a clean certificate.

The producer consumes an explicitly named, exact-byte-SHA-256-bound
user-supplied or synthetic snapshot/manifest pair. It has no native PPS
importer or fetch path, redistributes no PPS list content, and invokes no
model, API, judge, or ambient clock. It writes a new passport copy rather than
changing the source passport, title, abstract, or citation in place. Phase 1
corpus consumers remain read-only and do not use this heuristic to include,
exclude, rank, rewrite, or label a source's origin.

Rows remain `HEURISTIC-INDICATOR` with a closed
`HEURISTIC-ADVISORY` / `UNMEASURED` context. They render only in the single
`Bibliographic Integrity Advisories` section, never as a reference marker,
terminal policy, gate, replacement, or rewrite. The separate own-draft
`tortured-phrase-advisory/1.0` artifact is not a Schema 9 field and carries no
paper-mill, AI/author-origin, cleanliness, contextual-validity, or accuracy
claim. Authority: [`shared/bibliographic_integrity_signals.md`](bibliographic_integrity_signals.md).

### Preregistration Artifact Handoff and #672 Advisory

`preregistration-artifact/1.0` accompanies Schema 9 as a separately named,
byte-preserved JSON sidecar; it is not embedded into or reconstructed from an
ad hoc Material Passport field. Its provided companion is a second separately
named artifact. This keeps the raw sidecar bytes available for finalizer replay
without changing the legacy passport roster.

The research architect supplies only the caller declaration and, for a completed
provided preregistration, an explicitly named companion handle. Because that
agent has no shell, it does not compute a digest or build/update the sidecar. A
shell-capable orchestrator is the sole caller of
`scripts/build_cross_document_consistency_advisory.py
build-preregistration-artifact`, including for an explicit unavailable receipt,
and supplies the caller-held RFC3339 `declared_at`.

Academic-paper intake and every pipeline transition strict-parse, digest-check,
and replay the exact `preregistration-artifact/1.0` sidecar and provided companion
before carrying both byte-for-byte. Consumers do not infer a missing status,
repair a digest, reinterpret provenance, follow a stored path, or replace the
artifact with `deep-research/templates/preregistration_template.md`. Later
explicit user supply creates a new sidecar through the same builder.

At Stage 4.5, the #672 source manifest projects the exact sidecar: `provided`
becomes `present`; `not_provided` becomes `source_missing`; and
`access_failed`/`retrieval_failed` retain their state. Unavailable entries keep
the sidecar artifact ID and have null path/bindings with `not_provided`
provenance. A formerly provided companion that no longer replays is
`SOURCE_BINDING_INVALID`, not an ordinary not-checked receipt.

The final `cross-document-consistency-advisory/1.0` is a separate checkpoint
carrier, not a Material Passport field or terminal state. It is
`LLM-ADVISORY` / `UNMEASURED`, creates no score, gate, authorization, ClaimIntent,
rewrite, or consent/protocol duplicate, and cannot change integrity status or
Stage-5 routing. #660 runs first and #672 second at the same one mandatory
checkpoint against the identical accepted-draft artifact ID/SHA-256; a manuscript
revision stales both. See
[`shared/references/cross_document_consistency_advisory_protocol.md`](references/cross_document_consistency_advisory_protocol.md).

### Audit Artifact Ledger (v3.6.7)

Schema 9 gains an optional append-only `audit_artifact[]` ledger recording cross-model audit runs that gate the three v3.6.7 downstream agents (`synthesis_agent`, `research_architect_agent` survey-designer mode, `report_compiler_agent` abstract-only mode). Each entry conforms to [`shared/contracts/passport/audit_artifact_entry.schema.json`](contracts/passport/audit_artifact_entry.schema.json).

The ledger stores only `persisted` entries — those merged by `pipeline_orchestrator_agent` after Layer 2 (JSONL schema) + Layer 3 (sidecar metadata) anti-fake-audit checks pass per the eleven gating checks at [`docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md`](../docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md) §5.2. Wrapper-emitted `proposal` entries live under `audit_artifacts/<run_id>.audit_artifact_entry.json` until orchestrator consumes them; they never reach the passport.

```yaml
audit_artifact:
  - stage: 2                                   # destination stage gated by this audit
    agent: synthesis_agent                     # one of the three v3.6.7 agents
    deliverable_path: chapter_4/synthesis.md
    deliverable_sha: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2
    run_id: 2026-04-30T15-22-04Z-d8f3
    bundle_id: phase2-chapter4-2026-04-30
    bundle_manifest_sha: 9a8b7c6d5e4f3b2a1c0d9e8f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9876
    artifact_paths:
      jsonl: audit_artifacts/2026-04-30T15-22-04Z-d8f3.jsonl
      sidecar: audit_artifacts/2026-04-30T15-22-04Z-d8f3.meta.json
      verdict: audit_artifacts/2026-04-30T15-22-04Z-d8f3.verdict.yaml
    verdict:
      status: MINOR                            # persisted enum: PASS | MINOR | MATERIAL
      round: 2
      target_rounds: 3
      finding_counts:
        p1: 0
        p2: 0
        p3: 1
      verified_at: "2026-04-30T15:23:11.847Z"  # RFC 3339 UTC string, ms precision (quoted: schema is `string` + regex, not YAML datetime); strict-monotonic per scripts/_next_verified_at_ms.py
      verified_by: pipeline_orchestrator_agent
  # append-only; never overwrite, never reorder
```

**Semantics:**

- `stage` is the **destination stage** the just-completed deliverable is about to enter (synthesis_agent → 2, research_architect_agent survey-designer → 2, report_compiler_agent abstract-only → 5).
- `verdict.status` enum is `["PASS", "MINOR", "MATERIAL"]` for persisted entries. `AUDIT_FAILED` is reachable only in the proposal arm and never persists; see [`audit_artifact_entry.schema.json`](contracts/passport/audit_artifact_entry.schema.json) Lifecycle-conditional fields for the rationale.
- `verdict.verified_at` and `verdict.verified_by` are required on persisted entries (orchestrator-written) and forbidden on proposal entries (wrapper-emitted).
- Multiple entries for the same `(stage, agent, deliverable_sha)` represent multiple audit rounds; orchestrator selects the latest by `verified_at` for verdict reads.
- If `deliverable_sha` changes (deliverable mutated), prior entries become stale but remain as audit history; orchestrator only honors entries whose `deliverable_sha` matches the current deliverable.

**This mirrors the v3.6.3 `reset_boundary[]` append-only pattern**: history preserved, freshness computed by ledger scan. Deletion or reordering is forbidden; lint at `scripts/check_audit_artifact_consistency.py` enforces the invariant family at [`docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md`](../docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md) §3.7.

For the orchestrator-side gate procedure (Path A latest-by-`verified_at` selection, Path B proposal merge after Layer 2 + Layer 3 verification), the canonical contract is [`docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md`](../docs/design/2026-04-30-ars-v3.6.7-step-6-orchestrator-hooks-spec.md) §5.6 (Path A/B fall-through with the §5.6 A1.5 superseding-proposal preflight) plus §5.2 (eleven Layer 2 + Layer 3 gating checks). Implementation lands as a subsection of `academic-pipeline/agents/pipeline_orchestrator_agent.md` (Phase 6.6 deliverable). For the resume-time re-verification semantics, see [`academic-pipeline/references/passport_as_reset_boundary.md`](../academic-pipeline/references/passport_as_reset_boundary.md).

### Experiment Provenance Intake (#260)

Schema 9 gains the **intake + alignment** layer for experiments — NOT an execution layer. ARS keeps experiment execution outside the pipeline: the scholar runs experiments externally and brings results back. This extension records disclosure and lets manuscript claims be audited against declared provenance. It does **not** run experiments, judge experiment correctness, auto-fill provenance, or require provenance for literature-only pipelines.

**Three additions** (all under the Optional-Fields table above):

1. `experiment_intake_declaration` (passport-level object) — the Stage 1 intake decision, set by the intake/orchestrator layer (the agent that owns Stage 1 for that entry path), never by the three manifest writers:

   ```yaml
   experiment_intake_declaration:
     status: experiments_declared        # | no_experiments_declared | legacy_unknown
     declared_at: "2026-06-08T10:00:00Z"
     declared_by: scholar                # always scholar — an intake decision, not an agent emission
   ```

   **Fail-closed legacy boundary (D7).** The default is treat-as-post-#260, NOT treat-as-legacy. A passport is `legacy_unknown` (advisory) ONLY with positive proof it predates #260 — `repro_lock.ars_version` present AND `< the #260 release constant` (frozen in the gate at ship time). Everything else — including a passport with no `repro_lock` or a `repro_lock` with no `ars_version` — is treated as post-#260, so the declaration is REQUIRED and its absence is a gate FAIL. Version-unprovable ≠ legacy. This shuts the back door: a new run cannot dodge the declaration by omitting `repro_lock` to make its version unprovable. Even a pure-literature run (e.g. `deep-research lit-review`) must emit `{status: no_experiments_declared}`.

2. `experiment_provenance[]` (scholar-entered list) — one [`experiment_provenance_entry.schema.json`](contracts/passport/experiment_provenance_entry.schema.json) per experiment:

   ```yaml
   experiment_provenance:
     - experiment_id: exp-ablation-A      # passport-flat, FROZEN at intake (a rename is a re-intake event)
       title: "Ablation: remove head pruning"
       repro_lock: { schema_version: "1.0", ... }   # same inline shape as the passport-level repro_lock
       planned_vs_executed:
         - planned: "macro-F1 on held-out test, pruning removed"
           executed: true
           result_file: results/ablation_A.json
           metric: macro-F1
           value: 0.842
       negative_results: []               # KEY MUST be present (absent = malformed FAIL); empty [] is well-formed
       known_limitations: []              # KEY MUST be present; empty [] routes to the D6 check-4 advisory
   ```

   The `experiment_id` values are FROZEN once `status == experiments_declared` is set; writers reference that key space via `claim_intent_manifest.planned_experiment_ids[]`. A post-intake rename is a re-intake event (re-run the manifest emitters), caught by EP-INV-2 if it dangles.

3. `experiment_alignment_results[]` (integrity-agent-produced list) — the fourth ref_slug-less claim-finding aggregate. Each [`experiment_alignment_result.schema.json`](contracts/passport/experiment_alignment_result.schema.json) row carries an `alignment_verdict` computed by the integrity verification agent **at the gate** (Stage 2.5/4.5), mirroring #261's Phase C3. A mixed-evidence claim (carrying BOTH `planned_refs` and `planned_experiment_ids`) gets one `claim_audit_results[]` row AND one `experiment_alignment_results[]` row; the gate combines them worst-verdict-wins.

**Invariants** (lint-enforced in `scripts/check_claim_audit_consistency.py`): EP-INV-1 (experiment_id unique/passport) · EP-INV-2 (planned_experiment_ids resolve; rename + forward-reference guard) · EP-INV-3 (experiment ids ⟹ empirical; mixed literature+experiment allowed) · EP-INV-4 (declaration↔provenance symmetry) · EA-INV-1 (finding_id unique) · EA-INV-2 (alignment row references resolve; dangling id = structural FAIL, never a verdict). Shape-only validation of a single entry is also available via `scripts/check_experiment_provenance.py`.

See [`docs/design/2026-06-08-260-experiment-provenance-intake-spec.md`](../docs/design/2026-06-08-260-experiment-provenance-intake-spec.md) for the full design (7 decisions D1–D7) and [`examples/passport_with_experiment_provenance.yaml`](../examples/passport_with_experiment_provenance.yaml) for a worked passport.

### Run-level lineage signal (v3.7.4)

Schema 9 gains an optional boolean `slr_lineage` field carrying run-level provenance for downstream renderers that need to know whether the pipeline run included a systematic-review stage.

```yaml
slr_lineage: true   # any pipeline stage was deep-research in systematic-review mode
```

**Semantics:**

- `true` iff `bool(incoming_passport.slr_lineage) or any(stage.skill == "deep-research" and stage.mode in {"systematic-review", "slr"} for stage in state_tracker.stages.values())` at the time the passport is written. The OR is monotonic — a true value persists across resume / mid-entry passports whose `state_tracker.stages` was reconstructed from the ledger and may be empty. Run-level, not artifact-level — distinct from `origin_mode` which records the directly-producing skill's mode.
- Producer: `pipeline_orchestrator_agent` writes the field at every handoff transition; in practice only the Stage 1 → Stage 2 transition can flip `false` → `true`, and the OR keeps the value monotonic thereafter. Reference helper: `scripts/slr_lineage.py` `emit(stages, incoming_slr_lineage)` (or the underlying `resolve_from_stages(stages)` when callers need the pre-OR fragment alone).
- Consumer: `disclosure` mode renderer reads it as `RendererInput.slr_lineage` to dispatch `--policy-anchor=prisma-trAIce` per the §4.3 G2 invariant track gate documented in [`academic-paper/references/policy_anchor_disclosure_protocol.md`](../academic-paper/references/policy_anchor_disclosure_protocol.md) §3.1.
- Backward compat: passports written before v3.7.4 lack the field; renderer treats absence as `false` (cold-start path requiring explicit `mode_param='systematic-review'`). Identical to pre-v3.7.4 behavior.
- G1 boundary: this is a passport-level (run-level provenance) field, distinct from corpus-entry-level fields. The §4.4 #11 G1 invariant scope is `literature_corpus_entry.schema.json` (corpus entry data schema, frozen by Decision Doc §2.1); passport-schema extensions follow the v3.6.3 / v3.6.4 / v3.6.7 precedent and are permitted per Decision Doc §4.4 #11.

Spec: [`docs/design/2026-05-15-issue-111-slr-lineage-emission-design.md`](../docs/design/2026-05-15-issue-111-slr-lineage-emission-design.md). Conformance test: `scripts/test_slr_lineage_emission.py`.

### Claim-Faithfulness Audit Aggregates (v3.8)

v3.8 introduces six passport aggregates around the L3 (claim-faithfulness) audit. They ride in their own arrays on the audit run record rather than under a root `material_passport` schema (per v3.8 spec §8 explicit scope), and only the four audit-output aggregates are gated on `ARS_CLAIM_AUDIT=1`; the writer-side manifest aggregate and the sampling-summary record are independent.

**Writer-side (pre-commitment baseline — NOT gated on ARS_CLAIM_AUDIT):**

- [`shared/contracts/passport/claim_intent_manifest.schema.json`](contracts/passport/claim_intent_manifest.schema.json) — Stage-4 draft claim manifest. Producer: `synthesis_agent` / `draft_writer_agent` / `report_compiler_agent` emit one entry each. Consumer: the audit agent reads them for the D6 set-diff; adapters that preserve passports for a later audit pass MUST preserve this aggregate regardless of whether the audit ran in the producing session.

**Audit output (gated on ARS_CLAIM_AUDIT=1):**

- [`shared/contracts/passport/claim_audit_result.schema.json`](contracts/passport/claim_audit_result.schema.json) — per-citation judgment + retrieval method + defect stage
- [`shared/contracts/passport/claim_drift.schema.json`](contracts/passport/claim_drift.schema.json) — per-claim manifest set-diff records (D6 set-of-text semantics)
- [`shared/contracts/passport/uncited_assertion.schema.json`](contracts/passport/uncited_assertion.schema.json) — assertions present in prose without citation anchor
- [`shared/contracts/passport/constraint_violation.schema.json`](contracts/passport/constraint_violation.schema.json) — negative-constraint violations against retrieved excerpt

**Sampling transparency (when audited_count < total_citation_count):**

- `audit_sampling_summaries[]` — one entry per audit pass when `len(citations) > max_claims_per_paper` triggers stratified sampling. S-INV-1..S-INV-4 invariants (audited_count == |audited_indices|, count ≤ cap, count ≤ total, indices strictly ascending without duplicates). Schema is inline in `scripts/check_claim_audit_consistency.py` (no separate shipped schema file at v3.8.0); drives the paper-level `[CLAIM-AUDIT-SAMPLED — k/N audited]` formatter annotation. Adapters preserving audit runs MUST keep these entries for the transparency record.

Cross-field invariants (INV-1..INV-18 / M-INV-1..M-INV-4 / U-INV-1..U-INV-4 / D-INV-1..D-INV-4 / CV-INV-1..CV-INV-4 / S-INV-1..S-INV-4) are lint-enforced by `scripts/check_claim_audit_consistency.py` because the conditional matrix relating judgment / audit_status / defect_stage / ref_retrieval_method exceeds what JSON Schema can express. Audit-side producer: `claim_ref_alignment_audit_agent` (`academic-pipeline/agents/`). Consumer: `formatter_agent` REFUSE rules 6-10 (see v3.8 spec §5 mode flag rationale). Default OFF for v3.8.0 — ramp-on plan deferred to post-calibration evidence.

Spec: [`docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md`](../docs/design/2026-05-15-issue-103-claim-alignment-audit-spec.md) + decision doc [`2026-05-15-issue-103-claim-alignment-audit-decision.md`](../docs/design/2026-05-15-issue-103-claim-alignment-audit-decision.md) (D1-D6 settled).

---

## Schema 10: Style Profile (intake -> draft_writer / report_compiler)

**Producer**: `academic-paper/agents/intake_agent` (Step 10)
**Consumer**: `academic-paper/agents/draft_writer_agent`, `deep-research/agents/report_compiler_agent`
**Carried by**: `academic-pipeline` Material Passport (optional field)

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `calibration_source` | list[string] | Filenames or titles of the analyzed writing samples |
| `sample_count` | integer | Number of samples analyzed (minimum 1, recommended 3+) |
| `sentence_length` | object | `{mean: float, stddev: float, rhythm_pattern: string}` |
| `paragraph_length` | object | `{mean_sentences: float, variation: string}` |
| `vocabulary_preferences` | object | `{hedging_words: list[string], transition_words: list[string], preferred_verbs: list[string], formality: string}` |
| `citation_style` | object | `{narrative_ratio: float, parenthetical_ratio: float, density: float, placement: string}` |
| `modifier_style` | enum | `"minimal"` / `"moderate"` / `"elaborate"` |
| `register_shifts` | list[object] | `[{section_name: string, assertiveness_level: string}]` |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `conflicts_with_discipline` | list[string] | Noted conflicts between personal style and discipline/journal norms |
| `partial_profile` | boolean | `true` if < 3 samples were analyzed (lower confidence) |
| `language_mismatch` | boolean | `true` if samples are in a different language than the target paper |

### Consumption Priority System

```
Priority 1 (HARD):   Discipline conventions — cannot be violated
Priority 2 (STRONG): Target journal conventions — if specified
Priority 3 (SOFT):   Author's personal style — only where it does not conflict with 1 or 2
```

See `shared/style_calibration_protocol.md` for full consumption rules and conflict resolution.

### Example

```markdown
## Style Profile

**Calibration Source**: ["Chen_2024_AI_assessment.pdf", "Chen_2023_formative_feedback.pdf", "Chen_2022_STEM_pedagogy.pdf"]
**Sample Count**: 3

**Sentence Length**: mean: 22, stddev: 8, rhythm: "variable — mixes 10-word punchy sentences with 35-word complex ones"
**Paragraph Length**: mean 5 sentences, variation: "moderate — 3-7 sentences, shorter in Methods"
**Vocabulary Preferences**:
  - Hedging: suggests, appears to, may
  - Transitions: However, In contrast, Yet
  - Reporting verbs: found, argued, noted
  - Formality: moderate-formal
**Citation Style**: narrative 40%, parenthetical 60%, density 2.3/paragraph, placement: mixed
**Modifier Style**: minimal
**Register Shifts**: [Methods: neutral, Results: descriptive, Discussion: assertive, Conclusion: personal]
**Conflicts**: "Author prefers passive voice (68% in samples), but Education discipline conventions favor active voice — using active voice per convention."
```

---

### Schema 11: R&R Traceability Matrix

> #539 optional per-row fields: `cross_model_verdict` (FULLY_ADDRESSED / PARTIALLY_ADDRESSED / NOT_ADDRESSED / MADE_WORSE; present only on `diverges`/`agree` rows) + `cross_model_status` (`agree` / `diverges` / `unavailable` / `not_configured`). Scope: the blind, separately executed pass evaluates `must_fix` rows only — current `must_fix` rows ALWAYS carry `cross_model_status` (`not_configured` when cross-model is not active); `should_fix`/`consider` rows omit both fields. A `must_fix` row with neither field is a legacy pre-#539 record. This describes execution and blinding, not binary independence.

> **Machine-readable sidecar (#576/#670):** current contract version 1.1 emits the machine-readable traceability sidecar defined by [`shared/contracts/re_review/traceability.schema.json`](contracts/re_review/traceability.schema.json). Each row carries `obligation_class`, per-item verdicts, and exact copies of the hash-bound author sidecar's `author_triage`, conditional `author_reason`, `authorized_targets`, and `claim_strength_authorizations`. The current input manifest hard-requires original and revised manuscripts, roadmap, author adjudication, and Revision-Evidence Bundle. `scripts/check_re_review_synthesis.py` fully replays the bundle, binds the matched pre draft to the original manuscript, and requires the ordered manifest patch/report arrays to equal the bundle write projection exactly; a mixed 1.0/1.1 chain fails. Under the contract, `verified` and `status` derive mechanically from `final_verdict` (`FULLY_ADDRESSED → YES`, `PARTIALLY_ADDRESSED → PARTIAL`, `NOT_ADDRESSED → NO`, `MADE_WORSE → NO`, `CANNOT_VERIFY → CANNOT_VERIFY`). Archived 1.0 replay lives under `shared/contracts/re_review/legacy/v1_0/` and `scripts/legacy/`.

**Producer (multi-stage, Kong A1 / v3.11)**:
- `concern_id` / `obligation_class` / `original_comment` / `reviewer_source`: academic-paper-reviewer (first-round review)
- `commitment_extracted`: revision_coach_agent (Step 3.5 Commitment Extraction Pass)
- `authors_claim` / `revision_location` / `fulfillment_status` / `unfulfilled_rationale` / `residual_action`: academic-paper revision execution (authored), then independently confirmed by re-review
- `verified` / `status` / `quality_assessment`: academic-paper-reviewer (re-review mode)

**Consumer**: academic-paper (revision mode, if further revision needed), pipeline orchestrator. Schema 11 is carried forward via Material Passport (Schema 9) for cross-stage audit.

**Purpose**: Maps every reviewer concern through the full revision cycle — what was raised, what the author claims to have done, where the change is, and whether it was independently verified.

**Required fields**:
- `concern_id`: Unique ID (R1, R2, S1, S2, N1...)
- `obligation_class`: `MUST_FIX` / `SHOULD_FIX` / `CONSIDER` (editorial gate, not work rank)
- `author_triage`: `will_address` / `wont_address` / `not_on_point`, copied exactly from the hash-bound author sidecar
- `authorized_targets`: exact author-approved block/operation scopes, copied unchanged
- `claim_strength_authorizations`: exact registered-claim authorizations, copied unchanged
- `original_comment`: The reviewer's original concern text
- `authors_claim`: What the author states they did (from Response to Reviewers)
- `revision_location`: Section/page/paragraph reference in revised manuscript
- `verified`: `YES` (✅) / `PARTIAL` (⚠️) / `NO` (❌) / `CANNOT_VERIFY` (🔍)
- `status`: `FULLY_ADDRESSED` / `PARTIALLY_ADDRESSED` / `NOT_ADDRESSED` / `MADE_WORSE` / `CANNOT_VERIFY` (#576 — mirrors the contract verdict vocabulary; the `verified` field already carried it)
- `quality_assessment`: Free-text evaluation

**Optional fields**:
- `author_reason`: required exactly when `author_triage` is `wont_address` or `not_on_point`; absent for `will_address`
- `reviewer_source`: Which reviewer originally raised the concern (EIC, R1, R2, R3, DA)
- `residual_action`: What remains to be done if not fully addressed. This is a single concern-level string (one per Schema 11 row), distinct from the per-commitment `unfulfilled_rationale` field nested inside each `commitment_extracted` object below. Two coherence conventions govern how the two interact:
  - **(a) Semantic relationship on a partial / multi-commitment row.** A commitment's `unfulfilled_rationale` is diagnostic and per-commitment — it explains *why that commitment fell short* (backward-looking, carried on the commitment object itself). `residual_action` is forward-looking and concern-level — it states *what still remains to be done for the whole concern*. They are different granularity and different tense, so a row may legitimately carry both at once; this is neither redundancy nor contradiction. Example: a commitment object with `unfulfilled_rationale: "3-seed std error only; 5-seed deferred per §6"` (why) alongside the row-level `residual_action: "Run 5-seed replication in camera-ready"` (what remains).
  - **(b) Multi-commitment shape convention.** When one concern decomposes into N commitments, `residual_action` stays a single concern-level string (an aggregate of what remains across the concern); it is **not** expanded into a list or split per commitment. The per-commitment "why" lives on each commitment object's `unfulfilled_rationale`; the concern-level "what remains" stays on the row's `residual_action`.
- `commitment_extracted`: (Kong A1 / v3.11; nested-object shape since #268) List of objects extracted from `original_comment` by `revision_coach_agent` Step 3.5. Each object carries three **extraction** fields plus two optional **lifecycle** fields. The extraction fields are written at Step 3.5: `commitment_text` (string, verbatim or minimally normalized promise), `commitment_type` ∈ `{add_experiment, add_analysis, add_clarification, add_citation, restructure, other}`, and `required_evidence_type` ∈ `{new_section, new_figure, new_table, new_citation, methods_paragraph, discussion_paragraph, prose_edit, acknowledgment_only, other}`. Of these nine, seven are **manuscript-evidence** types verified at `revision_location` in the revised manuscript (`new_section`, `new_figure`, `new_table`, `new_citation`, `methods_paragraph`, `discussion_paragraph`, `prose_edit`); `acknowledgment_only` is the one **response-letter-evidence** type verified in the Response to Reviewers (Schema 8); `other` is an underspecified escape hatch that triggers a soft advisory at re-review (see `re_review_mode_protocol` Commitment Ledger Verification). `prose_edit` covers sentence- or paragraph-level prose changes too granular to bucket into the section/figure/table/etc. categories (typo fixes, terminology clarifications, equation formatting, citation-style corrections). The lifecycle fields (`fulfillment_status`, `unfulfilled_rationale`, defined next) are **absent at extraction time** and appended per-object during revision execution. Empty list `[]` is valid (comment carried no extractable commitment, e.g., positive feedback).
  - `commitment_extracted[].fulfillment_status`: (Kong A1 / v3.11; per-object since #268) Optional lifecycle field nested **inside each `commitment_extracted` object** (not a top-level Schema 11 field), ∈ `{fulfilled, partial, not-fulfilled, explicitly-rejected-with-rationale}`. Absent on a commitment object until revision execution fills it. Nesting it inside the object (rather than carrying a separate parallel list) makes index desynchronization between commitment and status structurally impossible (the failure mode #268 closes).
  - `commitment_extracted[].unfulfilled_rationale`: (Kong A1 / v3.11; per-object since #268) Optional lifecycle field nested **inside each `commitment_extracted` object** (not a top-level Schema 11 field): a free-text rationale required iff that object's `fulfillment_status` ∈ `{partial, not-fulfilled, explicitly-rejected-with-rationale}`. **Omitted** (not the empty string) when `fulfillment_status == fulfilled` or absent — the old `""` placeholder existed only to keep the parallel lists aligned and is dead weight in the nested shape. Three valid rationale forms: (a) "done elsewhere, see §X" pointer, (b) "rejected, reasons: …" rationale, (c) "deferred to future work" acknowledgment.

**Validation**:
- Every item from the original Revision Roadmap (Schema 7) must appear in the matrix
- `authors_claim` cannot be empty for `must_fix` items. The flag-as-`CANNOT_VERIFY` consequence of a missing claim is legacy-mode-scoped (#576): in current contract mode the requirement itself still stands — satisfied by the §11 letter-absent `"—"` fill — but `verified` derives from the sidecar's `final_verdict`, and letter absence travels via visible §11 markers rather than a rewritten verdict
- Every author-owned field must be an exact copy of the hash-bound `author-adjudication/1.0` sidecar. Declined choices carry a non-empty reason and no target/claim authority. A presentation-only display permutation never changes row or `R<n>` source order
- Matrix is carried forward in Material Passport (Schema 9) for audit trail
- Each object in `commitment_extracted` MUST carry the three extraction fields (`commitment_text`, `commitment_type`, `required_evidence_type`). The two lifecycle fields are nested per-object: `fulfillment_status` is optional (absent before revision execution); `unfulfilled_rationale` MUST be present and non-empty iff that object's `fulfillment_status` ∈ `{partial, not-fulfilled, explicitly-rejected-with-rationale}`, and MUST be absent when `fulfillment_status == fulfilled` or absent. There is no separate top-level `fulfillment_status` / `unfulfilled_rationale` list — the equal-length invariant the parallel-list shape needed is retired because length mismatch is now structurally impossible (#268). Empty list `commitment_extracted: []` stays valid (comment carried no extractable commitment). Violations (a non-`fulfilled` commitment object missing its `unfulfilled_rationale`) surface as `COMMITMENT_GAP` advisory at re-review (advisory only — author retains final responsibility).
- **Legacy normalization (pre-#268 artifacts).** If an artifact still carries the old top-level parallel arrays (`fulfillment_status` / `unfulfilled_rationale` as separate lists alongside `commitment_extracted`), normalize them into the nested objects before re-review. **First verify all three were the same length** — a pre-#268 artifact may already be desynchronized (the exact failure mode #268 closes), so do NOT auto-zip a length-mismatched ledger; flag it for manual reconciliation against the source comments instead. Only for an equal-length legacy row: copy the i-th `fulfillment_status` onto the i-th commitment object, and copy the i-th `unfulfilled_rationale` only when non-empty (an empty `""` or missing entry on a non-`fulfilled` status normalizes to an *absent* nested `unfulfilled_rationale` — i.e. the nested COMMITMENT_GAP case, not a literal empty string). Re-review agents then verify ONLY the nested per-object shape; they do not walk parallel top-level arrays.

---

## Schema 12 — Compliance Report (v3.4.0+)

**Source of truth:** [`shared/compliance_report.schema.json`](compliance_report.schema.json)

Mode-aware output of [`compliance_agent`](agents/compliance_agent.md). Three top-level subtrees: `prisma_trAIce` (null for primary research), `raise` (always present), and decision aggregation fields.

- **Emitted by:** `compliance_agent` at Stage 2.5 / 4.5 (pipeline) or pre-finalize (standalone skills)
- **Consumed by:** orchestrator (for checkpoint dashboard), `report_compiler_agent` (for AI Self-Reflection Report compliance summary at Stage 6)
- **Appended to:** `material_passport.compliance_history[]` (append-only)

### Key fields

- `mode`: dispatches payload (see [`shared/agents/compliance_agent.md`](agents/compliance_agent.md) §Dispatch logic)
- `stage`: `"2.5"` or `"4.5"`
- `prisma_trAIce`: `null` when `mode != "systematic_review"`; otherwise tier-bucketed item results
- `prisma_trAIce.protocol_maturity` *(optional, added per issue #95)*: snapshot of the upstream protocol's self-described maturity status (`foundational_proposal` / `delphi_consensus` / `empirically_validated`) plus citation, snapshot date, and a one-paragraph caveat summary. Populated by `compliance_agent` from [`shared/prisma_trAIce_protocol.md`](prisma_trAIce_protocol.md) — its frontmatter (`citation`, `snapshot_date`) is the deterministic source for `upstream_citation` and `snapshot_date`; `status` is derived from the protocol authors' self-description (currently `foundational_proposal` per Holst et al. 2025, until upstream graduates the checklist via formal consensus); `caveat_summary` is composed from the protocol's framing. (Issue #93 / PR #94 add a `§ Status disclaimer` section to the protocol file as the canonical prose source for `caveat_summary`; until that PR lands, agents derive the summary from the Holst 2025 framing.) Omittable for byte-equivalent compatibility with pre-#95 entries (zero-touch).
- `raise.mode`: `"full"` (SR + other_evidence_synthesis) or `"principles_only"` (primary_research)
- `raise.principles`: 4 keys, each with `pass` / `warn` / `fail`
- `raise.roles`: 8 keys, populated only when `raise.mode == "full"`
- `overall_decision`: aggregate across compliance + legacy integrity + v3.2 failure mode
- `user_override`: only present after a user overrides a block; rationale required
- `upstream_sync_status`: `"current"` or `"stale"` (from freshness check)

Full field spec: [`shared/compliance_report.schema.json`](compliance_report.schema.json).

### Material Passport extension

Schema 9 Material Passport gains one optional field, `compliance_history`:

```yaml
compliance_history:
  - <compliance_report entry>
  - <compliance_report entry>
  # append-only; never overwrite, never reorder
```

Ordering: chronological by `generated_at`. A Stage 2.5 FAIL followed by backfill + retry-pass produces two adjacent entries for Stage 2.5 — both preserved.

---

## Validation Rules

1. **Required field check**: All schema fields marked without "(optional)" or "No" in the Required column are REQUIRED. Consumer agents MUST verify all required fields are present before proceeding
2. **Type check**: Fields must match declared types (e.g., `enum` values must be from the allowed set)
3. **Cross-reference check**: Source IDs referenced in Synthesis must exist in Bibliography; RevisionItem IDs in Response to Reviewers must match the Revision Roadmap
4. **Version tracking**: Each handoff artifact MUST carry a Material Passport (Schema 9) with a version label. Version labels must be monotonically increasing within a pipeline run
5. **Failure on missing**: If a required field is missing, return `HANDOFF_INCOMPLETE` with a list of missing fields; do NOT proceed with partial data
6. **Producer validation**: Producing agent must validate output against its schema BEFORE handoff
7. **Consumer validation**: Consuming agent should validate input on receipt and request re-generation if schema violations are found. For a current #672 chain this includes exact byte replay of the one `preregistration-artifact/1.0` sidecar and its explicitly named companion when provided. Absence, substitution, a repaired digest, or a changed companion is `HANDOFF_INCOMPLETE`/contract failure, never an inferred unavailable receipt.
8. **Integrity gating**: Artifacts that have passed through integrity verification (Schema 5) must have their Material Passport updated with `verification_status: "VERIFIED"` and `integrity_pass_date`
9. **Staleness detection**: If an upstream artifact is modified after a downstream artifact was produced, the downstream artifact's Material Passport should be updated to `verification_status: "STALE"`
10. **Passport freshness**: A Material Passport's integrity results are considered STALE if `integrity_pass_date` is more than 24 hours old relative to the current timestamp. Stale passports require re-verification before proceeding
11. **Stage-skip eligibility via passport**: A passport allows skipping Stage 2.5 (pre-review integrity) ONLY when ALL of the following conditions are met: (a) `verification_status` = `"VERIFIED"`, (b) `integrity_pass_date` is within the current session or less than 24 hours old, (c) `version_label` matches the current artifact version (content has not been modified since verification), and (d) the user explicitly confirms the skip. If any condition fails, full Stage 2.5 re-verification is required
12. **Passport does not grant Stage 4.5 skip**: The final integrity check (Stage 4.5) can NEVER be skipped via Material Passport, regardless of passport status. Stage 4.5 always requires full Mode 2 verification

## `data_access_level` (v3.3.2+)

Every top-level `SKILL.md` declares `metadata.data_access_level` with one of three values:

- `raw` — consumes unverified sources; must assume adversarial/hallucinated input
- `redacted` — operates on sanitized material; no new raw ingestion
- `verified_only` — runs only after upstream integrity gates

This is a declarative signal (not a runtime permission system). Enforced by `scripts/check_data_access_level.py` in CI, which since #756 also pins each skill's declared value — a new skill must be registered there with the value matching the *dirtiest* input it may legitimately consume.

## `task_type` (v3.3.2+)

Every top-level `SKILL.md` declares `metadata.task_type` with one of two values:

- `outcome-gradable` — the task has an objective scalar metric the skill optimizes against; a third party can score the output without deep context
- `open-ended` — the task's quality depends on domain judgment, interpretive work, or context no metric captures

This is a declarative truth-in-advertising signal. All current ARS skills are `open-ended` because ARS targets humanities/QA/policy work, not benchmark tasks. When adding a new skill, do not invent a third value; if the skill genuinely spans both, split it into two skills.

Enforced by `scripts/check_task_type.py` in CI.

See [`ground_truth_isolation_pattern.md`](ground_truth_isolation_pattern.md) for the rationale and rules behind this annotation.


## v3.3.5 additions

- `benchmark_report.schema.json` + [`benchmark_report_pattern.md`](benchmark_report_pattern.md) — schema for publishing ARS benchmark comparisons with required human baseline + independence fields.
- `repro_lock` sub-block on Material Passport + [`artifact_reproducibility_pattern.md`](artifact_reproducibility_pattern.md) — configuration lockfile (NOT replay guarantee).
