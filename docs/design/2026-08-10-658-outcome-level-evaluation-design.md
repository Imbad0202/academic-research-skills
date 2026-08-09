# #658 — Outcome-level evaluation of ARS-assisted manuscript and process quality

> **Status:** DESIGN-FROZEN / NOT EXECUTED
> **Issue:** #658
> **Scope:** protocol design only; no recruitment, participant contact, model run,
> judging, data collection, or effectiveness claim is authorized by this document.
> **Existing-contract anchor:** `shared/benchmark_report_pattern.md`,
> `shared/benchmark_report.schema.json`, `scripts/check_benchmark_report.py`, and
> `examples/benchmark_report_template.json`.
> **Estimand boundary:** `POSITIONING.md` § "Integrity checks and the empirical-work
> boundary" (#657).

## 1. Decision

The first outcome-level ARS study will be a **matched-pair, parallel, randomized,
active-control study**. Two different eligible researchers in each matched pair receive
the exact same frozen task packet. One is assigned to the exact frozen ARS package; the
other receives the same base model, sources, time, token budget, file access, and
non-ARS tools without ARS prompts or orchestration. There is no crossover.

The primary outcome is a completion-adjusted, blinded external-expert manuscript-quality
score. The primary causal estimand is the intention-to-treat average of individual
potential-outcome contrasts over all randomized participants. The randomized signed
within-pair observed difference is its estimator for the recruited population and realized
frozen-task-packet distribution.

This design measures a bounded manuscript-production package and its reported process.
It does **not** establish that underlying research was executed, that raw data are true or
complete, that an analysis reproduces, or that a scientific conclusion is valid. Even a
positive result cannot license "ARS makes the science better."

The deliverable for #658 is this frozen design. Implementation of the report profile,
recruitment, execution, and publication of a measurement row are separate future work.

## 2. Existing benchmark contract and additive migration

### 2.1 One report family, not a third envelope

Outcome-level reports remain members of the existing ARS-versus-human benchmark-report
family. They do not use or fork the sibling `heldout-measurement/1.1` envelope, whose
subject is tool behavior. They also do not create a third generic measurement standard.

Future implementation adds two optional top-level fields to the existing benchmark
schema:

```json
{
  "benchmark_report_profile": "ars-outcome-evaluation/1.0",
  "outcome_evaluation": {}
}
```

`ars-outcome-evaluation/1.0` is a profile id inside the existing benchmark-report
family, not a new report-contract family. The marker and block travel together. When the
marker is present, the profile block is required and closed (`additionalProperties:
false` recursively). When the block is present, the exact marker is required.

Strict parsing is additive-profile scoped. Before constructing an ordinary JSON object,
a duplicate-preserving lexical pass decodes every **top-level** JSON object member name
(including `\u` escapes) and tests the decoded names for the exact marker key, exact block
key, or a folded spelling of either. Nested legacy content does not opt in. The fold is
NFKC normalization, Unicode format-character
removal, case-folding, and `-`-to-`_` mapping. A match enters the strict profile loader;
fold-colliding names, unknown versions, duplicate JSON keys, non-finite numbers,
misspelled fields, and a marker/block mismatch then fail. Any document selected by that
decoded-name match **or** by required-profile mode must have original bytes that are
strict UTF-8 without a BOM. The future CLI exposes
`--require-profile ars-outcome-evaluation/1.0`; every claimed outcome report must use it,
so deleting or misspelling the opt-in keys cannot fall back to legacy validation. A
completely unmarked legacy document run without that flag continues through the current
parser with its historical behavior. Repository-wide strict-JSON hardening for legacy
reports would be a separate breaking migration, not smuggled into this profile.

### 2.2 Legacy compatibility

The six existing required fields remain required and keep their present meanings:

- `ars_version`
- `task_definition`
- `human_baseline`
- `ars_run`
- `metrics`
- `caveats`

An unmarked legacy report remains valid under the current validator without retrofit,
rewrite, new warnings, or a changed exit code. Legacy validity continues to mean
**disclosure compliance only**. It does not gain causal, outcome, or effectiveness
authority merely because the new profile exists.

`ars_version` remains the software version and is not repurposed as a report-contract
version. Existing `human_baseline` remains the compatibility name for the comparator,
even though the chosen active control may use the same base model as the ARS condition.
The exact comparator is carried by the new profile.

No outcome-evaluation benchmark report may claim conformance until the schema and runtime
validator implement this profile. The current schema's acceptance of unknown properties
is not profile validation.

The completed cohort projects into the six legacy fields exactly as follows; the future
validator cross-checks each projection against the profile rather than accepting two
different accounts of one run:

| Legacy field | Frozen projection for this profile |
|---|---|
| `ars_version` | Exact treatment ARS semantic version; its commit/hashes remain in the profile |
| `task_definition.description` | Fixed description of the six-packet bounded empirical-report task |
| `task_definition.task_type` | `outcome-gradable`; the frozen 0–100 expert rubric makes this the existing contract's rubric-scored branch |
| `task_definition.outcome_gradable` | `true`; this says the task has a declared scoring outcome, not that the rubric is objective ground truth |
| `human_baseline.sample_size` | Number assigned to CONTROL at randomization, including noncompletion and later withdrawal counts |
| `human_baseline.author_independence` | `third-party-conducted`; participants are independent recruits, not benchmark authors |
| `human_baseline.hours_spent` | Sum of recorded active participant hours in CONTROL; the profile also reports mean/spread |
| `human_baseline.recruitment` | Exact cohort recruitment description and registry/protocol reference |
| `human_baseline.tools_allowed` | Exact active-control allowlist, including the frozen base model |
| `ars_run.hours_spent` | Sum of recorded active participant hours in ARS; the profile also reports mean/spread |
| `ars_run.cost_usd` | Direct ARS-arm model/tool charges only; compensation and shared study costs remain separately itemized in the profile |
| `ars_run.skills_used` | Exact loaded ARS workflow/skill ids |
| `ars_run.data_access_level_declared` | `raw`; the exact ARS chain directly consumes packet/source bytes that have not passed an upstream integrity gate. The profile cross-checks the same dirtiest declared access level for both arms; rights clearance or a closed packet does not promote it to `verified_only` |
| `metrics.*` | The primary contrast projection defined in §2.3 |
| `caveats` | At minimum the finite population/packet/version scope, #657 boundary, missingness state, and blinding-integrity state |

Randomized, retained, submitted, and scored counts remain distinct in the profile. Neither
legacy `sample_size` nor a retained count may be substituted for the randomized control
count.

### 2.3 Scorer compatibility projection

The current `metrics.scoring_independence` enum conflates two independent questions:
who scored, and what they were blinded to. It remains as a lossy compatibility
projection. A conforming completed study records the authoritative facts under the new
`judging` block:

