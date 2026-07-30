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
| Window (UTC) | 2026-07-30T23:18:29Z → 2026-07-30T23:48:11Z |
| Probe set | `evals/bakeoff/cross_model_promotion/probe_set_v2.json` |
| Probe-set sha256 | `cb7ac8dfc0db9513be716b0b2ab37f0d977ad424ee8c5c62758c57db8271c7be` |
| Adapter | `scripts/cross_model_codex_verify.sh`, sha256 `002f99e41ebc870b8dbb36f2818afbf5d33d61df9a9bbcf7506dd9622d025c01` |
| Transport | Codex CLI subscription route (`ARS_CROSS_MODEL_TRANSPORT=codex`) |
| Codex CLI | `codex-cli 0.145.0` |
| Auth mode | `chatgpt` (read from `auth.json`'s `auth_mode` field; `OPENAI_API_KEY` absent) |
| Repository HEAD | `14cf89ff08a878d77adf1b89d7adb6d3770758c2` |
| Event retention | `ARS_CODEX_EMIT_EVENTS=1` (2801 Codex events retained across 180 calls) |
| Event redaction | `command_execution` output and command strings cleared before publication, see § An unplanned finding |
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
| 5. p95 latency | 150.1 s | 77.8 s | ≤ 2 × baseline (300.2 s) | **PASS** |

Per-leg majority verdicts, both arms:

| leg | n | `gpt-5.5` | `gpt-5.6-sol` |
|---|---|---|---|
| easy | 10 | 10 VERIFIED | 10 VERIFIED |
| hard_preprint | 4 | 4 VERIFIED | 4 VERIFIED |
| hard_doi_less | 3 | 3 VERIFIED | 3 VERIFIED |
| hard_non_english | 3 | 3 VERIFIED | 3 VERIFIED |
| fabricated | 10 | 9 NOT_FOUND + 1 MISMATCH | 9 NOT_FOUND + 1 MISMATCH |

Both `NOT_FOUND` and `MISMATCH` count as catching a fabrication (measure 2 flags
on either). Neither arm returned a `VERIFIED` on a fabricated reference, and
neither flagged a real one.

The arms produced the same majority verdict on 28 of 30 references. Both
divergences are on fabricated references and both are correct flags: `fab-07`
(`gpt-5.5` NOT_FOUND, `gpt-5.6-sol` MISMATCH) and `fab-10` (the reverse). The two
models describe the same absence differently, which measure 2 counts identically.

Latency, full distribution: `gpt-5.5` median 18.5 s (min 6.6 s, max 179.5 s);
`gpt-5.6-sol` median 22.0 s (min 8.7 s, max 146.4 s). The candidate's p95 is
roughly half the baseline's while its median is higher: it has a much tighter
tail, not a uniformly faster response.

---

## Record integrity

`score_bakeoff.py` trusts the record it is given. It does not recompute the
fixture hash, verify that the job set is complete, reject duplicate rows, or
inspect exit codes, so a hand-authored JSONL makes it print
`ALL FIVE PASS -> eligible for provisional->validated`. That was demonstrated,
not hypothesised, during this work.

`evals/bakeoff/cross_model_promotion/audit_run.py` is the fail-closed gate that
closes it, and it ran before scoring. All 16 checks passed on this record:

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
| verdicts drawn from the closed set | VERIFIED 120 / NOT_FOUND 52 / MISMATCH 8 |
| Codex event stream retained | 180/180 calls |
| grounding flag re-derived from the retained events | 0 mismatches |
| `thread_id` matches the events' own `thread.started` | 0 mismatches |

The auditor was validated against five tampering scenarios before use: a
hand-authored record, a label-aware forgery that passes all five thresholds, a
truncated run whose `_meta` still claims 180 calls, a cherry-picked duplicate
row substituted for a bad one, and a post-hoc fixture swap. Each was caught.

Independently of the auditor, every row's parsed fields (`verdict`, `searched`,
`sources`, `thread_id`) were re-derived from that row's own retained raw adapter
output: **0 of 180 rows disagree**.

### What the events add, and what still cannot be proved

**The guard is now audited, not trusted.** This run was executed with
`ARS_CODEX_EMIT_EVENTS=1`, so each row carries the Codex events the adapter saw
(2801 events over 180 calls, about 2 MB). The auditor recomputes `searched` from
the presence of a completed `web_search` item and re-checks each `thread_id`
against the events' own `thread.started`: both agree on all 180 rows. An earlier
run of this same bakeoff, made before event retention existed, fails the current
auditor for that reason, which is the intended behaviour rather than a
regression.

That closes the gap where re-deriving a row from `stdout_raw` checked the harness
rather than the grounding decision. A reader who distrusts the adapter can now
recompute the grounding verdict from the retained events without running
anything.

**What remains unproved: the auditor detects incompleteness and inconsistency,
not fabrication.** A sufficiently careful hand-authored record, one that also
fabricates a plausible event stream, would still pass. Tested variants that do
fail: a record with no events at all, one whose events omit the `web_search` item
while the row claims grounding, and one whose `thread_id` does not match its own
events. Closing the remaining gap requires validating a `thread_id` against a
Codex-side record, which the CLI does not currently expose.

This limit applied equally to the 2026-07-16 run, which had strictly less. The
section exists so the difference is not overstated in either direction.

---

## An unplanned finding: the verifier read the local filesystem

Retaining the event stream surfaced something the summary fields could not.
Across 47 of the 180 calls the verifier issued shell commands and read files from
the operator's machine, for example:

```
/bin/zsh -lc "sed -n '1,240p' ~/.codex/skills/.../academic-paper/SKILL.md"
```

The file contents came back in the event stream as `command_execution` items with
a populated `aggregated_output`. 192 such items are present.

**Why it is possible.** The adapter runs `codex exec -s read-only` in an isolated
temporary `-C` directory. `read-only` prevents writes; it does not prevent command
execution, and it does not confine reads to the working directory. The model
decided on its own to inspect the surrounding machine while verifying a citation.

**What it means for this run.** Every call still shows a completed `web_search`
item, so the grounding contract held on all 180. But a bakeoff intended to measure
web-grounded citation verification recorded a verifier that was also reading local
files, which is not the behaviour under test. Read the results with that in mind:
the thresholds pass, and the measurement is less clean than a citation-only
transport would give.

**What it means for the transport.** This is the concrete form of a concern raised
in review as a hypothetical. It is no longer hypothetical: on this machine, on
this run, untrusted input (reference text and fetched pages) reached an agent that
executed shell commands and read local files, with web search available as an
egress path. A citation verifier should not have that capability. The finding
belongs to the transport under discussion in #567, not to this bakeoff.

**Redaction.** Because those reads captured local paths and unrelated file
contents, `evals/bakeoff/cross_model_promotion/redact_run.py` clears every
`command_execution` item's `aggregated_output` and `command` string before the
record is published. The items themselves are kept, with ids, status, and exit
codes, so the record still shows that commands ran and how many; deleting them
would hide the finding. Everything `audit_run.py` depends on is untouched:
`thread.started`, all 1802 `web_search` items including their queries, all
`agent_message` items, `turn.*`, and `error` items. The auditor passes all 16
checks against the redacted record, which is the copy committed here.

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

**Single-window run.** All 180 calls fall inside one 30-minute window on one
network from one machine. Latency figures in particular should be read as one
sample, not a stable characteristic: an earlier run of the identical bakeoff
three hours before produced p95 74.1 s and 123.2 s for the same two arms, against
77.8 s and 150.1 s here.

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
candidate's lower p95 latency (77.8 s vs 150.1 s) is an operational observation
from a single window, not that case.
