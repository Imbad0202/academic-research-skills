# Typst Syntax Reference for Academic Writing


## Table of Contents

- [Basic Syntax](#basic-syntax)
  - [Text Formatting](#text-formatting)
  - [Headings](#headings)
  - [Paragraphs](#paragraphs)
  - [Lists](#lists)
- [Math](#math)
  - [Inline Math](#inline-math)
  - [Display Math](#display-math)
  - [Common Math Symbols](#common-math-symbols)
- [Figures and Tables](#figures-and-tables)
  - [Figures](#figures)
  - [Tables](#tables)
- [Citations and References](#citations-and-references)
  - [Citations](#citations)
  - [Bibliography](#bibliography)
  - [Citation Styles](#citation-styles)
- [Page Setup](#page-setup)
  - [Basic Page Configuration](#basic-page-configuration)
  - [Two-Column Layout](#two-column-layout)
  - [Headers and Footers](#headers-and-footers)
- [Text Formatting](#text-formatting)
  - [Font Settings](#font-settings)
  - [Paragraph Settings](#paragraph-settings)
  - [Heading Settings](#heading-settings)
- [Cross-References](#cross-references)
  - [Labels](#labels)
  - [References](#references)
- [Functions and Variables](#functions-and-variables)
  - [Define Variables](#define-variables)
  - [Define Functions](#define-functions)
  - [Conditional Content](#conditional-content)
- [Show Rules (Styling)](#show-rules-styling)
  - [Style Headings](#style-headings)
  - [Style Links](#style-links)
  - [Style Figures](#style-figures)
- [Comments](#comments)
- [Special Characters](#special-characters)
- [Code Blocks](#code-blocks)
- [Common Patterns for Academic Papers](#common-patterns-for-academic-papers)
  - [Title and Authors](#title-and-authors)
  - [Abstract](#abstract)
  - [Acknowledgments](#acknowledgments)
- [Tips for Academic Writing](#tips-for-academic-writing)
- [Resources](#resources)

---

## Basic Syntax

### Text Formatting

```typst
// Bold
*bold text*

// Italic
_italic text_

// Code/Monospace
`code text`

// Combining
*_bold and italic_*
```

### Headings

```typst
= Level 1 Heading
== Level 2 Heading
=== Level 3 Heading
==== Level 4 Heading
```

### Paragraphs

```typst
// Normal paragraph
This is a paragraph. It will be justified if you set par(justify: true).

// Line break within paragraph
This is line one. \
This is line two.

// Paragraph break (blank line)
First paragraph.

Second paragraph.
```

### Lists

```typst
// Unordered list
- Item 1
- Item 2
  - Nested item 2.1
  - Nested item 2.2
- Item 3

// Ordered list
+ First item
+ Second item
  + Nested item 2.1
  + Nested item 2.2
+ Third item

// Description list
/ Term 1: Definition 1
/ Term 2: Definition 2
```

---

## Math

### Inline Math

```typst
The equation $x^2 + y^2 = z^2$ is the Pythagorean theorem.

Variables $a$, $b$, and $c$ are defined as...
```

### Display Math

```typst
// Centered display math
$ x = (a + b) / 2 $

// Numbered equation with label
$ y = m x + c $ <eq:line>

// Multi-line equations
$ x &= a + b \
  &= c + d $
```

### Common Math Symbols

```typst
// Greek letters
$alpha, beta, gamma, Delta, Sigma$

// Operators
$sum, product, integral, partial$

// Relations
$<=, >=, !=, approx, equiv$

// Fractions
$a/b$ or $(a)/(b)$

// Subscripts and superscripts
$x_i, x^2, x_i^2$

// Functions
$sin(x), cos(x), log(x), exp(x)$

// Matrices
$ mat(
  a, b;
  c, d
) $

// Cases
$ f(x) = cases(
  0 "if" x < 0,
  1 "if" x >= 0
) $
```

---

## Figures and Tables

### Figures

```typst
// Basic figure
#figure(
  image("figure.png", width: 80%),
  caption: [Description of the figure.]
) <fig:example>

// Figure with multiple images
#figure(
  grid(
    columns: 2,
    gutter: 1em,
    image("fig1.png"),
    image("fig2.png"),
  ),
  caption: [Two subfigures side by side.]
) <fig:comparison>

// Reference in text
As shown in @fig:example, the method...
```

### Tables

```typst
// Basic table
#figure(
  table(
    columns: 3,
    [*Method*], [*Accuracy*], [*Time*],
    [Baseline], [85.2%], [10ms],
    [Ours], [92.1%], [12ms],
  ),
  caption: [Comparison of methods.]
) <tab:results>

// Table with alignment
#figure(
  table(
    columns: (auto, 1fr, 1fr),
    align: (left, center, center),
    [*Method*], [*Accuracy*], [*Time*],
    [Baseline], [85.2%], [10ms],
    [Ours], [92.1%], [12ms],
  ),
  caption: [Results with custom alignment.]
) <tab:aligned>

// Reference in text
@tab:results shows the comparison...
```

---

## Citations and References

### Citations

```typst
// Single citation
According to @smith2020, the method...

// Multiple citations
Recent studies @smith2020 @jones2021 @wang2022 show...

// Citation in parentheses
The method has been studied extensively (@smith2020, @jones2021).

// Suppress author name (numeric style)
The method [1] shows...
```

### Bibliography

```typst
// BibTeX file
#bibliography("references.bib", style: "ieee")

// Hayagriva YAML file
#bibliography("references.yml", style: "apa")

// Multiple files
#bibliography(("refs1.bib", "refs2.bib"), style: "ieee")
```

### Citation Styles

```typst
// IEEE (numeric)
#bibliography("refs.bib", style: "ieee")

// APA (author-year)
#bibliography("refs.bib", style: "apa")

// Chicago
#bibliography("refs.bib", style: "chicago-author-date")

// MLA
#bibliography("refs.bib", style: "mla")

// GB/T 7714-2015 (Chinese)
#bibliography("refs.bib", style: "gb-7714-2015")
```

---

## Page Setup

### Basic Page Configuration

```typst
#set page(
  paper: "a4",              // or "us-letter"
  margin: 2.5cm,            // all sides
  // or
  margin: (x: 2.5cm, y: 3cm),  // horizontal and vertical
  // or
  margin: (top: 3cm, bottom: 3cm, left: 2.5cm, right: 2.5cm),
)
```

### Two-Column Layout

```typst
#set page(
  paper: "us-letter",
  margin: 1in,
  columns: 2,
  column-gutter: 0.33in
)
```

### Headers and Footers

```typst
#set page(
  header: [
    #set text(8pt)
    #smallcaps[Conference Name 2024]
    #h(1fr)
    Draft Version
  ],
  footer: [
    #set text(8pt)
    #h(1fr)
    #counter(page).display("1")
    #h(1fr)
  ]
)
```

---

## Text Formatting

### Font Settings

```typst
#set text(
  font: "Times New Roman",
  size: 11pt,
  lang: "en"
)

// Chinese font
#set text(
  font: ("Source Han Serif", "Noto Serif CJK SC"),
  size: 12pt,
  lang: "zh",
  region: "cn"
)

// Multiple fonts (fallback)
#set text(
  font: ("Linux Libertine", "Times New Roman", "Arial")
)
```

### Paragraph Settings

```typst
#set par(
  justify: true,              // Justify text
  leading: 0.65em,            // Line spacing
  first-line-indent: 1.5em,   // First line indent
  spacing: 0.65em             // Space between paragraphs
)
```

### Heading Settings

```typst
// Numbered headings
#set heading(numbering: "1.1")

// Custom heading style
#show heading.where(level: 1): it => {
  set text(size: 14pt, weight: "bold")
  block(above: 1.5em, below: 1em, it)
}
```

---

## Cross-References

### Labels

```typst
// Label a figure
#figure(...) <fig:example>

// Label an equation
$ x = y + z $ <eq:sum>

// Label a section
= Introduction <sec:intro>

// Label a table
#figure(table(...)) <tab:results>
```

### References

```typst
// Reference a figure
As shown in @fig:example, ...

// Reference an equation
Equation @eq:sum defines...

// Reference a section
See @sec:intro for details.

// Reference a table
@tab:results presents the results.

// Custom reference text
See #ref(<fig:example>, supplement: [Figure])
```

---

## Functions and Variables

### Define Variables

```typst
#let author = "John Smith"
#let title = "My Paper Title"

// Use variables
#author wrote #title.
```

### Define Functions

```typst
#let emphasis(body) = {
  text(weight: "bold", fill: blue, body)
}

// Use function
This is #emphasis[important].
```

### Conditional Content

```typst
#let draft = true

#if draft [
  *DRAFT VERSION*
]

#if not draft [
  Final version content
]
```

---

## Show Rules (Styling)

### Style Headings

```typst
#show heading.where(level: 1): it => {
  set text(size: 16pt, weight: "bold")
  block(above: 1.5em, below: 1em, it)
}

#show heading.where(level: 2): it => {
  set text(size: 14pt, weight: "bold")
  block(above: 1.2em, below: 0.8em, it)
}
```

### Style Links

```typst
#show link: it => {
  set text(fill: blue)
  underline(it)
}
```

### Style Figures

```typst
#show figure: it => {
  set align(center)
  it
}
```

---

## Comments

```typst
// Single-line comment

/* Multi-line
   comment */

// Comments are ignored during compilation
```

---

## Special Characters

```typst
// Non-breaking space
word~word

// Em dash
word---word

// En dash
word--word

// Ellipsis
word...

// Quotes
"double quotes"
'single quotes'
```

---

## Code Blocks

```typst
// Inline code
The function `main()` is the entry point.

// Code block
```python
def hello():
    print("Hello, world!")
```
```

---

## Common Patterns for Academic Papers

### Title and Authors

```typst
#align(center)[
  #text(size: 16pt, weight: "bold")[
    Your Paper Title
  ]
  
  #v(0.5em)
  
  Author Name#super[1], Co-author Name#super[2]
  
  #v(0.3em)
  
  #text(size: 10pt)[
    #super[1]University Name, #super[2]Institution Name \
    #link("mailto:author@email.com")
  ]
]
```

### Abstract

```typst
#heading(outlined: false, numbering: none)[Abstract]

Your abstract text here...

#v(0.5em)

*Keywords:* keyword1, keyword2, keyword3
```

### Acknowledgments

```typst
#heading(outlined: false, numbering: none)[Acknowledgments]

This work was supported by...
```

---

## Tips for Academic Writing

1. **Use labels consistently**: `<fig:name>`, `<tab:name>`, `<eq:name>`, `<sec:name>`
2. **Keep figures readable**: Use `width: 80%` or similar
3. **Number equations**: Use `$ ... $ <eq:label>` for important equations
4. **Consistent formatting**: Use `#set` rules at the beginning
5. **Modular content**: Use `#include "section.typ"` for large documents
6. **Version control**: Typst files are plain text, perfect for Git

---

## Resources

- [Typst Documentation](https://typst.app/docs/)
- [Typst Universe](https://typst.app/universe/) - Templates and packages
- [Typst Tutorial](https://typst.app/docs/tutorial/)
- [Typst Reference](https://typst.app/docs/reference/)

