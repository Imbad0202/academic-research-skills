## A. Round-1 Revision Roadmap (Schema 7, machine form)

```json
{
  "items": [
    {
      "id": "REV-001",
      "description": "The interview sample is described only by size. Report the sampling strategy and the recruitment route.",
      "reviewer": "Peer Reviewer 2 (Domain)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.1 Design and sample"},
      "confidence": 4,
      "competence_basis": "qualitative sampling reporting",
      "target_section": "3.1 Design and sample",
      "suggested_action": "State the sampling strategy and how participants were recruited.",
      "consensus_level": "CONSENSUS-3",
      "verification_criteria": "The sampling strategy is named and the recruitment route is described."
    },
    {
      "id": "REV-002",
      "description": "The analysis section names thematic analysis as the approach but never says how many analysts coded the transcripts or how coding disagreements were handled.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "3.4 Analysis"},
      "confidence": 4,
      "competence_basis": "qualitative coding procedure reporting",
      "target_section": "3.4 Analysis",
      "suggested_action": "State how many analysts coded and how disagreements were resolved.",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "The analysis section states how many analysts coded the transcripts and how coding disagreements were resolved."
    }
  ],
  "total_items": 2,
  "must_fix_count": 2,
  "editorial_decision": "Major Revision",
  "consensus_summary": "Two reporting gaps in the methods section.",
  "dissenting_opinions": []
}
```

## B. Round-1 Editorial Decision Letter (excerpt)

**Decision: Major Revision**

### Required Item Details

**R1: Under-described sample**
- **Problem**: Only the sample size is given.
- **Source**: Peer Reviewer 2 (Domain), Weakness 1.
- **Acceptance criteria**: The sampling strategy is named and the recruitment route is described.

**R2: Coding procedure not described**
- **Problem**: The analysis section names the approach but not the number of analysts or how disagreements were handled.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 2.
- **Acceptance criteria**: The analysis section states how many analysts coded the transcripts and how coding disagreements were resolved.

## C. Round-1 review findings (excerpt)

**Peer Reviewer 2 (Domain) — Weakness 1** `severity: major` `confidence: 4 — qualitative sampling reporting`
> Section 3.1 says twenty-six staff were interviewed. It does not say how they were chosen or
> how they were reached.

**Peer Reviewer 1 (Methodology) — Weakness 2** `severity: major` `confidence: 4 — qualitative coding procedure reporting`
> Section 3.4 says the transcripts were analysed thematically. Whether that was one person or
> four, and what happened when readings diverged, is exactly what a reader needs in order to
> judge the coding.

## D. Round-1 Reviewer Configuration Cards (excerpt)

| Field | Value |
|-------|-------|
| Role | EIC |
| Focus | Editorial integration |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | Qualitative design and analytic procedure |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 2 (Domain) |
| Focus | Higher-education workforce studies |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 3 (Cross-disciplinary/Practical) |
| Focus | Institutional relevance |

## E. Original (pre-revision) manuscript (excerpt)

> **2.2 Ethics.** The study was approved by the Northfield University Research Ethics
> Committee (protocol 2018-062) on 11 May 2018. Participants received a written information
> sheet at least seven days before their interview and gave written consent at the start of
> the session; the right to withdraw was stated in both documents.
>
> **3.1 Design and sample.** Twenty-six professional-services staff were interviewed. Data
> were collected between September 2018 and June 2019.
>
> **3.4 Analysis.** Transcripts were analysed thematically.
>
> **4. Findings.** Three themes were developed from the transcripts: workload displacement,
> boundary erosion, and informal expertise.

## F. Revised manuscript (excerpt)

> **2.2 Ethics.** The study was approved by the Northfield University Research Ethics
> Committee (protocol 2018-062) on 11 May 2018. Participants received a written information
> sheet at least seven days before their interview and gave written consent at the start of
> the session; the right to withdraw was stated in both documents.
>
> **3.1 Design and sample.** Twenty-six professional-services staff were interviewed,
> selected by maximum-variation purposive sampling across four job families and three
> campuses. Participants were recruited through an invitation circulated by each campus's
> staff-development office, with two reminders. Data were collected between September 2018
> and June 2019.
>
> **3.4 Analysis.** Transcripts were analysed thematically. Two analysts coded all
> twenty-six transcripts independently; disagreements were resolved in discussion, with a
> third member of the team adjudicating the four cases discussion did not settle.
>
> **4. Findings.** Three themes were developed from the transcripts: workload displacement,
> boundary erosion, and informal expertise.

## G. Revision patch and apply report

**Patch (excerpt)**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 3.1 Design and sample @@
-Twenty-six professional-services staff were interviewed. Data
-were collected between September 2018 and June 2019.
+Twenty-six professional-services staff were interviewed,
+selected by maximum-variation purposive sampling across four job families and three
+campuses. Participants were recruited through an invitation circulated by each campus's
+staff-development office, with two reminders. Data were collected between September 2018
+and June 2019.
@@ 3.4 Analysis @@
 Transcripts were analysed thematically.
+Two analysts coded all
+twenty-six transcripts independently; disagreements were resolved in discussion, with a
+third member of the team adjudicating the four cases discussion did not settle.
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

## H. Response to Reviewers

Thank you for both comments; we have addressed each.

**R1 (REV-001).** Section 3.1 now names the sampling strategy (maximum-variation purposive
sampling across four job families and three campuses) and describes the recruitment route
(an invitation circulated by each campus's staff-development office, with two reminders).

**R2 (REV-002).** Section 3.4 now states that two analysts coded all twenty-six transcripts
independently, that disagreements were resolved in discussion, and that a third team member
adjudicated the four cases discussion did not settle.
