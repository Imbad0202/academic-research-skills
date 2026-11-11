# Harness Retirement Audit: `academic-research-skills` (2026-11)

| | |
|-|-|
| Repo path | `~/Projects/academic-research-skills` |
| Branch / commit audited | `main @ 06a2e6bd` |
| Date | 2026-11-11 |
| Target model | Claude Fable 5.2, Claude Fable 5.1, and Claude Opus 5.5 (session); Codex `gpt-6-astra` (cross-model transport). Unchanged since `audits/harness-retirement-2026-11-fable-5-2.md` |
| Scope | All 23 Bucket A agent prompt bodies from `scripts/ars_phase_scope_manifest.json` v1 |
| Files scanned | 23 (all 23 changed since the 2026-09 monthly baseline) |
| Baseline | `audits/harness-retirement-2026-09.md` (last full-diff review of the Bucket A bodies, at `e8bf858`). The two model-update audits since then (`audits/harness-retirement-2026-09-opus-5-5.md`, `audits/harness-retirement-2026-11-fable-5-2.md`) mapped system cards to ARS mechanisms and ran mechanical scans; neither reviewed the Bucket A body diffs line by line. No Bucket A body changed in `6d938867..06a2e6bd`, so the Fable 5.2 audit's mechanical results still apply |
| Method | Line-by-line review of every Bucket A change in `e8bf858..06a2e6bd`, mechanical pattern search across all 23 current bodies, referenced-path existence check, and a lint-pin check for each candidate sentence |

## Executive summary

