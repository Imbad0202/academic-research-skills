# Pipeline Behavior Robustness Set (metamorphic pairs vs the runtime routing/gate layer)

Issue: #550. External motivation: Ren et al. (2026, arXiv:2607.13104 §8.2.1) — prompt-policy
changes should be evaluated under paraphrases, formatting shifts, and longer contexts to
measure genuine robustness rather than repeated optimization on a single template; §7.1
warns about overfitting fixed verifiers.

This directory holds **metamorphic paired cases** for the main-session LLM applying the
repo's routing and gate rules (`.claude/CLAUDE.md` § Routing Discipline + § Routing Rules,
`POSITIONING.md` § Rejected mechanisms, and the Stage 2.5/4.5 IRON RULE surfaces). It lives
under `evals/heldout/` — not `evals/gold/` — for the same reason as `rq_framing_offlist/`:
the measured judge is an LLM, not a script; there is no `target.entrypoint`,
`scripts/run_evals.py` must not discover it, and pass/fail is asserted by comparing observed
behavior against the documented expectation, not by a shipped reducer.

## Design

Each **base scenario** (`b-*`) states a user request whose correct handling is *documented*
(routing destination, clarify-first obligation, refusal, or gate hold). Each base has
**perturbed variants** — v0.1 ships three axes per base: `b-*-t` terse, `b-*-v` verbose,
`b-*-p` padding (the same request preceded or followed by irrelevant but plausible material
per the JSON's `padding_protocol`); `wrapper` (content inside Markdown quoting / XML-ish
tags / chat-forward framing) and `reorder` (same constraints, different order) are reserved
enum values for v0.2. The **invariant** is per-pair: the perturbed variant must produce the
same `expected.behavior` as its base. Language is held constant within a pair
(the set carries both en and zh-TW pairs; language itself is not a perturbation axis).

Ground truth here is **reproducible from the shipped documents** (unlike the
`rq_framing_offlist` noun-swap labels): every `expected.behavior` cites the rule that
mandates it. A change to those rules invalidates the affected items — update the item's
`rule_anchor` in the same PR, or drop it with a note in this README.

## Metrics

- **Paired consistency rate**: fraction of (base, variant) pairs whose observed behavior
  matches — for `route_direct` items this means behavior AND the structured
  `expected.skill` + `expected.mode` fields, so a variant that routes *somewhere* different
  from its base never scores as consistent. Primary metric; report per perturbation axis.
- **Long-context degradation**: absolute correctness of the `-p` variants MINUS absolute
  correctness of their bases (a signed delta; 0 = no degradation). Distinct from the
  paired-consistency metric, which cannot distinguish "both wrong the same way" from
  "both right".
- **Absolute correctness**: fraction of ALL items (bases included) matching the full
  expectation (`behavior` + `skill`/`mode` when present). Secondary — a base that itself
  misroutes is a routing bug, not a robustness finding, and files as its own issue.

## Running a measurement

Mirror the `rq_framing_offlist` measurement protocol: fresh session per item (no
cross-item contamination), the item's `prompt_text` as the first user message, record the
session's first substantive action (skill routed — including WHICH skill and mode — /
clarification asked / refusal issued / gate decision), then judge match against the FULL
expectation mechanically: `expected.behavior` plus `expected.skill` and `expected.mode`
when present. Store results as
`measurement-YYYY-MM-DD.json` beside this README (same convention as the #505 runs).
Fresh-session isolation matters: routing state (e.g., an earlier explicit skill choice)
legitimately changes later routing inside one session.

## Status

`set_version: 0.1.0` — seed set: 8 base scenarios × 3 perturbations each (32 items).
Expansion protocol: new bases must anchor to a documented rule (`rule_anchor`); new
perturbation axes extend the axis enum here first. Cross-model authoring of additional
surface variants (the `rq_framing_offlist` construction discipline) is the intended v0.2
step before this set is used as an acceptance test for routing-layer changes.
