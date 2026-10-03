# Quality control

## Contents
1. What is checked and when
2. Agreement statistics
3. Seeds
4. Near-miss and random rechecks
5. Human verification and overrides
6. Sources

## 1. What is checked and when

| Check | Pilot | Full run | Blocks progress when |
|-------|-------|----------|----------------------|
| Seed studies found by the search | yes | - | a seed is missing (search problem) |
| Seed studies advanced | yes | yes | a seed is excluded |
| Completeness (no pending records) | yes | yes | always, before reporting |
| Discarded decisions (label/code mismatch, wrong batch) | yes | yes | many in one batch: inspect it |
| Agreement and conflicts | yes | yes | conflicts show a criterion read two ways |
| Unclear share and code distribution | yes | yes | far from the team's expectations |
| Near-miss and random rechecks | - | yes | QC advances a large share of rechecked records |
| Human verification | - | yes | always, before the numbers are published |

## 2. Agreement statistics

Computed on advance (include or unclear) versus exclude, for records decided by both reviewers:

- counts: both advance (a), both exclude (d), A only advances (b), B only advances (c), n = a+b+c+d
- observed agreement po = (a + d) / n
- chance agreement pe = pA*pB + (1 - pA)*(1 - pB), where pA = (a + b)/n, pB = (a + c)/n
- Cohen's kappa = (po - pe) / (1 - pe)
- PABAK = 2*po - 1 (prevalence-adjusted bias-adjusted kappa)

With extreme prevalence, which is normal in screening, kappa is low even when agreement is
excellent: when each reviewer advances only 2-3% of records, 97.8% observed agreement can come
with a kappa near 0.47 and a PABAK of 0.96. Report all four numbers with the counts, and judge
agreement from the conflicts themselves: what the reviewers disagreed about matters more than
the statistic.

## 3. Seeds

Seeds are 3-5 studies the team knows are eligible, listed in the config by DOI, PMID or title.
`prepare_records.py` reports where each one landed after de-duplication:

- **Not found**: the search strategy misses it. Fix the search before screening; screening
  cannot recover a record the search never retrieved.
- **Excluded in the pilot**: read both reasons. Usually a definition is too narrow or a code
  is read too broadly; amend the protocol and pilot again.

Seeds test sensitivity only for studies like them. They do not prove that nothing else was lost.

## 4. Near-miss and random rechecks

- **Near-miss**: an excluded record whose title, abstract or keywords match at least one
  pattern in *every* keyword group of `qc.near_miss`. One group per core criterion keeps the
  list short and on topic: a record that mentions the population, the specimen and the marker,
  yet was excluded, deserves a second look.
- **Joint-exclusion sample (required)**: `qc.random_exclusion_sample` records that both
  reviewers excluded (at least 20, default 100; all of them when fewer), drawn reproducibly
  (`qc.random_seed`) once screening is complete. A joint exclusion never reaches the
  adjudicator, and two instances of the same model can share one misreading, so this sample is
  the only independent look those records get. It catches errors that keywords cannot predict.
- Candidates are packed into their own batch files (`batches/qNNN.txt`, listed in
  `qc_batches.json`), so rechecking a few hundred records takes a handful of agent calls. The
  registry only grows and the joint-exclusion sample is drawn once per review, so repeated
  merges never reshuffle what a QC run referred to. Candidates count as pending until the
  senior reviewer has decided them, so no methods text or final number is produced before,
  including at the full-text stage. Full-text preparation waits for these decisions because a
  QC advance changes which PDFs must be screened.
- A senior reviewer (default model `sonnet`) screens these records afresh without seeing the
  earlier decision. With `qc.policy: advance`, an exclusion it would advance becomes an advance
  marked `QC`; with `flag`, it is only listed.
- Many advances among random rechecks mean the exclusions are not reliable: find the pattern
  (a code, a batch, records without abstracts) before trusting the run.

## 5. Human verification and overrides

AI screening is decision support. Before publication the team should, at minimum:

- check every advanced record (the full-text stage does this anyway), and
- read a random sample of exclusions (50-100 is common; widen the check if an eligible study
  turns up), plus the QC-flagged records.

Team decisions go into `overrides.csv` and win over every automatic decision. Synthetic examples:

```csv
id,d,code,why,by
R00002,unclear,UNC,children after cardiac surgery; urinary marker not named,HUMAN:EXAMPLE
R00003,exclude,E2,piglet model only,HUMAN:EXAMPLE
```

Merge again with `--overrides overrides.csv`. The earlier automatic decision is kept on the
record (`pre_override`) and shown in the log, so the change stays visible.

## 6. Sources

- Page MJ, et al. The PRISMA 2020 statement: an updated guideline for reporting systematic
  reviews. BMJ 2021;372:n71 (item 8, selection process).
- Lefebvre C, et al. Searching for and selecting studies. Cochrane Handbook for Systematic
  Reviews of Interventions, chapter 4.
- Feinstein AR, Cicchetti DV. High agreement but low kappa: I. The problems of two paradoxes.
  J Clin Epidemiol 1990;43:543-9.
- Byrt T, Bishop J, Carlin JB. Bias, prevalence and kappa. J Clin Epidemiol 1993;46:423-9.
