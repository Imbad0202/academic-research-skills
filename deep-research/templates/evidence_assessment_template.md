# Evidence Assessment Template

## Purpose
Per-source quality assessment card. Used by the source_verification_agent to systematically evaluate each source entering the research pipeline.

## Assessment Card

```markdown
## Evidence Assessment Card

### Source Identification
- **Citation (APA 7.0)**: [full reference]
- **DOI/URL**: [link]
- **Type**: [journal article / book / report / web / conference paper / thesis / other]
- **Access Date**: [when verified]

---

### Quality Assessment

#### 1. Evidence Level
**Level**: [I / II / III / IV / V / VI / VII]
**Justification**: [why this level]

#### 2. Publication Venue
- **Journal/Publisher**: [name]
- **Indexed in**: [Scopus / WoS / PubMed / DOAJ / other / none]
- **Impact Factor/CiteScore**: [value or N/A]
- **COPE member**: [Yes / No / Unknown]
- **Predatory indicators**: [None / Flags: list]

**Venue Grade**: [Excellent / Good / Adequate / Questionable / Unacceptable]

#### 3. Author Credibility
- **Author(s)**: [names]
- **Affiliation(s)**: [institutions]
- **ORCID**: [if available]
- **Track record**: [publication history in field]
- **Expertise match**: [relevant to topic? Yes/Partial/No]

**Author Grade**: [Excellent / Good / Adequate / Unknown / Questionable]

#### 4. Methodological Quality
- **Design**: [description]
- **Sample**: [size, selection, representativeness]
- **Analysis**: [appropriate for design?]
- **Limitations acknowledged**: [Yes / Partially / No, naming the sections checked / not assessed (read scope: <scope>)]
- **Replicable**: [Yes / Partially / No]
- **Method weaknesses**: [per the Method weaknesses rules below the card]

**Method Grade**: [Excellent / Good / Adequate / Weak / Flawed / Not assessed (read scope: <scope>)]

#### 5. Currency
- **Publication year**: [YYYY]
- **Data collection period**: [if stated]
- **Field velocity**: [Rapid / Moderate / Slow / Foundational]
- **Still current**: [Yes / Conditionally / No]

**Currency Grade**: [Current / Acceptable / Dated / Outdated / Foundational]

#### 6. Conflict of Interest
- **Declared COI**: [None / Listed: details]
- **Funding source**: [source or Not stated]
- **Potential undeclared COI**: [None detected / Possible: details]

**COI Grade**: [Clean / Minor / Moderate / Significant / Critical]

---

### Overall Assessment

| Dimension | Grade |
|-----------|-------|
| Evidence Level | [I-VII] |
| Venue | [Excellent-Unacceptable] |
| Author | [Excellent-Questionable] |
| Method | [Excellent-Flawed] |
| Currency | [Current-Outdated] |
| COI | [Clean-Critical] |
| **Overall** | **[A / B / C / D / F]** |

### Recommendation
- [ ] **Use as primary evidence** (Grade A-B)
- [ ] **Use as supporting evidence** (Grade B-C)
- [ ] **Use with explicit caveats** (Grade C-D)
- [ ] **Do not use** (Grade D-F) — Reason: [specific reason]

### Notes
[Any additional observations, caveats, or context]
```

### Method weaknesses rules (§4)

<!-- method-weaknesses:begin -->
**Method weaknesses (per source, #916).** Information only. Nothing here blocks, gates, scores, or asks the scholar a question.

1. **Named design and failure condition.** Name the specific design, measure, sample, or analysis choice, and the condition under which it would distort the result. "Small sample" alone is not enough; "n = 24 from one site, so the site effect cannot be separated from the treatment" is.
2. **Provenance label on every item.** Mark each item `author-acknowledged` or `reader-inferred`. An `author-acknowledged` item carries a locator in one of the v3.7.3 anchor kinds (`quote`, `page`, `section`, `paragraph`). A `reader-inferred` item is an untested inference and says so.
3. **Bounded absence claims.** A statement that the authors do not address X names the sections that were checked (the #548 search-bounded pattern). If those sections cannot be named, do not make the absence claim.
4. **Fixed aspect checklist.** Use the source's paper-type table in `academic-paper-reviewer/references/review_criteria_framework.md` §2 (empirical, theoretical, review / meta-analysis, case study, policy). Mark each criterion in that table `checked: found`, `checked: none found`, or `not checked`. Stop at the end of the table; do not keep adding items until the list feels complete.
5. **No method-level weakness without the text.** When only the abstract or table of contents is available, or the recorded read scope (`/ars-mark-read --scope`) is `abstract_only`, `toc_only`, or `unknown`, write `not assessed (read scope: <scope>)` and no inferred weaknesses. For `sections`, stay within the declared sections.

Do not turn a weakness into an improvement suggestion or research direction; that step stays with the scholar. Keep the entry short:

```
- **Method weaknesses** (<paper type>; read: <what was read>)
  - checked: found: <criterion>, ... | checked: none found: <criterion>, ... | not checked: <criterion>, ...
  - <design choice>; distorts the result when <condition>. [author-acknowledged, <anchor kind>: <locator>] or [reader-inferred]
```

or, when rule 5 applies, `- **Method weaknesses**: not assessed (read scope: <scope>)`.
<!-- method-weaknesses:end -->

## Batch Assessment Summary

```markdown
## Source Verification Summary

**Date**: [YYYY-MM-DD]
**Sources assessed**: [N]
**Assessor**: source_verification_agent

### Grade Distribution
| Grade | Count | % |
|-------|-------|---|
| A (Excellent) | X | X% |
| B (Good) | X | X% |
| C (Adequate) | X | X% |
| D (Weak) | X | X% |
| F (Unacceptable) | X | X% |

### Flagged Sources
| Source | Issue | Severity | Recommendation |
|--------|-------|----------|---------------|
| [ref] | [issue] | [High/Medium/Low] | [Include with caveat / Exclude] |

### Predatory Journal Alerts
[List any flagged journals]

### Overall Source Base Quality
**Assessment**: [Strong / Adequate / Mixed / Weak]
**Recommendation**: [Proceed / Supplement / Major revision of source base needed]
```

## Usage Notes
- Complete one card per source for full verification
- Batch summary should be produced after all cards are complete
- Minimum spot-check: 20% of sources get full card assessment
- All Grade D/F sources require documented justification
- Any predatory journal flag requires full verification
