# #894: Instruction/data boundary for receivers that read third-party text through their own tool calls, and for the skill main session (design)

**Status**: interim, prompt-level extension of the #367 guidance layer. Its behavioral
effect is unmeasured. #676 stays open with its structural requirements unmet.

**Issue**: #894, a follow-up from #890.

**Related**: #272 and #367 (the guidance layer and its authoritative section,
`shared/ground_truth_isolation_pattern.md` § 2A); #890 (dispatch and passport-import
paths, `docs/design/2026-09-23-890-instruction-data-boundary-extension.md`); #892 (which
files load on each install path); #675 (behavioral measurement); #676 (structural
isolation at the task envelope).

---

## 1. What this change claims

It places the unchanged canonical block from § 2A, with its backpoint, in five more
agent files: the receivers whose task directs them to read third-party text through
their own tool calls. They are the formatter, the citation compliance agent, and the
three citation emitters (`synthesis_agent`, `draft_writer_agent`,
`report_compiler_agent`). It copies the canonical sentences into the single-reference
verification prompt that the integrity gates send to a cross-model verifier on the
first-party API route, whose own web search returns third-party pages. It places the
block in the four `SKILL.md` files, the home for the rule in the main session of a
skill run. `scripts/check_instruction_data_boundary.py` pins every copy.

It claims nothing about model behavior. The block states whose instructions count; it
does not stop a model from acting on planted text, and no evaluation has measured
whether it changes behavior on these paths (§7). It does not separate instructions
from data at the dispatch envelope, which is #676's requirement.

## 2. Inventory method

The starting point was the tool-call surface #890 §4.4 names. The inventory then
covered the 24 of the 39 agent files in the four skills and `shared/agents/` that did
not carry the block. A keyword scan found candidates only: web search, fetch,
retrieval, lookup, Semantic Scholar, Crossref, OpenAlex, Retraction Watch, DOI
resolution, download, PDF, author guidelines, journal website, API, PubMed, arXiv, and
Google Scholar. Fifteen files matched, and every match was read in context to decide
whether the agent's own task directs it to fetch or read third-party text. The nine
files without a match were classified from their role and input sections. For the
cross-model reference check, the prompt in `shared/cross_model_verification.md`, the
Codex transport's instructions in `scripts/cross_model_codex_transport.py`, and the
#787 bakeoff harness were read.

A surface this method missed may still exist. A keyword scan finds what a prompt
names, not what a model chooses to fetch without being told to.

## 3. Selection rule

**Path in scope.** Third-party text that a receiver obtains through its own tool call:
a web lookup, a database or resolver query, or a read of a document someone else wrote,
such as a source PDF. The #272 design covered this surface in its two retrieval hot
spots and left the other consumers as future scope (its §6).

**Ranking.** The two questions of #890 §3: how untrusted the origin is (first-hand
third-party, second-hand, or user-authored and model-generated), and what the receiver
can decide or change (high, medium, or low).

**Selection rule**: a receiver whose task directs such a tool call, first-hand
third-party origin, and medium or high consequence. This change does not edit a prompt
that a recorded validation run measured (§4.3, first row).

## 4. Inventory

### 4.1 Selected

| Receiver | Third-party text it reads itself | Where the agent file directs it | What the text can change | Consequence |
|---|---|---|---|---|
| `formatter_agent` | a journal's author guidelines, for a journal `references/journal_submission_guide.md` does not list | the journal submission checklist and the unknown-journal template steps | formatting decisions; a journal template's citation format replaces the paper's ("journal requirement > user preference") | medium: the submission package the user sends |
| `citation_compliance_agent` | Retraction Watch entries, DOI resolution results, publisher pages | § 3 DOI/URL Verification and § 5 Plagiarism & Retraction Screening | a citation's status and correction: remove or annotate a retracted source, correct a reference, flag a potential fabrication | high: its corrections are applied to the manuscript |
| `synthesis_agent`, `draft_writer_agent`, `report_compiler_agent` | a source PDF read locally to find the page for a `page` anchor | R-L3-1-D in each agent's citation-emission rules | how a claim is worded and anchored | medium: deliverables that later stages consume |
| Cross-model verifier, first-party API route (`shared/cross_model_verification.md`, integrity verification step 3) | the pages its own web search or grounding returns | the step-3 prompt ("Search the web to confirm") | the verdict, and so whether `[CROSS-MODEL-DISAGREEMENT]` fires for a reference | medium: a disagreement goes to human review; a false agreement hides one |

The formatter's lead-in says that a page's format requirements are data that its Core
Principle 3 tells it to apply, so the block does not stop it from following a journal's
format. The emitters' lead-in also names the source quotations inside the artifacts
they receive, which #890 classified as second-hand; those agents were selected for
their own PDF reads. The verifier receives only the prompt, so the canonical sentences
go inside its code block as plain lines, as #890 did for the devil's advocate prompt.
No recorded ARS run measured this prompt: the supported-model table in
`shared/cross_model_verification.md` names `gpt-5.6-sol` on the ChatGPT-subscription
transport as the only id with a measured run, and that transport sends its own
instructions, not this prompt.

