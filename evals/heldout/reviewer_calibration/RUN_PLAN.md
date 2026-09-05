# Reviewer-Calibration First Measured Run — Pre-Registration (#653)

Registered before the first scored panel dispatches. Changes after the first
dispatch are amendments logged in RUN_NOTES, never silent edits.

## Subject and tier

- **Tier**: `full` (calibration_mode_protocol.md; the only tier that produces
  a measured error profile).
- **Subject**: the `academic-paper-reviewer` calibration panel engine
  (pre-v3.6.2 single-call five-seat + synthesizer semantics), dispatched
  isolated via `scripts/dispatch_calibration_panel.py`.
- **Subject model**: `claude-fable-5`, effort `xhigh`, headless
  `claude -p --bare` with emptied tool whitelist (E4 transport recipe);
  fresh process per call; alias resolution probed before the fleet starts.

## Gold corpus

- ICLR 2026 (OpenReview, public decisions), n=12: 6 accept-side
  (`Accept (Poster|Spotlight|Oral)` → `accept`), 6 reviewed-and-rejected
  (`reject`). Withdrawn / desk-rejected sit in separate OpenReview venue
  partitions and never enter a pool.
- Selection: seeded deterministic shuffle
  (seed `ars-653-reviewer-calibration-iclr2026-v1`) over the full public
  pools (accepted n=5351, rejected n=8356; sorted-id sha256 pinned in
  `corpus/papers.json`), stratified 6+6, page cap 60, exclusions ledger with
  a closed reason enum. Rule details: `scripts/assemble_calibration_corpus.py`.
- Contamination probe: before freezing, each candidate title was probed on
  the subject model (fresh context) for claimed recall of the actual ICLR
  2026 outcome. Hit rule (pre-registered): `knows_paper=true` AND claimed
  outcome matches gold AND confidence `recall`. Result: 0 hits / 18
  candidates; one candidate reported knowing the paper but not its outcome
  (recorded in README). Probe transcripts retained in the raw evidence area.

## Substrate plan (locked)

- `substrate_plan: primary_only`, locked before the first scored panel, per
  the calibration transport exception's fallback branch: cross-model
  Reviewer-2 is configured-but-unconsented for this run (user decision
  2026-08-07: first execution prioritizes a completed homogeneous attempt;
  the attempt-atomicity rule makes a mid-attempt cross-model failure
  invalidate the whole attempt). Disclosure: the published profile and any
  session disclosure carry the single-family correlated-error caveat and the
  same-family optimism note (protocol § Same-family / rubric-aware judging).
- One `attempt_id` for the whole schedule. A panel abort inside the schedule
  blocks that replicate; recovery is re-dispatch of that replicate under the
  same plan (primary-only has no mixed-substrate hazard). No completed panel
  is ever discarded silently; blocked records are committed.

## Schedule and ensembling

- `runs_per_paper: 3` (protocol budget override; median scores, majority-vote
  decisions, variance reported as stability).
- Cards stage once per paper (field analyst; four Reviewer Configuration
  Cards frozen, reused by every replicate). 12 cards calls + 36 panels ×
  (5 seats + 1 synthesis) = 228 subject calls planned.
- Output verification happens only after the dispatching process exits
  (in-flight reads of 0-byte redirect targets are not failures — #652 run
  note); output sweeps include CJK/divider scans for ambient-config leakage.

## Judges (Phase 3.5 severity-risk classification)

- Two judge configurations, two model families (#654 I2):
  `judge-claude-fable-5` (Anthropic) and `judge-codex-gpt-5.6-sol-xhigh`
  (OpenAI, codex CLI, stateless `< /dev/null`, timeout ≥ 600 s, one retry,
  attempt-atomic per item batch).
- Judges see the seats' weakness text only — never the manuscript, never
  gold labels. Divergent items escalate to maintainer adjudication under
  `adjudication_rubric.md` (criterion_ref required). Judge failure after the
  retry leaves the item to `attempts.blocked_runs` + `partial_published`.

## What publishes

- Per-panel records + raw bundles under `runs/` (write-once).
- `scripts/score_calibration_run.py` metrics JSON (mechanical headline:
  confusion matrix, balanced accuracy, FNR over-harsh, FPR lenient,
  bootstrap 95% CIs seed 653, AUC over paper scores, stability;
  Minor/Major sub-matrix NOT ESTIMABLE; per-dimension error NOT COMPUTABLE).
- The Phase 4 Calibration Report (protocol template; Lu 2026 comparison
  table shown — all-binary accept/reject ML-venue gold set qualifies — with
  Lu values as descriptive context, never a benchmark target).
- One `measurement-<date>.json` row under the `heldout-measurement/1.1`
  contract (`suite: reviewer_calibration`, `suite_class: llm_judged`,
  `decision_relevant: true`, `judge_plan.exception: "none"`). 1.1 (the only
  version accepted for new rows since #664) additionally requires a
  `preregistration` record binding this file and `adjudication_rubric.md`
  by SHA-256 to the frozen commit, and a suite-local write-once
  `execution_manifest` with per-call ids, RFC-3339 start/complete
  timestamps, and prompt/output hashes — the dispatcher emits the manifest;
  the scorer builds the row. Both land with the scored run, never after.
