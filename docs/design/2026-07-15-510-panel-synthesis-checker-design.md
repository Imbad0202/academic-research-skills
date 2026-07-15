# #510 — Executable sprint-contract panel checker (design)

> Issue: #510. Status: settled 2026-07-15 (decision trail in this document §2), revised
> after a cross-model design review (gpt-5.6-sol xhigh, 2026-07-15; 10 P1 + 5 P2 — 9 P1
> accepted in full or reshaped, 1 P1 partially rejected with rationale in §4, 5 P2 accepted).
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
not a correctness gate**: it proves the stated decision (and the synthesizer's stated
fired-condition record) follows from the stated scores under the published rules; it
does not judge whether the scores themselves are right.

## 2. Settled decisions

1. **Mismatch blocks and retries once.** A failed recomputation voids that synthesis;
   the orchestrator re-runs the synthesizer once with the checker's diagnostics. Any
   nonzero result on the second attempt aborts the editorial round. This mirrors the
   existing "internally inconsistent = unusable" handling; log-only was rejected.
2. **Both layers are checked.** Layer 1: each reviewer's own scores → own declared
   fired-conditions → own `## Editorial Decision`. Layer 2: the panel scoring matrix →
   quantifier thresholds → precedence → the synthesizer's declared fired-condition set
   AND emitted decision. The per-reviewer derivability check was already promised in
   protocol §5 and is cheap to include because both layers share the same engine.
3. **Zero-fired fallback is aligned to the design doc.** The v3.6.2 design doc says
   "if no condition fired, emit the accept-grade action"; protocol §8 and the agent
   prompts omit it. All surfaces are aligned in this PR: zero fired conditions ⇒ the
   contract's F0 accept-grade `action` (Schema 13.1 branch 7 pins reviewer-mode F0 to
   `editorial_decision=accept`, so the checker derives the fallback from the contract's
   F0 entry rather than hardcoding a second copy of the string). Reachable: e.g. under
   `reviewer/full.json`, one reviewer warning one mandatory dimension fires neither F0
   nor F1/F2/F3. Applying the same fallback at the per-reviewer layer is a new
   specification (not historical alignment) and is pinned in the reviewer prompts in
   this PR (§5).
4. **The majority formula is a confirmed transcription error and is FIXED in this PR.**
   The v3.6.2 design doc states the formula `⌈N/2⌉ + 1` but every concrete threshold it
   gives (three separate places: `N=5 → 3/5`, `N=4 → 3/4`, `N=3 → 2/3`, plus the §10
   risk-8 "majority: 3 of 5" discussion) is **simple majority `⌊N/2⌋ + 1`**. No surface
   in the repo states a concrete `4/5` anywhere; the live surfaces (protocol §8, the
   synthesizer prompt) copied only the mis-transcribed formula glyph, never the numbers.
   This PR corrects the formula to `⌊N/2⌋ + 1` on both live surfaces and implements it
   in the checker; a tracking issue records the evidence chain for provenance. (An
   earlier draft of this design treated the strict formula as possibly-intentional and
   deferred; the concrete-threshold evidence settled it as a typo.)

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
  validation logic), **plus checker-local hard eligibility checks** (the reused
  functions accept writer/evaluator contracts and only warn on panel oddities):
  `mode` must be a reviewer mode with a §7-published panel mapping
  (`reviewer_full`, `reviewer_methodology_focus`), and `panel_size` must equal that
  mapping's value. Any violation ⇒ exit 2.
- `--report` (repeatable): one Phase-2 reviewer report each. Count MUST equal
  `contract.panel_size`; duplicate resolved paths and byte-identical report contents
  are rejected; the set of declared `contract_role:` values (§ Report parsing) must
  equal the mode's published role set exactly (no duplicates, no unknowns). Violations
  ⇒ exit 2 with `[PANEL-CARDINALITY: ...]` (mirrors the §6 `[PANEL-SHRUNK]` invariant —
  the checker never recomputes against a smaller or forged panel).
- `--synthesis`: the synthesizer's sprint-mode output containing the pinned emission
  block (§5 below). **Required by default.** Layer-1-only verification is an explicit
  opt-in: `--layer1-only` (mutually exclusive with `--synthesis`) accepts **1 to
  panel_size** reports and runs Layer 1 on each — this is the invocation the
  orchestrator can run per reviewer at Phase-2 lint time (protocol §5), before paying
  for a synthesis that would be voided anyway. In `--layer1-only` mode the
  role-set-equality check is relaxed to "each declared role ∈ mode's role set, no
  duplicates among the given reports".

Exit codes (classified by artifact source, because the runtime consequences differ —
§4):

- `0` — pass.
- `1` — synthesis-layer failure: panel recomputation mismatch (decision or declared
  fired-set) OR unparseable/malformed synthesis output. Runtime consequence: retry the
  synthesizer once.
