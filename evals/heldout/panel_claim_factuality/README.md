# Panel claim factuality (#1002)

How often does a weakness that the review panel states about a manuscript
contradict the manuscript itself? This suite measures that rate on the panels
the E4 suite already ran (`../reviewer_seeded_defects/runs/`), before ARS adds
any check for it. It is the first part of #1002; the second part, a check
between the panel and the editorial synthesizer, is planned only when the
decision rule in `plan.json` says so.

Suite class: `llm_judged` (`../suite_registry.json`). Status: `NOT_RUN`.

## What is measured

- **Claims**: 805, from the 17 score-eligible E4 bundles: each `### W<n>`
  weakness of the EIC, Methodology, Domain, and Perspective seats, and each
  Devil's Advocate CRITICAL and MAJOR row. Strengths are out of scope.
  `scripts/extract_panel_claims.py` writes them with the seat held back.
- **Verdicts**: `true`, `false`, or `not_verifiable` per `rubric.md`. Only a
  claim that the manuscript text positively contradicts is `false`.
- **Judges**: two model families (`gpt-6-astra` through codex,
  `gemini-4-argon-high` through agy), each reading every batch twice.
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
  `adjudication_decisions.json`, which scoring never overwrites.

## Steps

All commands run from the repository root; `$W` is a work directory outside the
repository. Raw outputs are written once and never overwritten.

1. Extract the claims (free); a count other than 17 bundles and 805 claims,
   or any extraction problem, exits 1:
   `python3 scripts/extract_panel_claims.py --runs evals/heldout/reviewer_seeded_defects/runs --out $W/claims --expect-bundles 17 --expect-claims 805`
2. Generate, check, and verify the contrast pairs, per manuscript:
   `python3 scripts/dispatch_panel_claim_audit.py generate --fixture ms00_clean --out $W/pairs`
   (and `ms01_quant`, `ms02_qual`), then `check-pairs` on the three
   `*.pairs.jsonl` files joined into one, then `verify-pairs`.
3. Build the batches (free) into a new directory. The build checks the claim
   inventory and the accepted pairs against `plan.json` and refuses anything
   else; it writes `build_manifest.json`, and every later step stops if an
   input changed since:
   `python3 scripts/dispatch_panel_claim_audit.py build --claims $W/claims/claims.jsonl --pairs $W/pairs/accepted_pairs.jsonl --out $W/batches`
4. Pilot: three batches per judge, replicate 1, with
   `run --judge <codex|gemini> --replicate 1 --batches $W/batches --out $W/runs --limit 3`.
   A run stops at the first transport failure, or at an output still
   unreadable after one retry. Report time and usage; the maintainer approves
   the full run.
5. Full run: both judges, replicates 1 and 2.
6. Score: `score --batches $W/batches --runs $W/runs --out $W/score --seat-key $W/claims/key.jsonl`.
   The maintainer reads `adjudication_packet.md` and fills
   `adjudication_decisions.json`; scoring again computes the headline once
   every decision has a verdict and a criterion.
7. Publish a `heldout-measurement/1.1` report row in this directory, with the
   raw outputs, the execution manifest, and the adjudication record.

## Boundaries

- No file under `../reviewer_seeded_defects/manifests/` is read, sent, or
  summarized. No script of this suite opens that directory.
- The judges see one manuscript and claim text with neutral ids, in hash
  order. The seat label, the condition, the panel decision, and other
  verdicts are left out. The claim text is the reviewer's own words, so it can
  still show the seat (a DA row has no title); the blinding is of metadata.
- Every input path is resolved before it is read, and a path under
  `../reviewer_seeded_defects/manifests/` stops the script.
- The rate says how often panel claims contradict the manuscript under this
  rubric. It does not say whether a panel's decision was right, and it does
  not cover claims about the outside literature (`not_verifiable`).
- Frozen files: `plan.json`, `rubric.md`, `prompts/`, `PREREGISTRATION.md`,
  `scripts/extract_panel_claims.py`, and `scripts/dispatch_panel_claim_audit.py`;
  `build_manifest.json` binds the hashes of the files that shape a prompt or a
  score. A change after the first judge call on a claim is a new version,
  logged as an amendment.
