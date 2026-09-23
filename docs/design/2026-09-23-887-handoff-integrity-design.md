# #887: Handoff integrity across context compaction and subagent returns (design)

**Status**: design, decisions complete. On 2026-09-23 the maintainer chose option D,
keeping the user's exact words, a deterministic fixture, a separate risk-register row,
and a handoff check that appears only when it has something to report (§7). The
implementation follows §8 in the same change. The vendor observations below are not an
ARS reproduction on Claude Code.

**Issue**: #887, a follow-up from #883 (`audits/harness-retirement-2026-09-opus-5-5.md`,
candidate follow-ups).

**Related**: R11 and checkpoint decision provenance
(`academic-pipeline/references/pipeline_state_machine.md`); the opt-in passport reset
(`academic-pipeline/references/passport_as_reset_boundary.md`); dispatch trim discipline
(`academic-pipeline/agents/pipeline_orchestrator_agent.md` § Context Hygiene at
dispatch); the E6 disposition event boundary
(`academic-pipeline/references/claim_verification_protocol.md`); the read log that
`/ars-mark-read` keeps beside the passport under the shared file lock
(`scripts/ars_mark_read.py`, `scripts/file_lock.py`).

**Scope**: the pipeline run the orchestrator drives. Phase-by-phase standalone runs
(`academic-paper` Mode B, which supports cross-session work) are outside this design and
keep today's behavior; §2's rows apply to them unchanged.

---

## 1. Problem

Two boundaries replace part of the working record with text a model wrote:

- **Platform context compaction.** A model-written summary replaces older turns. What
  the summary omits is gone from the session; what it paraphrases is no longer the
  user's words.
- **Subagent returns.** The orchestrator sees the subagent's report, not its working
  context. A report can omit unfinished work or describe a step as done.

**Vendor evidence.** The Claude Opus 5.5 system card reports internal snapshots, running
as a specialized subagent, that occasionally refused to write a compaction message
(under 0.01% of completions; §6.3.1, p. 102), and lists very long trajectories with
compaction and multi-agent scenarios among the blind spots of its automated behavioral
audit (§6.4.11, p. 122).

**ARS evidence.** One synthetic Pi run crossed automatic compaction
(`examples/pi/README.md`). Its persisted state records the Stage 1 collaboration
observer as `insufficient_evidence_raw_dialogue_compacted_non_blocking`: the observer's
turn-range pointer pointed at turns that compaction had removed. A terminal response sent
during compaction was not consumed, and the persisted state file, not the conversation,
controlled the completion claim. That run persisted pipeline state to a file
(`examples/pi/state/pipeline-state.json`). The Pi wrapper itself persists only whether
ARS is active (`pi/wrapper.js`), and the Claude Code path keeps no pipeline state file by
default (§2).

## 2. What survives today

