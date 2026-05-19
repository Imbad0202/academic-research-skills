# Journal Adaptation Workflow

This reference defines the step-by-step process for adapting a paper from one venue to another. The `adapt` module uses this workflow to guide systematic format conversion.

## Workflow Overview

### Step 1: Identify Source and Target Formats

1. **Detect current format** from document preamble:
   - `\documentclass{IEEEtran}` → IEEE
   - `\documentclass{acmart}` → ACM
   - `\documentclass[conference]{...}` → Conference paper
   - Typst: check `#import` or template usage
2. **Accept target format** from user:
   - User-provided journal guide takes **highest priority**
   - If no guide provided, use known venue rules from VENUES.md
   - If target venue is unknown, ask the user to provide the submission guidelines

### Step 2: Generate Diff Checklist

Compare source and target requirements across these dimensions:

#### 2a. Reference Format
- Citation style change (IEEE → APA, etc.)
- Cross-reference CITATION_STYLES.md for exact rules
- BibTeX style file change (`\bibliographystyle{...}`)
- Author truncation threshold change

#### 2b. Abstract Format
- Word count limit adjustment
- Structured vs unstructured abstract
- Keyword requirements (number, format)

#### 2c. Number and Unit Conventions
- Cross-reference NUMBER_UNIT_GUIDE.md
- SI unit formatting
- Number-word thresholds
- Percentage and statistical precision

#### 2d. Figure and Table Requirements
- Caption format (sentence case vs title case)
- Figure resolution requirements (DPI)
- Table style (booktabs required?)
- Placement rules (top of page, column-spanning)
- Color vs grayscale requirements

#### 2e. Page Layout (Manual Items)
- Margins, columns, line spacing
- Font family and size
- Header/footer content
- Page numbering style

### Step 3: Apply Automated Changes

For each diff item that can be changed in the source:
1. Make the change
2. Annotate with `[ADAPTED: reason]` in a comment

Changes that CAN be automated:
- Bibliography style switch
- Abstract word count trim (flagging, not cutting)
- Number formatting adjustments
- Caption style adjustments
- Package additions/removals

### Step 4: Output

Deliver two artifacts:

**Artifact 1: Modified Text**
- The adapted source with `[ADAPTED: ...]` annotations on changed lines
- Never alter substantive content (arguments, data, conclusions)

**Artifact 2: Manual Checklist**
Items that require manual intervention in Word/LaTeX/Typst settings:

```markdown
## Manual Adaptation Checklist

### Page Layout
- [ ] Set margins to [X cm / inches]
- [ ] Set columns to [single / double]
- [ ] Set line spacing to [single / 1.5 / double]
- [ ] Set font to [Times New Roman / Computer Modern / ...]
- [ ] Set font size to [10pt / 11pt / 12pt]

### Figures
- [ ] Verify all figures are [minimum DPI]
- [ ] Convert color figures to grayscale if required
- [ ] Check figure placement: [top of page / inline / ...]

### Tables
- [ ] Verify table style matches venue (booktabs / grid)
- [ ] Check caption position (above / below)

### Other
- [ ] Add/update page numbers
- [ ] Add/update running header
- [ ] Check supplementary material limits
- [ ] Verify total page count: [N pages max]
```

## Constraints

- **Never alter substantive content**: arguments, data, methodology, conclusions must remain unchanged
- **User-provided guide overrides all defaults**: if the user supplies a journal's author guidelines, those rules take absolute priority over VENUES.md
- **Flag uncertainty**: if a guideline is ambiguous or not found, flag it for user verification rather than guessing
- **Preserve all citations, labels, math environments**: same protection rules as all other modules
