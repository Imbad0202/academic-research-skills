# Reporting and handoff

## Contents
1. PRISMA 2020 numbers
2. Methods text and AI disclosure
3. Reference-manager import
4. Handoff to Academic Research Skills

## 1. PRISMA 2020 numbers

| PRISMA flow box | Source |
|-----------------|--------|
| Records identified from each database | `identification.json` `by_database` (raw records per export) |
| Duplicate records removed | `duplicates_removed` |
| Records screened | unique records with valid current final decisions |
| Records excluded | final title/abstract exclusions (the code breakdown is optional in PRISMA) |
| Reports sought for retrieval | records advanced (include + unclear) |
| Reports not retrieved | `ft_not_retrieved.csv` |
| Reports assessed for eligibility | retrieved reports with valid current final decisions |
| Reports excluded, with reasons | full-text exclusions by code, one reason per report |
| Studies included | full-text includes, after grouping companion reports into studies |

`*_prisma_counts.md` holds a Mermaid diagram (GitHub renders it) plus the JSON numbers. Records
from registers, websites or citation searching have separate PRISMA boxes; add them by hand.
Check that the per-database numbers match what each database reported for the search; if an
export was capped or split, say so.

Both stages mark counts as provisional and withhold methods text while any required decision
or recheck is pending. Full-text completeness also includes unfinished title/abstract screening,
adjudication and QC, even when every currently matched PDF already has a full-text decision.
Every prepared record (or FT manifest entry) needs a final decision; absent pending files do not
make missing decisions complete. Full-text preparation must also match the current TA decisions:
all advances occur exactly once in either retrieved or not-retrieved, and the TA decision snapshot
must be unchanged. A stale set stays provisional until it is prepared and assessed again.
The full-text diagram includes reports awaiting classification as a separate branch.

## 2. Methods text and AI disclosure

`*_methods_selection.md` is a draft with real numbers and `[TO COMPLETE]` slots. It covers what
PRISMA 2020 item 8 asks for: how many reviewers screened each record, whether they worked
independently, how disagreements were resolved, and which automation tools were used. The team
completes:

- the dates of the runs;
- the human verification that actually happened (who checked what, how many exclusions were
  sampled, what was changed);
- the final human-confirmed numbers.

Before submission, check the target journal's AI policy and current guidance on AI in evidence
synthesis (for example the RAISE recommendations). Name the exact models (`model_labels` in the
config), the tool and its version, and keep the screening log as a supplementary file.

## 3. Reference-manager import

- **EndNote**: File > Import > File, "Reference Manager (RIS)", Unicode (UTF-8). The decision is
  in Label (`TA-Include`, `TA-Unclear`, `TA-Exclude-E3`), the reasons in Notes; build smart
  groups on Label. The record ID (`R00012`) is in the Reference ID field and in the note.
- **Zotero**: import each RIS file into its own collection; `--tag-keywords` adds the decision
  as a tag.
- **Rayyan / Covidence**: import the RIS files, or use the Excel log to compare decisions.

Each RIS record is the richest source version (PubMed first) of the de-duplicated group, with
its original fields untouched plus the label and note.
Every rebuild writes all three category files, including empty categories, so earlier group
files cannot retain overridden records. Strings beginning with formula/control prefixes are
escaped as text in XLSX and CSV screening logs; the original record text remains in the source data.
All CSV exports quote every field, including empty fields. Formula prefixes after embedded
semicolons or tabs are also escaped with an apostrophe, so alternative-separator readers cannot
expose an executable formula by splitting a field. Original source data is preserved.

## 4. Handoff to Academic Research Skills

Within Academic Research Skills (ARS), `deep-research` covers research design and the search,
and `academic-paper` covers writing; this skill covers the screening in between.

- **Corpus**: `*_literature_corpus.yaml` is a list of `literature_corpus[]` entries in the ARS
  `literature_corpus_entry.schema.json` format (citation key, title, CSL-JSON authors, year,
  source pointer, venue, DOI, tags, provenance `obtained_via: other`,
  `adapter_name: sr-screener`). Paste it under `literature_corpus:` in a Material Passport, or
  give it to `academic-paper` or `deep-research` as the curated corpus: their literature agents
  then read it first and search only for gaps.
- **Methods and results**: give `academic-paper` (`full` or `lit-review` mode) the methods
  draft, the PRISMA counts and the excluded-with-reasons list for the Methods, Results and flow
  diagram.
- **What stays here**: screening decisions. The receiving skills read the corpus; if they
  re-apply criteria, it should be the same protocol, and any disagreement comes back here as an
  override with a reason.
- The corpus file has no abstracts: abstracts can be publisher-copyrighted, and passports are
  often shared.
