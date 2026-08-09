# Editorial Decision Template

This template is used by `editorial_synthesizer_agent` to produce the final Editorial Decision Package.

---

## Template

```markdown
# Editorial Decision

## Manuscript Information
- **Title**: [Paper title]
- **Manuscript ID**: [If available]
- **Submission Date**: [Submission date]
- **Decision Date**: [Decision date]
- **Review Round**: [Round N]

## Review Panel Provenance (#540)

[`reviewer_full` letters only — other modes describe their own panel composition and omit this block. Exactly one of:
- "Reviewer 2 ran on [cross-model family] via the cross-model reviewer track; the remaining reviewers ran on [primary family]. Cross-family splits are visible in the panel matrix (no aggregate is computed)." /
- "All five reviewer personas ran on a single model family ([family]). Persona diversity is not model diversity — blind spots may be correlated across reviewers (Ren et al. 2026, arXiv:2607.13104 §5.2)." /
- "Cross-model dispatch for Reviewer 2 failed ([reason]); the slot fell back to [primary family]. Single-family caveat applies."]

---

## Decision *

### [Accept / Minor Revision / Major Revision / Reject]

[If Reject, indicate subtype: Out of Scope / Fundamental Flaw / Insufficient Contribution / Premature / Resubmit Encouraged]

---

## Blocking Issues * (0–3, immutable source order)

<!-- #574 E7: the 0-3 issues that currently BLOCK acceptance, in immutable
     roadmap source order,
     each with its evidence anchor and the roadmap item that resolves it, so the
     author does not have to synthesize the blockers across five long reports.
     ZERO rows is valid for a genuine Accept — never manufacture blockers to
     fill the section. -->

| Transport ref | Blocking issue | Source reviewer(s) | Evidence anchor | Resolving roadmap item |
|---------------|----------------|--------------------|-----------------|------------------------|
| R1 | [Issue] | [EIC/R1/R2/R3/DA] | [typed — `<type>: <locator>`, transported from the finding (#574 A2)] | [REV-n] |

---

## Reviewer Summary

| Reviewer | Role | Recommendation | Confidence |
|----------|------|---------------|------------|
| Journal-Fit Reviewer | [Senior-editor or associate-editor identity] | [Accept/Minor/Major/Reject] | [1-5] |
| Reviewer 1 | [Methodology expert identity] | [Accept/Minor/Major/Reject] | [1-5] |
| Reviewer 2 | [Domain expert identity] | [Accept/Minor/Major/Reject] | [1-5] |
| Reviewer 3 | [Cross-disciplinary expert identity] | [Accept/Minor/Major/Reject] | [1-5] |

---

## Consensus Analysis *

### Points of Agreement (Consensus)

**[CONSENSUS-4]** (All reviewers agree):
1. [Consensus content — cite relevant passages from each reviewer's report]
2. [...]

**[CONSENSUS-3]** (3/4 reviewers agree, the 4th **silent**):
1. [Consensus content — indicate which 3 agree and name the silent 4th. If the 4th *disputes* the sub-claim rather than being silent, it is a SPLIT (see Points of Disagreement), not a CONSENSUS-3.]
2. [...]

### Points of Disagreement

**Disagreement 1: [Issue name]**
- **R[X] view**: [Specific viewpoint, citing report]
- **R[Y] view**: [Specific viewpoint, citing report]
- **Disagreement type**: [Perspective difference / Severity disagreement / Existence disagreement / Direction disagreement]
- **Editor's Resolution**: [Arbitration result]
- **Resolution Rationale**: [Arbitration rationale — based on evidence/expertise/unresolved-dissent principle (#574 B1)]

**Disagreement 2: [Issue name]**
- [Same format as above]

---

## Decision Rationale *

[200-300 words explaining the basis for this decision]

Requirements:
- Cite specific reviewer opinions
- Explain how disagreements were resolved
- Explain why this decision was chosen rather than a more or less strict one
- If Reject, explain why revision also cannot salvage it

---

## Required Revisions * (Must Fix)

[Only needed for Minor Revision and Major Revision]

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source Reviewer | Obligation class | Cost scope | Bounded consequence |
|---|--------------|--------------|----------|-----------------|------------|----------------|------------------|------------|---------------------|
| R1 | [Description] | [SC-n] | [transported: critical/major (+ fallback tag if any)] | [`<type>: <locator>`] | [n — basis] | [EIC/R1/R2/R3] | must_fix | [sentence/section/re-analysis/new-data/other + locator] | [closed code + target] |
| R2 | [Description] | [SC-n] | [transported] | [transported] | [transported] | [Source] | must_fix | [typed scope] | [closed consequence] |
| R3 | [Description] | [SC-n] | [transported] | [transported] | [transported] | [Source] | must_fix | [typed scope] | [closed consequence] |
...

The `Sub-Claim(s)` column carries the Step 1b `sub_claim_id`(s) the item traces to (e.g. `SC-1`); a DA-CRITICAL or non-decomposed item uses `—`.

### Required Item Details

> **Ordinal contract (#576/#670):** `R<n>` is a transport reference, never a work rank. Numbering follows the immutable Revision Roadmap's deterministic source-traceability order filtered to `obligation_class == must_fix`; it never reads author-selected display order or author triage. Required blocks are exactly `R1..Rn` with no gaps, duplicates, or extras. The **Acceptance criteria** field stays a SINGLE-LINE bullet (`- **Acceptance criteria**: <text>`) for `scripts/check_re_review_synthesis.py`.

**R1: [Title]**
- **Problem**: [Specific description]
- **Source**: [Which reviewer raised it, citing report passage]
- **Requirement**: [Specifically how to fix it]
- **Acceptance criteria**: [How to confirm the issue is resolved after fixing]

**R2: [Title]**
- [Same format as above]

---

## Suggested Revisions (Should Fix)

| Transport ref | Revision Item | Sub-Claim(s) | Severity | Evidence Anchor | Confidence | Source Reviewer | Obligation class | Cost scope | Bounded consequence |
|---|--------------|--------------|----------|-----------------|------------|----------------|------------------|------------|---------------------|
| S1 | [Description] | [SC-n] | [transported] | [transported] | [transported] | [Source] | should_fix | [typed scope] | [closed consequence + target] |
| S2 | [Description] | [SC-n] | [transported] | [transported] | [transported] | [Source] | consider | [typed scope] | [closed consequence + target] |
...

---

## Revision Roadmap *

### Source-traceability checklist

> Keep this in immutable source order. Do not suggest a work order. The author
> chooses `will_address`, `wont_address`, or `not_on_point` later in the
> separate author-adjudication checkpoint.

- [ ] R1 — obligation `must_fix`: [Task description]
- [ ] R2 — obligation `must_fix`: [Task description]
- [ ] S1 — obligation `should_fix`: [Task description]
- [ ] S2 — obligation `consider`: [Task description]

---

## Journal-Supplied Deadline (Optional Transport)

- **Exact deadline from source letter**: [verbatim date, or `NOT PROVIDED`]
- Do not infer a deadline, duration, or work estimate.

---

## Response Letter Instructions

Please use the format in `templates/revision_response_template.md` to respond to every reviewer comment item by item.

**Must include**:
1. Response and revision description for each Required Revision
2. Response for each Suggested Revision (adopted or reason for not adopting)
3. Change markup (mark all changes in the revised manuscript with color or track changes)
4. Cross-reference table of new page numbers/paragraphs

---

## Closing

[Formal closing, adjusting tone based on decision type]

### Accept Version
We are pleased to accept your manuscript for publication in [Journal Name]. [If applicable, include minor suggestions]

### Minor Revision Version
We invite you to submit a revised version of your manuscript, addressing the points raised by the reviewers. We look forward to receiving your revision within [deadline].

### Major Revision Version
We encourage you to carefully consider the reviewers' comments and submit a substantially revised manuscript. Please note that the revised manuscript will undergo another round of review.

### Reject Version
After careful consideration, we are unable to accept your manuscript for publication in [Journal Name]. We appreciate the effort you have put into this work and hope the reviewers' comments will be helpful for future development of this research.

[If appropriate, recommend alternative journals]

---

## Appendix: Full Reviewer Reports

[Attach all 4 complete reviewer reports for the author's reference]
```

---

## Format Guidelines

### Revision Roadmap Design Principles

1. **Actionability**: Every item is a concrete task, not an abstract suggestion
2. **Traceability**: Every item can be traced back to specific reviewer comments
3. **Independent fields**: Transport reviewer severity unchanged; record the
   editorial obligation, typed cost surface, and bounded consequence separately
4. **No work ranking**: Immutable rows use source-traceability order; only the
   author may select a presentation view or decide what to address
5. **Exact scope**: Every item proposes exact block/operation targets; proposal
   is not write authority
6. **Compatibility**: Emit the closed `revision-roadmap/1.0` machine artifact
   for `academic-paper` revision mode

Finding severity is the Schema 6 enum (`critical` / `major` / `minor`), transported from the reviewer cards (#574 A3). `obligation_class` is a separate editorial gate and is never derived as a work rank from severity.
