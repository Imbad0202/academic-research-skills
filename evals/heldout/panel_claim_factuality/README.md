# Panel claim factuality (#1002)

How often does a weakness that the review panel states about a manuscript
contradict the manuscript itself? This suite measures that rate on the panels
the E4 suite already ran (`../reviewer_seeded_defects/runs/`), before ARS adds
any check for it. It is the first part of #1002; the second part, a check
between the panel and the editorial synthesizer, is planned only when the
decision rule in `plan.json` says so.

Suite class: `llm_judged` (`../suite_registry.json`). Status: run once (plan version 8, 2026-10-24), plus a contrast test of the Claude session models (plan version 10, 2026-10-25); the results are in `PREREGISTRATION.md`. No `heldout-measurement/1.1` report row is published: adjudication is deferred, so the headline is not computed.

## What is measured

- **Claims**: 805, from the 17 score-eligible E4 bundles: each `### W<n>`
  weakness of the EIC, Methodology, Domain, and Perspective seats, and each
  Devil's Advocate CRITICAL and MAJOR row. Strengths are out of scope.
  `scripts/extract_panel_claims.py` writes them with the seat held back.
- **Verdicts**: `true`, `false`, or `not_verifiable` per `rubric.md`. Only a
  claim that the manuscript text positively contradicts is `false`.
- **Judges**: two model families (`gpt-6-astra` through codex,
  `gemini-4-argon` at medium thinking through the Gemini API), each reading every batch twice.
- **Contrast gate**: before a judge's claim verdicts count, it must find at
  least 95% of the false contrast sentences and call at most 5% of the
  accurate ones false (`PREREGISTRATION.md`, Decoys).
- **Agreement**: each judge's two replicates reduce to one `is_false` flag per
  claim, and every claim falls in one list (agreed false, agreed not false,
  cross-judge divergence, replicate instability, missing; `rubric.md`). A
  judge that fails the contrast gate is left out; with one valid judge the run
  is exploratory, with none it is void (`plan.json`, `validity`).
- **Adjudication**: claims in the last three lists go to the maintainer, on a
  packet that hides the judge, the seat, and the condition. Decisions go in
  `adjudication_decisions.json`, which scoring writes once, bound to the build
  and to each claim's text, and never overwrites.

## Steps

All commands run from the repository root; `$W` is a work directory outside the
repository. Raw outputs are written once and never overwritten.

1. Extract the claims (free); a count other than 17 bundles and 805 claims,
   or any extraction problem, exits 1:
   `python3 scripts/extract_panel_claims.py --runs evals/heldout/reviewer_seeded_defects/runs --out $W/claims --expect-bundles 17 --expect-claims 805`
2. Generate, check, and verify the contrast pairs. The generator and the
   verifier are the transports `plan.json` names:
   `python3 scripts/dispatch_panel_claim_audit.py generate --fixture ms00_clean --out $W/pairs`
   (and `ms01_quant`, `ms02_qual`), then
   `check-pairs --pairs-dir $W/pairs` and `verify-pairs --pairs-dir $W/pairs`.
3. Build the batches (free) into a new directory. The build reads the pairs
   back from the logged generator and verifier outputs, checks them and the
   claim inventory against `plan.json`, and refuses anything else. It copies
   its inputs into the batches directory and writes `build_manifest.json`;
   every later step stops if an input changed since:
   `python3 scripts/dispatch_panel_claim_audit.py build --claims $W/claims/claims.jsonl --pairs-dir $W/pairs --out $W/batches`
4. Probe each agy model that judges once from an empty directory (none from plan version 4), asking it to list
   every instruction, memory, skill, or file it received besides the
   message, and keep the answer with the raw outputs. A memory block with any
   entry stops the run (`PREREGISTRATION.md`, Arms).
5. Pilot: three batches per judge, replicate 1, with
   `run --judge <codex|gemini> --replicate 1 --batches $W/batches --out $W/runs --limit 3`.
   The Gemini judge is paid: set `GEMINI_API_KEY` and give `--cap-usd`; the cap
   covers every Gemini call logged under `--out`. A rebuild after a plan change
   that keeps the prompts takes `--match-manifest <earlier build_manifest.json>`.
   A run stops at the first transport failure, or at an output still
   unreadable after one retry. Report time and usage; the maintainer approves
   the full run.
6. Full run: both judges, replicates 1 and 2.
7. Score: `score --batches $W/batches --runs $W/runs --out $W/score --seat-key $W/claims/key.jsonl`.
   The maintainer reads `adjudication_packet.md` and fills
   `adjudication_decisions.json` (keep each `text_sha256`); scoring again
   computes the headline once every decision has a verdict and a criterion id
   (V1-V3, R1-R5). Scoring also writes `execution_manifest.json` (completed
   calls of all three roles) and `call_attempts.json` (every attempt).
8. Publish a `heldout-measurement/1.1` report row in this directory, with the
   raw outputs, the execution manifest, and the adjudication record.

Plan version 10 adds a separate contrast test for the Claude session models
(`PREREGISTRATION.md`, Amendments). It reads nothing but the contrast batches
and changes no claim result:

1. Rebuild the batches with `--match-manifest` (step 3).
2. Probe each model once through the same fence, and stop if the answer names
   any instruction from the maintainer's own settings.
3. `run --judge <claude_opus|claude_fable> --replicate <1|2> --contrast-only --batches $W/batches --out $W/runs`.
   The token is read from `~/.config/ars-889/oauth_token` and goes only into the
   call's environment.
4. `contrast-score --batches $W/batches --runs $W/runs --judge claude_opus --judge claude_fable`.

## Boundaries

- No file under `../reviewer_seeded_defects/manifests/` is read, sent, or
  summarized. No script of this suite opens that directory.
- The judges see one manuscript and claim text with neutral ids, in hash
  order. The seat label, the condition, the panel decision, and other
  verdicts are left out. The claim text is the reviewer's own words, so it can
  still show the seat (a DA row has no title); the blinding is of metadata.
- The codex judge runs with `-s read-only` in an empty directory, and a reply
  whose turn holds a command, a file read, or another tool item is a transport
  failure. That check runs after the call, so a read the CLI allowed has
  already happened. The suite's threat model covers this repository's inputs
  only: the three synthetic manuscripts and the 805 claims that the reviewer
  panel wrote about them, and the build refuses any other inventory. Do not
  point the harness at a manuscript or claims from outside this repository.
- The transports run on POSIX systems only (tested on macOS). Each call runs in
  its own process group, which is killed when the call ends, so a child that
  a CLI leaves behind does not outlive the call; a child that starts its own
  session does.
- The spend cap counts a completed Gemini call at the usage the API reports,
  unless that usage is below one token per 16 bytes of prompt or reply; then
  the call counts at its worst case. A provider that under-reports above that
  floor can still let a run spend past the cap. Set a budget on the Google
  account as well.
- Every input path is resolved before it is read, and a path under
  `../reviewer_seeded_defects/manifests/` stops the script.
- The rate says how often panel claims contradict the manuscript under this
  rubric. It does not say whether a panel's decision was right, and it does
  not cover claims about the outside literature (`not_verifiable`).
- Frozen files: `plan.json`, `rubric.md`, `prompts/`, `PREREGISTRATION.md`,
  `scripts/extract_panel_claims.py`, and `scripts/dispatch_panel_claim_audit.py`;
  `build_manifest.json` binds the hashes of all of them. A change after the first judge call on a claim is a new version,
  logged as an amendment.
