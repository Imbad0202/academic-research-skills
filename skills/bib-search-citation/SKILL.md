---
name: bib-search-citation
description: >-
  Search, filter, and format entries from BibTeX or BibLaTeX .bib files for
  research workflows. Use when a user wants to find papers, search a
  bibliography, filter a library, or look up references by topic, author, year,
  venue, DOI, arXiv ID, keywords, annotation, abstract, or entry type. Handles
  Zotero-exported libraries. Trigger for Chinese prompts such as "搜文献库",
  "查 BibTeX", "查文献", "翻文献库", "找引用", "查 Zotero 导出",
  "搜搜我的 .bib", "在文献库里找 Mamba 论文", "查 Cheng 2024 的引用",
  "整理参考文献", or "导出 BibTeX 条目". Supports compact search expressions
  such as author:, year-gte, type:, and has:, combined filters,
  research-oriented output fields, raw BibTeX export, and LaTeX/Typst citation
  snippets.
category: docs-writing-publishing
tags: [bibtex, biblatex, citation, latex, typst, bibliography, research, zotero, bib]
version: "1.1.0"
allowed-tools: Read, Bash
---

# Bib Search Citation

## Capability Summary

Use this skill when the user provides a local `.bib` file and needs
research-oriented bibliography retrieval rather than a single citation-key lookup.
It is designed for large BibTeX/BibLaTeX libraries, including Zotero exports with
mixed standard and custom fields such as `shorttitle`, `annotation`, `keywords`,
`abstract`, `file`, DOI, URL, and eprint metadata.

The skill can:

- search by topic words and field-specific filters
- filter by author, year, entry type, DOI, arXiv/eprint, PDF, code, keywords,
  annotation, or abstract
- return stable JSON for downstream tooling
- generate compact human-readable previews from JSON results
- emit LaTeX and Typst citation snippets
- return raw BibTeX only when exact export or manual verification requires it

## Triggering

Use this skill for requests such as:

- "Search my `.bib` file for recent Mamba forecasting papers."
- "Find entries by Cheng after 2024 that have code and return cite snippets."
- "Show the raw BibTeX for the best TimeMachine match."
- "Filter Zotero-exported entries whose annotation mentions CodeAvailable."
- "Preview the JSON output from a saved bibliography search."

If the user gives only a natural-language request, infer a conservative search
spec and state the assumptions. If the user gives a compact filter expression,
preserve it as closely as possible instead of translating it into vague prose.

## Do Not Use

Do not use this skill for:

- validating citations already used inside a `.tex` or `.typ` project
- compiling, formatting, or diagnosing manuscript source trees
- rewriting related-work prose
- online literature discovery when there is no local bibliography file
- inventing missing bibliographic metadata that is not present in the `.bib` file

For manuscript citation integrity, use the relevant writing skill's bibliography
module. For online paper discovery, use a research-oriented workflow and verify
metadata from external sources before adding it to a library.

## Module Router

| Module | Best for | Command |
| --- | --- | --- |
| `query` | one-shot compact search with inline filters | `uv run python -B $SKILL_DIR/scripts/search_bib.py --bib references.bib --query 'mamba forecasting author:Cheng year>=2024 has:code cite:both limit:5'` |
| `spec-json` | structured search spec generated from a complex request | `uv run python -B $SKILL_DIR/scripts/search_bib.py --bib references.bib --spec-json '{"query":"mamba forecasting","filters":{"year_min":2024},"citation_mode":"both"}'` |
| `spec-file` | repeatable saved search workflow | `uv run python -B $SKILL_DIR/scripts/search_bib.py --bib references.bib --spec-file search.json` |
| `preview` | compact human-readable summary after JSON search output exists | `uv run python -B $SKILL_DIR/scripts/preview_bib_search.py --input results.json` |

Keep `search_bib.py` as the source of truth for parsing, filtering, scoring,
sorting, raw BibTeX preservation, and citation snippet generation. Treat
`preview_bib_search.py` as a renderer only.

## Required Inputs

Minimum inputs:

- path to one local `.bib` file
- either a compact `--query`, inline `--spec-json`, or saved `--spec-file`
- optional sort, limit, citation-mode, raw BibTeX, or returned-field preferences

Common search spec fields:

- `query`: free-text topic query
- `filters.year_min`, `filters.year_max`, `filters.years_in`, `filters.exclude_years`
- `filters.author_contains`, `filters.author_excludes`
- `filters.type_in`, `filters.exclude_type_in`
- `filters.has`, `filters.exclude_has`
- `filters.field_contains`, `filters.field_excludes`
- `sort`: `relevance`, `year_desc`, `year_asc`, or `title`
- `limit`: default 5 unless the user asks for more
- `return_fields`: fields to expose in the JSON result
- `include_raw_bib`: `true` only when the user asks for original entries or exact export
- `citation_mode`: `latex`, `typst`, `both`, or `none`

## Output Contract

When presenting results to the user, use this order:

