# Promotion Bakeoff run — `gpt-5.6-sol` over the ChatGPT-subscription codex transport

**Date:** 2026-08-19 (all scored calls same-day, paired) · **Issue:** #787 · **Operator:** maintainer session
**Procedure:** `shared/cross_model_verification.md` § Promotion Bakeoff, executed over the #630 contained citation transport (codex-cli 0.147.0, `ARS_CROSS_MODEL_TRANSPORT=codex`).

## Transport qualification (what this run licenses)

The canonical bakeoff was written for the first-party API route. This run substitutes the codex subscription transport end-to-end, so its result is **transport-qualified**:

- It licenses `validated` for `gpt-5.6-sol` **on the ChatGPT-subscription citation transport only**.
- The first-party API route's jq grounding guards were not exercised; `gpt-5.6-sol` **remains provisional on the API route** and the API-route allowlist in the canonical doc is deliberately unchanged.
- Measure analogues: grounding evidence = receipt `searched == true` (webSearch-event binding); measure 4 = zero fail-closed receipt-guard misfires (`EVENT_STREAM_INVALID` / `FINAL_OUTPUT_INVALID` / `TURN_NOT_COMPLETED` families, and transport errors).

## Entry gate

`scripts/cross_model_smoke_test_codex.sh` PASS for both `gpt-5.5` and `gpt-5.6-sol` (2026-08-19), after the #785/#786 transport repair (attestation stream, provider `uniqueItems` rejection, `code_mode_host` disable killing standalone search).

## Preregistration

- **Probe set frozen before the scored run:** `evals/bakeoff/2026-08-19-gpt-5-6-sol-codex/probe_set.json`, sha256 **`6db7c1ffeb20d4b6819010f7c7ca79f422acfef560c14cfbaf6896c78db305c2`**, committed and pushed at branch commit `3fc6ddb` prior to run 4; not modified afterward.
- **Instrument frozen before the scored run:** the receipt parser used for run 4 is branch commit `c9c865d` (page-open exemption anchored to the first-party closed `WebSearchAction` set), committed and pushed prior to run 4.

Probe set: 30 references — 10 easy (DOI-keyed journal articles), 10 hard (3 arXiv preprints, 2 DOI-less NeurIPS proceedings papers, 5 non-English: 3 zh-TW higher-education-QA articles, 1 de, 1 fr), 10 synthetic fabrications. Every real row was resolver-confirmed the same day (Crossref direct DOI lookup / arXiv API id lookup / live papers.nips.cc fetch); every fabricated row was negative-checked against Crossref bibliographic search.

## Exploratory rounds (runs 1–3, archived, not scored)

The campaign deliberately reports its own tool failures:

- **Run 1 (tool defect):** two receipt-grammar drifts against real codex-cli 0.147.0 streams — page-open `webSearch` items made the whole stream `EVENT_STREAM_INVALID`, and `NOT_FOUND` verdicts carrying absence-evidence URLs died as `FINAL_OUTPUT_INVALID`. Both suppressed fabrication recall to 0.2 for BOTH models identically. Fixed before any scored run (page-open items skipped for binding, never stream-fatal; `DEVELOPER_INSTRUCTIONS` requires an empty `sources` array for NOT_FOUND/NOT_SEARCHED).
- **Run 2 (exploratory; ground-truth correction):** all five measures passed (recall 1.00 vs 0.80, p95 26.5 s vs 58.7 s), but three real probe rows carried operator transcription defects (missing co-authors 許羿梃 / 陳瑩; a wrong author initial and a fabricated completion of a truncated German title) — **both models correctly flagged all three as MISMATCH**. The rows were independently re-verified against full Crossref records and corrected. Because the fixture changed after observing outputs, run 2 is exploratory, not a gate result — the preregistration clause exists precisely for this.
- **Run 3 (instrument defect):** an interim over-narrow page-open exemption (single observed shape `other`) rejected the equally legitimate `openPage` shape, tool-suppressing the baseline's measures (13 `EVENT_STREAM_INVALID` cells, recall 0.50) while leaving the candidate at zero misfires — a comparison flattering the candidate, therefore discarded. The exemption was re-anchored to the protocol's closed `WebSearchAction` set (verified via `codex app-server generate-json-schema`).

## Scored run (run 4): 30 refs × 3 repeats × 2 models = 180 calls

Per-reference verdict = majority of 3 repeats (no 1–1–1 split occurred). Concurrency 3, one call per reference per repeat, both models same day. Per-call index: `evals/bakeoff/2026-08-19-gpt-5-6-sol-codex/run4_call_index.jsonl` (verdict, searched, reason_code, latency, receipt digests per call).

| Measure | `gpt-5.5` (baseline) | `gpt-5.6-sol` (candidate) | Threshold | Result |
|---|---|---|---|---|
| 1. Grounded-search completion (per call) | 0.867 | **0.933** | ≥ base − 5 pp | PASS |
| 2. Fabrication recall (10 fabs, majority) | 0.80 | **1.00** | ≥ base − 5 pp AND ≥ 0.80 | PASS |
| 3. False disagreement (20 real, majority) | 0.00 | 0.00 | ≤ base + 5 pp | PASS |
| 4. Receipt-guard misfires (shape families) | **0** | **0** | zero (candidate) | PASS |
| 5. p95 latency | 51.1 s | **27.5 s** | ≤ 2× base | PASS |

Baseline misses on measure 2: `fab-01`, `fab-08` returned majority `NOT_SEARCHED` for `gpt-5.5` (scored as misses, conservatively). Median latency: 16.2 s (base) / 16.2 s (candidate). Zero misfires on BOTH models confirms the final instrument is clean — run 4 is also the parser's live validation.

The exploratory run 2, on the pre-correction fixture and interim parser, produced the same qualitative ordering (candidate superior on measures 1, 2, 5; tie on 3) — reported for transparency, carrying no gate weight.

## Outcome (per the two-promotion rule)

1. **All five measures pass → `gpt-5.6-sol` is `validated` for the ChatGPT-subscription citation transport.**
2. **Superiority case (stated, measured):** +20 pp fabrication recall (1.00 vs 0.80), +6.7 pp grounded completion (0.933 vs 0.867), and p95 latency roughly half of baseline (27.5 s vs 51.1 s), with no inferiority on any measure. This licenses measured-superiority claims for this transport per § Promotion Bakeoff.
3. `gpt-5.6-sol` **stays provisional on the first-party API route** — an API-route bakeoff (same probe set reusable by hash) is the remaining step to full validation; tracked as follow-up in #787.

## Reproduction

Runner and scorer are deterministic consumers of the probe set + receipts; the live calls consume ChatGPT-subscription capacity and web-search results vary day to day — the 3-repeat majority and same-day pairing are the fairness mechanism, per the canonical procedure.
