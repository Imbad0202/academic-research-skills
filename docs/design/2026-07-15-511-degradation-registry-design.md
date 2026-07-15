# #511 Part A — Machine-readable degradation registry (native outcome semantics, no score caps)

- **Date:** 2026-07-15
- **Issue:** #511 (Part A; Part B — the transport-fixture citation-gate test — shipped separately in #533)
- **Status:** implemented in this PR

## Problem

ARS's graceful-degradation handling is individually sound but scattered: five
mechanisms (citation resolver outage, contamination-signal API degradation,
VLM absence, submission-package incompleteness, cross-model absence) each emit
a well-defined degraded state, but no single auditable inventory says what
degrades, into what state, visible where, consumed by whom, with what
terminal-policy effect. One live weakness: a contamination-signal omission
caused by API degradation was structurally indistinguishable from
"never computed" — the omission carried no reason.

## Design

### Registry (`shared/contracts/degradation_registry.json`)

One JSON file, six rows (the five issue mechanisms + the non-SR compliance
warn-cap, the one legitimate severity-cap because compliance already has a
native block>warn>info scale). Per row:

| field | meaning |
|---|---|
| `mechanism` | stable id |
| `failure_class` | what fails |
| `degraded_state` | the NATIVE degraded outcome (unresolvable / not_checked / PASS WITH NOTES / omit-field / warn-and-continue) |
| `diagnostic_marker` | where the degradation is visible |
| `downstream_consumer` | who reads the degraded state |
| `terminal_policy_effect` | how the policy layer treats it |
| `authority[]` | `{file, anchor}` — the per-mechanism source of truth |
| `pinned_by[]` | tests / lints / schemas pinning the behavior (`path` or `path::test_function`) |

**Index, never re-author.** Semantics live in each row's authority file; the
registry only cites them. Anchors are verbatim content strings (≥16 chars),
never line numbers — the issue itself cited line numbers that had already
drifted by implementation time, which is the demonstration case.

**No score caps.** The inspiring mechanism (a peer orchestrator's
`runtime-fallbacks.md`) caps numeric quality scores on degradation. ARS's gate
model is tri-state outcomes + advisory suffixes + opt-in terminal policies —
a universal cap column would be a category error (#511 "Explicitly rejected").

### Lint (`scripts/check_degradation_registry.py`)

Four invariant families, fail-closed: D1 shape (parse, required fields,
non-empty values), D2 unique ids, D3 authority files exist + anchors resolve
verbatim + no `:<line>` refs + min anchor length, D4 pinned files exist +
cited test functions defined. Wired into spec-consistency.yml + the unified
pytest manifest; 25 mutation tests (one failing witness per branch).

### Reason-provenance (`contamination_signal_omissions`)

New optional entry-level object in `literature_corpus_entry.schema.json`:
per-omitted-signal reason, closed enum `api_degraded` ONLY. Derivable
omissions are deliberately not recordable (manual exemption ←
`obtained_via='manual'`; arXiv skip ← absent `arxiv_id`) — recording them
would create a second driftable copy of facts the entry already carries.
Guard rails (allOf): forbidden on manual entries (mirrors the *_unmatched
not-rule), per-key mutual exclusion with `contamination_signals` (computed XOR
omitted-with-reason), `arxiv_unmatched` omission requires `arxiv_id`.
Writers: `bibliography_agent` (ingest; emission paragraph added — sha256
baseline in `check_v3_9_4_temporal_verification.py` updated per its built-in
procedure) and the `contamination_signals.py` module docstring carries the
caller contract for backfill tools. Additive; no migration; R-L3-2-C k/k_max
counting is unchanged (reads signal presence, never this object).

## Rejected alternatives

- **Line-number authority refs** — drift silently; content anchors fail loudly.
- **Recording manual/no-arxiv-id omission reasons** — derivable duplicates.
- **A universal degradation severity/cap column** — category error (see above).
- **Registry as markdown** — not machine-checkable without a parser layer;
  JSON + lint keeps the pin mechanical.
