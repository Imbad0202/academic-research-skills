---
name: ars-mark-read
description: ARS /ars-mark-read — record a user-attested reading signal for one or more citation keys
model: sonnet
---

Record the user's `USER_ATTESTED_READ` declaration for the source(s) backing the named citation key(s). This is a user statement, not independent evidence that a person read or understood the source. A finalizer may promote `<!--ref:slug LOW-WARN-->` to `<!--ref:slug ok-->` only when the declared scope covers that citation's anchor. Per v3.6.8 spec §3.6, the signal is stored in a session-scoped peer file `<passport-stem>_human_read_log.yaml` next to the active Material Passport; `literature_corpus[]` is adapter-owned and is NEVER mutated to carry reading state.

The dispatching agent substitutes `<path>` below with the active Material Passport path from session context before executing (the quoting is preserved so paths containing spaces remain a single argument). The CLI handles validation (citation_key must exist in `literature_corpus[]`; on miss emit `[ARS-MARK-READ ERROR: citation_key '<slug>' not in literature_corpus[]]` and refuse to write), 4 fail-fast environment checks (no active passport / passport not found / parent unreadable / read-log unwritable), and append-only write per §3.6 firm rule 3.

Read scope is required for every new mark (#738; declaration-only — pass through whatever the user states, never infer): `--scope {full_text,sections,abstract_only,toc_only,unknown}` records the declared coverage; `--locator "<text>"` (repeatable, requires `--scope sections`) names the read sections/pages; `--note "<text>"` free text (requires `--scope`). Use `--scope unknown` when the user cannot specify coverage. Missing scope is accepted only in legacy ledger records. Explicit `unknown` and legacy missing scope remain `coverage_unknown`; they acknowledge the declaration but can never promote an anchored citation to `ok`. Page coverage requires an explicit `page`, `p.`, or `pp.` locator—bare numbers and `section <n>` never count as page ranges. The deterministic resolver in `scripts/human_read_attestation_resolver.py` strictly validates the current ledger and computes a transient routing decision on every finalizer pass; its output is not a persisted audit receipt.

Implementation:
```bash
python3 scripts/ars_mark_read.py $ARGUMENTS --passport-path "<path>"
```

Mode reference: `docs/design/2026-04-30-ars-v3.6.8-trust-provenance-and-drift-transparency-spec.md` §3.6 + Step 7.
