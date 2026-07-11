# RQ Framing Held-Out Set (off-list shells vs the runtime LLM judge)

Issue: #501 Part 2. Direction from the PR #468 review thread (@brycewang-stanford).

This directory holds the **held-out measurement set** for the Socratic wording-pattern
advisory's **runtime judge** — the LLM applying the `## Wording-Pattern Advisory`
section of the two `socratic_mentor_agent.md` files. It is deliberately **outside**
`evals/gold/` because the judge is an LLM, not a script: it has no `target.entrypoint`,
`scripts/run_evals.py` must not discover it, and its ground-truth labels are not
reproducible by a shipped reducer (the `check_evals_gold_set` I9b invariant cannot
apply). The offline regex detector's calibration set lives at
`evals/gold/rq_framing_patterns/` and is a different measurement target.

## What "held-out" means here

Every `shell` item avoids (a) the twenty WP01–WP20 surface forms and (b) the four
off-list examples quoted inside the post-#503 advisory paragraph ("unpacking the
dynamics of…", "a deep dive into…", "rethinking X in the age of Y", "interrogating
the nexus between…") — those four are in the judge's prompt and are no longer
held out. The shipped regex detector (`scripts.check_rq_framing_patterns`) fires on
none of the 48 items; the 12 generated items it did fire on were excluded as on-list.

## Construction (2026-07-11)

1. **Natural generation.** Codex CLI 0.144.1 (`gpt-5.6-sol`) generated 80 research
   questions "the way you would naturally propose them to a graduate student",
   across ten fields, plus 20 specialist-style domain-native RQs. Cross-model
   generation avoids the judge's own model family authoring its test items.
2. **On-list filter.** The shipped regex detector removed 12 literal-surface-form
   matches. The remaining 68 are held out of the *listed surface forms* by
   construction.
3. **Dual annotation.** The 88 candidates were annotated independently by the
   generator model (noun-swap rubric verbatim) and by the maintainer-side reviewer.
   Seven disagreement/borderline items were dropped (`nat-041/050/052/055/056`
   name mechanisms or engineering artifacts; `nat-064/067` split between annotators).
   Only agreed labels shipped.
4. **Elicited rewrites (label by construction).** Two realistic de-cliché flows —
   "rewrite so it sounds less AI-cliché" (`el-*`) and "give my paper a catchy,
   ambitious title" (`ti-*`) — were run on agreed-shell sources with an explicit
   no-new-specifics constraint, so shell labels inherit from the sources; each
   rewrite was manually verified to add no mechanism/instrument/site. One borderline
   (`ti-005`, brushes the "concrete theoretical tension" exemption) was dropped.
   These flows are how off-list shells arise in the wild: users asking an AI to
   polish an already-shell phrasing.
5. **Final set.** 32 shells (23 `family_variant` + 9 `off_list`) + 16 domain-native
   hard negatives = 48 items. `tier` is descriptive metadata; `label` is ground truth.

## Measurement protocol (re-run this for any future advisory change)

- Judge = an isolated LLM agent given ONLY the verbatim `## Wording-Pattern Advisory`
  section (the variant under test) + a batch of 6 items (4 shells + 2 negatives,
  shuffled), instructed to decide fire/silent per item independently. No repo access,
  no labels, no other context.
- 8 batches cover the 48 items once; run ≥2 replicates for the decision-relevant
  variant (single-run flips of 1–2 borderline items were observed).
- Metrics: miss rate (shells not fired on) overall and per tier; false-fire rate
  (negatives fired on). Acceptance line inherited from
  `evals/gold/rq_framing_patterns/manifest.yaml`: FNR < 0.30, FPR < 0.20.

## 2026-07-11 baseline result (see `measurement-2026-07-11.json`)

| variant | overall miss | family_variant | off_list | false-fire |
|---------|-------------|----------------|----------|------------|
| pre-#503 (single run) | 0.375 | 0.261 | 0.667 | 0.000 |
| post-#503 rep1 | 0.375 | 0.217 | 0.778 | 0.000 |
| post-#503 rep2 | 0.344 | 0.174 | 0.778 | 0.000 |

**Verdict: miss rate HIGH** (overall ≥ the 0.30 line). The gap is concentrated in
`off_list` decorated compound-title shells — the same 7 of 9 missed in both post
replicates — where judges read generic topical nouns ("cybersecurity training",
"nurse workload") as the exemption's "specific mechanism". Family-variant
generalization is under the line (0.17–0.26), and false-fire is zero on both
variants: the conservative bar over-exempts rather than over-warns. Per issue
#501, this set is therefore the acceptance test for any future advisory change.
Judge model: `claude-sonnet-5`; both the set (English-only, one generator model)
and the judgments are model- and time-specific and drift across versions — re-run
rather than reuse the numbers.

Full write-up: `audits/rq-advisory-heldout-measurement-2026-07-11.md`.