- stable pseudonymous judge identity and expertise role;
- independence and conflict declarations;
- exact `blinded_to` dimensions;
- masking procedure and artifact hashes;
- raw score lock and adjudication history;
- post-score condition guess and confidence.

For the chosen protocol, the legacy projection is `blind-scored` when condition labels
were withheld as specified. A failed blindness check does not rewrite that historical
fact; it is recorded separately as `blinding_integrity=compromised` and lowers the claim
ceiling.

For a completed report with at least one complete observed pair, the legacy primary metric
projects the new primary contrast:

```text
metrics.primary_metric = mean_paired_difference_completion_adjusted_quality_0_100
metrics.primary_metric_value = the reported ARS-minus-control estimate
```

The profile migration broadens the base field to `number | null`, then conditionally
requires a number for every unmarked legacy report. For this exact profile, `null` is
required iff no complete observed pair exists and `hat_tau_obs` is therefore unavailable;
otherwise the number must equal `hat_tau_obs`. This lets a terminated zero-complete-pair
study publish a schema-valid profile report without fabricating an estimate and does not
change any legacy-valid instance.

The new profile, not these two compatibility fields, carries the estimand, uncertainty,
missingness, and claim authorization.

## 3. Research question, target population, and estimand

### 3.1 Primary research question

Among eligible researchers completing bounded, frozen manuscript-production tasks, what
is the intention-to-treat difference in completion-adjusted blinded manuscript-quality
score between assignment to an exact ARS release and assignment to an otherwise
resource-matched base-model active control without ARS?

### 3.2 Target population

The smallest credible study targets adult researchers working in empirical
social/behavioral science who:

1. can lawfully consent and write the study's output language;
2. have documented experience producing or revising scholarly manuscripts;
3. meet a task packet's declared subject-area eligibility;
4. have not previously used ARS or read the frozen ARS materials;
5. are not an ARS maintainer, contributor, protocol designer, packet designer, judge,
   data steward, or close collaborator/supervisor of those roles;
6. have no coauthor, supervisor/student, direct-report, laboratory-team, or active-project
   relationship with another enrolled participant; and
7. agree that, until every confirmatory participant output and process log is locked, they
   will not share or discuss any packet, interface, condition instruction, ARS material,
   or control guidance with any study candidate or enrolled participant.

Each participant completes exactly one task. A person may occur in only one matched pair
and one arm. This keeps the participant, assignment, and produced-manuscript units
one-to-one and avoids within-person learning and clustering.

Recruitment checks the evolving participant roster before enrollment; a tied later
candidate is ineligible. Prior exposure to any confirmatory packet or condition material
also makes a candidate ineligible. A discovered communication or spillover violation
stays in intention-to-treat, is reported as contamination, and blocks Level 3 rather than
being repaired through exclusion.

The inference population is the recruited population meeting these criteria. It is not
all scholars, disciplines, languages, manuscript types, or future ARS versions.

### 3.3 Exact primary estimand

Let `Y_pi(1)` be participant `i` in randomized pair `p`'s completion-adjusted quality
score under the frozen ARS condition and `Y_pi(0)` the score under the active control.
For `P` assignment-released pairs, the primary finite-sample causal estimand is the average
treatment effect over **all randomized participants**:

```text
tau_ITT = (1 / (2P)) * sum_p sum_(i in p) [Y_pi(1) - Y_pi(0)]
```

The observed signed within-pair mean in §8.3 is the randomization-based estimator of this
estimand; it is not itself the estimand. Withdrawal, administrative loss, or a missing
judge record does not remove a randomized participant from `tau_ITT`. It makes an assigned
outcome unobserved and activates the deterministic contrast bounds in §8.4.

A pair enters this set irreversibly when the allocator releases its arm assignments and
an append-only release ledger binds the pair id, canonically ordered participant ids,
packet id, sequence position, assignment, predecessor-ledger digest, release time, and
proof against the preregistered sequence commitment. Release cannot be retroactively
relabeled as "not randomized." A missing or inconsistent proof is an
allocation-integrity breach: the pair remains in reporting and bounds, but Level 3 is
blocked because causal assignment authority was not established.

The target is conditional on:

- the recruited participant pool;
- the packet distribution actually assigned among the randomized pairs;
- the exact ARS commit and skill hashes;
- the exact base-model build and inference configuration;
- the common time, token, source, and tool envelope; and
- the frozen judging rubric and masking procedure.

This is a package-effect estimand. It is not a per-stage effect and is not transportable
to a different model, ARS version, packet distribution, or population without a new
study or an explicitly justified replication.

## 4. Primary comparison design

### 4.1 Frozen task packets

Before registration, the study freezes six task packets. The allocation schedule cycles
through packets and plans six matched pairs per packet, giving 36 randomized pairs at the
enrollment cap. The primary estimand weights every assignment-released participant/pair
equally; it does not reweight packets. If an institution-owned early stop leaves a
different realized packet mix, that mix becomes part of the finite randomized target and
is reported exactly. Packet-standardized or equal-packet estimates are secondary
sensitivity analyses only and may not replace the primary after outcomes are seen.

The six packets are all bounded empirical-report tasks in the same output language:
two quantitative, two qualitative, and two mixed-methods packets. Each begins with a
fixed research question; research-question formation is therefore outside the primary
study. Every packet has a stable ASCII id and contains only rights-cleared or explicitly
permissioned material:

- a bounded scholarly task brief;
- one exact fixed research question;
- a closed source/evidence corpus with a file inventory and SHA-256 per file;
- any methods, results, tables, or figures the task permits the writer to use;
- a common venue-neutral specification for a 2,500–4,000-word research report;
- a common condition-neutral manuscript template;
- the permitted tools/data-access matrix; and
- packet-specific judge expertise criteria.

The task output is a bounded research-report manuscript that can be completed within six
active hours. All packets exercise evidence synthesis, drafting, and revision as one
composed production chain; none exercises original study execution or RQ formation.
Packet content may represent a synthetic or permissioned study record, but
the packet must label that status. It contains no unconsented identifiable participant
data, private raw data, credentials, live retrieval instructions, or claim that the
represented study actually occurred.

The exact UTF-8 packet bytes, inventory, rights/permission receipts, and manifest are
hash-pinned before recruitment. Both members of a pair receive byte-identical packets.
The primary report names the finite packets; it does not generalize beyond them.

### 4.2 Matching and allocation

Participants are matched within packet before randomization using only pre-outcome facts:

- subject-area eligibility;
- career-stage band;
- prior experience with the frozen base-model family;
- a brief neutral writing-calibration score assessed without ARS; and
- output-language proficiency band.

The exact matching algorithm, tie rule, covariate order, and calibration rubric are part
of the preregistered bundle. Pair formation occurs before condition assignment.