- `2` — contract/infra failure: contract invalid or ineligible, cardinality/role
  violations, unrecognised or semantically invalid expression, unreadable/non-UTF-8
  file. Runtime consequence: abort, no retry.
- `3` — reviewer-report failure: a report is unparseable OR internally inconsistent
  (Layer 1). Runtime consequence: that reviewer is unusable ⇒ `[PANEL-SHRUNK]` abort.

When multiple apply, exit-code precedence is `2 > 3 > 1`. All **independently
computable** diagnostics are printed (a contract parse failure necessarily suppresses
downstream recomputation diagnostics; the promise is scoped accordingly).
Fail-closed throughout: anything unparseable is an error, never a pass.

### Report parsing (strict, format-pinned grammar)

Parsing operates on the report with fenced code blocks (``` ... ```) stripped first,
so example/quoted content can never satisfy or double a required token. Each required
section heading must appear **exactly once** (a duplicated required section ⇒ parse
error). Required tokens are matched as full lines (anchored, case-sensitive,
trailing whitespace tolerated), not as substrings of prose.

From each Phase-2 report the checker reads:

- A pinned role declaration line: `contract_role: <role>` where `<role>` ∈ the mode's
  §7 role vocabulary (`eic | methodology | domain | perspective | da` for
  `reviewer_full`; `eic | methodology` for `reviewer_methodology_focus`). Exactly one.
- `## Dimension Scores` — one `### <Dn>: <name>` subsection per contract dimension,
  each containing exactly one pinned score line `score: <block|warn|pass>`. Missing
  dimension, unknown dimension id, zero or multiple score lines ⇒ parse error.
- `## Failure Condition Checks` — one `### <Fn>` subsection per `failure_conditions[]`
  entry, each containing exactly one pinned line `fired: <true|false>`.
  Missing/unknown/duplicated condition ids ⇒ parse error.
- `## Editorial Decision` — must contain exactly one occurrence of a pinned decision
  line holding one action token from the Schema 13.1 closed enum
  (`editorial_decision=accept | minor_revision | major_revision |
  reject_or_major_revision | reject`). Zero occurrences, more than one occurrence
  (even identical), or any unknown token ⇒ parse error.
- `## Scoring Plan Dissent` — presence is irrelevant to the checker (dissent changes
  how scores were produced, not what they are); parsed only to avoid false section
  matches.

The same grammar is pinned in the reviewer agents' Phase 2 prompt sections (§5), so
generation and parsing share one canonical form.

### Synthesis parsing

The synthesizer's sprint-mode output must contain a pinned emission block (§5):

- One `fired_conditions: [<Fn>, ...]` line — the synthesizer's declared fired set
  (empty list allowed).
- Exactly one pinned decision line `editorial_decision=<action>` (same closed enum and
  exactly-once rule as above).

Both are verified: the declared fired set must equal the recomputed fired set, and the
decision must equal the recomputed decision. This closes the "false intermediate
record, correct final answer" pass-through (a synthesizer whose F2/F3 both map to
`major_revision` could otherwise state a fabricated fired set and still land the right
action). The checker does NOT require the synthesizer to emit the full scoring matrix:
the matrix is recomputed from the reviewer reports themselves, so a synthesizer-emitted
copy would add prompt surface without adding verification power — the fired set + the
decision are the synthesizer's claimed reasoning artifacts, and both are checked.

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

Semantic validation is as hard as syntactic validation:

- An unrecognised expression ⇒ exit 2 with `[EXPRESSION-UNRECOGNISED: condition_id=<F>,
  expression=<...>]` — the same fail-closed behavior the synthesizer prompt mandates.
- A pattern-4 literal referencing a dimension id absent from the contract ⇒ exit 2.
- A priority scope (patterns 1–3) matching **zero** contract dimensions ⇒ exit 2. No
  vacuous truth: `every mandatory ...` over an empty set never fires-by-emptiness.

The parser guesses nothing; new expression forms require the §9-documented PR path
(protocol §9 + synthesizer prompt + this checker move in lockstep — §9's update rule
gains the checker as a third surface).

### Layer 1 — per-reviewer self-consistency

For each reviewer report, with the condition predicate evaluated over **that
reviewer's own scores**. At the single-reviewer layer the cross-reviewer quantifier is
panel-level machinery and reduces to the bare predicate — this rule is currently only
inferable from the agent instruction "evaluate each `failure_conditions` entry against
your `## Dimension Scores`", so this PR pins it explicitly in the reviewer prompts
(§5); the checker enforces only what the prompts state.

- **1a — fired-flag check:** recomputed predicate vs the reviewer's declared
  `fired: true | false`, per condition. Mismatch ⇒
  `[REVIEWER-SELF-INCONSISTENT: reviewer=<file>, condition=<F>, declared=<b>,
  recomputed=<b>]`.
