# Blocked panel evidence: 2026-07-27 MS00 post r2

This directory preserves the durable output that existed when the panel stopped.
It is not a complete review and must not be adjudicated or included in gate means.

The perspective model call emitted a `## Scoring Plan Dissent` heading without the
required canonical `dimension_id:` line. `perspective.conformance.log` records the
fail-loud diagnostic. The dispatch then exited before the Devil's Advocate seat and
before synthesis, as shown by `dispatch.log` and `dispatch.stderr`.

Preserved artifacts are:

- the sprint contract, metadata, and field analysis;
- the final conforming Phase 1 and completed Phase 2 outputs for EIC,
  methodology, and domain, with their layer-1 and conformance logs;
- the final conforming Perspective Phase 1, the malformed Perspective Phase 2,
  and its conformance log; and
- the dispatch chronology and terminal traceback.

The methodology and perspective Phase 1 calls each used the protocol-permitted
single structural retry. The runner overwrote each first malformed Phase 1 response
before this bundle was assembled; their exact checker diagnostics remain in
`dispatch.log` and the final conforming retries are preserved here. No Phase 2 retry
or replacement panel was run.

The machine-readable status record is
`../../../blocked/2026-07-27-ms00_clean-post-r2.json`.
