# Research Ethics Checklist — AI-Assisted Research

## Purpose
Comprehensive ethics checklist for AI-assisted academic research. Used by the ethics_review_agent.

## 1. AI Disclosure

### Mandatory Disclosure Elements
- [ ] AI tools used are named (e.g., "Claude," "GPT-4," "Gemini")
- [ ] Scope of AI involvement specified:
  - [ ] Literature search assistance
  - [ ] Source screening
  - [ ] Evidence synthesis
  - [ ] Draft writing
  - [ ] Editing/revision
  - [ ] Data analysis
  - [ ] Translation
- [ ] Human oversight described (who reviewed what, at which stages)
- [ ] AI limitations acknowledged (potential hallucination, knowledge cutoff, etc.)
- [ ] AI version/date noted (for reproducibility)

### Disclosure Statement Template
```
AI Disclosure: This research was conducted with assistance from [AI Tool Name]
(version/date). AI was used for [specific tasks]. All findings were verified
against cited sources by [human role]. The research team maintains full
responsibility for the accuracy and interpretation of all content.
```

### Where to Place Disclosure
- In the methodology section (detailed)
- In the abstract or author note (brief)
- In footnotes for specific AI-generated analyses

## 2. Attribution Integrity

### Citation Ethics
- [ ] Every factual claim has at least one supporting citation
- [ ] No fabricated or hallucinated references
  - Verification: Spot-check minimum 20% of references for existence
  - Cross-check DOIs, publication years, author names
- [ ] Paraphrasing is genuine (not just rearranging words)
- [ ] Direct quotes are exact and attributed
- [ ] Ideas are attributed to original authors, not intermediary sources
- [ ] Self-citation is proportionate (not excessive or exclusionary)

### AI-Specific Attribution Risks
| Risk | Description | Mitigation |
|------|-------------|-----------|
| Hallucinated references | AI generates plausible but non-existent citations | Verify every reference against database |
| Merged citations | AI combines details from multiple sources | Cross-check each citation element |
| Incorrect authors | AI assigns wrong authors to works | Verify author names against actual publications |
| Wrong year | AI uses incorrect publication year | Cross-check against database records |
| Ghost citations | References listed but never cited in text | Audit reference list against in-text citations |

## 3. Dual-Use Assessment

**Screen on concrete specifics, never on subject matter.** A sensitive, political, or institution-critical *topic* is not a dual-use trigger. Public-interest research — documenting institutional abuses, exposing surveillance practices, holding power to account — is expected to address harmful subject matter and must not be flagged for the topic alone. A finding triggers dual-use only when the work itself supplies **specific operational detail** that materially lowers the barrier to harm. Studying surveillance is fine; shipping a step-by-step deployment recipe is the trigger.

### Screening Questions
Each asks whether the **content of this work**, not its topic, supplies the specific:
1. Does the work provide concrete operational detail that would let a reader **carry out** harm against individuals or communities (beyond describing that the harm exists)?
2. Does it disclose a **specific, currently-exploitable** vulnerability together with enough detail to exploit it (vs. naming that vulnerabilities exist)?
3. Does it provide a **usable method** to build surveillance or control mechanisms (vs. analyzing or critiquing them)?
4. Does it contain **weaponizable specifics** — a recipe, design, or procedure — rather than discussion of weaponization risk?
5. Does it supply a **concrete means** to discriminate against a group (vs. documenting that discrimination occurs)?

If the answer rests on the topic being sensitive rather than on specific enabling detail in the text, the level is None.

### Risk Levels and Responses

This assessment is **advisory** — it routes to a Responsible Use Statement and never to a hard block. (Hard blocks are reserved for integrity violations; see `agents/ethics_review_agent.md` Blocking Conditions.) Escalation rests on concrete enabling specifics, not subject matter.

