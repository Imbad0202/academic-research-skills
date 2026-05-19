# Three-Line Table Guide (Typst)

This guide defines the standard for professional academic tables using the "three-line" convention in Typst documents.

## Three-Line Table Standard

A three-line table has exactly three horizontal rules and **no vertical lines**:

1. **Top rule**: above column headers
2. **Mid rule**: below column headers, above data rows
3. **Bottom rule**: below the last data row

### Typst Implementation

```typst
#figure(
  table(
    columns: 3,
    stroke: none,
    table.hline(stroke: 0.8pt),
    [*Model*], [*Precision*], [*Recall*],
    table.hline(stroke: 0.5pt),
    [Baseline], [85.3], [82.1],
    [Ours], [*91.2*], [*89.5*],
    table.hline(stroke: 0.8pt),
  ),
  caption: [Comparison of model accuracy (%).],
) <tab:accuracy>
```

### Key Points

- Set `stroke: none` on the table to remove all default borders
- Use `table.hline(stroke: 0.8pt)` for top and bottom rules (heavier)
- Use `table.hline(stroke: 0.5pt)` for the mid rule (lighter)
- Never use `table.vline()` — no vertical lines in three-line tables
- Never add extra `table.hline()` between data rows

### Anti-Patterns (must flag)

- `table.vline()` anywhere in the table
- More than 3 `table.hline()` calls
- Default stroke (non-none) that produces grid lines
- `stroke: 1pt` or similar on the table element itself

## Number Alignment

Typst does not have a built-in `siunitx` equivalent. For decimal alignment:
- Right-align numeric columns using `align: right`
- Ensure consistent decimal places manually

```typst
table(
  columns: (auto, 1fr, 1fr),
  align: (left, right, right),
  // ...
)
```

## Statistical Significance Markers

| Symbol | Meaning |
|--------|---------|
| `*`    | p < 0.05 |
| `**`   | p < 0.01 |
| `***`  | p < 0.001 |

## Number Precision Rules

| Data type | Precision | Example |
|-----------|-----------|---------|
| Percentage | 1 decimal place | 85.3% |
| Mean +/- SD | 2 decimal places | 3.14 +/- 0.05 |
| p-value | 3 significant figures | 0.003 |

Precision must be consistent within each column.

## Caption and Note Placement

- **Caption**: Use `#figure(caption: [...])` — Typst places table captions above by default when using `figure.where(kind: table)` show rule
- **Label**: `<tab:name>` after the figure
- **Table note**: Add below the table inside the figure: `[Note. Bold values indicate best performance.]`

## Bold Best Values

Use `*bold*` syntax in Typst: `[*91.2*]` for bold emphasis on best values.

## Word Compatibility Note

When converting to .docx:
1. Create a standard table in Word
2. Select all -> Borders -> No Border
3. Add top border, header bottom border, table bottom border
4. Result: three-line table
