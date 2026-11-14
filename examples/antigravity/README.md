# Antigravity wrapper: run evidence

Evidence for the [Antigravity wrapper](../../antigravity/README.md): three recorded runs of one lightweight mode (`deep-research` `three-way-scan`), the loader checks behind the wrapper's claims, and the state of a full `academic-pipeline` run that is still in progress. Local paths in the transcripts are replaced with `<ARS_ROOT>`, `<WORK>` and `~`; nothing else is edited.

**This is not yet the end-to-end evidence that `CONTRIBUTING.md` asks of a platform port.** The full pipeline run has completed Stage 1 and Stage 2 only, and its files are not in this directory yet. Nothing here supports a claim about the integrity gates, the reviewer panel, the revision loops, or finalization on Antigravity.

## Run identity

| Field | Value |
| --- | --- |
| Antigravity CLI | 1.5.5, macOS (arm64), headless `agy -p` with `--output-format stream-json` |
| ARS | 3.24.2, repository HEAD `c67a7be` |
| Date | 2026-11-13 |
| Claude baseline | none run; "baseline" below means the behaviour the ARS files specify |

## Three-way-scan runs

| | [Run 1](run-01-flash-natural-language/) | [Run 2](run-02-argon-ars-3w/) | [Run 3](run-03-hydrogen-ars-3w/) |
| --- | --- | --- | --- |
| Model | Gemini 3.8 Flash (the CLI default) | Gemini 4 Argon (High) | Gemini 4 Hydrogen (High) |
| Trigger | plain-language request | `/ars-3w` | `/ars-3w` |
| Topic | retrieval-augmented generation and hallucination | same | Japan in the Second World War |
| `antigravity/settings.json` | no | no | yes |
| Read `deep-research/SKILL.md` to its last line | yes | yes | yes |
| Read ARS agent prompts and index protocols | no | yes | yes |
| Specialist roles | inline, disclosed | two subagents; synthesis inline, disclosed | two subagents; synthesis inline, disclosed |
| Index lookups (Crossref, OpenAlex, Semantic Scholar) | not attempted | attempted, HTTP 403, disclosed as `api_degraded` | reported as successful, inside the subagents |
| DOI or URL per work | yes | yes | yes |
| Read depth reported | "full paper" (false) | `abstract_only` | `abstract_only` |
| AI-use disclosure naming Antigravity and the model | yes | yes | yes |
| Duration, tokens | 80 s, 47,737 | 756 s, 188,785 | 578 s, 144,148 |

Each run directory holds the final `response.md` and `tool-calls.txt`, the main agent's ordered tool calls taken from the event stream. Subagent tool calls are not in that stream, so run 3's index lookups are evidenced by the subagents' report and by the manual check below, not by a recorded call. In runs 2 and 3 the headless response also contains the agent's interim status lines.

### Checked by hand after the runs

- **Run 1 gave a NeurIPS proceedings link that does not exist** (HTTP 404), under a disclosure that said all records were verified against primary sources. It also reported "read: full paper" for all three papers after three web searches and no page fetch. The compatibility note was tightened after this run to require the read depth to be reported as performed. Run 1 is kept as evidence of what a small default model does with ARS on Antigravity.
- **Run 2:** the three DOIs resolve and the proceedings link returns 200.
- **Run 3:** all three DOIs are in Crossref with the title, authors, journal, volume and pages the response gives.

### Index lookups and the terminal sandbox

In run 2 the ARS clients `openalex_client.py` and `crossref_client.py` returned HTTP 403 when run through Antigravity's `run_command`. The same client run from an ordinary shell on the same machine returned a record. Antigravity compiles `read_url(...)` permission rules into the terminal's outbound allowlist. With `--settings antigravity/settings.json`, a request made through `run_command` returned 200 from Crossref, OpenAlex and Semantic Scholar, and 301 (the redirect to HTTPS) from arXiv. Run 3 used that file.

## Loader checks

Run against Antigravity CLI 1.5.5 in a throwaway home directory:

| Check | Result |
| --- | --- |
| `agy plugin install` on this repository (Claude Code conversion) | 16 command skills registered; none of the core skills; `agy plugin validate` reports all four agents skipped for invalid `tools` frontmatter |
| Native plugin whose `skills/` entries are symlinks to the original directories or files | `agy plugin validate` counts them; `agy plugin list` loads none |
| Original `SKILL.md` files mounted directly | `agy plugin validate`: "only the first 24000 are loaded" for all four |
| Plugin written by `antigravity/install.py` | `agy plugin list`: 20 skills; `agy plugin validate --strict`: passed |

## Full pipeline run (in progress)

One `/ars-full` run on Gemini 4 Hydrogen (High), topic "Japan in the Second World War". It is driven headless, one `agy -p --conversation` turn per checkpoint; the port maintainer answers every checkpoint in his own words and the answer is passed to the agent. Its files will be added here when the run is complete.

State after seven turns (about 4.6 hours of agent time, 2.7 million tokens):

| Stage | Result |
| --- | --- |
| Pipeline start | Configuration and budget shown; stopped for confirmation |
| Stage 1, Phase 1 | Research question, methodology, Devil's Advocate checkpoint 1 (REVISE, then PASS after revision); stopped for confirmation |
| Review-form note (#921) | Shown with no default; stopped for the author's choice |
| Stage 1, Phases 2 to 6 | 65-source bibliography, source verification, synthesis, Devil's Advocate checkpoints 2 and 3, editorial and ethics review, revised report; stopped at the stage checkpoint with the experiment-intake question (#925) and the standing constraints (#927) |
| Stage 2 | Draft in Arabic at the author's request, then redrafted in English when the author changed the constraint; in-pair evaluator gate passed; stopped before Stage 2.5 |
| Stages 2.5 to 6 | not run yet |

Checked by hand: the 36 DOIs in the Stage 1 reference list are all in Crossref with matching titles; 29 of the 30 entries without a DOI were found in Open Library or Crossref, and the remaining one is the *Senshi Sōsho* series. The English draft contains the same 36 DOIs and no others.

Problems found so far:

- **No full text was read.** All 65 sources were read as abstracts (31), search snippets (30) or catalogue records (4). The report and the draft say so and carry `verification_status: UNVERIFIED`.
- **The run ledger was never written.** `scripts/run_ledger.py` needs PyYAML, which the `python3` on the test machine lacks; a second interpreter that has it was outside the directories the sandbox allows. Checkpoint answers are in the passport file and in the driver's turn records only.
- **One turn ended with a provider error** ("improperly formatted function call") after the Stage 1 files were saved and before the checkpoint was shown. A follow-up turn recovered and presented the checkpoint.
- **The draft carries pipeline labels in its body text** (for example "Gate G-04", 26 occurrences) and its contributor-roles statement credits drafting to the human author. Neither has been corrected; whether Stage 2.5 and Stage 3 catch them is part of what the rest of the run will show.

## Model portability

ARS prompts are calibrated for Claude Opus and Sonnet. Three Gemini models were tested on one mode, one run each, and one of them on the first two pipeline stages. This is an observation, not a comparison.

- Command `model: sonnet` hints are ignored; the session model runs every role.
- Gemini 3.8 Flash followed the loader and the output format but skipped the agent prompts and overstated its verification. It is below the model class ARS is written for.
- Gemini 4 Argon (High) and Gemini 4 Hydrogen (High) read the role prompts, dispatched subagents, and disclosed each degraded item.
- Claude models offered inside Antigravity were not tested.
- Not exercised on any model: the integrity gates, `academic-paper-reviewer`, revision, finalization, interactive (non-headless) sessions, and Windows.
