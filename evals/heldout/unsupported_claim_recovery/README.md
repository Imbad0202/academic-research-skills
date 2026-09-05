# Unsupported / Contradicted-Claim Recovery Held-Out Set (#825)

Seed only. Status, purpose, pass rule, adjudication, and the item contract are
the `heldout_set.json` fields (`status`, `purpose`, `scoring`,
`subject_visible_fields`, `hidden_fields`); this file carries only what the
JSON cannot.

- **Why held-out, not gold:** the subject is an LLM running the
  `draft_writer_agent.md` self-review step, so `scripts/run_evals.py` must not
  discover this directory and there is no `target.entrypoint`.
- **What the subject sees:** `draft_passage` + `annotated_bibliography` only.
  `ground_truth` and `rule_anchor` are never shown; the `fail_patterns` there
  name the hedge-only rescue the pre-#825 rule authorized, and uc-03 / uc-04
  are over-correction controls.
- **Before any number is quoted:** file a `heldout-measurement/1.1` report per
  `evals/heldout/MEASUREMENT_CONTRACT.md` (registered class `llm_judged`).
- All content is synthetic: fictional agencies, authors, trials, effect sizes.
