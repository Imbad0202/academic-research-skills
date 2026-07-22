# Claim-Strength Ladder

**Issue:** #569. **External motivation:** DELEGATE-52 (arXiv:2604.15597) — round-trip
document editing corrupts scientific content by *subtle modification, not deletion*.
#390's block-anchored patch confines that exposure to touched blocks; this reference
governs the epistemic dimension *inside* a touched block, which the patch mechanism
does not check. Mechanism shape borrowed from
[Yila-AI/sci-ssci-skills](https://github.com/Yila-AI/sci-ssci-skills) by
@MissOrangePeel (`sci-ssci-polishing`, `references/invariants.md`).

**Epistemic status:** advisory / interpretive guidance for revision surfaces. It
does NOT gate, does NOT block, and makes no runtime-enforcement claim. Detection is
a judgment the revising agent and the integrity gate perform; there is no script
that verifies claim strength (the deterministic sibling, `#570`, conserves only
numbers and citation tokens — see `scripts/check_revision_token_conservation.py`).

## The ladder

Epistemic claims sit on an ordered strength scale. Revision must never move a claim
along it **silently** — in either direction — without an authorizing roadmap item.

```
is consistent with / may suggest
  < is associated with / relates to / correlates with
    < predicts
      < contributes to
        < affects / influences / leads to / shapes
          < causes / determines / demonstrates that / proves
```

The exact ordering varies by field (a clinical "predicts" and an econometric
"predicts" are not identical), so the operative rule is **"no silent move,"** not
one universal ordering. When unsure whether two phrasings occupy the same rung,
treat them as different rungs and preserve the source.

## What counts as a move (and what does not)

A **move** — requires authorization:

- `associated with` → `leads to` / `reduces` / `drives` / `causes` (up)
- `may support` / `might improve` → `supports` / `improves` (drop of a modal hedge = up)
- `predicts` → `is associated with` (down — silently *weakening* misrepresents the
  author just as much as strengthening; bidirectional by design)
- deleting a design-based causal caveat ("the observational design cannot establish
  causation"), a scope hedge ("in this sample", "for this cohort"), a status hedge
  ("preliminary", "exploratory"), or a null/negative result
- re-attaching a background citation's claim to the current study's finding

NOT a move — no authorization needed:

- reordering a sentence while keeping the same verb and hedges
- foregrounding / positioning prose that adds emphasis WITHOUT changing the verb's
  rung (e.g. stating the contribution is important, while the finding stays
  "associated with")
- a description swap at the same rung ("narrows the range" ↔ "reduces the range")
- condensing prose that preserves every hedge and every claim's rung

## Load-bearing overlap with existing protections

- **Hedges.** `shared/references/protected_hedging_phrases.md` protects hedges
  against *compression* in abstract-only mode. The ladder extends the same concern
  to *revision rounds* and adds the ordered scale that the phrase roster lacks. A
  phrase already on a paper's `protected_hedges` list is a ladder invariant too.
- **Novelty.** #548 bounds *priority* language ("first study to…"); the ladder
  governs *causal/evidential* strength. Disjoint concerns, same anti-overclaim family.
- **Numbers/citations.** #570 conserves numeric and citation *tokens*
  deterministically; the ladder covers what token-matching cannot see (negation,
  direction, modality, causal strength). The two are necessary-but-not-sufficient
  complements, mirroring the v3.11 deterministic-gate / LLM-semantic split.

## Where this is consumed

- `draft_writer_agent` § Claim-Strength Ladder (#569) — revision mode: a patch op
  touching a claim-bearing block records whether claim strength moved and, if so,
  which `roadmap_item_ids` authorized it.
- Stage 4.5 integrity audit — the audit vocabulary names the drift class so a
  reviewer/gate can flag it; advisory rows only, never terminal.

## Measurement

The acceptance test for any change to this guidance is
`evals/heldout/revision_claim_drift/`. The 2026-07-22 baseline measured 2/8 = 25%
claim-strength/hedge drift on the current frontier model under hedge-drop and
null-reframe pressure — the evidence that this mechanism earns its place rather
than closing as documented-negative-scope. Model- and time-specific; re-run, don't
reuse.
