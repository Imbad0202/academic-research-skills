# Three-Line Table Guide (GB/T Chinese Thesis)

This guide defines the standard for professional academic tables in Chinese theses using the "three-line" (booktabs) convention, following GB/T 7714 and common university thesis requirements.

## Three-Line Table Standard

A three-line table has exactly three horizontal rules and **no vertical lines**:

1. **Top rule** (`\toprule`): above column headers
2. **Mid rule** (`\midrule`): below column headers, above data rows
3. **Bottom rule** (`\bottomrule`): below the last data row

### Anti-Patterns (must flag)

- Vertical lines (`|` in column spec, `\vline`)
- Internal horizontal lines (`\hline` or `\cline` between data rows)
- Using `\hline` instead of booktabs commands
- Missing `\usepackage{booktabs}` in preamble

### Minimal Correct Example

```latex
\begin{table}[htbp]
  \caption{不同模型的准确率比较（\%）}
  \label{tab:accuracy}
  \centering
  \begin{tabular}{lSSS}
    \toprule
    模型 & {精确率} & {召回率} & {F1值} \\
    \midrule
    基线模型   & 85.3 & 82.1 & 83.7 \\
    本文方法   & \textbf{91.2} & \textbf{89.5} & \textbf{90.3} \\
    \bottomrule
  \end{tabular}
\end{table}
```

## Caption and Numbering (GB/T)

- **Caption position**: above the table
- **Numbering format**: "表 3-1" or "表3.1" (chapter-based), Song typeface 5-point (宋体五号)
- **Label**: immediately after caption (`\label{tab:...}`)
- **Table note**: below the table, starting with "注：" (Chinese) or "Note." (English)

## Decimal Alignment

Use the `siunitx` package `S` column type to align numbers by decimal point:

```latex
\usepackage{siunitx}
\sisetup{detect-weight, mode=text}
```

When `siunitx` is unavailable, right-align numeric columns with `r`.

## Statistical Significance Markers

| Symbol | Meaning |
|--------|---------|
| `*`    | p < 0.05 |
| `**`   | p < 0.01 |
| `***`  | p < 0.001 |

Place significance markers immediately after the value: `91.2***`.

## Number Precision Rules

| Data type | Precision | Example |
|-----------|-----------|---------|
| Percentage | 1 decimal place | 85.3% |
| Mean +/- SD | 2 decimal places | 3.14 +/- 0.05 |
| p-value | 3 significant figures | 0.003 |
| Large counts | No decimals | 1,024 |

Precision must be consistent within each column.

## Bold Best Values

In comparison tables, bold the best value in each column. Add direction indicators when ambiguous:
- `↑` higher is better
- `↓` lower is better

## Word Compatibility Note

When submitting thesis with .docx:
1. Create a standard table in Word
2. Select all -> Borders -> No Border
3. Add top border, header bottom border, and table bottom border
4. Result: three-line table matching booktabs aesthetic
