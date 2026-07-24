# Superseded: 2026-07-24 in-context-dispatch baseline attempt

These six run records (+ raw outputs under `raw/`) are the first baseline attempt,
executed as ONE subagent per review simulating the whole panel in a single context.
They are preserved for the audit trail but are NOT the operative baseline: the
cross-model review of the attempt showed that single-context simulation cannot
deliver the sprint contract's load-bearing mechanism ("physical separation of
calls: Phase 1 never sees paper content", `sprint_contract_protocol.md` §1), and
the leak was observable — several Phase-1 "paper-blind" scoring plans pre-registered
manuscript-specific facts. The maintainer re-ran the full baseline the same day with
physically separated per-seat Phase 1 / Phase 2 calls; the operative records live in
the parent `runs/` directory.

Comparative note (why these are still informative): the isolated re-run reproduced
the in-context attempt's headline numbers almost exactly (MS01 strict recall 0.90 in
both designs with the same sole GRIM miss; clean-control false findings 0 in both;
severity agreement 0.625 operative vs 0.599 superseded) — evidence that the Phase-1 blindness leak was
not inflating recall, and that the measurand is robust to this dispatch difference.
The one substantive divergence: the in-context MS02-r1 panel only PARTIALLY caught
the undescribed-interview-instrument defect, while both isolated MS02 panels named
the absent protocol explicitly.
