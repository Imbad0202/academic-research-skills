# Quick mode: worked example

Six synthetic records screened against `example_protocol_dta.md` in `quick` mode (single
reviewer, no subagents). The records are invented for illustration.

## Records

```
### R00001 | 2021 | Journal Article | Lang: English
TI: Urinary NGAL two hours after cardiopulmonary bypass predicts acute kidney injury in infants
AB: Prospective cohort of 84 infants undergoing congenital heart surgery. Urinary NGAL was measured
before and 2, 6 and 12 h after bypass; AKI was defined by KDIGO within 72 h. AUC 0.86 at 2 h.

### R00002 | 2020 | Journal Article; Review | Lang: English
TI: Novel biomarkers of kidney injury in children: where do we stand?
AB: We review NGAL, KIM-1, IL-18 and L-FABP in paediatric AKI, including after cardiac surgery.

### R00003 | 2019 | Journal Article | Lang: English
TI: Plasma NGAL after pediatric cardiac surgery and postoperative acute kidney injury
AB: In 120 children, plasma NGAL at 2 h after surgery identified AKI (AUC 0.79).

### R00004 | 2022 | Journal Article | Lang: Chinese
TI: Early biomarkers of acute kidney injury after congenital heart surgery in children
AB: 64 children after surgery for congenital heart disease; early biomarkers were compared between
children with and without AKI.

### R00005 | 2018 | Journal Article | Lang: English
TI: Lipocalin-2 expression in a piglet model of cardiopulmonary bypass
AB: Twelve piglets underwent 2 h of cardiopulmonary bypass; renal lipocalin-2 expression rose.

### R00006 | 2023 | Letter | Lang: English
TI: Urinary NGAL cut-offs after paediatric cardiac surgery
AB: [NO ABSTRACT AVAILABLE]
```

## Decisions

| ID | Decision | Code | Deciding fact | What would change it |
|----|----------|------|---------------|----------------------|
| R00001 | include | INC | Infants, urinary NGAL after bypass, KDIGO AKI | - |
| R00002 | exclude | E1 | Narrative review | - |
| R00003 | exclude | E4 | Plasma NGAL only, no urinary NGAL | Urinary NGAL mentioned anywhere in the record |
| R00004 | unclear | UNC | Paediatric cardiac surgery; markers not named | Abstract naming the markers |
| R00005 | exclude | E2 | Piglet model only | - |
| R00006 | unclear | UNC | Urinary NGAL and paediatric cardiac surgery; data not established | Full text confirms whether the letter reports eligible data |

## Why these are the right calls

- **R00003** fails the index test clearly (the specimen is stated and it is plasma), so the
  record does not pass the unclear gate even though the population is right.
- **R00004** is in Chinese, but the English abstract is screened normally; the missing marker
  names make it unclear rather than excluded (protocol case d). The language is flagged in the
  outputs if Chinese is outside `languages_allowed`.
- **R00006** could be a letter with original data. A missing abstract does not prove it lacks
  data, and the title plausibly meets both core criteria, so retrieve the full text.

This table is a single-reviewer triage. For the review itself, a person acts as the second
reviewer, or the records go through the dual-review pipeline.
