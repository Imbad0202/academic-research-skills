# Reviewer Calibration — Held-Out Gold Corpus and First Measured Error Profile (#653)

**Epistemic status.** This suite holds the provenance manifest and measurement
artifacts for the FIRST real execution of the reviewer calibration protocol
(`academic-paper-reviewer/references/calibration_mode_protocol.md`, full tier).
Until a run-history row lands below, the reviewer skill has **no measured error
profile** and no review may claim one. The protocol's resolved design decision
against shipping a built-in gold set stands unamended: this directory ships
**pointers and hashes, never paper text**.

## Corpus (provenance manifest, not a dataset)

> **SUPERSEDED — layout leaks the label; harness rehearsal only (2026-09-06, #828).**
> The 2026-09-06 freeze below is byte-valid but unusable as a calibration gold
> set: OpenReview replaces accepted ICLR papers' PDFs with the camera-ready
> revision (`Published as a conference paper at ICLR 2026` header, named
> authors, no line numbers) while rejected papers keep the anonymous
> line-numbered submission PDF — 6/6 + 6/6 in this corpus, 30/30 in a fresh
> accepted-pool sample. Submission-time revisions are not readable by an
> ordinary account. This manifest is retained to exercise the dispatch /
> scoring / measurement-envelope path end to end; **no error profile may be
> published from it.** The gold corpus will be an ICLR 2027 submission-time
> capture (PDFs fetched before decisions, labels attached after).
> Since the layout-tell guard landed in `assemble_calibration_corpus.py`
> (2026-09-06), `verify` FAILs on this corpus by design (every signal is 6/0
> across the classes); `freeze` refuses any corpus whose page-1 layout is not
> constant across every paper, and records `layout_tell_check` when it is.

- `corpus/papers.json` — 12 ICLR 2026 papers (OpenReview): forum id, title,
  canonical PDF URL, `pdf_sha256`, `extracted_text_sha256` (pypdf, version
  pinned in the manifest; normalization rule recorded as
  `extraction.text_normalization` and shared with the dispatcher via
  `scripts/_calibration_pdf_text.py` — NFC plus lone-surrogate → U+FFFD, the
  latter because one sampled manuscript's math fonts emit code points strict
  UTF-8 refuses), page count, retrieval timestamp. **Label-free by
  construction** (leak guard in `scripts/assemble_calibration_corpus.py`);
  this is the only corpus file on the dispatcher's read path.
- `manifests/gold_labels.json` — the gold labels (6 `accept` / 6 `reject`)
  with the public decision string and Decision-note id per paper, plus the
  label transform. Structurally excluded from every panel context (see
  Isolation below).
- `corpus/pool_accepted_ids.txt`, `corpus/pool_rejected_ids.txt` — the FULL
  sorted forum-id lists of both pools at retrieval time (accepted n=5351,
  `ICLR.cc/2026/Conference`; reviewed-and-rejected n=8356,
  `ICLR.cc/2026/Conference/Rejected_Submission`), so the pool-membership
  hashes in the manifest are reconstructable byte-for-byte. Withdrawn and
  desk-rejected submissions live in separate OpenReview venue partitions and
  never entered a pool — that IS the exclusion rule for them.
- Selection: deterministic seeded shuffle (seed
  `ars-653-reviewer-calibration-iclr2026-v1`), stratified 6+6, page cap 60,
  closed-enum exclusion ledger recorded in the manifest. Reconstruction:
  `python scripts/assemble_calibration_corpus.py verify --out-dir <this dir>
  --pdf-dir <your PDF cache>` (PDFs re-fetched with your own OpenReview
  account via `scripts/fetch_calibration_corpus.py`; anonymous PDF download
  was closed off by OpenReview as of 2026-08-07). Frozen 2026-09-06 (UTC
  2026-09-05T23:35–23:36Z retrieval window); no page-cap exclusion fired.
- Licensing: OpenReview submission notes carry their own licenses (the
  sampled notes declare CC BY 4.0); manuscript PDFs are NOT redistributed
  here. Metadata stored is pointer-grade (ids, titles, hashes, timestamps).

### Why ICLR 2026 (as pre-registered on 2026-08-07)

Decisions became public 2026-01 — at/after the then-subject model's stated
training cutoff (Claude Fable 5, 2026-01), minimizing decision-leakage risk;
it is also the same venue family and label route Lu et al. (2026) used, which makes the
protocol's Lu comparison table applicable (all-binary accept/reject ML-venue
gold set). Residual risk is handled by a per-paper **contamination probe**
(pre-registered hit rule in `RUN_PLAN.md`): 0/18 candidates claimed recall of
their actual outcome; one candidate (`nCEs0tSwc2`) reported knowing the paper
itself but not its decision and was retained — recorded here so readers can
weigh it. Two facts now cut against this venue for a *measured* run: the
layout leak above, and the subject model's move to Claude Fable 5.1 (stated
cutoff 2026-06), which places the ICLR 2026 decisions inside training. Both
are resolved by the ICLR 2027 capture; the probe is re-run on the subject
model actually dispatched.

