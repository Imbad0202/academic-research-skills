# Auditability and Re-execution Documentation

The pipeline standardizes stage contracts and records artifacts so a run can be inspected. This does not ensure identical model behaviour, judgements, or manuscript quality across executions.

## Standardized Workflow

| Contract surface | Mechanism and boundary |
|---------------|-----------|
| Integrity check every time | Stage 2.5 + Stage 4.5 are **mandatory** stages, cannot be skipped |
| Declared review angles | Journal-Fit Reviewer + R1/R2/R3 + Devil's Advocate — five role-separated perspectives; this is not evidence of independent errors or consistent findings |
| Declared verification procedure | integrity_verification_agent uses standardized templates and records coverage; semantic decisions and retrieval availability can vary |
| Explicit gate rules | Integrity PASS/FAIL criteria are inspectable; passing applies only to the registered/checked population and named verdict classes |
| Traceable workflow | Every stage's deliverables are recorded, enabling retrospective audit |

## Audit Trail

When the pipeline ends, state_tracker_agent produces a complete audit trail:

```
Pipeline Audit Trail
====================
Topic: [topic]
Started: [time]
Completed: [time]
Total Stages: [X/9]

Stage 1 RESEARCH: [mode] -> [output count]
Stage 2 WRITE: [mode] -> [word count]
Stage 2.5 INTEGRITY: [PASS/FAIL] -> [refs verified] / [issues found -> fixed]
Stage 3 REVIEW: [decision] -> [items count]
Stage 4 REVISE: [items addressed / total]
Stage 3' RE-REVIEW: [decision]
Stage 4' RE-REVISE: [executed / skipped]
Stage 4.5 FINAL INTEGRITY: [PASS/FAIL] -> [refs verified]
Stage 5 FINALIZE: Ask format style -> MD -> DOCX via Pandoc when available (otherwise instructions) -> LaTeX (apa7/ieee/etc.) -> tectonic -> PDF
Stage 6 PROCESS SUMMARY: Ask language -> MD -> LaTeX -> PDF (zh/en)

Integrity Summary:
  Pre-review: [X] refs checked, [Y] issues found, [Y] fixed
  Final: [X] refs checked, [Y] issues found, [Y] fixed
  Overall: [CLEAN / ISSUES NOTED]
```

## Re-execution boundary (v3.3.5+)

This document defines a PROCESS CONTRACT — declared stages, reviewer roles,
gate rules, and retained artifacts. It does not promise consistent outputs.

For computational re-execution documentation, see
[`../../shared/artifact_reproducibility_pattern.md`](../../shared/artifact_reproducibility_pattern.md).

The pipeline enforces process routing and deterministic validators where specified.
The Material Passport's optional `repro_lock` records configuration for inspection;
it is not a byte-replay guarantee for LLM output. The audit trail supports comparison,
not proof of equivalent outcomes or quality.
