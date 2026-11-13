# Author Letter Template (#1078)

The author letter is the review written for the author. It is rewritten from the finished Editorial Decision Package by the dispatching session, after the package's last write, and it changes nothing in the package. The package stays the record that `scripts/check_panel_synthesis.py`, re-review, the revision coach, and `academic-pipeline` read; none of them reads this letter.

## Rules

1. Write the whole letter in the user's language. Use the headings below in that language: the Traditional Chinese column when the user writes Traditional Chinese, the English column when the user writes English, and a translation of the English column for any other language.
2. The letter adds nothing the package does not say. It does not change the decision, add or drop a finding, or rank the required changes. Every required and suggested revision in the package appears in the letter once.
3. Keep machine lines and internal ids out of the body: no `dimension_verdicts:`, `fired_conditions:`, `editorial_decision=`, transport refs (`R<n>`, `S<n>`), `REV-<n>`, `SC-<n>`, finding ids, consensus tags, severity-source tags, calibration lines, or HTML comments. Number the items 1, 2, 3 instead. The only place for transport refs is the item map in the appendix.
4. Use quotation marks (`“…”`, `"…"`, `「…」`, `『…』`) only for words copied from the manuscript. Give a reviewer's point in your own words, without quotation marks. `scripts/check_author_letter.py` checks every quotation against the manuscript.
5. Give each change its location in the manuscript in square brackets, as the package gives it (section, table, figure, appendix, or page), and say what to change.
6. Group the required changes by topic, with a short topic line over each group. Grouping is not a work order; do not say which item to do first.

## Structure

| Part | English heading | Traditional Chinese heading |
|------|-----------------|-----------------------------|
| Title | `# Review Letter` | `# 審查意見` |
| Decision | `## Decision` | `## 審查決定` |
| Strengths | `## Strengths` | `## 優點` |
| Required changes | `## Required Changes` | `## 必須修改` |
| Suggested changes | `## Suggested Changes` | `## 建議修改` |
| Questions | `## Questions for the Authors` | `## 請作者回答的問題` |
| Appendix | `## Appendix` | `## 附錄` |
| How the review ran | `### How This Review Was Run` | `### 審查怎麼進行` |
| Limits | `### Limits of This Review` | `### 這份審查的限制` |
| Reviewer summaries | `### Reviewer Summaries` | `### 各審查人摘要` |
| Advisory checks | `### Advisory Checks` | `### 輔助檢查` |
| Item map | `### Item Map` | `### 項次對照` |

## Content of each part

- **Decision.** The decision from Part 1 of the package and its main reasons, in two to four sentences.
- **Strengths.** What the reviewers found sound, from the reviewer reports and the consensus analysis.
- **Required changes.** Every must-fix revision of the package, as numbered items under topic lines. Each item: location in square brackets, what is wrong, what to change.
- **Suggested changes.** Every should-fix and consider revision, numbered after the required changes, in the same form.
- **Questions for the authors.** Questions the reviewers asked, in your own words. Write "None." when there are none.
- **How this review was run.** Five AI-simulated reviewer roles (Journal-Fit Reviewer, three peer reviewers, Devil's Advocate) and an editorial synthesis, as the package's provenance block reports them.
- **Limits of this review.** It is AI-simulated, it is not calibrated against human reviewers, and the Coverage section of Phase 0 names any part of the manuscript that was not read. Name those parts. When no manuscript file was given, say that the quotation check did not run.
- **Reviewer summaries.** One or two sentences for each seat, from Part 3 of the package.
- **Advisory checks.** One line for each attachment of the package (acronym check, suggested-reference check, reviewer claim check) that says what it found or that it did not run. These checks do not change the decision.
- **Item map.** A table with one row for each numbered change:

```markdown
| Item | Transport ref |
|------|---------------|
| 1 | R1 |
| 2 | R2 |
| 3 | S1 |
```
