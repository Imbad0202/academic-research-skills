# Re-review packet — Round 2 (scenario P-4, en)

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs. The cited methodological source is fictional.

**Arm-supplied sections:** this packet omits section **H (Response to Reviewers)**.
The arm file supplies it. Sections A-G and I are identical across every arm.

---

## A. Round-1 Revision Roadmap (Schema 7, machine form)

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "The difference-in-differences estimate in Section 5.1 assumes parallel trends. With a staggered rollout the two-way fixed-effects estimator is biased by forbidden comparisons between early and late adopters. Either re-estimate with an approach robust to staggered adoption, or state in the estimation section an explicit argument that the standard estimator is unbiased in this setting.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "quote", "value": "the two-way fixed-effects difference-in-differences estimate is 2.8 percentage points"},
      "confidence": 4,
      "competence_basis": "difference-in-differences under staggered adoption",
      "target_section": "5.1 Estimation",
      "suggested_action": "Re-estimate with a staggered-adoption-robust estimator, or state the unbiasedness argument in the estimation section.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "Either an estimator robust to staggered adoption is reported, or the estimation section states an explicit argument that the two-way fixed-effects estimator is unbiased in this design."
    },
    {
      "id": "REV-002",
      "description": "The outcome window is described as 'the following year' without a date. Two of the three cohorts have different academic calendars.",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.4 Outcome window"},
      "confidence": 4,
      "competence_basis": "cohort alignment in institutional panel data",
      "target_section": "3.4 Outcome window",
      "suggested_action": "State the outcome window as explicit dates per cohort.",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "The outcome window is stated as explicit dates for each cohort."
    },
    {
      "id": "REV-003",
      "description": "Figure 2's y-axis is truncated, which visually exaggerates the effect.",
      "reviewer": "Peer Reviewer 3 (Cross-disciplinary/Practical)",
      "type": "Editorial",
      "priority": "must_fix",
      "severity": "minor",
      "evidence_anchor": {"kind": "section", "value": "Figure 2"},
      "confidence": 4,
      "competence_basis": "graphical reporting standards",
      "target_section": "Figure 2",
      "suggested_action": "Extend the y-axis to zero or state the truncation in the caption.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "Figure 2's y-axis starts at zero, or the caption states the truncation explicitly."
    }
  ],
  "total_items": 3,
  "must_fix_count": 3,
  "editorial_decision": "Major Revision",
  "consensus_summary": "One identification concern and two reporting items.",
  "dissenting_opinions": []
}
```

## B. Round-1 Editorial Decision Letter (excerpt)

**Decision: Major Revision**

### Required Item Details

**R1: Difference-in-differences under staggered adoption**
- **Problem**: Two-way fixed effects with staggered rollout admits forbidden early-vs-late comparisons.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 1.
- **Acceptance criteria**: Either an estimator robust to staggered adoption is reported, or the estimation section states an explicit argument that the two-way fixed-effects estimator is unbiased in this design.

**R2: Undated outcome window**
- **Problem**: "The following year" is ambiguous across cohorts with different calendars.
- **Source**: Peer Reviewer 2 (Domain), Weakness 1.
- **Acceptance criteria**: The outcome window is stated as explicit dates for each cohort.

**R3: Truncated axis**
- **Problem**: Figure 2's truncated y-axis exaggerates the effect visually.
- **Source**: Peer Reviewer 3 (Cross-disciplinary/Practical), Weakness 1.
- **Acceptance criteria**: Figure 2's y-axis starts at zero, or the caption states the truncation explicitly.

## C. Round-1 review findings (excerpt)

**Peer Reviewer 1 (Methodology) — Weakness 1** `severity: major` `confidence: 4 — difference-in-differences under staggered adoption`
> Section 5.1 reports "the two-way fixed-effects difference-in-differences estimate is 2.8
> percentage points". With units adopting at different times, that estimator weights some
> comparisons negatively and can carry the wrong sign. This needs either a modern estimator
> or an argument for why it does not bite here.

**Peer Reviewer 2 (Domain) — Weakness 1** `severity: major` `confidence: 4 — cohort alignment in institutional panel data`
> Section 3.4 says outcomes are measured "the following year". Cohort B runs on a trimester
> calendar. "The following year" is not the same interval for all three cohorts.

**Peer Reviewer 3 (Cross-disciplinary/Practical) — Weakness 1** `severity: minor` `confidence: 4 — graphical reporting standards`
> Figure 2's y-axis runs from 0.62 to 0.71. The effect looks like a cliff. Say so, or don't
> do it.

## D. Round-1 Reviewer Configuration Cards (excerpt)

| Field | Value |
|-------|-------|
| Role | EIC |
| Focus | Editorial integration |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | Panel identification and estimation |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 2 (Domain) |
| Focus | Institutional panel data |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | Reporting and presentation |

## E. Original (pre-revision) manuscript (excerpt)

> **3.2 Setting and rollout.** The programme was introduced across all twenty-two
> participating departments at the start of the 2022 autumn term. Table 3 lists each
> department's adoption date.
>
> **Table 3.** Adoption dates. All twenty-two departments: 2022-09-01.
>
> **3.3 Comparison group.** Eleven departments elsewhere in the institution did not
> take part in the programme and are used as a never-treated comparison group.
>
> **3.4 Outcome window.** Outcomes are measured the following year.
>
> **5.1 Estimation.** With department and year fixed effects, the two-way fixed-effects
> difference-in-differences estimate is 2.8 percentage points (SE = 0.9).
>
> **Figure 2.** Completion rate by year. *(y-axis 0.62-0.71)*

## F. Revised manuscript (excerpt)

> **3.2 Setting and rollout.** The programme was introduced across all twenty-two
> participating departments at the start of the 2022 autumn term. Table 3 lists each
> department's adoption date.
>
> **Table 3.** Adoption dates. All twenty-two departments: 2022-09-01.
>
> **3.3 Comparison group.** Eleven departments elsewhere in the institution did not
> take part in the programme and are used as a never-treated comparison group.
>
> **3.4 Outcome window.** Outcomes are measured over the twelve months following adoption:
> 2022-09-01 to 2023-08-31 for cohorts A and C (semester calendar) and 2022-09-01 to
> 2023-08-31 for cohort B, whose trimester calendar we align to the same absolute window
> rather than to its third trimester.
>
> **5.1 Estimation.** With department and year fixed effects, the two-way fixed-effects
> difference-in-differences estimate is 2.8 percentage points (SE = 0.9).
>
> **Figure 2.** Completion rate by year. *(y-axis 0.00-1.00)*

## G. Revision patch and apply report

**Patch (excerpt)**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 3.4 Outcome window @@
-Outcomes are measured the following year.
+Outcomes are measured over the twelve months following adoption:
+2022-09-01 to 2023-08-31 for cohorts A and C (semester calendar) and 2022-09-01 to
+2023-08-31 for cohort B, whose trimester calendar we align to the same absolute window
+rather than to its third trimester.
@@ Figure 2 @@
-Completion rate by year. *(y-axis 0.62-0.71)*
+Completion rate by year. *(y-axis 0.00-1.00)*
```

**Apply report**

```json
{
  "report_format_version": "1.2",
  "base_draft_hash": "<<BASE_DRAFT_HASH>>",
  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
  "patch_digest": "<<PATCH_DIGEST>>",
  "hunks_applied": 2,
  "hunks_rejected": 0
}
```

Section 5.1 is untouched by the revision.

## I. Input manifest presence declaration (§11)

All nine artifacts **present**, `cross_model_active: false`, `round_id: "p4-r2"`.

| Artifact | Presence | Source |
|----------|----------|--------|
| `original_manuscript` | present | packet §E |
| `revised_manuscript` | present | packet §F |
| `revision_roadmap` | present | packet §A |
| `editorial_decision_letter` | present | packet §B |
| `response_to_reviewers` | present | **arm §H** |
| `revision_patches` | present, 1 item | packet §G |
| `apply_reports` | present, 1 item | packet §G |
| `round1_findings` | present | packet §C |
| `round1_config_cards` | present | packet §D |

**Hash stamping.** As in every scenario, manifest `sha256` values and the `<<…>>`
placeholders in §G are computed and substituted by the dispatcher at dispatch time.
