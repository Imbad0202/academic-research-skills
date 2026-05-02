# Handoff Schemas — Cross-Skill Data Contracts

## Purpose

Defines the exact data structure for every artifact passed between pipeline stages.
All agents that produce or consume these artifacts MUST conform to these schemas.
Consuming agents should validate input and request re-generation if schema violations are found.

> **Convention**: All schemas use Markdown-based structured output. Agents MUST validate required fields before accepting a handoff. Missing required fields trigger a `HANDOFF_INCOMPLETE` failure path.

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
| `search_strategy` | object | `{databases: list[string], keywords: list[string], inclusion_criteria: list[string], exclusion_criteria: list[string], date_range: string}` |
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
| `retraction_check` | boolean | No | Whether checked against Retraction Watch |
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

**Minimum Sources**: 15

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
| `score_trajectory` | object / null | Review score delta tracking (v3.3, optional). Present only during re-review. See Score Trajectory Structure below. |
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
    distortions: [{claim: string, source: string, verdict: string, detail: string}]
  }
}
```

### Score Trajectory Structure (v3.3, optional)

Present only when the integrity report is for a re-review (Stage 3' or 4'). Tracks rubric score changes across revision rounds.

Dimensions match the 7 universal review dimensions from `academic-paper-reviewer/references/review_criteria_framework.md` plus an overall score:

```
score_trajectory: {
  round: integer,          // revision round number (1 or 2)
  previous_scores: {       // rubric scores from prior review (1-5 scale)
    originality: float,
    methodological_rigor: float,
    evidence_sufficiency: float,
    argument_coherence: float,
    writing_quality: float,
    literature_integration: float,
    significance_impact: float,
    overall: float
  },
  current_scores: {        // rubric scores from this review (1-5 scale)
    originality: float,
    methodological_rigor: float,
    evidence_sufficiency: float,
    argument_coherence: float,
    writing_quality: float,
    literature_integration: float,
    significance_impact: float,
    overall: float
  },
  deltas: {                // current - previous for each dimension
    originality: float,
    methodological_rigor: float,
    evidence_sufficiency: float,
    argument_coherence: float,
    writing_quality: float,
    literature_integration: float,
    significance_impact: float,
    overall: float
  },
  regression_detected: boolean,  // true if any delta < -3
  regressed_dimensions: list[string],  // names of dimensions where delta < -3
  early_stop_eligible: boolean   // true if overall delta < 3 AND no P0 issues (existing criterion)
}
```

**Consumer**: `pipeline_orchestrator_agent` uses `regression_detected` to trigger a warning checkpoint. `editorial_synthesizer_agent` includes trajectory in re-review reports.

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
| `revision_roadmap` | list[RoadmapItem] | Prioritized list of required changes |
| `confidence_score` | integer | 0-100 editorial confidence |

### ReviewerReport Object

| Field | Type | Description |
|-------|------|-------------|
| `reviewer_id` | string | Reviewer identifier (e.g., `EIC`, `R1`, `R2`, `R3`, `DA`) |
| `role` | string | Reviewer role description |
| `dimension_scores` | object | Per-dimension scores (skill-specific) |
| `strengths` | list[string] | Paper strengths identified |
| `weaknesses` | list[Weakness] | Paper weaknesses identified |
| `questions` | list[string] | Questions for the authors |

### Weakness Object

| Field | Type | Description |
|-------|------|-------------|
| `description` | string | What the weakness is |
| `severity` | enum | `critical` / `major` / `minor` |
| `type` | enum | `methodology` / `theory` / `evidence` / `writing` / `structure` / `ethics` |

---

## Schema 7: Revision Roadmap (reviewer -> academic-paper revision)

**Producer**: `academic-paper-reviewer/editorial_synthesizer_agent`
**Consumer**: `academic-paper/draft_writer_agent` | `academic-pipeline/pipeline_orchestrator_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `items` | list[RoadmapItem] | Ordered list of revision items |
| `total_items` | integer | Total number of items |
| `must_fix_count` | integer | Number of `must_fix` priority items |
| `editorial_decision` | enum | `"Accept"` / `"Minor Revision"` / `"Major Revision"` / `"Reject"` |
| `consensus_summary` | string | Summary of reviewer consensus |
| `dissenting_opinions` | list[string] | Notable disagreements among reviewers |

