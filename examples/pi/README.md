# Pi degraded-mode end-to-end evidence

This directory is a privacy-minimized evidence bundle from one completed `/ars-full` run through the thin Pi wrapper. It demonstrates checkpoint enforcement, source-read provenance gating, Stage 5 finalization, Stage 6 process recording, and persisted terminal completion when no Pi orchestration capability was installed.

This is evidence from one synthetic test scenario, not a general conformance certificate or a claim that degraded execution is equivalent to independent multi-agent review.

## Run identity

| Field | Value |
| --- | --- |
| Run ID | `ars-pi-e2e-gpt-5.6-sol-20260803T051847Z` |
| Pi | `0.83.0` |
| Provider/model | `openai-codex/gpt-5.6-sol` |
| ARS pipeline | `3.19.0` |
| Repository HEAD used for curation | `682b158ea02b6bdcc1f70b1ba577f237645bf7f5` |
| Execution | sequential, same recovered Pi/model context |
| Terminal state | Stage 6 `completed`, checkpoint confirmed, acknowledgement received, 36/36 round trips |

The run crossed a disclosed transport recovery and automatic context compaction. Continuity was established from persisted artifacts, state, and hashes; it was not represented as a new academic run.

After the run, the wrapper's system-prompt injection was scoped to ARS-active sessions and inactive prompts were hardened to hide this package's ARS skill entries. That guarantee and its probes cover prompts submitted while Pi is idle. Pi 0.83.0 does not rebuild the system prompt for prompts queued into an in-flight run, and its direct RPC `steer` and `follow_up` methods bypass the wrapper's `input` handler; those residuals are documented rather than represented as covered. The compatibility text used after `/ars-full` is unchanged; the final wrapper received fresh idle-path activation, automatic-invocation, and package-load regression tests, but these small post-run changes did not receive another full pipeline execution. See [`model-portability.md`](model-portability.md).

## Load-bearing Pi boundaries

1. **No wrapper-provided agent isolation.** [`runtime/ars-pi-doctor.txt`](runtime/ars-pi-doctor.txt) reported `Orchestration: none; sequential/degraded mode`. Specialist roles therefore ran sequentially in one recovered Pi/model context. No independent reviewer, writer, verifier, observer, formatter, or cross-model judgment is claimed. The external RPC driver delivered synthetic test-operator checkpoint responses only; it was not available to the inner Pi session as an orchestration tool or skill.
2. **No Claude hook enforcement.** The same doctor record reported that Claude hooks are unavailable in Pi. ARS write-scope enforcement was prompt-level in this run; no deterministic Claude `PreToolUse` hook boundary is claimed.

The installed `/skill:websearch` capability was visible to Pi. Source verification remained bounded as disclosed in the provenance and process records. [`runtime/package-load-validation.json`](runtime/package-load-validation.json) records fresh offline root/nested package loads that found all three wrapper commands, all 16 `/ars-*` prompt templates, and all four ARS skills, plus nine passing unit tests (including filesystem-backed symlink/XML-location, block-boundary, and single-pass argument-substitution probes) and five real Pi idle-prompt-scope probes.

## Evidence chain

### Full stage chain

[`run-log.md`](run-log.md) provides the chronological checkpoint record. Representative byte-for-byte outputs make each executed stage inspectable:

- Stage 1 Research: [`stage-01/revised-research-report.md`](stage-01/revised-research-report.md)
- Stage 2 Write: [`stage-02/course-paper-draft.md`](stage-02/course-paper-draft.md)
- Stage 2.5 Integrity: [`stage-02.5/focused-reverification-report.md`](stage-02.5/focused-reverification-report.md)
- Stage 3 Review: [`stage-03/editorial-decision-and-revision-roadmap.md`](stage-03/editorial-decision-and-revision-roadmap.md)
- Stage 4 Revise: [`stage-04/response-to-reviewers.md`](stage-04/response-to-reviewers.md)
- Stage 3′ Re-review: [`stage-03p/verification-review-report.md`](stage-03p/verification-review-report.md)
- Stage 4′ Re-revise: [`stage-04p/validation-report.md`](stage-04p/validation-report.md)
- Stage 4.5 Final integrity: [`stage-04.5/final-integrity-verification-report.md`](stage-04.5/final-integrity-verification-report.md)
- Stage 5 Finalize and Stage 6 Process summary: final package, process records, checkpoints, and terminal state below

