# AI Tone Terms (English) — Reference

This document lists the English vocabulary patterns most associated with
AI-generated academic prose, with a recommended per-document occurrence
budget. The companion file `AI_TONE_THRESHOLDS.yaml` is the authoritative
source consumed by `deai_check.py`.

## How thresholds are enforced

- `deai_check.py` reads `AI_TONE_THRESHOLDS.yaml` at startup.
- Each word in `term_thresholds:` triggers a `[Script] LOW` trace once its
  per-document count exceeds the listed value.
- Counts are case-insensitive and word-boundary matched against visible prose
  (citations, refs, math, comments are stripped first).
- Override by editing the YAML; this MD file is documentation only.

## High-frequency AI vocabulary

These words are not banned. They are useful when used sparingly. The
threshold is the point at which a reviewer is likely to flag the writing
as templated.

| Word          | Threshold | Why it matters                                                  |
|---------------|-----------|------------------------------------------------------------------|
| significant   | 5         | Often hides missing effect size or p-value                       |
| comprehensive | 3         | Marketing language; rarely earned by a single study              |
| effective     | 5         | Cheap claim without baseline comparison                          |
| novel         | 4         | Reviewers discount the word unless the novelty is named          |
| robust        | 4         | Needs the perturbation / noise level that justifies the claim    |
| important     | 5         | Replace with what is at stake                                    |
| various       | 5         | Vague quantifier; usually fixable with a number                  |
| several       | 5         | Vague quantifier                                                 |
| numerous      | 3         | Vague quantifier; almost always replaceable with a count         |
| furthermore   | 3         | Padding connector; often signals a content-free addition         |
| moreover      | 3         | Padding connector                                                |
| notably       | 3         | "Notably" is rarely needed when the content is genuinely notable |
| remarkable    | 3         | Editorial language; let the data carry the claim                 |
| remarkably    | 3         | Same as above                                                    |
| obvious       | 3         | Over-confident hedge                                             |
| obviously     | 3         | Over-confident hedge                                             |
| clearly       | 4         | Over-confident hedge                                             |

## Burstiness (paragraph opening repetition)

When three or more consecutive paragraphs begin with the same two opening
tokens, the script emits a `burstiness` trace. Typical offenders:

- "We propose ..." / "We propose ..." / "We propose ..."
- "In this ..." / "In this ..." / "In this ..."
- "Furthermore, ..." / "Furthermore, ..." / "Furthermore, ..."

The remedy is to rewrite at least one opener with a different syntactic
shape (subordinate clause, prepositional phrase, contrastive connector).

## Throat-clearing phrases

Phrases that occupy the first sentence of a paragraph without delivering
information. The default pattern set covers:

- `In order to better ...`
- `In this section, we ...`
- `It is worth noting that ...`
- `It should be noted that ...`
- `As mentioned earlier ...`
- Leading discourse markers: `Notably,`, `Furthermore,`, `Moreover,`, `In summary,`, `To summarize,`

Each trigger is a single `[Script] LOW` trace pointing at the offending line.

## Punctuation patterns

- More than `max_em_dashes_per_doc` em-dashes (`---` or `—`) across the
  document → one aggregate trace at the first occurrence.
- Any `!` in body sections (abstract through conclusion) → one trace per
  occurrence. Inline code, math, and comments are excluded.

## Out of scope

The following are intentionally NOT enforced here:
- Sentence-level grammar (handled by `analyze_grammar.py`).
- Citation density (handled by `verify_bib.py`).
- Section structure (handled by `check_format.py`).
- Domain-specific terminology, which lives in `FORBIDDEN_TERMS.md`.
