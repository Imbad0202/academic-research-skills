# #669 Review-pathway rule trace — frozen specification

Status: frozen for implementation
Issue: #669
Dependencies: #665, #666, #668, and #671 are closed
Date: 2026-08-11

## 1. Outcome and boundary

This feature displays the predicate work for caller-named candidate review
pathways. It never selects a pathway and never states or predicts exemption,
approval, clearance, risk, authorization, probability, confidence, likelihood,
rank, or timeline.

The only result value is:

`institutional determination required`

Every completed trace and every halted trace carries the exact #665 footer:

`Human-subjects boundary: This output does not authorize recruitment, consent, access to identifiable data, intervention, or data collection.`

The runtime is standard-library-only and deterministic. It opens only the five
explicitly named files supplied by the caller: context, authority registry,
resolved authority context, trace request, and (for replay validation) trace.
It performs no model/API/judge/eval/network/clock call and no directory scan.
This advisory is never a gate, verdict, checkpoint input, readiness input, or
authorization input.

## 2. Normative files and versions

- `shared/contracts/human_subjects/review_pathway_trace_request.schema.json`
  — `review-pathway-trace-request/1.0`
- `shared/contracts/human_subjects/review_pathway_rule_trace.schema.json`
  — `review-pathway-rule-trace/1.0`
- `scripts/build_review_pathway_rule_trace.py` — builder, validator, renderer
- `scripts/check_review_pathway_output.py` — surface-scoped banned-output lint
- `shared/references/review_pathway_rule_trace_protocol.md` — producer and
  consumer protocol

The two JSON Schemas are Draft 2020-12, closed at every object boundary, and
checked by `Draft202012Validator.check_schema` in tests and the integration
guard. Runtime validation additionally enforces cross-file identity, exact
coverage, ordering, digest, replay, normalization, and semantic invariants that
JSON Schema cannot express.

## 3. Inputs and exact authority binding

The builder receives:

1. an author-owned `irb-context-record/1.0`;
2. the exact `human-subjects-authority-registry/1.0`;
3. a serialized `resolved-human-subjects-authority-context/1.0`;
4. a caller-owned `review-pathway-trace-request/1.0`.

Before doing any trace work it calls
`validate_resolved_context(resolved, context, registry)`. The request's full
`context_pointer`, full `registry_pointer`, and `resolved_digest` must equal the
replay-validated resolved artifact exactly.

Only `authority_kind=profile` requirements whose exact `consumer_scopes`
contain `pathway_trace` are eligible. Both selected axes are accounted for, but
their candidates and alternatives remain profile-local: data-protection routes
are parallel authority work and are never relabelled as IRB pathways.
Institutional and funder overlays are not candidate-pathway definitions in V1
and are never substituted for a selected profile.

## 4. Caller-owned candidate mapping

The authority registry does not contain local pathway names. The builder must
not invent them. The request therefore supplies candidate labels and their
source metadata. `source_kind=institutional_material` records a named local
source; `author_declared_question` records only the author's question. Neither
source kind establishes authority or applicability.

Each candidate has one exact selected profile pin and one or more eligible
`predicate_requirement_ids`. Across all candidates for every selected profile,
those ids must form an exact, non-overlapping partition
of every eligible requirement in that profile. A missing, duplicate, foreign,
overlay, wrong-axis, or non-`pathway_trace` requirement fails closed.

Candidate ids are unique and serialized in ascending id order. Candidate order
is display-only and never means likelihood or priority. Names are non-empty,
NFKC-normalized, trimmed, single-line inert display text with no Unicode
control/format/surrogate character or Markdown structural delimiter. A
candidate name has at most 12 words, no sentence punctuation, and no
subject-plus-assertion grammar such as `this study is ...`. The name
source locator follows the same inert-text rules. Candidate names may contain a
pathway term only because the field is explicitly labelled
`candidate_pathway_name`; the lint rules in section 9 still reject an approval,
clearance, probability, confidence, or low-risk assertion inside that field.

## 5. Halt and unresolved behavior

There are three output states:

