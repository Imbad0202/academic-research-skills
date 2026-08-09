# Human-Subjects Authority Context Navigation Aid — Institutional Determination Required

## Purpose

This reference helps the `ethics_review_agent` and `research_architect_agent`
collect protocol facts, bind already-selected authority profiles, and prepare
questions for the responsible institution. It is a navigation aid, not an
authority, authorization tool, or review-pathway classifier.

The controlling local contract is
`shared/references/human_subjects_authority_protocol.md`; the only curated
authority rows available to this aid are in
`shared/human_subjects_authority_registry.json`. Every profile in that registry
is a `bounded_subset`, not a complete statement of any jurisdiction's law or an
institution's policy.

> **Authority boundary (#665/#666/#680):** Mixed-jurisdiction pathway mappings are not part of this reference. ARS output must use `institutional determination required`; applicability, requirements, timing, and authorization remain with the responsible institution and an exactly selected authority profile. Missing or unknown facts remain unresolved and never become a review determination.

---

## 1. Portable Fact Collection — No Pathway Inference

Collect facts without mapping them to `Exempt`, `Expedited`, `Full Board`, or a
similarly named local pathway. Those labels are authority- and
institution-specific; vulnerability, sensitivity, deception, identifiability,
and estimated risk are inputs for human assessment, not automatic pathway
rules.

```
Start
│
├── Record whether the activity involves human subjects
│   └── If unknown, preserve unknown and ask the responsible institution
│
├── Record each candidate review-ethics and data-protection authority
│   └── Do not infer jurisdiction from geography, funder, language, or topic
│
├── Record data, interaction, recruitment, population, and risk facts
│   └── Separate observed facts from researcher assumptions
│
├── Select exact #666 profile id/version/digest pointers only when confirmed
│   └── Leave an axis unresolved when no matching bounded profile is available
│
└── Send facts and unresolved questions to the responsible institution
    └── Output pathway: institutional determination required
```

### 1.1 Exact #666 declared facts

For a #666 context, record `true`, `false`, or `unknown` against these exact
catalogue identifiers. A missing value is unknown, not false.

| Exact fact id | Question to resolve |
|---|---|
| `activity.human_subjects` | Has the author confirmed that the activity involves human subjects? |
| `support.us_hhs_or_common_rule` | Has the author identified a U.S. HHS/Common Rule scope basis? |
| `scope.tw_hsra` | Has the author identified Taiwan's Human Subjects Research Act as a review authority? |
| `scope.eu_gdpr` | Has the author identified the GDPR as a data-protection authority? |
| `processing.personal_data` | Within the selected GDPR scope, does the activity process personal data? |
| `data.special_category` | Does that processing include special-category data? |
| `data.collected_from_subject` | Is the personal data obtained from the data subject rather than elsewhere? |
| `purpose.scientific_research` | Does the processing purpose include scientific research? |
| `gdpr.member_state_research_law_identified` | Has a specific applicable Union or Member State research-derogation law been identified? |

### 1.2 Additional portable planning facts

The following are **illustrative, unprofiled planning facts**. They preserve
useful protocol detail but are not predicates or requirement rows in the current
#666 registry:

- source and provenance of each dataset or specimen;
- direct identifiers, quasi-identifiers, and linkage/re-link keys;
- IP addresses, cookies, device identifiers, timestamps, and other platform
  metadata actually collected or accessible;
- direct interaction, intervention, observation, recordings, and follow-up;
- recruitment channel, compensation, dependency or power relationships, age,
  decision-making capacity, language, and accessibility needs;
- potentially sensitive topics, deception or incomplete disclosure, and the
  physical, psychological, social, economic, informational, or group risks the
  team has identified;
- risk mitigations, access controls, recipients, transfers, retention,
  destruction, reuse, withdrawal handling, and incident response;
- institution-, funder-, community-, sector-, or profession-specific rules and
  the office or person responsible for interpreting them.

Do not convert any single fact or combination in this list into a pathway,
clearance, readiness, compliance, or authorization result.

---

## 2. Exact Bounded Requirement Pointers

Use a row below only after the matching profile has been selected by exact
id/version/digest and the #666 resolved artifact permits profile-dependent use.
The link is the row's primary-source anchor; the requirement id is the navigation
pointer. The table is deliberately exhaustive only for the current bounded
registry, not for the underlying authorities.

### 2.1 Review-ethics axis

| Exact requirement id | Exact provision | Obligated actor | Consumer scopes | Bounded subject | Primary-source anchor |
|---|---|---|---|---|---|
| `us.45cfr46.107.irb-composition` | `45 CFR 46.107` | `institution_or_irb` | `["committee_governance", "pathway_trace"]` | IRB membership and composition | [45 CFR 46.107](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-A/section-46.107) |
| `us.45cfr46.116.informed-consent` | `45 CFR 46.116` | `investigator_and_irb` | `["participant_information", "submission_packet", "pathway_trace"]` | General informed-consent requirements | [45 CFR 46.116](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-A/part-46/subpart-A/section-46.116) |
| `tw.hsra.article-7.committee-composition` | `人體研究法第 7 條` | `research_institution_or_review_committee` | `["committee_governance", "pathway_trace"]` | Review-committee composition | [人體研究法第 7 條（全國法規資料庫中文控制文本）](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=L0020176) |
| `tw.hsra.article-14.consent-information` | `人體研究法第 14 條` | `principal_investigator` | `["participant_information", "submission_packet", "pathway_trace"]` | Information explained before consent | [人體研究法第 14 條（全國法規資料庫中文控制文本）](https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=L0020176) |

Committee-composition rows belong to their stated institutional/committee
actors. This aid must not turn them into investigator submission-packet
requirements. The U.S. and Taiwan rows remain parallel and retain their own
vocabulary; neither is a translation of the other.

### 2.2 Data-protection axis

| Exact requirement id | Exact provision | Obligated actor | Consumer scopes | Bounded subject | Primary-source anchor |
|---|---|---|---|---|---|
| `eu.gdpr.article-6.lawful-basis` | `GDPR Article 6` | `controller` | `["data_governance", "pathway_trace"]` | Identify and document an applicable Article 6 basis; the profile does not select one | [GDPR Article 6](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng) |
| `eu.gdpr.article-9.special-category-research` | `GDPR Article 9` | `controller` | `["data_governance", "pathway_trace"]` | Identify an applicable Article 9 condition and safeguards; the profile does not select the route | [GDPR Article 9](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng) |
| `eu.gdpr.article-13.direct-collection-information` | `GDPR Article 13` | `controller` | `["participant_information", "data_governance", "pathway_trace"]` | Information when data is obtained from the data subject | [GDPR Article 13](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng) |
| `eu.gdpr.article-14.indirect-collection-information` | `GDPR Article 14` | `controller` | `["participant_information", "data_governance", "pathway_trace"]` | Information when data is obtained elsewhere, subject to a separately established exception | [GDPR Article 14](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng) |
| `eu.gdpr.article-89.1.research-safeguards` | `GDPR Article 89(1)` | `controller` | `["data_governance", "pathway_trace"]` | Scientific-research safeguards, including assessment of data minimisation and pseudonymisation | [GDPR Article 89(1)](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng) |
| `eu.gdpr.article-89.2.member-state-derogation` | `GDPR Article 89(2)` | `controller` | `["data_governance", "pathway_trace"]` | A claimed research derogation must point to an identified applicable Union or Member State law | [GDPR Article 89(2)](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng) |

The GDPR rows do not determine whether the GDPR applies, select a lawful basis
or Article 9 condition, identify a Member State law, or authorize processing.

---

## 3. Illustrative Country and Institution Planning

### 3.1 Taiwan institutional-workflow example — illustrative and unprofiled

For a project connected with Taiwan, a useful planning conversation may ask:

1. Which institution or review committee owns the determination?
2. Which local submission system and current forms does it use?
3. Which protocol, participant-information, recruitment, instrument, training,
   data-management, or other materials does that institution request?
4. Which activities, if any, must wait for a documented institutional decision?
5. What current turnaround estimate, amendment process, continuing-reporting
   schedule, and closure process does the institution state?

These are **questions, not Taiwan legal requirements**. The current #666 Taiwan
profile covers only `tw.hsra.article-7.committee-composition` and
`tw.hsra.article-14.consent-information`. It does not profile NSTC or Ministry
of Education funding rules, the Personal Data Protection Act, clinical-trial or
biobank rules, training credentials, submission platforms, timelines, periodic
reports, or a local pathway taxonomy. Record any such item as `unprofiled` and
obtain the responsible authority's current instruction. Do not rename a Taiwan
process with U.S. pathway vocabulary.

### 3.2 Higher-education scenarios — illustrative fact prompts

| Scenario | Portable facts to collect; no determination implied |
|---|---|
| Public statistics analysis | source, publication/access terms, record-level identifiability, linkage with other data, and institutional policy |
| Institutional research data | provenance, authorization, direct/quasi-identifiers, re-link key, access roles, purpose, and data source |
| Student survey or interview | recruitment and power relationship, voluntariness, direct identifiers, platform metadata, topic, recording, and withdrawal handling |
| Teaching intervention | allocation, effect on grades/rights/access, alternatives, instructor-researcher roles, risk, and data collection |
| Mental-health or other sensitive-topic study | data categories, foreseeable harms, disclosure limits, response plan, and—only if the GDPR profile is selected—whether `data.special_category` is true |
| Learning portfolio or classroom observation | expectation of privacy, recorded identifiers, notice/interaction, recording, secondary use, and access |
| Career tracking or longitudinal follow-up | contact data, re-link key, follow-up period, recipients, retention, and withdrawal feasibility |
| Cross-border or multi-institution study | each review-ethics and data-protection authority, lead/participating institution roles, transfers, and unresolved conflicts |

Public availability, anonymity, minimal risk, vulnerability, or sensitivity does
not by itself assign a pathway in this reference.

---

## 4. Participant-Information and Consent Preparation

### 4.1 Authority-bound coverage

There is no universal consent-element checklist in this aid. When the applicable
row resolves true, use its exact pointer and full registry row:

- `us.45cfr46.116.informed-consent` for the bounded U.S. Common Rule consent row;
- `tw.hsra.article-14.consent-information` for the bounded Taiwan Article 14
  information row;
- `eu.gdpr.article-13.direct-collection-information` when the selected GDPR
  context says personal data is obtained from the data subject;
- `eu.gdpr.article-14.indirect-collection-information` when the selected GDPR
  context says personal data is obtained elsewhere.

Do not merge these rows into one universal form. If an authority, element,
waiver/exception, special population, sector, or institutional rule is not in
the registry, label it `unprofiled` and seek the responsible authority's current
requirements.

### 4.2 Portable drafting inventory — illustrative, non-authoritative

The following inventory is useful for drafting and gap questions, but it is not
a list of legally required elements:

- project title; responsible institution, investigator, funder, and contacts;
- purpose, procedures, duration, recordings, alternatives, and participant tasks;
- foreseeable risks/discomforts, possible benefits, compensation, and remedies;
- voluntary-choice and withdrawal statements appropriate to the actual design;
- data categories and sources; collection method; recipients and access roles;
- platform metadata, identifiers, linkage, security, retention, destruction,
  future use, sharing, transfer, publication, and commercial interests;
- complaint, rights, or authority contacts supplied by the responsible regime;
- signature, assent, representative, or electronic-interaction fields requested
  by the responsible institution.

### 4.3 Online-survey disclosure accuracy

Use this **portable drafting convention**: disclose what the selected survey
platform, institution, and research team actually collect or can access. Verify
settings and data exports before saying that an IP address, cookie, device
identifier, timestamp, contact field, or other metadata is not recorded. State
the collector, purpose, access roles/recipients, retention, and deletion or
masking behavior where known; preserve `unknown` where it has not been verified.

An `I agree` control records a participant interaction. This aid does not decide
whether that interaction satisfies consent, signature, documentation, or waiver
requirements under a selected authority or institutional process.

### 4.4 Drafting worksheet — illustrative and unprofiled until bound

```text
Participant Information / Consent Drafting Worksheet

Selected profile pointer(s): [profile id / version / digest]
Applicable requirement pointer(s): [exact requirement ids]
Unprofiled authorities or institutional rules: [list / unknown]

Project and responsible actors: [                              ]
Purpose, procedures, duration, and recordings: [               ]
Risks, benefits, compensation, and remedies: [                 ]
Choice, withdrawal, and limits on withdrawal/deletion: [       ]
Data and metadata actually collected (including platform data): [ ]
Access, recipients, transfers, security, and incident handling: [ ]
Retention, destruction, future use, sharing, and publication: [  ]
Contacts and institution-requested acknowledgement fields: [     ]

Unresolved questions for the responsible institution: [          ]
Review pathway: institutional determination required
```

---

## 5. Data-Handling Technical Planning

Use `shared/references/irb_terminology_glossary.md` for explicitly
convention-bound drafting terms. A technical transformation does not, by itself,
establish an authority-defined legal status.

### 5.1 Illustrative techniques

| Technique | Technical planning purpose; legal effect not asserted |
|---|---|
| Identifier removal or transformation | reduce direct-identification exposure |
| Pseudonym/code assignment | separate working records from additional identifying information while preserving a controlled link |
| Generalisation or aggregation | reduce precision and small-cell disclosure risk |
| Masking | limit visible portions of a field for a stated use |
| Re-identification risk assessment | test plausible combinations and auxiliary-data attacks under a named method or threshold |

### 5.2 Illustrative risk and control prompts

- Can small groups, quotations, rare attributes, dates, locations, or
  institutional characteristics identify a person or community?
- Can other datasets be linked to the planned release or analysis environment?
- Who holds each identifier or re-link key, and who can access both sides?
- Do storage, encryption, logging, export, backup, retention, and destruction
  controls match the participant-facing disclosure?
- Has the team tested the actual platform export for IP addresses and other
  metadata rather than relying on a default-setting assumption?

---

## Researcher Self-Check

Before handing the protocol to the responsible institution:

1. [ ] Have both authority axes been addressed with exact selected profiles or a visible unresolved state?
2. [ ] Are confirmed, false, and unknown facts kept distinct without jurisdiction inference?
3. [ ] Does every authority-bound statement point to an exact #666 requirement id and its selected profile?
4. [ ] Are actor and consumer boundaries preserved, especially for committee-governance rows?
5. [ ] Are country, sector, community, funder, and institutional examples outside the registry labelled `illustrative` or `unprofiled`?
6. [ ] Does survey/privacy wording accurately describe actual identifier and metadata handling?
7. [ ] Are vulnerability, sensitivity, deception, identifiability, and risk treated as facts rather than automatic pathways?
8. [ ] Is the pathway still `institutional determination required`, with timing and authorization obtained separately from the responsible institution?

**Human-subjects boundary:** This navigation aid does not authorize recruitment,
consent, access to identifiable data, intervention, or data collection.