| Item | Where it lives by default | Survives compaction | Survives a subagent return |
|---|---|---|---|
| Material Passport (Schema 9) and its append-only ledgers (`reset_boundary[]`, `compliance_history[]`, `audit_artifact[]`) | a user-owned file at the path the user names (`docs/DATA_FLOWS.md`) | yes, when written to disk | yes, carried in each dispatch |
| Durable deterministic artifacts: apply reports, `revision-evidence-bundle/1.0`, `author-adjudication/1.0`, the E6 finding set and disposition sidecar, PDF preflight sidecars, the preregistration sidecar, #660 and successful #672 carriers, the re-review traceability sidecar and its typed records, the read-attestation ledger | files with recorded hashes | yes | yes |
| Transient replay inputs: the E6 raw session-event files with their event-id-to-path mapping, and the exact session-held source-text map that `scripts/evidence_rows.py` needs for source-bound replay | run-local files outside the repository, or session memory | **no guarantee**; the durable E6 sidecar's digest alone cannot replay, and a missing source text fails the render | not applicable (orchestrator-side) |
| Pipeline state (`pipeline_state`, `current_stage`, per-stage `checkpoint_confirmed`, `decision`, `retry_count`, `loop_count`, `consecutive_continue_count`, revision `items_pending`, `dialogue_log_ref`) | model-maintained in the conversation (`academic-pipeline/agents/state_tracker_agent.md`); `docs/PERFORMANCE.md` states that ARS keeps no orchestrator state between sessions; a file only where a user-selected local store (#673) or a particular run writes one | **no guarantee** | not applicable |
| A pending checkpoint decision of any type (FULL, SLIM, MANDATORY) and a partly collected multi-item answer | the same conversation state; a file only as `pending_decision` in the opt-in reset ledger, for MANDATORY decisions | **only under `ARS_PASSPORT_RESET=1`**, and only for MANDATORY | not applicable |
| The user's verbatim decisions and authorizations | the user's turns; deterministic artifacts only for the #670 integrity-correction authorization, `/ars-mark-read` scope, `author-adjudication/1.0` choices, E6 disposition events, and the re-review deferral-loop typed records | **no**, except those artifacts | relayed by quotation (R11 rule) |
| A required tool step's outcome, where the step writes an artifact | that artifact | yes | yes |
| A required tool step's outcome, where the step reports its gating result only on stdout or by exit status. Found so far: `scripts/check_phase_conformance.py` and `scripts/check_panel_synthesis.py` in first-round review, `scripts/check_re_review_synthesis.py`, `scripts/check_revision_token_conservation.py`, `scripts/evidence_rows.py` validation and rendering, and the gate tokens of `scripts/verify_submission_package.py` (its report file is reused only after a freshness check, and the pipeline recomputes the gate at every pass); also a #672 failure (a bounded diagnostic, no carrier) | the conversation | **no** | a report's claim only |

The gap is the rows marked no: pending decisions, stage progress, verbatim decisions,
stdout-only tool outcomes, and the transient replay inputs default to living in the
conversation or in session memory, which is exactly what compaction rewrites.

## 3. Inventory per stage and checkpoint

Sources: the state machine's transition tables; the orchestrator's checkpoint rules,
handoff table, audit gate, revision and re-review sections, and checkpoint authority
fidelity; the claim verification protocol; the passport reset protocol; the
`academic-paper` and reviewer `SKILL.md` checkpoint and contract sections, with the
reviewer sprint contract protocol; the process summary protocol; and the output code of
the stdout-only scripts in §2. The list of stdout-only steps is what this inventory
found, not a guaranteed complete list; an implementation should enumerate required
steps from the skills' text rather than copy this table.

Checkpoint types follow the orchestrator's adaptive rules: MANDATORY where pinned; the
Stage 5 completion checkpoint is pinned FULL; every other checkpoint starts FULL and
becomes SLIM after two consecutive "continue" answers. A SLIM checkpoint still requires
an explicit continue or pause.

| Stage / checkpoint | Pending decisions | Unfinished work that can be in flight | Required tool steps and where the outcome persists | Verbatim authorization inputs |
|---|---|---|---|---|
| Entry (FULL, first checkpoint) | entry point and mode | mid-entry passport check | none beyond the passport | the user's initial instructions (the Stage 6 record quotes them verbatim); cross-model consent when `ARS_CROSS_MODEL` is set; #684 binding context |
| Opt-in reset and resume (`ARS_PASSPORT_RESET=1`) | at a FULL checkpoint outside systematic review, "continue" overrides the reset for the next stage; on resume, optional `stage=` and `mode=` overrides, a re-verify prompt when `verification_status` is `STALE` or `UNVERIFIED`, and any `pending_decision`, re-prompted before dispatch | a reset boundary not yet resumed | the boundary and resume entries in `reset_boundary[]` (passport); the hash check against the ledger on disk | the override and the resumed decision, recorded on the resume entry (`chosen_branch`, `user_override`) |
| Stage 1 research (FULL or SLIM) | checkpoint confirmation; design-freeze divergence when the cross-model checkpoint runs | Socratic rounds; per-phase deep-research checkpoints | PDF preflight sidecars (#512); preregistration sidecar or a #672 failure diagnostic (conversation only); inquiry ledger (opt-in) | design-freeze divergence choice |
| Stage 2 writing (FULL or SLIM) | checkpoint confirmation; the Paper Configuration Record (an Iron Rule confirmation before Phase 1); intake answers (citation-verification policy); outline approval; after a writer or evaluator phase aborts, the choice to retry, fall back, or return to an earlier phase | plan-mode chapter confirmations; drafting phases | writer pre-commitment output (full mode); `claim_intent_manifests[]` | intake answers that set `terminal_policies`; the configuration confirmation |
| Audit artifact gate (cross-stage: after a synthesis, survey-design, or abstract-only deliverable) | `MINOR`: a MANDATORY continue, iterate, or pause; `MATERIAL`: blocked unless the user acknowledges every finding; after the target round is reached still `MATERIAL`: `ship_with_known_residue`, `another_round` (raises the cap by one), or `abort_stage`; `AUDIT_FAILED`: blocked until a fresh wrapper run | revision and re-audit rounds; an `another_round` or `abort_stage` choice made but not yet committed, since `another_round` becomes durable only when the higher-round wrapper run produces its proposal | persisted verdicts in `audit_artifact[]` (passport), each with `round` and `target_rounds`; an `AUDIT_FAILED` verdict only in the wrapper's output artifacts, never in the passport | the acknowledgement (`finding_ids`, `acknowledged_at`); the escalation choice |
| Stage 2.5 integrity (MANDATORY) | gate closure; the three-round FAIL-loop choice; one E6 disposition per finding; per-row E4 and E5 advisory choices, where an E5 confirmation of an absolute novelty claim lives only in the checkpoint conversation and is later carried into the AI-usage disclosure | correction rounds (`retry_count`); a partly collected set of E6 choices | citation verification summary; compliance report (`compliance_history[]`); E6 finding set and disposition sidecar (durable) plus the raw event files and mapping (transient); evidence-row validation and rendering (stdout; needs the session-held source-text map) | E6 dispositions; E5 confirmations; compliance overrides; #670 correction authorization |
| Stage 3 review (MANDATORY) | reviewer-configuration confirmation; the decision branch (revise, restructure, abort) | panel calls not yet returned; the one permitted synthesizer re-run after a synthesis-layer failure | phase conformance check before synthesis and panel synthesis check after it (both stdout and exit status; exit 1 allows one re-run, exits 2 and 3 abort the round); review-panel provenance carrier | branch choice; cross-model reviewer consent |
| Coaching 3 to 4 | one author choice per roadmap item | a partly finished triage (items answered before the sidecar is built) | `revision_roadmap.py build-adjudication` and `validate-adjudication` | per-item author choices |
| Stage 4 and 4' revision (FULL or SLIM) | checkpoint confirmation; a structural-escalation MANDATORY choice (narrow to exact scope, expand exact scope, or, at apply time only, acknowledge the already authorized structural patch) | patch rounds | anchorize and the apply report (artifact); token conservation (stdout); finalizer; evidence bundle | the escalation choice with its exact scope |
| Stage 3' re-review (MANDATORY) | the decision branch (to 4.5 or to 4'); the deferral loop (dissent adjudications, unresolved divergences, escalation approvals, G2(d) fail-closed acceptances); after an abort, the recovery choice (fix and re-run, legacy flag, or abandon) | the three gate calls; scoped Phase 2B′ re-verifications; sidecar revisions | the checker (exit status and stdout); the traceability sidecar and its typed records (artifacts) | each deferral answer (typed record); branch and recovery choices |
| Coaching 3' to 4' | a **new** complete author choice per item of the new roadmap; prior-round choices are never inferred or carried forward | a partly finished triage | as coaching 3 to 4 | per-item author choices |
| Stage 4.5 final integrity (MANDATORY) | as Stage 2.5 | as Stage 2.5 | as Stage 2.5, plus the claim audit (opt-in) and the finalizer's markers | as Stage 2.5 |
| Stage 5 entry gate (MANDATORY) | confirmation; citation style | none yet | #660 carrier, and #672 carrier or failure diagnostic (advisory) | read attestations; strict policies already set |
| Stage 5 execution | in-stage questions: LaTeX, content confirmation; `VERIFICATION-INCOMPLETE` remediation (declare a venue profile, or switch `submission_package` back to `advisory` and re-finalize) | MD, DOCX, PDF steps; the formatter fix loop (at most two rounds) | formatter hard gate; submission-package verifier (stdout tokens; recomputed at every pass by design) | a policy change, when chosen |
| Stage 5 completion (FULL) | accept deliverables, or decline Stage 6 | none | none | the decline, when given |
| Stage 6 record and terminal | the record's language; terminal acknowledgement | the whole-pipeline observer pass, which reads live conversation turns and never a summary; Process Record compilation, which quotes the initial instructions and key decisions verbatim; Pandoc and LaTeX rendering to PDF | rendered files; #673 post-terminal sequence (opt-in store) | the acknowledgement; the verbatim quotes the record needs |

Three observations from the table:

1. **Tool outcomes split in two.** Steps that write an artifact already persist, usually
   with a hash, so a resumed stage can check the artifact instead of trusting a
   summary. The steps in §2's last row report their gating result only on stdout or by
   exit status, and a #672 failure leaves only a diagnostic. For those, nothing outside
   the conversation says whether the step ran, passed, failed, or never ran, or how many
   of its permitted retries are used.
2. **Decisions and progress mostly do not persist.** The pending state of every
   checkpoint type, partly collected multi-item answers (coaching triage, E6
   dispositions, re-review deferral answers), E5 confirmations, an audit escalation
   choice not yet committed by the wrapper, retry and loop counters, and the in-stage
   Stage 5 questions live in the conversation. Audit rounds are the exception: each
   persisted audit entry records its `round` and `target_rounds`.
3. **Some inputs cannot be kept by any ledger of answers.** E6 validation needs the raw
   event bytes, and evidence-row rendering needs the session-held source text; both fail
   closed when the input is missing, so their loss surfaces as a failure and recovery
   means collecting the input again. The collaboration observer needs the original
   turns, never a summary. In the Pi run, the Stage 1 observer reported insufficient
   evidence because compaction had removed its turns, while the Stage 6 pass scored the
   whole pipeline from a raw dialogue index covering both sessions. None of the options
   below stores the original turns, so wherever they are unavailable the observer
   reports insufficient evidence.

## 4. Rules that do not depend on the storage decision

These follow from rules ARS already has, and the design recommends them whichever
option §6 picks.

- **R-HI-1, a paraphrase is not a decision.** The state machine already says a
  paraphrase of an earlier turn is never the user's decision. After compaction, a
  checkpoint whose answer survives only as summary text is treated as open: the
  orchestrator shows what the summary says was decided and asks the user to confirm.
  This does not revoke a decision the user made; it recovers the words before anything
  relays them.
- **R-HI-2, an artifact, a receipt, or a fresh run.** A required tool step counts as run
  only when its artifact exists and validates, when a recorded receipt shows its
  outcome (§5), or when the step is run again. A summary's or a subagent report's
  statement that a step ran or passed is recorded as unverified. The stdout-only steps
  are deterministic over their inputs, so the default is a fresh run on resume; the
  submission verifier already requires one at every pass. A fresh run needs its inputs:
  when an input is transient and gone (the E6 raw events, the evidence source text), the
  step is reported as not run and the input is collected again. A step with a retry
  limit is re-run only when a receipt shows how many retries are used; without one, the
  orchestrator asks the user before retrying. The status vocabulary keeps `passed`,
  `failed`, and `not run` distinct, and the absence of any evidence reads as `not run`,
  never as `passed`.
- **R-HI-3, unfinished work is named, not inferred.** At each stage close, the
  orchestrator compares the stage's declared deliverables and required steps with what
  exists (the existing material-gap detection in the state tracker). Anything missing
  is reported as unfinished, including items a subagent report did not mention.
- **R-HI-4, surface, never assume.** On resume, after compaction, or after a subagent
  return, an item that cannot be verified is shown to the user with its status (open,
  unverified, not run, or missing). It is never filled from inference. For a partly
  collected multi-item answer, the items already recorded in a typed artifact stand; the
  rest are asked again.

- **R-HI-5, the handoff check speaks only when it has something to report.** After
  compaction, on resume, and after each subagent return, the orchestrator compares what
  the session shows with the record (§5, when one exists). When at least one item needs
  the user, it shows one handoff check with four groups: awaiting your answer (an open
  checkpoint or a partly collected answer), cannot confirm (a summary or report states a
  decision the record cannot show in the user's words), not run (a required step with
  no artifact, receipt, or fresh run), and missing (a referenced file that is absent or
  changed). Items the record already backs are not asked again, and the check ends with
  the number of such items. With nothing to report it shows nothing, so silence cannot
  distinguish a check that found nothing from a check that did not run; the alternative
  was a one-line status every time.

Without a storage change these rules are prompt-level. They can only act on what the
session still shows: if compaction removed every trace of a pending checkpoint, no
prompt rule can recover it.

**Noticing a compaction.** The rules also depend on the orchestrator noticing that a
compaction happened. The SessionStart hook (`hooks/hooks.json`,
`scripts/announce-ars-loaded.sh`) receives the event's `source`, and its `compact`
branch, which it shares with `resume`, already sends a short announcement; one sentence
there can tell the session to run the handoff check before continuing an ARS pipeline
run. The hook cannot tell whether a run is in progress, so the sentence is conditional
and appears after every compaction or resume where the hook runs (on Windows only with
Git Bash, as for the rest of the hook). Plugin installs wire the hook by default; other
install paths do not, unless the user wires it into their own Claude Code settings
(`docs/CONTROL_AVAILABILITY.md`, the SessionStart row and note 3). Without the hook, the
rules rely on the orchestrator recognizing the summary.

## 5. What a storage change has to hold

Whichever file holds it, a record that closes the gap in §2 needs five kinds of entry:

- **The initial instructions**, verbatim or by option, as the first entry.
- **Checkpoint events**: opened (stage, type, question, options) and closed (the
  answer), for FULL, SLIM, and MANDATORY checkpoints, the audit gate's choices, the
  reset-path overrides, and the in-stage questions that change a deliverable.
- **Partial answers**: each item of a multi-item answer as the user gives it, until the
  deterministic builder runs (coaching triage, E6 dispositions, E5 confirmations,
  re-review deferral answers, the structural-escalation scope).
- **Tool receipts**: for each stdout-only step, the command, the input hashes, the exit
  status, and the gate tokens or a digest of stdout, with a status of `passed`,
  `failed`, or `not run`, and the number of permitted retries used. A receipt lets a
  resumed stage report an outcome without a fresh run; R-HI-2's fresh run remains the
  check.
- **Progress and references**: retry, loop, and fix-round counters, and
  pointers (path and hash) to the transient replay inputs, so a resumed stage knows what
  to look for and can say precisely what is missing.

**Coordination with the reset ledger.** Under `ARS_PASSPORT_RESET=1`, `pending_decision`
on a boundary entry stays authoritative for the reset path, and the reset protocol
governs its re-prompt. The new record's open checkpoint entry points at that boundary
hash, and the answer closes both: the reset protocol's resume entry, which consumes that
hash, records it, and so does the new record's closing entry for the same checkpoint. One
pending state, two views.

## 6. Storage options

**Option A: a checkpoint ledger inside the Material Passport.** Generalize
`pending_decision` into an always-on, append-only ledger in Schema 9 holding the five
kinds of entry in §5, with answers stored as option values only.

- Survives compaction, because each entry is written when the event happens, before any
  summary exists. One file, so no second file to keep consistent.
- Travels with the passport into every dispatch, and a user may share the passport.
  That is why A stores option values only: exact words would be re-asked when a dispatch
  needs them (R-HI-1), the E5 confirmations would keep only the chosen option, and the
  Stage 6 record would say that a quote was lost to compaction.

**Option B: persist the whole pipeline state to a local file by default.** The Pi example
run did this. It reverses the documented position that ARS keeps no orchestrator state,
adds a new user-visible store with a data-flow entry and a deletion story, and stores a
snapshot rather than an auditable sequence of events.

**Option C: prompt-level rules only.** Adopt §4 and nothing else. Cheapest; it cannot
recover a checkpoint whose every trace is gone, and the acceptance's fixture item would
be met by the explicit statement that the rule is prompt-level and unmeasured.

**Option D: a local run ledger beside the passport (recommended).** An append-only peer
file next to the passport, named after it, holds the five kinds of entry in §5,
including the user's exact words. This follows the `/ars-mark-read` read log, a peer
file named after the passport (`<passport-stem>_human_read_log.yaml`) and written
under the shared file lock (`scripts/ars_mark_read.py`). The passport itself gains no
field, so there is no second record to keep in step.

- **What it keeps out.** The whole ledger is not carried in routine dispatches, and it
  is not inside the passport a user may share. It is not a promise that the words never
  leave the machine: checkpoint authority fidelity requires quoting the user's exact
  words when a dispatch carries a decision, so the needed excerpt still goes into that
  dispatch; whenever the session model reads the ledger, its content travels over the
  Claude platform connection like any file the model reads (`docs/DATA_FLOWS.md`); and
  the Codex audit wrapper embeds any supporting file its invoker names
  (`scripts/audit_snapshot.py`), which the docs would advise against for the ledger.
- **What it adds over A.** The exact words that R11 relays, E5 confirmations, and the
  Stage 6 record rely on survive compaction; the initial instructions can be quoted at
  Stage 6. D does not store the original conversation, so the observer's limit in §3
  (observation 3) applies to D as well.
- **What it costs over A.** Its own schema, a validator, a `docs/DATA_FLOWS.md` store
  entry and deletion note, and edits to three content-locked pipeline files (the state
  machine, the orchestrator, and the state tracker), with their locks re-pinned. Writes
  follow the read log: under the shared file lock (`flock` on POSIX, and on Windows a
  best-effort `msvcrt` backend that has no CI coverage, the same standing as the read
  log today), each write replaces the whole file atomically, so an interrupted write
  leaves the previous ledger intact. Each entry carries its own hash and the hash of the
  previous one. That catches an accidental change to any entry, the final one included,
  and a deleted entry that has a later entry, such as a line lost in a sync conflict. It
  does not catch a lost tail or an edit that recomputes the hashes, so the chain detects
  accidental damage, not deliberate edits.
- **What it cannot detect.** A missing ledger fails closed: every checkpoint whose
  answer the session cannot show in the user's words is asked again. A broken chain
  fails closed for the entries from the break onward. But the passport records nothing
  about the ledger, so a restored older copy of the ledger alone keeps a valid chain and
  looks current; the rollback limit below applies. The alternative, binding the
  ledger's current hash into the passport on every write, would catch that case and an
  edit that recomputes the hashes (unless the passport is edited too), but needs an
  atomic two-file update; the machinery ARS has
  for that (the inquiry branch ledger, `scripts/inquiry_branch_ledger.py`) refuses to
  run on any lock backend but POSIX `fcntl`, so it would exclude native Windows.
- **On the Pi port**, the ledger would be written by the same orchestrator prompt; the
  wrapper adds no integration, so it depends on the model following that prompt.

**Common to A, B, and D.** None stops fabrication: the orchestrator writes the entries,
so a model that invents an approval can also invent the entry. That failure stays R11's;
these options address loss. A validator is deterministic only over what the record
contains. None detects a rollback either: a restored older copy of the file that holds
the record (the passport under A, the state file under B, the ledger under D) looks
valid and lacks the newest entries. Whether that fails closed depends on what is lost.
A lost closing entry or receipt does: the checkpoint is asked again and the step counts
as not run. A lost later entry that changed an earlier answer does not: the earlier
answer looks current again, as when a later pause is lost and the continue before it
stands. A lost counter does not either: the older copy can show fewer retries used than
were spent, so a retry limit could be passed without asking the user.

## 7. Decisions for the maintainer

1. **Storage** for pending decisions, partial answers, receipts, and progress: chosen,
   D (2026-09-23; the alternatives were A, B, and C).
2. **Exact words** (D only): chosen, keep the user's exact words in the local ledger
   (part of option D as presented; the alternative was option values only).
3. **Evidence**: chosen, a deterministic fixture for the validator (2026-09-23; six
   synthetic scenarios, §8 step 3). The alternative, required only with C, was the
   explicit prompt-level-and-unmeasured statement. The fixture shows the validator
   reads a ledger correctly; whether the orchestrator writes the entries stays
   prompt-level and unmeasured.
4. **Risk register**: chosen, a new row for handoff loss that cross-references R11
   (2026-09-23; loss and fabrication fail differently, and the ledger addresses only
   loss). The alternative was an extension of R11.
5. **When the handoff check shows**: chosen, only when it has something to report
   (R-HI-5, 2026-09-23). The alternative was a one-line status every time.

## 8. Implementation outline

For Option D with the chosen answers:

1. Schema: the local ledger's entry schema (§5's five kinds, each entry carrying its own
   hash and the previous entry's hash); the file is named after the passport, as the read
   log is.
2. Writes: the shared file lock and an atomic whole-file replace, as
   `scripts/ars_mark_read.py` uses them; fail closed on a missing ledger, and from the
   break onward on a broken chain.
3. Validator and fixture: a script that reads the ledger and reports open checkpoints,
   partly collected answers, steps without a receipt, counters, and referenced files that
   are missing or changed. Synthetic fixtures: a summary that drops a pending decision, a
   summary that claims approval, a step reported as passed with no receipt, a missing E6
   raw event file, a broken chain, and a normal close.
4. Prompt edits: the orchestrator writes entries as events happen and applies §4,
   including the R-HI-5 display, on resume, after compaction, and after each subagent
   return; the state machine names the ledger beside checkpoint decision provenance and
   the reset coordination rule; the state tracker's structure names the ledger. Content
   locks are re-pinned in the same commit. Required tool steps are enumerated from the
   skills' text, not from §2.
5. Hook: one conditional sentence in the `compact` branch (shared with `resume`) of
   `scripts/announce-ars-loaded.sh`, which plugin installs wire by default (§4, noticing
   a compaction).
6. Docs: `docs/RISK_REGISTER.md` (new row), `docs/DATA_FLOWS.md` (the new local store,
   its deletion note, and the advice not to pass it to the audit wrapper),
   `docs/CONTROL_AVAILABILITY.md` (the compaction reminder rides the SessionStart hook,
   which only plugin installs wire by default),
   `CHANGELOG.md`.

The rules stay prompt-level where they rely on the orchestrator writing and reading the
ledger; the validator is deterministic only over what the ledger contains.

## 9. Non-goals

No change to the platform's compaction mechanism, no claim that ARS can stop a model from
omitting content, no replacement for the opt-in passport reset, and no coverage of
standalone phase-by-phase runs in this design.
