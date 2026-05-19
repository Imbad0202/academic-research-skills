# NOTICE

This repository is a **merged fork** that combines two upstream projects. The two upstreams use **different licenses** — this notice documents which skills came from where, and which license applies to which file tree.

## Upstreams

### 1. Academic Research Skills (ARS) — primary upstream

- **Repo:** [Imbad0202/academic-research-skills](https://github.com/Imbad0202/academic-research-skills)
- **License:** [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/)
- **Author:** Cheng-I Wu (`@Imbad0202`)
- **Covers:** Everything in this repo **except** the five skills listed below — that is, the four ARS pipeline skills (`deep-research`, `academic-paper`, `academic-paper-reviewer`, `academic-pipeline`), all `shared/`, `agents/`, `commands/`, `hooks/`, `scripts/`, `docs/`, `examples/`, and the original `README.md` / `POSITIONING.md` / `MODE_REGISTRY.md`.
- **The CC BY-NC 4.0 license file** (`LICENSE`) at the repo root continues to govern this portion of the tree.

### 2. Academic Writing Skills (AWS) — merged in

- **Repo:** [bahayonghang/academic-writing-skills](https://github.com/bahayonghang/academic-writing-skills)
- **License:** MIT (declared in `pyproject.toml`: `License :: OSI Approved :: MIT License`)
- **Author:** bahayonghang
- **Covers:** Only the **five subdirectories** under `skills/` that were merged in (see list below).

## Skills merged from AWS (MIT-licensed)

Each of the following directories was copied verbatim from `bahayonghang/academic-writing-skills/academic-writing-skills/<skill-name>/` and remains under MIT:

| Path in this repo | Purpose |
|---|---|
| `skills/latex-paper-en/` | English LaTeX paper polish (IEEE / ACM / NeurIPS / ICML / Springer) |
| `skills/latex-thesis-zh/` | Chinese degree thesis polish (GB/T 7714-2015, thuthesis / pkuthss / ustcthesis / fduthesis) |
| `skills/typst-paper/` | Bilingual Typst paper polish |
| `skills/bib-search-citation/` | Local BibTeX / BibLaTeX library search |
| `skills/aiwei-zh/` | Chinese AI-tone detection and removal (Huangfu Boyuan 2026 six-dimension framework + typographic hard gates) |

### MIT License text (applies to the five subdirectories above)

```
MIT License

Copyright (c) bahayonghang (academic-writing-skills contributors)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

> **Note:** The upstream AWS repo declares MIT only in `pyproject.toml`; it does not ship a `LICENSE` file at the repo root. The text above is the standard MIT license boilerplate as applied to that project. For the canonical declaration, see [`pyproject.toml`](https://github.com/bahayonghang/academic-writing-skills/blob/main/pyproject.toml) in the upstream repo.

## Skills NOT merged from AWS (and why)

Two AWS skills were deliberately excluded from this merge to avoid routing collisions and bloat:

| AWS skill | Why excluded |
|---|---|
| `paper-audit` | Substantially overlaps with the existing ARS `academic-paper-reviewer` (both run multi-reviewer simulation with a synthesis step). Bundling both would make Claude's skill-routing ambiguous. Use ARS `academic-paper-reviewer` for peer-review simulation. |
| `industrial-ai-research` | A vertical (industrial AI) specialization of ARS `deep-research`. The general-purpose `deep-research` already covers this domain. |

## License-compatibility summary

- **MIT** is permissive — MIT-licensed code can be redistributed inside a CC BY-NC 4.0 project, provided the MIT copyright notice and permission text are preserved. This `NOTICE.md` is that preservation.
- **CC BY-NC 4.0** is the *project-level* license. The full repository (including non-MIT files like `README.md`, `shared/`, `docs/`) cannot be used for commercial purposes. The five MIT subdirectories, taken on their own, remain MIT and are not subject to the NC clause.
- If you want the *MIT-only* subset for commercial use, copy `skills/{latex-paper-en, latex-thesis-zh, typst-paper, bib-search-citation, aiwei-zh}/` directly — they are self-contained.

## Merge maintainer

This merged fork is maintained by `@jiayou20021120-afk` (dizzy). It is a personal working copy and is **not** an official release of either upstream. For the canonical upstreams, see:

- ARS: https://github.com/Imbad0202/academic-research-skills
- AWS: https://github.com/bahayonghang/academic-writing-skills

To pull future updates from either upstream, the merge fork keeps `upstream` (ARS) configured as a git remote; AWS updates are merged manually since the two repos have unrelated histories.
