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
      "description": "The ethics statement names the approving committee, its protocol number and the approval date, but never describes how consent was obtained.",
      "reviewer": "Peer Reviewer 1 (Methodology)",
      "type": "Minor",
      "priority": "must_fix",
      "severity": "major",
      "evidence_anchor": {"kind": "section", "value": "2.2 Ethics"},
      "confidence": 4,
      "competence_basis": "human-subjects reporting requirements",
      "target_section": "2.2 Ethics",
      "suggested_action": "Describe the consent procedure.",
      "consensus_level": "CONSENSUS-4",
      "verification_criteria": "The ethics statement describes how informed consent was obtained from participants."
    }
  ],
  "total_items": 2,
  "must_fix_count": 2,
  "editorial_decision": "Major Revision",
  "consensus_summary": "Two reporting gaps in the methods and ethics sections.",
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

**R2: Consent procedure not described**
- **Problem**: The ethics statement gives committee, protocol number and approval date, but not the consent procedure.
- **Source**: Peer Reviewer 1 (Methodology), Weakness 2.
- **Acceptance criteria**: The ethics statement describes how informed consent was obtained from participants.

## C. Round-1 review findings (excerpt)

**Peer Reviewer 2 (Domain) — Weakness 1** `severity: major` `confidence: 4 — qualitative sampling reporting`
> Section 3.1 says twenty-six staff were interviewed. It does not say how they were chosen or
> how they were reached.

**Peer Reviewer 1 (Methodology) — Weakness 2** `severity: major` `confidence: 4 — human-subjects reporting requirements`
> Section 2.2 gives the committee, the protocol number and the approval date. It never says
> how consent was obtained, which is the part a reader needs in order to judge the procedure.

## D. Round-1 Reviewer Configuration Cards (excerpt)

| Field | Value |
|-------|-------|
| Role | EIC |
| Focus | Editorial integration |

| Field | Value |
|-------|-------|
| Role | Peer Reviewer 1 (Methodology) |
| Focus | Research design and human-subjects procedure |

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
> Committee (protocol 2019-114) on 14 March 2019.
>
> **3.1 Design and sample.** Twenty-six professional-services staff were interviewed. Data
> were collected between September 2018 and June 2019.
>
> **4. Findings.** Three themes were developed from the transcripts: workload displacement,
> boundary erosion, and informal expertise.

## F. Revised manuscript (excerpt)

> **2.2 Ethics.** The study was approved by the Northfield University Research Ethics
> Committee (protocol 2019-114) on 14 March 2019. Participants received a written
> information sheet at least seven days before their interview and gave written consent at
> the start of the session; the right to withdraw was stated in both documents.
>
> **3.1 Design and sample.** Twenty-six professional-services staff were interviewed,
> selected by maximum-variation purposive sampling across four job families and three
> campuses. Participants were recruited through an invitation circulated by each campus's
> staff-development office, with two reminders. Data were collected between September 2018
> and June 2019.
>
> **4. Findings.** Three themes were developed from the transcripts: workload displacement,
> boundary erosion, and informal expertise.

## G. Revision patch and apply report

**Patch (excerpt)**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 2.2 Ethics @@
 Committee (protocol 2019-114) on 14 March 2019.
+Participants received a written
+information sheet at least seven days before their interview and gave written consent at
+the start of the session; the right to withdraw was stated in both documents.
@@ 3.1 Design and sample @@
-Twenty-six professional-services staff were interviewed. Data
-were collected between September 2018 and June 2019.
+Twenty-six professional-services staff were interviewed,
+selected by maximum-variation purposive sampling across four job families and three
+campuses. Participants were recruited through an invitation circulated by each campus's
+staff-development office, with two reminders. Data were collected between September 2018
+and June 2019.
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

**R2 (REV-002).** Section 2.2 now describes the consent procedure: participants received a
written information sheet at least seven days before the interview and gave written consent
at the start of the session, with the right to withdraw stated in both documents.
