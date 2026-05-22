---
description: ARS /ars-mark-read — record human-read signal for one or more citation keys
model: sonnet
---

Acknowledge that the user has personally read the source(s) backing the named citation key(s), so the next finalizer pass can promote `<!--ref:slug LOW-WARN-->` to `<!--ref:slug ok-->` for each acknowledged slug. Per v3.6.8 spec §3.6, the signal is stored in a session-scoped peer file `<passport-stem>_human_read_log.yaml` next to the active Material Passport; `literature_corpus[]` is adapter-owned and is NEVER mutated to carry `human_read_source`.

Implementation:
```bash
python3 scripts/ars_mark_read.py $ARGUMENTS --passport-path "$ARS_ACTIVE_PASSPORT"

Mode reference: `docs/design/2026-04-30-ars-v3.6.8-trust-provenance-and-drift-transparency-spec.md` §3.6 + Step 7.
