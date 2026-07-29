# Re-review packet — Round 2 (scenario P-5, en)

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs. The cited prior-validation source is fictional.

**Arm-supplied sections:** this packet omits section **F (Revised manuscript)**, section
**G (Revision patch and apply report)** and section **H (Response to Reviewers)**. The arm
file supplies all three. Sections A-E and I are identical across every arm.

---

## A. Round-1 Revision Roadmap (Schema 7, machine form)

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "The 12-item self-efficacy scale is summed into a composite and used as the key predictor, but no evidence of its measurement quality in this sample is reported. Prior-study reliability is not evidence about this sample.",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "4.2 Measurement"},
      "confidence": 5,
      "competence_basis": "scale reliability and dimensionality assessment",
      "target_section": "4.2 Measurement",
      "suggested_action": "Report internal consistency or a measurement model estimated on this sample.",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "Evidence for the scale's measurement quality in THIS sample is reported: either an internal-consistency coefficient computed on this sample, or a factor / measurement model with fit indices estimated on this sample."
    },
    {
      "id": "REV-002",
      "description": "Missing-data handling is never described.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "4.3 Analytic strategy"},
      "confidence": 4,
      "competence_basis": "missing-data procedures",
      "target_section": "4.3 Analytic strategy",
      "suggested_action": "State the missing-data mechanism assumed and the procedure used.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "The missing-data procedure is named and the proportion of missingness is stated."
    },
    {
      "id": "REV-003",
      "description": "The abstract reports an effect size the results section does not contain.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Editorial",
      "priority": "must_fix",
      "severity": "minor",
      "evidence_anchor": {"kind": "quote", "value": "a moderate predictor of end-of-year attainment (d = 0.55)"},
      "confidence": 5,
      "competence_basis": "internal consistency between abstract and results",
      "target_section": "Abstract",
      "suggested_action": "Reconcile the abstract with the results section.",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "The abstract's reported effect size matches a value present in the results section."
    }
  ],
  "total_items": 3,
  "must_fix_count": 3,
  "editorial_decision": "Major Revision",
  "consensus_summary": "A measurement-evidence gap on the key predictor, plus two reporting items.",
  "dissenting_opinions": []
}
```

## B. Round-1 Editorial Decision Letter (excerpt)

**Decision: Major Revision**

### Required Item Details

**R1: No measurement evidence for the key predictor**
- **Problem**: The 12-item composite carries the analysis; nothing establishes it holds together in this sample.
- **Source**: Peer Reviewer 2 (Domain), Weakness 1.
- **Acceptance criteria**: Evidence for the scale's measurement quality in THIS sample is reported: either an internal-consistency coefficient computed on this sample, or a factor / measurement model with fit indices estimated on this sample.

**R2: Undescribed missing-data handling**
- **Problem**: Neither the mechanism nor the procedure appears.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 2.
- **Acceptance criteria**: The missing-data procedure is named and the proportion of missingness is stated.

**R3: Abstract-results mismatch**
- **Problem**: The abstract reports d = 0.55; no such value appears in the results.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 3.
- **Acceptance criteria**: The abstract's reported effect size matches a value present in the results section.

## C. Round-1 review findings (excerpt)

**Peer Reviewer 2 (Domain) — Weakness 1** `severity: major` `confidence: 5 — scale reliability and dimensionality assessment`
> Section 4.2 names the instrument and cites its original validation. That tells us the scale
> worked in someone else's sample. The composite is the key predictor here; we need to know it
> behaves in THIS one.

**Peer Reviewer 1 (Methodology) — Weakness 2** `severity: major` `confidence: 4 — missing-data procedures`
> There is no missing-data section. With survey data there is always missingness; silence is
> not a procedure.

**Peer Reviewer 1 (Methodology) — Weakness 3** `severity: minor` `confidence: 5 — internal consistency between abstract and results`
> The abstract calls self-efficacy "a moderate predictor of end-of-year attainment
> (d = 0.55)". Section 5 reports b = 0.31 for that same relationship, and no d anywhere.

## D. Round-1 Reviewer Configuration Cards (excerpt)

| Field | Value |
|-------|-------|
| Role | EIC |
| Focus | Editorial integration |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | Analysis and internal consistency |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 2 (Domain) |
| Focus | Educational measurement |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | Practitioner relevance |

## E. Original (pre-revision) manuscript (excerpt)

> **Abstract.** … self-efficacy was a moderate predictor of end-of-year attainment (d = 0.55) …
>
> **4.2 Measurement.** Self-efficacy was measured with the 12-item Academic Self-Efficacy
> Scale (Lin & Ortega, 2021; DOI 10.5555/ases.2021.0043). Items are rated 1-5 and summed.
>
> **4.3 Analytic strategy.** We estimate ordinary least squares models with school fixed
> effects.
>
> **5. Results.** Self-efficacy predicts end-of-year attainment (b = 0.31, SE = 0.09,
> p = .001).

## I. Input manifest presence declaration (§11)

All nine artifacts **present**, `cross_model_active: false`, `round_id: "p5-r2"`.

| Artifact | Presence | Source |
|----------|----------|--------|
| `original_manuscript` | present | packet §E |
| `revised_manuscript` | present | **arm §F** |
| `revision_roadmap` | present | packet §A |
| `editorial_decision_letter` | present | packet §B |
| `response_to_reviewers` | present | **arm §H** |
| `revision_patches` | present, 1 item | **arm §G** |
| `apply_reports` | present, 1 item | **arm §G** |
| `round1_findings` | present | packet §C |
| `round1_config_cards` | present | packet §D |

**Hash stamping.** As in every scenario, manifest `sha256` values and the `<<…>>`
placeholders in the arm's §G are computed and substituted by the dispatcher at dispatch time.
