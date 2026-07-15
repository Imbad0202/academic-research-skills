# #510 — Executable sprint-contract panel checker (design)

> Issue: #510. Status: user-approved design, 2026-07-15.
> Predecessors: `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md` (Schema 13 sprint contract),
> `academic-paper-reviewer/references/sprint_contract_protocol.md` (authoritative orchestration reference).

## 1. Problem

The v3.6.2 sprint-contract machinery specifies a fully mechanical decision rule for
reviewer panels — `block | warn | pass` scores, severity/quantifier/expression
conditions, and the synthesizer's three-step protocol — and the protocol declares
internally-inconsistent report decisions unusable. But nothing executes that promise:
`scripts/check_sprint_contract.py` validates contract **structure** only. A synthesizer
(or a reviewer) that states scores which don't justify its own stated decision passes
every current gate.

This design adds a deterministic checker that recomputes both decision layers from the
primary artifacts and fails on mismatch. It is a **self-consistency gate on LLM output,
not a correctness gate**: it proves the stated decision follows from the stated scores
under the published rules; it does not judge whether the scores themselves are right.

## 2. User-approved decisions

1. **Mismatch blocks and retries once.** A failed recomputation voids that synthesis;
   the orchestrator re-runs the synthesizer once with the checker's diagnostics. A
   second failure aborts the editorial round. This mirrors the existing "internally
   inconsistent = unusable" handling; log-only was rejected.
2. **Both layers are checked.** Layer 1: each reviewer's own scores → own declared
   fired-conditions → own `## Editorial Decision`. Layer 2: the panel scoring matrix →
   quantifier thresholds → precedence → the synthesizer's emitted decision. The
   per-reviewer derivability check was already promised in protocol §5 and is cheap to
   include because both layers share the same engine.
3. **Zero-fired fallback is aligned to the design doc.** The v3.6.2 design doc says
   "if no condition fired, emit the accept-grade action"; protocol §8 and the agent
   prompts omit it. All surfaces are aligned in this PR: zero fired conditions ⇒
   `editorial_decision=accept`. (Reachable: e.g. under `reviewer/full.json`, one
   reviewer warning one mandatory dimension fires neither F0 nor F1/F2/F3.)
4. **The majority-threshold oddity is NOT touched here.** The documented formula
   (`⌈N/2⌉ + 1`, i.e. 4-of-5, 3-of-3) is stricter than colloquial majority. The checker
   implements the documented formula verbatim; the question of whether the formula is a
   spec bug is filed as its own issue (changing it changes real editorial outcomes and
   deserves standalone discussion).

## 3. Component: `scripts/check_panel_synthesis.py`

### CLI

```
python scripts/check_panel_synthesis.py \
  --contract shared/contracts/reviewer/full.json \
  --report r_eic.md --report r_meth.md --report r_domain.md --report r_persp.md --report r_da.md \
  --synthesis synthesis_output.md
```

- `--contract`: sprint contract JSON. Validated first by importing and reusing
  `check_sprint_contract.validate()` + `check_structural_invariants()` (no forked
  validation logic). Any error ⇒ exit 2.
- `--report` (repeatable): one Phase-2 reviewer report each. Count MUST equal
  `contract.panel_size`; otherwise exit 2 with `[PANEL-CARDINALITY: got=<k>,
  panel_size=<N>]` (mirrors the §6 `[PANEL-SHRUNK]` invariant — the checker never
  recomputes against a smaller panel).
- `--synthesis`: the synthesizer's sprint-mode output containing the pinned decision
  line (§5 below). **Optional:** when omitted, only Layer 1 runs — this lets the
  orchestrator verify each reviewer at Phase-2 lint time (§5 of the protocol), before
  paying for a synthesis that would be voided anyway.

Exit codes: `0` pass; `1` panel-synthesis mismatch (Layer 2); `2` structural/parse
error; `3` reviewer self-inconsistency (Layer 1). When multiple apply, precedence is
`2 > 3 > 1` (all diagnostics are still printed). Fail-closed throughout: anything
unparseable is an error, never a pass.

### Report parsing (strict, format-pinned)

From each Phase-2 report the checker reads:

