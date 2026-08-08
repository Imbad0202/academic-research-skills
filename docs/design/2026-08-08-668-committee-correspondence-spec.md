# #668 Committee correspondence tracker V1 specification

## Frozen entrypoint and owner

V1 is a specialized `committee-correspondence` variant of the existing
`academic-paper` `revision-coach` entrypoint (`/ars-revision-coach`). The user must
identify the input as correspondence from a real committee or institutional
review office; the router does not infer that authority from tone or vocabulary.
`revision_coach_agent` owns the parse-and-confirm interaction because it already
preserves source comments, handles compound asks, and produces response skeletons.

The variant has its own schema and checker. It never emits the paper-review
Schema 11 commitment ledger, assigns manuscript-review severity, or writes to the
Material Passport. This prevents committee requirements from being translated
into peer-review taxonomy.

## Bundle and storage

Standalone output is a directory named
`committee_correspondence/<source_sha256_first_12>/` containing:

- `source_letter.txt` — exact input bytes, never normalized or overwritten;
- `concern_tracker.json` — `committee-correspondence/1.0` artifact;
- `response_skeleton.md` — drafting aid bound to every concern.

All paths inside the tracker are relative to its bundle root. The checker rejects
absolute paths, parent traversal, symlinks, files outside the bundle, hash drift,
and byte-length drift.

## Source accounting

`source_artifact.segments[]` covers the raw letter from byte zero to EOF without a
gap or overlap. Each segment is `comment` or `non_comment`, has a stable source
order, byte range, and SHA-256. Non-comment material (headers, sign-offs,
administrative metadata) remains preserved and visible; it is not silently
dropped merely because it does not become a concern.

Every comment segment maps to exactly one concern. Every non-comment segment maps
to zero concerns. A concern copies the exact decoded source bytes into
`verbatim_text` and repeats the segment locator. Thus the checker proves complete
transport after segmentation and makes any questionable segmentation auditable.
It does not claim a semantic theorem that arbitrary prose was segmented correctly;
the agent must show the byte-complete segmentation to the user for confirmation
before finalizing the tracker.

Compound source comments stay one concern and carry multiple `action_type` values.
Splitting one source comment into several records would break exactly-once
accounting. If a letter has separately numbered subcomments, they should be
separate source segments.

## Concern record

Each concern carries:

- stable `CC-<three digits>` concern id and its exact source locator;
- `authority_status`: `explicitly_required`, `conditional`, `question`,
  `suggestion`, or `unclear`;
- `authority_basis`: an exact committee phrase, author confirmation, or explicit
  unresolved state — never a tone inference;
- multi-valued `action_type[]`: design, explanation, revise/add artifact,
  administrative, or legal/policy check;
- affected artifacts, owner, dependencies, and required-before milestone, each
  with explicit committee/author/profile provenance or an unresolved state;
- fixed response/evidence placeholders and `resolution_status=unresolved`.

There is no priority, severity, risk score, probability, satisfaction prediction,
or elapsed-time estimate. The source-order concern array is canonical. Optional
working views must be exact permutations of the same concern-id set; they can
reorder display without replacing or dropping source order.

## Profile coupling

`profile_context.state=not_selected` is valid and forces
`artifact_resolution_state=artifact_agnostic`. A selected #666 profile may enrich
affected-artifact pointers, but it cannot rewrite the verbatim concern, authority
status, owner, deadline, or source order. V1 ships no authority profile and never
blocks on profile absence.

## #665 boundary

The tracker rides a fixed human-subjects administrative header:

- `submission_readiness=unresolved`;
- `authorization_status=documented | not_provided | cannot_verify`;
- `review_pathway=institutional determination required`;
- the fixed #665 non-authorization footer.

`authorization_status=documented` requires a pointer to a comment segment that
contains the committee's own documentation; it is never derived from concern
completion. The tracker and response skeleton remain drafting aids and never state
that a concern is resolved or that the skeleton is submission-ready.

## Deterministic checker

`scripts/check_committee_correspondence.py` validates the schema and recomputes:

1. raw-letter path containment, byte length, and SHA-256;
2. contiguous full-file segmentation and every segment digest;
3. comment-segment/concern one-to-one coverage and exact verbatim transport;
4. canonical source order, stable ids, dependency resolution, and provenance
   constraints;
5. degraded-mode and selected-profile rules;
6. every working view as a full permutation;
7. response-skeleton containment/hash plus one marker and both unresolved
   placeholders per concern;
8. fixed drafting-aid and human-subjects boundary text.

The checker does not judge whether a proposed response will satisfy the committee,
whether a requested change is legally sufficient, or whether institutional
authorization exists beyond the explicit source pointer.

## Handoff

The concern tracker plus response skeleton can feed response drafting and
resubmission work only after the user confirms the segmentation and concern
records. Downstream work preserves `concern_id` and source locator. Evidence fields
remain placeholders until an author supplies an artifact pointer; the checker never
promotes a placeholder into evidence.

## Acceptance fixtures

The committed synthetic bundle contains a compound comment requiring both design
and artifact revision, an administrative question, a non-comment header/sign-off,
no selected profile, and no inferred priority. Mutation tests cover dropped or
duplicated comments, byte gaps/overlap, source/hash drift, reordered source records,
destructive/incomplete working views, response-marker omissions/duplicates,
false resolution, undeclared priority/severity, profile misuse, and a response that
loses the #665 boundary.
