# Citation Style Guide

This reference defines the formatting rules for four major citation styles used in academic publishing. Use this when validating bibliography entries with `verify_bib.py --style <style>`.

## Style Comparison Matrix

| Feature | IEEE | APA 7th | Vancouver | Nature |
|---------|------|---------|-----------|--------|
| In-text format | `[1]` numeric | `(Smith, 2023)` author-year | `(1)` or superscript | Superscript |
| Author threshold | 6 → et al. | 3 → et al. (in-text: 1-2 spell, 3+ et al.) | 6 → et al. | 5 → et al. |
| Journal name | ISO 4 abbreviated | Full name, italicized | NLM abbreviated | ISO 4 abbreviated |
| Volume | Bold | Italicized | Bold | Bold |
| Pages | en dash (pp. 1--10) | en dash (pp. 1--10) | en dash (1--10) | en dash (1--10) |
| DOI | Required when available | Required as URL | Optional | Required when available |
| Year position | After author | After author in parens | After journal | After journal |

## IEEE Style

**In-text**: `[1]`, `[2-4]`, `[1], [3]`

**Reference format**:
```
[1] A. B. Author, C. D. Author, and E. F. Author, "Article title," J. Abbrev., vol. 10, no. 2, pp. 1--15, Mar. 2023, doi: 10.xxxx/xxxxx.
```

**Rules**:
- Authors: initials before surname, up to 6 listed, then "et al."
- Title: sentence case in double quotes
- Journal: ISO 4 abbreviation, italicized
- Volume/number/pages: `vol. X, no. Y, pp. A--B`
- Month abbreviated: Jan., Feb., Mar., Apr., May, Jun., Jul., Aug., Sep., Oct., Nov., Dec.
- DOI required when available
- Pages use en dash (`--` in BibTeX, renders as `–`)

## APA 7th Edition

**In-text**: `(Smith, 2023)`, `(Smith & Jones, 2023)`, `(Smith et al., 2023)` for 3+

**Reference format**:
```
Author, A. B., Author, C. D., & Author, E. F. (2023). Article title. Journal Name, 10(2), 1--15. https://doi.org/10.xxxx/xxxxx
```

**Rules**:
- Authors: surname, initials; up to 20 listed, 21+ use first 19 + ... + last
- In-text: 1-2 authors spell out, 3+ use "et al."
- Title: sentence case, no quotes
- Journal: full name, italicized
- Volume italicized, issue in parentheses (not italicized)
- DOI formatted as URL: `https://doi.org/10.xxxx/xxxxx`
- Hanging indent (0.5 inch)
- No "pp." before page numbers in journals

## Vancouver Style

**In-text**: `(1)` or superscript `¹`, numbered by order of appearance

**Reference format**:
```
1. Author AB, Author CD, Author EF. Article title. J Abbrev. 2023;10(2):1-15.
```

**Rules**:
- Authors: surname followed by initials (no periods, no commas between initials)
- Up to 6 authors listed, then "et al."
- Title: sentence case, no quotes
- Journal: NLM (PubMed) abbreviation
- No spaces between volume, issue, pages: `2023;10(2):1-15`
- DOI typically omitted in print; include for online-only
- Pages: en dash preferred but hyphen accepted

## Nature Style

**In-text**: Superscript numbers `¹`, `²,³`, `⁴⁻⁶`

**Reference format**:
```
1. Author, A. B., Author, C. D. & Author, E. F. Article title. J. Abbrev. 10, 1--15 (2023).
```

**Rules**:
- Authors: surname, initials; up to 5 listed, then "et al."
- Title: sentence case, no quotes, no period after title
- Journal: ISO 4 abbreviation, italicized
- Volume bold, pages with en dash, year in parentheses
- No "vol.", "no.", "pp." labels
- DOI required when available (appended after year)

## En Dash Rule

All styles require en dash (`–`, Unicode U+2013) between page ranges, not hyphen (`-`).

In BibTeX: use `--` which renders as en dash. Flag single hyphens in page fields.

**Validation check**: `pages` field should contain `--` not a single `-`.

## Unverifiable Fields

When a field cannot be confirmed (DOI not found, page numbers uncertain):

- English: mark as `[Unverified]`
- Chinese: mark as `[待核实]`
- Never fabricate DOI, page numbers, volume, or issue numbers
- Flag uncertain entries separately rather than guessing silently

## Style Detection Heuristic

When `--style` is not specified, attempt detection from:
1. `\bibliographystyle{IEEEtran}` → IEEE
2. `\bibliographystyle{apalike}` or `\usepackage{apacite}` → APA
3. `\bibliographystyle{vancouver}` or `\usepackage{vancouver}` → Vancouver
4. Document class or preamble hints for Nature-family journals
5. Default: IEEE (most common in CS/EE)