- `## Dimension Scores` — one `### <Dn>: <name>` subsection per contract dimension,
  each carrying exactly one `$defs.score` token (`block | warn | pass`). Missing
  dimension, unknown dimension id, zero or multiple score tokens ⇒ parse error.
- `## Failure Condition Checks` — one subsection per `failure_conditions[]` entry with
  `fired: true | false`. Missing/unknown/duplicated condition ids ⇒ parse error.
- `## Editorial Decision` — must contain exactly one action token from the Schema 13.1
  closed enum (`editorial_decision=accept | minor_revision | major_revision |
  reject_or_major_revision | reject`). Zero or multiple distinct tokens ⇒ parse error.
- `## Scoring Plan Dissent` — presence is irrelevant to the checker (dissent changes
  how scores were produced, not what they are); parsed only to avoid false section
  matches.

### Expression parser (protocol §9, closed vocabulary)

Implements exactly the five recognised patterns, including the published
natural-English variants:

1. Priority-scoped single-match: `any <priority> dimension scores '<score>'`
   (+ `priority=<p>` and `<p>-priority` variants).
2. Priority-scoped count-based: `two or more <priority> dimensions score '<score>' or
   worse` (+ `priority=<p>` variant), with score ordering `pass < warn < block`.
3. Universal over priority: `every <priority> dimension scores '<score>'`.
4. Single-dimension literal: `<Dn> scores '<score>'`.
5. Conjunction: any of the above joined by ` AND `.

An unrecognised expression ⇒ exit 2 with `[EXPRESSION-UNRECOGNISED: condition_id=<F>,
expression=<...>]` — the same fail-closed behavior the synthesizer prompt mandates.
The parser guesses nothing; new expression forms require the §9-documented PR path
(protocol §9 + synthesizer prompt + this checker move in lockstep — §9's update rule
gains the checker as a third surface).

### Layer 1 — per-reviewer self-consistency

For each reviewer report, with the condition predicate evaluated over **that
reviewer's own scores** (the quantifier is panel-level; at the single-reviewer layer
`any` / `majority` / `all` all reduce to the bare predicate, matching the agent
instruction "evaluate each `failure_conditions` entry against your `## Dimension
Scores`"):

- **1a — fired-flag check:** recomputed predicate vs the reviewer's declared
  `fired: true | false`, per condition. Mismatch ⇒
  `[REVIEWER-SELF-INCONSISTENT: reviewer=<file>, condition=<F>, declared=<b>,
  recomputed=<b>]`.
- **1b — decision check:** apply the precedence rule (highest severity among the
  reviewer's declared-fired set; ties by ordinal position; zero fired ⇒ accept-grade)
  and compare with the reviewer's `## Editorial Decision` token. Mismatch ⇒
  `[REVIEWER-SELF-INCONSISTENT: reviewer=<file>, decision_declared=<a>,
  decision_recomputed=<a>]`.