### Source-read hard gate

1. [`stage-05/cite-time-gate-refusal-report.md`](stage-05/cite-time-gate-refusal-report.md) and [`stage-05/cite-time-gate-refusal.json`](stage-05/cite-time-gate-refusal.json) show that Stage 5 refused converted output while all 79 citation occurrences remained unacknowledged `LOW-WARN`.
2. After the required human attestation was consumed, [`stage-05/cite-time-gate-pass.json`](stage-05/cite-time-gate-pass.json) recorded 21 attested sources, 79/79 markers resolved to `OK`, and a hard-gate `PASS` before clean outputs were emitted.
3. Exact attestation wording, Pi session identifiers, event identifiers, and human-read ledger were intentionally omitted from the public bundle. The aggregate gate state is sufficient for port evidence and is not independent proof that reading occurred.

### Stage 5

- Retained public evidence: final [`paper.md`](stage-05/package/paper.md), [format validation](stage-05/package/format-validation.md), cite-time refusal/PASS records, and [FULL checkpoint](stage-05/full-checkpoint.md).
- The run also generated a DOCX and advisory submission-verifier artifacts. Those redundant binary/snapshot files are intentionally omitted; their hashes and outcomes remain in the checkpoint and persisted state.
- No paper PDF exists because the test operator declined paper LaTeX. HTML-to-PDF was not used.
- The submission-package policy was advisory. B1–B5 and C1–C2 remained `NOT-CHECKED`; this is not a clean universal submission-verifier pass.

### Stage 6 and terminal state

- The concise public process evidence is the [English Markdown record](stage-06/process-record-en.md). Redundant PDF, LaTeX, translated copy, and build-validation files are omitted.
- [Terminal checkpoint](stage-06/terminal-checkpoint.md) was correctly nonterminal when presented.
- [`state/pipeline-state.json`](state/pipeline-state.json) is the controlling proof: `pipeline_state: completed`, Stage 6 `completed`, checkpoint confirmed, terminal acknowledgement received, and completion timestamp persisted. Exact acknowledgement wording and transport identifiers are omitted.

## Model portability

[`model-portability.md`](model-portability.md) compares observed `openai-codex/gpt-5.6-sol` behavior with the repository's illustrative Claude-oriented example. It separates runtime-established divergences from output differences that cannot be causally attributed to the model.

## Privacy boundary

- No maintainer name, email, account, home-directory path, credential, API key, authorization token, or Git remote is included.
- “Scholar” decisions in generated artifacts are synthetic test-operator inputs for the canonical example. Funding, conflict, affiliation, authorship, and placeholder statements are not biographical declarations about the Pi port maintainer.
- The public bundle records only aggregate human-read gate state; exact attestation wording and internal session/event identifiers are excluded.
- Public-source UUIDs appearing inside government document URLs are source locators, not Pi or user identifiers.

## Preserved limitations

- Sequential same-context role simulation is weaker than independent agents or context windows.
- Source verification and the scholar's source-read attestation have distinct evidentiary meanings.
- The paper is a non-systematic evidence synthesis and retains the nonblocking PRISMA-trAIce/RAISE reporting warning.
- The submission verifier was advisory and incomplete for checks requiring absent venue-profile or corpus inputs.
- Four title-page placeholders remain.
- The run experienced model-stream stalls, recovery, and compaction.

See [`inventory.json`](inventory.json) for source-to-curated path and hash provenance. `SHA256SUMS` covers every curated file except itself. Raw RPC streams, full session logs, internal identifiers, downloaded source files, redundant binaries/translations, and intermediate caches are intentionally excluded.
