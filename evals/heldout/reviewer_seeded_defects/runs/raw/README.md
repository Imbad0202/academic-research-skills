# Raw panel outputs (audit evidence for the run records)

One file per run, named `<run-record-stem>.review.md`: the complete output of that
run's blinded full-mode panel under the ISOLATED dispatch design — the field-analyst
report, then for each of the five seats the Phase 1 pre-commitment (produced by a
physically separate, paper-blind call that received only the contract +
title/field/word_count and was forbidden from reading any manuscript) and the Phase 2
paper-visible review, then the editorial synthesis. These files are the evidence base
that makes the sibling `../*.json` records re-adjudicable: DETECTED/PARTIAL calls can
be re-classified from the full text, severity can be recomputed from the seats' own
tags, and the clean-control zero-false-findings claim can be verified only against
the complete reports.

**Fidelity note:** these files are verbatim subagent output (no redaction was needed
this round; the repo-boundary deny-list scan came back clean). The
`superseded/2026-07-24-in-context-dispatch/` directory holds the earlier
single-context attempt these runs replace.

**Voided artifacts:** `voided/` holds any synthesis output voided under the protocol
§8.1 grammar rule, preserved verbatim; the operative retried synthesis lives in the
parent run file's PART 3 with a provenance note.

**Contamination reminder:** these are *outputs* of past measurement runs, not ground
truth — but they live under `evals/`, which review sessions are already forbidden to
read under the measurement protocol. Never paste them into a review session's context.
