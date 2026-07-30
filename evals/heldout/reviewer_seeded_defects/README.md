# Reviewer Seeded-Defect Set (#574 E4, v0.1)

Held-out acceptance instrument for reviewer-prompt changes: synthetic manuscripts with
planted, ground-truthed quality defects plus a clean control, so that any change to the
review stage's prompts (the #574 behavior batch first — quota removal, typed evidence
anchors, severity transport, register/severity separation) is measured against a
baseline instead of shipped on intuition. Same discipline as
`evals/heldout/revision_claim_drift/` (#569/#570): measure the CURRENT model first,
then change the prompt, then measure again.

## Epistemic status

This is a **directional smoke tier, not a calibration set** (the #574 rescope's scaled
form of the E5 decision). n = 2 defective manuscripts (19 seeded defects) + 1 clean
control, labels adjudicated by the maintainer, not a blinded expert panel. It supports
"recall did not regress / clean-paper false findings did not increase" statements about
a specific model + prompt pair; it makes NO distributional FNR/FPR claim. Scope per
repo convention: state what was measured, nothing more.

## Contents

| Fixture | File | Ground truth |
|---------|------|--------------|
| MS01 — quantitative (educational technology, cross-sectional survey + LMS logs) | `manuscripts/ms01_quant_defective.md` | `manifests/ms01_quant.defects.json` (10 defects) |
| MS02 — qualitative/mixed (higher-education policy, interviews + small survey) | `manuscripts/ms02_qual_defective.md` | `manifests/ms02_qual.defects.json` (9 defects) |
| MS00 — clean control (educational technology survey, deliberately sound at its scale) | `manuscripts/ms00_clean_control.md` | none — zero planted defects; findings against it are scored per protocol step 5 (only factually-false assertions count as false findings) |

All content is synthetic: fictional authors, fictional institutions, `10.5555/…`
reserved-prefix DOIs. Defect classes: `statistical`, `inference`,
`citation_claim_mismatch`, `methods`, `ethics`, `internal_consistency`, `overclaim`,
`qual_rigor`. Each manifest row carries a verbatim `anchor_quote` (unique in its
manuscript) so adjudication is anchored, not vibes.

## Measurement protocol

1. **Blinded, isolated run per manuscript.** Copy the single manuscript to a
   NEUTRAL filename (`manuscript.md`) in an empty directory OUTSIDE this
   repository checkout, and run `academic-paper-reviewer` full mode there in a
   fresh session. The checked-in filenames (`_defective`, `_clean_control`) and
   this directory's name leak the condition; a repo-enabled session can also read
   the sibling manifests. The `manifests/` files are held-out ground truth — they
   must NEVER enter a review session's context (contamination voids the run).
   **Dispatch shape (frozen 2026-07-24):** full mode must be executed with the
   sprint contract's physically separated calls (`sprint_contract_protocol.md`
   §2) — each seat's Phase 1 produced by a clean, paper-blind call receiving only
   the contract + title/field/word_count, Phase 2 by a separate paper-visible
   call, structural §§4-5 lints enforced at dispatch. Single-context whole-panel
   simulation observably leaks manuscript content into the "blind" Phase 1
   (see `runs/superseded/2026-07-24-in-context-dispatch/`) and is NOT the
   measured condition; post-change runs must use the same isolated dispatch.
   **Isolation mechanism note:** once a baseline exists, any orchestrating
   session is manifest-aware by construction, so contamination isolation rests
   on the dispatch fence — review/synthesis agents receive only the
   neutral-named manuscript path, the reviewer skill files, the contract, and
   prior-phase outputs as delimited data, with `evals/` reads forbidden and no
   defect-related vocabulary in any prompt — never on orchestrator ignorance.
   Record the fence in the run records.
2. **Replicates.** At least **2 independent runs per manuscript per condition**
   (baseline and post-change). Full-mode output is stochastic; a single run's
   recall moves ~10 points on one defect flip. Report each run; gates use the
   mean across replicates.
