# Panel Claim Factuality Rubric (v2, #1002)

This rubric is frozen before any judge output exists. A change after the first
judge call is a new rubric version with a new hash, logged in the run notes.

A **claim** is one weakness (`### W<n>`) of the EIC, Methodology, Domain, or
Perspective seat, or one row of the Devil's Advocate CRITICAL or MAJOR table, as
`scripts/extract_panel_claims.py` writes it. The judge reads the claim and the
reviewed manuscript only. It never sees the seat, the panel decision, other
claims' verdicts, or any held-out manifest.

## Verdicts

Each claim gets exactly one verdict.

- **V1 `false`**: the manuscript text positively contradicts at least one
  factual statement the claim makes about the manuscript. The evidence is one
  of two kinds:
  - `contradiction`: the judge quotes the contradicting manuscript passage
    verbatim (at most 40 words) and names where it is. Examples: the claim
    says a section never reports attrition, and the section reports it; the
    claim says a table gives n = 120, and the table gives n = 102.
  - `absent_quotation`: the claim presents words as a quotation of the
    manuscript, and the manuscript contains no such words. The judge copies the
    quoted words from the claim.

  The scorer checks the evidence mechanically: a `contradiction` quote must
  appear in the manuscript, and an `absent_quotation` quote must appear in the
  claim and not in the manuscript (whitespace and quotation marks normalized).
  A `false` whose evidence fails the check is not counted as agreed and goes to
  adjudication.
- **V2 `true`**: every factual statement the claim makes about the manuscript
  is supported by the manuscript text. A claim whose only factual statement is
  a verbatim quotation the manuscript contains, plus a judgment, is `true` for
  the quotation.
- **V3 `not_verifiable`**: the claim's factual statements cannot be checked
  against the manuscript text alone (they concern the outside literature,
  field norms, or the authors' intent), or the claim is only a judgment
  (importance, adequacy, clarity) with no checkable factual premise.

Precedence: a factual statement that the judge can show to be contradicted, by
one of the two evidence kinds, makes the claim `false`, even when the claim's
other statements are judgments or cannot be checked. Only when no statement is
shown to be contradicted: if every factual statement is supported, `true`;
otherwise `not_verifiable`. When the judge is unsure whether a passage
contradicts the claim, the verdict is `not_verifiable`. Disagreement with a
judgment, or a low-importance claim, is never `false`.

## Rules for hard cases

- **R1 Multi-part claims.** One contradicted factual statement makes the claim
  `false`, even when the rest is supported, judged, or not checkable. Example:
  a weakness says the paper does not report attrition (the paper reports it in
  §3) and that the design falls short of field norms: `false`, by the attrition
  statement.
- **R2 Absence claims.** "The paper does not report X" is `false` only when the
  judge can quote where the manuscript reports X. Reporting something close to
  X is not a contradiction.
- **R3 Internal inconsistency.** When the manuscript states two different values
  for one quantity, a claim that reports the inconsistency is `true`; a claim
  that states only one of the values as the manuscript's value is `true` for
  that value and does not become `false` because the other value exists.
- **R4 Computations.** A claim that states a value or result the manuscript
  reports (a mean, a reliability, a power statement, a test result) differently
  from the manuscript is `false` under V1, with the manuscript passage quoted.
  R4 covers only a claim that recomputes a statistic from the manuscript's
  inputs: such a claim is `false` only when it misstates those inputs, and a
  disputed arithmetic result with correct inputs is `not_verifiable` in this
  rubric (the E4 receipt checker covers arithmetic). (v2: the first sentence is
  new; see the amendment in `PREREGISTRATION.md`.)
- **R5 Locators and quotations.** A wrong section or table number in an
  Evidence Anchor, when the quoted text exists elsewhere in the manuscript,
  does not make the claim `false`. A quotation that exists nowhere in the
  manuscript makes it `false`, with `absent_quotation` evidence. A close
  paraphrase marked as a quotation is still `absent_quotation`; the
  adjudicator may overrule the mechanical check when only punctuation or a
  typographic variant differs, citing R5.

## Severity

Each claim also gets a severity for the issue it raises, judged independently
of its verdict: `cosmetic`, `minor`, `major`, or `fundamental`. Severity is
recorded for analysis and never changes a verdict.

## Agreement, instability, and adjudication

For the headline each judge's verdict on a claim reduces to one flag: `is_false`
is true when both replicates say `false` with evidence that passes the
mechanical check, false when neither replicate says `false`, and unresolved
otherwise (the replicates differ on `false`, or a `false` fails the check). A
`true` against `not_verifiable` difference does not change the flag; both
verdicts publish in the raw outputs.

Each claim falls in exactly one list:

- **agreed false**: both valid judges flag it true; counted false.
- **agreed not false**: both valid judges flag it false; counted not false.
- **cross-judge divergence**: both judges' flags are resolved and differ.
- **replicate instability**: at least one judge's flag is unresolved.
- **missing**: a judge has no readable verdict for it in a replicate.

Claims in the last three lists go to the maintainer, who applies V1 to V3 and
R1 to R5 and records one verdict and the criterion id per claim. The sheet
hides the subject model, the judge identity, and the condition (the contract's
`subject_model`, `judge_identity`, and `condition`), and also the seat, which
the contract enum does not name and the report states separately. Resolution
direction is `bidirectional`: the maintainer can move a claim to or from
`false`. Raw per-judge verdicts publish beside the adjudicated ones.
