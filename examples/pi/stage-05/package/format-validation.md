# Stage 5 Markdown and DOCX Format Validation

## Gate status

- Scholar full-text attestation: recorded for 21/21 cited sources.
- Human-read ledger schema: PASS.
- Cite-time finalizer: 79/79 markers resolved to `ok`; 0 LOW-WARN; 0 NO-LOCATOR; 0 HIGH-BLOCK.
- Cite-time hard gate: PASS.
- Verified Stage 4.5 source remained unchanged at SHA-256 `513004b245efe8a557e92144faa8c06eb6bd95e16095d35a624d3d7d4870e40f`.

## Markdown output

- File: `02-final-paper-apa7.md`
- SHA-256: `64ac9f2d5794f1f920136259869fe6a8f4c248f74a5d052f8d349818796ad219`
- Transformation: exact Stage 4.5 manuscript with ARS audit/control comments stripped after gate PASS.
- Substantive prose changes: none.
- ARS markers remaining: 0.
- Warning/block tokens remaining: 0.

## DOCX output

- File: `03-final-paper-apa7.docx`
- SHA-256: `23740f600c870235efcf8a58b6ea4c3a5b79720f06e91f1d9af24e3639cf728a`
- Generator: Pandoc 3.10.
- Package integrity: `unzip -t` PASS.
- Page size: A4.
- Margins: 1 inch / 2.54 cm on all sides.
- Body fonts: Times New Roman for Latin text; Songti TC for Traditional Chinese fallback; 12 pt.
- Line spacing: double.
- Page numbers: top-right header, PAGE field present.
- Heading mapping: manuscript title → Title; main sections → Heading 1; subsections → Heading 2.
- References: Bibliography style with 0.5-inch hanging indent.
- Tables: 2; row counts 6 and 5, matching the Markdown source.
- Explicit title-page page break: present.
- ARS markers: absent.

## Content-preservation checks

- Pandoc plain-text comparison ratio: 0.9995657.
- After removing renderer-generated table-border lines, normalized Markdown and DOCX text are exactly equal (16,313/16,313 characters).
- Bilingual abstracts, keywords, body sections, two tables, Appendix A, 21 references, declarations, and bounded AI disclosure are present.
- The acknowledged compliance WARN was not inserted into manuscript prose.
- No model/provider/version, prompt detail, AI performance metric, or independent-verification claim was added.

## Nonblocking warnings

1. Pandoc reported missing `zh-TW` interface translations for the terms “Abstract” and “Table”; these warnings do not alter manuscript text because the document supplies its own headings and table labels.
2. The title page intentionally preserves the verified placeholders `［學生姓名］`, `［系所名稱］`, `［課程名稱］`, and `［教師姓名］`. The package is not submission-ready until the scholar replaces them.
3. No journal-specific template or Format Profile was declared; generic APA 7 course-paper formatting was applied.
4. The formatter ran sequentially in the same recovered model context; no independent formatter is claimed.

## Current status

Markdown and DOCX have passed format/content checks. Stage 5 remains in progress pending the in-stage LaTeX decision and later content confirmation.
