# Module: Venue Reporting Checklist

**Trigger**: reporting, reproducibility, checklist, broader impact, limitations, ethics statement, compute disclosure, IRB, NeurIPS checklist, ACL checklist, ICLR reproducibility, 报告清单, 复现性声明, 伦理声明

## Commands

```bash
uv run python -B scripts/check_reporting.py main.tex --venue neurips
uv run python -B scripts/check_reporting.py main.tex --venue acl
uv run python -B scripts/check_reporting.py main.tex --venue iclr --json
uv run python -B scripts/check_reporting.py main.tex --venue ieee --strict
```

Supported venues: `neurips`, `icml`, `iclr`, `acl`, `chi`, `acm`, `ieee`,
`springer-lncs`.

## What this module checks

- Whether the paper contains each venue-required disclosure (Limitations,
  Broader Impact, Reproducibility, Ethics, Compute, IRB, etc.).
- Severity is derived from the venue's published policy, not from the
  reviewer's taste. CRITICAL items map to common desk-reject criteria.
- The auditor checks for **presence** of a statement, not its quality. A
  one-line "We acknowledge our model may have biases" passes the broader
  impact check on this module; quality of that statement is paper-audit's job.

## When to use

- Before submission to a venue with a published checklist (NeurIPS, ICML,
  ICLR, ACL/ARR, CHI).
- When adapting a paper across venues (run with the target `--venue` to
  surface newly-required items).
- After polishing language with `grammar` / `expression` / `deai`, as a
  final formal-completeness gate before `paper-audit`.

## When NOT to use

- For language or formatting issues (use `grammar`, `format`, `deai`).
- For deep quality assessment of statements (use `paper-audit` with
  `methodology_reviewer_agent` or `critical_reviewer_agent`).
- For citation correctness (use `bibliography`).
- For venues without a published checklist (the script will report
  best-practice items only; do not over-interpret WARN as REJECT).

## Output policy

- Default Markdown report with one entry per item:
  `[Script] <SEVERITY> [venue] <item>: PASS|MISSING — <signal> — <policy URL>`.
- `--json` returns a structured object: `{venue, summary: {pass, missing,
  critical_missing}, items: [...]}`.
- `--strict` upgrades all MAJOR-missing items to FAIL in the exit code, for
  CI gating.
- Exit code: `0` if no CRITICAL missing (and, with `--strict`, no MAJOR
  missing); `1` otherwise.

## Interaction with other modules

- Run **after** `compile`, `bibliography`, and `format` (those gate the
  paper at the syntax layer; this module gates at the policy layer).
- Run **before** `paper-audit` for pre-submission. paper-audit consumes the
  reporting summary as part of its synthesis input.
- If `adapt` (cross-venue retargeting) is invoked, run `reporting` again
  with the new `--venue` to surface newly-required items the prior venue
  did not enforce.

## Limitations

- Pattern-based detection. Heavily-rewritten or paraphrased statements may
  evade simple regex. When a CRITICAL item is reported MISSING, confirm by
  reading the relevant section before adding it.
- "CRITICAL when applicable" items (IRB for non-human-subject papers) are
  reported as MAJOR with an "applicability uncertain" note; the reviewer
  must confirm whether the venue's conditional requirement triggers.
- Yearly policy drift: `references/REPORTING_CHECKLISTS.md` is the source
  of truth. If the venue's call for papers has been updated since the date
  noted at the top of each venue block, prefer the official call.
