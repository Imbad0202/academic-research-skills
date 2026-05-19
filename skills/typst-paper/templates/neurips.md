# NeurIPS / ICML / ICLR (Typst)

> Venue-specific snapshot extracted from `references/VENUES.md`. These three
> ML conferences share most expectations in the Typst toolchain; venue-
> specific deltas (page count, broader-impact section) live in the source
> `VENUES.md` quick-reference table. Load this file directly when the user
> names NeurIPS / ICML / ICLR as the target venue, instead of reading the
> full venue catalog.

## Format Requirements

- **Page Limit**: 8 pages (excluding references)
- **Paper Size**: US Letter
- **Columns**: Single column
- **Font**: Times New Roman 10pt
- **Margins**: 1" all sides
- **Line Spacing**: Single

## Typst Configuration

```typst
#set page(
  paper: "us-letter",
  margin: 1in
)

#set text(
  font: "Times New Roman",
  size: 10pt
)

#set par(
  justify: true,
  leading: 0.65em
)

#set heading(numbering: none)  // No section numbering
```

## Writing Style

- **Anonymous Submission**: Remove author info for review
- **Figures**: High-quality, readable in grayscale
- **Code**: Supplementary material only
- **Reproducibility**: Include implementation details

## Special Requirements

- **Broader Impact Statement**: Required for NeurIPS
- **Checklist**: Complete reproducibility checklist
- **Supplementary Material**: Separate PDF