An independent statistician or allocation service creates a computer-generated 1:1
sequence. The allocation algorithm, full sequence commitment, and consumption rules are
registered before recruitment; the unrevealed sequence is access-controlled. The
generator/allocator cannot see participant covariates, calibration, manuscripts, or
outcomes, while the enrollment service, recruiters, matchers, packet assessors, and
intervention operators cannot inspect any future sequence value.

The registered mapping is mechanical. An independent enrollment service issues each
stable pseudonymous participant id from its monotonic signed enrollment receipt before
calibration or matching; ids cannot be chosen, edited, or reissued. Within a pair, those
ids are ordered by unsigned ASCII byte order; the sequence bit assigns ARS to the first or
second id. After consent, eligibility, calibration, matching, packet binding, and the
common window are locked, an automated `PAIR_READY` event receives a unique monotonic event
number. Pairs consume the strictly next unused sequence position in event-number order.
No actor may skip, reuse, swap, select, or backfill a position. A cancellation before
`PAIR_READY` consumes nothing. At `PAIR_READY`, position consumption, proof append, and
assignment release are one atomic event; there is no reserved-but-unreleased state. Any
later cancellation leaves that pair in intention-to-treat with its outcome bounded under
§8.3, and the position is never recycled or replaced. The exact sequence has 36 usable
positions, so a released cancellation reduces complete outcomes rather than authorizing a
37th pair. The release proof binds both ordered participant ids, the `PAIR_READY` event,
predecessor-ledger digest, position, bit, assignment, packet, and sequence-commitment
proof.

Each pair's common start/deadline window is also locked before assignment is revealed.
Both participants receive six active hours inside the same 48-hour UTC window and the
same attested model endpoint/build. If call records cannot establish the common build and
window after randomization, the affected outcome is administrative missing under §8.4;
the report cannot call that pair an exact matched-envelope observation.

There is no crossover, washout, reassignment, or participant-selected arm. A participant
who does not follow the assignment remains in the assigned arm for primary analysis.

### 4.3 Treatment and active control

| Surface | ARS condition | Active control |
|---|---|---|
| Participant role | Human researcher retains every research-state decision | Same |
| Base model | Exact preregistered provider/model/build | Same exact provider/model/build |
| Inference settings | Exact preregistered settings | Same settings |
| Task packet and sources | Exact pair-bound bytes | Same exact bytes |
| Active task time | Six hours maximum | Six hours maximum |
| Total billed token ceiling | Same preregistered ceiling, including system/context overhead | Same ceiling |
| File and non-ARS tool access | Frozen allowlist | Same allowlist |
| Output template | Same condition-neutral template | Same template |
| Orchestration | Exact frozen ARS package and named workflow | Neutral interface; no ARS files, prompts, routing, or copied ARS guidance |
| User prompting | Participant may interact within assigned interface | Same freedom within neutral interface |

The active control isolates the incremental package effect of ARS relative to ordinary use
of the same base model under the same resource envelope. It is not a no-AI or unaided-human
arm. Any later no-model comparison is a separately powered secondary study, not an
unplanned third arm.

The ARS prompt/context overhead counts against the common token ceiling because it is part
of the package. Actual active time, wall time, model calls, tokens, and direct cost are
recorded for both arms and never normalized after the fact.

### 4.4 Intervention version and adherence

The preregistered intervention record freezes:

- ARS semantic version, Git commit, and hashes of every loaded skill/reference/template;
- workflow/mode and every user-visible checkpoint;
- base-model provider, exact model id/build, context length, temperature, seed support,
  tool configuration, and retry rule;
- execution environment and interface version;
- prompt/context and output token ceilings;
- packet and source hashes;
- session reset and cache policy; and
- the neutral control instruction and proof that no ARS repository content is mounted in
  the control environment.

Minimum intervention adherence is use of the assigned interface, exact version record,
retained call/event log, and completion of every mandatory human checkpoint. Minimum
control adherence is use of the neutral interface with no ARS material. Both arms record
off-protocol model/tool use, participant communication, extra sources, time overruns,
environment failures, and packet exposure.

Adherence never controls primary inclusion. The primary analysis is intention-to-treat;
a per-protocol analysis is secondary and labels every exclusion rule in advance.

If the model, ARS bytes, task packet, or resource envelope changes, new enrollment stops.
An append-only amendment creates a new cohort boundary. Different intervention versions
are never silently pooled into the primary estimate.

## 5. Rejected alternatives and residual contamination

| Design | Decision | Reason |
|---|---|---|
| Same-author crossover | Rejected | ARS strategies and packet knowledge cannot be washed out; the second period inherits learning and prompt habits. |
| Fixed control-then-ARS order | Rejected | Treatment is inseparable from period, practice, fatigue, and first exposure. |
| Single-arm before/after revision | Rejected | Maturation, review exposure, regression to the mean, and elapsed time can mimic improvement. |
| Unmatched author-owned manuscripts | Rejected for the primary | Topic, baseline quality, author skill, coauthor input, and study type differ with condition. |
| Historical or prior-version controls | Rejected | Model, source access, interface, and time-period drift remain uncontrolled. |
| Unblinded maintainer scoring | Rejected | It is both evaluator dependence and expectancy bias. |
| Chosen matched-pair parallel design | Adopted | Same packet and resource envelope, different matched authors, concealed within-pair allocation, and external blinded judging. |

The adopted design still has residue. Matching cannot make two people identical; a finite
packet library is artificial; ARS structure or prose may reveal condition; participants
may communicate; a base provider may drift behind a stable model id; and task performance
may not transport to the participant's own manuscript. These are reported as limitations,
not repaired by post-hoc exclusions.

## 6. Outcomes and proxy gaps

### 6.1 Primary: completion-adjusted blinded quality

The primary outcome ranges from 0 to 100.

- The required submission is one non-empty, strict-UTF-8 Markdown artifact. A blinded
  mechanical preflight checks only on-time receipt, strict decoding, non-empty body, and
  parseability. Word-count, section, citation, prose, and scientific-quality defects do
  not make an artifact unevaluable; every mechanically parseable non-empty artifact goes
  to the judges and loses points only through the frozen rubric.
- A mechanically evaluable artifact is assigned to three eligible blinded human experts
  using a preregistered anchored rubric.
- The artifact score is the arithmetic mean of exactly three complete, valid raw expert
  composites after the blinded reserve rule in §8.4. If a planned slot remains missing,
  its unknown composite stays bounded on `[0,100]`; two ratings cannot be promoted to an
  exact primary score. Judge ratings are measurement repetitions, not additional
  participant observations.
- A rating disqualified by the closed conflict rule remains published as raw history but
  is replaced, not co-averaged, in the primary composite as specified in §10.4.
- No artifact, an empty artifact, invalid UTF-8, or an artifact that cannot be parsed by
  the frozen preflight at the deadline because of participant action, assigned-package
  failure, or ordinary model/tool behavior receives `0`.
