---
name: typst-paper
description: Typst academic paper assistant for existing `.typ` manuscripts in English or Chinese. Use whenever the user wants Typst compile/export diagnosis, venue formatting, BibTeX or Hayagriva bibliography checks, grammar, sentence-length, logic, abstract, title, table, pseudocode, experiment-section, de-AI, translation, expression, related-work synthesis, research-gap derivation, journal adaptation, or submission-readiness help on a Typst paper. Trigger even if the prompt mentions only a .typ file, typst compile/export error, typst bibliography, one section rewrite, rewrite related work, research gap, three-line table, check abstract, reformat for another journal, algorithm-figure, lovelace, or algorithmic.
metadata:
  category: academic-writing
  tags: [typst, paper, chinese, english, ieee, acm, springer, neurips, compilation, grammar, bibliography, hayagriva, pseudocode, algorithmic, lovelace]
  version: "1.3"
  last_updated: "2026-05-03"
argument-hint: "[main.typ] [--section SECTION] [--module MODULE]"
allowed-tools: Read, Glob, Grep, Bash(uv *), Bash(typst *)
---

# Typst Academic Paper Assistant

Use this skill for targeted work on an existing Typst paper project. Route requests to the smallest useful module and keep outputs compatible with Typst source review.

## Capability Summary

- Compile Typst projects and diagnose Typst CLI issues.
- Audit format, bibliography, grammar, sentence length, argument logic, expression quality, and AI traces.
- Diagnose and rewrite-plan literature review sections so they move from theme clustering to comparison and gap derivation.
- Review IEEE-like pseudocode blocks for `algorithmic`, `algorithm-figure`, `lovelace`, caption handling, and comment length.
- Support both BibTeX and Hayagriva bibliography files.
- Improve titles, translation, and experiment-section clarity for Typst papers.

## Triggering

Use this skill when the user has an existing `.typ` paper project and wants help with:

- Typst compilation or export issues
- format or venue compliance
- bibliography validation for BibTeX or Hayagriva
- grammar, sentence, logic, or expression review
- literature review restructuring, related-work synthesis, or research-gap derivation
- translation or bilingual polishing
- title optimization
- pseudocode and algorithm-block review
- de-AI editing
- experiment-section review

## Do Not Use

Do not use this skill for:

- LaTeX-first conference or thesis projects
- DOCX/PDF-only editing without Typst source
- thesis template detection or GB/T 7714 thesis workflows
- from-scratch paper planning or literature research
- multi-perspective review, scoring, or submission gate decisions (use `paper-audit`)
- standalone pseudocode drafting without a paper context

## Module Router

| Module | Use when | Primary command | Read next |
| --- | --- | --- | --- |
| `compile` | Typst build, export, font, or watch issues | `uv run python $SKILL_DIR/scripts/compile.py main.typ` | `references/modules/COMPILE.md` |
| `format` | Venue/layout review for a Typst paper | `uv run python $SKILL_DIR/scripts/check_format.py main.typ` | `references/modules/FORMAT.md` (load `templates/<venue>.md` instead of the full `references/VENUES.md` when a venue is named) |
| `bibliography` | BibTeX or Hayagriva validation | `uv run python $SKILL_DIR/scripts/verify_bib.py references.bib --typ main.typ` | `references/modules/BIBLIOGRAPHY.md` |
| `grammar` | Grammar cleanup on Typst prose | `uv run python $SKILL_DIR/scripts/analyze_grammar.py main.typ --section introduction` | `references/modules/GRAMMAR.md` |
| `sentences` | Long or dense sentence diagnostics | `uv run python $SKILL_DIR/scripts/analyze_sentences.py main.typ --section introduction` | `references/modules/SENTENCES.md` |
| `logic` | Argument flow, introduction funnel, cross-section closure, and abstract/conclusion alignment review | `uv run python $SKILL_DIR/scripts/analyze_logic.py main.typ --section methods` | `references/modules/LOGIC.md` |
| `literature` | Related Work is list-like, under-compared, or missing a literature-backed gap | `uv run python $SKILL_DIR/scripts/analyze_literature.py main.typ --section related` | `references/modules/LITERATURE.md` |
| `expression` | Tone and expression polishing | `uv run python $SKILL_DIR/scripts/improve_expression.py main.typ --section methods` | `references/modules/EXPRESSION.md` |
| `translation` | Chinese/English academic translation in Typst context | `uv run python $SKILL_DIR/scripts/translate_academic.py input_zh.txt --domain deep-learning` | `references/modules/TRANSLATION.md` |
| `title` | Generate, compare, or optimize Typst paper titles | `uv run python $SKILL_DIR/scripts/optimize_title.py main.typ --check` | `references/modules/TITLE.md` |
| `pseudocode` | Review `algorithmic` / `algorithm-figure` / `lovelace` output for IEEE-like safety, captions, and comment length | `uv run python $SKILL_DIR/scripts/check_pseudocode.py main.typ --venue ieee` | `references/modules/PSEUDOCODE.md` |
| `deai` | Reduce English or Chinese AI-writing traces while preserving Typst syntax | `uv run python $SKILL_DIR/scripts/deai_check.py main.typ --section introduction` | `references/modules/DEAI.md` |
| `experiment` | Inspect experiment-section clarity, discussion layering, and reporting quality | `uv run python $SKILL_DIR/scripts/analyze_experiment.py main.typ --section experiment` | `references/modules/EXPERIMENT.md` |
| `tables` | Table structure validation, three-line table generation | `uv run python $SKILL_DIR/scripts/check_tables.py main.typ` | `references/modules/TABLES.md` |
| `abstract` | Abstract five-element structure diagnosis and word count validation | `uv run python $SKILL_DIR/scripts/analyze_abstract.py main.typ` | `references/modules/ABSTRACT.md` |
| `adapt` | Journal adaptation: reformat paper for a different venue | (LLM-driven workflow) | references/modules/ADAPT.md |

