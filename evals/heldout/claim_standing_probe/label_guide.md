# Claim-Standing Stance Label Guide (v0.1)

Authority for the closed vocabulary: `docs/design/2026-08-13-655-search-bounded-claim-standing-probe-design.md` §5.1. This guide operationalizes those rules for human expert labelers. Every label cites one criterion id below (`label_guide_criterion`).

## What you receive, and what you must not see

You receive, per item: one claim, one candidate record (title, venue, year, coverage flag, and the evidence text when available), and this guide. You must not see, and must not seek: the set's construction intent, any other expert's labels, any model output, or any expectation about performance. If you have seen any of those for an item, do not label that item; report it.

## Labeling procedure per item

1. **Relevance first (`REL`).** Is this candidate's work family topically capable of bearing on the claim? `relevant` / `not_relevant`. Relevance is about the work, not about which way it points. If `not_relevant`: stop; record `check_state: not_checked`, `stance: null`, `failure_state: null`.
2. **Checkability (`CHK`).** If no evidence text is available (missing abstract, metadata only), record `check_state: not_checked`, `stance: null`, `failure_state: abstract_missing` (or `source_missing` if the record itself is defective). Never map missing evidence to `not_addressed`.
3. **Stance (`ST-*`)**, only when `check_state: performed`. The unit is this one candidate's evidence text against this one exact claim:
   - `ST-SUP` → `support`: the evidence makes a claim in the same direction as the tested claim, at face value.
   - `ST-CON` → `contradict`: the evidence makes a claim in the opposite direction, or reports a well-powered null against an asserted effect.
   - `ST-MIX` → `mixed`: the evidence explicitly states both directions (different subgroups, conditions, dosages), each direction explicit in the text.
   - `ST-NA` → `not_addressed`: the evidence was inspected, is relevant, and makes no claim about the proposition. This means "this text is silent on it", never "the literature is silent".
   - `ST-IE` → `INSUFFICIENT_EVIDENCE`: the text touches the proposition but gives too little information to assign a direction (protocols, descriptive-only reports, results-pending statements).
   - `ST-AMB` → `AMBIGUOUS`: the text permits incompatible readings of the direction, or a population/condition difference prevents resolving direction and both directions are not explicit (if both are explicit, use `mixed`).
4. **Evidence scope (`SCOPE`).** Record what you actually judged from: `abstract`, `session_held_full_text`, or `metadata_only`. Do not claim full-text adjudication from an abstract.
5. **Rationale.** 1–4 sentences quoting or pointing at the decisive phrasing. No numeric confidence, probability, or score of any kind — a labeled scalar would be discarded and the file rejected.

## Boundary reminders

- `support`/`contradict` describe the relation of the inspected text to the claim. They do not certify quality, reproduce analyses, or establish truth.
- Direction changes driven by population, intervention, comparator, outcome, timing, or condition differences: `mixed` when both directions are explicit, otherwise `AMBIGUOUS` (criterion `ST-MIX`/`ST-AMB` note).
- Label independently. Disagreements are resolved later by a separate adjudicator; do not discuss items with the other expert before your file is sealed.

## Record format

One file per expert, validating against `expert_label.schema.json`, one row per item, `label_guide_criterion` ∈ {REL, CHK, ST-SUP, ST-CON, ST-MIX, ST-NA, ST-IE, ST-AMB, SCOPE}.
