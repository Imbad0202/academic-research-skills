# Running the pipeline

## Contents
1. Setup and the reviewer subagent
2. Paths: Workflow tool, Agent tool, single session
3. Cost and batch size
4. Resume after interruption
5. Mode recipes

## 1. Setup and the reviewer subagent

- **Plugin install** (skill + subagent): `/plugin marketplace add Imbad0202/academic-research-skills`,
  then `/plugin install academic-research-skills`. The reviewer subagent ships in the plugin's
  `agents/` folder and is listed with the plugin prefix:
  `academic-research-skills:screening_reviewer_agent`.
- **Skills-copy install** (the `sr-screener` folder symlinked or copied into `~/.claude/skills/`):
  also copy `sr-screener/agents/screening_reviewer_agent.md` into `.claude/agents/` (this
  project) or `~/.claude/agents/` (all projects); it is then listed as `screening_reviewer_agent`.
- Put the exact agent name shown in the session's agent list into `agent_type` in
  `screening_config.json`. A wrong name makes every call fail at once, which the pilot shows
  immediately. An empty `agent_type` uses the default workflow subagent: it works, but it
  carries more tools and more overhead per call.
- Python 3.9+ runs the scripts; `pip install openpyxl` gives an Excel log instead of CSV files.

## 2. Paths

### Workflow tool (preferred at scale)

1. `build_workflow.py ta --jobs pilot|all|pending|recheck ...` writes a script under
   `<work>/runs/` and prints its path, job count, planned agent calls and models.
2. Show the user that estimate. The Workflow tool runs only when the user has opted into
   multi-agent orchestration; a request such as "run the screening workflow" is enough.
3. `Workflow({scriptPath: "<path>"})`. Each batch runs Reviewer A and Reviewer B in parallel,
   retries missing IDs with a Grep subset call, and sends advance-vs-exclude conflicts to the
   adjudicator in the same run.
4. When it finishes, merge: the journal sits at
   `~/.claude/projects/<project>/<session>/subagents/workflows/<runId>/journal.jsonl`. Pass that
   folder, or the whole `workflows` folder, to `merge_decisions.py --from`.
5. Never edit the generated script by hand; change `templates/prompts.md`, the protocol or the
   config and generate it again. Generated scripts are the audit trail of what each run used.

### Agent tool (no Workflow tool)

1. Add `--emit-prompts <work>/prompts` to `build_workflow.py`; it writes one prompt file per
   call and `index.json` (label, prompt file, model).
2. For each entry: an Agent call with the reviewer subagent and the prompt "Read the file
   <prompt_file> and follow its instructions exactly." Run a few at a time.
3. Save each returned JSON as `<work>/decisions/<label with : replaced by _>.json` holding
   `{"label": "A:b001", "decisions": [...]}`, exactly as returned.
4. `merge_decisions.py --from <work>/decisions` reads the folder. Conflicts and missing IDs
   come back through `--jobs pending --emit-prompts ...` the same way.

### Single session (no subagents, for example claude.ai)

Only `quick` mode is honest here: one model reading a record twice is not two independent
reviewers. Screen small sets with the decision procedure in `references/reviewer_roles.md`, label the
result single-reviewer triage, and have a person act as the second reviewer.

## 3. Cost and batch size

- Agent calls for title/abstract screening: about 2 x batches, plus one adjudication call per
  batch with conflicts, plus retries. With 50 records per batch, 10,000 records mean roughly
  400-500 calls.
- Measure, do not guess: after the pilot, scale its token use by
  (total batches / pilot batches).
- Each call reads the protocol and rules (identical for every batch, placed first so providers
  can cache them) plus one batch file. Long protocols cost on every call; keep them focused.
- The default batch (50 records, at most 90,000 characters, lines wrapped at 150 characters)
  fits one Read call; the Read tool cuts very long lines, which is why lines are wrapped.
  Lower `max_records` if reviewers often return fewer decisions than records.
- Full text: two calls per report plus adjudications. Reports are long, so use the stronger
  model there (`FTA`/`FTB`) and expect far fewer calls than at title/abstract stage.

## 4. Resume after interruption

Usage limits, closed sessions and failed agents are normal on long runs:

1. `merge_decisions.py --from <all run folders>`: everything returned so far is kept; the
   earliest valid decision per record and role wins.
2. `build_workflow.py ta --jobs pending` schedules only what is missing: whole batches when a
   reviewer never ran, ID subsets when a reviewer skipped records, and open conflicts. It checks
   the pilot gate whenever those jobs reach outside the batches recorded in `pilot_batches.json`.
   To finish an incomplete pilot, use `--jobs pilot --batches <pilot batches>`; pending jobs
   confined to those batches also remain available. Work folders from before pilot-batch
   recording must regenerate the pilot workflow to record its batches.
3. Repeat until the merge prints "complete". A record is never given a default label along the
   way.

## 5. Mode recipes

**protocol**: follow `agents/protocol_architect_agent.md`; ends with the user's confirmation.

**quick**: no scripts. Apply the decision procedure to each record and answer with the table in
`references/reviewer_roles.md`. Offer the full pipeline if more records follow.

**pilot**: `prepare_records.py`, then `build_workflow.py ta --jobs pilot` (a spread of batches
plus every seed batch; `--pilot-n` or `--batches` to change). The team labels the same records
independently in `pilot_labels.csv`. Workflow, `merge_decisions.py --pilot-labels
pilot_labels.csv`, then the QC Auditor's pilot report. Amend, re-pilot, and continue only when
every labelled record has been compared, the AI misses none of the records the team advanced,
and the user gives the go-ahead. The workflow generator records the selected batches in
`pilot_batches.json` so pilot retries can be distinguished from screening the remaining batches.

**ta-screen**: `build_workflow.py ta --jobs all`, which refuses to start without a passing
`pilot_check.json`; `--jobs pending` also checks this gate for jobs outside the pilot (the pilot
batches can stay in: their decisions are already merged, so rerunning them only costs a little).
Then merge, `--jobs pending` until screening is complete,
`--jobs recheck` for the required QC recheck of joint exclusions, merge again until it prints
"complete", `overrides.csv` for the team's decisions, `build_outputs.py`.

**ft-screen**: `prepare_fulltext.py --pdf-dir PDFS` (name PDFs by record ID when possible;
missing ones are "reports not retrieved"). Preparation is blocked until the required
title/abstract QC recheck is decided, since QC may advance more records. Write the full-text
protocol, then
`build_workflow.py ft --jobs all`, Workflow, `merge_decisions.py --stage ft`, `--jobs pending`
until complete, `build_outputs.py --stage ft`. A full-text merge or report also remains incomplete
while title/abstract decisions or QC rechecks are pending; it cannot produce final counts or methods text.

**adjudicate** (a human screening set with conflicts): export the conflicting records with
titles and abstracts (Rayyan or Covidence CSV/RIS), `prepare_records.py` into a new work
folder, `build_workflow.py ta --jobs recheck-all`, Workflow, `merge_decisions.py --audit`.
`audit_report.csv` holds an independent AI third opinion per record for the team to weigh; it
does not decide.

**audit** (double-check exclusions): the same recipe on the excluded set.
`audit_report.csv` lists first the records the senior reviewer would advance.

**report**: `build_outputs.py` (and `--stage ft`), then the Reporter card.
