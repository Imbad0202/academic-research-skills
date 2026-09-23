# #890: Instruction/data boundary for third-party text in dispatches and passport imports (design)

**Status**: interim, prompt-level extension of the #367 guidance layer. Its behavioral
effect is unmeasured. #676 stays open with its structural requirements unmet.

**Issue**: #890, a follow-up from #883.

**Related**: #272 and #367 (the guidance layer and its authoritative section,
`shared/ground_truth_isolation_pattern.md` § 2A); #883 (the revision coach, DG-1 in
`audits/harness-retirement-2026-09-opus-5-5.md`); #675 (behavioral measurement); #676
(structural isolation at the task envelope).

---

## 1. What this change claims

It places the unchanged canonical block from § 2A, with its backpoint, in twelve more
agent files, and copies the canonical sentences into the claim-audit judge prompt.
`scripts/check_instruction_data_boundary.py` pins every copy.

It claims nothing about model behavior. The block states whose instructions count; it
does not stop a model from acting on planted text, and no evaluation has measured
whether it changes behavior on these paths (§6). It does not separate instructions from
data at the dispatch envelope, which is #676's requirement.

## 2. Inventory method

The inventory covers all 39 agent files in the four skills and `shared/agents/`. For
each agent it asks: which third-party text reaches the agent, from which source, on
which path (a user turn, a dispatch task prompt, a tool result, or a passport import),
and which boundary, if any, already applies.

The sources were the agent and mode tables in the four `SKILL.md` files, each agent's
role and input sections, the reviewer dispatch harness (`scripts/dispatch_e4_panel.py`),
and keyword counts (retrieval, PDF, reviewer comments, manuscript, corpus, passport,
cross-model, paste) used only to find candidates. The role and input sections of every
selected agent and of the higher-signal unselected ones were read. The other
unselected agents were classified from the `SKILL.md` tables and the keyword counts
without a full read.

A first pass selected eight agents. A second pass, made while writing this document,
found two more qualifying paths: deep-research `review` mode, whose three agents read a
paper the user provides (the mode guide's use case is a paper to evaluate before
citing it), and the compliance agent, which receives the whole Material Passport. Both
meet the selection rule in §3 and were added.

## 3. Ranking and selection rule

The issue ranks surfaces by two questions.

**How untrusted is the origin?**

- *First-hand third-party*: text written by someone other than the user and the suite
  that reaches the agent directly: retrieved pages, fetched PDFs, pasted manuscripts or
  comments, and `literature_corpus[]` abstracts.
- *Second-hand*: third-party text that reaches the agent only as quotations or extracted
  values inside an artifact another agent produced.
- *User-authored or model-generated*: the user's own text and dialogue, the suite's
  drafts, and verifier model output.

**What can the receiving agent decide or change?**

- *High*: a gate verdict, a reviewer or editorial verdict, a configuration that shapes
  later stages, or a routed or relayed decision.
- *Medium*: a deliverable that later stages consume or that the user relies on.
- *Low*: advisory output that never blocks and is not consumed as a decision.

**Selection rule**: first-hand third-party origin, and medium or high consequence.

## 4. Inventory

### 4.1 Selected in this change

| Path | Third-party text | Receiving agent | Boundary before #890 | Consequence |
|---|---|---|---|---|
| Researcher turns and the dispatches the orchestrator builds | pasted manuscripts, reviewer or committee comments, source excerpts | `pipeline_orchestrator_agent` | none for embedded text (checkpoint provenance governs decisions only) | high: routes stages, relays decisions, builds dispatches |
| `resume_from_passport` import | passport fields copied from external documents, such as `literature_corpus[]` abstracts | `pipeline_orchestrator_agent` | none | high |
| Stage 2.5 and 4.5 reference verification | search results, fetched pages, source text, the manuscript, cross-model verdicts | `integrity_verification_agent` | none | high: gate verdict |
| Stage 4 to 5 claim audit (`ARS_CLAIM_AUDIT=1`) | retrieved reference text, `literature_corpus[]` | `claim_ref_alignment_audit_agent` and its judge call | none | high: feeds the formatter hard gate |
| Stage 2.5 and 4.5 compliance check | the Schema 9 passport payload (corpus abstracts), manuscript quotations | `compliance_agent` | none | high: tier-based gate block |
| academic-paper literature phase | search results, `literature_corpus[]` `abstract` and `user_notes` | `literature_strategist_agent` | none | medium: screening and bibliography |
| Reviewer Phase 0 | the whole manuscript | `field_analyst_agent` | the skill-level untrusted-materials rule, which the agent's own prompt does not carry | high: configures the reviewer identities |
| Reviewer Phase 2 | manuscript text, reviewer cards | `editorial_synthesizer_agent` | re-review response-letter fence (Phase 2B); a call-level boundary in the evaluation harness only | high: editorial decision |
| Systematic-review Phase 2 | study reports, protocols, registrations | `risk_of_bias_agent` | none | high: risk-of-bias ratings feed certainty grading |
| deep-research Phase 2 temporal extraction | corpus entries, Crossref metadata, first-page PDF text | `timeline_extraction_agent` | none | medium: temporal verification sidecars |
| deep-research `review` mode | a paper the user provides, often written by someone else | `editor_in_chief_agent`, `devils_advocate_agent`, `ethics_review_agent` | none | high: editorial verdict, challenge verdict, integrity verdict |

