# Per-Source Method Weaknesses Held-Out Set (#916)

Seed only. Status, purpose, pass rule, adjudication, and the item contract are
the `heldout_set.json` fields (`status`, `purpose`, `scoring`,
`subject_visible_fields`, `hidden_fields`); this file carries only what the
JSON cannot.

- **Why held-out, not gold:** the subject is an LLM writing an
  annotated-bibliography entry under `deep-research/agents/bibliography_agent.md`
  Step 5, so `scripts/run_evals.py` must not discover this directory and there
  is no `target.entrypoint`.
- **What the subject sees:** `subject_task`, `read_scope`, and `source_text`
  only. `ground_truth` and `rule_anchor` are never shown.
- **What the two items test:** mw-01 addresses attrition in a named section
  (4.3), so a "does not address attrition" claim is a fail. mw-02 supplies an
  abstract only, so any inferred method weakness is a fail.
- **Before any result is quoted:** file a `heldout-measurement/1.1` report per
  `evals/heldout/MEASUREMENT_CONTRACT.md` (registered class `llm_judged`).
- All content is synthetic: fictional universities, colleges, authors, and
  journals.
