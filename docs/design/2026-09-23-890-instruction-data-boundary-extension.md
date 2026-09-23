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
agent files. It copies the canonical sentences into two prompts that a model receives
without the agent file around them: the claim-audit judge prompt and the cross-model
devil's advocate prompt. `scripts/check_instruction_data_boundary.py` pins every copy.

It claims nothing about model behavior. The block states whose instructions count; it
does not stop a model from acting on planted text, and no evaluation has measured
whether it changes behavior on these paths (§6). It does not separate instructions from
data at the dispatch envelope, which is #676's requirement.

## 2. Inventory method

The inventory covers all 39 agent files in the four skills and `shared/agents/`, and
the prompts `shared/cross_model_verification.md` sends to a cross-model verifier. For
each receiver it asks: which third-party text reaches it, from which source, on which
path (a user turn, a dispatch task prompt, a tool result, or a passport import), and
which boundary, if any, already applies.

The sources were the agent and mode tables in the four `SKILL.md` files, each agent's
role and input sections, the reviewer dispatch harness (`scripts/dispatch_e4_panel.py`),
the re-review protocol, and keyword counts used only to find candidates: retrieval, PDF,
reviewer comments, manuscript, corpus, passport, cross-model, and paste, plus lookup
terms (web search, fetch, Retraction Watch, Crossref, OpenAlex, website). The role and
input sections of every selected agent and of the higher-signal unselected ones were
read. The other unselected agents were classified from the `SKILL.md` tables and the
keyword counts without a full read.

The first pass missed four agents (deep-research `review` mode and the compliance
agent) that a second pass found. A cross-model review then found the devil's advocate
prompt and two wrong exclusion reasons (the formatter and the citation compliance
agent), and a follow-up keyword scan corrected two more (the monitoring agent and the
citation emitters). A surface this method missed may still exist.

## 3. Ranking and selection rule

**Paths in scope.** #890 frames its scope by two paths: third-party text inside a
dispatch task prompt, and text imported through the Material Passport. The pipeline
orchestrator qualifies through the passport import; because it also reads researcher
turns and builds dispatches from them, its row in §4.1 includes those turns. Text an
agent obtains through its own tool calls, such as a web lookup or a local PDF read, is
the retrieval surface the #272 design addressed with its two retrieval hot spots. §4.4
lists the receivers on that surface and the other paths outside this change.

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

**Selection rule**: a path in scope, first-hand third-party origin, and medium or high
consequence.

## 4. Inventory

### 4.1 Selected in this change

| Path | Third-party text | Receiver | Boundary before #890 | Consequence |
|---|---|---|---|---|
| Researcher turns and the dispatches the orchestrator builds | pasted manuscripts, reviewer or committee comments, source excerpts | `pipeline_orchestrator_agent` | none for embedded text (checkpoint provenance governs decisions only) | high: routes stages, relays decisions, builds dispatches |
| `resume_from_passport` import | passport fields copied from external documents, such as `literature_corpus[]` abstracts | `pipeline_orchestrator_agent` | none | high |
| Stage 2.5 and 4.5 reference verification | search results, fetched pages, source text, the manuscript, cross-model verdicts | `integrity_verification_agent` | none | high: gate verdict |
| Stage 4 to 5 claim audit (`ARS_CLAIM_AUDIT=1`) | retrieved reference text, `literature_corpus[]` | `claim_ref_alignment_audit_agent` and its judge call | none | high: feeds the formatter hard gate |
| Stage 2.5 and 4.5 compliance check | the Schema 9 passport payload (corpus abstracts), manuscript quotations | `compliance_agent` | none | high: tier-based gate block |
| academic-paper literature phase | search results, `literature_corpus[]` `abstract` and `user_notes` | `literature_strategist_agent` | none | medium: screening and bibliography |
| Reviewer Phase 0 | the whole manuscript | `field_analyst_agent` | the skill-level untrusted-materials rule, which the agent's own prompt does not carry | high: configures the reviewer identities |
| Reviewer Phase 2 | manuscript text, reviewer cards | `editorial_synthesizer_agent` | a call-level boundary in the evaluation harness only | high: editorial decision |
| Systematic-review Phase 2 | study reports, protocols, registrations | `risk_of_bias_agent` | none | high: risk-of-bias ratings feed certainty grading |
| deep-research Phase 2 temporal extraction | corpus entries, Crossref metadata, first-page PDF text | `timeline_extraction_agent` | none | medium: temporal verification sidecars |
| deep-research `review` mode | a paper the user provides, often written by someone else | `editor_in_chief_agent`, `devils_advocate_agent`, `ethics_review_agent` | none | high: editorial verdict, challenge verdict, integrity verdict |
| Cross-model devil's advocate critique (`ARS_CROSS_MODEL` set and the user consents) | the reviewed material: a paper the user provides in deep-research `review` mode, or the manuscript in panel review | the cross-model verifier, which receives only the simplified DA prompt in `shared/cross_model_verification.md` and the material | none | medium: its novel findings enter the DA report as `[CROSS-MODEL-FINDING]` |

