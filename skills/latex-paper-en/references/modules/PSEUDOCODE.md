# Module: Pseudocode Review

**Trigger**: pseudocode, 伪代码, algorithm block, algorithmicx, algpseudocodex, algorithm2e, Algorithm 1, Require/Ensure

## Commands

```bash
uv run python -B scripts/check_pseudocode.py main.tex --venue ieee
uv run python -B scripts/check_pseudocode.py main.tex --venue ieee --json
```

## IEEE-safe defaults

- Treat IEEE pseudocode as a figure-like object, not as a dedicated floating `algorithm` environment.
- Prefer `figure` + `algorithmicx` / `algpseudocodex` for IEEE submissions.
- Do not default to `algorithm.sty` / `algorithm2e` floating environments for IEEE papers.
- Use direct captions rather than article-led captions such as `The proposed algorithm...`.
- Prefer explicit input/output markers such as `\Require` and `\Ensure`.
- Keep inline comments short. Move long explanation back into the main text, or use `\LComment` when a longer side note is unavoidable.
- Line numbers are recommended for review convenience, but they are not treated as a hard IEEE requirement.

## What this module checks

- IEEE hard violation: floating `algorithm` / `algorithm2e` usage
- missing figure caption or label around pseudocode
- first textual reference appearing after the pseudocode figure
- captions that start with `A`, `An`, or `The`
- missing explicit input/output markers
- long inline comments or prose-length algorithm steps
- line numbers missing (advisory only)

## Output policy

- Report hard constraints separately from recommendations.
- Do not rewrite the pseudocode block automatically unless the user explicitly asks for source edits.
- When recommending a fix, explain whether it is:
  - IEEE hard constraint
  - IEEE-safe default
  - readability recommendation