- **Findings: 0 P0, 0 P1, 1 P2 (three sentences in two files), accepted and applied.**
- This period's prompt changes trace to 13 merged PRs, each anchored to an issue: #823-#826, #857/#882, #849, #862 Phase 1, #890, #894, #916, #927, #928, #938, #973, #1001, #1037. None of them adds a model pin, a sampling override, a generic anti-hallucination line, a teaching few-shot block, or an open retry loop.
- Three changes this period, landed through two reviewed PRs (PR #827 for #823-#826 and PR #869 for #862 Phase 1), are themselves retirements of debt-like patterns: hedging as a substitute for missing evidence was replaced by `[MATERIAL GAP]` or omission in `draft_writer_agent` (#825), fixed quotas (TEEL ≥80%, 120-200-word paragraphs, the em-dash and semicolon counts) were replaced by judgement tied to author and venue requirements (#825), and the fixed abstract lengths in `abstract_bilingual_agent` and `structure_architect_agent` were replaced by a lookup in one regime table keyed by paper type and language pair, with a venue limit taking precedence (#862).
- **P2-F01:** three sentences added by #862 Phase 1 state, in whole or in part, how far the change's claim reaches. That claim-scope wording is addressed to a reader of the repository, not to the model; the instructions in the same sentences stay. The wording is not lint-pinned, and the same scope statement lives in `shared/output_language_pair.md` and `CHANGELOG.md`.

### Findings by issue #1034 category

| Category | Findings | Result |
|---|---:|---|
| Capability-era workarounds | 0 | The rewritten "Bash denied" statements (#973) now describe when the runtime guard applies; they record a runtime boundary, not a model limit |
| Pre-tool-use scaffolds | 0 | The new acronym hooks (#849) hand work to `scripts/check_acronyms.py` rather than duplicate it in prose |
| Verbose reasoning scaffolds | 1 (P2) | P2-F01 below; no step-by-step reasoning template was added |
| Defensive few-shot examples | 0 | 0 `Example N` / `<example>` blocks across the 23 bodies; the new blocks are output grammars (`suggested-references`, method weaknesses) consumed by scripts or sync lints |
| Format guards | 0 | The `suggested-references` block (#1001) is the input format for `scripts/verify_panel_recommendations.py`; it does not repeat a schema check |
| Deprecated tool references | 0 | 174 of 174 script, schema, and reference paths cited in the 23 bodies exist at `06a2e6bd` |

## Findings

```
[P2-F01] academic-paper/agents/abstract_bilingual_agent.md:32, :43;
         academic-paper/agents/draft_writer_agent.md:369 | category 3 (verbose scaffold, maintainer-facing prose)
Excerpt (:32): "Absence is the legacy state, not a gap, and the claim is exactly this much:
  with the key omitted the legacy object keys and the heading literals below reproduce
  exactly and the serialized key is omitted."
Excerpt (:43): "This pins the literals, not the rendered output: no rendered-output
  equivalence with a pre-#862 run is claimed."
Excerpt (:369): "Absence is the legacy state, and what stays put is exact: the omitted key,
  the legacy object keys, and the heading literals — so a pre-#862 handoff keeps the same
  keys, headings, and serialized shape, and every downstream step then omits the value too."
Rationale: the sentences at :32 and :369 mix an instruction (treat absence as the
  default, keep the legacy keys and headings) with a statement of how far the change's
  claim reaches; the sentence at :43 is only such a statement. That statement tells a
  reviewer of the repository how far the change's evidence goes; it gives the model no
  action. The same scope statement is in shared/output_language_pair.md:77 and :115-117
  and in the CHANGELOG 3.22.0 entry. No lint pins
  these sentences (grep over scripts/, shared/, tests/; check_output_language_pair_contract()
  checks registry membership and the default token, not this wording).
Proposed: keep the instructions, drop the claim-scope wording.
  :32 -> "Absence is the legacy state, not a gap: the legacy object keys and the heading
         literals below stay as they are, and the serialized key is omitted."
  :43 -> delete the sentence "This pins the literals, not the rendered output: no
         rendered-output equivalence with a pre-#862 run is claimed."
  :369 -> "Absence is the legacy state: the key stays omitted, and the legacy object keys
          and heading literals stay as they are, so every downstream step omits the value too."
Risk: low. The headings and keys are pinned by check_spec_consistency.py (line 1310 pins
  "### English Abstract" / "### Chinese Abstract"), and the instructions the model acts on
  are unchanged. The lint checks file text, not runs; the effect on runs is unmeasured.
Decision: accepted by the maintainer on 2026-11-11 and applied in this change.
```

## Examined and kept (delta over the September keep-list)

The September keep-list and the keep rows of the two model-update audits (DM-001 to DM-021, FT-009 to FT-018) stand unchanged. This period adds:

### Instruction/data boundary block in 10 Bucket A agents (#890, #894)

`citation_compliance`, `draft_writer`, `formatter`, `literature_strategist`, `editor_in_chief`, `ethics_review`, `risk_of_bias`, `synthesis`, `timeline_extraction`, and `editorial_synthesizer` each inline the canonical block plus one agent-specific sentence. Kept: the block is single-sourced and pinned by `scripts/check_instruction_data_boundary.py`, and the Fable 5.2 card still reports a low residual rate of acting on instructions in pasted text (FT-009). The failure it guards against is silent.

### #973 enforcement sentence in all 23 bodies

The paragraph grew by about 34 words in every body (36 to 70 in `bibliography_agent`) to say that the write-scope guard engages only for a separately dispatched subagent in an install that wires the hook. Kept: it is pinned verbatim by `scripts/check_v3_9_2_phase_boundary.py` invariant 4, and the shorter version overstated where the fence engages.

### #916 method-weaknesses block in `bibliography_agent` and `literature_strategist_agent`

Rule 4 ("Stop at the end of the table; do not keep adding items until the list feels complete") is a negative with a positive counterpart in the same sentence. Kept: the two copies are byte-synced by `scripts/check_method_weaknesses_sync.py`, and the stop rule bounds a list that would otherwise grow without a criterion.

### #882 DOI evidence-boundary paragraph in `citation_compliance_agent`

Six prohibitions in nine lines. Kept: each sits next to its positive form ("describe resolution as unchecked", "remain separate from the corrections/error count"), the paragraph came from the #857/#882 citation-check eval evidence, and the failure (a heuristic presented as a confirmed source error) is silent to the author.

### #1001 `suggested-references` block and the revised no-invention rule (domain and perspective seats)

Kept: the block is the input grammar for `scripts/verify_panel_recommendations.py`, and the no-invention rule now states that the check runs after the decision, which is why the rule still has to hold.

## Out of scope, recorded so it does not resurface

- `academic-paper/agents/draft_writer_agent.md:326` ("Source annotation missing Key Findings | Use source's Title + Method to infer likely contribution direction") is a behaviour bug, not prompt debt. It is tracked in #993.

## Mechanical scan results (all 23 current bodies)

- Hardcoded model pins (`claude-*`, `Opus N`, `Sonnet N`, `Haiku N`, `Fable N`, `Mythos N`): **0 hits.**
- Sampling and budget overrides (`temperature`, `top_p`, `max_tokens`, `budget_tokens`): **0 hits.**
- Few-shot headings (`Example N`, `<example>`): **0 hits.**
- Anti-hallucination phrasing: every new hit is a domain contract clause (#574 A5 no-invention, #882 DOI evidence boundary, #825 `[MATERIAL GAP]` routing, #916 bounded absence claims). High-stakes academic-citation domain: kept per the iron rule.
- Largest bodies: `formatter_agent` 1,022 lines, `draft_writer_agent` 685, `literature_strategist_agent` 663. Their growth this period includes the instruction/data boundary block (in all three), the longer #973 enforcement paragraph (in all 23 bodies), and contract text: the #862 Schema 4 section in `draft_writer_agent`, the #916 method-weaknesses block in `literature_strategist_agent` (the same block is in `bibliography_agent`), and the #928 output and content-scope rules in `formatter_agent`. The blocks added this period that several agents share are the instruction/data boundary block, the #916 method-weaknesses block, and the #1001 `suggested-references` block; each is examined above.

## Verification

- `git diff` review covered every Bucket A change in `e8bf858..06a2e6bd` (396 inserted and 102 deleted lines across 23 files, 13 commits).
- `git diff 6d938867..06a2e6bd` over the 23 bodies is empty, so the Fable 5.2 audit's mechanical scans apply to the same text.
- Referenced-path existence check: 174 of 174 paths resolve against the repo root or the agent's skill directory.
- Lint-pin check for P2-F01: no match for the three excerpts under `scripts/`, `shared/` (outside the contract doc's own wording), or `tests/`.
- The only prompt edits are the three P2-F01 sentences in `abstract_bilingual_agent.md` and `draft_writer_agent.md`.

## Routing checklist (issue #1034)

- [ ] Audit report posted as a comment on #1034.
- [x] P0 retirements: none.
- [x] P1 retirements: none.
- [x] P2-F01: accepted and applied; listed in `CHANGELOG.md` `[Unreleased]`.
