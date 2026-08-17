# Integrity Review Protocol (Added in v2.0)

## Stage 2.5: First Integrity Check (Pre-Review Integrity)

**Trigger**: After Stage 2 (WRITE) completion, before Stage 3 (REVIEW)
**Purpose**: Check the named registered/sample populations for fabricated or erroneous reporting before review; this does not establish global correctness, raw-data truth, or actual execution

```
Execution steps:
1. integrity_verification_agent executes Mode 1 (initial verification) on the paper
2. Verification scope:
   - Phase A: 100% of registered references for existence + bibliographic accuracy + ghost citations
   - Phase B: >= 30% citation context spot-check
   - Phase C: 100% of registered statistical/data surfaces
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
**Purpose**: Recheck all registered references/claims and the named Phase B-D surfaces before finalization; PASS is not a certificate that the paper or underlying research is 100% correct or publication-ready

```
Execution steps:
1. integrity_verification_agent executes Mode 2 (final verification) on the revised draft
2. Verification scope:
   - Phase A: 100% of registered references (including registered additions during revision)
   - Phase B: 100% of registered citation contexts (not a sample within that population)
   - Phase C: 100% of registered statistical/data surfaces
   - Phase D: >= 50% originality spot-check (100% for newly added/modified paragraphs)
   - Phase E: 100% of E1 registered claims (zero MAJOR_DISTORTION + zero UNVERIFIABLE required within that population; semantic extraction completeness remains unknown)
   - Phase E additionally emits the scope-conformance advisory (#547) and the novelty-claim classification (#548) — both advisory-only, never gate; advisory rows are not issues, stay outside the zero-issues PASS count, and may remain open — see `claim_verification_protocol.md` § E4-E5
3. Special check: Compare with Stage 2.5 results to confirm all previous issues are resolved
4. Result handling:
   - PASS (zero issues) -> checkpoint -> Stage 5
   - FAIL -> fix -> re-verify -> PASS -> Stage 5
   - FAIL after 3 correction rounds -> Integrity Check FAIL Loop (`pipeline_state_machine.md`): unresolved items listed, user decision recorded
5. ⚠️ **IRON RULE**: Stage 5 entry requires PASS with zero issues, or — only after the 3-round FAIL loop is exhausted — an explicit, recorded user decision on the listed unresolved items; unresolved items are never silently dropped
```

## Tortured-Phrase Advisory Boundary (#660)

Tortured-phrase screening is not a sixth integrity phase and never changes a
Stage 2.5 or Stage 4.5 PASS/FAIL decision. After the exact final draft passes
Stage 4.5, the orchestrator builds the separate own-draft
`tortured-phrase-advisory/1.0` immediately before formatting. It remains
`HEURISTIC-ADVISORY` / `UNMEASURED`; a match requires review but establishes no
AI/author origin, paper-mill production, misconduct, cleanliness, contextual
false-positive/false-negative status, accuracy, or publisher acceptance. A
zero-match result states only that no list match was observed on the checked
bytes and is not a clean certification.

The checker consumes only the explicitly named local draft and, when supplied,
canonical snapshot and detached-manifest paths. The manifest's
`snapshot_sha256` binds the exact raw snapshot bytes and declares
`user_supplied` or `synthetic_fixture` supply; omitted supply produces an
explicit `not_checked` artifact. The #660 path
has no native PPS import/fetch or redistributed PPS content and invokes no
model, external API, human/model judge, ambient clock, file time, or network
time; timestamps are explicit inputs. It never edits the draft. A user-chosen
revision changes the checked bytes and must re-enter the existing integrity
and screening sequence rather than being auto-rewritten by the advisory.

Cited-source v1.2 rows remain separate per title and abstract. A missing
abstract is explicit `not_checked` / `unresolved` (`ABSTRACT_MISSING`). They
render only in the single `Bibliographic Integrity Advisories` section and
never mint a marker, trigger a gate, or supply replacement text.

## Cross-Document Consistency Advisory Boundary (#672)

#672 is not a sixth integrity phase. After the same exact Stage 4.5 PASS, it runs
second, after #660, inside the one existing mandatory Stage-5 entry checkpoint.
Both bind the identical accepted draft: #660's
`input_binding.artifact.artifact_id/artifact_sha256` must equal #672's
`input_binding.accepted_draft_artifact_id/accepted_draft_sha256`. Their
independent carriers and failure semantics must not be merged.

Before observations are consumed, the #672 finalizer replay-validates the exact
builder-produced `preregistration-artifact/1.0` sidecar, its provided companion,
the exact two-artifact source manifest, and the accepted draft. Methods absence
requires an exact named counterpart scope; a performed preregistration deviation
requires its third exact manuscript disclosure-scope witness. Missing or
unavailable evidence remains not checked and cannot become a clean result.

The result is always `LLM-ADVISORY` / `UNMEASURED`. It has no score, pass/fail,
gate, issue-count effect, ClaimIntent, rewrite authority, consent/protocol
duplicate, or agreement/clean meaning. A #672 contract failure writes no carrier
and leaves only bounded `ADVISORY_UNAVAILABLE:<CODE>`; it does not change the
Stage 4.5 verdict, block or delay the checkpoint, enter Phase E, or change
formatter/Stage-5 routing. A later manuscript revision stales both #660 and #672
and must re-enter integrity before both rerun in fixed order.

## Criterion Trajectory Tracking

Reference: `academic-pipeline/references/score_trajectory_protocol.md`

At Stage 3' (RE-REVIEW), the `pipeline_orchestrator_agent` performs a
criterion-local narrative comparison and triggers a MANDATORY checkpoint on
decision-bearing regressions. It uses `NOT_COMPARABLE` when the criterion or
evidence base changed and produces no numerical score or hidden delta. A typed
`criterion_trajectory` carrier is not wired in the current release and the
Integrity Report must not pretend to supply one; see the explicit design-only
status in `score_trajectory_protocol.md`.
