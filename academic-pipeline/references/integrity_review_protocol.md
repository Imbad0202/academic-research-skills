# Integrity Review Protocol (Added in v2.0)

## Stage 2.5: First Integrity Check (Pre-Review Integrity)

**Trigger**: After Stage 2 (WRITE) completion, before Stage 3 (REVIEW)
**Purpose**: Ensure all references and data are not fabricated or erroneous before submission for review

```
Execution steps:
1. integrity_verification_agent executes Mode 1 (initial verification) on the paper
2. Verification scope:
   - Phase A: 100% reference existence + bibliographic accuracy + ghost citations
   - Phase B: >= 30% citation context spot-check
   - Phase C: 100% statistical data verification
   - Phase D: >= 30% originality spot-check + self-plagiarism check
   - Phase E: risk-stratified claim verification (#549): 100% of HIGH-IMPACT claims (headline / numerical / causal / methods-critical / disputed) + 10% random sentinel of the remainder (rounded up, min 3 / max 10; remainder <3 → all of it), topped up to min(10, total claims) — bounds per `claim_verification_protocol.md` § Sampling Strategy
   - Phase E additionally emits the scope-conformance advisory (#547) and the novelty-claim classification (#548) — both advisory-only, never gate; advisory rows are not issues and may remain open on PASS — see `claim_verification_protocol.md` § E4-E5
3. Result handling:
   - PASS -> checkpoint -> Stage 3
   - FAIL -> produce correction list -> fix item by item -> re-verify corrected items
   - PASS after corrections -> checkpoint -> Stage 3
   - Still FAIL after 3 rounds -> notify user, list unverifiable items
```

## Stage 4.5: Final Integrity Check (Post-Revision Final Check)

**Trigger**: After Stage 4' (RE-REVISE) or Stage 3' (RE-REVIEW, Accept) completion, before Stage 5 (FINALIZE)
**Purpose**: Confirm the revised paper is 100% correct and ready for publication

```
Execution steps:
1. integrity_verification_agent executes Mode 2 (final verification) on the revised draft
2. Verification scope:
   - Phase A: 100% reference verification (including those added during revision)
   - Phase B: 100% citation context verification (not spot-check, full check)
   - Phase C: 100% statistical data verification
   - Phase D: >= 50% originality spot-check (100% for newly added/modified paragraphs)
   - Phase E: 100% claim verification (zero MAJOR_DISTORTION + zero UNVERIFIABLE required)
   - Phase E additionally emits the scope-conformance advisory (#547) and the novelty-claim classification (#548) — both advisory-only, never gate; advisory rows are not issues, stay outside the zero-issues PASS count, and may remain open — see `claim_verification_protocol.md` § E4-E5
3. Special check: Compare with Stage 2.5 results to confirm all previous issues are resolved
4. Result handling:
   - PASS (zero issues) -> checkpoint -> Stage 5
   - FAIL -> fix -> re-verify -> PASS -> Stage 5
5. ⚠️ **IRON RULE**: Must PASS with zero issues to proceed to Stage 5
```

## Score Trajectory Tracking (v3.3)

Reference: `academic-pipeline/references/score_trajectory_protocol.md`

At Stage 3' (RE-REVIEW), the `pipeline_orchestrator_agent` tracks per-dimension score deltas and triggers a MANDATORY checkpoint on regressions. Results stored in Integrity Report `score_trajectory` field (Schema 5).
