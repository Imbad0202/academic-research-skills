# Two-Stage Review Protocol (Added in v2.0)

## Stage 3: First Review (Full Review)

- **Input**: Paper that passed integrity check
- **Review team**: EIC + R1 (methodology) + R2 (domain) + R3 (interdisciplinary) + Devil's Advocate
- **Output**: 5 review reports + Editorial Decision + Revision Roadmap + Socratic Revision Coaching
- **Decision branches**: Accept -> Stage 4.5 / Minor|Major -> Revision Coaching -> Stage 4 / Reject -> Stage 2 or end

See `academic-paper-reviewer/SKILL.md` for review process details.

## Stage 3 -> 4 Transition: Revision Coaching

EIC uses Socratic dialogue to guide the user in understanding review comments and planning revision strategy (max 8 rounds). User can say "just fix it for me" to skip.

## Stage 3': Second Review (Verification Review)

- **Input**: Revised draft + Response to Reviewers + original Revision Roadmap + Editorial Decision Letter (#539 — its Review Panel Provenance block feeds the Judge Record) + apply report(s) (#390) + Round-1 Reviewer Configuration Cards (yardstick continuity — field_analyst NOT re-run; `academic-paper-reviewer/references/re_review_mode_protocol.md` § Yardstick Continuity). This input set describes re-review mode, the default Stage 3'; a user-requested fresh full review at 3' instead (mid-entry quick→full path) takes the revised draft + available context only and runs full mode, field_analyst included
- **Mode**: `academic-paper-reviewer` re-review mode (default); the user-requested fresh full review at 3' dispatches full mode instead
- **Output**: re-review mode — Revision response comparison table + new issues list + new Editorial Decision + R&R Traceability Matrix (Schema 11); fresh full review — the normal full-review package (5 review reports + Editorial Decision + Revision Roadmap), no R&R matrix
- **Decision branches**: Accept|Minor -> Stage 4.5 / Major -> Residual Coaching -> Stage 4'

See `academic-paper-reviewer/SKILL.md` Re-Review Mode for verification review process.

## Stage 3' -> 4' Transition: Residual Coaching

EIC guides the user in understanding residual issues and making trade-offs (max 5 rounds). User can say "just fix it" to skip.
