# Model portability: `openai-codex/gpt-5.6-sol`

## Comparison boundary

This note records one observed Pi run with `@earendil-works/pi-coding-agent` 0.83.0 and `openai-codex/gpt-5.6-sol`. The comparison target is [`academic-pipeline/examples/full_pipeline_example.md`](../../academic-pipeline/examples/full_pipeline_example.md), which documents the intended Claude-oriented experience but is an illustrative conversation log, not a paired empirical run. Differences below therefore must not be interpreted as a controlled model benchmark.

The run also differs in ARS version, available tools, user decisions, and evidence availability. A behavior is attributed specifically to the Pi runtime only when the execution record establishes that boundary; other differences are reported as observations without causal attribution.

## Tested configuration

| Field | Value |
| --- | --- |
| Pi | `@earendil-works/pi-coding-agent` 0.83.0 |
| Provider/model | `openai-codex/gpt-5.6-sol` |
| Thinking | high |
| ARS | 3.19.0 |
| Orchestration | none exposed inside Pi |
| Web retrieval | `/skill:websearch` exposed |
| Claude hooks | unavailable |
| Execution | sequential in one model context, with persisted-session recovery |

No Claude, Opus, or Sonnet run was executed as part of this evidence. “Claude baseline” below means the repository's documented illustrative behavior, not a fresh Claude result.

## Observed divergences

| Area | Documented Claude-oriented baseline | Observed Pi/model behavior | Evidence and interpretation |
| --- | --- | --- | --- |
| Model routing | ARS is calibrated for Opus architecture/review and Sonnet execution; command frontmatter can request Sonnet. | Every role used `openai-codex/gpt-5.6-sol`; Claude `model: sonnet` metadata was ignored. | Runtime difference. See [`runtime/ars-pi-doctor.txt`](runtime/ars-pi-doctor.txt) and [`state/pipeline-state.json`](state/pipeline-state.json). |
| Agent execution | Example describes parallel independent reviewer agents and specialist handoffs. | Specialist roles and five reviewer perspectives ran sequentially in the same recovered context. No independent reviewer, writer, verifier, formatter, observer, or cross-model judgment is claimed. | Load-bearing runtime divergence. Actual disclosure appears in [`stage-03/editorial-decision-and-revision-roadmap.md`](stage-03/editorial-decision-and-revision-roadmap.md), [`stage-04.5/final-integrity-verification-report.md`](stage-04.5/final-integrity-verification-report.md), and [`stage-06/process-record-en.md`](stage-06/process-record-en.md). |
| Write-scope enforcement | Claude distribution wires a `PreToolUse` write-scope guard. | Claude hooks did not execute. Scope discipline was prompt-level and artifact-checked after writes. | Load-bearing runtime divergence; no deterministic Claude hook boundary is claimed. |
| Review independence | Example reports independent review reports before editorial synthesis. | Reports were structurally separated but shared one model context. The final self-reflection mechanically classified sycophancy risk as HIGH because both explicit Devil's Advocate concessions were accepted. | Same-context execution may correlate errors. This is not evidence that independent Claude reviewers would reach different verdicts. |
| Re-review outcome | Illustrative example reaches Minor Revision after one revision and proceeds to finalization. | Stage 3′ returned Major Revision, causing focused Stage 4′ re-revision before final integrity. | Observed output divergence; cannot be attributed solely to model because manuscript content and current ARS contracts differ. See [`stage-03p/verification-review-report.md`](stage-03p/verification-review-report.md). |
| Interaction length | Example abbreviates several Socratic rounds and presents a compact happy path. | Run consumed all 36 advisory round trips, crossed 20 mandatory/full checkpoints, and required persisted-session recovery. | Not a direct efficiency comparison because baseline rounds are intentionally omitted. It does show materially higher operational friction in this run. |
| Transport/context | Example does not describe stream recovery or compaction. | Stage 3′ encountered stalled model streams; execution resumed from persisted artifacts, state, and hashes across two Pi sessions. | Observed provider/runtime behavior. Continuity was disclosed rather than represented as cognitive independence. |
| Length interpretation | Example targets a 5,200-word paper. | Model initially treated “6,000 words” too literally for Traditional Chinese; scholar corrected target to approximately 6,000 Chinese characters. | Observed model behavior corrected through checkpoint interaction. |
| Claim discipline | Example presents a smooth draft/review sequence. | Model initially overclaimed that all findings were verified and carried an incorrect O7 locator. Stage 2.5 correctly failed, a narrow correction was applied, and focused re-verification passed. | Observed error plus successful gate behavior. See [`stage-02.5/focused-reverification-report.md`](stage-02.5/focused-reverification-report.md). |
| Human-read provenance | Example proceeds directly from accepted re-review to formatting. | Stage 5 refused conversion despite 21/21 technical source verification because no scholar-read attestation existed. It resumed only after explicit full-text attestations resolved 79/79 markers. | Current ARS gate behavior exercised in Pi. See [`stage-05/cite-time-gate-refusal-report.md`](stage-05/cite-time-gate-refusal-report.md) and [`stage-05/cite-time-gate-pass.json`](stage-05/cite-time-gate-pass.json). |
| Final formats | Example emits Markdown, DOCX, LaTeX, and paper PDF. | Run emitted Markdown and DOCX. Scholar explicitly declined paper LaTeX/PDF; bilingual process-record PDFs were still produced. | User decision, not a model or Pi limitation. |

## Behavior that remained effective

Despite the divergences, this run completed the full current pipeline:

- research, writing, integrity, review, revision, re-review, re-revision, final integrity, finalization, and process summary all persisted terminal states;
- no mandatory/full checkpoint was automatically skipped;
- Stage 2.5 produced a real FAIL followed by a bounded correction and PASS;
- Stage 5 produced a real provenance refusal followed by a user-authorized PASS;
- deterministic patch/apply evidence and hashes survived transport recovery;
- degraded sequential execution was disclosed at runtime rather than only predicted by documentation.

These observations show functional execution on the tested model. They do not establish parity with Claude or independence equivalent to a multi-agent panel.

## Portability conclusion

`openai-codex/gpt-5.6-sol` completed ARS 3.19.0 on Pi, but the observed run diverged materially from the documented Claude-oriented experience in model routing, agent independence, hook enforcement, transport stability, re-review path, and several model errors corrected by gates. The strongest supported claim is therefore “completed with disclosed degraded same-context execution,” not Claude runtime parity.