### 4.2 Covered earlier or by another mechanism

| Path | Receiving agents | Boundary |
|---|---|---|
| Web and database retrieval | `source_verification_agent`, `bibliography_agent` | canonical block since #367 |
| Pasted reviewer and committee text | `revision_coach_agent` | canonical block since #883 |
| Manuscript in panel review, including the cross-model Reviewer 2 transport | the five panel seats | `<paper_content>` fence inside the loaded `### Phase 2 — Paper-visible review` subsection, pinned by `scripts/check_reviewer_data_fences.py` |
| Author response letter in re-review | the panel seats | fenced as untrusted author persuasion (`academic-paper-reviewer/references/re_review_mode_protocol.md`, Phase 2B) |

The #272 design (§2, §6) named `perspective_reviewer_agent` as an uncovered consumer of
pasted comments. Today its only third-party input is the manuscript, which reaches it
inside the fence above, and pasted reviewer comments route to the revision coach. This
change leaves the five seats' sync-checked subsections unchanged.

### 4.3 Not selected

| Agents | Why not |
|---|---|
| `synthesis_agent`, `report_compiler_agent`, `draft_writer_agent`, `structure_architect_agent`, `argument_builder_agent`, `abstract_bilingual_agent`, `meta_analysis_agent`, `formatter_agent` | Second-hand. Third-party text reaches them only as quotations or extracted values inside artifacts from covered agents. In revision mode the writer acts on roadmap items the author triaged, and the deterministic apply replays exact target scopes (`academic-paper/references/revision_patch_protocol.md`). Disclosure mode reads the policy snapshots recorded in the repo, not fetched pages. |
| `intake_agent`, both `socratic_mentor_agent` files, `research_question_agent`, `citation_compliance_agent`, `peer_reviewer_agent`, `visualization_agent` | User-authored or suite-authored input: the user's answers and dialogue, the user's own manuscript in citation-check or revision mode, the suite's drafts, the user's data. |
| `collaboration_depth_agent` | Reads the user's turns, including any pasted text, but its output is advisory and never blocks. |
| `research_architect_agent` | Its outside input at the design-freeze checkpoint is a verifier model's result in the `[CROSS-MODEL-HANDOFF v1]` envelope. The verifier reads suite artifacts, and a divergence goes to the user. |
| `state_tracker_agent`, `monitoring_agent` | Structured state only; the monitoring agent does no retrieval. |
| Requests a fallback model serves | Platform-side; no ARS prompt path to place a block in. |

## 5. Placement and the prompt-construction check

**Whole-file prompts.** Every selected agent except the judge call receives its whole
agent file. The evaluation harness sends the field analyst and the synthesizer whole
(`PromptBuilder._whole` in `scripts/dispatch_e4_panel.py`); only the five panel seats
are narrowed to a subsection. No script extracts a section from the other selected
files, and their skills name them as whole files. A block anywhere outside a
sync-checked or extracted section therefore reaches the model whenever the file is
loaded, the same assumption the three original hot spots rest on.

**Checked.** The field-analysis and synthesis system prompts that `PromptBuilder`
assembles on synthetic input contain the canonical body and the backpoint. This is a
prompt-construction check, not behavioral evidence.

**The judge call.** The caller-supplied judge function may receive only the unified
judge prompt between the `JUDGE-PROMPT-CANONICAL` markers, without the agent body. The
canonical sentences are therefore copied into that template as blockquote lines. The
template is sent as written, so the copy carries no HTML markers and no backpoint. The
lint's new `check_judge_template()` strips the blockquote prefixes and requires the
canonical body verbatim; three mutation tests cover removal, weakening, and renamed
markers.

