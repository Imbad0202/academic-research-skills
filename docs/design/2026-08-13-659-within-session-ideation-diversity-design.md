# #659 — Within-session ideation-diversity measurement design

Status: Phase-1 design, codebook, actor-role seed, and non-production ablation
freeze. No subject, actor, judge, or adjudicator session is authorized by this
document.

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
model/provider/auth/runtime, settings, prompt hashes, token limits, tool/web
allowance, order seed, judge plan, and spend boundary.

Stop on the first prompt/role-card hash mismatch, arm leakage, ineligible session,
unplanned tool/network action, evidence-write failure, partial subject output, or
actor-protocol deviation. Preserve the event and do not retry. A replacement is
a new disclosed replicate, never a silent continuation.

Retain role packets, exact prompts, actor messages, subject responses, event
streams, eligibility decisions, judge packets, raw labels, adjudication, hashes,
and the final measurement row.

## 9. Phase boundary

This PR may freeze the design, seed, codebook, ablation transform, validator, and
tests. It does not publish a baseline and cannot satisfy Phase 2 of #659.

Any subject, actor, judge, or adjudicator session requires a new exact run plan
and fresh authorization. No API, subscription-model, web, or tool call is
authorized here. #659 remains open until the per-mechanism baseline and bounded
claims row are complete.
