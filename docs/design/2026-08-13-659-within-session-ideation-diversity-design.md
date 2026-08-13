# #659 — Within-session ideation-diversity measurement design

Status: Phase-1 assets plus a Phase-2 no-call execution envelope are frozen. No subject, actor, judge, or adjudicator session is authorized by this document or by the envelope.

## 1. Construct and claims boundary

This study asks whether two existing Socratic mechanisms change the breadth of
framing that a synthetic scholar role expresses before the question is frozen.
It does not measure idea quality, novelty, cross-user homogenization, or real
scholars' creativity.

The lawful constructs are reported separately:

1. **Scholar-script-owned framing breadth**: the count and facet-family
   dispersion of precommitted role-card framings that the actor explicitly
   expresses before freeze.
2. **AI-surfaced facet follow-through**: a directionless facet surfaced by the
   mentor, whether it corresponds to a precommitted role-card framing, and
   whether the actor explicitly expresses that framing within the frozen
   response window.

The two constructs are never merged into a scalar diversity score. A model-
originated question, hypothesis, mechanism, ranking, or option is never credited
as scholar-originated, even if the actor agrees with it. This preserves the
POSITIONING and Kong L2 boundary: ARS may surface a directionless facet and ask;
it may not originate, expand, rank, select, or substitute the scholar's research
question.

The v0.1 fixtures are repository-owned synthetic role cards. "Scholar" in a
measurement row therefore means **synthetic scholar role**, not a real person.
Any study of real scholars requires a new protocol, consent/ethics review where
applicable, and a separate claims boundary.

## 2. Eligible population and unit of analysis

A session is eligible only when all of these are true:

- Socratic mode is active;
- intent is exploratory;
- the dialogue remains in Layer 1 Problem Framing;
- the synthetic scholar has no fixed research question or requested deliverable;
- the role is novice-targeted and has not supplied a manuscript or draft; and
- no retrieval, writing, or later-stage review task is underway.

Correct non-firing outside this population is not treatment failure and is not
included in a treatment denominator.

The transcript is segmented into mentor turns and actor turns. A framing is
counted at most once per session, on the first actor turn that independently
states a relation or contrast matching one precommitted role-card framing. A
bare assent, repetition of the mentor's wording, or selection from a model-made
menu is not independent expression.

## 3. Separate experiments and arms

The mechanisms differ in purpose and timing, so v0.1 uses two independent paired-control
experiments. Results may be shown side by side but not pooled as one treatment.

### Experiment A — adjacent probe

- `adjacent_probe_off`: production Socratic prompt, environment variable unset;
- `adjacent_probe_on`: byte-identical production prompt,
  `ARS_SOCRATIC_ADJACENT_PROBE=1`.

Both arms retain the production exploratory-mode convergence and challenge
rules. This experiment asks about the incremental behavior of the real opt-in
flag only.

### Experiment B — exploratory guardrails

- `exploratory_guardrails_on`: production Socratic prompt, adjacent probe off;
- `exploratory_guardrails_ablated`: a frozen non-production prompt variant,
  adjacent probe off.

The ablation changes only the exploratory auto-convergence prohibition,
mentor-initiated summary prohibition, premature-convergence correction, and
higher `[Q:CHALLENGE]` ratio. The exact source digest and replacement list live
in `nonproduction_variant.json`. The rendered prompt is an experimental artifact
only: it must never replace or modify the production agent file.

DA anti-sycophancy floors are outside the construct because they operate during
later adversarial critique, not Layer-1 ideation.

## 4. Synthetic actor-role protocol

Each fixture freezes a private role card before assignment:

- one initially expressed framing;
- two additional role-owned framings the actor is permitted to express;
- a directionless facet family for each framing;
- deterministic response dispositions for matching facets, non-matching facets,
  model-originated formed questions, and ordinary open questions; and
- a fixed user-turn freeze point.

The actor sees its role card but not mechanism name, arm label, paired transcript,
expected metric direction, or aggregate. The subject sees only actor messages,
not the inventory or codebook. Role-card ownership predates the session; it does
not imply that a real scholar originated the text.

Use a fresh context for every cell. Counterbalance arm order within scenario and
actor block. An actor must not perform both arms of the same scenario until its
first transcript is sealed; the execution plan discloses any unavoidable reuse.
No adaptive or model-generated actor is permitted under v0.1.

## 5. Language equivalence

The seed contains three English/zh-TW role-card pairs. Pair members share the
same canonical framing IDs, facet families, response dispositions, eligibility,
and freeze point. They are meaning-matched role cards, not literal translation
tests.

