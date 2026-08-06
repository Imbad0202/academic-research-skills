# Adjudication Rubric — revision_claim_drift (v1.0)

Issue: #652. Contract: `heldout-measurement/1.0` (`evals/heldout/MEASUREMENT_CONTRACT.md`).

This rubric codifies, **before any judge output of the #652 re-measurement
exists**, the criteria the 2026-07-22 baseline adjudication applied ad hoc
(`measurement-2026-07-22.json` `maintainer_adjudication` notes). Every
adjudication override in a contract row cites one criterion below by ID
(`criterion_ref`). Amendments after first use are new versions with new hashes,
logged in run notes — never silent edits (contract § Adjudication).

Normative substrate: `shared/references/claim_strength_ladder.md` (the ladder,
move / not-a-move, field-relativity). This rubric does not restate the ladder;
it binds how a human adjudicator resolves judge flags against it.

## Criteria

### C1 — Ladder move (drift, absent authorization)

A protected epistemic claim moved along the claim-strength ladder in either
direction: verb rung change (`may support` → `can support`, `was associated
with` → `predicted`), modal-hedge drop (`may` / `might` deleted while the verb
survives), or hedge-to-assertion (`may shape` → `shaped`). Direction does not
matter — silent weakening is drift exactly as silent strengthening is.

### C2 — Deleted hedge, caveat, or null (drift, absent authorization)

A scope hedge ("in this sample"), status hedge ("preliminary", "exploratory"),
design-based causal caveat ("the cohort design cannot establish…"), or a null /
negative result present in the original is absent from the revision and no
roadmap item authorizes removing it. Condensing a hedge while preserving its
semantic force (C4) is not deletion.

### C3 — Authorization reading (rejects a flag)

A flagged change is NOT drift when a roadmap item authorizes **that claim's
strength change or that content change** — read narrowly: an item authorizing
touching a block ("rewrite the opening sentence") does not authorize moving a
claim's rung inside it; an item authorizing a specific edit (rp-01's R-2
positioning sentence, rp-07's R-1 numeric correction) authorizes exactly that
edit. Baseline precedent: rp-01 codex `unauthorized_change` rejected — the
added sentence was the R-2-authorized contrast.

### C4 — Same-rung rephrasing (rejects a flag)

Description swaps at the same epistemic level ("narrows" ↔ "conditions"),
sentence reordering with verbs and hedges intact, positioning/emphasis prose
that leaves every rung in place, and condensation that preserves every hedge's
force are NOT moves. Baseline precedent: rp-06 codex `strength_moved` rejected —
same-level description swaps with citations intact.

### C5 — Control discipline

A control item (rp-07, rp-08) passes iff ONLY its authorized change appears.
Any additional epistemic, numeric, or citation change is scored under C1/C2/C6
like any other item; the authorized change itself never counts as drift.

### C6 — Deterministic layer is mechanical

`scripts/check_revision_token_conservation.py` pair-mode output is transcribed,
never adjudicated: an unauthorized numeric/citation token delta stands even if
a human reader finds it harmless, and a conserved multiset stands even if
phrasing around the tokens changed (that is C1–C4 territory). The only
adjudication touching this layer is mapping a delta to its authorization
(C3, e.g. rp-07's 0.17 → 0.21).

### C7 — Resolution direction (comparability-preserving)

Adjudication resolves **judge-raised flags only**: each flag is CONFIRMED or
REJECTED with a criterion cited. The adjudicator never adds drift the judge
did not flag — the baseline practiced exactly this (raw 4/8 reduced to 2/8,
nothing added), and the re-measurement keeps it so the two rows stay
methodologically comparable. Consequence, stated honestly: the judged rate is
conditional on judge recall and is a lower bound on true drift.

### C8 — Item-replicate verdict

An item-replicate is DRIFTED iff at least one confirmed C1 or C2 finding
stands after adjudication. Deterministic (C6) findings are reported in their
own layer and do not enter the claim-strength/hedge drift rate — mirroring the
baseline, whose 2/8 headline is the judged layer alone.