3. **Collect** the five reviewer reports + the Editorial Decision Letter.
4. **Adjudicate per seeded defect** (maintainer, against the manifest):
   - `DETECTED` — any seat names the defect substantively (overlaps the anchor or
     an equivalent description of the same flaw);
   - `PARTIAL` — the symptom is noticed but misdiagnosed;
   - `MISSED` — no seat surfaces it.
   **Recall is strict**: numerator counts `DETECTED` only (`PARTIAL` contributes
   0 and is reported separately). Severity agreement is scored over `DETECTED`
   defects using the highest-severity assessment among the seats that detected
   it: exact band = 1, adjacent band = 0.5, further = 0, averaged.
   **Severity-source ladder (frozen 2026-07-24, applies identically to baseline
   and post-change runs):** a seat's severity is its explicit per-finding tag
   (the DA always carries one; other seats only when their report happens to tag
   the finding — pre-A3 they usually don't). When NO detecting seat carries an
   explicit tag, fall back to the Editorial Decision Letter's severity for the
   matching roadmap item (`Critical`/`Major` words; where a letter gives only
   priorities, P1 → major, P2/P3 → minor), and record the fallback in the run
   record. Rationale: before the #574 A3 change the non-DA seats emit no
   per-finding severity, so the "highest among detecting seats" rule is not
   fully computable from seat output alone; the ladder is the deterministic
   proxy that keeps baseline and post-change severity numbers comparable —
   post-change runs MUST use the same ladder (a post-A3 run will simply hit the
   fallback rung less often, which is itself part of what A3 is buying).
5. **Clean control — what counts as a false finding.** Count only findings that
   assert a defect that is FACTUALLY NOT PRESENT (fabricated flaw, invented
   inconsistency, mis-recomputed statistic). Deduplicate by defect concept
   across seats and the letter: the same false flaw claimed by three seats and
   repeated in the letter counts ONCE. Explicitly NOT false findings:
   style/preference suggestions, hedged "consider…" advice, and **true
   observations about genuine absences** (the control is sound at its scale,
   not perfect — a correct observation is a legitimate finding, never a false
   positive, and also not a seeded-defect detection).
   **Scoring exclusion:** citation-existence complaints about the synthetic
   references (`10.5555/…` reserved-prefix DOIs, fictional authors) are
   excluded from all counts by design — the reviewer is right that they don't
   resolve, but citation existence is the v3.11 gate's jurisdiction, not this
   set's measurand, and the fixtures cannot carry real citations.
6. **Record per run** (committed): write `runs/<date>-<fixture>-<baseline|post>-r<k>.json`
   with `{model_id, suite_commit, date, condition, per_defect: {SD-xx: verdict},
   severity_scores, clean_control_false_findings: [...concepts...], notes}`, AND
   commit the run's complete raw panel output (all reviewer reports + the
   Editorial Decision Letter) under `runs/raw/<same-stem>.review.md` for a
   hand-dispatched run, or as the bundle directory `runs/raw/<same-stem>/`
   for a harness-dispatched run (see § Dispatch harness) — verdicts
   without the underlying reports are not re-adjudicable (DETECTED/PARTIAL
   reclassification, severity recomputation, and clean-control zero-false-finding
   verification all need the full text). The summary table below is derived from
   these records, never the only artifact. Under
   `reviewer-e4/2026-07-27`, also commit every model response that a checker
   rejected before a retry plus that checker's output. A re-dispatch after a
   transport, quota, or session failure that produced no model response has no
   rejected response or checker output to preserve; disclose the no-response
   event in `notes`, but it is not a retry-evidence violation.

   Every normal or blocked record governed by this contract MUST carry
   `"evidence_contract": "reviewer-e4/2026-07-27"` (or a named later contract
   that retains at least the same retry-evidence requirement), plus these
   closed machine fields: `measurement_status` is `completed` or `blocked`;
   `provenance_status` is `valid` or
   `invalid_incomplete_retry_evidence`; `panel_completion_status` is
   `completed` or `aborted`; and `score_eligible` is Boolean. A normal scored
   record uses `completed` / `valid` / `completed` / `true`; every blocked
   record uses `measurement_status: blocked` and `score_eligible: false` while
   the other two fields state its independent provenance and completion facts.
   `provenance_status` is scoped only to retry-evidence completeness under the
   named evidence contract: `valid` does not attest contamination isolation,
   dispatch blindness, panel completeness, or any other provenance axis.
   The `invalid_incomplete_retry_evidence` downgrade is also the emitter's
   terminal fallback when ANY named location still fails to resolve at
   emission time (a terminal abort artifact is rewritten once from its own
   diagnostic before this fallback fires), so a downgraded record means
   "some named evidence location could not be made to resolve", not
   necessarily that a retry occurred.
   The closed
   grandfathered records and every artifact under `runs/superseded/` are frozen
   under their historical status and MUST NOT be backfilled with this contract
   label. A governed record with any retry MUST enumerate every event in its
   stage-specific retry list (for example, `phase1_retries`) and declare
   `rejected_response_preserved` plus `checker_output_preserved`. Whenever
   `rejected_response_preserved` is `true`, the same event MUST name a
   record-relative `rejected_response_location`, and that path MUST resolve.
   Every stored diagnostic, including a terminal abort diagnostic outside a
   retry list, MUST carry `diagnostic_form: "verbatim"` or
   `diagnostic_form: "normalized"` and name a record-relative
   `checker_output_location`; that path MUST resolve.
   `verbatim` is byte-for-byte checker output; `normalized` means absolute
   run-root prefixes were removed — the leading artifact path for checker
   output, and any registered run root wherever it appears for
   harness-assembled diagnostics (an OSError spells its path mid-sentence)
   — with every remaining character verbatim. The named checker-output
   artifact remains authoritative.

   **Blocked-run separation:** if a fail-loud checker stops the panel before all
   five cards and synthesis exist, or any checker-rejected response followed by
   a retry or its checker output is not preserved, do not write a normal
   scored-run record. Preserve the available
   evidence under `runs/raw/blocked/<same-stem>/` and a status record under
   `runs/blocked/<same-stem>.json`. A completed final panel with incomplete retry
   provenance is still invalid for scoring because paper blindness and retry
   eligibility are no longer independently re-adjudicable. Blocked attempts are
   operational evidence, not zero-valued measurements: exclude them from all means,
   do not impute missing responses or seats, and do not launch a replacement draw to
   conceal the abort.

   **Prospective retry-evidence boundary (adopted 2026-07-27):** only the new
   requirement to preserve every checker-rejected response followed by a retry
   and its checker output has a grandfathered exception. Every other
   blocked-run rule above — complete panel requirement, exclusion from means,
   no imputation, and no replacement draw that conceals an abort — applies to
   every attempt regardless of date.
   The exception is a closed artifact set of exactly 18 normal scored records:
   the 6 already committed as `runs/2026-07-24-*.json` and the 12 already
   committed as `runs/2026-07-25-*.json`, together with the accepted final
   panels they reference, remain governed by the earlier collection contract.
   No other pre-adoption abort, raw root, or unregistered attempt may be
   promoted into the scored namespace.

   That earlier contract required the five accepted final reviewer reports plus
   the Editorial Decision Letter. It permitted a multi-dissent restart but did
   not require the rejected response or its checker transcript to be retained.
   This is protocol versioning, not evidence reconstruction: the preserved
   accepted outputs remain re-adjudicable for the recorded recall, severity,
   and false-finding measurands, while the grandfathered rows make no
   independent claim that retry eligibility or the rejected response's paper
   blindness can now be re-adjudicated. Applying a new evidence requirement
   after observing the registered baseline and post-change outcomes would
   itself change the comparison set post hoc. Every non-grandfathered attempt,
   including both conditions after a model upgrade, uses
   `reviewer-e4/2026-07-27` or a named later contract that preserves this
   fail-closed minimum.

   **Contract-sensitivity disclosure:** the 2026-07-24 MS01 baseline r1,
   2026-07-24 MS02 baseline r1, and 2026-07-25 MS02 baseline r1 would not be
   score-eligible if dispatched under `reviewer-e4/2026-07-27`; each remains
   eligible only under its governing earlier contract. The 2026-07-24 MS01
   synthesis retry preserved its checker-rejected model response under
   `runs/raw/voided/`, but not the exact checker output, so it fails the strict
   current artifact pair. Any new or amended citation on or after 2026-07-27 of
   the registered 2026-07-25 gate verdicts MUST carry that non-attestation.
   Pre-adoption historical text is not retroactively rewritten, but quoting or
   reusing it in a current decision triggers the disclosure. Moving an
   Unreleased pre-adoption claim into a numbered release counts as current
   reuse, so the release notes must carry the disclosure before tagging.

   As diagnostics only, omitting both affected 2026-07-24 panels changes that
   row's severity agreement from 0.625 to
   `(0.667 + 0.500) / 2 = 0.584`; omitting the affected 2026-07-25 panel
   changes its baseline severity agreement from 0.663 to
   `(0.650 + 0.611 + 0.722) / 3 = 0.661`, still above the post-change 0.536,
   so the registered severity direction remains a regression. In the 2026-07-24
   counterfactual, MS01 recall remains 0.90 and MS02 recall remains 1.00 on one
   retained replicate each; in the 2026-07-25 counterfactual, MS02 recall
   remains 1.00 on its single retained replicate. Clean controls are
   unaffected, but the two-replicate requirement is broken; neither
   sensitivity is a recomputed formal gate.
   The disclosed no-response transport re-dispatches in the 2026-07-25 post
   records produced no checker-rejected response, so they do not create a
   symmetric missing-artifact exposure.

