# Promotion Bakeoff run — `gpt-5.6-sol` over the ChatGPT-subscription codex transport

**Date:** campaign 2026-08-19 → 2026-08-20 (scored fleet: all 180 calls same-day paired on 2026-08-20) · **Issue:** #787 · **Operator:** maintainer session
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
- **Instrument frozen before the scored run:** the receipt parser, gate scorer, and fleet runner used for run 7 are branch commit `69cd04a` — including counterbalanced pair scheduling (the two models' calls for each cell adjacent, pair order alternating by parity, so model identity is decorrelated from execution time), the no-erasure/no-reroll runner with identity-bound fresh cells and orphan/stray preflights, and the scorer's probe-hash, identity-binding, completeness, dated-same-day, effort-marker, and nonzero-on-fail gates. Committed and pushed prior to run 7.

Probe set: 30 references — 10 easy (DOI-keyed journal articles), 10 hard (3 arXiv preprints, 2 DOI-less NeurIPS proceedings papers, 5 non-English: 3 zh-TW higher-education-QA articles, 1 de, 1 fr), 10 synthetic fabrications. Every real row was resolver-confirmed the same day (Crossref direct DOI lookup / arXiv API id lookup / live papers.nips.cc fetch); every fabricated row was negative-checked against Crossref bibliographic search.

## Exploratory rounds (runs 1–6, archived, not scored)

The campaign deliberately reports its own tool failures:

- **Run 1 (tool defect):** two receipt-grammar drifts against real codex-cli 0.147.0 streams — page-open `webSearch` items made the whole stream `EVENT_STREAM_INVALID`, and `NOT_FOUND` verdicts carrying absence-evidence URLs died as `FINAL_OUTPUT_INVALID`. Both suppressed fabrication recall to 0.2 for BOTH models identically. Fixed before any scored run (page-open items skipped for binding, never stream-fatal; `DEVELOPER_INSTRUCTIONS` requires an empty `sources` array for NOT_FOUND/NOT_SEARCHED).
- **Run 2 (exploratory; ground-truth correction):** all five measures passed (recall 1.00 vs 0.80, p95 26.5 s vs 58.7 s), but three real probe rows carried operator transcription defects (missing co-authors 許羿梃 / 陳瑩; a wrong author initial and a fabricated completion of a truncated German title) — **both models correctly flagged all three as MISMATCH**. The rows were independently re-verified against full Crossref records and corrected. Because the fixture changed after observing outputs, run 2 is exploratory, not a gate result — the preregistration clause exists precisely for this.
- **Run 3 (instrument defect):** an interim over-narrow page-open exemption (single observed shape `other`) rejected the equally legitimate `openPage` shape, tool-suppressing the baseline's measures (13 `EVENT_STREAM_INVALID` cells, recall 0.50) while leaving the candidate at zero misfires — a comparison flattering the candidate, therefore discarded. The exemption was re-anchored to the protocol's closed `WebSearchAction` set (verified via `codex app-server generate-json-schema`).
- **Run 4 (prior-instrument round, superseded):** all five measures passed under parser `c9c865d` (recall 1.00 vs 0.80, grounded completion 0.933 vs 0.867, p95 28.1 s vs 51.2 s), but cross-model review correctly held that later parser hardening (rounds 7–10 closed verdict-masking paths) made those zero-misfire counts unverifiable for the parser actually shipped — raw streams are digest-only, so the fleet was rerun rather than argued.
- **Run 5 (prior-instrument round, superseded):** all five measures passed under parser `db6ed67` (recall 0.90 vs 0.80, grounded completion 0.911 vs 0.889, p95 26.1 s vs 47.6 s), superseded for the same reason after the round-11 hardening (unbound-entry and item-id validation) post-dated it.
- **Run 6 (order-confounded, superseded):** all five measures passed under `adf18f9` (recall 1.00 vs 0.70, grounded completion 0.911 vs 0.867, p95 28.8 s vs 43.3 s) and its receipts survive the post-run hardening by the receipt-level invariance proof below — but the fleet executed essentially all baseline calls before all candidate calls (timestamps confirm), confounding model identity with execution time. Cross-model review round 32 held, correctly, that a paired comparison requires counterbalancing; the fleet was rerun with interleaved parity-alternating scheduling rather than argued. Notably, run 6's grounded-completion edge (+4.4 pp) did NOT survive counterbalancing (run 7: tie), while the recall and latency advantages did.

## Instrument-freeze boundary (decision record)

Runs 4 and 5 were discarded because parser gaps let malformed CONSUMED data hide behind model verdicts. Transport hardening that landed after run 6 (`adf18f9`) is dispositioned by RECEIPT-LEVEL PROOF, not assertion. Run 6's 180 receipts contain exactly two reason states — `null` (clean rows) and `SOURCE_NOT_IN_SEARCH_RESULTS` (12 baseline / 8 candidate) — with zero receipt-less rows, zero error rows, and zero occurrences of `NO_BOUND_SEARCH_RESULTS`, `NO_REFERENCE_BOUND_QUERY`, `FINAL_OUTPUT_INVALID`, `MODEL_RETURNED_NOT_SEARCHED`, or `EVENT_STREAM_INVALID`. Each later change therefore provably cannot alter any run-6 cell:

- Page-open payload/id/results checks (round 15) touch only fields of items excluded from every consumed path — no receipt field can differ.
- Hashability guards (round 19) matter only for streams that crashed the old verifier — zero receipt-less/error rows means no such stream occurred.
- NOT_FOUND-precedence (round 24) and the key-drift classification (rounds 26/28) only RELABEL cells that emitted `FINAL_OUTPUT_INVALID` / `NO_BOUND_SEARCH_RESULTS` / `NO_REFERENCE_BOUND_QUERY` — zero such cells exist, so no run-6 cell ever reached either branch.
- The NOT_SEARCHED-with-sources check (round 9, in `adf18f9`) was already active during run 6.

Maintainer policy, pinned here and in the canonical recorded-run note: a scored fleet is bound to its preregistered frozen instrument, and post-run hardening stands or falls on this kind of receipt-level invariance proof — where receipts cannot establish invariance for a consumed path, the fleet is rerun (as runs 4 and 5 were). Cross-model review rounds 16 and 30 requested reruns; both are resolved by the proof above, with the disagreement recorded rather than hidden.

## Answer-key exposure analysis

Preregistering the fixture in a public repository publishes the `real`/`fabricated` labels before a live-web-search run — in principle a search backend could retrieve the answer key instead of verifying citations. Assessment for this run:

- **Empirical scan (primary):** across all 1,080 retained receipts (runs 2–7, both models), zero bound search queries and zero bound sources reference `github.com/Imbad0202`, `raw.githubusercontent.com`, the repository name, or the fixture filename. Scope caveat: receipts record reference-bound queries and bound sources; unbound queries and opened-page contents are not retained, so the scan covers what the verdicts were actually allowed to rest on.
- **Corroboration:** fabricated-row rationales cite domain evidence (journal tables of contents, publisher records), not the repository; the fixture reached a non-default branch roughly one hour before run 4, inside ordinary search-index latency; and the baseline's recall stayed at 0.80 — an accessible answer key would have lifted both models.
- **Residual risk + forward fix:** the exposure is a property of the canonical procedure (public repo + commit-before-run), not of this run's compliance. A sealed-preregistration variant (commit the fixture's hash, reveal contents after the fleet) is filed as a follow-up for future bakeoffs; the labels of THIS probe set are now public permanently, so any future run needs a fresh fabrication pool regardless.

