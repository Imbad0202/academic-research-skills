# Number and Unit Formatting Guide

This reference defines conventions for numbers, units, and statistical reporting in academic papers.

## SI Unit Formatting

- Always insert a space between the number and the unit: `5 kg`, `100 mL`, `25 °C`
- Exceptions: percentage (`5%`), degree symbol alone (`45°`), currency (`$100`)
- Use SI base/derived units; spell out non-standard units on first use
- In LaTeX: use `\SI{5}{kg}` (siunitx) or `5\,kg` for thin space
- In Typst: use `5 #unit("kg")` or manual thin space `5#h(0.15em)kg`

## Number-Word Thresholds

| Context | Rule |
|---------|------|
| Sentence start | Always spell out: "Twenty participants..." |
| Values 1-9 in prose | Spell out: "three experiments", "five categories" |
| Values 10+ in prose | Use digits: "12 features", "256 samples" |
| Precise measurements | Always digits: "3 mL", "7 days" |
| Large round numbers | Mixed: "1.2 million", "3 billion" |
| Adjacent numbers | Alternate forms: "two 3-layer networks" |

## Statistical Reporting

| Measure | Format | Example |
|---------|--------|---------|
| Percentage | 1 decimal place | 85.3% |
| Mean +/- SD | 2 decimal places | 3.14 +/- 0.05 |
| p-value | Exact (3 sig figs) or threshold | p = 0.003, p < 0.001 |
| Correlation | 2-3 decimal places | r = 0.87 |
| Confidence interval | Same precision as estimate | [2.10, 4.18] |
| Effect size (Cohen's d) | 2 decimal places | d = 0.75 |
| F-statistic | 2 decimal places with df | F(2, 47) = 3.85 |
| t-statistic | 2 decimal places with df | t(49) = 2.10 |
| Chi-square | 2 decimal places with df | chi-sq(3) = 7.81 |

## Consistency Rules

- Precision must be consistent within each column of a table
- Precision must be consistent for the same measure across the paper
- Report exact p-values when p >= 0.001; use "p < 0.001" otherwise
- Never report "p = 0.000" — use "p < 0.001"

## Range Formatting

- Use en dash for number ranges: "10--20", "pp. 1--15"
- In LaTeX: `10--20` renders as `10–20`
- In Typst: `10--20` or `10#sym.dash.en 20`
- Do not use "from X-Y"; use "from X to Y" or "X--Y"

## Large Number Formatting

- Use comma separators for numbers >= 1,000: `1,024`, `10,000`
- In some European venues, use period: `1.024`, `10.000` — check venue guide
- Scientific notation for very large/small: `3.2 x 10^5`, `1.5 x 10^{-3}`