- A study-caused failure or consent withdrawal follows §8.4 and is not silently converted
  into either zero or a deletion chosen after scores are seen.

The frozen rubric has five equally weighted 0–20 domains:

1. claim scope and evidence calibration;
2. source/citation traceability and claim-source alignment against the supplied corpus;
3. methods/results reporting completeness and internal consistency against the packet;
4. discussion, limitation, and uncertainty calibration; and
5. organization, clarity, and appropriate transparency/provenance disclosures.

The composite is the sum of the five domain scores. No domain may be dropped, reweighted,
or marked not applicable after registration. Judges assess what the manuscript reports
against supplied packet evidence. They do not certify the truth of the packet, actual
execution, raw data, scientific validity, or reproducibility.

### 6.2 Secondary and exploratory outcomes

| Outcome | Status | Defensible proxy | Does not establish |
|---|---|---|---|
| Submission by deadline | Exploratory secondary | Bounded task completion under the assigned package | General productivity or long-run publication speed |
| Blinded quality among submitted artifacts | Exploratory secondary | Conditional manuscript quality when an artifact exists | ITT benefit; conditioning can select different participants by arm |
| Independently detected integrity/reporting defect count | Exploratory secondary | Detectable defects under the frozen audit rubric | Absence of hidden defects or valid underlying science |
| Neutral process-trace completeness | Exploratory secondary | Whether declared goals, evidence use, decisions, and final checks are traceable | Quality of unobserved reasoning or actual research execution |
| Active time, wall time, tokens, and direct cost | Exploratory | Resource use in this exact environment | Future prices, other models, or total institutional cost |
| Participant workload and usability | Exploratory | Experience in this bounded task | Manuscript quality or research validity |
| Intermediate synthesis/draft/revision artifacts | Descriptive only | Observable artifacts produced during the assigned package | Causal effect of an individual pipeline stage |
| Judge condition guesses and confidence | Blinding diagnostic | Detectability of condition cues | Proof of successful blinding or a treatment effect |

The defect audit preserves raw flags and any adjudication separately. Adjudication cannot
overwrite raw primary scores. The neutral process log is identical across arms and asks
only for goals, consulted packet evidence, adopted/declined changes with reasons, and a
final check; it does not embed ARS-specific guidance in the control condition.

## 7. Judges, independence, and blinding

### 7.1 Judge eligibility and conflicts

Every artifact receives three ratings from three distinct stable human identities. Every
judge must meet the packet's minimum domain and methods/reporting qualifications; at least
one of the three must additionally qualify as a scholarly-integrity specialist. A judge
cannot be:

- an ARS agent or model output;
- the maintainer or an ARS contributor;
- a participant, protocol designer, packet designer, packet/calibration assessor,
  recruiter, data steward, process auditor, analyst, or adjudicator in this study;
- an author, coauthor, supervisor, student, employee evaluator, or recent close collaborator
  of a participant; or
- financially or professionally dependent on the study result.

Judge identity may be pseudonymized in the public dataset, but an accountable institution
holds the identity, qualification, compensation, and conflict record. Conflicts are
declared and resolved before a judge sees an artifact or allocation key. Replacement uses
a preregistered reserve pool and the same assignment algorithm.

Until their raw score and guess records are locked, judges may not discuss an assigned
artifact with another judge, view another judge's score/comment/guess, or participate in
calibration using any confirmatory artifact. Calibration uses separate frozen examples.

### 7.2 Condition-neutral production and deterministic masking

Both arms write into the same required section skeleton and output format. After lock, one
deterministic, hash-pinned canonicalizer is applied identically to all artifacts. It may:

- strip file metadata and author identifiers;
- normalize typography, margins, page headers, and file naming; and
- apply an opaque artifact id from the steward's sealed mapping.

The steward generates the opaque-id mapping and commits its hash before opening any
submitted artifact. Given the input bytes and committed mapping, the canonicalizer is
deterministic. It may not paraphrase, summarize, reorder, delete, add, or rename substantive text,
headings, citations, numbers, tables, or figures. Input/output hashes and a transform log
are retained. A human masking operator may verify execution but may not edit content.

The independent data steward holds the condition, pair, participant, and packet mapping.
Judges receive no condition label, participant identity, ARS log, process log, partner
artifact, or study hypothesis. Before any artifact is opened, a hash-pinned incidence
schedule assigns three distinct qualified identities to every artifact. Each judge sees
at most one artifact per packet, never both outputs from a matched pair, and has masked
`A/B` arm counts differing by at most one across all assignments. The schedule contains
at least 36 judge identities and must make the pair/arm design matrix full rank; reserve
replacement preserves these rules. Balancing uses only opaque ids, packet qualifications,
and masked `A/B`, not scores or the `A/B -> condition` key.

### 7.3 Raw-score lock and blindness check

Judges complete all domain scores and comments before condition guessing. The scoring
system then locks and hashes the raw record. Only afterward does each judge record:

- `condition_guess = ARS | CONTROL | UNSURE`;
- confidence on a frozen scale; and
- optional cue category from a closed list.

No guess can change, exclude, or reweight a score or judge. After every raw score is
locked, the analyst receives opaque `A/B` arm labels plus pair/packet structure, runs the
frozen analysis, signs and hashes its complete output, and only then receives the
mechanical `A/B -> ARS/CONTROL` mapping for relabeling. The report publishes guess
accuracy, `UNSURE` frequency, confidence, and uncertainty with the primary result.

The frozen diagnostic scores each guess as `1` when correct, `0` when incorrect, and
`0.5` for `UNSURE`; a missing planned guess is recorded as `UNSURE`, never dropped. It
first averages the three planned guess scores equally within each judged artifact, then
averages available artifact statistics equally within pair, and finally averages pairs
equally. Thus rating availability cannot reweight artifacts or pairs.

With guesses, judge assignment, artifacts, and missingness held fixed, the diagnostic
performs 10,000 within-pair treatment-label permutations under a preregistered seed and
compares the observed statistic with that one-sided randomization distribution. Ties
count in the numerator: `p = (1 + count(T_perm >= T_obs)) / 10001`. This preserves
repeated-judge and artifact dependence without treating guesses as independent. It is
`unassessable` when any evaluable artifact's planned guess record is missing or fewer than
32 pairs have at least one judged artifact. The descriptive statistic still uses `0.5`
for a missing guess, and the locked score remains valid without replacement, but missing
guess data can never produce a blindness claim. Otherwise, a direct allocation leak, or
`p <= 0.05` together with an observed statistic above `0.5`, sets
`blinding_integrity=compromised`; all other assessable cases are
`blinding_integrity=no_detectable_compromise`, never proof that blinding succeeded.
Decisive-guess accuracy and `UNSURE` frequency are also reported separately. A
`compromised` or `unassessable` state blocks the ordinary Level 3 blinded-quality claim.

## 8. Statistical analysis

