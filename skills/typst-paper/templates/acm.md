# ACM Conferences and Journals (Typst)

> Venue-specific snapshot extracted from `references/VENUES.md`. Load this
> file directly when the user names ACM as the target venue, instead of
> reading the full venue catalog.

## Format Requirements

- **Paper Size**: US Letter or A4
- **Columns**: Two-column format
- **Font**: Linux Libertine or similar
- **Font Size**: 9-10pt
- **Margins**: 0.75" left/right, 1" top/bottom

## Typst Configuration

```typst
#set page(
  paper: "us-letter",
  margin: (x: 0.75in, y: 1in),
  columns: 2,
  column-gutter: 0.33in
)

#set text(
  font: "Linux Libertine",
  size: 9pt
)

#set par(justify: true)
```

## Writing Style

- **Tense**: Present tense for general truths
- **Figures**: "Figure 1" consistently
- **Tables**: "Table 1" consistently
- **Citation**: Numeric or author-year depending on venue

## Citation Styles

- **Numeric**: [1], [2, 3]
- **Author-Year**: (Smith et al., 2020)