**Acceptance gates for a reviewer-prompt change** (all three, on replicate means):
mean strict recall does not regress (overall AND within the `critical` band);
mean clean-control false-finding count does not increase; mean severity-agreement
score does not regress. "Stricter" alone is not an improvement (#574 rescope,
product outcome).

## Baseline

The 2026-07-24 and 2026-07-25 table rows are the closed grandfathered set
described above. In particular, the 2026-07-24 row's PANEL-SHRUNK re-dispatch
and synthesis void-and-retry, plus the 2026-07-25 MS02 r1 multi-dissent retry,
were accepted under that earlier contract; neither row claims those recovery
events would be eligible under `reviewer-e4/2026-07-27`.

| Date | Commit | Model | Runs | MS01 recall (strict) | MS02 recall (strict) | Clean-control false findings | Severity agreement | Notes |
|------|--------|-------|------|----------------------|----------------------|------------------------------|--------------------|-------|
| 2026-07-24 | 307ef24 | claude-opus-4-8 (reasoning effort xhigh; isolated per-seat two-phase dispatch per the frozen dispatch shape) | 2 per fixture (6) | **0.90** (9/10 both replicates; critical band 0.75 — SD-01 GRIM = PARTIAL in both, the only non-detection across all MS01 runs in both dispatch designs) | **1.00** (9/9 both replicates; critical band 1.00 — both panels explicitly name the absent interview protocol) | **0** (both replicates; decisions Minor Revision / "Major Revision gated on citation verification" — the latter driven entirely by the excluded-by-design synthetic-DOI class, see run notes) | **0.625** (per-run 0.722 / 0.667 / 0.611 / 0.500) | Recall losses are recompute-class only (GRIM); severity-agreement losses split between DA band placement (dominant; same defects swing a full band across replicates/seats) and three letter-fallback 0.5-losses where no seat carried a tag — both halves of the #574 A3 gap (A4/B1 also evidenced). Two protocol events, both recovered per protocol: one PANEL-SHRUNK abort (DA multi-dissent, §5 retry) and one voided-and-retried synthesis (§8.1 duplicate emission pair, voided output preserved in `runs/raw/voided/`). Records in `runs/2026-07-24-*.json` + `runs/raw/`; the superseded single-context attempt (near-identical numbers — the leak did not inflate recall) in `runs/superseded/` |
| 2026-07-25 | f7d9d07 (prompt state; fixtures v0.1 unchanged) | claude-opus-5 (effort xhigh, thinking enabled; isolated per-seat two-phase headless-CLI dispatch per the frozen dispatch shape) | 2 per fixture (6) | **0.95** (10/10 + 9/10; critical band 0.875 — r1 is the first observed full-GRIM detection across any run of this set (R1 performs the achievability recompute verbatim); r2 = PARTIAL on SD-01, the A4 recompute class) | **1.00** (9/9 both replicates; critical band 1.00) | **4 / 2** (decisions reject_or_major_revision on both clean runs; all six counted findings are narrative-logic fabrications — invented contradictions or facts asserted without textual basis — with no mis-recomputed statistic anywhere; synthetic-DOI class excluded by design) | **0.663** (per-run 0.650 / 0.611 / 0.667 / 0.722; non-DA seats emit zero per-finding tags pre-A3; 4 letter-fallback cells — both MS02 SD-01 severities ride the letter because the seats that substantively detect the missing instrument are untagged and the DA tag covers only the label-contradiction symptom) | Model-upgrade re-measurement: the `opus` dispatch alias moved from claude-opus-4-8 to claude-opus-5 on 2026-07-25, so BOTH conditions were re-measured per this protocol's re-run-don't-reuse rule — this row (not 2026-07-24) is the operative baseline for the #581 acceptance gates. The opus-5 register is markedly harsher than opus-4-8 on the clean control (0 → 4/2 false findings; Minor Revision → reject_or_major_revision), so cross-model rows must never be compared. One §5 multi-dissent recovery (MS02 r1, Perspective seat), accepted under the pre-2026-07-27 evidence contract; its rejected first response was not then a required artifact and is not used to claim retry re-adjudicability. Records in `runs/2026-07-25-*-baseline-r*.json` + `runs/raw/` |
| 2026-07-25 | ad81b2e (#581 behavior batch A1/A2/A3/B1) | claude-opus-5 (same dispatch) | 2 per fixture (6) | **1.00** (10/10 both replicates; critical band 1.00 — SD-01 GRIM detected with the full achievability arithmetic in BOTH replicates, by R1 and the DA independently) | **1.00** (9/9 both replicates; critical band 1.00) | **2 / 1** (mean 1.5 vs baseline 3.0; the baseline's logical-foreclosure / inoculation / recruitment-channel-as-fact fabrications do not recur — the dedup-vs-anonymity invented incompatibility is the one concept surviving in both post replicates (r1 adds one DA mis-absence claim); r1 is the ONLY run of all twelve whose clean-control decision avoided reject_or_major_revision: major_revision, no F1 fired) | **0.536** (per-run 0.600 / 0.600 / 0.500 / 0.444) — a REGRESSION on the frozen highest-tagged-seat ladder | **Gate verdicts vs the 2026-07-25 baseline row**: strict recall PASS (improved, overall and critical band); clean-control false findings PASS (decreased); severity agreement FAIL as frozen-measured. Diagnostic decomposition (recorded, not a gate substitute): DA-only agreement is flat-to-up (0.621 → 0.644; post MS02-r2's 0.75 is the best of all twelve runs), letter-fallback cells drop 4 → 0, and per-finding tag coverage goes 0 → 100% on the non-DA formal registers (A3's transport goal achieved) — the frozen max rule now aggregates four newly-tagged seats whose tag distributions skew critical (one Domain seat tagged 7/7 critical), i.e. the metric can now SEE cross-seat band inflation the baseline could not express. Open residual: seat-level severity-band anchoring (#574 B1 follow-up). Records in `runs/2026-07-25-*-post-r*.json` + `runs/raw/` |
| 2026-07-27 | 19bc872 (Spec A implementation, including terminal DA-contract correction) | claude-opus-5 (effort xhigh, thinking enabled; same isolated per-seat two-phase dispatch) | **BLOCKED:** 2 clean panels launched; r1 reached synthesis but has incomplete retry provenance; r2 has incomplete Phase 1 retry evidence and conformance-aborted; **0 score-eligible runs**; MS01/MS02 not launched | **NOT COMPUTABLE** | **NOT COMPUTABLE** | r1 unscored observation: **1**, panel decision `major_revision`; replicate mean **NOT COMPUTABLE** | **NOT COMPUTABLE** | Formal Spec-A E4 attempt produced no score-eligible run. r1's first malformed methodology Phase 1 response was overwritten by its permitted structural retry, so the completed final panel cannot prove paper blindness or retry eligibility and is namespaced under `runs/blocked/`. r2's first malformed Methodology and Perspective Phase 1 responses were also overwritten; their exact checker diagnostics survive, but the rejected responses do not, so r2 is independently provenance-invalid. Its Perspective Phase 2 then emitted an empty `## Scoring Plan Dissent` section and failed `[DISSENT-GRAMMAR: dissent section must name dimension_id]`; Phase 2 retry is permitted only for multi-dissent, so DA and synthesis were not run. Observed clean-cohort provenance-invalid rate **2/2 = 1.00** and conformance-abort rate **1/2 = 0.50**, the latter versus the Spec-A diagnostic expectation of approximately zero. Required 2 × 3 fleet and all acceptance gates are **BLOCKED / NOT COMPUTABLE**, not pass or fail. No replacement draw, missing-value imputation, or reconstruction of missing retry output was used. |
| pending (corrective iteration) | — | — | — | — | — | — | — | A future full 2 × 3 measurement must start as a new cohort after the conformance-abort cause is corrected; compare with the newest same-model baseline and re-run both conditions after model upgrades |

## Dispatch harness (#608)

`scripts/dispatch_e4_panel.py` launches one panel and makes the evidence
contract structural instead of aspirational. Hand dispatch lost retry
provenance on both panels of the 2026-07-27 fleet because a retry wrote over
the response it was retrying, and that is not a discipline problem: the
preservation step sat at the exact moment the operator was trying to get the
run to proceed.

```
python3 scripts/dispatch_e4_panel.py --fixture ms01_quant --condition post \
    --replicate 1 --date 2026-08-01 --work-dir /tmp/e4-ms01-post-r1
```

**Operational precondition:** the calls run `claude -p --bare`, which skips
CLAUDE.md auto-discovery, hooks, plugins and auto-memory so that no context
outside the allowlist reaches a prompt. `--bare` authenticates strictly through
`ANTHROPIC_API_KEY` (or `apiKeyHelper` via `--settings`); OAuth and keychain are
never read, so export the key before launching a fleet. Before a fleet, run
ONE single-panel smoke test: the `--tools ""` shutoff and the
`--bare` + `--effort xhigh` + `MAX_THINKING_TOKENS` interaction have not been
exercised with a live call, and either failing would fail fleet-wide —
recoverably (blocked records, no evidence loss), but at the cost of the run.

What it changes, and why each is a property rather than a step:

- **A response is written to a path that cannot be overwritten, before any
  checker is allowed to judge it.** Attempts are numbered in the filename
  (`methodology.phase1.a1.md`, `…a2.md`) and the write uses `O_EXCL`, so
  preservation precedes the decision to retry instead of depending on it.
- **Each checker invocation's own bytes are stored** next to the response it
  judged (`…a1.gate.log`). Checkers run from inside the bundle with relative
  paths, so no absolute prefix has to be stripped and every stored diagnostic
  is `verbatim`.
- **Paper-blind and paper-visible calls get separate whitelisted sandboxes.**
  The blind sandbox does not contain the manuscript at all, so blindness is a
  filesystem fact rather than the seat's restraint; hand dispatch put every
  artifact in one directory. `evals/` is outside both, so no call can reach
  the manifests. The CLI's own built-in tools are shut off per call with the
  whitelist spelling (`--tools ""` — the seats' task is pure text and needs
  none), so the fence does not rest on headless permission defaults — the
  checkout is public, and an enabled WebSearch could otherwise retrieve a
  manuscript's held-out siblings with no tool-use audit trail in a text
  response. Under an emptied whitelist a tool added by a later CLI is closed
  by default, the property a deny list can never have; a `--disallowedTools`
  deny list rides behind it as depth only.
- **The contamination fence is a path allowlist, not a word denylist.** The
  harness may read only the contract, the seven agent files, and the three
  manuscripts; a manifest is not readable, and a future held-out artifact is
  not readable by default either — the property a denylist can never have. A
  word denylist was written first and measured to be worse than the failure it
  guarded: `manifest` and `seeded` are ordinary review vocabulary ("Where it
  manifests"; "how far the themes were seeded by the questions") and **5 of
  the 18 committed real panels of this set contain one**, so gating assembled
  prompts on them would abort roughly a quarter of panels after all five cards
  existed, with no replacement draw permitted. Ground-truth tokens appearing in
  model output are now recorded as an advisory `leak_canary_hits` field for the
  maintainer, never as a panel-killing gate: output cannot carry ground truth
  the model was never given, and a true hit is not repaired by aborting.
- **The seat set is derived from the contract**, ordered by the frozen dispatch
  order, with `panel_size` asserted — so a mode or `panel_size` change cannot
  leave the harness dispatching yesterday's panel while both sides of the
  synthesis check agree with each other and disagree with the contract.
- **Only a reviewer-conformance exit is retried.** §11 routes every exit-2
  class (contract, metadata, IO, role binding) to abort-no-retry, and retrying
  one would also file a `phase1_retries` event for something the evidence
  contract does not classify as a retry at all. Retry eligibility for the one
  permitted Phase 2 recovery is read from the checker's own
  `[PROTOCOL-VIOLATION: multi_dissent=true]` line, pinned by the checker's
  tests so a reword fails CI instead of silently killing a fleet.
- **The four closed status fields are derived**, and `provenance_status` is
  derived by checking that each named location still resolves rather than by
  trusting the write path.
- **The work directory mirrors this tree**, so promoting a run is a copy:
  `runs/<stem>.json` beside `runs/raw/<stem>/`, or the blocked namespace for
  an aborted panel, with every `*_location` already record-relative. Nothing
  has to be rewritten at commit time — that rewrite is what previously turned
  a verbatim diagnostic into a paraphrase.
- **A completed panel carries `adjudication.status: "pending"`.** The harness
  cannot adjudicate `per_defect` — that needs the held-out manifest, which must
  never enter a session — so the maintainer fills the verdicts before the
  record is committed.
- **The delivered prompts are dispatched whole where the protocol does not
  narrow them.** §2 names a subsection only for the five seats; the field
  analyst and the synthesizer get their full agent files. Sending the
  synthesizer just its sprint-contract block produced panels with no Editorial
  Decision Letter and no Revision Roadmap while the arithmetic checker still
  passed, which no gate would have caught.
- **A synthesis-layer failure is voided and re-run once** with the checker
  diagnostics appended as delimited data, per §8.1; exit 2 and exit 3 abort
  with no re-run. Aborting on any nonzero blocked valid panels on ordinary
  stochastic formatting.
- **A no-response transport event is durable but is not a retry.** A timeout or
  a missing binary writes its exact bytes and blocks the run, without filing a
  retry event — which is what the contract says a re-dispatch that produced no
  response is.
- **`--date` and `--fixture` are validated before they name anything.** They
  become path components, and one separator relocated the evidence bundle,
  filed a blocked run under the scored namespace, or lost the record entirely.
- **Prompt material may not be reached through a link.** An allowlist over
  names would otherwise authorize whatever a name points at, so one symlink in
  `manuscripts/` could make a manifest readable while the fence still reported
  itself intact.
- **A committed record carries no absolute local path.** Blocked records are
  committed to a public repo, so the `diagnostic` field is stripped rather than
  left to a hand pass at commit time.
- **A work directory inside this repository is refused outright**, with no
  record written, because writing one there is the thing being refused. The
  same applies to an unnameable run: a malformed `--date` or an unknown
  `--fixture` is refused before anything is written, because the record's own
  name is built from them. An
  internal preservation fault produces a blocked record rather than a
  traceback: losing the record is the one failure mode this mechanism cannot
  afford.

Records and bundles land in the work directory, never straight into the repo;
committing them stays a deliberate step.

**Comparability:** the harness changes the dispatched condition relative to
the 2026-07-24/25 hand-dispatched rows — `--bare` removes the operator's
user-level context, each seat receives only its own configuration card,
instructions and data travel as separate system and user halves, blind and
visible calls get separate sandboxes, and the contract is stamped and
validated before call one. Harness-dispatched runs therefore form a new
cohort: never compare them against the hand-dispatched rows above, and
re-measure BOTH conditions under the harness per this protocol's
re-run-don't-reuse rule before reading any gate. One provenance bound is
declared rather than detected: `suite_commit_reproducible` compares the
checkout state before and after the panel, so an edit made DURING a gate
and reverted before the end probe is not caught — prompt material is
snapshotted at dispatch and is immune, but the checkers load from the
repository at each gate, so do not modify the checkout while a panel
runs.

**Emission-failure recovery.** The record install is staged-then-atomic
and rolls the raw bundle back on failure, so a transient filesystem
fault after the panel completes leaves one of two recoverable states,
neither of them silent. (1) Any staged-write or install failure: the
staged temp file is removed, the bundle is rolled back into the work
directory, no record exists, and the identity is NOT consumed — the
evidence is intact on disk, but re-emitting it needs a fresh dispatch
(a fresh work directory re-runs the panel; there is no
resume-from-bundle CLI in this version, a declared bound). (2) Rollback
failure on top of (1): the bundle stays under `runs/raw/<stem>` with no
record beside it; the console names the fault, and the bundle is the
complete account of the attempt for manual reconstruction.

## Integrity checking

`scripts/check_seeded_defect_fixtures.py` validates structure only (manifest schema,
closed enums, defect-count agreement, every `anchor_quote` present verbatim exactly
once in its manuscript, clean control free of manifest references). It is a fixture
integrity gate, NOT a behavioral measurer — `run_evals` has no native task for this
set; the behavioral measurement is the manual protocol above.