## Routing Rules

- Infer the module from the user request first. Ask for the module only if the request still maps equally well to multiple incompatible modules.
- If the user requests 2-3 compatible checks, run them in sequence rather than collapsing everything into one generic review.
- Use this execution order when multiple modules are needed: `compile` -> `bibliography` -> `format` -> `pseudocode` / `tables` -> `grammar` / `sentences` / `deai` -> `logic` / `literature` / `experiment` -> `title` / `expression` / `translation` / `adapt`.
- For bibliography requests, decide BibTeX vs Hayagriva before running the script; do not guess the format after the fact.
- Prefer `logic` for abstract-introduction-conclusion alignment, introduction funnel breaks, or contribution drift; prefer `literature` only when the user is specifically asking for Related Work synthesis, comparison, or gap derivation.
- Keep `pseudocode` for `algorithm-figure`, `algorithmic`, `lovelace`, caption, wrapper, and IEEE-like style-hook issues even when the user phrases them as formatting problems.
- If a command fails, report the exact command and exit code before suggesting the next fallback; do not silently replace a failed script run with a generic prose review.

## Required Inputs

- `main.typ` or the Typst entry file.
- Optional `--section SECTION` for targeted analysis.
- Optional bibliography path when the request targets references.
- Optional venue context when the user cares about IEEE, ACM, Springer, or similar expectations.

If arguments are missing, preserve the inferred module and ask only for the missing Typst entry file, section, bibliography path, or venue context.

## Output Contract

- Return findings in Typst diff-comment style whenever possible: `// MODULE (Line N) [Severity] [Priority]: Issue ...`
- Report the exact command used and the exit code when a script fails.
- Preserve `@cite`, `<label>`, math blocks, and Typst macros unless the user explicitly asks for source edits.
- For `literature`, diagnose and offer a rewrite blueprint first; only produce revised prose when the user explicitly asks for it.

## Workflow

1. Parse `$ARGUMENTS`, infer the active module, and keep that inference unless the user explicitly changes the target.
2. If the request combines multiple compatible concerns, run them in the routing order above and group the output by module.
3. Read only the reference file needed for that module.
4. Run the module script with `uv run python ...`.
5. Return Typst-ready comments and next actions.
6. For bibliography requests, decide BibTeX vs Hayagriva first, then run `bibliography`.

## Safety Boundaries

- Don't invent citations, labels, or experimental claims — fabricated evidence is harder to retract once the user trusts it than a clearly flagged gap.
- Leave `@cite`, `<label>`, math blocks, and Typst macros untouched by default — a stray edit there is far harder to spot in a diff than a prose edit, and Typst surfaces those errors only at compile time.
- Keep compile diagnostics separate from prose rewrites — bundling them encourages the user to apply both at once and lose track of which change broke what.

## Reference Map

- `references/TYPST_SYNTAX.md`: Typst syntax reminders and pitfalls.
- `references/STYLE_GUIDE.md`: paper-writing style baseline.
- `references/CITATION_VERIFICATION.md`: citation verification workflow.
- `references/VENUES.md`: full venue catalog (treat as index; prefer `templates/<venue>.md` for IEEE / ACM / NeurIPS).
- `templates/`: per-venue snapshots loaded on demand. Files: `ieee.md`, `acm.md`, `neurips.md`.
- `references/modules/`: module-specific Typst commands and choices.
- `references/modules/PSEUDOCODE.md`: IEEE-like defaults for Typst pseudocode.

Read only the file that matches the active module.

## Example Requests

- “Compile this Typst paper and tell me why the export works locally but fails in CI.”
- “Check bibliography, title, and abstract wording in my `main.typ` submission.”
- “Rewrite the related work in my Typst paper so it sounds like an academic dialogue rather than a paper list, but keep citation anchors untouched.”
- “Review this `algorithm-figure` block for IEEE-like caption, line-number, and comment issues.”
- “Review the methods section for sentence length and logic, but keep Typst labels intact.”

See `examples/` for full request-to-command walkthroughs.