- **1b — decision check:** apply the precedence rule (highest severity among the
  reviewer's declared-fired set; ties by ordinal position; zero fired ⇒ the contract's
  F0 accept-grade action) and compare with the reviewer's `## Editorial Decision`
  token. Mismatch ⇒ `[REVIEWER-SELF-INCONSISTENT: reviewer=<file>,
  decision_declared=<a>, decision_recomputed=<a>]`.

1b runs on the **declared** fired set (that is the §5 "derivable from `## Failure
Condition Checks`" promise); 1a separately pins the declared set to the scores. Both
diagnostics can fire on one report.

**Scope note (deliberate narrowing):** Layer 1 verifies score/fired/decision
self-consistency ONLY. It is a partial, executable supplement to protocol §5 — it does
NOT implement the rest of the §5 Phase-2 lint (required `## Review Body`, dissent
cardinality, the Phase-1 scoring-plan trigger substring check), which remain
prompt/orchestrator-level. The design claims exactly this, no more.

### Layer 2 — panel synthesis recomputation

Per protocol §8, from parsed scores only (never from reviewers' declared fired flags):

1. Build the N-column scoring matrix per dimension.
2. Per condition: evaluate the predicate per reviewer, then apply the quantifier —
   `any`: ≥ 1 of N; `majority`: **simple majority `⌊N/2⌋ + 1`** (N=5 → 3, N=3 → 2;
   N == 2 ⇒ both, collapsing to `all`, as already documented; N == 1 ⇒ vacuous, never
   fires, warning printed — matching protocol §8; the SC-11 validator note is aligned
   to this reading in this PR); `all`: all N.
3. Precedence: highest severity among fired conditions, ties by ordinal position;
   zero fired ⇒ the contract's F0 accept-grade action (§2 decision 3).
4. Compare the recomputed fired set with the synthesizer's declared
   `fired_conditions:` AND the recomputed decision with the pinned decision line.
   Either mismatch ⇒ exit 1 with `[PANEL-SYNTHESIS-MISMATCH: recomputed_fired=<[...]>,
   declared_fired=<[...]>, recomputed=<a>, stated=<a>]`.

## 4. Runtime wiring (protocol §8.1, new)

`sprint_contract_protocol.md` gains §8.1 "Executable recomputation": after the
synthesizer emits its output, the orchestrator runs the checker over the contract, the
N usable Phase-2 reports, and the synthesis output.

- Exit 1 ⇒ void this synthesis, re-run the synthesizer **once**. The checker
  diagnostics are appended to the re-run input **wrapped in a data delimiter**
  (`<checker_diagnostics>...</checker_diagnostics>`, treat-as-data instruction
  included) so file names/expression strings can never act as an instruction channel.
  ANY nonzero exit on the second attempt (1, 2, or 3) ⇒ abort the editorial round with
  `[SYNTHESIS-MISMATCH]` (new §11 tag).
- Exit 2 ⇒ contract/infra protocol violation; abort the round, no retry (a contract or
  cardinality error means the round inputs are wrong; re-prompting an LLM cannot fix
  them).
- Exit 3 ⇒ the offending reviewer is unusable, exactly as §5 already specifies ⇒
  `[PANEL-SHRUNK]` abort. **No synthesizer re-run** — re-synthesizing over an
  inconsistent reviewer report cannot help. (The checker gives that existing rule an
  executable edge; it does not change the rule.) The `--layer1-only` invocation at
  Phase-2 lint time catches this before synthesis cost is paid.

**Enforcement pattern (explicit, addressing the cross-model P1 on runtime wiring):**
ARS has no code-level conductor — orchestration is LLM-driven by design, and the
structured task-envelope layer is deliberately deferred (#134 Slice 3+). The
enforcement layer for this checker is therefore the same as for the existing
`check_sprint_contract.py` §2-step-1 invocation: a protocol-mandated orchestrator
step, plus CI-pinned tests of the checker itself. The cross-model reviewer's request
for an executable caller/hook is acknowledged and rejected as out of architectural
scope; the accepted mitigations are `--synthesis` required by default and Layer-1-only
demoted to an explicit flag, so an accidental partial invocation cannot read as a full
pass.

CI runs the checker's pytest suite (fixtures, no live reports); real-run enforcement is
the orchestrator invocation above.

## 5. Prompt/document alignment (same PR, lockstep)

1. `sprint_contract_protocol.md` — §8 step 2 majority formula corrected to
   `⌊N/2⌋ + 1` (§2 decision 4); §8 step 3 gains the zero-fired accept-grade sentence;
   new §8.1 (runtime wiring); §9 update rule adds the checker as a lockstep surface;
   §11 gains `[SYNTHESIS-MISMATCH]` and the checker's diagnostic tags.
2. `editorial_synthesizer_agent.md` (v3.6.2 protocol block) — majority formula
   corrected; Step 3 gains the zero-fired fallback + the pinned emission block:
   `fired_conditions: [...]` line + the decision stated as the action string verbatim
   on its own line (e.g. `editorial_decision=major_revision`).
3. The five reviewer agents (`eic`, `methodology`, `domain`, `perspective`,
   `devils_advocate`) — Phase 2 step 4 gains: the pinned `contract_role:` line, the
   pinned per-dimension `score:` line form, the pinned `fired:` line form, the pinned
   exactly-once decision line, the bare-predicate rule (quantifiers are panel-level;
   evaluate each condition's predicate against your own scores only), and the
   zero-fired accept-grade rule for deriving the decision.
4. `scripts/check_sprint_contract.py` — SC-11's N=1 wording aligned to "majority at
   N=1 never fires" (§3 Layer 2 note).
5. `academic-paper-reviewer/SKILL.md` — orchestration note pointing at §8.1.
6. `CHANGELOG.md` — `[Unreleased]` entry.
7. `docs/design/2026-04-23-ars-v3.6.2-sprint-contract-design.md` is historical and is
   NOT edited (the tracking issue records the formula-typo evidence instead).

Existing v3.6.2/v3.6.6 lints that count or pin these prompt blocks must stay green;
any lint that pins affected wording is updated in the same commit as the wording.

## 6. Tests

`scripts/test_check_panel_synthesis.py` (pytest, colocated per repo convention), with
fixtures under `tests/fixtures/panel-synthesis/`. CI wiring is **one entry in the
pytest manifest** (`scripts/_ci_pytest_manifest.toml`; the workflow forbids direct
per-file pytest invocations, so no parallel workflow step is added).

- **Positive:** a consistent 5-report `reviewer_full` round (fired set + decision both
  match); a consistent 2-report `reviewer_methodology_focus` round; a zero-fired round
  that correctly states the F0 accept action; a consistent `--layer1-only` single-report
  run.
- **Mutation (each must fail with the right tag AND exit code):**
  - Decision layer: flipped synthesis decision; correct decision with fabricated
    `fired_conditions:` list (must still fail); missing/duplicate decision line;
    missing emission block.
  - Score layer: one flipped dimension score that changes the panel outcome; reviewer
    fired-flag contradicting own scores (1a); reviewer decision contradicting own
    declared fired set (1b); reviewer zero-fired fallback vs panel zero-fired fallback
    (separately).
  - Expression engine: every §9 variant positive; anchored near-misses (case, quote,
    whitespace mutations) rejected; `or worse` at every boundary (`pass`/`warn`/`block`);
    conjunction (`AND`); orphan `Dn` literal ⇒ exit 2; empty priority scope ⇒ exit 2.
  - Quantifiers: `any`; `all`; majority at N=5 (2-of-5 must NOT fire, 3-of-5 MUST fire —
    the corrected simple-majority bar); majority at N=2 (1-of-2 no, 2-of-2 yes);
    majority at N=1 (never fires + warning).
  - Precedence: higher severity wins (independent of ordinal); equal-severity ordinal
    tie-break.
  - Contract eligibility: writer/evaluator-mode contract rejected; mode↔panel_size
    mismatch rejected; schema-invalid contract rejected.
  - Cardinality/roles: report count ≠ panel_size; duplicate report paths; byte-identical
    duplicate contents; duplicate/unknown/missing `contract_role:`.
  - Grammar: missing required section; duplicated required section; unknown dimension
    id; zero/multiple score lines; decoy tokens inside fenced code blocks ignored;
    prose-embedded token not matched (anchored-line rule); non-UTF-8 / unreadable file
    ⇒ exit 2.
  - Modes/exit codes: exit-code precedence (`2 > 3 > 1`); `--layer1-only` accepts 1..N
    reports and never emits Layer-2 verdicts; `--layer1-only` with `--synthesis`
    rejected.

## 7. Non-goals

- The legacy/general 0–100 rubric path (`quality_rubrics.md` /
  `editorial_decision_standards.md`) — contradictory decision authorities; unifying
  them precedes any mechanical check there (per issue #510).
- The v3.6.6 writer/evaluator contract path — parallel machinery, different report
  shapes; out of scope by the issue's own boundary.
- The remaining §5 Phase-2 lint items (Review Body, dissent handling, Phase-1 trigger
  substring check) — prompt/orchestrator-level; Layer 1 is an executable supplement,
  not a replacement (§3 scope note).
- A code-level orchestrator/caller for the checker (#134 territory; see §4 enforcement
  pattern).
- Semantic quality judgment of scores or review bodies — this is a self-consistency
  gate only.
- No new env flags, no schema change (Schema 13.1 untouched), no change when sprint
  contracts are not in use.
