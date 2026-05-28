# evals/ — gold-set corpora for ARS measurement targets

This directory holds the v3.10 #184 generalized gold sets. Each subdirectory under `gold/` is a self-contained gold set for one measurement target. The structure mirrors the v3.8 `scripts/fixtures/claim_audit_calibration/` pattern but generalizes to multiple targets.

## Layout

```
evals/
├── README.md                          # this file
├── gold/
│   ├── citation_extraction/           # Phase 1a — baseline for #182
│   │   ├── README.md                  # this file (shipped)
│   │   ├── manifest.yaml              # (Phase 1a, in progress)
│   │   ├── tuples/                    # (Phase 1a, in progress)
│   │   │   └── NNN-{kind-slug}-{discriminator}.json
│   │   └── expected_outcomes.json     # (Phase 1a, in progress)
│   ├── rq_framing_patterns/           # #257 Socratic wording advisory calibration
│   ├── status_classification/         # Phase 2 (lands post-#183)
│   └── summarization_adequacy/        # Phase 2 (lands post-#183)
```

## Authoring conventions

See each task's `README.md` for task-specific conventions (tuple naming, kind distributions, expected outcomes shape).

## Validator

Run `python -m scripts.check_evals_gold_set evals/gold/<task>` to validate any gold set against its manifest. The same validator runs in CI on every PR that touches `evals/gold/**`.

## Provenance

- Phase 1a (citation-extraction): v3.10 #184, spec `docs/design/2026-05-21-v3.10-184-extend-eval-harness-spec.md`
- RQ framing patterns: Kong #257 idea-diversity advisory, spec `docs/design/2026-05-28-kong-257-idea-diversity-coverage-gap-advisory.md`
- Phase 2 (status + summarization): scheduled post-#183 ship
