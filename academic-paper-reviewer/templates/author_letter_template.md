# Author Letter Template (#1078)

The author letter is the review written for the author. It is rewritten from the finished Editorial Decision Package by the dispatching session, after the package's last write, and it changes nothing in the package. Its inputs are the finished package, the Coverage section from Phase 0, the Phase 2 reports (for strengths and questions only), and the result of `scripts/check_author_letter.py`. The package stays the record that `scripts/check_panel_synthesis.py`, re-review, the revision coach, and `academic-pipeline` read; none of them reads this letter.

## Rules

1. Write the whole letter in the user's language, including any fixed phrase such as "none"; only a quotation of the manuscript (Rule 4) keeps the manuscript's language. Use the headings below in that language: the Traditional Chinese column when the user writes Traditional Chinese, the English column when the user writes English, and a translation of the English column for any other language. Keep the order of the parts: the appendix heading is the letter's last level-2 heading, and the item map is the appendix's last level-3 subsection; `scripts/check_author_letter.py` reads them by that position.
2. The letter does not change the decision, add, drop, or change a finding or a revision, or rank the required changes. Every required and suggested revision in the package appears in the letter once. A strength or question from a Phase 2 report is left out when the package's Editor's Resolution rejected the point or a revision already covers it.
3. Keep machine lines and internal ids out of the whole letter, the appendix included: no `dimension_verdicts:`, `fired_conditions:`, `editorial_decision=`, transport refs (`R<n>`, `S<n>`) outside the item map, `REV-<n>`, `SC-<n>`, finding ids, consensus tags, severity-source tags, calibration lines, HTML comments, or fenced code blocks. `scripts/check_author_letter.py` checks the whole letter for these, except a bare `R1` or `S1`, which it does not search for because a manuscript location such as "Table S1" has the same form. Number the changes in one sequence (`1.`, `2.`, `3.`, …) across the required and suggested changes. Only the changes use a numbered list; a list in any other part uses bullets. The script does not check the numbering.
4. In every language, use only `“…”` or `「…」` as quotation marks, and only around words copied from the manuscript; give a reviewer's point, a suggested wording, or a term in your own words, without any quotation marks (`"…"`, `'…'`, `‘…’`, `『…』`, `« »`, and `„ “` included). Copy a quotation exactly, and keep it on one line. Put no other quotation mark inside a quotation: if the words you want to quote hold one, quote a shorter part without it, or give the point in your own words. `scripts/check_author_letter.py` checks each quotation in `“…”`, `"…"`, `‘…’`, `「…」`, or `『…』` against the manuscript with the match of the reviewer claim check (#1002). That match applies NFC, folds case, makes each whitespace run one space, removes the double quotation marks `"` `“` `”`, reads `‘` `’` as `'`, and keeps `「」`, `『』`, and every other mark; it does not check whole words, it does not read other quotation marks, and an unpaired or empty mark can pair with the wrong mark and leave the words after it unchecked, so the exact copy is yours to make. A line break between two CJK characters, in the letter or in the manuscript file, becomes a space, so a true quotation across such a break is reported as not found: quote a shorter part that does not cross it, or give the point in your own words.
5. Give each change its location in the manuscript in square brackets, as the package gives it (section, table, figure, appendix, or page), and say what to change.
6. Group the required changes by topic, with a short topic line over each group. Grouping is not a work order; do not say which item to do first.
7. When a part has nothing to say (no required changes for an Accept, no suggested changes, no questions), keep its heading and say so in one line in the user's language. With no changes at all, the item map is the table's header row and delimiter row, with no rows after them.
8. When `scripts/check_author_letter.py` still reports a problem after one correction, put one line under the title, in the user's language, that names each kind of problem left (for example, a quotation not found, an internal id in the letter, or an item map that does not match) and says that the decision package is the record. Do not repeat the quotation or the id in that line. When the script cannot run at all, put one line under the title, in the user's language, that says the letter check did not run and that the decision package is the record.

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
- **Suggested changes.** Every should-fix and consider revision, numbered after the required changes, each item in the same form (location in square brackets, what is wrong, what to change), with no topic lines.
- **Questions for the authors.** Questions the reviewers asked, in your own words, as bullets. When there are none, say so in the user's language (for example, `無。` in Traditional Chinese).
- **How this review was run.** The AI-simulated reviewer roles that ran (the full panel is five: Journal-Fit Reviewer, three peer reviewers, Devil's Advocate) and an editorial synthesis, as the package's provenance block reports them. Say that this letter is for reading, and that a re-review or the revision coach takes the decision package, not this letter.
- **Limits of this review.** It is AI-simulated and it is not calibrated against human reviewers. Name each part of the manuscript that the Coverage section of Phase 0 marks as not read or not readable, without naming Phase 0 or the Coverage section, or say that the whole manuscript was read. When no manuscript file was given, or the script could not read it, say that the quotation check did not run.
- **Reviewer summaries.** One or two sentences for each seat, from Part 3 of the package.
- **Advisory checks.** One line for each attachment of the package (acronym check, suggested-reference check, reviewer claim check) that says what it found, that it is turned off, or that it did not run. These checks do not change the decision, and nothing in the body comes from them: no decision reason, strength, change, or question.
- **Item map.** One table of exactly two columns, and nothing else with a pipe, with one row for each numbered change: the item number, then the record ref. Write the header in the user's language (Traditional Chinese: `| 項次 | 審查紀錄編號 |`); the second column holds the transport ref of the package row:

```markdown
| Item | Record ref |
|------|------------|
| 1 | R1 |
| 2 | R2 |
| 3 | S1 |
```

With no changes, the item map keeps only the first two lines of this table.