### 8.1 Units and aggregation

- **Randomization unit:** participant.
- **Design block:** matched participant pair bound to one task packet.
- **Produced artifact:** one manuscript per participant.
- **Primary point-estimate contribution:** one within-pair difference after exactly three
  judge ratings for each evaluable artifact have been averaged.
- **Uncertainty rows:** individual rating composites, with matched-pair and repeated-judge
  cluster identities preserved for the primary two-way covariance.
- **Judge ratings:** repeated measurements only; they never increase participant `n`, and
  a judge reused across packets is never treated as an independent pair.
- **Task packets:** a finite six-packet set with planned balance; every randomized pair is
  equally weighted, and packet-stratified/standardized results are secondary.

The report gives participant, pair, packet, artifact, judge, and exact/bounded counts
separately. It never reports `3 × artifacts` as the study sample size.

### 8.2 Sample size and precision target

The fixed enrollment is **36 matched pairs / 72 participants**: six assignment-released
pairs for each of six packets. Every pair remains in the target. Level 3 requires exact
assigned outcomes for all 36 pairs; a smaller complete subset cannot become the
claim-bearing cohort.

The frozen precision target is a two-sided 95% primary-interval half-width no greater than
`5.0` points on the 0–100 outcome scale. The primary interval is the crossed
pair-by-human-judge interval in §8.3, with the pair component also carrying structural
zeros; it is not an ordinary independent-pair interval. The familiar reference
`t(0.975,35)/sqrt(36) = 0.3384` paired-difference SD is reported only as a no-crossed-
dependence planning diagnostic and has no claim-gate authority. This design makes no
power, minimum-detectable-effect, equivalence, or non-inferiority promise.

Before recruitment, a checked-in deterministic calculator must reproduce the reference
calculation, the exact judge-incidence matrix, the two-way covariance on synthetic
fixtures, its degrees of freedom, and the five-point gate. The registered output reports
any simulation grid and assumptions; no favorable simulation result substitutes for the
realized crossed interval. A half-width above five, a negative/undefined estimated
variance of `beta`, rank failure, fewer than 36 exact pairs, or any missing assigned outcome produces
`INCONCLUSIVE_IMPRECISE`. Recruitment is never extended after outcomes are inspected.
Pilot variance cannot change this version's enrollment, precision gate, primary outcome,
or favorable direction, and pilot participants or packets are never pooled into it.

### 8.3 Primary estimator and uncertainty

For each pair whose two assigned artifact outcomes are exact, define
`D_p = Y_p,assigned-ARS - Y_p,assigned-CONTROL`. The observed-data point estimator is
`hat_tau_obs = mean(D_p)` over those exact pairs. If none exists it is unavailable, not
zero. With all 36 assigned outcomes exact, it is the randomization-based point estimator
of `tau_ITT`.

The primary 95% interval accounts for the fact that judges are reused across packets.
Every exact artifact contributes exactly three analysis slots: an evaluable artifact
contributes its three raw rating composites; a mechanically determined completion zero
contributes three zero-valued structural slots. Thus each arm keeps equal artifact weight
without pretending that a non-submission was human-scored. Structural slots have no judge
id and never create a judge cluster or degrees of freedom. On all slot rows, the
frozen analysis fits ordinary least squares

```text
R_pr = alpha_p + beta * assigned_ARS_pr + error_pr
```

with one fixed intercept per exact pair and six rows per pair (three ratings per arm).
`beta` equals `hat_tau_obs`. Its primary covariance is the
two-way Cameron–Gelbach–Miller cluster sandwich
`V_pair,all(CR1) + V_judge,human(CR1) - V_pair×judge,human(CR1)`. The pair component uses
all slot rows. The judge and intersection components use only human-rated rows grouped by
stable human judge id; structural zeros enter neither component. For design matrix `X`, residuals `u`,
`N` rating rows, rank `K`, and `G` clusters, the frozen correction is
`CR1(G) = [G/(G-1)]*[(N-1)/(N-K)]*(X'X)^-1*Σ_g(X_g'u_g u_g'X_g)*(X'X)^-1`.
The two-sided interval uses `df = min(number_of_exact_pairs - 1,
number_of_contributing_human_judges - 1)`. A negative/undefined estimated variance of
`beta`, rank-deficient design, or fewer than two clusters on either dimension is reported
and cannot authorize Level 3;
the variance is never clipped to zero. This crossed interval—not an ordinary paired-`t`
interval—is primary. A within-pair randomization test and a judge-fixed-effect model are
prespecified robustness analyses and cannot replace it according to favorability.

For every assigned participant the report constructs an outcome interval `[A,B]` on the
closed `[0,100]` range. A participant-behavior/package-failure zero is `[0,0]`; three
complete valid ratings give `[mean(r1,r2,r3), mean(r1,r2,r3)]`; `q < 3` valid ratings with
missing planned judge slots give
`[sum(r_observed)/3, (sum(r_observed) + 100*(3-q))/3]`; and a legally unavailable or
administratively missing artifact is `[0,100]` unless narrower retained information is
lawfully usable. Pair and cohort bounds are then:

```text
[L_p, U_p] = [A_ARS - B_CONTROL, B_ARS - A_CONTROL]
[L, U] = [mean_p(L_p), mean_p(U_p)] over every assignment-released pair
```

The primary report carries `hat_tau_obs` and its exact-pair crossed interval together with
`[L,U]`, explicitly labeled as bounds on the **realized assigned-outcome statistic under
missing data**, not identification bounds for the causal potential-outcome estimand. It
reports no single all-pair point estimate when `[L,U]` is non-degenerate. Because this
protocol freezes no causal missing-data model, any non-degenerate bound blocks Level 3
even when `L > 0`; missingness cannot be converted into a directional causal claim.

The analysis also reports every exact pair difference, packet-stratified and equal-packet
sensitivity estimates, judge-fixed-effect and packet-adjusted sensitivity models, and
inter-rater spread/reliability. None can replace the frozen point estimator, crossed
interval, or all-pair bounds according to favorability.

### 8.4 Exclusions, missingness, and failures

Eligibility and exclusion rules are applied before randomization. After randomization:

- nonadherence, contamination, time overrun, ordinary model failure, and participant
  non-submission remain in intention-to-treat; an absent evaluable artifact is `0`;
- a participant withdrawal is handled according to the consent and institutional record.
  If data must be destroyed, its assigned outcome is missing and enters the exact
  pair-contribution bounds in §8.3. After the frozen A/B analysis is hashed and mechanically
  relabeled, withdrawal/missing counts are published by assigned arm and packet;
