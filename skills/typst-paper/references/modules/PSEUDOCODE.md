# Module: Pseudocode Review

**Trigger**: Typst algorithm, algorithmic, algorithm-figure, lovelace, 伪代码块, 算法流程排版

## Commands

```bash
uv run python -B scripts/check_pseudocode.py main.typ --venue ieee
uv run python -B scripts/check_pseudocode.py main.typ --venue ieee --json
```

## IEEE-safe defaults

- Prefer the Typst `algorithmic` package for IEEE-like pseudocode output because it gives a figure wrapper, caption handling, line numbering, and conventional control-flow rendering.
- Prefer `algorithm-figure(...)` for IEEE-like output.
- Treat `lovelace` as a flexible fallback for custom syntax, not the default recommendation.
- If `lovelace` is used for an IEEE-like submission, wrap the output in `#figure(...)` and give it a caption.
- Line numbers are recommended for review convenience, but not treated as a hard IEEE requirement.
- Keep comments short and move paragraph-level explanation into the surrounding prose.

## What this module checks

- missing `algorithm-figure(...)` or missing figure wrapper in IEEE-like contexts
- missing `style-algorithm`
- missing caption
- missing line numbers (advisory only)
- long comment lines
- prose-length algorithm lines that should live in the main text

## Output policy

- Report hard IEEE-like layout risks first.
- Separate `mandatory` from `recommended`.
- Keep Typst labels, references, and math intact unless the user explicitly asks for source edits.