The edit changes the template hash. `JUDGE_PROMPT_SHA256` and the label
`JUDGE_PROMPT_VERSION` (now `step0-decomp-v2-data-boundary`) in
`scripts/_claim_audit_constants.py` are re-pinned, as
`scripts/check_judge_prompt_version.py` requires. The judge-verdict cache key includes
the hash (#361), so persistent-cache verdicts from the old prompt are no longer served.
The audit is opt-in (`ARS_CLAIM_AUDIT=1`, default off), and the persistent cache needs
`cache_dir`.

**Locks and budgets.**

- The orchestrator is one of the five pipeline files with a whole-file lock; the lock in
  `scripts/check_pipeline_boundary_semantics.py` is updated in the same commit. Its new
  section (20 lines) gets its own 25-line budget in `scripts/test_v3_6_7_phase_6_6.py`,
  because the shared budget had no headroom.
- The synthesizer's block sits in Core Mission, outside the
  `## v3.6.2 Sprint Contract Synthesizer Protocol` section that
  `scripts/check_reviewer_sprint_prompt_sync.py` keeps in sync.
- No other selected file carries a hash lock.

**One addition beyond the block.** The orchestrator's section also asks it to label
third-party material it embeds in a dispatch as third-party material. The orchestrator
is the only surface that builds dispatches. The sentence is guidance, not the
structural separation #676 requires.

**Stale rationale.** Three comments and one test docstring in the evaluation harness
said the field analyst and synthesizer files carry no untrusted-material rule. They now
say the files state only the general principle and name none of the delimited blocks.
The harness's call-level boundaries and their tests are unchanged.

## 6. #675 mapping

#675's scope names six surfaces: web or source verification, PDF or manuscript
ingestion, bibliography intake, pasted reviewer or committee comments, other text the
user pastes, and requests a fallback model serves (the last two added on 2026-09-23).

Its seed (`evals/heldout/indirect_prompt_injection_behavior/heldout_set.json`) has
eight scenarios over the first four surfaces. The guided condition uses one generic
prompt (`evals/heldout/indirect_prompt_injection_behavior/prompt_ars_guided.txt`) with
its own `<external_content>` fence, not any agent's prompt, and allows no tools or web
access. **As seeded, #675 evaluates none of the paths in §4.1.** A #675 result on this
seed measures that generic prompt. A measured claim for a path below needs a completed
#675 evaluation with a scenario that loads the receiving agent's assembled prompt, plus
retained evidence and a measurement row.

| Selected path | Overlapping #675 surface | Status |
|---|---|---|
| Orchestrator: pasted text in researcher turns | other pasted text | in #675 scope; no scenario yet |
| Orchestrator: `resume_from_passport` | none | outside #675 scope |
| Integrity verification | web or source verification | class overlap; the scenarios use the generic prompt |
| Claim-audit judge | none named | outside #675 scope |
| Compliance check (passport) | none | outside #675 scope |
| Literature strategist | bibliography intake | class overlap; generic prompt |
| Field analyst, editorial synthesizer | PDF or manuscript ingestion | class overlap; generic prompt |
| Risk of bias | PDF or manuscript ingestion (study reports) | class overlap; generic prompt |
| Timeline extraction | bibliography intake, PDF ingestion | class overlap; generic prompt |
| deep-research `review` mode | PDF or manuscript ingestion, other pasted text | class overlap; no agent-prompt scenario |

## 7. What stays open

- **#676.** Envelope-level separation of instructions and data, with least-privilege
  grants, is unbuilt. This layer adds prompt sentences, which #676 rules out as its own
  mechanism.
- **The compliance agent's declared access level.** Its frontmatter declares
  `data_access_level: verified_only`, but its passport input can carry unverified
  corpus text. The dirtiest-input rule in `shared/ground_truth_isolation_pattern.md`
  would need a separate re-derivation to settle the declaration; this change leaves it
  as is.
- **Second-hand consumers.** Revisit §4.3's first row if a #675 run shows planted text
  surviving as quotations through covered agents.

## 8. Touch list

- Agents: the twelve files in §4.1.
- `shared/ground_truth_isolation_pattern.md` § 2A: the hot-spot paragraph names the
  extension.
- `scripts/check_instruction_data_boundary.py`, `scripts/test_check_instruction_data_boundary.py`:
  twelve agents, the judge-template check, and three mutation tests.
- `scripts/_claim_audit_constants.py`: judge prompt hash and label.
- `scripts/check_pipeline_boundary_semantics.py`, `scripts/test_v3_6_7_phase_6_6.py`:
  orchestrator lock and section budget.
- `scripts/dispatch_e4_panel.py`, `scripts/dispatch_calibration_panel.py`,
  `scripts/test_dispatch_e4_panel.py`: rationale comments only.
- `docs/RISK_REGISTER.md` R3, `CHANGELOG.md`.
