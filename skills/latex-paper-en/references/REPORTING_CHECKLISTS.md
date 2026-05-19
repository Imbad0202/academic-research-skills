# Venue Reporting Checklists

> Per-venue submission-gate items that go **beyond** language, formatting, and
> bibliography. Many top-tier CS/AI venues now require explicit statements
> (reproducibility, broader impact, limitations, compute resources, ethics,
> safeguards, etc.) as a condition of acceptance. Missing these is a common
> desk-reject reason that pure language polish cannot catch.
>
> This file is the data source for the `reporting` module. Each venue entry
> lists items the auditor scans for, the regex patterns that signal presence,
> the severity if missing, and the upstream policy reference.

## How to Use

- Run `uv run python -B scripts/check_reporting.py main.tex --venue neurips`
  to audit a paper against a specific venue's checklist.
- The script reads the venue tables below (mirrored in
  `scripts/check_reporting.py` as a Python dict) and produces a PASS / WARN /
  FAIL report per item.
- Patterns are deliberately permissive: they look for the presence of a
  *statement* (section, paragraph, or sentence), not for content quality.
  Quality review still goes through `paper-audit`.

## Severity

- **CRITICAL**: venue requires the item; absence is grounds for desk reject.
- **MAJOR**: venue strongly encourages or commonly demands; absence is a
  reviewer red flag.
- **MINOR**: best-practice item that improves reviewer confidence but is not
  formally required.

---

## NeurIPS

> Policy reference: NeurIPS Paper Checklist (2024 onward). See
> https://neurips.cc/public/guides/PaperChecklist

| Item | Severity | Signal patterns (any one match counts as present) |
|---|---|---|
| Limitations statement | CRITICAL | `\\section\\*?\\{[^}]*Limitation`, `limitations of (our|this) (work\|study\|approach)`, `we (acknowledge\|note) the following limitation` |
| Broader impact / societal impact | CRITICAL | `\\section\\*?\\{[^}]*(Broader Impact\|Societal Impact\|Impact Statement)`, `broader impact`, `societal (impact\|consequences)` |
| Reproducibility statement | CRITICAL | `\\section\\*?\\{[^}]*Reproducib`, `reproducibility (statement\|checklist)`, `to (ensure\|support) reproducibility` |
| Compute resources disclosure | MAJOR | `compute (resources\|budget)`, `(GPU\|TPU)[- ]hours`, `trained on \\d+ (GPU\|TPU)`, `wall[- ]?clock time` |
| Safeguards for high-risk artifacts | MAJOR | `safeguard`, `release (policy\|plan)`, `responsible (release\|disclosure)` |
| Code / data availability | MAJOR | `(code\|data) (is\|are\|will be) (available\|released)`, `https?://github\.com/`, `anonymous (github\|repository)` |
| Licenses for assets | MINOR | `\\bMIT\\b`, `Apache 2`, `CC[- ]BY`, `license:` |
| Crowdsourcing / human subjects | MINOR | `IRB`, `institutional review board`, `crowdworker (compensation\|wage)`, `informed consent` |

---

## ICML

> Policy reference: ICML uses the ML Reproducibility Checklist (Pineau et al.).
> ICML 2024 onward also expects Broader Impact discussion.

| Item | Severity | Signal patterns |
|---|---|---|
| Limitations statement | CRITICAL | (same as NeurIPS) |
| Broader impact discussion | MAJOR | `broader impact`, `societal (impact\|consequences)`, `ethical (consideration\|implication)` |
| Reproducibility: code release | CRITICAL | `(code\|implementation) (is\|will be) (available\|released)`, `https?://github\.com/`, `anonymous repository` |
| Reproducibility: data details | CRITICAL | `dataset (statistics\|split\|preprocessing)`, `train(ing)?[/ ]val(idation)?[/ ]test split`, `data preprocessing` |
| Reproducibility: hyperparameters | CRITICAL | `hyper[- ]?parameter`, `learning rate`, `batch size`, `random seed` |
| Reproducibility: compute | MAJOR | `(GPU\|TPU)[- ]hours`, `trained on \\d+ (GPU\|TPU)`, `compute (resources\|budget)` |
| Error bars / variance reporting | MAJOR | `error bar`, `confidence interval`, `standard deviation`, `\\\\pm\\s*\\d`, `over \\d+ (runs\|seeds)` |
| Statistical significance | MINOR | `statistical(ly)? significan`, `p[- ]value`, `t[- ]test`, `Wilcoxon` |

