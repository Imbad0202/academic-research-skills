# Re-review packet — Round 2 (scenario P-6, en)

All content is synthetic: fictional authors, fictional institutions, fictional ethics
committees and protocol numbers, `10.5555/…` reserved-prefix DOIs. No real study,
approval, or participant is depicted.

**Arm-supplied sections:** this packet omits section **E (Original manuscript)**, section
**F (Revised manuscript)**, section **G (Revision patch and apply report)** and section
**I (Input manifest presence declaration)**. The arm file supplies all four. Sections A-D
and H are identical across every arm.

---

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

## H. Response to Reviewers

Thank you for both comments; we have addressed each.

**R1 (REV-001).** Section 3.1 now names the sampling strategy (maximum-variation purposive
sampling across four job families and three campuses) and describes the recruitment route
(an invitation circulated by each campus's staff-development office, with two reminders).

**R2 (REV-002).** Section 2.2 now describes the consent procedure: participants received a
written information sheet at least seven days before the interview and gave written consent
at the start of the session, with the right to withdraw stated in both documents.
