# Disclosure Mode Protocol

**Status**: v3.2 + #596 venue-intake extension (#108 parallel `--policy-anchor=<a>` path unchanged)
**Parent skill**: `academic-paper`
**Mode name**: `disclosure`
**Purpose**: Generate either (a) a venue-specific AI-usage disclosure bundle aligned to the policy snapshot recorded by ARS (v3.2 path, default), or (b) a policy-anchor-specific disclosure rendered from the 4-anchor matrix (PRISMA-trAIce / ICMJE / Nature / IEEE) when the author targets a policy anchor rather than a specific journal venue (#108 path). This mode renders AI-use disclosure; it does not certify that the complete submission package satisfies every reporting requirement of the venue.

---

## Two parallel tracks (#108 + v3.2)

The `disclosure` mode dispatches on the author-supplied selector:

| Selector | Track | Lookup source | Output shape |
|---|---|---|---|
| `--venue=<v>` (v3.2, default) | Venue track | `venue_disclosure_policies.md` database (v2, 15 policy targets: ICLR / NeurIPS / Nature / Science / ACL / EMNLP + the #596 medical-publishing set — ICMJE / NEJM / The Lancet / JAMA / BMJ / PLOS / Frontiers / 中华护理杂志社 Chinese Nursing Journals Publishing House / 国际眼科杂志 International Eye Science) | Zero or more location-tailored disclosure blocks + placement/action instructions (zero blocks only for an explicit `NOT_REQUIRED` or `ACTION_ONLY` result) |
| `--policy-anchor=<a>` (#108) | Anchor track | `policy_anchor_table.md` 4-anchor × 16-field matrix | 4-anchor-conditioned render per `policy_anchor_disclosure_protocol.md` |

The two tracks are **selector-mutually-exclusive by default** — one selector picks one track. When the author supplies **both** selectors in the same invocation, the renderer evaluates compatibility per concern #7 rules: a consistent pair (Nature venue + nature anchor, both sourced from `shared/policy_data/nature_policy.md`) proceeds; any other pair is **rejected with an explicit error** listing the policy conflict. Silent precedence between selectors is forbidden. See [policy_anchor_disclosure_protocol.md §5](policy_anchor_disclosure_protocol.md) for the full conflict-resolution detail.

If neither selector is supplied and the pipeline orchestrator does not infer one from upstream context, the mode prompts the user to specify which selector applies. The venue track remains the default for explicit journal submissions; the anchor track applies when targeting policy frameworks (e.g., compliance reporting to ICMJE-adopting journals collectively, or pre-submission alignment to IEEE author guidelines).

**Conflict resolution (concern #7) — exhaustive cases:**
- Supplied both, **consistent pair** (only currently defined case): `--venue=Nature` (any Nature Portfolio variant string) **and** `--policy-anchor=nature` → both target Nature substantive policy via the shared source pointer → **proceed**.
- Supplied both, **any other combination** (e.g., `--venue=Nature` + `--policy-anchor=ieee`; `--venue=ICLR` + `--policy-anchor=icmje`; or a Nature-venue spelling that does not match the canonical set with a non-nature anchor) → **reject** with explicit error citing the policy conflict; require the user to drop one selector. Silent precedence is forbidden by §4.4 #7.
- Supplied only one selector → run that track.
- Supplied neither selector → prompt the user to specify.

---

## Why this mode exists

`academic-paper` already ships two generic AI disclosure examples in `journal_submission_guide.md` ("Minimal Disclosure" and "Detailed Disclosure"). They are venue-agnostic educational examples, not a fallback inside this mode: they don't know that Nature requires disclosure in the Methods section specifically, that ICLR requires it in the paper body with acknowledgement that "LLMs were used as general-purpose writing tools", or that ACL requires the disclosure in the Acknowledgements section. A venue-track lookup failure therefore halts rather than silently using either example.

The v3.2 venue track closes the venue-specific gap. The #108 anchor track closes the policy-framework-specific gap that emerges when authors target a policy anchor (PRISMA-trAIce SLR guideline, ICMJE recommendations, Nature Portfolio editorial policy, IEEE author guidelines) rather than a specific journal venue.

---

## Inputs

1. **Paper draft**: current manuscript text (the mode needs to know what the AI actually did in order to describe it accurately).

2. **Selector** (one of):
   - **Target venue/policy target (`--venue=<v>`)**: journal, conference, publisher-wide policy, or umbrella recommendation label (v3.2 path; the option name remains `--venue` for compatibility). If the target is in the database (v2: ICLR, NeurIPS, Nature, Science, ACL, EMNLP, plus the medical-publishing targets ICMJE, NEJM, The Lancet, JAMA, BMJ, PLOS, Frontiers, Chinese Nursing Journals Publishing House 中华护理杂志社, International Eye Science 国际眼科杂志), use the cached policy. If not, refuse to guess — prompt the user to paste the target's current AI policy text from its official submission or policy page. Canonicalize only explicit aliases recorded below; do not silently map a publisher or journal family to one member journal.
   - **Policy anchor (`--policy-anchor=<a>`)**: one of `prisma-trAIce, icmje, nature, ieee` (#108 path). Anchor lookup follows `policy_anchor_disclosure_protocol.md`.

3. **Pipeline signal** (#108 anchor path only): `slr_lineage=true|false` set by the upstream pipeline orchestrator. Required for `--policy-anchor=prisma-trAIce` per §4.3 G2 invariant. Cold-start invocation requires explicit `mode=<value>` parameter; silent fallback to general track is forbidden.

4. **What ARS did**: the mode reads the paper's commit history / pipeline log (if using the full `academic-pipeline`) to identify which AI-assisted steps produced which parts of the paper. Collect the complete Phase 2 category table, including editing, analysis, and visual/artwork/media assistance; do not maintain a shorter intake enum. If the pipeline log is not available, ask the user to confirm which categories apply.

5. **Venue-required disclosure facts** (#596 venue path only): collect the fields selected by the venue matrix in Phase 2b. Each field has state `KNOWN`, `NOT_APPLICABLE`, or `UNKNOWN` and a value/evidence pointer when `KNOWN`. Pipeline logs and session metadata may prefill facts, but the renderer must show the prefilled value to the author for confirmation; it must not infer a missing fact from manuscript prose or invent a value. The anchor path keeps its separate field contract in `policy_anchor_disclosure_protocol.md`.

### Venue selector aliases added by #596

Match case-insensitively after trimming surrounding whitespace. The left-hand
label is the canonical database heading; the remaining values are accepted
aliases. Any value not listed here or in the pre-v2 selector set is unknown.

| Canonical target | Accepted aliases |
|---|---|
| BMJ | `The BMJ` |
| Chinese Nursing Journals Publishing House | `中华护理杂志社` |
| Frontiers | `Frontiers journals` |
| ICMJE | `International Committee of Medical Journal Editors` |
| International Eye Science | `国际眼科杂志` |
| JAMA | `Journal of the American Medical Association` |
| NEJM | `The New England Journal of Medicine`, `New England Journal of Medicine` |
| PLOS | `PLOS journals`, `PLOS ONE` |
| The Lancet | `Lancet` |

`JAMA Network` without the exact journal name and an arbitrary `Frontiers in
...` title are not silently treated as JAMA or Frontiers. Ask for the exact
target or current target policy. This prevents a family/publisher label from
quietly inheriting one member journal's instructions.

---

## Process

### Phase 1: Intake + lookup (selector-aware)

**Step 1a — selector dispatch:**
- Both `--venue=<v>` and `--policy-anchor=<a>` supplied → check policy compatibility per the Two-parallel-tracks section above. **Consistent pair (currently only any Nature Portfolio venue + `--policy-anchor=nature`, where "Nature Portfolio venue" includes canonical labels {"Nature", "Nature Portfolio", "Nature (Nature Publishing Group)", "Nature Publishing Group"} and the journal-family prefix `"Nature "` matching e.g. "Nature Medicine", "Nature Communications", "Nature Climate Change", etc.) → route the consistent pair to **step 1c (anchor path)** so the shared canonical source `shared/policy_data/nature_policy.md` drives rendering; step 1b's venue database (v2) does not need to contain every Nature Portfolio journal**. Conflicting pair → reject with explicit error.
- `--venue=<v>` only → step 1b (venue path).
- `--policy-anchor=<a>` only → step 1c (anchor path).
- Neither supplied → prompt the user to specify selector.

**Step 1b — venue lookup (v3.2 + #596 venue path):**
- If venue is in the database (v2) → load policy from `venue_disclosure_policies.md`.
- If venue is unknown → halt. Print: "I do not have a cached policy for {venue}. Please paste the venue's current AI-usage / generative-AI policy text so I don't guess." Do NOT fabricate a policy.
- If the user pastes a policy for an unknown venue, use it for this session only. Do NOT auto-persist it to the database — policies drift, and the database needs curation.

**Step 1c — anchor lookup (#108 path):**
- Validate `--policy-anchor=<a>` ∈ `{prisma-trAIce, icmje, nature, ieee}`. Other values → reject with the closed-enum error.
- For `--policy-anchor=prisma-trAIce`: confirm `slr_lineage=true` (pipeline signal) or `mode=systematic-review` (cold-start input) per the G2 invariant track gate. Otherwise refuse with G2 invariant citation.
- Reuse only Phase 2's generic AI-usage category shape, then delegate the anchor-specific decision, input expansion, rendering, and placement contract to `policy_anchor_disclosure_protocol.md`. Do not run venue Phase 2a/2b or venue placement rules on the anchor track.

### Phase 2: Categorize AI usage

Produce a categorized list of how AI was used in the manuscript:

| Category | Examples |
|---|---|
| Research assistance | Literature search, annotated bibliography, claim verification |
| Drafting assistance | Section drafting, paraphrasing, outline generation |
| Revision assistance | Reviewer response drafting, tracked changes, consistency checking |
| Editing assistance | Grammar, style, formatting, citation format conversion |
| Analysis assistance | Not applicable to pure writing flows; flag if the paper reports any analysis the AI did |
| Visual / artwork / media assistance | Explanatory figures, data visualizations, primary-research images, research-method images, clinical illustrations, graphical abstracts, cover art, or other submitted media |
| Peer review simulation | `academic-paper-reviewer` was used on the draft pre-submission |

For each category, mark: USED / NOT USED / UNCERTAIN. UNCERTAIN items require user confirmation before the disclosure text is finalized.

For the #596 venue track, create one author-confirmed use record per distinct
`tool × task/run/artifact` for every `USED` category. Each record retains the
tool identity, purpose, category, affected section or artifact, whether the tool
generated, substantively drafted, edited, analysed, or searched it, and whether the use was manuscript
preparation or part of the research. Do not collapse multiple tools, prompt
runs, figures, or research tasks into a single generic use. These records feed
both the prohibited-use discriminators and the venue-required fact ledger. The
anchor track keeps its separate per-anchor input contract.

### Phase 2a: Decide whether the venue requires a disclosure (#596 venue path)

Before expanding venue-required fields, compute `disclosure_outcome` as one of
`REQUIRED`, `ACTION_ONLY`, `NOT_REQUIRED`, or `UNKNOWN`. Base this decision on
confirmed uses, not merely on the selected venue.

Resolve Phase 2a.1 for every triggered use record before finalizing this
decision. A visual-only, data-only, or research-method use participates in
applicability even when all writing categories are `NOT USED`; it must not be
classified `NOT_REQUIRED` before its venue-specific predicates are resolved.

- `REQUIRED`: at least one confirmed use falls within the target's disclosure
  rule.
- `ACTION_ONLY`: no confirmed use requires manuscript disclosure text, but a
  recorded policy condition requires an author action or permission check. Emit
  the audit ledger and a labelled action checklist with zero disclosure blocks.
  In this database, the defined case is Elsevier AI-assisted cover art after its
  permissions/rights gate. If another use in the same invocation requires
  disclosure, the aggregate result is `REQUIRED` and the cover-art checklist is
  included alongside the relevant blocks.
- `NOT_REQUIRED`: every category is confirmed and either no AI was used or every
  use falls entirely within an explicit policy exemption. Emit the decision and
  policy basis; do not generate a disclosure paragraph.
- `UNKNOWN`: a category or an exemption predicate is unresolved. Halt and ask
  only for the fact needed to decide applicability.

Explicit exemption predicates relevant to this database include:

| Target | `NOT_REQUIRED` exemption (only when this is the complete AI use) |
|---|---|
| ACL / EMNLP | Language-only paraphrasing/polishing, predictive-keyboard input, or literature-search assistance covered by ACL's no-special-disclosure cases |
| JAMA | Basic grammar or spelling checking only |
| The Lancet / Elsevier | Basic grammar, spelling, or punctuation checking only; or specialist assistive technology used solely for accessibility |

For every other target, `NOT_REQUIRED` is available when all categories are
confirmed `NOT USED`; never invent an exemption absent from the recorded policy.
If a confirmed use is prohibited by the target, halt with the prohibited-use
finding instead of rendering language that could make the use acceptable.

#### Phase 2a.1: Resolve explicit prohibited-use discriminators

As part of Phase 2a, resolve every decision fact below when its trigger is
true. These facts decide whether rendering is permitted; they are audit-ledger
inputs, not prose to infer from a tool brand, manuscript text, or a broad use
category. Give each predicate `KNOWN` or `UNKNOWN` state and retain its value
and author-confirmed evidence basis. `UNKNOWN` halts before Phase 2b; a known
prohibited combination halts with the policy finding.

For the two Chinese-language policy targets, first record the author-confirmed
`policy_tool_scope` of every use record as `GENAI_OR_AIGC`, `OTHER_AI`, or
`UNKNOWN`; never infer it from a brand name. `UNKNOWN` halts. `OTHER_AI` does not
trigger the GenAI/AIGC-specific children below. If all records are `OTHER_AI`,
halt with a policy-scope gap and direct the author to the venue's current
non-GenAI instructions rather than claiming `NOT_REQUIRED`; for mixed records,
evaluate the `GENAI_OR_AIGC` records and add a scope note identifying the
`OTHER_AI` records that this policy row did not evaluate.

| Target | Trigger | Decision facts and outcome |
|---|---|---|
| Chinese Nursing Journals Publishing House (中华护理杂志社) | A `GENAI_OR_AIGC` use record is `USED` | For each record, collect `operations[]` from the closed set `GENERATED`, `SUBSTANTIVELY_DRAFTED`, `EDITED`, `ANALYSED`, `SEARCHED`, `OTHER_CONFIRMED`, and `affected_targets[]` from `WHOLE_PAPER`, `METHODS`, `RESULTS`, `RESULT_INTERPRETATION`, `RESEARCH_FIGURE_OR_MEDIA`, `ORIGINAL_RESEARCH_DATA`, `RESEARCH_PROCESS`, `OTHER_CONFIRMED`. Then confirm `generated_whole_paper_or_important_part`, `generated_research_figure_or_media`, `altered_original_research_data_process_or_results`, and `used_unverified_genai_reference`. The first predicate must be true when `GENERATED` or `SUBSTANTIVELY_DRAFTED` is paired with `WHOLE_PAPER`, `METHODS`, `RESULTS`, or `RESULT_INTERPRETATION`; the second must be true when `GENERATED` is paired with `RESEARCH_FIGURE_OR_MEDIA`; the third must be true when the record says original research data, process, or results were altered; and the fourth must be true when a GenAI reference was used without verification. A contradictory mapping is `INCOMPATIBLE`; any true predicate is a prohibited-use halt. |
| Frontiers | Visual / artwork / media assistance is `USED` | Record whether the use affected a figure. If true, record `figure_represents_data`; originality/plagiarism-free confirmation is required for every figure, while accuracy-to-data confirmation is required only when `figure_represents_data` is true. `KNOWN(false)` for an applicable affirmative fact is incompatible and halts. |
| International Eye Science (国际眼科杂志) | A `GENAI_OR_AIGC` use record is `USED` | For each use record, classify `use_scope` as `LANGUAGE_POLISHING`, `LITERATURE_RETRIEVAL`, `DATA_ORGANIZATION`, `OTHER_CONFIRMED_NON_CORE_RESEARCH_STEP`, or `CORE_RESEARCH_STEP`. Record the author-confirmed basis for an `OTHER_CONFIRMED` classification; `CORE_RESEARCH_STEP` is prohibited and an unknown scope halts. For each tool, also record `tool_is_overseas`. If false, the qualification child is `NOT_APPLICABLE`. If true, record `lawful_compliance_qualification` and its verification basis; `KNOWN(false)` is a prohibited-use halt. Never infer origin, qualification, or research-step scope from the product name, provider, or manuscript prose. For each use record also confirm `generated_core_main_text_conclusion_analysis_viewpoint_or_innovation_claim`, `fabricated_experimental_plan_technical_route_or_citation`, `replaced_author_in_experimental_design_or_data_validation`, `fabricated_data_invented_results_or_tampered_conclusions`, `rewrote_plagiarized_work_to_evade_detection`, `generated_peer_review_response_grant_contribution_or_integrity_statement`, and `uploaded_secret_research_data_or_unpublished_results_to_public_ai_platform`; `KNOWN(true)` for any of these is a prohibited-use halt. |
| JAMA | Drafting assistance is `USED` | Record the author-confirmed `submission_type` as `OPINION_MANUSCRIPT`, `LETTER_TO_THE_EDITOR`, `ONLINE_COMMENT`, or `OTHER_CONFIRMED`. Any of the first three is a prohibited-use halt. Do not classify the submission type from its prose. |
| JAMA | Visual / artwork / media assistance is `USED` | For each visual record, confirm `clinical_image_or_illustration_created_or_manipulated`. If false, its formal-research child is `NOT_APPLICABLE`. If true, record `part_of_formal_research_design_or_methods`; `KNOWN(false)` is a prohibited-use halt and `KNOWN(true)` continues to the method and rights facts in Phase 2b. |
| The Lancet / Elsevier | Visual / artwork / media assistance is `USED` | First record the positive predicate `generated_media_duplicates_or_refers_to_protected_subject`, where a protected subject is an existing copyrighted image, a real person, another party's identifiable product/brand, or an individual's voice likeness; `KNOWN(true)` is prohibited. Next classify non-primary artifacts as `EXPLANATORY_IMAGE`, `DATA_VISUALIZATION`, `GRAPHICAL_ABSTRACT`, or `COVER_ART`. For a record involving primary observed/experimental data, do not preselect a class: collect `ai_is_formal_research_design_or_method`, `image_output_directly_obtained_in_research_through_that_method`, and reproducible-method details, then resolve it to exactly one of `PRIMARY_RESEARCH_IMAGE` or `RESEARCH_METHOD_IMAGE`. If both predicates are confirmed true, use `RESEARCH_METHOD_IMAGE` even when the output concerns primary data. If AI created or altered an image presented as primary evidence but the output was not directly obtained in the research through a confirmed formal method, use `PRIMARY_RESEARCH_IMAGE` and halt as prohibited. Unknown provenance/method facts halt; do not use the method label without the two affirmative facts and reproducible detail. An unmodelled nonvisual-media use halts as a contract gap after the protected-content check. For every otherwise permitted submitted visual, confirm accuracy and originality; record whether it is based on existing artwork/graphics and, when true, the rights-holder permission and attribution. `KNOWN(false)` for an applicable accuracy/originality/rights fact is incompatible. A `DATA_VISUALIZATION` must be confirmed as directly derived from underlying data through a reproducible method; `KNOWN(false)` is prohibited/incompatible. For `GRAPHICAL_ABSTRACT`, record `graphical_abstract_used_ai_or_ai_assisted_illustration`. If false, the AI-tool-class and disclosure children are `NOT_APPLICABLE` (ordinary non-AI illustration is outside this renderer). If true, record `graphical_abstract_tool_class` as `GENERAL_PURPOSE_GENERATIVE_AI_IMAGE_TOOL` or `DEDICATED_SCIENTIFIC_OR_PROFESSIONAL_ILLUSTRATION_TOOL`; the first is prohibited and the second continues to Phase 2b. For `COVER_ART`, additionally collect prior permission from both the journal editor and publisher, `cover_art_contains_third_party_material`, and appropriate content-attribution details. A false third-party predicate makes only its permission child `NOT_APPLICABLE`; a true predicate requires the corresponding permission evidence. Content attribution remains an affirmative action fact; if no attribution is applicable, record `KNOWN(none_applicable)` with the author-confirmed basis rather than `NOT_APPLICABLE`. An unknown/false required permission or unknown attribution fact halts, and a cover-art-only invocation resolves to `ACTION_ONLY`. |

The `KNOWN` / `NOT_APPLICABLE` / `UNKNOWN` and incompatibility rules in
Phase 2b apply to these discriminators as well. A halt here reports the facts
already established but does not draft language that could imply a prohibited
use becomes acceptable through disclosure.

JAMA's statement that AI, LLMs, and chatbots **should not** generate or format
references is policy guidance, not the same modal strength as its explicit
"not permitted" uses. Surface a non-blocking advisory warning when that use is
reported, but do not turn the sentence into either a prohibited-use halt or a
disclosure-rendering prerequisite.

Chinese Nursing Journals Publishing House separately says that another author's
content already labelled as AI-generated generally should not be cited as an
original source and, when genuinely necessary, should be explained. When such
a citation is reported, record its necessity and explanation when available and
surface a non-blocking advisory/action note. Do not merge this qualified rule
into the hard `used_unverified_genai_reference` predicate, and do not make an
unknown explanation block the AI-use disclosure renderer.

### Phase 2b: Build the venue-required fact ledger (#596 venue path)

Run this phase only when Phase 2a returns `REQUIRED`. Select the target row below and build a field-level ledger. "Required" here means required before ARS may render a venue-aligned AI-use disclosure bundle; it does not certify the rest of the submission or convert policy advice into a prohibition. A conditional field becomes required only when its predicate is confirmed `true`.

| Venue | Required facts before render | Conditional facts |
|---|---|---|
| ACL | tool name; specific AI-produced content or task; affected section/content | For low-novelty generated text: author confirmation that output accuracy and source/idea citations were checked |
| BMJ | AI technology; why it was used; how it was used | Research-related use: method-level description |
| Chinese Nursing Journals Publishing House (中华护理杂志社) | tool/service name; purpose; affected text/figure/code; human review/editing performed; author acceptance of full responsibility | Use affecting research methods: method-level description |
| EMNLP | Same fact contract as ACL | Same conditional facts as ACL |
| Frontiers | tool name; version; model; source/provider; whether content was AI-produced or AI-edited; affected written/visual content | Use that forms part of the research method: method-level description. Figure use: originality/plagiarism-free confirmation; when `figure_represents_data` is true, also confirm that the figure accurately reflects the data. |
| ICLR | tool name; specific assisted tasks; author acceptance of full responsibility | None |
| ICMJE | description of the AI-assisted technology; how it was used | AI-generated quoted material: attribution and full-citation details. Exact tool name is ARS-recommended metadata, not an ICMJE-only render blocker. Human review/editing remains policy advice and responsibility practice, not a separate render-blocking condition. |
| International Eye Science (国际眼科杂志) | tool name; version; purpose; scope; proportion of generated content | Use involving **data organization (数据整理)**: data types and verification status |
| JAMA | affected use class; author review/accuracy confirmation; author acceptance of responsibility for content integrity | AI-assisted content creation, revision, or formatting beyond basic grammar/spelling: platform/program/tool name; model/tool version and extension number(s) when applicable; manufacturer; date(s) of use; what/how/affected portions. When `ai_used_in_scientific_study` is true: specific research use plus the three predicates `study_uses_llm`, `copyright_protected_content_entered`, and `ai_generated_content_included_in_submission`. Only when `study_uses_llm` is true: platform/program/tool name and version; manufacturer; date(s); prompt(s), prompt sequence, and prompt revisions. If `copyright_protected_content_entered` is true: (a) a copy/evidence pointer for the copyright-holder permission or license that must accompany the submission and (b) a separate description of that permission/license for Methods. If `ai_generated_content_included_in_submission` is true: affected item/content type plus the publication-rights or permission basis **as determined by the AI service or owner**, for Methods or the relevant legend. AI-created/manipulated clinical images within a confirmed formal research design: method and image-rights details. JAMA's broader study-design/reporting requirements remain outside this AI-disclosure renderer and must be surfaced as a separate scope note. |
| Nature | tool name; how it was used; affected content; author acceptance of accountability | AI-produced images or other research elements: method and image-rights details |
| NEJM | AI-assisted technology description; what the technology produced; human review/editing performed; author assertion that AI-produced text/images contain no plagiarism | AI-generated quoted material: attribution and full-citation details |
| NeurIPS | tool name; version when known; specific tasks; human review of AI-generated content | None |
| PLOS | tool name; how it was used; how outputs were validated; affected parts of the work | None |
| Science | tool name; affected manuscript parts; author verification of AI-generated content | None |
| The Lancet | affected use class; actual tool identity for every USED task; author acceptance of full responsibility | All permitted submitted visuals first satisfy the global Phase-2a.1 accuracy, originality, protected-subject, rights, and attribution gates. Substantive manuscript-preparation use: tool/service name, purpose/reason, human oversight, and review/editing performed. AI used as part of research: reproducible method details. Explanatory image use: per-image tool, version, and how used. AI-generated data visualization: model/tool name, version, developer/manufacturer, and reproducible Methods details. Research-method image use: name, version, developer/manufacturer when applicable, and reproducible Methods details. If `graphical_abstract_used_ai_or_ai_assisted_illustration` is true and Phase 2a.1 confirms a dedicated scientific or professional illustration tool: tool name for the caption and publication-rights/license basis. Cover-art action facts are collected in Phase 2a.1 and preserved in the audit/action checklist, not rendered as manuscript text. Primary-research-image alteration or general-purpose GenAI graphical-abstract use: prohibited-use halt, not a disclosure field. |

**Ledger rules (fail closed):**

1. Record the Phase-2a applicability result. Phase 2b cannot begin while it is `UNKNOWN`; neither `NOT_REQUIRED` nor `ACTION_ONLY` may render a disclosure paragraph. `ACTION_ONLY` returns the already-confirmed action facts and zero disclosure blocks unless another use makes the aggregate result `REQUIRED`.
2. Give every unconditional field, every conditional predicate, and every field expanded by a `true` predicate one state: `KNOWN`, `NOT_APPLICABLE`, or `UNKNOWN`.
3. `NOT_APPLICABLE` is valid only for a conditional child field whose predicate is explicitly recorded as false. An unconditional field cannot be `NOT_APPLICABLE`; an unknown predicate does not make its children not applicable.
4. A session or pipeline value may count as `KNOWN` only when its exact value is available and presented to the author for confirmation. Generic labels such as "an AI tool" do not satisfy tool/model/source fields.
5. `KNOWN` means epistemically known, not policy-compatible. For a required affirmative fact such as human review/editing, author responsibility, figure/data verification, or no-plagiarism confirmation, record both the confirmed value and the required value. `KNOWN(false)` is `INCOMPATIBLE`, not a pass; halt without writing the affirmative sentence.
6. If any required field or triggering predicate is `UNKNOWN`, or any required value is `INCOMPATIBLE`, **halt before Phase 3**. Output the incomplete/incompatible ledger and ask only for remediable missing facts. Do not ask the author to falsely change a historical fact, generate a draft with placeholders, or silently drop the field.
7. Continue only after every required field is `KNOWN` with a compatible value or validly `NOT_APPLICABLE`. Preserve the applicability decision and ledger with the rendered disclosure so an author can audit where every statement came from.
8. Key tool- and use-specific facts by their `tool × task/run/artifact` record. Do not satisfy one tool's version, prompt sequence, rights basis, review confirmation, generated proportion, per-image disclosure, or other child fact with a value belonging to another record. Where the policy asks for an aggregate (for example, total affected portions), retain links to every contributing record.
9. After expanding all conditional facts, rerun the Phase-2a.1 compatibility sweep against each use record. A record with an unresolved discriminator, an unmodelled use/artifact class, or a fact combination that conflicts with the selected row halts before Phase 3. Do not infer a new hard condition from policy prose; report a contract gap when the executable table and evidence row cannot be reconciled.

The ledger applies to the venue path only. It does not weaken or replace the anchor path's three-state and per-anchor input rules.

### Phase 3: Match categories to the venue's required phrasing

Run Phase 3 and Phase 4 only for a `REQUIRED` result. `ACTION_ONLY` skips prose
generation and proceeds directly to Phase 5 with its audit-backed action
checklist; `NOT_REQUIRED` emits only the applicability decision and policy basis.

The Phase-2a predicates and Phase-2b table are the venue track's executable category-to-field mapping. `venue_disclosure_policies.md` is the evidence layer: it supplies the policy summary, wording elements, prohibited uses, and placement channels. Do not claim that the seven-field policy row itself contains a machine-readable category mapping, and do not infer extra mandatory fields from free prose during rendering. If the evidence row appears to require a field absent from Phase 2b, halt and report a contract gap so the two coordinated surfaces can be updated together. If a category remains UNCERTAIN, a required fact is UNKNOWN, or a required value is INCOMPATIBLE, Phase 3 does not run.

### Phase 4: Generate the disclosure text

Generate a disclosure bundle containing one tailored block per required placement channel, using:
- The venue's preferred voice (first person vs passive, past tense vs present)
- The venue's required phrasing elements (many venues require the phrase "The authors take full responsibility for the content" or equivalent)
- The confirmed tool/service, provider/developer, model, and version values from the ledger, including one identity per tool when more than one tool was used
- The specific categories marked USED

Never hard-code Claude, ChatGPT, or any other product as the current tool. Never
emit square-bracket placeholders. When a version/provider field is policy-required,
an absent value remains `UNKNOWN` and the render halts; when it is genuinely
optional, omit it rather than inventing it. Nature's venue row does not make a
model version mandatory, so an unknown version alone does not halt that venue
render.

For JAMA scientific-study use, label the generated Methods text as the **AI-use
disclosure portion only**. When the corresponding predicates are true, include
the confirmed description of the copyright-holder permission/license for
protected model input and the confirmed publication-rights/permission facts for
included AI-generated content. The permission/license copy itself is a separate
submission-package action: report its confirmed evidence pointer in the audit
bundle, but do not paste the license document into Methods. Put item-specific
image rights in the relevant legend when that is the confirmed channel, and
generate a separately labelled block rather than hiding it in the general
Methods paragraph. Append a scope note directing the author to JAMA's remaining
current study-design and reporting instructions; do not call the output a
complete or submission-ready Methods section.

### Phase 5: Placement instructions

Output includes explicit placement instructions matching the venue's policy for every block:

```
Placement: Methods section (Nature policy, accessed YYYY-MM-DD from
https://www.nature.com/.../policy-url). Include as the final
subsection of Methods, before Data Availability.
```

If the venue requires placement in multiple locations (e.g., Methods + cover letter + Acknowledgements), the mode generates separately labelled, purpose-tailored text for each location rather than one paragraph copied into every channel. A policy phrase such as "at submission" is a timing instruction, not a manuscript location; when the source does not name a section, say that the section is unspecified and direct the author to the submission system/current journal instructions instead of inventing one.

For The Lancet / Elsevier, when Phase 2a.1 confirms the permitted AI-assisted
graphical-abstract path, generate a distinct caption disclosure naming the
illustration tool and place it in the graphical-abstract image caption. Preserve
the confirmed publication-rights/license basis and accuracy/originality checks
in the audit ledger; add attribution to the caption when applicable. Never reuse
the general manuscript-preparation declaration as a substitute for this caption.

For an Elsevier `ACTION_ONLY` cover-art result, emit zero manuscript disclosure
blocks and a labelled pre-submission checklist recording the confirmed editor
permission, publisher permission, whether third-party material is present and
its permissions when applicable, appropriate content-attribution details (or a
confirmed `none_applicable` basis), and the global image responsibility facts. Do not
invent a manuscript section for those actions. When cover art accompanies
another disclosable use, append the same checklist to the normal placement
instructions.

For Chinese Nursing Journals Publishing House, also emit a non-blocking
submission reminder that authors should cooperate with the editorial office in
submitting and archiving AI-assisted text, figures, or code as supplementary
material. Do not invent a first-submission attachment slot or make that
operational cooperation clause a disclosure-rendering field.

---

## Failure cases this mode does NOT cover

- **Venues outside the database**: the mode halts and asks the user. It does not guess.
- **Policies that have changed since the database snapshot**: the mode records the access date in the placement instructions. Users should verify against the current venue page before submission.
- **Analysis assistance**: if the AI actually ran computations or generated analysis results (not just writing), the renderer evaluates the target's research-use and data-use conditions, then emits any additional location-tailored block the policy requires. It does not assume a Code Availability or Analysis location when the source names a different section or no section.
- **Co-authored AI**: as of the 2026 policy snapshot, no venue in the database (v1 or v2) accepts AI as a listed author. The mode refuses to produce author-list text and instead produces authorship-rejection text plus the disclosure.

---

## Integration with existing journal_submission_guide.md

`journal_submission_guide.md` retains two generic examples (Minimal / Detailed)
for human adaptation outside this mode. They are **not** an unknown-venue
fallback: standalone disclosure mode halts and asks for the target's current
policy text when lookup fails. For a known venue, the protocol-driven disclosure
bundle supersedes those examples.

---

## References

- `venue_disclosure_policies.md` — policy database (v2: the 6 ML/NLP venues plus 9 medical-publishing policy targets incl. the ICMJE umbrella and the database's first Chinese-language entries; see its Scope line)
- `policy_anchor_table.md` — #108 4-anchor × 16-field matrix (PRISMA-trAIce, ICMJE, Nature, IEEE) for the policy-anchor track
- `policy_anchor_disclosure_protocol.md` — #108 policy-anchor track render protocol (per-anchor flows, G10 7-row precedence table, auto-promotion forbiddance, §4.4 11 concerns resolved paths)
- `journal_submission_guide.md` — existing generic examples for manual adaptation outside disclosure mode (not a runtime fallback)
- `credit_authorship_guide.md` — existing CRediT authorship best practices
- Lu et al. (2026). Towards end-to-end automation of AI research. *Nature* 651, 914-919 — the ethics statement for Lu 2026 was drafted in compliance with Nature's policy; their methodology is a worked example of what this mode should produce.
- `docs/design/2026-05-14-ai-disclosure-schema-decision.md` — #108 Decision Doc (G1-G10 + §4.3 invariants + §4.4 11 open concerns)
- `docs/design/2026-05-14-ai-disclosure-impl-spec.md` — #108 implementation spec (resolved-paths table)
- ROADMAP_v3.2.md item 6 — design decisions (v1 venue set, unknown-venue halt, education/QA venues deferred to v2)
