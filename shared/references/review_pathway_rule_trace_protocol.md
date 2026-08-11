# Review-pathway rule trace protocol (#669)

This protocol governs the candidate-only, deterministic rule trace built by
`scripts/build_review_pathway_rule_trace.py`. The trace displays selected-profile
predicate work. It never selects, predicts, ranks, approves, clears, exempts, or
authorizes a pathway.

Normative contracts:

- `shared/contracts/human_subjects/review_pathway_trace_request.schema.json`
- `shared/contracts/human_subjects/review_pathway_rule_trace.schema.json`
- `shared/contracts/human_subjects/irb_context_record.schema.json`
- `shared/contracts/human_subjects/authority_profile_registry.schema.json`
- `shared/contracts/human_subjects/resolved_authority_context.schema.json`
- `docs/design/2026-08-11-669-review-pathway-rule-trace-spec.md`

## Fixed result and non-authorization boundary

Every completed or halted trace carries exactly:

```text
Result: institutional determination required
```

and the exact #665 footer:

```text
Human-subjects boundary: This output does not authorize recruitment, consent, access to identifiable data, intervention, or data collection.
```

The trace is advisory navigation only. It cannot change submission readiness,
authorization status, institutional acceptance, recruitment, consent, data
access, intervention, collection, delivery, a verdict, a checkpoint, or any
other workflow state.

## Producer contract

Only a permitted dispatching layer may assemble a
`review-pathway-trace-request/1.0`. It supplies the exact bound
`context_pointer`, `registry_pointer`, and `resolved_digest`; it does not infer a
profile from locale, language, affiliation, topic, or manuscript prose.

Candidate names come only from an explicitly identified institutional material
or an author-declared question. They are question labels, not authority. A
request must partition every selected-profile requirement whose exact
`consumer_scopes` contains `pathway_trace`. Each eligible requirement appears
under exactly one candidate for its own exact profile. The dispatching layer may
not omit an awkward predicate, move a data-protection requirement into a
review-ethics candidate, use an overlay as a selected profile, or invent a local
pathway rule.

Candidate and requirement arrays use ascending ids. Ordering is
`display_only_sequence_no_decision_meaning`; it never indicates likelihood, priority, or a
recommended route. Alternatives are profile-local. A data-protection route
remains parallel authority work and cannot be described as an IRB route.
Requests projecting more than 4,096 complete alternative rows fail; trace JSON
and rendered Markdown are each capped at 8 MiB.

## Builder contract

Before dereferencing any requirement, the builder calls
`validate_resolved_context(resolved, context, registry)`. It then requires exact
request pointer/digest equality and exact selected-profile requirement
coverage. It opens only the explicitly named context, registry, resolved,
request, and trace files. It uses no model, API, evaluator, network, clock,
ambient filesystem scan, caller template, or caller prose fragment.

For every emitted predicate, the builder verifies the exact requirement id,
digest, `requirement_pointer`, and `authority_anchor_pointer` against the bound
registry. It projects only:

- tri-state applicability and leaf fact occurrences;
- the exact author-declared fact state and value;
- missing or unknown fact ids;
- exact `authoritative_decision_maker.role_id`;
- exact anchor source id, provision, https link, and effective date.

It does not copy or interpret a requirement title, summary, structured
expectation, evidence description, legal conclusion, or institutional rule.
Every fact occurrence is retained; an unresolved fact cannot be converted into
a matched or unmatched predicate.

All selected profiles on both authority axes must be exact, profile-applicable,
and bound to current sources. A missing profile emits no candidate trace and
preserves `JURISDICTION_UNRESOLVED`. Any profile-level applicability/source or
overlay-base problem emits no candidate trace and uses
`authority_context_unresolved`.

There is one narrow, trace-only treatment of unknown requirement predicates. If
both axes have exact selected profiles, every selected profile itself is true
and current, and all unresolved reasons are selected-profile requirement-level
`APPLICABILITY_UNRESOLVED`, the builder may display those rows under
`unresolved_predicates`. This does not open or change #666's
`profile_dependent_result_allowed` gate; no consumer may turn such a row into an
action or result.

## Replay and render contract

`request_digest` binds the complete canonical request. `trace_digest` binds the
complete canonical trace with only that digest field omitted. Neither digest is
sufficient by itself.

Before accepting or rendering a serialized artifact, call:

```python
validate_review_pathway_rule_trace(
    trace,
    request,
    context,
    registry,
    resolved,
)
```

The validator replays #666, rebuilds the request coverage and complete expected
trace, recomputes digests, and requires exact canonical equality.

The fixed renderer emits only the labelled grammar
`Candidate pathway examined`, `Matched predicates`, `Unmatched predicates`,
`Unresolved predicates`, `Alternative pathway triggers`, `Result`, and
`Authority`, plus the fixed header, state, ordering statement, source label, and
boundary footer. Empty lists are the literal `- none`. It accepts no template.

## Surface-scoped output lint

After replay, call `scripts/check_review_pathway_output.py` with the one explicit
trace JSON path and, when present, the one explicit rendered Markdown path. The
checker scans only every string leaf in that named generated JSON and every line
in that named rendering. It never scans a directory, repository, source
document, protocol, fixture corpus, log, or sibling file.

Lint normalization is Unicode NFKC, `casefold()`, Unicode format/surrogate
removal, control-to-whitespace mapping, Unicode-whitespace collapse, and
punctuation-spacing normalization. `No IRB needed`, approval/clearance,
`Low risk`, probability/confidence/likelihood language, percentages, rankings,
timelines, and comparison to “most studies like yours” fail. A pathway term is
allowed only in the exact JSON `candidate_pathway_name` field and an exact
renderer line beginning `Candidate pathway examined: ` whose profile/name pair
equals the paired JSON. Approval, clearance, low-risk, and probability language
remain banned even inside a candidate name.

## Consumer contract

An agent may display the trace only after the permitted dispatching layer
confirms both successful replay and successful surface lint against the exact
named artifacts. Preserve the candidate labels, buckets, fact states, holders,
pointers, anchors, ordering statement, result, and footer exactly. Do not
summarize a candidate as the likely, probable, usual, low-risk, simplest,
preferred, approved, exempt, cleared, or expected route.

The trace never supplies an action assignment. For action planning, the normal
#666 gate and exact actor/consumer-scope rules still apply independently. A
candidate label or matched predicate does not establish applicability of local
policy, institutional acceptance, submission readiness, authorization, or
permission to begin any activity.

`deep-research/references/irb_decision_tree.md` is a derived navigation aid. Its
bounded branches backpoint to registry requirement ids and exact primary-source
anchors. It is not authority, is not a complete local taxonomy, and cannot
supply an unanchored predicate to this trace.

## Non-goals

No determination, probability, confidence, likelihood ranking, timeline,
comparison cohort, simulated committee, legal advice, institutional acceptance,
submission readiness, authorization, action assignment, or workflow decision.
