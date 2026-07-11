# Wording-Pattern Advisory — held-out miss-rate measurement (issue #501 Part 2)

**Date:** 2026-07-11
**Scope:** the runtime LLM judge of the `## Wording-Pattern Advisory` section in
`deep-research/agents/socratic_mentor_agent.md` (the `academic-paper` twin differs
only in scenario prose; substance identical, verified by diff).
**Deliverables:** `evals/heldout/rq_framing_offlist/` (set + measurement JSON + protocol README), this report.
**Provenance chain:** PR #468 review thread (@brycewang-stanford) → issue #501 → PR #503 (Part 1 prompt edit) → this measurement (Part 2).

## Question

Issue #501: does the runtime judge miss real AI-typical RQ phrasings that sit
outside the twenty WP01–WP20 surface forms? If the miss rate is low, close with no
further action; if high, the held-out set becomes the acceptance test for any
future change.

## Method (summary — full protocol in the set's README)

- 48-item held-out set: 32 shells (23 family-variant, 9 off-list) + 16 domain-native
  hard negatives. Generated cross-model (`gpt-5.6-sol` via Codex CLI 0.144.1),
  filtered against the shipped regex detector and the four in-prompt examples,
  dual-annotated (generator + maintainer; 8 borderline/disagreement items dropped),
  elicited-rewrite labels inherited by construction under a no-new-specifics
  constraint. English-only per the #468 language/model-drift caveat.
- Judge: isolated `claude-sonnet-5` sub-agents, given only the verbatim advisory
  section (variant under test) + 6 shuffled items each, no labels, no repo access.
- Variants: pre-#503 (table + trigger rule) single run; post-#503 (adds the
  illustrative/noun-swap paragraph) two replicates.
- Acceptance line inherited from `evals/gold/rq_framing_patterns/manifest.yaml`:
  FNR < 0.30, FPR < 0.20.

## Results

| variant | overall miss | family_variant (n=23) | off_list (n=9) | false-fire (n=16) |
|---------|-------------|----------------------|----------------|-------------------|
| pre-#503 | 12/32 = 0.375 | 6/23 = 0.261 | 6/9 = 0.667 | 0/16 = 0.000 |
| post-#503 rep1 | 12/32 = 0.375 | 5/23 = 0.217 | 7/9 = 0.778 | 0/16 = 0.000 |
| post-#503 rep2 | 11/32 = 0.344 | 4/23 = 0.174 | 7/9 = 0.778 | 0/16 = 0.000 |

Replicate stability: the two post-#503 runs disagree on exactly one item
(`nat-049`); the seven off-list misses are identical across both replicates
(`nat-044`, `ti-002`, `ti-004`, `ti-008`, `ti-010`, `ti-012`, `ti-013`).

## Findings

1. **Verdict: miss rate HIGH.** Overall FNR 0.34–0.38 sits above the 0.30
   acceptance line in all three runs. Per issue #501's decision rule, the held-out
   set becomes the acceptance test for any future advisory change.
2. **The gap is one specific shape, not diffuse.** Family-variant generalization
   (interrogative/synonym rewordings of listed families — "How does X affect Y",
   "What shapes X among Y") is under the line post-#503 (0.17–0.22). What the judge
   stably misses is the **decorated compound-title shell**: an evocative pre-colon
   phrase plus a generic "X and Y (in Z)" subtitle ("The Weight of Care: Nurse
   Workload and the Quality of Patient Care"). 7 of 9 off-list items, missed in
   both replicates.
3. **Failure mechanism is the exemption clause, not the table.** Judge reasoning
   (captured per batch) shows the misses are argued as "names a specific
   mechanism/population", applied to generic topical noun pairs like "cybersecurity
   training → behavior". The exemption ("names a specific mechanism, instrument,
   site, or tension") is being read broadly enough to exempt decorated shells whose
   nouns are ordinary topic labels, not named instruments/sites. Any future fix
   should sharpen the exemption (e.g., a named instrument/scale/site test) rather
   than extend the pattern table.
4. **Zero over-warning, both variants.** 0/16 false-fires on hard negatives that
   deliberately contain shell-adjacent verbs ("mediate", "affect") inside fully
   specified designs. The conservative high-confidence bar errs entirely toward
   silence — consistent with the advisory's non-blocking design intent.
5. **The #503 Part 1 paragraph helped where it aimed.** Family-variant misses
   dropped (0.261 → 0.174–0.217) and one in-prompt-example generalization
   (`ti-001` "Rethinking …") flipped to caught. It did not touch the decorated-title
   shape, which none of its four examples resemble.
6. **Corpus observation.** Of 80 naturally-generated AI RQs, 12 matched WP surface
   forms literally and ~60 more were family variants; genuinely off-list shells in
   natural output were rare (1). Off-list shells concentrate in the *polish* flows
   ("make it less cliché", "give me a catchy title") — which is also the realistic
   user path that produces them.

## Caveats

- Single judge model (`claude-sonnet-5`), single generator model (`gpt-5.6-sol`),
  English-only, 2026-07 snapshot. Both AI-typical phrasing and judge behavior are
  model- and time-specific (PR #468 discussion); re-run the protocol rather than
  reusing numbers.
- n=9 off-list items is small; the 7/9 stable-miss signal is directional but the
  tier rate carries wide uncertainty. The decorated-title failure shape, however,
  is consistent with the captured judge reasoning, not just the counts.
- Ground truth is two-model consensus plus construction-inheritance, documented
  drops included; borderline items were removed rather than adjudicated.

## Disposition

- Issue #501 closes: Part 1 shipped (PR #503), Part 2 measured (this report), and
  the high-miss branch's deliverable — the acceptance test — is committed.
- The measured off-list gap is tracked as a follow-up design issue (sharpen the
  exemption clause; evaluate any change against this set at FNR < 0.30 / FPR < 0.20
  with ≥2 replicates, plus the existing on-list gold set for non-regression).