Before pooling languages, two bilingual reviewers independently attest that
each pair preserves role authority, framing opportunities, response policy, and
difficulty. Disagreement is adjudicated while blind to arm results. Without that
attestation, report languages separately and make no language-equivalence claim.

## 6. Labels and metrics

The frozen codebook is
`evals/heldout/within_session_ideation_diversity/codebook.md`.

Report at least:

- unique scholar-script-owned framings expressed before freeze;
- distinct facet families represented by those framings;
- expression opportunities and opportunity-normalized rates;
- legal AI-surfaced facets;
- surfaced facets matching a precommitted role-card framing;
- matching facets followed by independent actor expression within two actor
  turns;
- irrelevant option inflation, formed-RQ/hypothesis proposals, ranked/menu
  suggestions, and premature freeze attempts; and
- blocked, partial, schema-invalid, ineligible, and protocol-deviation sessions.

Count and dispersion are separate estimands. Facet follow-through has its own
denominator. Illegal model-originated options can only add violation counts;
they cannot improve either breadth metric.

The primary paired contrasts are arm differences within each experiment,
scenario, language, and replicate block. Report raw cell values and replicate
spread. No universal efficacy threshold is frozen in Phase 1; a later baseline
plan must pre-register any directional or precision claim before dispatch.

## 7. Judge and adjudication protocol

A decision-relevant row requires at least two independent judges per transcript.
Judges receive the transcript, private role-card inventory, and codebook, but not
mechanism, arm, pair/replicate mapping, expected direction, other transcript, or
aggregate. Presentation order and neutral handles are frozen before judging.

Judges label each actor framing, each AI facet/proposal, freeze eligibility, and
every exclusion/violation. Raw labels remain retained. A separate adjudicator
resolves every disagreement while blind to the same arm and aggregate fields.
Resolution is bidirectional and cites a codebook criterion. Unblind only after
raw labels and adjudication are sealed and hashed.

The final row uses `heldout-measurement/1.1`, suite class `paired_controls`, the
suite-local replicate rule, a precommitted rubric/plan, and a write-once execution
manifest. Model judges, human judges, and actor identities/status are disclosed;
no one is described as independent unless the execution record supports it.

## 8. Replicates, stopping, and evidence

A decision-relevant baseline requires at least two complete independent subject
replicates per scenario-arm cell. The later plan freezes actor blocks, subject
model/provider/auth/runtime, settings, prompt hashes, operator-declared token limits, tool/web
allowance, order seed, judge plan, and spend boundary.

The no-call runner does not resolve Git objects or invoke a provider tokenizer.
Its suite commit and token caps are explicitly operator-declared and unverified:
asset bindings plus the run-plan SHA are the verifiable byte authority, while
observed token usage and cap enforcement require later external receipts.

Stop on the first prompt/role-card hash mismatch, arm leakage, ineligible session,
unplanned tool/network action, evidence-write failure, partial subject output, or
actor-protocol deviation. Preserve the event and do not retry. A replacement is
a new disclosed replicate, never a silent continuation.

Retain role packets, exact prompts, actor messages, subject responses, event
streams, eligibility decisions, judge packets, raw labels, adjudication, hashes,
and the final measurement row.

## 9. Phase-2 no-call execution envelope

The file-only runner freezes one exact cross-product: 2 experiments x 6
scenarios x 2 arms x 2 independent subject replicates = 48 subject-session
cells. A seed-bound SHA-256 order forms 12 experiment/scenario blocks; replicate
2 reverses replicate 1's two-arm order within every block. Every cell binds the
suite assets, exact prompt bytes, prompt environment, scenario and initial
message, repository-owned actor packet, non-executable session envelope, and
fresh-context requirement by hash.

The command surface is limited to `init-run`, `materialize`, `validate`,
`ingest`, and `prepare-blind-packet`. It contains no provider transport,
dispatch, probe, actor, subject, judge, or adjudicator execution path.
`materialize` creates only frozen input files. `ingest` accepts one externally
recorded transcript, canonical external-session receipt, and closed canonical
raw-event stream at a time in exact order. The runner parses the raw event bytes
itself; unknown/free-form events fail closed, action classes come from those
bytes, every message turn is derived byte-exactly from its raw message event,
and exactly one first start plus one last completion forbids stitched sessions.
It does not cause or authorize a session. The run plan pins tools empty, web
off, transport `none`, dispatch
unavailable, API spend ceiling USD 0, API fallback off, and fresh external
authorization required.

