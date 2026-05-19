# IEEE Conferences and Journals (Typst)

> Venue-specific snapshot extracted from `references/VENUES.md`. Load this
> file directly when the user names IEEE as the target venue, instead of
> reading the full venue catalog.

## Format Requirements

- **Paper Size**: US Letter (8.5" × 11")
- **Columns**: Two-column format
- **Column Width**: 3.5" (8.89 cm)
- **Column Separation**: 0.33" (0.84 cm)
- **Margins**: 0.75" top/bottom, 0.625" left/right
- **Font**: Times New Roman 10pt
- **Line Spacing**: Single

## Typst Configuration

```typst
#set page(
  paper: "us-letter",
  margin: (top: 0.75in, bottom: 0.75in, left: 0.625in, right: 0.625in),
  columns: 2,
  column-gutter: 0.33in
)

#set text(
  font: "Times New Roman",
  size: 10pt
)

#set par(justify: true, leading: 0.55em)
```

## Writing Style

- **Voice**: Active voice preferred
- **Tense**: Past tense for methods, present for results
- **Figures**: "Fig. 1" in text, "Figure 1" in captions
- **Tables**: Roman numerals (Table I, Table II)
- **Equations**: Numbered consecutively

## Citation Style

- Numeric citations in square brackets: [1], [2-4]
- IEEE reference format

## Template

```typst
#import "@preview/charged-ieee:0.1.0": ieee

#show: ieee.with(
  title: [Your Paper Title],
  authors: (...),
  abstract: [...],
  index-terms: ("Keyword1", "Keyword2"),
  bibliography: bibliography("refs.bib", style: "ieee"),
)
```

## Pseudocode

- Prefer the `algorithmic` package for IEEE-like Typst pseudocode because it provides `algorithm-figure`, caption support, and conventional control-flow rendering.
- Treat `lovelace` as a flexible fallback when the user explicitly wants freer syntax.
- In IEEE-like output, wrap pseudocode in `algorithm-figure(...)` or `#figure(...)` with a caption.
- Line numbers are recommended for review convenience, but they are not enforced here as an IEEE hard rule.
- Keep comments short and move paragraph-level explanation back into the main text.
