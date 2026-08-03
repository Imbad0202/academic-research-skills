# Curated academic-pipeline run log

This is a chronological, human-readable projection of persisted pipeline state and generated artifacts. It is not a verbatim replacement for the excluded RPC streams. Stage status, hashes, timestamps, and checkpoint facts come from [`state/pipeline-state.json`](state/pipeline-state.json) and linked run artifacts. “Scholar” language inside generated artifacts refers to the synthetic test operator, not the Pi port maintainer's identity or biography.

## Invocation and capability boundary

The run used the original scenario prompt through `/ars-full`:

```text
I want to write a paper on the impact of declining birthrate on enrollment
strategies of private universities in Taiwan. Help me from start to finish.
This is my first time writing an academic paper and I'm not sure about the process.
```

Pi was started with discovered extensions, skills, prompt templates, and context files disabled. Only the wrapper, four original ARS skills, original ARS commands, and `/skill:websearch` were explicitly loaded. [`runtime/ars-pi-doctor.txt`](runtime/ars-pi-doctor.txt) recorded:

```text
Orchestration: none; sequential/degraded mode
Web retrieval: skill: /skill:websearch
Claude hooks: unavailable in Pi; write-scope enforcement remains prompt-level
```

The external RPC/workflow driver delivered synthetic test-operator checkpoint responses and recovered transport. It was not exposed inside Pi as a tool, skill, reviewer, or orchestration capability.

## Chronology

| Order | Stage | Persisted result | Checkpoint/operator action | Representative evidence |
| ---: | --- | --- | --- | --- |
| 1 | Research | Completed. RQ brief, methodology, bounded search, source verification, synthesis, reviewed and revised research report. | Test operator prohibited invented interviews, participants, original-data analysis, statistical results, and strategy-effect rankings; required paired registration-rate and actual-freshman outcomes. Stage checkpoint confirmed. | [`stage-01/revised-research-report.md`](stage-01/revised-research-report.md) |
| 2 | Write | Completed in plan-to-full mode. Fresh course-paper draft, bilingual abstracts, and citation check emitted. | Test operator required a fresh paper rather than relabeling Stage 1 and corrected the target from “6,000 words” to approximately 6,000 Chinese characters. Outline, argument, and draft checkpoints confirmed. | [`stage-02/course-paper-draft.md`](stage-02/course-paper-draft.md) |
| 3 | Integrity 2.5 | Round 1 **FAIL**, bounded correction, Round 2 **PASS**. | Test operator accepted the O7 locator mismatch and authorized only the verified URL and stale process-status corrections. Compliance WARN acknowledged without converting it to PASS. | [`stage-02.5/focused-reverification-report.md`](stage-02.5/focused-reverification-report.md) |
| 4 | Review | Five role reports executed sequentially in one context. Editorial decision: **Major Revision**. | Reviewer configuration and decision confirmed. Test operator completed revision coaching and reframed contribution around measurement core, scope stratification, and prototype demotion. | [`stage-03/editorial-decision-and-revision-roadmap.md`](stage-03/editorial-decision-and-revision-roadmap.md) |
| 5 | Revise | Three deterministic patch rounds; apply chain passed; 10/10 response coverage. | Test operator prohibited new search, required patch-only revision, and confirmed the inspection checkpoint. | [`stage-04/response-to-reviewers.md`](stage-04/response-to-reviewers.md) |
| 6 | Re-review 3′ | Hash-bound contract and checker passed; decision remained **Major Revision**. Transport recovery resumed the same academic run. | Mandatory decision accepted. Residual coaching skipped; no new search authorized. | [`stage-03p/verification-review-report.md`](stage-03p/verification-review-report.md) |
| 7 | Re-revise 4′ | One authorized block changed; 115/116 blocks preserved byte-identically; validation passed. | Test operator inspected focused diff and accepted the token-conservation advisory while preserving the declared limitation. FULL checkpoint confirmed. | [`stage-04p/validation-report.md`](stage-04p/validation-report.md) |
| 8 | Final integrity 4.5 | **PASS**. 21/21 references, 58/58 citation contexts, 41/41 claim clusters, data reproduction, originality sampling, and failure-mode checks completed. | Test operator inspected report/checklist, accepted 12 advisories and nonblocking compliance WARN, then authorized Stage 5. | [`stage-04.5/final-integrity-verification-report.md`](stage-04.5/final-integrity-verification-report.md) |
| 9 | Finalize | Initial cite-time gate **REFUSE** because 79 markers lacked human-read attestation. After the required human attestation, 79/79 resolved to `OK`; Markdown and DOCX emitted. | Exact attestation wording and internal identifiers are omitted. Test operator selected APA 7, declined paper LaTeX/PDF, retained placeholders and warnings, and confirmed FULL checkpoint. | [`stage-05/cite-time-gate-refusal-report.md`](stage-05/cite-time-gate-refusal-report.md), [`stage-05/cite-time-gate-pass.json`](stage-05/cite-time-gate-pass.json), [`stage-05/package/paper.md`](stage-05/package/paper.md) |
| 10 | Process summary | Bilingual records and PDFs were validated during the run. Pipeline and Stage 6 persisted `completed`. | Terminal checkpoint was presented as nonterminal until acknowledgement arrived. Successful retry and acknowledgement persisted; 36/36 advisory round trips used. | [`stage-06/process-record-en.md`](stage-06/process-record-en.md), [`stage-06/terminal-checkpoint.md`](stage-06/terminal-checkpoint.md), [`state/pipeline-state.json`](state/pipeline-state.json) |

## Actual degraded-mode disclosure

Degradation was not inferred only from `/ars-pi-doctor`. Generated runtime artifacts repeatedly disclosed it. For example, the Stage 3 editorial record states that the five roles ran sequentially in one Pi session, without independent context windows or genuine cognitive paper blindness. Stage 3′, Stage 4′, Stage 4.5, and Stage 6 repeat the same boundary.

This establishes that fallback behavior actually fired. It does not establish equivalence to independent Claude agents.

## Checkpoint and terminal audit

Persisted state records:

- mandatory/full checkpoints automatically skipped: 0;
- Stage 2.5 integrity history: FAIL then PASS;
- Stage 3 decision: Major Revision;
- Stage 3′ decision: Major Revision;
- Stage 4.5 final integrity: PASS and scholar-confirmed;
- Stage 5 cite-time provenance: REFUSE then PASS after explicit attestation;
- Stage 6: completed;
- terminal checkpoint: confirmed;
- terminal acknowledgement: received;
- pipeline state: completed.

The first terminal-response transport attempt was not consumed during compaction. Internal transport/request identifiers are omitted from this public bundle; the persisted terminal state controls the completion claim.

## Completeness and exclusions

Representative output from every executed stage is committed, along with final Markdown, process record, terminal state, inventory, and hashes. Provider streams, session JSONL, internal identifiers, exact personal attestation text, downloaded source bodies, redundant binaries/translations, and intermediate caches are excluded. Their omission is disclosed in [`inventory.json`](inventory.json); no excluded file is required to establish the persisted stage sequence or final terminal state.