## Retained artifacts (replayability)

Everything the scoring rests on is committed beside the probe set in `evals/bakeoff/2026-08-19-gpt-5-6-sol-codex/`:

- `run7_receipts_gpt-5.5.jsonl` / `run7_receipts_gpt-5.6-sol.jsonl` — the 180 full receipt rows (verdict, searched, reason_code, bound sources, search queries, request/event digests, wall-clock latency).
- `score_run.py` — offline stdlib scorer; recomputes all five measures and the gate from the committed receipts alone (verified to reproduce the table below byte-for-byte).
- `run_fleet.py` — the runner (live subscription calls; reproduction consumes quota and web results vary by day).
- `run7_call_index.jsonl` — compact per-call index.

Boundary of replayability, stated plainly: raw app-server event streams are not retained — the closed transport emits only receipts with event-stream digests, by design. The `searched` bit and source bindings therefore rest on the transport's fail-closed validation (pinned by its 59-test suite), not on re-inspection of the streams.

## Scored run (run 7, 2026-08-20, instrument `69cd04a`, counterbalanced): 30 refs × 3 repeats × 2 models = 180 calls

Per-reference verdict = majority of 3 repeats. Two 1–1–1 splits occurred, both scored INDETERMINATE = conservative recall misses exactly as the canonical procedure prescribes: baseline `fab-05` and candidate `fab-01`. Counterbalanced pair scheduling, concurrency 3, one call per reference per repeat, both models same day. Reasoning effort pinned to the provider default and recorded per row (`reasoning_effort` marker in every committed run-7 row).