### 4.2 Covered earlier or by another mechanism

| Path | Receivers | Boundary |
|---|---|---|
| Web and database retrieval | `source_verification_agent`, `bibliography_agent` | canonical block since #367 |
| Pasted reviewer and committee text | `revision_coach_agent` | canonical block since #883 |
| Manuscript in panel review, including the cross-model Reviewer 2 transport | the five panel seats | `<paper_content>` fence inside the loaded `### Phase 2 — Paper-visible review` subsection, pinned by `scripts/check_reviewer_data_fences.py` |
| Revised manuscript and author response letter in re-review | the gate calls the orchestrating layer dispatches (Phase 2A and 2B; the letter reaches 2B only); contract-governed default re-review invokes neither the EIC nor the synthesizer agent file as a worker | the revised manuscript is marked untrusted data, and the letter is fenced as untrusted author persuasion (`academic-paper-reviewer/references/re_review_mode_protocol.md`) |
| Re-review cross-model judge pass (#539) | the cross-model verifier | per-item inputs delimited as data, not instructions; the author's response letter does not reach it (same protocol, § Judge Provenance and Correlated-Error Boundary) |

The #272 design (§2, §6) named `perspective_reviewer_agent` as an uncovered consumer of
pasted comments. Today its only third-party input is the manuscript, which reaches it
inside the fence above, and pasted reviewer comments route to the revision coach. This
change leaves the five seats' sync-checked subsections unchanged.

### 4.3 Not selected

| Receivers | Why not |
|---|---|
| `synthesis_agent`, `report_compiler_agent`, `draft_writer_agent`, `structure_architect_agent`, `argument_builder_agent`, `abstract_bilingual_agent`, `meta_analysis_agent` | Second-hand on the paths in scope: their dispatches carry third-party text only as quotations or extracted values inside artifacts from covered agents. In revision mode the writer acts on roadmap items the author triaged, and the deterministic apply replays exact target scopes (`academic-paper/references/revision_patch_protocol.md`). The three citation emitters can also anchor a page in a locally read PDF (R-L3-1-D); a read the agent makes itself is a tool call (§4.4). |
| `formatter_agent`, `citation_compliance_agent` | Their dispatch input is a manuscript the user or the suite wrote. Their third-party input arrives only through their own lookups (§4.4): the formatter's journal author guidelines for a journal the submission guide does not list, and the citation compliance agent's Retraction Watch check and DOI resolution. The formatter's disclosure mode reads the policy snapshots recorded in the repo, not fetched pages. |
| `intake_agent`, both `socratic_mentor_agent` files, `research_question_agent`, `peer_reviewer_agent`, `visualization_agent` | User-authored or suite-authored input: the user's answers and dialogue, the user's own manuscript, the suite's drafts, the user's data. |
| `collaboration_depth_agent` | Reads the user's turns, including any pasted text, but its output is advisory and never blocks. |
| `monitoring_agent` | Produces digest templates and alert settings for the user to act on; the titles, abstracts, and metadata a digest draws on feed advisory output only. |
| `research_architect_agent` | Its outside input at the design-freeze checkpoint is a verifier model's result in the `[CROSS-MODEL-HANDOFF v1]` envelope. The verifier reads suite artifacts, and a divergence goes to the user. |
| Blind disagreement checkpoints (the cross-model verifier) | The payloads are suite artifacts: the RQ Brief and draft blueprint at design freeze, and the reviewer cards and paper metadata at the final editorial decision. |
| `state_tracker_agent` | Structured state only. |
| Requests a fallback model serves | Platform-side; no ARS prompt path to place a block in. |

### 4.4 Outside the paths in scope

- **Third-party text a receiver obtains through its own tool calls.** The formatter's
  journal author guidelines; the citation compliance agent's Retraction Watch check and
  DOI resolution; a citation emitter's own read of a local PDF; and the cross-model
  reference sample check, whose prompt carries the manuscript's reference entry and
  citing sentence while the third-party text arrives through the verifier's own
  grounded search. The #272 design placed the block in its two retrieval hot spots and
  left the remaining external-content consumers as future scope (its §6). These
  receivers stay uncovered.
- **The main session of a skill run.** It reads text the user pastes into their own
  turn before it loads any agent file. Of the four `SKILL.md` files, only
  `academic-paper-reviewer/SKILL.md` carries an untrusted-materials rule (its Iron Rule
  on untrusted review materials); the selected agents carry the block once the session
  loads them.

`docs/RISK_REGISTER.md` R3 records both as uncovered.

## 5. Placement and the prompt-construction check

**Whole-file prompts.** Every selected agent receives its whole agent file. The
evaluation harness sends the field analyst and the synthesizer whole
(`PromptBuilder._whole` in `scripts/dispatch_e4_panel.py`); only the five panel seats
are narrowed to a subsection. No script extracts a section from the other selected
files, and their skills name them as whole files. A block anywhere outside a
sync-checked or extracted section therefore reaches the model whenever the file is
loaded, the same assumption the three original hot spots rest on.

**Checked.** The field-analysis and synthesis system prompts that `PromptBuilder`
assembles on synthetic input contain the canonical body and the backpoint. This is a
prompt-construction check, not behavioral evidence.

**Prompts sent without the agent file.** Two prompts reach a model on their own. The
caller-supplied judge function may receive only the unified judge prompt between the
`JUDGE-PROMPT-CANONICAL` markers, without the agent body. The cross-model verifier
receives only the simplified devil's advocate prompt in
`shared/cross_model_verification.md` and the reviewed material. The canonical sentences
are copied into both: as blockquote lines in the judge prompt, and as plain lines inside
the DA prompt's code block. Each prompt is sent as written, so neither copy carries HTML
markers or a backpoint. The lint's `PROMPT_TEMPLATES` gives each prompt a pattern that
spans only the text the model receives: for the judge prompt, the region #361 hashes,
reused from `scripts/check_judge_prompt_version.py`; for the DA prompt, the whole code
block that directly follows the step naming it, closed only by a fence of the same
character at least as long as the opening one. The check strips blockquote prefixes
and requires the canonical body verbatim inside that text. Mutation tests cover a
removed copy (also inside a block with a nested example fence), a copy moved just
outside the transmitted text, a copy hidden in a comment before the DA code block, a
weakened copy, and a renamed anchor; controls confirm that a copy elsewhere inside the
DA code block, and a nested example fence, still pass.

The judge edit changes the template hash. `JUDGE_PROMPT_SHA256` and the label
`JUDGE_PROMPT_VERSION` (now `step0-decomp-v2-data-boundary`) in
`scripts/_claim_audit_constants.py` are re-pinned, as
`scripts/check_judge_prompt_version.py` requires. The judge-verdict cache key includes
the hash (#361), so persistent-cache verdicts from the old prompt are no longer served.
The audit is opt-in (`ARS_CLAIM_AUDIT=1`, default off), and the persistent cache needs
`cache_dir`. Because the copy sits inside the region #361 hashes, any later rewording of
§ 2A also forces a judge hash re-pin, a label bump, and a cache invalidation; both lints
fail until that is done. The DA prompt carries no hash pin;
`scripts/check_reviewer_finding_contract.py` reads the same block for its finding-quota
check.

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
| Integrity verification | web or source verification | class overlap; generic prompt |
| Claim-audit judge | none named | outside #675 scope |
| Compliance check (passport) | none | outside #675 scope |
| Literature strategist | bibliography intake | class overlap; generic prompt |
| Field analyst, editorial synthesizer | PDF or manuscript ingestion | class overlap; generic prompt |
| Risk of bias | PDF or manuscript ingestion (study reports) | class overlap; generic prompt |
| Timeline extraction | bibliography intake, PDF ingestion | class overlap; generic prompt |
| deep-research `review` mode | PDF or manuscript ingestion, other pasted text | class overlap; generic prompt |
| Cross-model devil's advocate prompt | PDF or manuscript ingestion (the receiver is the cross-model verifier) | class overlap; generic prompt |

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
- **The surfaces in §4.4.** Covering the tool-call receivers needs its own selection on
  the retrieval surface, the item the #272 design left as future scope. A rule for the
  main session would need a home that loads on every install path, since only the
  reviewer's `SKILL.md` carries one.

## 8. Touch list

- Agents: the twelve files in §4.1.
- `shared/cross_model_verification.md`: the copy inside the simplified DA prompt.
- `shared/ground_truth_isolation_pattern.md` § 2A: the hot-spot paragraph names the
  extension.
- `scripts/check_instruction_data_boundary.py`, `scripts/test_check_instruction_data_boundary.py`:
  twelve agents, the prompt-template check, nine mutation tests, and two placement
  controls.
- `scripts/_claim_audit_constants.py`: judge prompt hash and label.
- `scripts/check_pipeline_boundary_semantics.py`, `scripts/test_v3_6_7_phase_6_6.py`:
  orchestrator lock and section budget.
- `scripts/dispatch_e4_panel.py`, `scripts/dispatch_calibration_panel.py`,
  `scripts/test_dispatch_e4_panel.py`: rationale comments only.
- `docs/RISK_REGISTER.md` R3, `CHANGELOG.md`.