---

## ICLR

> Policy reference: ICLR Reproducibility Statement requirement (since 2022).

| Item | Severity | Signal patterns |
|---|---|---|
| Reproducibility statement | CRITICAL | `\\section\\*?\\{[^}]*Reproducib`, `reproducibility statement` |
| Ethics statement | CRITICAL | `\\section\\*?\\{[^}]*Ethic`, `ethics statement`, `ethical consideration` |
| Code release | MAJOR | `(code\|implementation) (is\|will be) (available\|released)`, `https?://github\.com/`, `anonymous (github\|repository)` |
| Compute resources | MAJOR | `(GPU\|TPU)[- ]hours`, `trained on \\d+ (GPU\|TPU)` |
| Hyperparameters in appendix | MAJOR | `(see\|in) (the\|our)? ?[Aa]ppendix`, `hyper[- ]?parameter`, `Table \\d.*hyper` |

---

## ACL / ARR (EMNLP / NAACL share the ARR checklist)

> Policy reference: ACL Rolling Review Responsible NLP Research Checklist.
> https://aclrollingreview.org/responsibleNLPresearch/

| Item | Severity | Signal patterns |
|---|---|---|
| Limitations section (mandatory, not in page count) | CRITICAL | `\\section\\*?\\{Limitations?\\}`, `\\section\\*?\\{[^}]*Limitation` |
| Ethics / risks discussion | CRITICAL | `\\section\\*?\\{[^}]*Ethic`, `ethics statement`, `potential risk`, `misuse` |
| Use of AI assistants disclosure | MAJOR | `AI (assistant\|writing tool)`, `ChatGPT\|GPT[- ]?4\|Claude\|Gemini`, `(was\|were) used (to\|for) (assist\|help\|polish)` |
| Computational budget | MAJOR | `(GPU\|TPU)[- ]hours`, `trained on \\d+ (GPU\|TPU)`, `compute (budget\|cost)`, `inference (cost\|time)` |
| Hyperparameter search | MAJOR | `hyper[- ]?parameter (search\|tuning\|sweep)`, `grid search`, `Bayesian optimization`, `best validation` |
| Dataset documentation | MAJOR | `dataset (card\|statistics\|description)`, `train(ing)?[/ ]val(idation)?[/ ]test`, `data preprocessing`, `data collection` |
| Licenses of artifacts used | MAJOR | `license:`, `\\bMIT\\b`, `Apache 2`, `CC[- ]BY`, `dataset license` |
| Demographic / annotator information | MINOR | `annotator (demographic\|background\|compensation)`, `crowdworker`, `IRB`, `informed consent` |

---

## CHI / CSCW / UIST (ACM HCI venues)

> Policy reference: ACM SIGCHI ethics policy + venue-specific calls.

| Item | Severity | Signal patterns |
|---|---|---|
| IRB / ethics approval for human subjects | CRITICAL | `IRB`, `institutional review board`, `ethics (committee\|approval)`, `approved by` |
| Informed consent | CRITICAL | `informed consent`, `participants (consented\|gave consent)` |
| Participant compensation | MAJOR | `(compensated\|paid) (participants\|with)`, `\\\\\\$\\d+ (per hour\|/hr)`, `gift card`, `compensation` |
| Demographic reporting | MAJOR | `(age\|gender\|ethnicity) of (participants\|the sample)`, `participant demographic`, `Mage\\s*=`, `participants \\(N\\s*=` |
| Data handling / privacy | MAJOR | `anonymi[sz]ed`, `pseudonym`, `data (storage\|handling\|retention)`, `GDPR` |
| Positionality / reflexivity (qualitative) | MINOR | `positionality`, `reflexivity`, `our (background\|perspective)` |

---