### RoadmapItem Object

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique revision ID (e.g., `REV-001`) |
| `description` | string | What needs to change |
| `reviewer` | string | Which reviewer(s) raised this (e.g., `R1, R3`) |
| `type` | enum | `"Major"` / `"Minor"` / `"Editorial"` |
| `priority` | enum | `"must_fix"` / `"should_fix"` / `"consider"` |
| `target_section` | string | Section of the paper to modify |
| `suggested_action` | string | How to address the item |
| `consensus_level` | enum | `"CONSENSUS-4"` / `"CONSENSUS-3"` / `"SPLIT"` / `"DA-CRITICAL"` |
| `verification_criteria` | string | How to confirm the fix is adequate |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `deadline_suggestion` | string | Suggested timeline for completion |

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
| `literature_corpus` | list[object] | Optional append-friendly literature corpus. Each entry conforms to [`shared/contracts/passport/literature_corpus_entry.schema.json`](contracts/passport/literature_corpus_entry.schema.json). Produced by user-written adapters (see [`academic-pipeline/references/adapters/overview.md`](../academic-pipeline/references/adapters/overview.md)); ARS does not produce these entries itself. Added v3.6.4+. |
| `audit_artifact` | list[object] | Optional append-only ledger of cross-model audit runs for v3.6.7 downstream-agent deliverables. Each entry conforms to [`shared/contracts/passport/audit_artifact_entry.schema.json`](contracts/passport/audit_artifact_entry.schema.json). Produced by the pipeline orchestrator after Layer 2 + Layer 3 verification of wrapper-emitted proposal entries; only `persisted` entries are stored here. Added v3.6.7+. |

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

**Producer**: academic-paper-reviewer (re-review mode)
**Consumer**: academic-paper (revision mode, if further revision needed), pipeline orchestrator

**Purpose**: Maps every reviewer concern through the full revision cycle — what was raised, what the author claims to have done, where the change is, and whether it was independently verified.

**Required fields**:
- `concern_id`: Unique ID (R1, R2, S1, S2, N1...)
- `priority`: `MUST_FIX` / `SHOULD_FIX` / `CONSIDER`
- `original_comment`: The reviewer's original concern text
- `authors_claim`: What the author states they did (from Response to Reviewers)
- `revision_location`: Section/page/paragraph reference in revised manuscript
- `verified`: `YES` (✅) / `PARTIAL` (⚠️) / `NO` (❌) / `CANNOT_VERIFY` (🔍)
- `status`: `FULLY_ADDRESSED` / `PARTIALLY_ADDRESSED` / `NOT_ADDRESSED` / `MADE_WORSE`
- `quality_assessment`: Free-text evaluation

**Optional fields**:
- `reviewer_source`: Which reviewer originally raised the concern (EIC, R1, R2, R3, DA)
- `residual_action`: What remains to be done if not fully addressed

**Validation**:
- Every item from the original Revision Roadmap (Schema 7) must appear in the matrix
- `authors_claim` cannot be empty for Priority 1 items (flag as `CANNOT_VERIFY` if missing)
- Matrix is carried forward in Material Passport (Schema 9) for audit trail

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
7. **Consumer validation**: Consuming agent should validate input on receipt and request re-generation if schema violations are found
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

This is a declarative signal (not a runtime permission system). Enforced by `scripts/check_data_access_level.py` in CI. When adding a new skill, pick the value matching the *dirtiest* input the skill may legitimately consume.

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
