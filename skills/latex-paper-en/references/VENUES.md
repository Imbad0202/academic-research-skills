# Venue-Specific Requirements

> **Summary index.** Each venue lives as its own snapshot under
> `../templates/`; load `templates/<venue>.md` directly when the user names a
> specific venue (`ieee`, `acm`, `neurips`, `icml`, `springer-lncs`).
> This file remains the cross-venue overview (quick-reference table,
> pre-submission checklist, resubmission conversions, figure specs).


## Table of Contents

- [IEEE Conferences/Journals](#ieee-conferencesjournals)
  - [Style](#style)
  - [Format](#format)
  - [Citations](#citations)
  - [Figures/Tables](#figurestables)
- [ACM Conferences](#acm-conferences)
  - [Style](#style)
  - [Format](#format)
  - [Special Requirements](#special-requirements)
- [Springer (LNCS)](#springer-lncs)
  - [Style](#style)
  - [Format](#format)
  - [Figures/Tables](#figurestables)
  - [Citations](#citations)
- [NeurIPS / ICML](#neurips-icml)
  - [Style](#style)
  - [Format](#format)
  - [Special](#special)
- [CVPR / ICCV / ECCV](#cvpr-iccv-eccv)
  - [Style](#style)
  - [Format](#format)
  - [Figures](#figures)
- [ArXiv Preprints](#arxiv-preprints)
  - [Format](#format)
  - [Best Practices](#best-practices)
- [Conference Quick Reference Table](#conference-quick-reference-table)
- [Pre-Submission Checklist](#pre-submission-checklist)
  - [Universal (All Venues)](#universal-all-venues)
- [Resubmission Format Conversion](#resubmission-format-conversion)
  - [Common Conversion Paths](#common-conversion-paths)
  - [Content Migration Principles](#content-migration-principles)
- [Figure and Table Specifications](#figure-and-table-specifications)
  - [Tables](#tables)
  - [Figures](#figures)

---

## IEEE Conferences/Journals

### Style
- Active voice for contributions
- Past tense for methods
- Present tense for results discussion

### Format
- Two-column layout
- Abstract: 150-200 words
- Keywords: 3-5 terms

### Citations
- IEEE style: [1], [2-4]
- Full reference in bibliography

### Figures/Tables
- Captions below figures
- Captions above tables
- Referenced in text before appearing

### Pseudocode
- IEEEtran only recognizes `figure` and `table` as standard floats; do not assume a dedicated `algorithm` float is IEEE-safe.
- Prefer `figure` + `algorithmicx` / `algpseudocodex` for LaTeX pseudocode in IEEE submissions.
- Give the pseudocode block a normal figure caption and reference it in text before the figure appears.
- Prefer direct captions such as `Adaptive inference procedure` instead of `The proposed algorithm...`.
- Explicit input/output markers and short inline comments are recommended defaults, not IEEE hard requirements.

## ACM Conferences

### Style
- Structured abstract (some venues)
- Author-date citations accepted

### Format
- ACM reference format
- CCS concepts required
- Keywords required

### Special Requirements
- Accessibility requirements
- Supplementary material guidelines

## Springer (LNCS)

### Style
- British or American English (consistent)
- Third person preferred

### Format
- Single column
- Strict page limits
- Camera-ready deadline strict

### Figures/Tables
- Figure captions: below
- Table captions: above
- High resolution (300 dpi minimum)

### Citations
- Numbered: [1]
- Springer nature template

## NeurIPS / ICML

### Style
- Concise writing essential
- Mathematical notation consistent

### Format
- 8-page main paper
- Unlimited appendix
- Blind review requirements

### Special
- Broader impact statement
- Reproducibility checklist
- Code submission encouraged

## CVPR / ICCV / ECCV

### Style
- Visual results emphasized
- Quantitative comparisons required

### Format
- Double-blind review
- Supplementary video allowed
- 8 pages + references

### Figures
- High-quality visualizations
- Comparison figures expected
- Video demonstrations encouraged

## ArXiv Preprints

### Format
- No strict format
- PDF preferred
- Abstract: 1500 characters max

### Best Practices
- Include author affiliations
- Link to code/data
- Version control with updates

---

## Conference Quick Reference Table

| Conference | Page Limit | Extra (Camera-Ready) | Key Requirement | Template |
|------------|------------|---------------------|-----------------|----------|
| **NeurIPS 2025** | 9 pages | +0 | Mandatory checklist, lay summary | neurips.sty |
| **ICML 2026** | 8 pages | +1 | Broader Impact Statement | icml2026.sty |
| **ICLR 2026** | 9 pages | +1 | LLM disclosure, reciprocal review | iclr2026.sty |
| **ACL 2025** | 8 pages (long) | varies | Limitations section mandatory | acl.sty |
| **AAAI 2026** | 7 pages | +1 | Strict style file adherence | aaai2026.sty |
| **COLM 2025** | 9 pages | +1 | Language model focus | colm2025.sty |

**Universal Requirements:**
- Double-blind review (anonymize submissions)
- References don't count toward page limit
- Appendices unlimited but reviewers not required to read
- LaTeX required for all venues

---

## Pre-Submission Checklist

### Universal (All Venues)
- [ ] Paper compiles without errors
- [ ] All figures referenced in text
- [ ] All tables referenced in text
- [ ] No orphaned citations
- [ ] No placeholder text (TODO, FIXME, XXX)
- [ ] Anonymous submission (no author names)
- [ ] Page limit respected
- [ ] Consistent notation throughout
- [ ] All acronyms defined on first use
- [ ] Limitations section included

---

## Resubmission Format Conversion

### Common Conversion Paths

| From → To | Page Change | Key Adjustments |
|-----------|-------------|-----------------|
| NeurIPS → ICML | 9 → 8 | Cut 1 page, add Broader Impact |
| ICML → ICLR | 8 → 9 | Expand experiments, add LLM disclosure |
| NeurIPS → ACL | 9 → 8 | Restructure for NLP, add Limitations |
| ICLR → AAAI | 9 → 7 | Significant cuts, strict style |
| Any → COLM | varies → 9 | Reframe for language model focus |

### Content Migration Principles
1. **Never copy LaTeX preambles** between templates — start fresh with target template
2. **Copy ONLY content sections** (abstract, sections, figures, tables, bib entries)
3. When cutting pages: move proofs to appendix, condense related work, combine tables
4. When expanding: add ablations, expand limitations, include qualitative examples

---

## Figure and Table Specifications

### Tables
Use `booktabs` package for professional tables:
- Bold best value per metric
- Include direction symbols (↑ higher is better, ↓ lower is better)
- Right-align numerical columns
- Consistent decimal precision

### Figures
- **Vector graphics** (PDF, EPS) for all plots and diagrams
- **Raster** (PNG 600 DPI) only for photographs
- **Colorblind-safe palettes**: Okabe-Ito or Paul Tol recommended
- **Grayscale readability**: Verify figures work without color (8% of men have color vision deficiency)
- **No title inside figure** — the caption serves this function
- **Self-contained captions** — reader should understand without main text