### 4.2 Covered earlier

Agents whose own lookups the block already covers: `source_verification_agent` and
`bibliography_agent` (#367); `integrity_verification_agent`,
`claim_ref_alignment_audit_agent`, `literature_strategist_agent`, and
`timeline_extraction_agent` (#890).

### 4.3 Not selected

| Receiver or path | Why not |
|---|---|
| Cross-model reference check on the ChatGPT-subscription transport (`scripts/cross_model_codex_transport.py`) | The transport sends its own developer instructions, not the step-3 prompt. The #787 bakeoff that validated `gpt-5.6-sol` on this transport sent its calls through this script, and the instructions have not changed since, so they are part of what the run measured. Editing them changes a measured setup, so this change leaves them to a maintainer decision. They already treat the reference data as untrusted data, but they do not name the pages the verifier's search returns. |
| The promotion entry gates (`scripts/cross_model_smoke_test.sh` and its Codex variant) | Health checks that send one fixed, known reference; not a path for manuscript data. |
| `monitoring_agent` | It writes monitoring configurations and digest templates for the user to run; its Limitations say it cannot run monitoring itself or read full texts. Low consequence: advisory output. |
| `research_architect_agent` | It records only the caller's declaration about a completed artifact; it has no shell and must not open the companion (#672). |
| `intake_agent`, `visualization_agent`, `structure_architect_agent`, deep-research `socratic_mentor_agent`, `research_question_agent`, `state_tracker_agent`, `domain_reviewer_agent`, `devils_advocate_reviewer_agent` | Their keyword matches are output formats, citations of published work, or statements that no retrieval happens. None of them fetches third-party text itself. |
| The nine agents without a keyword match | No lookup in their task; their inputs are suite artifacts or the user's own text. |

## 5. The main session

The main session of a skill run reads text the user pastes into their own turn, such
as a manuscript someone else wrote, reviewer comments, or a copied web page or email.
`.claude/CLAUDE.md` loads only for sessions started inside the checkout, not on plugin
or skills-copy installs (#892), so it cannot be the rule's home. A skill's `SKILL.md`
loads on every install path when the skill runs, before any agent file.

The canonical block therefore goes into the four `SKILL.md` files, with a lead-in that
names pasted third-party text, placed outside the routing-core block that #892 keeps
byte-identical across copies. In `academic-paper-reviewer/SKILL.md` the existing Iron
Rule on untrusted review materials stays; the block adds the canonical wording the lint
pins.

The SessionStart announce also reaches plugin installs before any skill loads, but this
change does not add the block there. The announce's startup text is what the #892
routing fixtures measured, and adding to it would need those fixtures re-run. The
window the block does not reach is the routing decision itself, made before `SKILL.md`
loads.

## 6. #675 mapping

#675's scope names six surfaces: web or source verification, PDF or manuscript
ingestion, bibliography intake, pasted reviewer or committee comments, other text the
user pastes, and requests a fallback model serves. Its seed runs one generic guided
prompt, not any agent's prompt, so as seeded it evaluates none of the paths below. A
measured claim for a path needs a #675 scenario that loads the receiving agent's
assembled prompt.

| Selected path | Overlapping #675 surface | Status |
|---|---|---|
| Formatter: journal author guidelines | web or source verification | class overlap; generic prompt |
| Citation compliance: Retraction Watch, DOI resolution | web or source verification | class overlap; generic prompt |
| Citation emitters: local source PDF | PDF or manuscript ingestion | class overlap; generic prompt |
| Cross-model reference verification prompt | web or source verification (the receiver is the cross-model verifier) | class overlap; generic prompt |
| Main session: pasted text | pasted reviewer or committee comments, other pasted text | in #675 scope; generic prompt |

## 7. What stays open

- **Behavior.** Unmeasured on every path here (§6).
- **#676.** Envelope-level separation of instructions and data is unbuilt.
- **The ChatGPT-subscription transport.** Adding the boundary to its instructions is a
  maintainer decision, because it changes the setup the #787 bakeoff measured (§4.3).
- **The startup announce.** Adding the block there needs the #892 routing fixtures
  re-run (§5).

## 8. Touch list

- Agents: the five files in §4.1, and the plugin mirrors `agents/synthesis_agent.md`
  and `agents/report_compiler_agent.md`, copied from their `deep-research/agents/`
  sources.
- `shared/cross_model_verification.md`: the copy inside the step-3 prompt.
- Skills: the four `SKILL.md` files, and the whole-file lock on
  `academic-pipeline/SKILL.md` in `scripts/check_pipeline_boundary_semantics.py`.
- `scripts/check_instruction_data_boundary.py`, `scripts/test_check_instruction_data_boundary.py`:
  the new files, with the existing mutation tests parametrized over them, and the
  reference prompt as a third prompt template that shares the devil's advocate
  prompt's extractor and its mutation tests.
- `shared/ground_truth_isolation_pattern.md` § 2A: where the copies sit, by kind of
  receiver.
- `docs/RISK_REGISTER.md` R3, `CHANGELOG.md`.
