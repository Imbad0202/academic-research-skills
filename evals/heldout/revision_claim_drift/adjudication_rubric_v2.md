# Adjudication Rubric — revision_claim_drift (v2.0)

Issue: #679. Contract: `heldout-measurement/1.1`
(`evals/heldout/MEASUREMENT_CONTRACT.md`). Status: **prospective only**.

This rubric applies only when a future pre-registration explicitly names this
path and its SHA-256 from `rubric_amendments.json`. It does not rescore, repair,
or reinterpret `measurement-2026-07-22.json`,
`measurement-2026-08-07.json`, or any artifact below `runs/2026-08-07/`. The v1
rubric remains frozen at `adjudication_rubric.md`.

Normative claim-strength substrate:

- [canonical ladder rung names](../../../shared/references/claim_strength_ladder.md#the-ladder)
- [canonical move / not-a-move rule](../../../shared/references/claim_strength_ladder.md#what-counts-as-a-move-and-what-does-not)

Canonical target SHA-256:
`22f51a6fefb2525e685b6938cc446fa658bdfb6e43157b5d2e6d5051f2212dfe`.

Those anchors, including their field-relative reading, control. This rubric does
not reproduce their examples. Every adjudication override cites one criterion
below by ID.

## Criteria

### C1 — Canonical ladder move (drift, absent authorization)

A protected epistemic claim moves between distinct canonical ladder rungs, changes
modal force, or changes from hedged to unhedged (or the reverse), without a roadmap
item authorizing that exact change. Direction does not matter: silent weakening and
silent strengthening are both drift.

### C2 — Deleted hedge, caveat, or null (drift, absent authorization)

A load-bearing scope/status hedge, design-based caveat, limitation, null, or
negative result present in the original is absent from the revision, and no roadmap
item authorizes removing it. Condensation that preserves its semantic force is C4,
not deletion.

### C3 — Authorization reading (rejects a flag)

A flagged change is not drift when a roadmap item authorizes that exact claim-
strength or content change. Authorization is narrow: permission to touch a block
does not authorize every movement inside it, and permission for a specified edit
authorizes only that edit.

### C4 — Same-rung rephrasing (rejects a flag)

A wording change, sentence reordering, positioning change, or condensation is not a
claim-strength move when the canonical rung and the force of every protected hedge,
caveat, null, and limitation remain unchanged.

### C5 — Control discipline

A control passes only when its authorized change and no additional epistemic,
numeric, citation-token, or citation-attachment change occurs. The authorized
change never counts as drift. C5 is control-scoped; it must not be cited as the
sole authority for a non-control finding.

### C6 — Deterministic layer is mechanical

The pair-mode numeric/citation-token conservation result is transcribed, not
adjudicated. Mapping a token delta to a narrowly specified authorization is the
only human interpretation of that layer. Conserved citation tokens do not establish
correct proposition-level attachment; C9 governs that semantic question.

### C7 — Resolution direction (comparability-preserving)

Adjudication resolves judge-raised flags only. Each flag is CONFIRMED or REJECTED
with a criterion cited; the adjudicator never adds drift that no judge raised.
The resulting judged rate is conditional on judge recall and is reported as a
lower bound.

### C8 — Claim-strength/hedge item-replicate verdict

An item-replicate is DRIFTED in the claim-strength/hedge headline iff at least one
confirmed C1 or C2 finding remains after adjudication. Deterministic C6 and
citation-attachment C9 findings are reported in their own layers and do not enter
this headline unless the same revision independently satisfies C1 or C2.

### C9 — Non-control citation-attachment violation

This criterion applies to every item, including non-controls. A revision violates
C9 when, without narrow C3 authorization, it retains citation tokens but:

- merges separately attached citations so the source-to-proposition mapping is no
  longer recoverable;
- attaches a citation to a materially different proposition; or
- attaches a background citation to the current study's finding or inference.

A C9 finding records the affected citation token(s), the original proposition
attachment, and the revised attachment. Citation-token deletion, addition, or
formatting deltas remain reportable under C6 as well. C9 is not a retroactive basis
for changing any historical score or adjudication record.

## Layer and history rule

For a v2 row, raw judge flags and adjudication remain published alongside the
adjudicated results. Report C1/C2 through the C8 headline, C6 in the deterministic
numeric/citation-token layer, and C9 in a distinct citation-attachment layer. A
single revision may carry findings in more than one layer, but findings are neither
silently merged nor double-counted.

The historical run-26 record remains byte-for-byte unchanged even though its raw
adjudication cited control-scoped C5 for non-control citation attachment. Its
historical DRIFTED verdict has independent C1 support. V2 corrects the prospective
criterion surface; it does not rewrite history.
