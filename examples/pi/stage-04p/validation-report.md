# Stage 4' Focused Re-Revision Validation Report

## Verdict

**PASS FOR SCHOLAR INSPECTION — FINAL INTEGRITY NOT STARTED**

The Stage 4' round modified only `B0031` for `REV-3P-001`. `REV-3P-002` remains an explicit limitation, and no search was rerun.

## Focused patch and apply

- Base: `00-anchored-pre-rerevision-base.md`
- Base SHA-256: `ac17240daedee845185f875d395e6e03aa7d44981ce99b1a52c61d6c5461f3b7`
- Patch: `phase6-round1/revision_patch_round1.json`
- Patch SHA-256: `ce9519ba434fed3fcc47158d4d11d84c25881eac962d16ce6b67747e9758e152`
- Applied output: `03-re-revised-course-paper-for-inspection.md`
- Output SHA-256: `513004b245efe8a557e92144faa8c06eb6bd95e16095d35a624d3d7d4870e40f`
- Apply report: `03-re-revised-course-paper-for-inspection.md.apply-report.json`
- Apply-report SHA-256: `800415dce2534ff33bf959a916d7211b468b1529abb754c7d651cf867398ed50`
- Ordered chain: `ac17240daede → 513004b245ef` — PASS.
- Patch-digest binding: PASS.
- Operations: 1 `replace_block` on `B0031`.
- Preserved blocks: 115/116 byte-identical (`preserved_ratio: 0.9914`).
- Structural flags: none; no structural acknowledgment and no full re-emission.

The first apply command under system Python stopped before validation because `jsonschema` was unavailable and wrote no output. The retry under the existing `<temporary-virtualenv>` completed successfully. This tooling recovery is recorded in `05-focused-patch-apply-record.json`.

## REV-3P-001 verification

The inserted clarification is limited to the frozen 96→16 selection stage:

1. The 96 closer-review clusters were assessed under the frozen direct-relevance and comparative-mechanism criteria.
2. A DOI suitable for identity/retrieval verification was required for the initial DOI core.
3. The exact 16-item list is named at `stage-01-research/phase2-search/core-dois.txt`.
4. The manuscript explicitly states that the 16-item core was a prioritized identity/retrieval set, not evidence that the other 80 clusters were nonexistent or all full-text excluded.
5. The original downstream accounting remains unchanged: 16 initial core + 2 citation-chased works = 18 identity-verified works = 9 full text + 2 abstract-only + 7 metadata-only.

Frozen-log witness check: PASS. No per-record decision ledger was newly created; the clarification reports the already-frozen rule surfaces and exact core list rather than pretending a new retrospective screen occurred.

## REV-3P-002 preservation

- `B0070`: byte-identical to the Stage 4' base.
- `B0116`: byte-identical to the Stage 4' base.
- Taiwan exit, regional-difference, and institutional-research coverage remain explicitly limited.
- No metadata-only or inaccessible record was upgraded to substantive evidence.

## Citation, data, and scope integrity

- Three-layer citation lint: PASS.
- Citation/ref/anchor stream: exactly unchanged; Cite-Time Provenance Finalizer was therefore a no-op.
- New references: 0.
- New searches: 0.
- Existing accounting values: preserved.
- Stage 3' frozen findings bundle SHA-256 remains `30387db1f64b0f3f22e016e5d22fbdc66c774d9c146022a9e5fb70822e3db5eb`.
- Empirical findings, table values, scope hedges, and causal-strength language were not modified.

## Token-conservation advisory

`ADV-REV-1` was emitted because the authorized clarification repeats the existing 96 and 16 values, states the implied remaining 80 clusters, and names a path containing `stage-01`. Citation and protected-hedge multisets are unchanged. This is non-blocking but must remain visible for inspection and the Stage 4.5 E6 claim-strength audit.

## Execution disclosure

The patch-writing and orchestration steps ran sequentially in the same `openai-codex/gpt-5.6-sol` Pi context after the disclosed transport recovery. There was no independent writer, evaluator, or context window. Deterministic apply guarantees untouched-block preservation; it does not establish cognitive independence or certify the substantive edit.

## Downstream status

Stage 4.5 final integrity has not started. On scholar confirmation, the patch, base, residual roadmap, apply report, response record, and Stage 3' traceability sidecar must travel together as the Revision-Evidence Bundle.
