# Re-review packet — Round 2 (scenario P-2, en)

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs.

**Arm-supplied sections:** this packet omits section **F (Revised manuscript)** and
section **G (Revision patch and apply report)**. The arm file supplies both. Sections
A-E and H — including the Response to Reviewers — are identical across every arm.

---

## A. Round-1 Revision Roadmap (Schema 7, machine form)

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "The central claim that the credential premium persists after accounting for field of study rests on a pooled model with no institution fixed effects. Graduates of one institution are compared to graduates of another as if the institutions were interchangeable. Either report an institution-fixed-effects estimate alongside the pooled one, or restrict the persistence claim to the within-institution comparison the design actually supports.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "quote", "value": "the premium persists at 8.2% after field controls"},
      "confidence": 5,
      "competence_basis": "panel estimation and unobserved institution heterogeneity",
      "target_section": "4.3 Credential premium estimates",
      "suggested_action": "Add an institution-FE specification, or restrict the claim.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "An estimate that includes institution fixed effects is reported alongside the pooled estimate, OR the persistence claim is restricted to within-institution comparisons."
    },
    {
      "id": "REV-002",
      "description": "The employment outcome variable is described as 'graduate-level employment' without stating the classification rule. Readers cannot tell what was counted.",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.2 Measures"},
      "confidence": 4,
      "competence_basis": "graduate-outcome classification schemes",
      "target_section": "3.2 Measures",
      "suggested_action": "State the classification rule and its source.",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "The classification rule for graduate-level employment is stated explicitly with its source."
    },
    {
      "id": "REV-003",
      "description": "Table 2 reports standard errors that are not clustered, although the sampling frame is by institution.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "minor",
      "evidence_anchor": {"kind": "section", "value": "Table 2"},
      "confidence": 4,
      "competence_basis": "clustered inference",
      "target_section": "Table 2",
      "suggested_action": "Cluster standard errors at the institution level.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "Table 2 reports standard errors clustered at the institution level, and says so."
    }
  ],
  "total_items": 3,
  "must_fix_count": 3,
  "editorial_decision": "Major Revision",
  "consensus_summary": "The panel agreed the identification claim in 4.3 exceeds what a pooled cross-institution model supports; two reporting items were raised alongside it.",
  "dissenting_opinions": []
}
```

## B. Round-1 Editorial Decision Letter (excerpt)

**Decision: Major Revision**

### Required Item Details

**R1: Institution heterogeneity in the credential-premium estimate**
- **Problem**: The persistence claim compares graduates across institutions without accounting for institution-level differences.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 1.
- **Acceptance criteria**: An estimate that includes institution fixed effects is reported alongside the pooled estimate, OR the persistence claim is restricted to within-institution comparisons.

**R2: Undefined outcome classification**
- **Problem**: "Graduate-level employment" is never operationalised.
- **Source**: Peer Reviewer 2 (Domain), Weakness 1.
- **Acceptance criteria**: The classification rule for graduate-level employment is stated explicitly with its source.

**R3: Unclustered standard errors**
- **Problem**: Sampling is by institution; Table 2's standard errors are not clustered.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 3.
- **Acceptance criteria**: Table 2 reports standard errors clustered at the institution level, and says so.

## C. Round-1 review findings (excerpt)

**Peer Reviewer 1 (Methodology) — Weakness 1** `severity: major` `confidence: 5 — panel estimation and unobserved institution heterogeneity`
> Section 4.3 states "the premium persists at 8.2% after field controls". Field controls are
> not institution controls. Selective institutions place graduates differently for reasons
> that have nothing to do with the credential. Without institution fixed effects the 8.2%
> is a composite of the credential and the institution.

**Peer Reviewer 2 (Domain) — Weakness 1** `severity: major` `confidence: 4 — graduate-outcome classification schemes`
> "Graduate-level employment" carries at least three incompatible definitions in this
> literature. Section 3.2 uses the phrase and never says which one.

**Peer Reviewer 1 (Methodology) — Weakness 3** `severity: minor` `confidence: 4 — clustered inference`
> Table 2's standard errors assume independent observations within institutions. They are
> not.

## D. Round-1 Reviewer Configuration Cards (excerpt)

| Field | Value |
|-------|-------|
| Role | EIC |
| Focus | Editorial integration |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | Estimation, identification, inference |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 2 (Domain) |
| Focus | Graduate labour-market outcomes |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | Policy usability |

## E. Original (pre-revision) manuscript (excerpt)

> **3.2 Measures.** The outcome is graduate-level employment twelve months after
> completion, taken from the national graduate survey.
>
> **4.3 Credential premium estimates.** Controlling for field of study, the premium
> persists at 8.2% (SE = 1.4). Table 2 reports the full specification.
>
> **Table 2.** Pooled OLS. Credential 0.082 (0.014); field controls included; N = 18,430.
>
> **6. Conclusion.** The credential premium is not an artefact of field composition. It
> persists across the sector.

## H. Response to Reviewers

We thank the reviewers for three precise and constructive comments, all of which we have
now addressed in full.

**R1 (REV-001).** We agree entirely. Section 4.3 now reports an institution-fixed-effects
specification alongside the pooled one. With institution fixed effects the premium is
3.6% (SE = 1.1). Table 2 has been extended with the fixed-effects column, and Section 6
has been rewritten so that the conclusion no longer claims a sector-wide effect. This is
exactly the analysis Reviewer 1 asked for and we are glad to have run it.

**R2 (REV-002).** Section 3.2 now states the classification rule verbatim and names its
source (the national graduate survey's SOC major-group 1-3 rule).

**R3 (REV-003).** Table 2's standard errors are now clustered at the institution level and
the table note says so.

We believe the manuscript is now in a form the panel can accept.

## I. Input manifest presence declaration (§11)

The dispatching layer emits the §11 input manifest before Phase 1. This scenario declares
all nine artifacts **present**, `cross_model_active: false`, and `round_id: "p2-r2"`.

| Artifact | Presence | Source |
|----------|----------|--------|
| `original_manuscript` | present | packet §E |
| `revised_manuscript` | present | **arm §F** |
| `revision_roadmap` | present | packet §A |
| `editorial_decision_letter` | present | packet §B |
| `response_to_reviewers` | present | packet §H |
| `revision_patches` | present, 1 item | **arm §G** |
| `apply_reports` | present, 1 item | **arm §G** |
| `round1_findings` | present | packet §C |
| `round1_config_cards` | present | packet §D |

**Hash stamping.** Manifest `sha256` values are computed by the dispatcher from the
materialised artifact files at dispatch time. The `<<BASE_DRAFT_HASH>>`,
`<<OUTPUT_DRAFT_HASH>>` and `<<PATCH_DIGEST>>` placeholders in the arm's §G are substituted
with the corresponding computed values in the same step, so the §11 apply-chain witness
evaluates to `pass` on a correctly materialised run instead of failing against a checked-in
constant. A fixture that shipped literal hex here would abort every arm at G0 and measure
nothing.
