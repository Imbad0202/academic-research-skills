# Claim Verification Protocol (Phase E)

## Purpose
Verifies that quantitative and factual claims in the paper are accurately supported by their cited sources. Phase A-D verify that references exist and are original; Phase E verifies that claims derived from those references are truthful.

## Scope
- All numerical claims (percentages, counts, effect sizes, p-values)
- All categorical assertions ("X is the largest...", "Y was the first to...")
- All trend claims ("increasing", "declining", "stable")
- All causal claims ("X causes Y", "X leads to Y")

## E1: Claim Extraction
- Scan the paper for all quantitative/factual claims
- For each claim, record: claim text, cited source(s), paper section, page/line
- Expected output: Claim Registry table

## E2: Source Tracing
- For each claim, locate the specific passage in the cited source that supports it
- Use WebSearch + DOI lookup to find the original source
- If source is behind paywall, note as UNVERIFIABLE_ACCESS

## E3: Cross-Referencing
- Compare claim text vs source text
- Check: exact numbers, date ranges, population descriptions, methodology descriptions
- Flag any discrepancies

## E4: Scope-Conformance Advisory (#547 — advisory-only)

**Inputs**: the RQ Brief `scope` object (E4's one required input), plus two optional refinements — `sub_question_bindings` and the outline's section→sub-question map — carried in the integrity dispatch context per the pipeline handoff table (Stage 2→2.5 / Stage 4→4.5). SKIP E4 with `[E4-SKIPPED: no scope context]` ONLY when the parent `scope` object itself is unavailable (standalone runs with no RQ Brief) — never reconstruct or guess one. Absent bindings or section map (pre-#547 artifacts): compare every section's claims against the full parent `scope` — that is the documented fallback, not a skip.

Compare each audited claim's population, timeframe, geography, and domain against the **effective scope** the claim's section inherits:

1. Resolve the section's effective scope (section → serves sub-question → bindings; fall back to the whole `scope` object when no bindings exist). Axes named in `inherits` use those values; omitted axes inherit the parent `scope` value; each recorded user-approved deviation REPLACES the bound on its axis — so an already-approved extension is never re-flagged.
2. Flag claims whose stated scope exceeds the effective scope on any axis as `SCOPE-BROADENED`, recording: claim location, effective scope, drafted scope, broadened axis.
3. ADVISORY ONLY: `SCOPE-BROADENED` rows never change Phase E verdicts and never gate PASS/FAIL — they are not issues, do not enter the gate's issue count, and may remain open when the gate passes. Each row carries a stable ID `ADV-E4-<n>` and is recorded in the Integrity Report's advisory table. Checkpoint options per row: **proceed open** (default, recorded) or **accept the broadening** (with a note to justify it in the text; recorded). E4 defines no reword route and places no obligation on any downstream agent: a user who wants wording narrowed asks for it as an ordinary revision instruction in the normal flow — the advisory table is visible wherever the Integrity Report travels (it accompanies the Stage 2.5→3 handoff materials), so rows can be cited by their ADV-E4 IDs when doing so. Rows still open at Stage 4.5 simply remain recorded in the Final Integrity Report deliverable. No automatic rewriting, no new dispatch path.

External motivation: Ren et al. (2026, arXiv:2607.13104 §5.1) — decomposition-based generation becomes vulnerable when sub-problems stop preserving the constraints of the original task (design inference: a drafted claim is the last link in that chain).

## Verdict Taxonomy

| Verdict | Definition | Severity | Example |
|---------|-----------|----------|---------|
| VERIFIED | Claim matches source exactly or within rounding tolerance | None | Paper: "15.2%"; Source: "15.2%" |
| MINOR_DISTORTION | Claim paraphrases source but meaning is preserved | MINOR | Paper: "about 15%"; Source: "15.2%" |
| MAJOR_DISTORTION | Claim oversimplifies, exaggerates, or misrepresents source | SERIOUS | Paper: "declined sharply"; Source: "declined by 2.1%" |
| UNVERIFIABLE | Source doesn't contain the claimed information | SERIOUS | Paper cites Smith (2020) for a claim, but Smith (2020) doesn't discuss this topic |
| UNVERIFIABLE_ACCESS | Source exists but full text not accessible for verification | MEDIUM | Paywalled journal article |

## Sampling Strategy
- Mode 1 (pre-review): 30% random sample of claims (minimum 10 claims)
- Mode 2 (final-check): 100% of claims

## Output Format

### Claim Verification Report
| # | Claim | Source | Section | Verdict | Detail |
|---|-------|-------|---------|---------|--------|
| 1 | [claim text] | [source] | [section] | VERIFIED | Exact match |
| 2 | [claim text] | [source] | [section] | MAJOR_DISTORTION | Paper says X, source says Y |

### Summary
- Total claims checked: [N]
- VERIFIED: [N]
- MINOR_DISTORTION: [N]
- MAJOR_DISTORTION: [N] (must be 0 for PASS)
- UNVERIFIABLE: [N] (must be 0 for PASS)
- UNVERIFIABLE_ACCESS: [N] (noted but does not block PASS)

## Pass/Fail Criteria
- PASS: Zero MAJOR_DISTORTION + Zero UNVERIFIABLE
- FAIL: Any MAJOR_DISTORTION or UNVERIFIABLE
- PASS_WITH_NOTES: Only MINOR_DISTORTION and/or UNVERIFIABLE_ACCESS