The closed external authorization record binds exact plan SHA, run id,
operator-declared unverified suite commit, complete execution envelope, ordered
48-cell scope, decision, and time.
Its bytes must match each transcript's declared hash. A separate hash-bound
external-session receipt binds unique artifact/receipt/session ids, exact cell
and sequence, fresh-context attestation, and start/completion times. Session
start cannot predate authorization, start cannot follow completion, ids cannot
be reused, and accepted cell times cannot regress behind the preceding cell.
This proves only structure and byte binding; the runner does not authenticate operator identity,
recorder identity, fresh context, or genuine consent. Those remain
procedural responsibilities. The ingestion receipt retains the authorization
reference/digest plus external artifact and session-receipt digests. The first
prompt/role/envelope or authorization-record mismatch, arm leak, ineligible
session, unplanned tool or network action, evidence-write failure, partial
output, actor-protocol deviation, out-of-order ingestion, or
transcript-contract failure first publishes a durable closed write-once stop
intent embedding the raw bytes and exact stopped-state replay. Materialization
precommits one immutable attempt guard per cell; ingestion atomically advances
the next guard from `ready` to `active` before acquiring external bytes. The
active guard is a permanent retry poison if both predeclared stop-intent
publication slots fail, while a successful cell advances it to `completed`.
An unavailable
or over-bound transcript produces a bounded terminal acquisition record rather
than leaving a retryable cell. NFKC-normalized execution, authorization, and
message fields must contain an NFKC-normalized letter, number, or symbol;
execution and authorization identity fields require a letter or number, so
combining-mark-only strings never count as identity, consent, or output.
The runner then preserves the rejected transcript at a content-addressed path
and atomically replaces the manifest. A failed replacement remains
retry-forbidden and can recover only by exact marker replay. Validation
re-reads and hashes the marker and blocked evidence. The run tree must match
the exact state inventory. A compact canonical digest binds an arbitrary
number of unexpected files and directories, while deterministic marker-hardlink
and state-replacement staging paths bind post-marker crash artifacts. The
primary and fallback stop slots publish the same staged inode and exact bytes.
Bytes
written before a failed success-state commit remain hash-bound evidence rather
than untracked orphans. The append-only manifest must remain an exact ingested prefix
followed by pending cells, or by one blocked cell after a stop.

Only 48 complete, unstopped external transcripts can produce blinded material.
During each ingestion, and again before copying turns, the runner applies NFKC
plus punctuation/separator normalization and rejects all frozen identifiers, explicit
pair/arm/replicate markers, and prior-label/adjudication/human-evidence markers
from transcript free text. Before staging, a durable deterministic blind intent
freezes a one-time private nonce, all blind ids, and all
packet/inventory/map/manifest hashes against the exact plan plus complete
ingestion state. The intent remains a `0600` procedural-nondisclosure artifact
and is never delivered to judges. Partial staging can only exact-resume that
transaction or quarantine on collision; it cannot generate a second mapping.
Every complete-byte publication uses a deterministic intent-bound alias under
a `0700` run-local root. A cleanup failure preserves that hardlink as evidence;
validation checks its bytes and inode against the staging or final target.
The complete staging directory is then atomically renamed into
48 write-once isolated single-session packets.
The public inventory contains only blind ids and packet
hashes; an exact blind manifest binds all packet/map hashes to the complete
pre-blind ingestion manifest. Final state is `blind_finalized`, and validation
replays every packet plus the exact bundle inventory. An already-published
bundle can recover a crash before the state update only if exact replay passes.
A first-round packet cannot be delivered until a future closed assignment
ledger gate prevents the same judge from seeing another arm or replicate that
shares its pair/scenario/role card. This runner does not implement that ledger,
so the bundle alone never proves judge-exposure blindness. The complete
directory is never delivered. Packet presence flags mean no
structured label, adjudication, or human-evidence artifact is attached; they do
not reinterpret arbitrary text. The private map is a `0600` file under a `0700`
directory and explicitly declares `procedural_nondisclosure_only` plus
`encrypted=false`. This is not an enforced cannot-open seal; operators must
withhold it until raw labels and adjudication are sealed. The requirement remains at least two independent
arm-blind human judges and one separate arm-blind human adjudicator. The runner
does not fabricate or replace any of them.

## 10. Claims and authorization boundary

This phase freezes schemas, ordering, hashes, materialization, ingestion, and
blinding contracts. It publishes no actor or subject output, no judge or
adjudicator output, no baseline, and no effectiveness result. It does not modify
the production Socratic prompt or any historical baseline claim.

Any subject, actor, judge, or adjudicator session requires fresh authorization
for the exact frozen plan outside this no-call runner. No API,
subscription-model, web, tool, or other external call is authorized here. #659
remains open until the per-mechanism baseline and bounded claims row are
complete.