- `completed`: selected profiles are exact, applicable, and bound
  to current authority sources; candidate rows are emitted.
- `jurisdiction_unresolved`: either required authority axis lacks a selected
  profile. `candidate_pathways` is empty and at least one exact
  `JURISDICTION_UNRESOLVED` reason is preserved.
- `authority_context_unresolved`: a selected profile is unknown/false, a source
  is not current, or another profile/overlay-level condition prevents a safe
  trace. No candidate rows are emitted.

An unknown requirement predicate is intentionally different. If both axes are
selected, all selected profiles themselves are `applicability=true` and
`source_state=current`, and every unresolved reason is requirement-level
`APPLICABILITY_UNRESOLVED`, the builder may emit the bounded rule trace. The
affected requirement remains exactly in `unresolved_predicates`; it cannot be
coerced to matched or unmatched. This narrow exception exposes predicate work,
not a profile-dependent result, and does not change the #666 downstream gate.

All selected profiles on both axes participate in the safe-context check. A
data-protection candidate remains separate from review-ethics candidates and
cannot appear in another profile's `alternative_pathway_triggers`.

Every halted artifact still says `institutional determination required` and
carries the boundary footer. It contains no partial candidate trace.

## 6. Predicate projection

For each requested requirement the builder dereferences its exact
`requirement_pointer` and `authority_anchor_pointer` in the replay-bound
registry and verifies the requirement id and digest. The emitted predicate row
contains:

- exact requirement id, digest, and both pointers;
- exact requirement applicability from the resolved artifact;
- every leaf fact occurrence from `predicate_trace`, including expression path,
  operator, tri-state result, author-declared state, and exact declared value;
- sorted unknown or missing fact ids;
- the requirement's exact `authoritative_decision_maker.role_id`, which answers
  who holds an unresolved determination;
- exact `source_id`, `authority_url`, `provision`, and `effective_date` from the
  requirement authority anchor.

`true`, `false`, and `unknown` requirements go respectively into
`matched_predicates`, `unmatched_predicates`, and `unresolved_predicates` when
all of their leaf facts are resolved. Any missing or unknown leaf keeps the
complete requirement row in `unresolved_predicates` even when Strong-Kleene
short-circuiting makes the aggregate applicability false.
Rows are sorted by requirement id. No text summary, expectation, evidence
description, title, or legal interpretation is copied from the registry.

For one candidate, `alternative_pathway_triggers` is the complete set of
predicate rows assigned by the request to every other candidate under the same
exact profile. Each row names its `target_candidate_id` and preserves its
observed tri-state; it is not filtered to matched predicates and is not called a
recommendation. Cross-profile candidates are not alternatives to one another.
The request is rejected if this complete expansion would exceed 4,096 total
alternative rows. Canonical JSON, pretty-printed JSON, and rendered Markdown are
each capped at 8 MiB; the lint traversal is iterative and capped at 200,000 JSON
nodes.

## 7. Output digest and replay

`request_digest` is SHA-256 over canonical JSON of the complete request.
`trace_digest` is SHA-256 over canonical JSON of the complete trace with only
`trace_digest` omitted. Canonical JSON is UTF-8, key-sorted, compact, finite,
and preserves array order.

`validate_review_pathway_rule_trace` first validates the four authority inputs
and the stored digest, rebuilds the entire expected trace, and requires exact
canonical-byte equality. Schema validation or a self-digest alone is never
treated as replay validation.

## 8. Exact renderer

The Markdown renderer is a pure function of a replay-validated trace. It emits
one fixed heading, trace state, display-only ordering statement, and then, for
each candidate, the exact labelled sections:

```text
Candidate pathway examined: <profile_id> <candidate_pathway_name>
Matched predicates:
Unmatched predicates:
Unresolved predicates:
Alternative pathway triggers:
Result: institutional determination required
Authority: <requirement_id> | <provision> | <source link> | effective <date>
```

Each predicate list row contains the exact requirement id, fact bindings,
authority provision/link/date, and responsible authority role. Empty lists emit
the literal `- none`. A halted trace emits its exact halt reasons and no
candidate section. The final line is the exact blockquoted #665 footer. The
renderer never accepts a caller-supplied template or prose fragment.