1b runs on the **declared** fired set (that is the §5 "derivable from `## Failure
Condition Checks`" promise); 1a separately pins the declared set to the scores. Both
diagnostics can fire on one report.

### Layer 2 — panel synthesis recomputation

Per protocol §8, from parsed scores only (never from reviewers' declared fired flags):

1. Build the N-column scoring matrix per dimension.
2. Per condition: evaluate the predicate per reviewer, then apply the quantifier —
   `any`: ≥ 1 of N; `majority`: N ≥ 3 ⇒ ≥ `⌈N/2⌉ + 1`, N == 2 ⇒ both, N == 1 ⇒
   vacuous (never fires, warning printed); `all`: all N.
3. Precedence: highest severity among fired conditions, ties by ordinal position;
   zero fired ⇒ `editorial_decision=accept` (decision 3 in §2).
4. Compare with the synthesis decision line. Mismatch ⇒ exit 1 with
   `[PANEL-SYNTHESIS-MISMATCH: recomputed=<a>, stated=<a>, fired=<[...]>]`.

## 4. Runtime wiring (protocol §8.1, new)

`sprint_contract_protocol.md` gains §8.1 "Executable recomputation": after the
synthesizer emits its output, the orchestrator runs the checker over the contract, the
N usable Phase-2 reports, and the synthesis output.

- Exit 1 ⇒ void this synthesis, re-run the synthesizer **once**, appending the checker
  diagnostics to the re-run input. A second exit 1 ⇒ abort the editorial round with
  `[SYNTHESIS-MISMATCH]` (new §11 tag).
- Exit 2 ⇒ structural protocol violation; abort the round (do not retry — a parse
  error means an upstream lint should have caught the report, or the artifacts are
  mismatched with the contract).
- Exit 3 ⇒ the offending reviewer is unusable, exactly as §5 already specifies ⇒
  `[PANEL-SHRUNK]` abort. **No synthesizer re-run** — re-synthesizing over an
  inconsistent reviewer report cannot help. (The checker gives that existing rule an
  executable edge; it does not change the rule.) The reports-only invocation
  (no `--synthesis`) at Phase-2 lint time catches this before synthesis cost is paid.

CI runs the checker's pytest suite (fixtures, no live reports); real-run enforcement is
the orchestrator invocation above, same pattern as `check_sprint_contract.py` §2 step 1.

## 5. Prompt/document alignment (same PR, lockstep)

1. `sprint_contract_protocol.md` — §8 step 3 gains the zero-fired accept-grade
   sentence; new §8.1 (runtime wiring); §9 update rule adds the checker as a lockstep
   surface; §11 gains `[SYNTHESIS-MISMATCH]` and the checker's diagnostic tags.
2. `editorial_synthesizer_agent.md` (v3.6.2 protocol block) — Step 3 gains the
   zero-fired fallback + a pinned emission requirement: the decision is stated as the
   action string verbatim on its own line (e.g. `editorial_decision=major_revision`).
3. The five reviewer agents (`eic`, `methodology`, `domain`, `perspective`,
   `devils_advocate`) — Phase 2 step 4 gains the same pinned line requirement for
   `## Editorial Decision`, and (matching the synthesizer) the zero-fired accept-grade
   rule for deriving it.
4. `academic-paper-reviewer/SKILL.md` — orchestration note pointing at §8.1.
5. `CHANGELOG.md` — `[Unreleased]` entry.
6. `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md` is historical and is
   NOT edited.

Existing v3.6.2/v3.6.6 lints that count or pin these prompt blocks must stay green;
any lint that pins affected wording is updated in the same commit as the wording
(repo release-prep convention).

## 6. Tests

`scripts/test_check_panel_synthesis.py` (pytest, colocated per repo convention), with
fixtures under `tests/fixtures/panel-synthesis/`:

- **Positive:** a consistent 5-report `reviewer_full` round (decision matches) and a
  consistent 2-report `reviewer_methodology_focus` round; a zero-fired round that
  correctly states `editorial_decision=accept`.
- **Mutation (each must fail with the right tag/exit):** flipped synthesis decision;
  one flipped dimension score that changes the panel outcome; a reviewer fired-flag
  contradicting their scores (1a); a reviewer decision contradicting their declared
  fired set (1b); report count ≠ panel_size; missing required section; unknown
  dimension id; zero/multiple action tokens; unrecognised expression; majority
  threshold edges (3-of-5 must NOT fire, 4-of-5 must fire, documented formula);
  severity tie broken by ordinal position; conjunction (`AND`) evaluation; exit-code
  precedence (`2 > 3 > 1`); reports-only mode (no `--synthesis`) runs Layer 1 only.
- CI wiring: new script + test added to `.github/workflows/spec-consistency.yml` and
  the local pytest manifest in the same commit (manifest count bumps accordingly).

## 7. Non-goals

- The legacy/general 0–100 rubric path (`quality_rubrics.md` /
  `editorial_decision_standards.md`) — contradictory decision authorities; unifying
  them precedes any mechanical check there (per issue #510).
- The v3.6.6 writer/evaluator contract path — parallel machinery, different report
  shapes; out of scope by the issue's own boundary.
- Changing the majority formula (separate issue, per §2 decision 4).
- Semantic quality judgment of scores or review bodies — this is a self-consistency
  gate only.
- No new env flags, no schema change (Schema 13.1 untouched), no change when sprint
  contracts are not in use.
