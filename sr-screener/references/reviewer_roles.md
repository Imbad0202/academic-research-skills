# Reviewer roles: Reviewers A and B, the Adjudicator and the QC reviewer (Phases 2-5)

These roles run as subagents (the lean `screening_reviewer_agent`, `agents/screening_reviewer_agent.md`)
with the prompts in `templates/prompts.md`. That file is the single source of the reviewer
wording; `scripts/build_workflow.py` fills it in and embeds the confirmed protocol verbatim. This
reference explains, for the orchestrating session, what each role sees and why, and how the main
session applies the same rules itself in `quick` mode.

## Who sees what

| Role | Sees | Does not see | Default model |
|------|------|--------------|---------------|
| Reviewer A (content expert) | protocol, decision rules, one batch file | B's decisions, other batches | sonnet |
| Reviewer B (methodologist) | protocol, decision rules, one batch file | A's decisions, other batches | sonnet |
| Adjudicator | protocol, rules, the disputed records, both labels | the reviewers' reasons | sonnet |
| QC reviewer | protocol, rules, selected excluded records | earlier labels and reasons | sonnet |

Why the adjudicator gets labels but not reasons: labels tell it what is disputed; reasons would
invite it to pick the more persuasive reviewer instead of reading the record. The QC reviewer
gets neither, so it screens afresh.

The two personas are deliberate. A content expert notices what the record is about; a
methodologist notices what kind of study it is. Two lenses make the decisions more independent
than two copies of one prompt.

## Decision procedure (apply in this order)

1. Read the header line: publication type, year and language settle many exclusions quickly.
2. Check the exclusion codes in the protocol's order; the first one that clearly fails is the code.
3. If nothing clearly fails, check whether every title/abstract-assessable criterion is clearly
   met: `include`.
4. Otherwise, if the core criteria are plausibly met: `unclear`. If a core criterion clearly
   fails, go back to step 2: that is an exclusion.
5. Write `why` as the deciding fact in at most 15 words. Synthetic examples: "Piglet model only",
   "Plasma NGAL only, no urinary NGAL", "Narrative review", "Urinary NGAL after paediatric cardiac surgery".

Good reasons name a fact from the record. Poor reasons restate the label ("Not relevant",
"Does not meet criteria") or guess ("Probably no comparison group").

## Traps and full-text rules

The traps reviewers most often fall into (specimen confusion, human samples in vitro, reviews
that look like studies, subgroups, conference abstracts, records without an abstract) and the
full-text rules are in `agents/screening_reviewer_agent.md`, the file the reviewer subagents
load. Apply them in `quick` mode too.

## Quick mode (main session, no subagents)

For a handful of records the main session applies the procedure itself:

```markdown
| ID / title (short) | Decision | Code | Deciding fact | What would change it |
|--------------------|----------|------|---------------|----------------------|
| Smith 2021, NGAL after PCS | include | INC | Children, urinary NGAL, AKI by KDIGO | - |
| Lee 2019, rat IRI model | exclude | E2 | Rat model only | - |
| Chen 2023, "biomarkers" in CHD | unclear | UNC | Paediatric cardiac surgery; markers not named | Names urinary NGAL in methods |
```

Say plainly that this is a single-reviewer triage: one model reading twice is not two
independent reviewers, so a person has to act as the second reviewer.
