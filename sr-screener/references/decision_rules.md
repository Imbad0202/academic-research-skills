# Decision rules

## Contents
1. Labels and codes
2. Title/abstract rules
3. Conflicts, adjudication and final labels
4. Edge cases
5. Full-text rules

The protocol always wins. These rules fill the gaps a protocol usually leaves, and the reviewer
prompts (`templates/prompts.md`) carry the short form.

## 1. Labels and codes

| Label | Code | Title/abstract meaning | Full-text meaning |
|-------|------|------------------------|-------------------|
| include | INC | every criterion that can be judged from the record is clearly met | every criterion met |
| unclear | UNC | core criteria plausibly met, text insufficient | information missing from the report, or file unreadable |
| exclude | protocol code | at least one criterion clearly fails | at least one criterion fails |

A label and code must agree (`include` with INC, `unclear` with UNC, `exclude` with a protocol
code). The scripts discard any decision where they do not; the record is then retried or stays
pending, never filled in.

## 2. Title/abstract rules

1. **Record text only.** The title, abstract, keywords and header fields are the evidence. A
   reviewer who "knows" the paper still judges the record, because recall is uneven (famous
   studies get remembered, small ones do not) and can be wrong.
2. **First failing code.** Check codes in the protocol's order and report the first that clearly
   fails. "Clearly" means the record states it (for example "in rats", "narrative review",
   "serum samples"), not that the reviewer suspects it.
3. **Full-text-only criteria never exclude here.** If an abstract does not mention the reference
   standard or the outcome data, that is silence, not failure.
4. **The unclear gate.** Unclear requires the core criteria to be plausibly met. A record that
   clearly fails a core criterion is excluded even if other parts look promising.
5. **Sensitive but decisive.** Between advancing and excluding a record that passes the gate,
   advance. Everything that clearly fails is excluded without hedging; a typical search has 95%
   or more irrelevant records.
6. **No abstract.** Decide from the title and publication type. Advance only when the title
   itself suggests the core criteria; exclude when the title or type clearly fails a criterion.
7. **Language.** Judge the English title/abstract when present. Languages outside
   `languages_allowed` are flagged in the outputs, not excluded, unless the protocol makes
   language a title/abstract criterion.

## 3. Conflicts, adjudication and final labels

| Reviewer A | Reviewer B | Final (policy `adjudicate`) | Final (policy `liberal`) |
|------------|------------|-----------------------------|--------------------------|
| include | include or unclear | include | include |
| unclear | unclear | unclear | unclear |
| exclude E_i | exclude E_j | exclude, earlier of E_i, E_j in protocol order | same |
| advance | exclude | adjudicator decides | the advancing label |

- The adjudicator re-reads the disputed records with both labels (not reasons) and applies the
  tie-break: advance when the core criteria are plausibly met.
- Include vs unclear is not a conflict at this stage; both advance.
- QC rechecks (Phase 5) can turn an exclusion into an advance (policy `advance`) or flag it
  (policy `flag`).
- Human overrides (`overrides.csv`) win over everything and are marked `HUMAN` (or the `by`
  value given).

## 4. Edge cases (defaults when the protocol is silent)

| Situation | Title/abstract default | Reason |
|-----------|------------------------|--------|
| Systematic review or meta-analysis | exclude as publication type | not primary research; the team may still mine its reference list |
| Narrative review with a new name ("update", "state of the art") | exclude as publication type | the label is not the test; the design is |
| Study protocol, trial registration | exclude as publication type unless ongoing studies are eligible | no results |
| Erratum, retraction notice, reply, comment | exclude as publication type | not a study report |
| Letter or short communication with original data | screen on content unless letters are excluded | some letters report data |
| Conference abstract | follow the protocol; if silent, screen on content and note the type | inclusion policies differ between reviews |
| Preprint, thesis | screen on content unless excluded | grey literature is often in scope |
| Case report / small series | apply the protocol's minimum size | |
| Animal and human data in one paper | judge the human part | |
| Human cells or samples studied only in vitro | "in vitro only" unless the protocol says otherwise | no participant-level data |
| Mixed population with a possibly eligible subgroup | unclear if the subgroup may be reported separately | resolved at full text |
| Secondary analysis, re-analysis, cohort update | screen on content | overlapping reports are linked at full text |
| Several records for one study | screen each record | linking is a full-text task |
| Title and abstract disagree | follow the more specific statement; unclear if unresolvable | |
| Non-English record with English abstract | screen normally, flag the language | |
| Retracted article | screen on content, flag it | the retraction is handled at full text |

## 5. Full-text rules

1. Judge the report in hand; do not rely on memory of the study.
2. Each criterion is met or not; there is no "plausibly".
3. One exclusion reason per report, the first failing criterion in the protocol order. PRISMA
   asks for the number of reports excluded for each reason, so each report needs exactly one.
4. `where` names the page and section with the deciding information, so a person can check the
   decision in seconds.
5. `unclear` means the information is not in the report (for example, eligible and ineligible
   age groups are mixed and separate data are not given): the study waits for classification or author contact. An
   unreadable or incomplete file is also `unclear`, with that reason.
6. Companion reports of the same study are assessed together at the end: keep one decision per
   report, then group reports into studies for the PRISMA "studies included" count.