1. Briefly state how many matches were found and which filters were applied.
2. List top matches with requested research fields.
3. Include LaTeX and/or Typst snippets when requested or useful.
4. Include raw BibTeX only when requested or materially needed.
5. If no entries match, suggest specific filter relaxations.

For each selected entry, usually include:

- citation key
- title and optional shorttitle
- authors
- year and venue/journal/booktitle
- DOI and/or eprint when present
- the supporting fields that made the entry relevant, such as keywords,
  annotation, or a short abstract excerpt

If the user supplied compact filters, echo the interpreted filters when negation,
field filters, or mixed citation/export options could otherwise be ambiguous.

## Workflow

1. Identify the `.bib` file path. If multiple candidates exist, use the one the
   user named or ask one concise clarification only if choosing would be risky.
2. If `rtk` is available, use it only for model-facing exploration such as locating
   `.bib` files or inspecting representative fields.
3. Translate the request into a compact query or JSON search spec.
4. Run `search_bib.py` with `uv run python -B` and preserve the JSON output.
5. Optionally run `preview_bib_search.py` after JSON output exists.
6. Inspect the result payload before answering.
7. Report matches, citation snippets, raw entries, or empty-result recovery advice
   according to the output contract.

RTK fast path guidance:

- locate bibliography files with `rtk find . -name "*.bib"`
- inspect a representative slice with `rtk read /path/to/library.bib -l aggressive -m 80`
- confirm fields with `rtk grep "doi|keywords|annotation|eprint" /path/to/library.bib`
- do not wrap machine-readable `search_bib.py` JSON output with RTK compression

## Search Planning

Use these defaults unless the user says otherwise:

- research discovery request -> `sort: relevance`
- no explicit limit -> `limit: 5`
- no explicit field list -> return `key`, `title`, `shorttitle`, `author`, `year`,
  `venue`, `doi`, `eprint`, `keywords`, `annotation`, and `abstract`
- asks for "original", "full entry", or "bib" -> `include_raw_bib: true`
- asks for citation snippets in a mixed LaTeX/Typst workflow -> `citation_mode: both`

Supported compact operators include:

- `author:cheng`
- `year>=2024`, `year<=2025`, `year:2024`, `year:2023,2024`
- `type:article,misc`, `-type:misc`
- `has:code,doi`, `-has:pdf`
- `annotation:CodeAvailable`, `keywords:mamba`, `abstract:photovoltaic`
- `sort:year_desc`, `limit:10`, `fields:key,title,year,doi`
- `cite:latex`, `cite:typst`, `cite:both`, `cite:none`
- `raw:true`

The useful `has` values are `doi`, `abstract`, `keywords`, `annotation`,
`shorttitle`, `eprint`, `pdf`, and `code`. The `code` flag is inferred from
fields such as `url`, `abstract`, `keywords`, `annotation`, `note`, and
`howpublished` when they mention GitHub, GitLab, code, repository, or source.

## Safety Boundaries

- Do not fabricate missing titles, authors, venues, DOIs, URLs, or eprint IDs.
- Treat raw BibTeX as source data; preserve it exactly when quoting or exporting.
- Do not claim an entry strongly supports a manuscript claim unless the relevant
  fields actually support that relationship.
- If the `.bib` file is malformed, report that entries may have been skipped
  instead of silently presenting the result set as complete.
- Keep online discovery out of this skill unless the user explicitly asks to
  extend beyond the local bibliography and the external metadata is verified.
- Do not edit the user's `.bib` file unless they explicitly ask for a rewrite or
  export operation.

## Reference Map

- `scripts/search_bib.py`: parses `.bib` files, applies filters, ranks results,
  and formats citation snippets.
- `scripts/preview_bib_search.py`: renders `search_bib.py` JSON into a compact
  human-readable summary.
- `references/query-syntax.md`: maps natural-language requests into compact query
  expressions and JSON search specs.
- `examples/compact-query.md`: typical topic search with filters and citations.
- `examples/raw-bib-export.md`: exact-entry export workflow.
- `examples/preview-summary.md`: JSON search plus preview rendering workflow.

## Example Requests

```text
Search references.bib for Cheng papers after 2024 on Mamba forecasting and return both LaTeX and Typst citations.
```

```text
Find entries in library.bib whose annotation contains CodeAvailable and show the raw BibTeX.
```

```text
List the newest transformer forecasting papers in references.bib, but exclude misc entries and require DOI.
```

```text
Find the best TimeMachine match in references.bib and return one raw entry plus cite snippets.
```

## Error Handling

### Parse errors

If a `.bib` file contains malformed entries, the script processes the valid
entries it can parse. When unexpectedly few entries are returned, inspect the
file encoding and look for obvious structural corruption such as missing closing
braces.

### Empty result sets

When zero entries match, suggest broadening the search in this order:

1. remove `has:` constraints such as `has:code`
2. widen or remove the year range
3. use fewer or shorter topic keywords
4. check author spelling or try partial-name matches

### Large files

The helper scripts use linear scans and no external parser dependency. For very
large libraries, expect proportionally longer runtime but the same JSON contract.
