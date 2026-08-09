# #680 Human-subjects authority-reference migration

## Decision

The shared human-subjects references are portable navigation aids. They collect
facts and point to the exact authority records selected under the #666 contract;
they do not choose a review pathway, merge jurisdictions, or become an authority.

This migration removes the remaining universalized Exempt / Expedited / Full
Board taxonomy, country-to-country translations, and unanchored consent or
privacy claims. It does not add an authority profile, expand a bounded profile,
or emit a determination.

The canonical authority artifacts are:

- `shared/references/human_subjects_authority_protocol.md`
- `shared/human_subjects_authority_registry.json`
- a replay-validated `resolved-human-subjects-authority-context/1.0` artifact

Every consumer must preserve the #665 output boundary: the review pathway is
`institutional determination required`; readiness and authorization remain
independent; no ARS result authorizes recruitment, consent, access to identifiable
data, intervention, or data collection.

## Portable navigation surface

The portable references may ask authors to record facts such as:

- human-participant interaction or intervention;
- source and identifiability of data or specimens;
- study purpose, procedures, risks, benefits, and populations;
- recruitment, voluntariness, power relationships, and safeguards;
- data collected by an online platform, including metadata and identifiers;
- institutions, sites, funders, data locations, and cross-border transfers;
- current institutional forms, training, contacts, and process estimates.

These facts never map directly to Exempt, Expedited, Full Board, approval,
exemption, legality, or readiness. Missing profile selection or unresolved
applicability remains visible and keeps the #666 downstream gate closed.

The terms `anonymity`, `confidentiality`, `de-identification`, and
`pseudonymization` are operational planning vocabulary. Their legal effect and
the treatment of a retained re-link key depend on the selected governing
convention or authority. Examples must disclose the study's actual collection
and handling configuration; they may not promise that an online platform does
not record IP addresses or other metadata unless that fact was verified.

## Profile destinations

Only requirements already present in the bounded #666 V1 registry may be named
as authority destinations:

| Topic | Exact requirement pointer |
|---|---|
| US informed-consent planning | `us.45cfr46.116.informed-consent` |
| Taiwan consent-information planning | `tw.hsra.article-14.consent-information` |
| GDPR lawful basis | `eu.gdpr.article-6.lawful-basis` |
| GDPR special-category research route | `eu.gdpr.article-9.special-category-research` |
| GDPR direct-collection information | `eu.gdpr.article-13.direct-collection-information` |
| GDPR indirect-collection information | `eu.gdpr.article-14.indirect-collection-information` |
| GDPR research safeguards | `eu.gdpr.article-89.1.research-safeguards` |
| GDPR Member-State derogation dependency | `eu.gdpr.article-89.2.member-state-derogation` |

The committee-composition rows
`us.45cfr46.107.irb-composition` and
`tw.hsra.article-7.committee-composition` are committee-governance obligations.
They are not investigator packet or consent-element requirements.

Every named requirement is consumed through the resolved-context pointer,
`obligated_actor`, and `consumer_scopes`. A reference never copies a requirement
summary and presents it as a complete checklist.

## Explicitly unprofiled material

The following material is not silently migrated into V1:

- exemption, limited-review, expedited-review, full-board, waiver, or exception
  pathway rules;
- institution-specific submission forms, training prerequisites, contacts,
  timelines, approval routes, and reporting cadence;
- Taiwan Personal Data Protection Act, clinical-trial, biobank, indigenous, or
  other procedures not represented by a live #666 row;
- GDPR Member-State implementation, international transfers, security measures,
  and data-subject-right procedures beyond the bounded live rows;
- universal special-population procedures or claims that one fact automatically
  selects a pathway.

References may retain these as questions or visibly illustrative planning
examples. They must label the material `illustrative/unprofiled` and direct the
author to the responsible institution or a future authority-profile update.

## Consumer boundaries

- #665 owns non-authorization output grammar, readiness/authorization separation,
  the fixed boundary footer, and the institutional-determination pathway value.
- #666 owns declaration, authority profiles, exact selection, applicability,
  anchors, and the downstream gate. #680 does not modify registry bytes.
- #667 may check packet presence and declared consistency after it validates the
  resolved context. #680 does not decide whether a packet is adequate.
- #669 may later render a rule trace. #680 does not generate, rank, recommend, or
  suppress candidate pathways.

The preregistration-template status surface is outside this reference migration;
it remains a separate #665 output-surface follow-up rather than expanding #680
into a general output audit.

## Mechanical guard

`scripts/check_human_subjects_reference_migration.py` reads only the named
references, consumers, and the local #666 registry. It must fail when:

1. a migration-owned reference or consumer loses its #666 protocol/registry
   pointer;
2. an agent loses or reverses the exact replay-evidence, no-simulated-validation,
   `resolved` + open-gate conditions, adds a second non-canonical positive-use
   paragraph, or lets a missing/unresolved context emit profile-dependent work;
3. a named requirement id is absent from the registry, a canonical table omits
   a live row, or its provision, obligated actor, ordered consumer scopes, or
   authority URL differs from the row-local registry anchor;
4. a committee-governance requirement is promoted as an investigator packet or
   consent item, including a promotion hidden by Markdown line wrapping;
5. a universal scenario-to-pathway table, `Recommended Review Level`, automatic
   vulnerability/sensitivity-to-Full-Board rule, fixed IP-not-recorded promise,
   `IRB will reject` claim, or additive local-plus-Taiwan rule returns; paragraph
   scanning must catch split-line assertions without rejecting a separately
   verified platform/export statement;
6. retained-key terminology again claims an unconditional cross-regime legal
   effect;
7. the two research-architect mirrors drift.

Mutation tests use temporary copies and the local registry. The guard performs no
network request and invokes no model.

## Acceptance

The migration is complete when:

- all three shared references are portable or visibly illustrative/unprofiled;
- consent planning points to exact selected requirement ids rather than a
  universal element list;
- agent consumers require a replay-validated #666 resolved context and preserve
  the #665 unresolved output boundary;
- US and Taiwan rules remain parallel and are never translated into each other's
  taxonomy;
- the B1 pattern oracle uses actor-, lifecycle-, and convention-bound privacy
  terminology and never reclassifies a retained key by itself;
- the registry and live profile digests remain unchanged;
- the #665 and #666 focused suites, mirror checks, migration mutations, spec
  consistency, B1 pattern runtime, and CI manifest lint all pass.
