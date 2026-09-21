# Chinese citation-check boundary cases (#882)

Companion to `plugin-evals-citation-check`. All papers and people in these
inputs are fictional. This suite checks the scope of the abbreviation and
ordering repair, rather than changing the original case-02 acceptance rules.

```bash
claude plugin eval . --eval-dir plugin-evals-citation-locale --ablation none --model sonnet --judge-model opus --runs 1 --no-publish
```

| Case | Required behavior |
|---|---|
| 09 — stroke inversion and two authors | Report a genuine out-of-order Chinese list using the supplied surname stroke counts; preserve both names in a two-author citation. |
| 10 — same-year disambiguation | Preserve all names when two three-author works differ only at the final author; do not shorten the reference-list entries. |
| 11 — venue romanization override | Accept the supplied alphabetical romanized order despite its differing from stroke order. |

The original mixed-overclaim case remains in the main citation suite and is
repeated three times for the two reported defects. Its existing quality
rubrics are unchanged. Additional `tool_used` graders record attempted reads
of the agent and Chinese guide; successful loading is checked in the traces.
Loading metrics are distinct from the output-quality judgements. These small
synthetic tests do not establish universal accuracy or a with/without uplift.

The supplied stroke counts in case 09 isolate applying the ordering rule from
looking up character data. They do not test a general-purpose stroke-count
lookup implementation. No such implementation is added by this prompt fix.

## Verification (2026-09-21)

On the final #882 candidate, Claude Code 2.1.278 with `--ablation none
--model sonnet --judge-model opus --runs 1 --no-publish` passed all three
cases and all their graders (3/3). The observed agent was `claude-sonnet-5`.
Case 09 uses different personal names from the operative guide examples.
The result covers these three supplied-input boundaries; it does not certify
all Chinese ordering/author-name cases.
