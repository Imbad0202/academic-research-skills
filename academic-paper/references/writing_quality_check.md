# Writing Quality Check

## Purpose

A set of context-sensitive writing diagnostics for clear, precise academic prose, regardless of who wrote it.

> **Design boundary**: This checklist improves writing quality. It is NOT a humanizer. We do not aim to fool AI detectors. We aim to produce clear, precise, varied academic prose.

Reference this checklist during the self-review step of drafting (draft_writer_agent Step 2.7, report_compiler_agent final check).

**Priority and scope**: Author requirements and target venue rules take priority, followed by discipline conventions and the approved Style Profile. The patterns below are non-blocking prompts for judgment, not vocabulary bans, punctuation quotas, paragraph templates, or a pass/fail score. Revise only when a specific clarity, precision, or support problem warrants it. Preserve formal word limits, citation and evidence requirements, quoted source text, and the authorized revision scope; this checklist does not authorize rewriting otherwise sound prose or weakening a claim's evidential support.

---

## A. High-Frequency Term Warnings

The following terms can be vague or overused in context. They are not banned and do not establish authorship. When reviewing one, ask: **"Is this the most precise word here?"** Keep it when the answer is yes.

### Flagged Terms

| Term | Why it's flagged | Better alternatives (context-dependent) |
|------|-----------------|----------------------------------------|
| delve | Overused as "explore" substitute | examine, investigate, analyze, explore |
| tapestry | Cliché metaphor for complexity | network, interplay, system, landscape |
| landscape | Vague when not literal | field, domain, context, state of |
| pivotal | Inflation of importance | important, significant, central, key |
| crucial | Same as above | essential, necessary, critical, vital |
| foster | Vague verb | promote, develop, cultivate, encourage |
| showcase | Non-academic register | demonstrate, illustrate, present, reveal |
| testament | Cliché | evidence, indicator, demonstration |
| navigate | Vague when not literal | manage, address, handle, negotiate |
| leverage | Business jargon | use, employ, utilize, apply |
| realm | Archaic/poetic | domain, field, area, sphere |
| embark | Overwrought for "begin" | begin, initiate, undertake, start |
| underscore | Overused emphasis verb | emphasize, highlight, stress, reinforce |
| multifaceted | Vague complexity claim | complex, varied, diverse, multilayered |
| nuanced | Often vacuous | subtle, detailed, fine-grained, qualified |
| comprehensive | Often unjustified | thorough, extensive, broad, detailed |
| robust | Vague quality claim | reliable, strong, rigorous, resilient |
| intricate | Same problem as multifaceted | complex, detailed, elaborate, involved |
| cornerstone | Cliché metaphor | foundation, basis, core element, pillar |
| paradigm | Overused outside philosophy of science | framework, model, approach (exception: "paradigm shift" in philosophy of science is standard) |
| synergy | Business jargon | interaction, cooperation, combined effect |
| holistic | Vague without definition | comprehensive, integrated, whole-system |
| streamline | Non-academic | simplify, optimize, improve efficiency |
| cutting-edge | Cliché | recent, advanced, state-of-the-art, novel |
| groundbreaking | Inflation | novel, innovative, pioneering, original |

### Exception Rule

If a flagged term is **standard terminology in the target discipline**, it is exempt:
- "paradigm shift" in philosophy of science → OK
- "landscape" in ecology/geography (literal) → OK
- "robust" in statistics ("robust estimator") → OK
- "navigate" in wayfinding research (literal) → OK

---

## B. Punctuation Pattern Review

### Em Dash (—)
- **Check**: Does the aside clarify the argument, or interrupt it unnecessarily?
- **Possible revision**: Use commas, parentheses, or a separate sentence when that improves readability. Keep an effective em dash where the author's and venue's style permits it
- **Exception**: Direct quotes from sources retain their original punctuation

### Semicolons
- **Check**: Are the linked clauses closely related and easy to follow?
- **Possible revision**: Split an overloaded sentence when a period makes the relationship clearer. Keep semicolons that aid meaning or are required by citation/style conventions

### Colon-List Sequences
- **Check**: Do repeated lists clarify comparable items, procedures, or findings, or fragment the argument?
- **Possible revision**: Integrate items into prose or consolidate lists when that improves the explanation. Repeated lists are appropriate when the content or required format calls for them

---

## C. Throat-Clearing Openers