- no pair is voided, excluded, or replaced after assignment release. Before release, a
  common-envelope failure may cancel an unrandomized pair. After release, the closed
  administrative-missing codes are `PACKET_BYTES_MISMATCH`,
  `COMMON_MODEL_BUILD_UNATTESTED`, `STUDY_PLATFORM_OUTAGE`, and
  `STUDY_STORAGE_LOSS`. An operations owner blinded to assignment/condition, every
  participant-output byte, artifact content, process/adherence/model logs, judge records,
  and all scores records the code; affected outcomes enter the §8.3 bounds. A failure of
  ARS itself is treatment behavior, not administrative loss;
- judge loss means that a planned judge slot has no complete locked five-domain score and
  comment record by its preregistered deadline. A missing condition guess is recorded as
  `UNSURE` under §7.3 and never invalidates, drops, or replaces an otherwise valid score.
  Conflict disqualification and replacement follow the separate closed §10.4 rule.
  Partial/raw records remain immutable.
  A reserve-assignment owner who sees only opaque artifact id, packet qualification, slot
  status, and deadline—not arm, content, logs, or any score—uses the frozen assignment
  rule before unmasking. Any slot still missing contributes its exact `[0,100]` term in
  §8.3; Level 3 requires all three valid independent ratings for every evaluable artifact;
  and
- no output, participant, pair, packet, judge, or domain is removed because its value is
  inconvenient or an outlier.

The complete-pair estimate is never presented without the all-pair bounds. Multiple
imputation, complete-case-only claims, and favorable-case substitution are exploratory at
most. Any non-degenerate primary bound blocks a directional benefit claim.

### 8.5 Multiplicity

There is exactly one confirmatory primary outcome, contrast, and favorable direction.
There are no confirmatory secondary outcomes, so this protocol has no additional
hypothesis family to adjust. Every outcome in §6.2 receives descriptive estimates and
intervals without confirmatory p-value, pass/fail, benefit, or causal language. Subgroups,
packets, stage artifacts, adherence, and per-protocol analyses are likewise exploratory.
Promoting any of them creates a new protocol version with its own outcome definition,
multiplicity rule, precision calculation, and design review; it is not an amendment to
this primary family.

### 8.6 Stopping and amendments

There is no efficacy, futility, variance, or favorable-trend interim look. Enrollment ends
at 36 randomized pairs. It may stop earlier only for:

- an institution-owned authorization or safety decision;
- a privacy/security incident;
- loss of the frozen intervention or comparator that prevents exact execution; or
- inability to continue within the registered resources.

The stop owner cannot see assignment/condition, participant-output bytes,
process/adherence/model logs, judge/auditor records, guesses, or scores. Safety and
institutional authorities may access what their duties require, but any such pre-decision
access is logged and automatically blocks Level 3 for the terminated cohort; safety is
never withheld to preserve inference. Early termination, cause, accrued count, access
history, and all legally publishable observations are reported. An early stop does not
authorize a benefit, equivalence, or non-inferiority claim.

## 9. Per-stage identifiability

The primary assignment changes the package as a whole. Intermediate artifacts do not
identify the causal contribution of a stage.

| Stage | Primary study status | What would identify a stage effect later |
|---|---|---|
| Research-question formation | Fixed by every packet; not exercised or identified | New parallel randomization with the same broad brief and constraints, with all later inputs held out of the stage outcome |
| Literature synthesis | Composed into the package effect | New parallel randomization using the same fixed RQ and corpus |
| Drafting | Composed into the package effect | New parallel randomization using the same RQ, evidence matrix, methods/results packet, and output brief |
| Revision | Composed into the package effect | New parallel randomization using the same draft, reviewer comments, claim register, and evidence packet |
| Bounded manuscript-production chain from fixed RQ/evidence to report | Identified only for the frozen packet mixture and package version | Replication under a new population/version is needed for transport |
| Full research-to-paper end to end, including RQ and empirical execution | Not exercised or identified | A separately governed study with a new estimand; this protocol cannot supply it |
| Actual study design/execution, raw-data truth, reproducibility | Not observed and not identifiable | Independent empirical, institutional, and reproducibility work outside ARS manuscript checking |

An end-to-end null is not evidence that every stage is equivalent. A favorable intermediate
score is not a stage effect. A separately randomized stage effect is not evidence of an
end-to-end benefit. These interpretation rules are part of the claim gate, not caveats a
writer may omit.

## 10. Human-participant governance

### 10.1 Institution-owned determination and authorization

This document does not select an Exempt, Expedited, Full Board, or equivalent pathway.
ARS does not infer a pathway from location, affiliation, packet content, or the bounded
authority registry. Before recruitment or data collection, the responsible institution
must provide a written determination and any required authorization. The submission and
written response explicitly cover confirmatory writers, pilot participants, human judges,
and human process auditors because the study collects their identities, work products,
ratings, guesses, confidence, conflicts, or audit records. Judge/auditor recruitment and
scoring cannot begin before that record exists. If the institution determines a role is
staff/service activity rather than a human-subjects pathway, that role-specific written
classification is retained; ARS does not assume it. The determination also addresses
collaborating sites, compensation, confidential manuscripts, model-provider data flow,
and publication/reuse.

Until that external record exists, the study carries the #665 boundary exactly:

```text
Review pathway: institutional determination required
Submission readiness: unresolved
Authorization status: not_provided
Review timeline: unknown — obtain current institutional estimate
```

Readiness and authorization remain independent. `no_listed_gaps_located` cannot promote
authorization. A future study may record `authorization_status=documented` only by
copying the caller-supplied institutional reference; ARS does not derive it.

> **Human-subjects boundary:** This output does not authorize recruitment, consent,
> access to identifiable data, intervention, or data collection.

Where #666 authority profiles are used, selection must be author-declared and exactly
replay-validated; every shipped profile is a bounded subset. The profile registry has no
pathway catalog, definition, or trigger set, so it cannot supply a pathway name for this
study.

### 10.2 Consent, confidentiality, and withdrawal

Institution-approved, role-appropriate materials for every human data contributor
(writers, pilot participants, judges, and process auditors) must state:

- purpose, procedures, assignment, model/tool exposure, duration, foreseeable risks, and
  lack of guaranteed direct benefit;
- voluntary participation, unconditional withdrawal, and the exact effect of withdrawal
  on already collected data;
- what manuscript/task/process/model-log data are collected and which third parties may
  process them;
- that compensation is prorated at the same institution-approved fair rate in both arms,
  is not conditional on output quality or favorable results, and is retained for completed
  time after withdrawal;
- confidentiality limits and publication/reuse choices; and
- contacts for the research team and responsible institution.

Judge and auditor materials additionally state how ratings, guesses, confidence, conflict
records, expertise metadata, and pseudonymous identifiers will be analyzed and published;
their compensation is independent of condition, score direction, or agreement with the
study team.

Real unpublished manuscripts cannot enter a task packet without separate written rights-
holder permission for study use, judge access, derived-output publication, and the stated
reuse scope. Participant consent is not a substitute for a manuscript owner's permission,
and one coauthor cannot silently grant every coauthor's rights.

