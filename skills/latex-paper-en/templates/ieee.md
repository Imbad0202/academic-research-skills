# IEEE Conferences/Journals (LaTeX)

> Venue-specific snapshot extracted from `references/VENUES.md`. Load this
> file directly when the user names IEEE as the target venue, instead of
> reading the full venue catalog.

## Style

- Active voice for contributions
- Past tense for methods
- Present tense for results discussion

## Format

- Two-column layout
- Abstract: 150-200 words
- Keywords: 3-5 terms

## Citations

- IEEE style: [1], [2-4]
- Full reference in bibliography

## Figures/Tables

- Captions below figures
- Captions above tables
- Referenced in text before appearing

## Pseudocode

- IEEEtran only recognizes `figure` and `table` as standard floats; do not assume a dedicated `algorithm` float is IEEE-safe.
- Prefer `figure` + `algorithmicx` / `algpseudocodex` for LaTeX pseudocode in IEEE submissions.
- Give the pseudocode block a normal figure caption and reference it in text before the figure appears.
- Prefer direct captions such as `Adaptive inference procedure` instead of `The proposed algorithm...`.
- Explicit input/output markers and short inline comments are recommended defaults, not IEEE hard requirements.
