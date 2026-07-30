# Promotion Bakeoff: `gpt-5.6-sol`, maintainer run, 2026-07-30

**Outcome: all five non-inferiority thresholds pass. `gpt-5.6-sol` is eligible for
`provisional` → `validated`.**

This run supersedes the 2026-07-16 contributor run as the promotion receipt for
`gpt-5.6-sol`. It measures the same candidate against the same pinned probe set;
what changed is that the record is auditable and the run was executed by the
maintainer. Reasons are in § Why this run exists.

Spec: `shared/cross_model_verification.md` § Promotion Bakeoff (#518).

---

## Run provenance

| | |
|---|---|
| Executed by | maintainer (repository owner) |
| Window (UTC) | 2026-07-30T13:31:19Z → 2026-07-30T13:58:09Z |
| Probe set | `evals/bakeoff/cross_model_promotion/probe_set_v2.json` |
| Probe-set sha256 | `cb7ac8dfc0db9513be716b0b2ab37f0d977ad424ee8c5c62758c57db8271c7be` |
| Adapter | `scripts/cross_model_codex_verify.sh`, sha256 `297232e20dafdd4a98821d9fdca82edf61619587c29c1daa5ae749f8b78ec9ab` |
| Transport | Codex CLI subscription route (`ARS_CROSS_MODEL_TRANSPORT=codex`) |
| Codex CLI | `codex-cli 0.145.0` |
| Auth mode | `chatgpt` (read from `auth.json`'s `auth_mode` field; `OPENAI_API_KEY` absent) |
| Repository HEAD | `609bc4baded49fda20437b2d83b6fe68c5cb0f88` |
| Reasoning effort | adapter default (`xhigh`), both arms |
| Composition | 30 references × 2 models × 3 repeats = 180 calls |
| Raw record | `evals/bakeoff/cross_model_promotion/full_run_maintainer_2026-07-30.jsonl` |
| Scored report | `evals/bakeoff/cross_model_promotion/report_maintainer_2026-07-30.json` |

The probe set is the one introduced with the 2026-07-16 run, byte-identical: its
hash was recomputed at scoring time and matches the value recorded in the run's
`_meta`. It was not modified for this run, so the two runs are comparable.

---

## Results

| measure | baseline `gpt-5.5` | candidate `gpt-5.6-sol` | threshold | verdict |
|---|---|---|---|---|
| 1. grounded-search completion (per call) | 100.0% (90/90) | 100.0% (90/90) | ≥ baseline − 5 pp | **PASS** |
| 2. citation-mismatch recall | 100.0% (10/10) | 100.0% (10/10) | ≥ baseline − 5 pp AND ≥ 80% absolute | **PASS** |
| 3. false-disagreement rate on real references | 0.0% (0/20) | 0.0% (0/20) | ≤ baseline + 5 pp | **PASS** |
| 4. guard shape stability | 0 misfires | 0 misfires | == 0 (hard) | **PASS** |
| 5. p95 latency | 123.2 s | 74.1 s | ≤ 2 × baseline (246.4 s) | **PASS** |

Per-leg majority verdicts, both arms:

| leg | n | `gpt-5.5` | `gpt-5.6-sol` |
|---|---|---|---|
| easy | 10 | 10 VERIFIED | 10 VERIFIED |
| hard_preprint | 4 | 4 VERIFIED | 4 VERIFIED |
| hard_doi_less | 3 | 3 VERIFIED | 3 VERIFIED |
| hard_non_english | 3 | 3 VERIFIED | 3 VERIFIED |
| fabricated | 10 | 8 NOT_FOUND + 2 MISMATCH | 9 NOT_FOUND + 1 MISMATCH |

Both `NOT_FOUND` and `MISMATCH` count as catching a fabrication (measure 2 flags
on either). Neither arm returned a `VERIFIED` on a fabricated reference, and
neither flagged a real one.

The arms produced the same majority verdict on 29 of 30 references. The single
divergence is `fab-10`: `gpt-5.5` returned MISMATCH, `gpt-5.6-sol` returned
NOT_FOUND. Both are correct flags on a fabricated reference; the two models
described the same absence differently.

Latency, full distribution: `gpt-5.5` median 20.2 s (min 7.9 s, max 164.5 s);
`gpt-5.6-sol` median 25.8 s (min 7.8 s, max 130.5 s). The candidate's p95 is
lower while its median is higher: it has a tighter tail, not a uniformly faster
response.

---

## Record integrity

`score_bakeoff.py` trusts the record it is given. It does not recompute the
fixture hash, verify that the job set is complete, reject duplicate rows, or
inspect exit codes, so a hand-authored JSONL makes it print
`ALL FIVE PASS -> eligible for provisional->validated`. That was demonstrated,
not hypothesised, during this work.

`evals/bakeoff/cross_model_promotion/audit_run.py` is the fail-closed gate that
closes it, and it ran before scoring. All 13 checks passed on this record:

| check | result |
|---|---|
| fixture sha256 recomputed, matches `_meta` | PASS |
| call count equals the full job set | 180 / 180 |
| job set complete (no missing cells) | 0 missing |
| no cells outside the declared job set | 0 extra |
| no duplicate `(model, ref, repeat)` rows | 0 duplicates |
| every call exited 0 | 0 non-zero / timeout |
| every call carries a `thread_id` | 0 missing |
| `thread_id`s unique (one Codex thread per call) | 0 repeated |
| raw adapter output retained for every call | 0 missing |
| every call timestamped | 0 missing |
| auth mode is a ChatGPT subscription | `chatgpt`, no API key |
| adapter identified by hash | recorded |
| verdicts drawn from the closed set | VERIFIED 120 / NOT_FOUND 50 / MISMATCH 10 |

The auditor was validated against five tampering scenarios before use: a
hand-authored record, a label-aware forgery that passes all five thresholds, a
truncated run whose `_meta` still claims 180 calls, a cherry-picked duplicate
row substituted for a bad one, and a post-hoc fixture swap. Each was caught.

Independently of the auditor, every row's parsed fields (`verdict`, `searched`,
`sources`, `thread_id`) were re-derived from that row's own retained raw adapter
output: **0 of 180 rows disagree**.

### What this record still does not prove

Two limits, stated so the guarantee is not read as stronger than it is.

**The auditor detects incompleteness, not fabrication.** A hand-authored record
that fills in plausible `thread_id` and timestamp values passes all 13 checks;
this was tested after the fact and confirmed. What the checks establish is that
the job set is complete, internally consistent, and self-consistent with its own
retained output. They do not establish that any HTTP request occurred. Raising
that bar means validating `thread_id` against a Codex-side record, which nothing
in the CLI currently exposes.

**`stdout_raw` retains the adapter's output, not the Codex event stream.** The
retained value is the adapter's four-field JSON, so the underlying
`thread.started` / `web_search` / `agent_message` events, which are what the
grounding guard actually reads, are still discarded when the run directory is
removed. Re-deriving a row from `stdout_raw` therefore checks the harness, not
the guard. Retaining the event stream itself is the next improvement, and it
would also make the grounding claim independently checkable.

Neither limit is specific to this run: they apply equally to the 2026-07-16 one,
which had strictly less. The difference is in degree, and this section exists so
that difference is not overstated.

---

## Transport-limited checks: stated, not skipped

The Codex subscription route cannot satisfy two entry-gate checks that the
API-key route can. This section records the limitation rather than substituting
inference for it.

**Check 5, served model id.** `codex exec --json` emits only `thread.started`,
`turn.started`, `item.completed`, and `turn.completed`. No event carries a model
field. Verified directly on `codex-cli 0.145.0` (2026-07-30) by walking every key
of every event in a live run: the only model-adjacent key present anywhere is
`usage.reasoning_output_tokens`.

**An invalid model id does not produce a clean rejection.** Passing
`-m gpt-5.6-nonexistent-xyz` yields:

```
Model metadata for `gpt-5.6-nonexistent-xyz` not found.
Defaulting to fallback metadata; this can degrade performance and cause issues.
```

The CLI accepts the unknown id, falls back, and proceeds to `turn.started`
before failing later in the request. Measured 2026-07-30. Therefore
**"a wrong id fails" does not entail "a correct id was served as requested"**:
the failure path for an unknown id is degradation, not refusal, so it carries no
information about how a known id was routed. This run does not claim the model
id was confirmed.

**Check 6, reasoning effort.** Both arms ran the adapter default (`xhigh`),
requested identically. No event confirms the server honoured it. Not coverable
on this transport.

**What this run does confirm** that the 2026-07-16 run could not: the auth mode
is read from `auth.json`'s `auth_mode` field rather than inferred from the file
existing, so "this ran on a ChatGPT subscription rather than a metered API key"
is attested (`auth_mode: chatgpt`, `OPENAI_API_KEY` absent) instead of assumed.

**Standing recommendation.** Until a Codex event carries the served model id, a
promotion on this transport rests on the requested id, not a confirmed one. That
is acceptable for a non-inferiority comparison where both arms are requested the
same way through the same adapter in the same window; it would not be acceptable
as evidence about a single model in isolation.

---

## Measurement limits worth carrying to the next run

**Measure 2's tolerance cannot bind.** The fabricated leg has 10 items, so recall
moves in 10 pp steps, while the threshold's tolerance is ± 5 pp. The band is
narrower than the instrument's resolution. Only the 80% absolute floor did real
work here. A future probe set wanting a meaningful ± 5 pp comparison needs at
least 20 fabricated references. (First surfaced in the 2026-07-16 run;
re-confirmed here.)

**Measure 3's denominator is 20**, giving 5 pp resolution, so its tolerance is
exactly one item wide. Both arms scored 0, so it was not stressed.

**Both arms scored the ceiling on measures 1, 2, and 3.** A non-inferiority test
where baseline and candidate both hit 100% establishes that the candidate is not
worse; it cannot rank them. The probe set is not discriminating at this
difficulty. If a future comparison needs to separate two frontier models rather
than screen out a bad one, the fabricated and hard legs need harder items.

**The prompt carries no citing context.** Each call verifies a reference in
isolation ("does this work exist, are its fields right"), not whether a
manuscript's claim is supported by it. This measures the lookup channel only.
Claim-support verification is a different measurement and this run says nothing
about it.

**Single-window run.** All 180 calls fall inside one 27-minute window on one
network from one machine. Latency figures in particular should be read as one
sample, not a stable characteristic.

---

## Why this run exists

The 2026-07-16 run reached the same conclusion. It was not reusable as the
promotion receipt, for reasons that are about the record rather than the result:

1. **The raw evidence was discarded.** `run_bakeoff.py` set `stdout_raw` to
   `None` whenever a call succeeded, so the rows constituting the evidence kept
   only the harness's own normalised summary. No timestamps, no `thread_id`, no
   way to audit the record after the fact.
2. **The scorer could not tell that from a forgery.** With no fail-closed input
   validation, "this record scores well" and "this record came from 180 real
   calls" were indistinguishable.
3. **The run could not have executed as shipped on macOS.** The adapter used
   `mapfile`, absent from Bash 3.2 (what macOS ships); under `set -u` the failure
   aborts before any fail-closed JSON is emitted. The maintainer's platform could
   not have produced that record with that adapter, and the record has no
   platform attestation.
4. **The entry gate was amended after the fact.** The spec named only
   `cross_model_smoke_test.sh` (API-key route) when the run happened on
   2026-07-16; the amendment admitting the Codex route was written 2026-07-19,
   three days after the run it authorised, and the `validated` flip was committed
   19 minutes after the evidence.

None of this implies the earlier numbers were wrong; this run reproduces the
same outcome. It means they could not be checked, and a promotion gate whose
input is unverifiable measures the submitter rather than the model.

The three defects behind (1)–(3) are fixed in commit `609bc4b`: Bash 3.2
compatibility, `thread_id` emission, unconditional retention of raw output plus
timestamps and run provenance, and `audit_run.py` as the fail-closed gate.

On (4): the entry-gate amendment is sound as a rule, since a transport that cannot
echo a model id should say so rather than pretend to check it. It should stand on
this run, which was executed under it, rather than on the run it was written to
accommodate. Its wording should also absorb the wrong-id finding above, since the
2026-07-16 audit offered "a wrong id returns an error" as behavioural evidence
that the requested ids were served, and that inference does not hold.

---

## Verdict

All five thresholds pass, on a record that passes a fail-closed integrity audit
and verifies against its own retained receipts. `gpt-5.6-sol` is eligible for
`validated`.

Per the spec's Outcome bullet, this is a validation only. **The recommended
default is not flipped**: `gpt-5.5` remains the default, and a separate
superiority or operational-benefit case would be needed to change that. The
candidate's lower p95 latency (74.1 s vs 123.2 s) is an operational observation
from a single window, not that case.
