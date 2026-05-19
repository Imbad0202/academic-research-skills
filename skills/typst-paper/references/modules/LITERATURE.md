# Module: Literature Review Synthesis

Purpose: review the Related Work section as an analytical conversation, not a citation list.

```bash
uv run python -B scripts/analyze_literature.py main.typ --section related
```

## Core Checks

- **A1: Enumeration** — repeated author/year listing instead of theme clustering.
- **A2: Comparative synthesis** — missing sentences on trade-offs, differences, or shared limitations.
- **A3: Gap derivation** — no literature-backed unresolved limitation near the end of the section.

## Recommended Rewrite Chain

`Consensus -> Disagreement -> Limitations -> Gap -> This paper`

Use the chain above when proposing edits:

1. summarize what multiple papers agree on
2. surface one disagreement or trade-off
3. isolate the remaining limitation
4. turn that limitation into an evidence-backed gap
5. connect the gap to the present paper

## Boundaries

- Keep `@cite`, `<label>`, and math intact unless the user explicitly asks for source edits.
- Do not force a gap when the cited evidence is too thin or contradictory.
- Prefer diagnosis + rewrite blueprint before generating new prose.