## 9. Surface-scoped banned-output lint

The lint opens only explicitly supplied generated artifacts:

- every string leaf in one named
  `review-pathway-rule-trace/1.0` JSON artifact; and
- every line in one optional named Markdown rendering.

It never scans the repository, a directory, siblings, source manuscripts,
protocol prose, fixtures, or logs. It performs Unicode NFKC normalization,
`casefold()`, removes Unicode format/surrogate characters, maps control
characters to whitespace, converts every Unicode whitespace run to one ASCII
space, removes spacing around punctuation, and then checks the normalized
surface.

The following are banned on every scanned path: `no IRB needed`, `approved`,
`approval`, `cleared`, `clearance`, `low risk`, probability/confidence/chance/
odds, `likely`/`unlikely`/`probably`, percentages, likelihood ranking, timeline
estimates, and `most studies like yours`. `exempt`, `expedited`, `full board`,
`convened board`, `not human subjects research`, and `NHSR` are pathway-name
terms. They are permitted only in the exact JSON path
`candidate_pathways[*].candidate_pathway_name` and the exact corresponding
Markdown line beginning `Candidate pathway examined: `. `Approved`, `Cleared`,
`Low risk`, and probability/confidence language are never permitted even there.

The Markdown exception is grammar-bound: the prefix must match exactly, the
profile id and candidate name must equal a candidate row in the paired JSON,
and the whole rendered artifact must equal the deterministic renderer output.
Thus `Result: Exempt`, `The study may be exempt`, `Candidate pathway examined -
Exempt`, and a valid candidate line followed by a hedged determination all fail.

Near-miss fixtures cover case, full-width Unicode, non-ASCII whitespace,
punctuation spacing, hedged determinations, percentages, confidence phrases,
bare pathway terms, and valid candidate-context uses.

## 10. Producers and consumers

Only a permitted dispatching layer may assemble a request. It must preserve the
author or institutional source of candidate names and may not derive labels from
manuscript prose, locale, language, affiliation, or model inference. The
deterministic builder validates and projects; it does not authorize the mapping.

Consumers must receive the exact four bound inputs, request, trace, and optional
rendering and confirm successful replay plus lint. They may display the trace as
a navigation aid. They may not use it as a gate/verdict/checkpoint input or to
change submission readiness, authorization status, recruitment, collection,
consent, access, intervention, manuscript delivery, or any other workflow state.

`deep-research/references/irb_decision_tree.md` is a derived navigation aid. Its
branches point to exact requirement ids and primary authority anchors; it is not
an independent authority source and does not supply unanchored pathway rules.

## 11. Acceptance matrix

The shipped tests and integration guard prove:

1. both schemas pass Draft 2020-12 metaschema validation;
2. positive and negative payloads exercise every conditional branch;
3. all predicate rows resolve exact selected-profile requirement and anchor
   pointers under deterministic replay;
4. the same declared facts under the U.S. and Taiwan review profiles produce
   different anchored traces;
5. an unknown fact remains an unresolved predicate and names its holder;
6. a no-profile request emits no candidate row and preserves
   `JURISDICTION_UNRESOLVED`;
7. missing, duplicated, wrong-profile, wrong-axis, overlay, and non-scoped
   requirement mappings fail;
8. source/profile/digest/request/output drift fails replay;
9. JSON and Markdown lint catch every normalized near miss while accepting the
   exact candidate grammar;
10. AST guards reject transport/process/clock imports, ambient scans, model or
    evaluator calls, caller prose templates, and use of trace results as a
    decision or workflow gate;
11. protocol, agent, contract index, navigation, CI manifest, and direct
    workflow wiring remain present.

## 12. Explicit non-goals

No determination, probability, confidence, likelihood ranking, timeline,
analogy to other studies, institutional acceptance, submission readiness,
authorization, legal advice, complete review taxonomy, or simulated committee.
The trace is always advisory navigation and always institution-owned at the
decision boundary.
