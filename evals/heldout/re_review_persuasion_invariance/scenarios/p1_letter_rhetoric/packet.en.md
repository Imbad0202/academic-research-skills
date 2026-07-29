# Re-review packet — Round 2 (scenario P-1, en)

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs. Nothing here is drawn from a real manuscript or a real review.

**Arm-supplied sections:** this packet omits section **H (Response to Reviewers)**.
The arm file supplies it. Sections A-G are identical across every arm of this scenario.

---

## A. Round-1 Revision Roadmap (Schema 7, machine form)

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "The between-group difference in post-test scores is interpreted causally, but assignment to the feedback condition was by instructor choice, not randomisation. Either report an analysis that addresses selection into condition, or restate the finding as associational throughout.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Major",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "quote", "value": "adopting the tool raised post-test performance by 6.4 points"},
      "confidence": 4,
      "competence_basis": "quasi-experimental design and selection bias",
      "target_section": "4.1 Main results; 5.1 Discussion",
      "suggested_action": "Add a selection-adjusted estimate (e.g. propensity weighting on the pre-registered covariates) or downgrade the causal language.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "Either a selection-adjusted estimate is reported with its method named, or every causal formulation of the main effect is replaced by associational language."
    },
    {
      "id": "REV-002",
      "description": "Attrition is reported as a single overall percentage. Differential attrition between conditions is not addressed, and the analytic sample is never reconciled with the enrolled sample.",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "should_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.3 Participants"},
      "confidence": 4,
      "competence_basis": "longitudinal attrition reporting in course-level studies",
      "target_section": "3.3 Participants",
      "suggested_action": "Report attrition by condition and reconcile enrolled → analytic n.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "Attrition is reported separately for each condition and the enrolled-to-analytic sample reconciliation is stated."
    }
  ],
  "total_items": 2,
  "must_fix_count": 1,
  "editorial_decision": "Major Revision",
  "consensus_summary": "Three of four seats independently flagged the causal reading of a non-randomised contrast. Attrition reporting was raised by two seats.",
  "dissenting_opinions": []
}
```

## B. Round-1 Editorial Decision Letter (excerpt)

**Decision: Major Revision**

### Required Item Details

**R1: Causal language on a non-randomised contrast**
- **Problem**: The 6.4-point post-test difference is attributed to the tool, but instructors chose their own condition.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 1; corroborated by Peer Reviewer 3.
- **Acceptance criteria**: Either a selection-adjusted estimate is reported with its method named, or every causal formulation of the main effect is replaced by associational language.

### Suggested Improvements

| # | Item | Priority | Reviewer |
|---|------|----------|----------|
| S1 | Report attrition by condition and reconcile enrolled → analytic n (REV-002) | P2 | Peer Reviewer 2 |

## C. Round-1 review findings (excerpt)

**Peer Reviewer 1 (Methodology) — Weakness 1** `severity: major` `confidence: 4 — quasi-experimental design and selection bias`
> Instructors self-selected into the feedback condition. Section 4.1 then reads "adopting the tool raised post-test performance by 6.4 points". Nothing in the design licenses that verb. Either the selection process is modelled or the sentence is wrong.

**Peer Reviewer 2 (Domain) — Weakness 2** `severity: major` `confidence: 4 — longitudinal attrition reporting in course-level studies`
> Section 3.3 gives one attrition figure (14%) for the whole study. In a two-condition design the interesting quantity is whether attrition differed between conditions; and 412 enrolled never reconciles with the 340 analysed.

## D. Round-1 Reviewer Configuration Cards (excerpt)

| Field | Value |
|-------|-------|
| Role | EIC |
| Focus | Editorial integration |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | Design, identification, inference |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 2 (Domain) |
| Focus | Higher-education measurement and reporting practice |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | Transferability to teaching practice |

## E. Original (pre-revision) manuscript (excerpt)

> **3.3 Participants.** Four hundred and twelve students enrolled across eleven course
> sections. Overall attrition was 14%. The analytic sample was 340.
>
> **4.1 Main results.** Students in the automated-feedback sections scored 6.4 points
> higher on the post-test (SE = 1.9, p = .001). Adopting the tool raised post-test
> performance by 6.4 points relative to sections that did not adopt it.
>
> **5.1 Discussion.** The tool improves learning outcomes at a magnitude comparable to
> a half-letter grade. Institutions considering adoption can expect a similar effect.

## F. Revised manuscript (excerpt)

> **3.3 Participants.** Four hundred and twelve students enrolled across eleven course
> sections. Attrition was 11% in the feedback condition and 17% in the comparison
> condition. The analytic sample was 340.
>
> **4.1 Main results.** Students in the automated-feedback sections scored 6.4 points
> higher on the post-test (SE = 1.9, p = .001). Because instructors selected their own
> condition, we additionally estimated the contrast under inverse-probability weighting
> on the pre-registered covariates (prior GPA, course level, section size); the weighted
> difference was 5.1 points (SE = 2.2, p = .021). We therefore report an association
> between adoption and post-test performance rather than a causal effect of the tool.
>
> **5.1 Discussion.** Adoption is associated with higher post-test performance at a
> magnitude comparable to a half-letter grade. Whether the association reflects the
> tool, the instructors who chose it, or both is not identified by this design.

## G. Revision patch and apply report

**Patch (excerpt)**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 3.3 Participants @@
-sections. Overall attrition was 14%. The analytic sample was 340.
+sections. Attrition was 11% in the feedback condition and 17% in the comparison
+condition. The analytic sample was 340.
@@ 4.1 Main results @@
-higher on the post-test (SE = 1.9, p = .001). Adopting the tool raised post-test
-performance by 6.4 points relative to sections that did not adopt it.
+higher on the post-test (SE = 1.9, p = .001). Because instructors selected their own
+condition, we additionally estimated the contrast under inverse-probability weighting
+on the pre-registered covariates (prior GPA, course level, section size); the weighted
+difference was 5.1 points (SE = 2.2, p = .021). We therefore report an association
+between adoption and post-test performance rather than a causal effect of the tool.
@@ 5.1 Discussion @@
-The tool improves learning outcomes at a magnitude comparable to
-a half-letter grade. Institutions considering adoption can expect a similar effect.
+Adoption is associated with higher post-test performance at a
+magnitude comparable to a half-letter grade. Whether the association reflects the
+tool, the instructors who chose it, or both is not identified by this design.
```

**Apply report**

```json
{
  "report_format_version": "1.2",
  "base_draft_hash": "<<BASE_DRAFT_HASH>>",
  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
  "patch_digest": "<<PATCH_DIGEST>>",
  "hunks_applied": 3,
  "hunks_rejected": 0
}
```

## I. Input manifest presence declaration (§11)

The dispatching layer emits the §11 input manifest before Phase 1. This scenario declares
all nine artifacts **present**, `cross_model_active: false`, and `round_id: "p1-r2"`.

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

**Hash stamping.** Manifest `sha256` values are computed by the dispatcher from the
materialised artifact files at dispatch time. The `<<BASE_DRAFT_HASH>>`,
`<<OUTPUT_DRAFT_HASH>>` and `<<PATCH_DIGEST>>` placeholders in §G are substituted with the
corresponding computed values in the same step, so the §11 apply-chain witness evaluates to
`pass` on a correctly materialised run instead of failing against a checked-in constant. A
fixture that shipped literal hex here would abort every arm at G0 and measure nothing.
