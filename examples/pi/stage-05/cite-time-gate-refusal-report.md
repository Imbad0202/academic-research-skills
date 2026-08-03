# Stage 5 Cite-Time Provenance Gate Report

## Result

**REFUSE — converted final artifacts were not emitted.**

This is a formatter hard-gate refusal, not a reversal of the Stage 4.5 factual-integrity PASS.

## Bound input

- Source: `stage-04.5-final-integrity/14-final-verified-course-paper.md`
- SHA-256: `513004b245efe8a557e92144faa8c06eb6bd95e16095d35a624d3d7d4870e40f`
- Entry hash check: PASS
- Source mutation: none

## Gate evidence

- Citation marker occurrences: 79 (58 body/table-note occurrences plus 21 reference-list markers)
- Unique cited sources: 21
- Paired non-`none` anchors: 79/79
- Anchor kind: section, 79/79
- Stage 4.5 reference identity/source adjudication: 21/21 VERIFIED
- Literal NO-ORIGINAL, NOT-CROSS-CHECKED, NO-LOCATOR, HIGH-WARN, or HIGH-BLOCK hits: 0
- Passport `literature_corpus[]`: absent because this run began before that aggregate was emitted
- Peer human-read log: absent
- Human reading inferred from inspection of the integrity report: **no**

The finalizer used the Stage 4.5 VERIFIED adjudication as the disclosed source-acquisition and AI/source-cross-check witness. It did not infer that the scholar personally read the original sources. Under the cite-time matrix, all 21 unique sources therefore resolve to `LOW-WARN` and all 79 marker occurrences remain unacknowledged. The formatter hard gate refuses conversion until the source-read state is resolved.

## Working artifact

A working copy was created only to demonstrate the deterministic gate result:

- `phase7-format/01-provenance-finalized-working-draft.md`
- SHA-256: `5cdbf1584ef261dd95dcb5f5365847161a04e643178b04fa5387448d09d2575d`
- Difference from verified source: citation-marker status tokens only (`LOW-WARN`); manuscript prose is not revised.
- Three-layer citation lint: PASS.

The verified Stage 4.5 source remains byte-identical.

## Required scholar action

The read-attestation checklist is:

- `phase7-format/02-human-read-attestation-checklist.tsv`
- SHA-256: `4bef368341d7e903389234a370b73e6b18e63a37e551353ff4ef2333459ca574`

It covers: `A1`–`A9`, `O1`, `O3`, `O4`, `O6`, `O7`, `O8`, and `U01`–`U06`.

For each source, the scholar may truthfully attest either:

1. `full_text`, or
2. `sections` with locators covering every listed section anchor.

Inspection of the integrity report, citation audit, or bibliography alone is not a source-read attestation. There is no “accept warning and bypass” option for this terminal formatter gate.

If the originals have not been personally reviewed, the safe action is to pause Stage 5 and review them. Removing or replacing citations would be a content revision and would require a new integrity pass before finalization.

## Other carried decisions

- APA 7 remains selected.
- All 12 token advisories are accepted.
- The compliance WARN remains an acknowledged reporting limitation and has not been inserted into the manuscript.
- No AI performance metric or independent-verification claim has been invented.
- The LaTeX question is deferred until this hard gate passes.
