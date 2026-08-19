# Promotion Bakeoff run — `gpt-5.6-sol` over the ChatGPT-subscription codex transport

**Date:** 2026-08-19 (all calls same-day, paired) · **Issue:** #787 · **Operator:** maintainer session
**Procedure:** `shared/cross_model_verification.md` § Promotion Bakeoff, executed over the #630 contained citation transport (codex-cli 0.147.0, `ARS_CROSS_MODEL_TRANSPORT=codex`).

## Transport qualification (what this run licenses)

The canonical bakeoff was written for the first-party API route. This run substitutes the codex subscription transport end-to-end, so its result is **transport-qualified**:

- It licenses `validated` for `gpt-5.6-sol` **on the ChatGPT-subscription citation transport only**.
- The first-party API route's jq grounding guards were not exercised; `gpt-5.6-sol` **remains provisional on the API route** and the API-route allowlist in the canonical doc is deliberately unchanged.
- Measure analogues: grounding evidence = receipt `searched == true` (webSearch-event binding); measure 4 = zero fail-closed receipt-guard misfires (`EVENT_STREAM_INVALID` / `FINAL_OUTPUT_INVALID` / `TURN_NOT_COMPLETED` families, and transport errors).

## Entry gate

`scripts/cross_model_smoke_test_codex.sh` PASS for both `gpt-5.5` and `gpt-5.6-sol` (2026-08-19), after the #785/#786 transport repair (attestation stream, provider `uniqueItems` rejection, `code_mode_host` disable killing standalone search).

## Probe set

`evals/bakeoff/2026-08-19-gpt-5-6-sol-codex/probe_set.json`
**sha256 `6db7c1ffeb20d4b6819010f7c7ca79f422acfef560c14cfbaf6896c78db305c2`**

30 references: 10 easy (DOI-keyed journal articles), 10 hard (3 arXiv preprints, 2 DOI-less NeurIPS proceedings papers, 5 non-English — 3 zh-TW higher-education-QA articles, 1 de, 1 fr), 10 synthetic fabrications. Every real row was resolver-confirmed the same day (Crossref direct DOI lookup / arXiv API id lookup / live papers.nips.cc fetch); every fabricated row was negative-checked against Crossref bibliographic search.

**Ground-truth correction during the campaign:** three real rows initially carried metadata defects introduced while transcribing truncated discovery output (missing co-authors 許羿梃 / 陳瑩; a wrong author initial and a fabricated completion of a truncated German title). Both models flagged all three as MISMATCH — correctly. The rows were re-verified against full Crossref records, corrected in the fixture, and their 18 cells re-run; no other cell was touched. The episode is itself evidence for the citation-integrity design: the check caught the operator's own transcription/hallucination errors.

## Tool-defect run (run 1, archived, not scored)

The first 180-call fleet surfaced two receipt-grammar drifts against real codex-cli 0.147.0 streams, concentrated on fabricated references (absence checks legitimately open result pages):

1. Page-open `webSearch` items (`action.type == "other"`, no query string) made the whole stream `EVENT_STREAM_INVALID`.
2. `NOT_FOUND` verdicts carrying absence-evidence URLs died as `FINAL_OUTPUT_INVALID`.

Both were fixed in the transport before the scored run (page-open items skipped for binding, never stream-fatal — an opened page's URL still can never become a bound source; `DEVELOPER_INSTRUCTIONS` now instructs an empty `sources` array for NOT_FOUND/NOT_SEARCHED, contract unchanged). Run-1 artifacts are retained off-repo as defect evidence; run 1 produced no scored measures (recall was tool-suppressed to 0.2 for both models identically).

## Scored run (run 2): 30 refs × 3 repeats × 2 models = 180 calls

Per-reference verdict = majority of 3 repeats; no 1–1–1 split occurred in the scored run. Concurrency 3, one call per reference per repeat. Per-call index: `evals/bakeoff/2026-08-19-gpt-5-6-sol-codex/run2_call_index.jsonl` (verdict, searched, reason_code, latency, receipt digests per call).

| Measure | `gpt-5.5` (baseline) | `gpt-5.6-sol` (candidate) | Threshold | Result |
|---|---|---|---|---|
| 1. Grounded-search completion (per call) | 0.900 | **0.933** | ≥ base − 5 pp | PASS |
| 2. Fabrication recall (10 fabs, majority) | 0.80 | **1.00** | ≥ base − 5 pp AND ≥ 0.80 | PASS |
| 3. False disagreement (20 real, majority) | 0.00 | 0.00 | ≤ base + 5 pp | PASS |
| 4. Receipt-guard misfires (shape families) | 0 | **0** | zero (candidate) | PASS |
| 5. p95 latency | 58.7 s | **26.5 s** | ≤ 2× base | PASS |

Baseline misses on measure 2: `fab-01`, `fab-05` returned majority `NOT_SEARCHED` for `gpt-5.5` (scored as misses, conservatively). Median latency: 16.9 s (base) / 17.6 s (candidate).

## Outcome (per the two-promotion rule)

1. **All five measures pass → `gpt-5.6-sol` is `validated` for the ChatGPT-subscription citation transport.**
2. **Superiority case (stated, measured):** +20 pp fabrication recall (1.00 vs 0.80), +3.3 pp grounded completion, and p95 latency under half of baseline, with no inferiority on any measure. This licenses measured-superiority claims for this transport per § Promotion Bakeoff.
3. `gpt-5.6-sol` **stays provisional on the first-party API route** — an API-route bakeoff (same probe set reusable by hash) is the remaining step to full validation; tracked as follow-up in #787.

## Reproduction

Runner and scorer are deterministic consumers of the probe set + receipts; the live calls consume ChatGPT-subscription capacity and web-search results vary day to day — the 3-repeat majority and same-day pairing are the fairness mechanism, per the canonical procedure.