### 10.3 Storage, access, retention, and destruction

Confidential packet bytes, participant identities, allocation keys, raw prompts/outputs,
process logs, auditor records, judge identities/ratings/guesses, and conflict records are stored encrypted in an
institution-controlled environment. Role-separated access is frozen:

- recruiters: identity/eligibility, not outcomes;
- intervention operators: assignment only after lock, not judge data;
- masking steward: artifact and mapping, not participant compensation decisions;
- judges: masked artifacts only;
- analyst: masked A/B data until the signed analysis output is hashed; and
- an accountable custodian: the re-identification key and institutional records.

Before recruitment, the institution supplies and the registered bundle freezes one row for
each data class—identity/contact, allocation key, manuscript/packet, prompt/output,
process/adherence, judge/auditor, conflict, analysis, and public derivative. Every row
requires an exact duration or event-based trigger, start event, destruction method,
responsible role, backup/replica treatment, and any legal-hold exception. There is no ARS
default. A missing row or value blocks execution.

The public dataset includes only permissioned, de-identified artifacts and aggregate or
pseudonymous records allowed by the consent and rights receipts. Raw confidential material
is not made public merely to satisfy reproducibility language.

### 10.4 Conflicts and publication permission

Recruiters, packet designers, judges, adjudicators, analysts, and authors declare conflicts
before access to their role's data. A conflicted judge is replaced before scoring. If a
potential conflict is discovered after scoring, an independent conflict owner who cannot
see arm identity, artifact content, or any scores applies the preregistered closed
relationship/time-window rule. The original raw score remains visible. A blinded reserve
judge re-rates the artifact and the replacement rating enters the primary composite; both
the original-included and replacement versions publish as sensitivity records. If no
independent replacement is available or the conflict remains unresolved, Level 3 is
blocked rather than silently retaining the favorable score.

Publication permission is distinct from participation and model processing. The study
publishes no manuscript text, prompt/output transcript, or identifiable quote without the
specific recorded permission for that content class.

## 11. Preregistration, hashes, and result publication

Before recruitment, participant contact for study enrollment, allocation, model dispatch,
or data collection, the team deposits one exact protocol bundle in a public immutable
registry or an institution-approved registry that supplies an externally verifiable
persistent id, RFC 3339 timestamp, and receipt over the exact SHA-256. A Git commit alone
is insufficient.

The registered bundle contains or hash-binds:

1. this protocol version and the final statistical analysis plan;
2. the five-domain scoring rubric and score anchors;
3. the six-packet manifest, planned allocation schedule, actual-pair weighting rule, and
   rights/permission inventory;
4. participant eligibility, matching algorithm, calibration rubric, and allocation
   algorithm, canonical participant/pair ordering, atomic next-position consumption and
   non-reuse rules, release-ledger grammar, plus a commitment to the concealed sequence;
5. exact ARS, base-model, environment, neutral-control, budget, and adherence records;
6. the condition-neutral template and deterministic masking canonicalizer;
7. judge eligibility, assignment, conflict, blinding, reserve, and raw-score-lock rules;
8. missingness, bounds, multiplicity, stopping, claim-gate rules, and every exploratory
   defect/process audit instrument that will be reported;
9. data-management, retention, destruction, and publication-permission plans; and
10. a commitment to publish favorable, null, negative, inconclusive, and terminated
    results.

The registration record carries `protocol_sha256`, `bundle_sha256`, `registered_at`,
`registry_id`, `persistent_id`, and the external receipt. File modification times and an
operator-entered date are not preregistration evidence.

Amendments are append-only. Each row records:

- monotonic amendment id and RFC 3339 timestamp;
- reason and accountable owner;
- old and new bundle/file hashes;
- whether any participant/judge/auditor recruitment contact, eligibility screening,
  calibration, matching, or other study data collection had begun;
- whether anyone had accessed any recruitment/eligibility/calibration record,
  participant-output bytes, process/adherence/model logs, judge/auditor record, condition
  label, manuscript score, guess, or aggregate outcome;
- affected cohort and analysis consequence; and
- whether the original primary claim remains authorized.

Nothing overwrites the registered bytes. Before any study contact or data, a superseding
pre-data amendment needs its own external timestamp and receipt. From the first
participant/judge/auditor recruitment contact or any eligibility, calibration, matching,
or other study-data collection—whichever occurs first—the frozen core cannot be amended.
That core comprises the primary estimand/design/outcome/rubric, allocation and release
ledger, unit/weighting/analysis/precision, missingness/bounds/stopping/claim gate,
intervention and adherence definition, masking/blinding diagnostic, judge eligibility,
assignment, conflicts, reserve and raw-lock rules, and governance, consent, compensation,
retention, destruction, and publication-permission rules. Any later change is a deviation;
continuing under it requires a new protocol version, fresh external registration, and a
non-pooled cohort. All deviations and the original frozen primary result publish together.

## 12. Feasibility and budgeted capacity

The operational pilot uses at most 12 pairs and may test delivery scheduling within the
fixed six-active-hour/48-hour window, interface parity,
log completeness, masking, judge assignment, and variance estimation. It requires its own
institutional determination, authorization record, consent, and externally timestamped
pilot registration before any pilot recruitment or data collection. Pilot outcomes are
not pooled with the confirmatory cohort and authorize no effectiveness claim. Pilot task
packets and calibration examples are byte- and content-distinct from the six confirmatory
packets; no pilot participant may inspect confirmatory bytes. Pilot input
may adjust packet timing, interface logistics, reserve capacity, or other artifacts within
the frozen rules. Changing the estimand, design, primary outcome/rubric, allocation/unit,
precision, missingness, multiplicity, stopping, masking gate, or claim ceiling requires a
new protocol version and fresh design review—not merely new hashes. The pilot record
remains immutable and visible.

The fixed confirmatory cohort is 36 pairs / 72 participants; Level 3 requires all 36 pair
outcomes to be exact. The rule that a judge sees at most one output from any packet
implies at least 36 distinct expert judges for 72 manuscripts / 216 planned primary
ratings, plus a preregistered reserve pool. At the stated per-task and per-rating planning
budgets, the scheduled capacity is:

| Work | Budgeted hours at 36-pair cap |
|---|---:|
| Participant task window (up to 6 h each) | 432 h |
| Standardized orientation (1 h each) | 72 h |
| Three expert rating slots/output (up to 45 min each) | 162 h |
| Two neutral process-audit slots/output (up to 30 min each) | 72 h |
| Stewardship, masking, conflict handling, analysis, reporting reserve | at least 80 h |
| **Nominal scheduled capacity** | **at least 818 h** |

This excludes recruitment, packet construction, institutional review, secure
infrastructure, translation, model/tool charges, and publication preparation. The
preregistered budget records those amounts rather than inventing a universal currency
estimate. These are planning ceilings/reserves, not a claim that every slot consumes its
maximum or a minimum observed labor total. Compensation uses the responsible institution's
approved local rate, equally and pro rata across arms.

