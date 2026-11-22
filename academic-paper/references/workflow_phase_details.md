# Orchestration Workflow — Phase Details

Detailed per-phase agent behavior and output descriptions for the 8-phase orchestration workflow.

---

## Phase 0: CONFIG (Interactive)

**Agent**: `intake_agent`
**Output**: Paper Configuration Record

- Paper type (IMRaD / Lit Review / Theoretical / Case Study / Policy Brief / Conference)
- Discipline and sub-field
- Target journal (optional)
- Citation format (APA 7 / Chicago / MLA / IEEE / Vancouver)
- Output format (LaTeX / DOCX / PDF / Markdown / Combined)
- Language (EN / zh-TW / bilingual sections)
- Bilingual abstract (Yes / EN-only / zh-TW-only) — cardinality only; it does not select which languages
- Output language pair (`output_language_pair`) — the two abstract languages, from the registry in `shared/output_language_pair.md`; default `zh-tw-en`, per-run override; the PCR row is omitted when the run declares none
- Word count target
- Existing materials (RQ, data, drafts, lit)

**Checkpoint**: User confirms configuration.

---

## Phase 1: RESEARCH

**Agent**: `literature_strategist_agent`
**Output**: Search Strategy + Source Corpus

- Database selection + search strings
- Inclusion/exclusion criteria
- Source screening + annotated bibliography
- Literature matrix (Source x Theme)
- Research gap mapping

**Checkpoint**: User reviews sources (optional add/remove).

---

## Phase 2: ARCHITECTURE

**Agent**: `structure_architect_agent`
**Output**: Paper Outline + Evidence Map

- Structure pattern selection (from paper_structure_patterns.md)
- Section-by-section outline with word count allocation
- Evidence-to-section assignment
- Transition logic between sections

**Checkpoint**: User approves outline.

---

## Phase 3: ARGUMENTATION

**Agent**: `argument_builder_agent`
**Output**: Argument Blueprint

- Central thesis + sub-arguments
- Claim-Evidence-Reasoning chains per section
- Counter-argument identification + rebuttal strategy
- Logical flow diagram

---

## Phase 4: DRAFTING

**Agent**: `draft_writer_agent`
**Output**: Complete Draft

- Section-by-section writing following outline
- Register adjustment for discipline
- In-text citations integrated
- Word count tracking per section
- Transition paragraphs between sections
- Acronym check on the saved draft (#849; [`writing_quality_check.md`](writing_quality_check.md) § F)

---

## Phase 5a & 5b: CITATIONS + ABSTRACT (Parallel)

### Phase 5a: Citations

**Agent**: `citation_compliance_agent`
**Output**: Citation Audit Report + Corrected Draft (`full` mode only; the first Phase 6 review reads it and the first revision round edits it)

- In-text <-> reference list cross-check (zero orphans)
- Format compliance (per selected style)
- DOI/URL verification
- Self-citation ratio check
- Auto-correction of detected errors

### Phase 5b: Abstract

**Agent**: `abstract_bilingual_agent`
**Output**: Bilingual Abstract + Keywords (both languages of the run's declared output language pair)

- L2 abstract (default: English), structured — length from the regime table ([`abstract_writing_guide.md`](abstract_writing_guide.md), run's paper type)
- L1 abstract (default: Traditional Chinese), structured — length from the same regime table
- L2 keywords, count from the same regime table
- L1 keywords, same declared count
- Headings and report columns are pair-derived; for the default pair `zh-tw-en` they render exactly as `### English Abstract` / `### Chinese Abstract`
- Independent writing (not mechanical translation)
- Field absent → default pair; the heading literals are unchanged from the pre-#862 surface (no rendered-output equivalence is claimed)
- Acronym check on the saved abstracts (#849; [`writing_quality_check.md`](writing_quality_check.md) § F)

---

## Phase 6: PEER REVIEW

**Agent**: `peer_reviewer_agent`
**Output**: Review Report + Revision Instructions

- 5-dimension criterion-bound judgement:
  Originality | Methodological Rigor | Evidence Sufficiency |
  Argument Coherence | Writing Quality
- Every live Phase 6 report and downstream review package emits
  `calibration_status: NOT_CALIBRATED` unconditionally in the current release.
  Candidate empirical target profiles declare
  `application_status: NOT_WIRED_TO_LIVE_REVIEW`; attaching one or observing an
  apparent metadata match cannot upgrade the live status. No weighted total or
  fixed verdict mapping is available.
- Verdict: Accept / Minor Revision / Major Revision / Reject
- Line-level feedback with suggested fixes
- Max 2 revision loops -> back to Phase 4 [draft_writer_agent] (limited to 1 round in academic-pipeline)
- In `full` mode, call `citation_compliance_agent` for a re-check before Phase 7 if any Phase 6 revision round or the Option A edit (the "Acknowledged Limitations" section) added, removed, or changed a citation or a reference-list entry. Count the changes of every round, not only the last one. Send the writer's latest draft to the re-check. When the reviewer accepted a draft, keep that draft with its `## References` section for comparison.
- In `full` mode, when a re-check runs, use its Corrected Draft as the sole Phase 7 manuscript and use its accompanying reference list. Keep the Phase 5a Citation Audit Report, and its correction log when Phase 5a produced one, alongside the re-check's report. The re-check verifies sources as usual and records conflicts in Items Flagged for Review. Use the Phase 5a list only when no re-check ran. With no revision round (a Round 1 Accept, or early formatting after Phase 5a and before any revision round), no re-check runs; send the initial Phase 5a Corrected Draft (#1071).
- In `full` mode, Phase 7 skips Review Status confirmation and uses the reviewer's Final Counts only when the Phase 7 draft and its reference list both match the accepted version (the accepted draft with its `## References` section). The caller makes this comparison and passes the Final Counts to the formatter only on a match. If the re-check changed a citation in the draft or an entry in the list after acceptance, the formatter shows `Citations changed after Round N acceptance; this version has not been re-reviewed`, asks once, and counts the draft it receives (#1071).

---

## Phase 7: FORMAT

**Agent**: `formatter_agent`
**Output**: Final Output Package

- In `full` mode, once Review Status allows formatting, compare the incoming draft and list before conversion. Count only works that require an entry under the selected citation style, and count an entry as uncited only where that style requires a list entry to be cited. List missing, uncited, or duplicate entries in an Output Package warning and continue formatting with citation content preserved (#1071).
- Target format conversion (LaTeX + .bib / DOCX / PDF / Markdown)
- Journal-specific formatting (if target journal specified)
- Cover letter (if journal submission)
- AI disclosure statement
- Final quality checklist