| Level | Action Required |
|-------|----------------|
| None | No additional action |
| Low | Brief note in limitations |
| Moderate | Responsible Use statement in report |
| High | Prominent warning + limited distribution recommendation |
| Critical | Responsible Use statement + recommend institutional ethics review before publication (advisory — does not auto-block; a human, not the agent, adjudicates a Critical flag) |

### Responsible Use Statement Template
```
Responsible Use: This research is intended for [stated purpose]. The authors
acknowledge that findings related to [sensitive area] could potentially be
applied in ways not intended by this research. Users of this research are
urged to consider the ethical implications of their applications and to
prioritize [specific ethical principle].
```

## 4. Fair Representation

### Balanced Treatment Checklist
- [ ] Multiple perspectives on contested issues are presented
- [ ] Minority/dissenting viewpoints are not dismissed without engagement
- [ ] Subjects and communities are described accurately
- [ ] Language is respectful and non-stigmatizing
- [ ] Cultural context is acknowledged where relevant
- [ ] Power dynamics are considered (who is studied vs. who studies)
- [ ] Geographic and cultural diversity in sources

### Sensitive Topics
- Indigenous knowledge: Identify and follow the specific community-governance
  convention in scope; use OCAP (Ownership, Control, Access, Possession) only
  where the relevant First Nations authority or community has adopted it
- Disability: Person-first language unless community prefers identity-first
- Gender/sexuality: Use inclusive, current terminology
- Race/ethnicity: Use preferred terminology of the communities discussed
- Socioeconomic status: Avoid deficit framing
- Mental health: Avoid stigmatizing language

### Representation Audit Questions
1. Whose voices are centered? Whose are missing?
2. Are communities described on their own terms?
3. Is there implicit bias in the framing?
4. Would the subjects/communities recognize themselves in this description?

## 5. Data Ethics

### Data Source Ethics — Portable Integrity Planning

These are **planning and documentation conventions**, not legal conclusions.
Applicable law, licence interpretation, and institutional authorization remain
with the responsible authority.

- [ ] For each source, the asserted access/use basis and unresolved questions are documented
- [ ] Public data: Publication status, access terms, provenance, and licence are recorded
- [ ] Licensed data: Relevant licence terms and the team's intended use are recorded
- [ ] Scraped data: Site terms, robots instructions, collection method, and unresolved authority questions are recorded
- [ ] Personal data: Each candidate data-protection authority is recorded; no jurisdiction or legal basis is inferred
- [ ] Institutional data: The supplying institution's documented access status and conditions are recorded

### Privacy Protection

The following are **portable technical planning prompts**, not a universal
privacy-law checklist:

- [ ] Direct identifiers, quasi-identifiers, platform metadata, and re-link keys are inventoried
- [ ] The asserted authority or institutional basis for collecting and processing identifiers is recorded; consent is not presumed to be the only or applicable basis
- [ ] Aggregation, masking, or other disclosure controls have been considered for small-N groups and identifiable institutions
- [ ] Access roles, recipients, security, retention, deletion, reuse, and incident handling are documented
- [ ] If the exact GDPR profile is selected, the trace points to the applicable bounded rows (`eu.gdpr.article-6.lawful-basis`, `eu.gdpr.article-9.special-category-research`, `eu.gdpr.article-13.direct-collection-information`, `eu.gdpr.article-14.indirect-collection-information`, and/or `eu.gdpr.article-89.1.research-safeguards`) rather than asserting a result

### AI-Specific Data Concerns
- [ ] AI training data biases acknowledged
- [ ] AI knowledge cutoff date noted
- [ ] AI-generated data clearly labeled as such
- [ ] No circular citation (AI cites AI-generated content)

## 6. Conflict of Interest

### Types to Assess
- [ ] Financial: Funding source, consulting relationships
- [ ] Institutional: Author evaluating own institution
- [ ] Intellectual: Author defending own prior work
- [ ] Personal: Relationships with subjects/stakeholders
- [ ] Political: Government-funded research on government policy
- [ ] Commercial: Industry connections or product interests
- [ ] AI-specific: AI tool company influence on research design

