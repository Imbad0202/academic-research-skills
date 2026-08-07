# Reviewer-Calibration Adjudication Rubric (#653) — v1

Pre-registered BEFORE any judge output exists (#654 R1: this file's sha256 is
pinned in every measurement row as `rubric_sha256`; amendments are new
versions with new hashes, logged in run notes, never silent edits).

Two element classes are judged or adjudicated in this suite. The headline
FNR/FPR/balanced-accuracy computation is mechanical (closed-grammar decision
extraction + fixed binarization + majority vote, `scripts/score_calibration_run.py`)
and is NOT subject to adjudication; only the elements below are.

## A — Verdict transcription (when the closed grammar fails)

The extraction grammar accepts exactly one `##`/`###`/`####` heading line
`Decision: <Accept|Minor Revision|Major Revision|Reject>` (brackets optional).
A synthesis text that yields zero or multiple distinct values goes to
adjudication:

- **A1 — nonstandard but unambiguous.** The synthesis states exactly one
  final editorial decision from the closed four-value set, in a nonstandard
  format (prose, bold line, decision letter body). Transcribe it verbatim
  into the overrides file with the raw excerpt. Never infer a decision from
  tone, score values, or weakness counts.
- **A2 — no decision statement.** The synthesis contains no final decision
  from the closed set. The panel is incomplete: re-dispatch the SYNTHESIS
  CALL ONLY (fresh context, same five frozen seat reports, same cards) once,
  and record the re-dispatch in the run notes. If the re-dispatch also yields
  no decision, the replicate is blocked and the whole paper's ensemble is
  incomplete — the paper cannot enter the aggregate (no partial ensembles).
- **A3 — multiple distinct decisions.** If one of them is in the Editorial
  Decision Letter's own `Decision` section and the others are quotations or
  hypotheticals, A1-transcribe the letter's value with the excerpt. If two
  places both claim to be the final decision, treat as A2.

Adjudicator blinding for class A: the adjudicator reads ONLY the synthesis
text — never the gold label, never the manifest venue partition
(`blinded_to: [expected_label]` at minimum; declare honestly what was seen).

## B — Severity-miscalibration risk classification (Phase 3.5)

Unit: each distinct weakness/finding emitted by the five seats across the
gold runs. Classes (calibration protocol Phase 3.5, W1 / §F.3.4 anchors in
`evals/gold/field_norm_severity/`):

- **B1 — `high`.** The finding's asserted severity rests on a field norm or
  the "would addressing this change the core result?" formula, AND the seat
  asserted that severity without grounding the norm in an external checkable
  source (named venue policy, named methods literature, named reporting
  standard with enough identity to check).
- **B2 — `med`.** Severity depends on a field norm and the seat gave partial
  grounding: a standard is named but its applicability to this subfield or
  this manuscript is not established.
- **B3 — `low`.** Severity does not depend on a field norm, OR the norm is
  grounded in an external checkable source.
- **B4 — grounding, not correctness.** The judge classifies whether the seat
  SUPPLIED external grounding, never whether the seat's norm is factually
  right. A judge output that argues norm-correctness from its own knowledge
  is itself the W1 failure shape and is discarded as invalid, with the
  discard logged.

Judge divergence (the two judges assign different classes to the same
weakness): the maintainer adjudicates by applying B1-B3 to the seat's text,
records the chosen class with `criterion_ref` (B1/B2/B3), the judges' raw
values, and a one-sentence rationale. Gold labels are irrelevant to class B
and are not consulted (`blinded_to` still lists what applies).

## Tie and construction rules referenced by the measurement row

- Headline metric construction: majority vote over 3 replicates on the
  BINARIZED side (odd replicate count — no tie exists); exact-decision mode
  reported descriptively, three-way splits printed as `no_exact_mode`, never
  resolved.
- Judge ties in class B always escalate to adjudication — never
  majority-of-two, never averaging.
