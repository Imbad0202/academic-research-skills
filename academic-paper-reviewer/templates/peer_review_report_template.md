# Peer Review Report Template

This template is used by the Journal-Fit Reviewer and Reviewers 1-3. Each reviewer uses the same structure but fills in review content from their respective perspectives.

---

## Usage Instructions

1. Text in `[brackets]` is explanatory and needs to be replaced with actual content
2. Each reviewer must fully complete all required fields (items marked with *)
3. Detailed Comments are section-by-section commentary; only comment on sections relevant to your review focus
4. Language follows the paper's language (Chinese papers reviewed in Chinese, English papers in English)
5. Never emit raw HTML in a reviewer card; mention markup only in inline code. Inside `## Scoring Plan Dissent`, any non-comment raw-HTML tag or delimiter outside inline code aborts as `[DISSENT-RAW-HTML]` and cannot grant a trigger-binding exemption.

---

## Template

```markdown
# Peer Review Report

## Manuscript Information
- **Title**: [Paper title]
- **Manuscript ID**: [If available, enter manuscript ID]
- **Review Date**: [Review date]
- **Review Round**: [Round N review]

---

## Reviewer Information

### Reviewer Role *
[Journal-Fit Reviewer / Peer Reviewer 1 (Methodology) / Peer Reviewer 2 (Domain) / Peer Reviewer 3 (Perspective)]

### Reviewer Identity *
[Identity description configured by field_analyst_agent]

### Review Focus *
[Core focus of this review, 2-3 sentences]

---

## Overall Assessment *

### Recommendation *
[Select one]
- [ ] **Accept** — Can be published directly, only minor formatting changes needed
- [ ] **Minor Revision** — Minor revisions needed, no re-review after revision
- [ ] **Major Revision** — Substantial revisions needed, re-review required after revision
- [ ] **Reject** — Not suitable for publication in this journal

### Confidence Score *
[1-5]
| Score | Meaning |
|-------|---------|
| 5 | Completely within my area of expertise, I am very confident in my assessment |
| 4 | Mostly within my area of expertise, high confidence |
| 3 | Partially within my area of expertise, moderate confidence |
| 2 | Some aspects outside my expertise, somewhat uncertain about my assessment |
| 1 | Mostly outside my expertise, my opinion is for reference only |

Confidence is an uncertainty/scope disclosure only; it never changes consensus counts, severity, decision bearing, or arbitration.

### Summary Assessment *
[150-250 word overall assessment]

Requirements:
- Sentences 1-2: What the paper does (topic, methods, main findings)
- Sentences 3-4: Overall quality assessment (from your review focus perspective)
- Sentences 5-6: Most critical strengths and weaknesses among the findings you actually made — a one-polarity review mentions only that polarity, never manufactured balance (#574 A1)
- Final: Your recommendation rationale

---

## Strengths *

List every genuine strength you actually found — no minimum, no maximum (#574 A1). Do not manufacture praise to fill a quota; an empty list is valid and triggers the Coverage Receipt below. Each strength must:
- Have a specific title
- Carry a typed evidence anchor (see § Evidence Anchor Types under Format Guidelines)
- Explain why it is a strength
- Omit the Severity field entirely — never emit `Severity: Strength`; Severity is weakness-only

### S1: [Strength title]
[Specific description. E.g., "The research design uses a quasi-experimental pretest-posttest control group design (p. X), effectively controlling for..."]
**Evidence Anchor**: [`<type>: <locator>`]
[Replace the complete backticked value above; never wrap `<type>` alone. See § Evidence Anchor Types.]

### S2..Sn
[Repeat the S1 structure for each additional strength — as many entries as the evidence supports, including zero.]

---

## Weaknesses *

List every weakness you actually found — no minimum, no maximum (#574 A1). Do not manufacture findings to fill a quota, and do not omit real ones to seem agreeable; an empty list is valid and triggers the Coverage Receipt below. Each weakness must:
- Have a specific title
- Describe the specific problem
- Explain why it is a problem
- Provide specific improvement suggestions
- Carry a typed Evidence Anchor, a Severity, and a per-finding Confidence (fields below)

### W1: [Weakness title]
**Problem**: [Specific description of the problem]
**Evidence Anchor**: [`<type>: <locator>`]
[Replace the complete backticked value above; never wrap `<type>` alone. Critical/Major findings require an adequate, applicable type (#574 A2); see § Evidence Anchor Types.]
**Why it matters**: [Explain the impact of this problem]
**Suggestion**: [Specific improvement direction]
**Severity**: [Critical / Major / Minor] — the Schema 6 enum (§ Severity Levels below); set by decision impact alone (#574 A3/B1)
**Confidence**: [1-5] — [competence basis, one phrase: e.g. "core expertise: psychometrics" / "adjacent field: applying general standards"] (#574 A3)

Finding fields may be unindented or Markdown-list-indented, and may be separate lines or pipe-delimited on one line. The complete typed anchor value, including its type and locator, may be bare, backtick-wrapped, or square-bracketed; these presentation variants do not weaken the one-finding/one-Severity/one-anchor gate.

Every Evidence Anchor value begins with the literal `<type>: <locator>` grammar. An opening backtick or `[` immediately before `<type>` starts an outer wrapper and requires its matching closer; nothing may appear between the type and its colon, so `` `text`: §3 `` and `` `text` — §3 `` are both invalid. Wrapper-like characters inside a locator are content and must be locally balanced — a bracketed locator such as `equation: Eq. [3]` and a locator naming inline code such as ``text: §3 "quote" per `df``` are valid. A `text:` anchor contains one or more verbatim excerpts, each inside a balanced pair of straight or curly double quotes, and every quoted excerpt is at most 25 words. Before output, confirm at least one quoted excerpt exists, count each quoted excerpt in a `text:` anchor, and shorten any excerpt over 25 words; never place commentary inside the quotation. An `absence:` anchor uses the exact grammar `absence: <where> — expected <item>; checked <surfaces>`, including the literal single space after the semicolon and non-empty content for every placeholder. The reserved ` — expected ` and `; checked ` separator sequences each occur exactly once.

### W2..Wn
[Repeat the W1 structure for each additional weakness — as many entries as the evidence supports, including zero.]

---

## Coverage Receipt (conditional *)

REQUIRED whenever the Strengths list or the Weaknesses list above is EMPTY (#574 A1): removing the finding quotas is not permission for a thin review. State which polarity the receipt covers, then one row per review dimension you actually examined (use your Detailed Comments sub-sections as the dimension list):

**Covers**: [Strengths / Weaknesses / both]

| Dimension examined | What you checked | Basis for "nothing found" |
|--------------------|------------------|---------------------------|
| [e.g. Sampling strategy] | [what you looked at] | [why nothing of the covered polarity rose to a finding] |

The basis column speaks only to the covered polarity — "no strength found" or "no weakness found", never a blanket "no finding" when the other list is populated. An empty finding list without its Coverage Receipt is invalid.

---

## Detailed Comments *

Section-by-section commentary on the paper. Only comment on sections relevant to your review focus.

### Title & Abstract
- [Assess title accuracy and appeal]
- [Assess abstract structure and completeness]

### Introduction
- [Is research background sufficient]
- [Is research question/purpose clear]
- [Is research motivation persuasive]

### Literature Review / Theoretical Framework
- [Literature coverage] (Primarily reviewed by Reviewer 2)
- [Theoretical framework appropriateness] (Primarily reviewed by Reviewer 2)
- [Research gap argument]

### Methodology / Research Design
- [Research design appropriateness] (Primarily reviewed by Reviewer 1)
- [Sampling strategy]
- [Data collection]
- [Analysis methods]

### Results / Findings
- [Completeness of results presentation]
- [Figure/table quality]
- [Alignment of results with research questions]

### Discussion
- [Whether discussion addresses research questions]
- [Dialogue with the literature]
- [Theoretical and practical implications]
- [Discussion of limitations]

### Conclusion
- [Whether conclusions over-infer]
- [Value of future research directions]

### References
- [Citation format]
- [Quality and recency of cited references]

---

## Questions for Authors *

List 2-4 questions requiring author response. These questions should:
- Not be rhetorical, but genuinely need answering
- The answer could change the paper's quality or direction
- Be specific and answerable

1. [Question 1]
2. [Question 2]
3. [Question 3] (Optional)
4. [Question 4] (Optional)

---

## Minor Issues

List minor issues that don't affect academic quality but need correction.

**Non-finding channel (#574 A2/A3 boundary):** entries here are copyedit-level items BELOW the finding threshold — they carry no Severity/Evidence Anchor/Confidence fields and never enter Schema 6 `weaknesses[]` (the synthesizer merges them into Priority 3 as aggregated editorial items, not transported findings). Anything with decision impact belongs in Weaknesses with the full field set.

### Language / Grammar
- [Page X, Line Y: Specific language issue]
- [...]

### Citation Format
- [Specific citation format issues]
- [...]

### Figures and Tables
- [Figure/table improvement suggestions]
- [...]

### Layout
- [Layout issues]
- [...]

---

## Criterion-Bound Judgements *

Calibration status: `NOT_CALIBRATED`

Current seat reports cannot know the final actual panel topology and never
self-upgrade from a candidate profile. Live package application remains
unavailable until a closed profile artifact and replay validator ship.

Apply `references/quality_rubrics.md` to each applicable dimension. Do not assign points, calculate a weighted total, rank papers, or derive the recommendation from a fixed mapping.

| Dimension | Criterion source | Judgement | Evidence anchor(s) | Rationale | Uncertainty / scope limit | Decision bearing? |
|---|---|---|---|---|---|---|
| Originality | | [EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED] | | | | |
| Methodological Rigor | | [EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED] | | | | |
| Evidence Sufficiency | | [EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED] | | | | |
| Argument Coherence | | [EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED] | | | | |
| Writing Quality | | [EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED] | | | | |
| Literature Integration | | [EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED] | | | | |
| Significance & Impact | | [EXCEEDS/MEETS/PARTLY_MEETS/DOES_NOT_MEET/NOT_ASSESSED] | | | | |

Explain the recommendation by naming the unresolved decision-bearing criteria and their repairability. Do not let strengths on one criterion numerically offset a failure on another.
```

---

## Format Guidelines

### Severity Levels

| Level | Per-finding decision-impact test | Revision Requirement |
|-------|----------------------------------|---------------------|
| **Critical** | This single defect, uncorrected, invalidates the core claim or makes acceptance impossible. It alone would justify `block` on a mandatory dimension. | Required before acceptance; may be fatal or repairable at the dimension layer |
| **Major** | This finding materially weakens confidence in a core claim and requires substantial re-analysis, rewriting, or new data, while the core survives. | Substantial revision |
| **Minor** | Quality or clarity improves if fixed; core claims are unaffected. | Limited revision |

These levels ARE the Schema 6 `severity` enum (`shared/handoff_schemas.md` § Weakness Object) — the single source for finding severity across the reviewer stack (#574 A3). Every weakness entry carries its level explicitly; the Devil's Advocate's OBSERVATION category is a non-defect channel that never maps into this enum. Severity is set by these decision-impact definitions alone: respectful register never lowers a level, and adversarial or rigor-signaling framing never raises one (#574 B1).

Apply the test to each finding independently, never to its surrounding narrative or defect cluster. A finding never inherits a higher band from siblings; joint impact belongs in the criterion judgement and synthesis. If a defect needs siblings to reach rejection-level impact, it is not Critical alone. These are per-finding decision-impact tests, never distributional targets: there is no expected frequency for any band.

### Evidence Anchor Types (#574 A2)

Every finding carries ONE typed evidence anchor matched to its evidence — a verbatim quote + page is one type, not a universal requirement:

| Type | Use for | Locator content |
|------|---------|-----------------|
| `text` | Claims the manuscript states | Verbatim quote (≤ 25 words) + section/page/paragraph |
| `table` | Numeric/tabular evidence | Table number + row/column or the cell value cited |
| `figure` | Visual evidence | Figure number + panel/feature |
| `equation` | Formal/mathematical content | Equation number (or section) + the term at issue |
| `dataset` | Data/artifact properties as reported in the manuscript | Artifact name + the property at issue |
| `absence` | Omissions — missing statement, section, analysis, or reference | `absence_scope` (where it should appear) + what was expected + which surfaces you checked |

Rules:
- **Critical/Major findings MUST carry an adequate anchor of an applicable type** (#574 A2). A Critical/Major claim you cannot anchor with any applicable type is not yet a finding — do the check that produces the anchor, or route it to Questions for Authors.
- An `absence` anchor is only checkable if it names where you looked — "the paper never states X" requires "checked Methods, Limitations, appendix".
- Minor findings carry an anchor too; a section-level locator suffices.

```
# Correct (text)
Evidence Anchor: text: p. 12 "AI can replace human judgment in QA processes"

# Correct (table)
Evidence Anchor: table: Table 3 — p = 0.04 reported without an effect size

# Correct (absence)
Evidence Anchor: absence: Methods — expected a consent/ethics statement; checked §3, §6, appendix

# Incorrect (untyped, unlocated)
"Methodology has problems"
"Literature review is not comprehensive enough"
```

### Constructive Tone Examples

```
# Good
"The author is encouraged to consider adding X analysis to strengthen the argument for Y."

# Good
"This section's argumentation could be clearer. Specifically, the causal inference in paragraph 2, page 8 needs additional evidence support."

# Bad
"The author clearly does not understand X."

# Bad
"This method is wrong."
```

Tone is register, not severity (#574 B1): these phrasing rules change WORDING only — they never lower a finding's severity, and blunt phrasing never raises one.
