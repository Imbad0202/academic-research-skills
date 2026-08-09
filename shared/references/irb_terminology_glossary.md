# IRB Terminology Glossary — Convention-Bound Data-Handling Language

**Spec:** v3.6.7 §7.1 — pattern-protection reference for
`research_architect_agent` (survey designer mode), Pattern B1.

**Audience:** Agents drafting participant-facing consent/privacy language and
human authors reviewing instrument drafts.

**Status:** This is an ARS operational drafting convention. It is not a legal
definition set, an authority-selection rule, or a review determination. A term
is usable only with its named governing authority/convention, actor boundary,
data state, and lifecycle. Different regimes can classify the same retained
re-link key differently.

**Why this exists:** Survey drafts often use Anonymity, Confidentiality,
De-identification, and Pseudonymization as if they were interchangeable. That
can make participant-facing statements inaccurate. This glossary keeps the
facts visible while exact authority requirements remain in
`shared/human_subjects_authority_registry.json`.

---

## Record the Operational Facts First

Before choosing a term, record:

1. every actor that collects, receives, stores, or can access the data,
   including the survey platform, institution, research team, processors, and
   recipients;
2. direct identifiers, quasi-identifiers, free text, IP addresses, cookies,
   device identifiers, timestamps, contact fields, and other metadata;
3. whether a linkage/re-link key or other additional information is created,
   who holds it, who can access both sides, and when it is destroyed or becomes
   inaccessible;
4. the purpose, disclosure boundary, security controls, retention, deletion,
   reuse, transfer, publication, and withdrawal/deletion feasibility;
5. the exact governing authority, institutional rule, or technical release
   convention and the test it applies.

Before describing an IP address or other metadata as absent from the collected
record, verify the platform settings and actual data export/log behavior. If a
platform collects metadata that researchers cannot access, say both facts; do
not silently upgrade that scoped boundary to absolute anonymity.

---

## The Four Terms

### Anonymity

**ARS drafting convention (not a universal legal definition):** Within the
explicitly named actor and lifecycle boundary, no identity-response link is
created, retained, or reasonably recoverable. Use an absolute claim such as
"anonymous to everyone" only when the platform/provider and every downstream
actor are included in, and satisfy, that verified boundary.

**Operational facts to support the wording:**

- no direct identifier or respondent-specific contact field within the stated
  boundary;
- platform metadata collection and researcher access are stated accurately;
- no code, token, or key available within the boundary can reconnect identity
  and response;
- quasi-identifier and free-text re-identification risks have been assessed
  under a named project or institutional method.

**Illustrative drafting template — populate only verified facts:**

> "The research team does not ask for your name or contact details and cannot
> link the exported response to you. The survey platform [does/does not/has not
> been verified to] log IP addresses or device metadata; [state access,
> retention, and recipient details]."

**Drift to flag:** Calling a survey absolutely anonymous while collecting a
follow-up email, retaining a researcher-accessible response code, or leaving
platform metadata behavior unstated.

### Confidentiality

**ARS drafting convention (not a universal legal definition):** An identity or
identity-response link may exist, while one or more named actors commit to
bounded access, use, and disclosure. Confidentiality is a handling promise; it
does not mean identifiers were never collected.

**Operational facts to support the wording:**

- identity/linkage holders and access roles are named;
- purposes, recipients, exceptions/limits, and publication treatment are stated;
- security, retention, deletion, reuse, and incident procedures match the
  participant-facing promise.

**Illustrative drafting template — populate only verified facts:**

> "The research team will receive [identity/contact/linkage data]. Access is
> limited to [roles] for [purposes]. Identified data will be retained until
> [event/date] and then [verified disposition]. Reports will [describe actual
> aggregation, quotation, or identification practice]."

**Drift to flag:** Promising confidentiality without naming the actual
collectors/access roles or while the planned publication and retention behavior
contradicts the promise.

### De-identification

**Convention-bound working use:** Data has been transformed and evaluated under
a **named** authority, institutional standard, or technical release test. This
glossary does not define a universal point at which data becomes de-identified,
and key destruction is not a cross-regime definition.

**Operational facts to record:**

- the named convention/test and the dataset/lifecycle stage to which it applies;
- identifiers removed, transformed, retained, or separately held;
- quasi-identifier and auxiliary-data attack assumptions;
- any linkage/re-link code, custodian, access boundary, derivation, disclosure,
  and destruction/inaccessibility state;
- the method, evaluator, threshold, date, and residual-risk statement.

**Illustrative unprofiled authority example:** Under the U.S. HIPAA Privacy Rule,
[45 CFR 164.514(b)](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E/section-164.514)
describes Expert Determination and Safe Harbor routes, while
[45 CFR 164.514(c)](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E/section-164.514)
permits a covered entity to assign a re-identification code subject to stated
conditions. The effect of retaining a re-link key is therefore
convention-specific and cannot be classified portably. HIPAA is not a profile
in the current #666 registry; applicability and full requirements are
`unprofiled` here.

**Illustrative drafting template — populate the named convention and facts:**

