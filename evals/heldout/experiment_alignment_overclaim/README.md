# Experiment-Alignment Overclaim Held-Out Set (#915)

Seed only. Status, purpose, pass rule, and the item contract are the
`heldout_set.json` fields (`status`, `purpose`, `scoring`,
`subject_visible_fields`, `hidden_fields`); this file carries only what the
JSON cannot.

- **Source:** the DynaSpec-RAG showcase manuscript in ScientistTwo (Nam et al.,
  2026, arXiv:2609.19644 v1, Appendix D). The PDF is not vendored. Passports
  hold short quotes, numbers, and arXiv v1 page references only.
- **Why held-out, not gold:** the subject is an LLM running
  `integrity_verification_agent.md` section C4, so `scripts/run_evals.py` must
  not discover this directory and there is no `target.entrypoint`.
- **What the subject sees:** the passport file and `manuscript_locators`.
  `ground_truth` and `rule_anchor` are never shown.
- **Why this is not `cross_document_consistency`:** that suite compares two
  documents. Here one manuscript's claims are checked against its own tables.
- **Controls:** each passport carries one supported claim (st2-01 C-003,
  st2-02 C-002). A subject that marks every claim OVERSTATED fails them.
- **Before any result is quoted:** file a `heldout-measurement/1.1` report per
  `evals/heldout/MEASUREMENT_CONTRACT.md` (registered class `mechanical_match`).
  Two cases from one paper are a smoke check, not a detection rate.