| Measure | `gpt-5.5` (baseline) | `gpt-5.6-sol` (candidate) | Threshold | Result |
|---|---|---|---|---|
| 1. Grounded-search completion (per call) | 0.900 | 0.900 | ≥ base − 5 pp | PASS |
| 2. Fabrication recall (10 fabs, majority) | 0.80 | **0.90** | ≥ base − 5 pp AND ≥ 0.80 | PASS |
| 3. False disagreement (20 real, majority) | 0.00 | 0.00 | ≤ base + 5 pp | PASS |
| 4. Receipt-guard misfires (shape families) | **0** | **0** | zero (both fleets) | PASS |
| 5. p95 latency (nearest-rank) | 49.6 s | **25.0 s** | ≤ 2× base | PASS |

Measure-2 misses (scored conservatively): baseline `fab-01` majority `NOT_SEARCHED` and `fab-05` INDETERMINATE; candidate `fab-01` INDETERMINATE. p95 is the nearest-rank order statistic (ceil(0.95·n)-th smallest); the committed scorer additionally refuses probe-set hash drift, identity-binding violations, truncated/duplicated/partial fleets, undated rows, and mixed-date fleets, and exits nonzero on any gate failure. Zero misfires on BOTH fleets under the shipped frozen instrument `69cd04a`. Median latency: 17.5 s (base) / 14.8 s (candidate). Across all five full paired fleets (runs 2, 4, 5, 6, 7) the candidate led fabrication recall and p95 latency every time; the grounded-completion edge seen in the sequential fleets did not survive counterbalancing (run 7: tie at 0.900) and is NOT claimed. Across the four full paired fleets (runs 2, 4, 5, 6) the candidate led on measures 1, 2, and 5 every single time.

The exploratory run 2, on the pre-correction fixture and interim parser, produced the same qualitative ordering (candidate superior on measures 1, 2, 5; tie on 3) — reported for transparency, carrying no gate weight.

## Outcome (per the two-promotion rule)

1. **All five measures pass → `gpt-5.6-sol` is `validated` for the ChatGPT-subscription citation transport.**
2. **Superiority case (stated, measured, counterbalanced):** +10 pp fabrication recall (0.90 vs 0.80) and p95 latency at 50% of baseline (25.0 s vs 49.6 s nearest-rank; median 14.8 s vs 17.5 s), with no inferiority on any measure (grounded completion tied at 0.900). Recall and latency advantages held in all five full paired fleets; the sequential fleets' grounded-completion edge did not survive counterbalancing and is not claimed. This licenses measured-superiority claims for this transport per § Promotion Bakeoff.
3. `gpt-5.6-sol` **stays provisional on the first-party API route** — an API-route bakeoff is the remaining step to full validation, and it requires a FRESH probe set under the #789 sealed-preregistration protocol (this set's labels are now public); tracked as follow-up in #787.

## Reproduction

Runner and scorer are deterministic consumers of the probe set + receipts; the live calls consume ChatGPT-subscription capacity and web-search results vary day to day — the 3-repeat majority and same-day pairing are the fairness mechanism, per the canonical procedure.
