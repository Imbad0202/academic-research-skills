# Three-Line Table Guide

This guide defines the standard for professional academic tables using the "three-line" (booktabs) convention. All table-related checks and generation follow these rules.

## Three-Line Table Standard

A three-line table has exactly three horizontal rules and **no vertical lines**:

1. **Top rule** (`\toprule`): above column headers
2. **Mid rule** (`\midrule`): below column headers, above data rows
3. **Bottom rule** (`\bottomrule`): below the last data row

### Anti-Patterns (must flag)

- Vertical lines (`|` in column spec, `\vline`, `\hline` with `|`)
- Internal horizontal lines (`\hline` or `\cline` between data rows, except for grouping sub-headers)
- Using `\hline` instead of booktabs commands
- Missing `\usepackage{booktabs}` in preamble

### Minimal Correct Example

```latex
\begin{table}[t]
  \caption{Comparison of model accuracy (\%).}
  \label{tab:accuracy}
  \centering
  \begin{tabular}{lSSS}
    \toprule
    Model & {Precision} & {Recall} & {F1} \\
    \midrule
    Baseline   & 85.3 & 82.1 & 83.7 \\
    Ours       & \textbf{91.2} & \textbf{89.5} & \textbf{90.3} \\
    \bottomrule
  \end{tabular}
\end{table}
```

## Decimal Alignment

Use the `siunitx` package `S` column type to align numbers by decimal point:

```latex
\usepackage{siunitx}
\sisetup{detect-weight, mode=text}
% Column spec: {l S[table-format=2.1] S[table-format=2.1]}
% Wrap non-numeric headers in braces: {Precision}
```

When `siunitx` is unavailable, right-align numeric columns with `r` and ensure consistent decimal places manually.

## Statistical Significance Markers

Use superscript symbols with footnote definitions in the table note:

| Symbol | Meaning |
|--------|---------|
| `*`    | p < 0.05 |
| `**`   | p < 0.01 |
| `***`  | p < 0.001 |
| `n.s.` | not significant |

Place significance markers immediately after the value: `91.2***`.

## Number Precision Rules

| Data type | Precision | Example |
|-----------|-----------|---------|
| Percentage | 1 decimal place | 85.3% |
| Mean ± SD | 2 decimal places | 3.14 ± 0.05 |
| p-value | 3 significant figures | 0.0032 |
| Correlation coefficient | 2-3 decimal places | 0.87 |
| Large counts | No decimals | 1,024 |

Precision must be consistent within each column. Mixed precision in the same column is a warning.

## Caption and Note Placement

- **Caption**: above the table (`\caption{...}` before `\begin{tabular}`)
- **Label**: immediately after caption (`\label{tab:...}`)
- **Table note**: below the table, starting with "Note." (English) or "注：" (Chinese)

Table note format:

```latex
\begin{tablenotes}
  \small
  \item Note. Bold values indicate best performance.
  \item * $p < 0.05$; ** $p < 0.01$; *** $p < 0.001$.
\end{tablenotes}
```

Or use `\par\vspace{2pt}{\footnotesize Note. ...}` after `\end{tabular}` if `threeparttable` is not loaded.

## Bold Best Values

In comparison tables, bold the best value in each column using `\textbf{}`. When using `siunitx` S columns, use `\bfseries` or wrap in `{\textbf{91.2}}`.

Add direction indicators when the "best" direction is ambiguous:

- `↑` (higher is better): accuracy, recall, F1
- `↓` (lower is better): error rate, latency, loss

## Booktabs Package Requirements

The `booktabs` package must be loaded for `\toprule`, `\midrule`, `\bottomrule`. These commands produce variable-weight rules (top/bottom are heavier than mid) for a professional appearance.

Never mix `\hline` with booktabs commands in the same table.

## Word Compatibility Note

When submitting to venues that require .docx, convert the three-line table by:
1. Create a standard table in Word
2. Select the entire table → Borders → No Border
3. Add top border to first row, bottom border to header row, bottom border to last row
4. Result: a three-line table matching the booktabs aesthetic