> "For [dataset/lifecycle stage], the team applied [named de-identification
> convention/test] on [date]. [Identifiers and transformations]. A re-link code
> [does/does not] remain; it is held by [actor] under [access/disclosure
> conditions]. Residual risk was evaluated by [method/role] as [bounded result]."

**Drift to flag:** Saying only "identifiers were removed," omitting the governing
test, or assuming that the presence/absence of a key has the same legal effect
under every regime.

### Pseudonymization

**GDPR authority-specific definition:**
[GDPR Article 4(5)](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng)
defines pseudonymisation for personal data by reference to processing that
prevents attribution to a specific data subject without additional information,
provided that additional information is kept separately and protected by
technical and organisational measures. Because the definition concerns
personal data, pseudonymised data is not treated as anonymous merely because a
code replaced direct identifiers.

Article 4(5) is a definitional anchor, not a separate requirement row in the
current bounded registry. When the exact GDPR profile is selected and the
applicability facts resolve true,
`eu.gdpr.article-89.1.research-safeguards` points to the bounded Article 89(1)
research-safeguards row, which records that pseudonymisation is assessed where
the research purposes can be fulfilled that way. It does not assert that every
study or every other regime uses the GDPR definition.

**Operational facts to support GDPR-specific wording:**

- the pseudonym/substitution method and the additional information needed for
  attribution;
- separate holders, storage, and access controls;
- who can combine the dataset and additional information and for which purposes;
- retention/destruction state and technical/organisational safeguards.

**Illustrative drafting template — populate only verified facts:**

> "For the selected GDPR context, the working dataset is pseudonymised. Direct
> identifiers are replaced by [method]. The additional information needed to
> reconnect the code to a participant is held separately by [actor], accessible
> to [roles] for [purposes], and retained until [event/date]."

**Drift to flag:** Calling GDPR-pseudonymised data anonymous, or applying the
GDPR term to another authority without naming that authority's own convention.

---

## Quick Distinction Table

| Term | Identity/re-link state under the stated boundary | What the wording communicates | Authority/convention status |
|---|---|---|---|
| **Anonymity** | No identity-response link within a precisely named and verified actor/lifecycle boundary | inability to link within that boundary | ARS drafting convention unless a selected authority defines it |
| **Confidentiality** | Link may exist | limits on access, use, and disclosure | ARS drafting convention plus any selected authority/institutional terms |
| **De-identification** | Depends on the named test; retained-key effect is convention-specific | transformation and bounded residual-risk result | name the governing authority or technical release convention |
| **Pseudonymization** | Under GDPR, attribution requires separately kept additional information | a controlled but still personal-data state in the GDPR context | GDPR Article 4(5); other regimes must be named separately |

---

## Exact #666 Pointers for Participant/Data Language

These identifiers are navigation pointers only. Use them only from an exactly
selected, resolved profile and read the full row, obligated actor, predicate,
consumer scopes, and authority anchor.

| Drafting question | Exact bounded requirement pointer(s) |
|---|---|
| U.S. Common Rule participant consent | `us.45cfr46.116.informed-consent` |
| Taiwan Human Subjects Research Act participant information | `tw.hsra.article-14.consent-information` |
| GDPR lawful-basis record | `eu.gdpr.article-6.lawful-basis` |
| GDPR special-category condition/safeguards | `eu.gdpr.article-9.special-category-research` |
| GDPR information for direct collection | `eu.gdpr.article-13.direct-collection-information` |
| GDPR information for collection elsewhere | `eu.gdpr.article-14.indirect-collection-information` |
| GDPR scientific-research safeguards | `eu.gdpr.article-89.1.research-safeguards` |

The registry does not currently profile HIPAA de-identification, a universal
anonymity test, a universal confidentiality promise, or institution-specific
release thresholds. Mark those bases `unprofiled` rather than fabricating a row
or verdict.

---

## Where This Glossary Is Enforced

The `research_architect_agent` survey designer mode requires consent/privacy
language to pass through this glossary before output. The pattern-protection
clause lives in `deep-research/agents/research_architect_agent.md` under
`PATTERN PROTECTION (v3.6.7)`. Passing through the glossary means checking actual
data flow and attaching the named convention; it does not establish legal
applicability, compliance, review pathway, readiness, or authorization.

---

## Primary Sources and Local Authority Contract

- `shared/references/human_subjects_authority_protocol.md` ([local protocol](human_subjects_authority_protocol.md)) — exact-selection, bounded-profile, pointer-only, and no-verdict contract.
- [Curated #666 authority registry](../human_subjects_authority_registry.json) — requirement ids and row-local primary-source anchors.
- [45 CFR 164.514](https://www.ecfr.gov/current/title-45/subtitle-A/subchapter-C/part-164/subpart-E/section-164.514) — HIPAA de-identification and re-identification-code provisions; illustrative and unprofiled in #666.
- [GDPR Articles 4(5) and 89](https://eur-lex.europa.eu/eli/reg/2016/679/2016-05-04/eng) — pseudonymisation definition and research-safeguards source; only the bounded Article 89(1) requirement is represented by `eu.gdpr.article-89.1.research-safeguards`.
