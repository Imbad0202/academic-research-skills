<!-- Thanks for contributing to academic-research-skills. -->

## Summary

<!-- What does this PR change and why? -->

## Eval impact

The eval harness (`.github/workflows/eval-harness.yml`) runs automatically on PRs
that touch scoring / generation logic or the gold sets (see the Delta 3 path
filter in that workflow). Most PRs do not affect eval metrics — leave this
section as "No eval impact." if that applies.

If your change **alters ranking / scoring / generation behavior** and moves a
gold-set metric:

1. Declare each affected metric, one per line, in the exact form:

   ```
   Affected metric: <task>.<class>.<metric>
   ```

   e.g. `Affected metric: citation_extraction.aggregate.accuracy`
   (use class `aggregate` for the headline metric; otherwise the per-class name).

2. If a metric **regresses** (polarity-corrected `signed_lift < -0.05`, or any
   zero-baseline metric changes), the gate blocks unless you add BOTH:

   - the acknowledgement token (on its own line):
     - `[eval-regression-acknowledged]` — for the CI deterministic gate, and/or
     - `[ranking-regression-acknowledged]` — for `scripts/check_ranking_lift.py`
   - a link to an **OPEN** follow-up GitHub issue, e.g.
     `https://github.com/Imbad0202/academic-research-skills/issues/NNN`

> No eval impact.

## Checklist

- [ ] Tests added / updated and passing locally
- [ ] Eval impact section above is accurate
