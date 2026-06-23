# ARS × SkillOpt integration harness

Wire [Microsoft **SkillOpt**](https://github.com/microsoft/SkillOpt) onto ARS's
existing `rq_framing_patterns` gold set so the **Socratic wording-pattern
advisory** (Kong #257) can be *trained as a natural-language skill* and gated on
held-out validation — the same way SkillOpt trains any agent skill: rollout →
reflect → bounded edit → validation gate → `best_skill.md`.

> **Status: harness only.** This directory ships the integration plumbing and a
> seed skill. It does **not** ship a trained skill or modify any `SKILL.md`.
> Running an optimization (which spends model budget) and proposing a trained
> skill is a separate, maintainer-gated step — see [Scope & next steps](#scope--next-steps).

## Why this exists (honest framing)

ARS already detects AI-typical research-question wording with a **deterministic
regex detector** — `scripts/check_rq_framing_patterns.py`, twenty hardcoded shells
`WP01`–`WP20`. It scores a perfect `balanced_accuracy = 1.000` on the gold set…
*because the gold set was authored to match those regexes*. That precision is real
but brittle: any **novel** AI-typical phrasing that no `WP` regex anticipated slips
through silently.

This harness offers the complementary capability: train a compact **LLM skill**
that makes the same advisory judgment, measured by the **same metric and the same
acceptance gate** (FNR < 0.30, FPR < 0.20, balanced accuracy ≥ 0.75). The bet is
that an LLM skill can generalize to wording the regex can't enumerate while keeping
false positives on domain-native questions low. SkillOpt is the disciplined way to
evolve that skill instead of hand-editing a prompt and hoping.

## Layout

| File | Role |
|---|---|
| `ars_scoring.py` | **Pure**, no SkillOpt/network/key. Parse `trigger_advisory` from a model answer; score + aggregate vs gold (mirrors ARS's own metric). |
| `ars_gold_loader.py` | SkillOpt `SplitDataLoader` — reads `evals/gold/rq_framing_patterns/gold_set.json`, normalizes, splits. |
| `ars_adapter.py` | SkillOpt `EnvAdapter` — single-turn rollout (`chat_target`) + scoring + reflect delegation. |
| `run_ars_skillopt.py` | Launcher — registers the adapter into SkillOpt's env registry, then delegates to `skillopt-train` / `skillopt-eval`. **No fork of SkillOpt.** |
| `configs/rq_framing_patterns.yaml` | Self-contained SkillOpt config (Claude backend, small budget). |
| `skills/rq_framing_patterns/initial.md` | Seed skill — the trainable starting point. |
| `tests/test_ars_scoring_offline.py` | Zero-API plumbing test over the real gold set. |

## Prerequisites

- `pip install skillopt` (lightweight core: `openai`, `numpy`, `pyyaml`, `httpx`, …).
- The Claude backend (`backend: claude_chat`) drives your **local Claude CLI**
  (`claude --print`), so it uses your authenticated `claude` binary rather than a
  separate metered API key. Optimizer = Opus, target = Sonnet by default (ARS's
  Opus-for-review / Sonnet-for-execution convention; never Haiku).

## Run

**Offline plumbing test — zero API, zero model calls:**

```bash
python -m pytest tools/skillopt/tests/test_ars_scoring_offline.py -q
```

**Train the skill (spends model budget — see the warning below):**

```bash
# from the ARS repo root (paths in the config are CWD-relative):
PYTHONPATH=. python tools/skillopt/run_ars_skillopt.py \
    --config tools/skillopt/configs/rq_framing_patterns.yaml
```

**Evaluate an already-optimized skill instead of training:**

```bash
PYTHONPATH=. python tools/skillopt/run_ars_skillopt.py --eval \
    --config tools/skillopt/configs/rq_framing_patterns.yaml
```

> ⚠️ **Cost.** Training issues many model calls (epochs × batch × rollouts +
> optimizer reflection). The shipped config is deliberately small (2 epochs, the
> 40-item gold set), but it is **not free** — every call goes through your Claude
> CLI. Start small; scale `train.num_epochs` / `optimizer.learning_rate` only after
> a smoke run.

## Validate a trained skill against ARS's own harness

A skill SkillOpt produces should be checked by ARS's **independent** tooling, not
just SkillOpt's internal gate:

```bash
# ARS's own deterministic checker + the multi-task eval harness:
PYTHONPATH=. python -m scripts.check_rq_framing_patterns
PYTHONPATH=. python -m scripts.run_evals --task rq_framing_patterns
```

A trained skill is only interesting if it clears the same FNR/FPR/balanced-accuracy
gate the regex detector already clears — ideally while catching held-out wording the
regex misses.

## Notes & caveats

- **`scripts` package name collision (benign).** Both ARS and SkillOpt expose a
  top-level `scripts` package. SkillOpt's is a *regular* package (has `__init__.py`);
  ARS's is a *namespace* dir (no `__init__.py`). Per PEP 420, the regular package
  wins, so `from scripts import train` resolves to SkillOpt's even with the ARS repo
  root first on `PYTHONPATH`. Verified; no action needed.
- **Single skill, not the whole pipeline.** SkillOpt trains one compact skill
  against one auto-scorable target. This harness targets exactly one ARS measurement
  task; it does not "optimize ARS."
- **Gold-set provenance.** The gold set was authored to the regex detector, so the
  regex baseline is ~1.0 on it. The honest value of an LLM skill is *generalization*
  to wording outside the 20 shells — best measured on held-out / new items, which is
  follow-up work.
- **Version pin.** Built and verified against SkillOpt `v0.1.0` (PyPI). `v0.1.0`
  marks `EnvAdapter.reflect` abstract with no body, so `ars_adapter.py` implements
  `reflect` explicitly (delegating to `run_minibatch_reflect`).

## Scope & next steps

Per [`CONTRIBUTING.md`](../../CONTRIBUTING.md), changes to a shipped `SKILL.md` or
agent definition need an issue + maintainer discussion first. This harness changes
**none** of those — it is additive tooling, like the existing `evals/` harness. The
natural follow-up (separate, opt-in, budgeted): run an optimization, validate the
lift with `scripts/run_evals.py`, and bring before/after evidence to an issue before
proposing any trained skill for the pipeline.
