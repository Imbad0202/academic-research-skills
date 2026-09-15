# `output_language_pair` fixtures (#862 Phase 1)

Deterministic fixtures for the per-run output-language-pair contract
(`shared/output_language_pair.md`). Unlike `tests/fixtures/issue_133_routing/` (a
behavioral smoke corpus with no CI consumer), this corpus **is** consumed in CI:
`scripts/test_output_language_pair.py::OutputLanguagePairFixtureTest` loads every
directory, parses the fenced `yaml` block(s) of `input.md`, runs the parsed value through
`check_spec_consistency.validate_output_language_pair`, and grades the outcome against
`expected.yaml`.

## Cases

| Directory | Field value | Expected outcome |
|---|---|---|
| `omitted/` | key absent | valid — today's default pair (`zh-tw-en`) |
| `default/` | `zh-tw-en` | valid — the default registry entry |
| `unsupported/` | `ja-en` | visible failure naming the registry |
| `malformed/` | `null`, then `[zh-tw-en]` | visible failure naming the registry |

## Surface covered

The fixtures pin the **contract helpers and the field value**, not a live model run. The
heading literals (`### English Abstract`, `### Chinese Abstract`, `## English Abstract`,
`## Chinese Abstract (zh-TW)`) and the legacy object keys (`abstract: {english, chinese}`,
`keywords: {en, zh_tw}`) are pinned on the real consumer surfaces by
`check_spec_consistency.py` and `scripts/test_check_spec_consistency.py`. No repo.md
pass-rate, rendered-output, or model-behaviour claim is made from this corpus.

## Adding a case

1. Add a directory with `input.md` (prose + one fenced `yaml` block per case) and
   `expected.yaml` (`cases:` list, one entry per block, in the same order).
2. Run `python3 -m unittest scripts.test_output_language_pair -v`.
