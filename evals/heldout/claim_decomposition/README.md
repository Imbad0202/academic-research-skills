# Claim Decomposition Held-Out Set (#1128)

Seed only. Status, purpose, pass rule, adjudication, and the item contract are
the `heldout_set.json` fields (`status`, `purpose`, `scoring`,
`subject_visible_fields`, `hidden_fields`); this file carries only what the
JSON cannot.

- **Why held-out, not gold:** the subject is an LLM running
  `source_verification_agent.md`'s Claim Decomposition pass, so
  `scripts/run_evals.py` must not discover this directory and there is no
  `target.entrypoint`.
- **What the subject sees:** `user_claim` and `verified_source_set`
  only. `user_claim` is absent for cd-04 (no claim named at all); for
  cd-06 it holds a fact-check-mode prompt listing several claims, not
  one claim to decompose. `ground_truth` and `rule_anchor` are never
  shown.
- **Before any number is quoted:** file a `heldout-measurement/1.1` report per
  `evals/heldout/MEASUREMENT_CONTRACT.md` (registered class `llm_judged`).
- All content is synthetic: fictional programs, authors, trials, effect sizes.