### Disclosure Requirement
Any identified conflict must be disclosed in the report, with an assessment of whether it could have influenced the findings.

## 7. Reproducibility Ethics

### Documentation Requirements
- [ ] Search strategies documented (databases, terms, dates)
- [ ] Inclusion/exclusion criteria documented
- [ ] Analytical methods described in replicable detail
- [ ] AI prompts/instructions documented (if relevant)
- [ ] Data processing steps documented
- [ ] Code/scripts shared (if applicable)

### Reproducibility Statement Template
```
Reproducibility: The search strategy, inclusion criteria, and analytical
methods used in this research are documented in [section/appendix]. The
AI-assisted components used [specific prompts/parameters]. Researchers
wishing to replicate or extend this work should note [relevant limitations
or conditions].
```

## 8. Human Subjects Ethics

> **Authority boundary (#665/#666/#680):** Mixed-jurisdiction review-level mappings are not part of this checklist. This section collects facts and exact bounded requirement pointers only; the output pathway is `institutional determination required`. Unknown selection or applicability stays unresolved, and neither this checklist nor #666 emits a review determination, readiness result, compliance conclusion, or authorization.

Apply `shared/references/human_subjects_authority_protocol.md` and use only
curated rows from `shared/human_subjects_authority_registry.json`. All shipped
profiles are bounded subsets.

### 8.1 Authority Context and Exact Facts

- [ ] The review-ethics and data-protection axes each have an exact selected #666 profile or a visible unresolved state
- [ ] Profile selection records id, version, digest, and authority scope; geography, funder, language, and topic are not used to infer selection
- [ ] Confirmed, false, and unknown facts remain distinct
- [ ] The exact #666 fact catalogue has been addressed where relevant:
  - [ ] `activity.human_subjects`
  - [ ] `support.us_hhs_or_common_rule`
  - [ ] `scope.tw_hsra`
  - [ ] `scope.eu_gdpr`
  - [ ] `processing.personal_data`
  - [ ] `data.special_category`
  - [ ] `data.collected_from_subject`
  - [ ] `purpose.scientific_research`
  - [ ] `gdpr.member_state_research_law_identified`
- [ ] Additional interaction, intervention, recruitment, population, power-relationship, sensitivity, deception, identifiability, and risk facts are labelled `illustrative/unprofiled` when they are not in the registry

Vulnerability, sensitivity, deception, public availability, identifiability,
and estimated risk are facts for the responsible institution. They do not map
to a pathway in this checklist.

### 8.2 Exact Bounded Requirement Trace

Use these identifiers only as pointers to the full selected registry row,
including its predicate, obligated actor, consumer scopes, expected evidence,
and primary-source anchor. Do not restate them as universal requirements.

| Axis | Exact #666 requirement ids currently available |
|---|---|
| Review ethics — U.S. bounded profile | `us.45cfr46.107.irb-composition`; `us.45cfr46.116.informed-consent` |
| Review ethics — Taiwan bounded profile | `tw.hsra.article-7.committee-composition`; `tw.hsra.article-14.consent-information` |
| Data protection — GDPR bounded profile | `eu.gdpr.article-6.lawful-basis`; `eu.gdpr.article-9.special-category-research`; `eu.gdpr.article-13.direct-collection-information`; `eu.gdpr.article-14.indirect-collection-information`; `eu.gdpr.article-89.1.research-safeguards`; `eu.gdpr.article-89.2.member-state-derogation` |

- [ ] Each pointer belongs to an exactly selected profile whose resolved result permits profile-dependent use
- [ ] Committee-composition rows remain with their institutional/committee actors and are not converted into investigator packet requirements
- [ ] U.S. and Taiwan rows retain their own authority vocabulary and are not translated into one another's pathway terms
- [ ] Requirements outside these bounded rows are labelled `unprofiled` and referred to the responsible authority

### 8.3 Participant-Information and Consent Preparation

- [ ] If applicable after exact resolution, the trace uses `us.45cfr46.116.informed-consent` or `tw.hsra.article-14.consent-information` rather than a merged universal element list
- [ ] If the selected GDPR facts resolve direct collection, participant information points to `eu.gdpr.article-13.direct-collection-information`; if they resolve collection elsewhere, it points to `eu.gdpr.article-14.indirect-collection-information`
- [ ] Waiver, exception, signature, assent, representative, recording, community-governance, sector, and institution-specific questions absent from the registry are visibly `unprofiled`
- [ ] Online-survey language accurately says whether the platform, institution, or research team collects or can access IP addresses, cookies, device identifiers, timestamps, contact fields, or other metadata
- [ ] A statement that metadata is not recorded is used only after platform settings and actual exports have been verified; unknown behavior is disclosed as unknown
- [ ] An electronic `I agree` interaction is described as an interaction record, not automatically as legally sufficient consent or signature

### 8.4 Data-Handling Facts — Illustrative Technical Planning

These prompts do not establish an authority-defined anonymity,
de-identification, or compliance status:

- [ ] Direct identifiers, quasi-identifiers, quotations, rare attributes, and small-cell risks are inventoried
- [ ] Every identifier/re-link key has a named holder, access boundary, purpose, and retention state
- [ ] Platform collection, exports, logs, backups, recipients, transfers, encryption, access controls, retention, destruction, and incident handling are documented
- [ ] Participant-facing statements match the actual data flow and withdrawal/deletion feasibility
- [ ] Terminology is bound to the named convention in `shared/references/irb_terminology_glossary.md`

### 8.5 Population and Context Facts — Illustrative and Unprofiled

| Population or context | Facts/questions to prepare; no pathway or requirement implied |
|---|---|
| Minors or participants with uncertain decision-making capacity | age, capacity, representative/assent questions, accessible explanation, and the applicable authority's process |
| Persons with disabilities | accessibility needs, communication format, capacity assumptions, support persons, and accommodation plan |
| Students, employees, or dependent relationships | recruitment authority, grading/employment effects, alternatives, privacy, and role separation |
| Indigenous peoples or communities | the specific community-governance authority/convention, collective and individual interests, data governance, and engagement expectations |
| Economically constrained participants | compensation, alternatives, dependency, undue-influence questions, and local institutional assessment |
| Incarcerated or otherwise institutionally confined participants | custodial setting, permission structure, voluntariness/coercion risks, privacy, and the applicable authority's process |

- [ ] Relevant population and contextual facts have been recorded without treating identity or vulnerability as an automatic review level
- [ ] Proposed safeguards and unresolved questions are presented to the responsible institution without a verdict
- [ ] Current institutional timeline, training, submission, reporting, and authorization requirements are requested; absent a dated response, they remain `unknown/unprofiled`

> For the portable fact flow, exact requirement anchors, survey metadata disclosure rule, and illustrative Taiwan/institution planning questions, see `references/irb_decision_tree.md`. Do not treat that reference as authorization.

---

## Quick Audit Checklist (Pre-Delivery Self-Check)

Before delivery, confirm ALL items (this is a self-check, not a veto):

- [ ] AI disclosure present and accurate
- [ ] All references spot-checked (minimum 20%)
- [ ] No fabricated citations detected
- [ ] Dual-use assessment completed
- [ ] Fair representation reviewed
- [ ] Data-source bases and unresolved legal/ethical questions documented
- [ ] Conflicts of interest disclosed
- [ ] Reproducibility documentation provided
- [ ] Writing is inclusive and respectful
- [ ] Report benefits stated audience without causing foreseeable harm
- [ ] If human-subjects activity is possible, are exact authority pointers or unresolved states, institutional questions, and the `institutional determination required` boundary visible?