### Known corpus limits (declared up front)

- **Domain scope**: ML conference papers. The measured profile is valid for
  this corpus and domain only; the protocol's same-family / rubric-aware
  epistemic note applies on top.
- **Binary labels**: ICLR supplies accept/reject, not four-tier editorial
  labels. The Minor/Major boundary sub-matrix publishes as `NOT ESTIMABLE`,
  and per-dimension calibration error as `NOT COMPUTABLE` (no
  `per_dimension_gold_scores`), by the protocol's own honest-gap paths.
- **Page cap 60** is a budget-driven scope rule (pre-registered): the sample
  under-represents papers with very long appendices.

## Isolation model (gold-label isolation, not manuscript blindness)

The calibration engine is the pre-v3.6.2 single-call panel: every seat sees
the manuscript, so the axis that must hold is that **gold labels never enter
any field-analyst / seat / synthesizer context** (protocol § Inputs). The
dispatcher (`scripts/dispatch_calibration_panel.py`) enforces this
structurally: its read path is `corpus/papers.json` (label-free), the seven
agent files, and the local PDF cache (hash-verified against the manifest,
symlinks refused); `manifests/gold_labels.json` is on no read path, and the
join happens only in `scripts/score_calibration_run.py` after every panel
record is frozen. The synthesizer additionally never receives the manuscript.

## Tooling (one attempt, in order)

1. `dispatch_calibration_panel.py --stage cards` per paper, then
   `--stage panel` per (paper, replicate). A rejected credential is caught by a
   zero-cost `GET /v1/models` preflight before the first billed call and is
   never retried mid-run; an aborted cards stage leaves
   `runs/blocked-cards-<paper>.json` with its per-call rows, and a re-run
   needs a fresh work dir (evidence and stage records are write-once).
2. `dispatch_calibration_panel.py --stage manifest` once, after the last
   panel: folds every completed call row into the write-once
   `execution-manifest.json` (`heldout-execution-manifest/1.0`); refuses mixed
   attempt ids.
3. `score_calibration_run.py` — mechanical metrics, gold joined only here.
4. Phase 3.5 judges (two families) produce the contract-shaped judge rows.
5. `build_calibration_measurement_row.py` — the 1.1 row: pre-registration
   record (plan + rubric hashed and compared against `frozen_commit`), manifest
   reference, blocked runs, judge rows, adjudication overrides; validated by
   `check_heldout_measurement_report.py` before it is written. Filing the row
   and `runs/` under this directory is a separate step; `--resolve-refs` then
   re-runs R1-R5.

## Run rules

`RUN_PLAN.md` (pre-registered) fixes: subject model and transport recipe,
`substrate_plan: primary_only` with the required disclosure, 3 replicates per
paper with frozen per-paper Reviewer Configuration Cards, the two-family
judge plan for Phase 3.5 severity-risk classification, and the adjudication
rubric (`adjudication_rubric.md`, sha256-pinned in each measurement row).

## Run history

| Date | Row | Verdict |
|---|---|---|
| — | — | no measured run yet |

## Measurement contract (#654 / #664)

Scored runs publish one `measurement-<date>.json` in `heldout-measurement/1.1`
envelope form (with the 1.1 pre-registration record + write-once execution
manifest; 1.0 is closed to new rows) (`suite: reviewer_calibration`, `suite_class: llm_judged`,
registered in `evals/heldout/suite_registry.json`): mechanical headline
(FNR/FPR/balanced accuracy from the closed decision grammar) declared via
`construction_rule`; per-judge `per_item` rows for the judged elements; raw
pre-adjudication values always published alongside adjudicated ones; raw
outputs retained under `runs/`.