## ACM (general: TOPLAS, TOSEM, CCS, SIGMOD, etc.)

> Policy reference: ACM Artifact Review and Badging v1.1.
> https://www.acm.org/publications/policies/artifact-review-and-badging-current

| Item | Severity | Signal patterns |
|---|---|---|
| Artifact availability statement | MAJOR | `artifact (is\|will be) (available\|published)`, `https?://zenodo\.org/`, `https?://figshare\.com/`, `DOI:\\s*10\\.` |
| Reproducibility instructions | MAJOR | `(see\|in) the (artifact\|README)`, `to reproduce`, `README\\.md`, `install instructions` |
| Conflict of interest | MINOR | `conflict of interest`, `competing interest`, `the authors declare` |
| Funding disclosure | MINOR | `funded by`, `supported (in part\|by) (grant\|award)`, `grant (number\|no)\\.?\\s*\\w` |

---

## IEEE (transactions and most conferences)

> Policy reference: IEEE Author Center. IEEE does not require a uniform
> reproducibility checklist, but Trans. journals increasingly request code and
> data statements. Items here are best-practice, not mandatory.

| Item | Severity | Signal patterns |
|---|---|---|
| Data availability statement | MAJOR | `data (availability\|sharing) statement`, `(data\|code) (is\|are\|will be) (available\|released)` |
| Conflict of interest | MAJOR | `conflict of interest`, `competing interest`, `the authors declare (no\|the following)` |
| Funding statement | MAJOR | `funded by`, `supported (in part\|by)`, `grant (number\|no)\\.?\\s*\\w` |
| Ethical approval (if human / animal subjects) | CRITICAL when applicable | `IRB`, `ethics (committee\|approval)`, `animal (care\|use) committee` |
| Author contributions (CRediT) | MINOR | `author contribution`, `CRediT`, `\\bconceptualization\\b`, `\\bmethodology\\b.*\\bvalidation\\b` |

---

## Springer LNCS

> Policy reference: Springer Nature research integrity policy. LNCS conference
> proceedings inherit most journal-level disclosure expectations.

| Item | Severity | Signal patterns |
|---|---|---|
| Competing interests | MAJOR | `competing interest`, `conflict of interest`, `the authors declare` |
| Funding statement | MAJOR | `funded by`, `supported (in part\|by)`, `grant (number\|no)\\.?\\s*\\w` |
| Data availability | MAJOR | `data availability`, `(data\|code) (is\|are\|will be) (available\|released)` |
| Ethical approval (if applicable) | CRITICAL when applicable | `IRB`, `ethics (committee\|approval)` |

---

## Cross-venue Item Index

When a single item appears across venues, the script reuses the same pattern
set. The canonical source is this file; `scripts/check_reporting.py` must
keep its dict aligned. See `references/modules/REPORTING.md` for the module's
operational contract.

| Item | Used by |
|---|---|
| Limitations statement | NeurIPS, ICML, ACL/ARR |
| Broader / societal impact | NeurIPS, ICML |
| Reproducibility statement | NeurIPS, ICLR |
| Compute resources / budget | NeurIPS, ICML, ICLR, ACL/ARR |
| Ethics statement | ICLR, ACL/ARR, CHI |
| IRB / informed consent | NeurIPS (crowdsourcing), CHI, IEEE (when applicable) |
| Code / data availability | NeurIPS, ICML, ICLR, ACL/ARR, ACM, IEEE, Springer LNCS |
| Conflict of interest / funding | ACM, IEEE, Springer LNCS |
| AI assistant usage disclosure | ACL/ARR |

---

## Maintenance Notes

- Venue requirements evolve yearly. When updating, bump the policy reference
  date at the top of each venue block and cross-check against the live call
  for papers.
- Adding a new venue: add a new section here, mirror the items into
  `VENUE_CHECKLISTS` in `scripts/check_reporting.py`, and add the venue name
  to the `--venue` choices in the script's argparse setup.
- Items marked "CRITICAL when applicable" require the script to first detect
  whether the paper involves the triggering condition (human subjects, animal
  subjects, etc.). The current script flags them as MAJOR by default and
  notes "verify applicability" in the report.
