# Bilingual Abstract Template

## Usage
Use this template when writing bilingual abstracts in the run's declared output language pair (default `zh-tw-en`: Traditional Chinese L1 + English L2). Each version must be independently composed — not a translation of the other.

---

## Pair Binding (#862 Phase 1)

The headings and column labels below are **pair-derived**: the L2 heading is the second language of the run's `output_language_pair` entry and the L1 heading is its first language. For the default entry `zh-tw-en` they render exactly as written here — `## English Abstract` (L2) and `## Chinese Abstract (zh-TW)` (L1), with the quality-checklist columns labelled `EN` (L2) and `zh-TW` (L1). The derived L1 heading label is the registry entry's short language name (`Chinese` for `Traditional Chinese (zh-TW)`), as in `abstract_bilingual_agent.md`; the registry's full name is never rendered.

For any other registry entry, substitute that entry's declared L2 and L1 language names in the headings and in the checklist column labels. The structure, the five components, and the keyword line do not change. When the field is absent the default entry applies and this template is used unchanged.

Registry and language roles: [`shared/output_language_pair.md`](../../shared/output_language_pair.md). Abstract length and keyword counts: the regime table in [`references/abstract_writing_guide.md`](../references/abstract_writing_guide.md). Enter a token only from that registry; an unsupported value fails visibly and names the registry rather than falling back to the default.

---

## English Abstract

### [Paper Title in Title Case]

[**Background** — 1-2 sentences: Establish the context and identify the research problem.]

[**Purpose** — 1 sentence: State the specific research objective or question.]

[**Method** — 1-2 sentences: Describe the research approach, data sources, and analytical method.]

[**Findings** — 2-3 sentences: Present the key results. Include specific details, numbers, or effect sizes where applicable.]

[**Implications** — 1-2 sentences: State the significance, practical impact, or contribution to the field.]

**Keywords**: [keyword 1], [keyword 2], [keyword 3], [keyword 4], [keyword 5], [keyword 6] *(optional)*, [keyword 7] *(optional)*

*Target: the L2 length of this run's row in the regime table of [`abstract_writing_guide.md`](../references/abstract_writing_guide.md)*

---

## Chinese Abstract (zh-TW)

### [Paper Title in Chinese]

[**Research Background** — 1-2 sentences: Describe the research context and the problem being investigated.]

[**Research Purpose** — 1 sentence: Clearly state the research objective or research question.]

[**Research Method** — 1-2 sentences: Describe the research methodology, data sources, and analytical strategy.]

[**Research Findings** — 2-3 sentences: Present the main research results, including specific data or key findings.]

[**Research Significance** — 1-2 sentences: Explain the research contribution, practical implications, or theoretical value.]

**Keywords**: [Keyword 1], [Keyword 2], [Keyword 3], [Keyword 4], [Keyword 5], [Keyword 6] (optional), [Keyword 7] (optional)

*Target: the L1 length of this run's row in the regime table of [`abstract_writing_guide.md`](../references/abstract_writing_guide.md)*

---

## Quality Checklist

| Check | EN | zh-TW |
|-------|:--:|:-----:|
| Covers all 5 components (Background, Purpose, Method, Findings, Implications) | ☐ | ☐ |
| Within the regime table's range (`abstract_writing_guide.md`) for the run's pair and paper type | ☐ | ☐ |
| Independently composed (not a translation) | ☐ | ☐ |
| Key findings match between versions | ☐ | ☐ |
| Quantitative data consistent | ☐ | ☐ |
| Keyword count per language within the regime table in `abstract_writing_guide.md` | ☐ | ☐ |
| Keywords complement title (not duplicate) | ☐ | ☐ |
| No citations in the abstract | ☐ | ☐ |
| No undefined abbreviations | ☐ | ☐ |
| Reads naturally in target language | ☐ | ☐ |

---

## Guidelines

### Independence Test
Your abstracts are truly independent if:
- Sentence structures differ between languages
- The L1 version uses natural phrasing in its own academic register (default: Chinese, not translationese)
- Minor details may be grouped or reordered to suit each language's conventions
- Both versions stand alone as complete summaries

### Keywords Strategy
- The two languages' keywords should cover similar conceptual space
- Keywords should complement (not duplicate) the title
- Count per language comes from the regime table in the linked guide (`abstract_writing_guide.md`) — this template restates no figure
- Mix broad discipline terms with specific research terms
- Include methodology terms if distinctive