The pilot is credible for feasibility and variance only. The confirmatory cohort is the
smallest version allowed to make the narrow directional claim in §13, and then only if
precision, missingness, blinding, governance, and preregistration gates all hold.

## 13. Claims ladder

| Level | Evidence state | Maximum licensed statement |
|---|---|---|
| 0 — this issue | Frozen design only; no run | "A preregistration-ready outcome-evaluation design has been frozen." |
| 1 — operational pilot | Procedures executed; no claim-bearing cohort | "The bounded procedure was feasible/not feasible under the recorded conditions," plus descriptive estimates. |
| 2 — confirmatory but inconclusive | Registered cohort reported, but any assigned outcome is bounded/missing or another directional gate is unmet | "The estimated difference was X with interval/bounds Y; the study was inconclusive." |
| 3 — narrow directional result | All 36 assigned outcomes are exact; every evaluable artifact has three valid independent ratings; the primary crossed interval has lower bound above zero and half-width at most five points; allocation proofs are intact; no spillover, unresolved judge conflict, envelope mismatch, preregistration, governance, or stopping-access failure exists; and blinding status is `no_detectable_compromise` from at least 32 assessable pairs | "For these randomized researchers, frozen packets, exact ARS version, base model, and active control, ARS assignment increased mean completion-adjusted blinded manuscript/reporting quality by X points (95% CI Y)." |
| 3b — blinding compromised | Every Level 3 gate except the blindness gate holds, and the assessable diagnostic is `compromised` | "Under attempted but compromised blinding, observed scores differed by X"; no successfully blinded quality claim. |
| Never licensed | Any result from this protocol | ARS makes science valid/better; the reported experiment occurred; raw data are true/complete; analyses reproduce; every discipline/language/version benefits; any individual stage caused the total effect. |

A null or non-significant result is not equivalence or non-inferiority. Either claim would
require a separately preregistered margin, sample size, and analysis. A successful result
does not authorize a README/CHANGELOG efficacy statement broader than the exact Level 3
language and evidence link.

## 14. Future profile shape and enforcement plan

Future implementation extends the existing files; it does not land a parallel report
schema. The closed `outcome_evaluation` block will require these sections:

```json
{
  "benchmark_report_profile": "ars-outcome-evaluation/1.0",
  "outcome_evaluation": {
    "protocol": {},
    "estimand": {},
    "population": {},
    "design": {},
    "task_packets": {},
    "intervention": {},
    "adherence": {},
    "outcomes": {},
    "judging": {},
    "analysis": {},
    "governance": {},
    "preregistration": {},
    "feasibility": {},
    "claim_ceiling": {},
    "results": {}
  }
}
```

The future implementation surface is:

- `shared/benchmark_report_pattern.md`
- `shared/benchmark_report.schema.json`
- `scripts/check_benchmark_report.py`
- `scripts/test_check_benchmark_report.py`
- `examples/benchmark_report_template.json`
- `scripts/_ci_pytest_manifest.toml`
- `CHANGELOG.md` (future implementation only: state that the profile/schema/runtime
  shipped and that the study remains unexecuted; make no efficacy claim)

It must keep the existing six-field fixture valid and preserve its warnings/output. For
the opt-in profile it must enforce, at minimum:

1. exact marker/block pairing and closed nested objects;
2. exactly one primary estimand, outcome, contrast, direction, estimator, and the
   profile-only `primary_metric_value=null` condition for zero complete pairs;
3. parallel allocation, participant randomization, pair blocking, and judge aggregation;
4. ITT primacy with per-protocol only secondary;
5. exact ARS/model/tool/packet/budget bindings and cohort-boundary amendments;
6. the completion-adjusted score and frozen five-domain weights;
7. the fixed sample, crossed pair-by-human-judge precision, exclusion, missingness,
   multiplicity, and stopping rules;
8. distinct judge identity/independence/conflicts and `blinded_to` fields;
9. raw-score preservation, format-only masking, and post-score guesses;
10. institution-owned determination, independent readiness/authorization, and the fixed
    #665 non-authorization footer;
11. an external preregistration receipt plus append-only amendments; and
12. exact stage and #657 claims ceilings.

Mutation tests must reject escaped/fold-colliding profile keys, duplicate keys, profile
BOM/non-UTF-8, crossover, a second primary outcome, judge ratings counted as participants,
independent-pair uncertainty, a missing third rating collapsed to a two-rating score,
structural zeros counted as judge clusters/degrees of freedom, a no-human-judge interval,
a missing guess used to drop or replace a valid score, or a missing guess allowed to pass
the ordinary Level 3 blindness gate,
reissued participant ids, swapped locked pairs, reversed participant order,
skipped/reused sequence positions,
recycled released positions or a 37th pair, post-randomization void/exclusion/replacement,
missing-outcome deletion instead of bounds,
outcome-dependent stopping, cross-pair participant spillover, a maintainer/self or
unresolved-conflict judge, semantic masking, hidden raw scores, Git-only preregistration,
core changes after recruitment/eligibility/calibration data, pre-determination
recruitment/scoring, stage-effect promotion, null-as-equivalence, and underlying-science
claims. Positive fixtures must include an all-36 exact crossed-interval report, a
terminated zero-complete-pair report whose compatibility metric is `null`, and an
otherwise legacy fixture with exact/fold-like marker names only in nested extension data
whose byte behavior remains unchanged.

The held-out measurement contract may be reused as design vocabulary for hashes,
append-only amendments, raw preservation, and judge disclosure, but the outcome profile
does not `$ref` it and does not make human participants into held-out LLM runs.

## 15. Acceptance checklist and non-goals

This design freezes:

- [x] one primary comparison and estimand;
- [x] allocation, no-crossover rule, unit, pair blocking, and judge aggregation;
- [x] a precision target and fixed enrollment cap;
- [x] exclusions, missingness, multiplicity, stopping, version, adherence, and amendments;
- [x] stage identifiability and non-identifiability;
- [x] primary/secondary outcomes with proxy gaps;
- [x] independent human judging, attempted blinding, and a blindness diagnostic;
- [x] institution-owned determination, consent, confidentiality, retention, compensation,
  conflicts, and publication permission;
- [x] external immutable preregistration and all-result publication;
- [x] the smallest credible scheduled labor capacity and narrow claims ladder; and
- [x] additive migration of the existing benchmark-report family.

Non-goals for #658:

- no schema, validator, template, runtime, or CI-manifest implementation;
- no task-packet, rubric, judge panel, participant, or model recruitment;
- no live model, external API, judge, or scored evaluation;
- no retrofit of legacy benchmark reports;
- no README or CHANGELOG effectiveness claim; and
- no statement that design completion is measurement evidence.