Review these openers for unnecessary wording. The examples below suggest possible edits, not mandatory substitutions; keep signposting or qualification that helps the reader, and preserve the strength and meaning of the supported claim.

| Throat-clearing phrase | What to do |
|-----------------------|-----------|
| "In the realm of..." | Delete. Start with the actual subject |
| "It's important to note that..." | Delete. If it's important, the content speaks for itself |
| "It is worth mentioning that..." | Same as above |
| "In today's rapidly evolving..." | Delete. Timestamped clichés add no information |
| "This serves as a testament to..." | Replace with direct claim: "This demonstrates..." or just state the evidence |
| "It goes without saying that..." | If it goes without saying, don't say it |
| "In order to..." | Replace with "To..." |
| "It should be noted that..." | Delete. Just note it |
| "As a matter of fact..." | Delete. State the fact |
| "When it comes to..." | Replace with the subject directly: "X shows..." |
| "At the end of the day..." | Delete. Colloquial and vague |
| "With that being said..." | Delete or use "However" if a contrast is intended |

### Meta-Commentary to Avoid

Also watch for sentences that describe what the paper is doing instead of doing it:
- "This section will discuss..." → Just discuss it
- "The following paragraph examines..." → Just examine it
- "We now turn our attention to..." → Just turn to it

Exception: Roadmap sentences in the Introduction ("Section 2 reviews the literature; Section 3 describes the methodology") are standard academic practice and should be kept.

---

## D. Structure Pattern Warnings

### Rule of Three Compulsion
- **Pattern**: Every argument has exactly 3 sub-points, every list has exactly 3 items
- **Why**: Real analysis doesn't always decompose into trios. Two strong points beat three padded ones
- **Fix**: Use as many points as the evidence warrants. 2 is fine. 5 is fine. Don't pad to 3

### Paragraph Length
- **Check**: Does each paragraph have enough space to develop its point without padding or overload?
- **Possible revision**: Split or combine paragraphs when the argument becomes easier to follow. Similar lengths can be appropriate; do not introduce variation for its own sake

### Synonym Cycling
- **Pattern**: Switching terms for the same concept merely to avoid repetition
- **Why**: In academic writing, consistent terminology is a virtue. Swapping "students" → "learners" → "participants" → "subjects" within one paragraph confuses rather than impresses
- **Possible revision**: Use consistent terminology for the same construct and distinguish terms when they mean different things. Preserve meaningful technical distinctions and the wording of quoted sources

### Binary Contrast Overuse
- **Check**: Does the contrast identify a supported distinction, or impose a false dichotomy or repetitive framing?
- **Possible revision**: State the actual relationship directly when the contrast obscures it. Keep useful, supported contrasts

### Mirror Structure
- **Pattern**: Every section has the same internal structure (topic sentence → 3 evidence points → synthesis sentence)
- **Check**: Does the repeated structure fit each section's purpose, or leave analysis missing or padded?
- **Possible revision**: Let section structure follow content needs. Methods can be procedural and discussion can be exploratory; keep parallel structures when they aid comparison or satisfy the required format

---

## E. Sentence Length and Readability

### What to Check
Match sentence length to meaning and the reader's needs. Short sentences can emphasize a finding; longer ones can explain a relationship. Similar lengths are acceptable when the passage remains clear.

### Review Prompt
If a passage is difficult to follow or sounds repetitive, check whether sentence structure contributes to the problem. Word-count similarity alone is not a defect and does not require revision.

### Possible Revisions
- Split an overloaded sentence at a meaningful boundary
- Combine fragmented statements when this makes their relationship clearer
- Read the paragraph aloud to identify awkward phrasing; preserve accurate, readable prose even when its sentence lengths are similar

### Section Context
Abstracts must respect venue length and structure requirements. Methods may benefit from parallel procedural sentences; results and discussion may need different amounts of explanation. Choose the form that communicates the evidence and reasoning.

---

## How to Use This Checklist

### During Drafting (Preferred)
Use these diagnostics in the self-review sub-step (Step 2.7 in draft_writer_agent) when they help resolve an actual writing problem.

### During Final Review (Fallback)
Review the assembled paper for clarity, precision, and supported claims before handoff to citation_compliance_agent. Do not repeat cosmetic passes once the relevant problems are resolved.

### Review Outcome
Resolve identified writing problems within the authorized scope and report material evidence gaps or unmet author/venue requirements; nothing in this checklist alone blocks handoff.
