# Committee Correspondence Protocol (#668)

This is the `committee-correspondence` variant of `academic-paper`
`revision-coach`. It structures comments already returned in a research ethics or human-subjects protection
review that the Activation gate below covers. It never simulates a committee, predicts satisfaction,
or makes a human-subjects determination.

Canonical schema:
`shared/contracts/human_subjects/committee_correspondence.schema.json`.
Artifact version: `committee-correspondence/1.0`.
Deterministic checker: `scripts/check_committee_correspondence.py`.
Design authority:
`docs/design/2026-08-08-668-committee-correspondence-spec.md`.

## Activation gate

Use this variant only when the user explicitly identifies the input as comments or
a letter from a review that this gate covers, and asks for tracking, response preparation, or
resubmission organization. Do not infer official authority
from formal tone, letterhead-like prose, words such as “required,” or a file name.

If the source is ordinary manuscript peer review, use normal `revision-coach`.
Journal or conference reviewers, editors, area chairs, and program committees are
peer review, even when the user names the venue or the venue calls the role a
committee (#854).
This variant covers only a letter or comments from a research ethics or human-subjects
protection review of research with human participants, their data, or their biological
samples, made by a body with formal review authority over the study, such as a research
ethics committee, an institutional review board (IRB), or a human research ethics office.
The kind of review decides, not the topic of each comment: such a review's comments on
statistics, data access, or safety monitoring stay in the variant. A formal review that
such a body holds to decide whether the study needs its review also counts. A mock or advisory
review before submission does not count. A review held for another purpose (scientific
merit, statistics, data access, or safety monitoring), a thesis or dissertation
committee, and a grant or funding panel take normal `revision-coach` (#907). This gate
is the one full statement of the variant's scope; the other entry points point here,
and comments that it excludes take normal `revision-coach` (#907).

Before taking this branch, start the reply with the user's own words that name the
body, in quotation marks. If the user's own turns do not name it (for example, the name
appears only in the pasted letter), ask the user which body sent the comments and in
what review, and quote that answer; a reply of only yes or no does not name the body,
so ask again (#907).

If the source identity is uncertain, ask the user to identify it as above
before choosing the variant. V1 accepts UTF-8 letter text. For a binary PDF/DOCX,
retain the user’s original file outside this bundle and obtain a UTF-8
export/transcription; label that textual source honestly rather than claiming byte
identity with the binary.

This variant is standalone and separate from paper-review traceability. It MUST NOT:

- emit Schema 11 `commitment_extracted` or a peer-review Revision Roadmap;
- assign Major/Minor/Editorial, P1/P2/P3, severity, or model priority;
- write to the Material Passport or claim a Stage 4.5 integrity pass;
- state that a concern is resolved, that a response will satisfy the committee, or
  that any artifact is submission-ready;
- translate committee wording into another jurisdiction’s taxonomy.

## Required interaction

Start the reply with the user's own words that name the body, in quotation marks
(see the Activation gate). Then:

1. Preserve the supplied UTF-8 text exactly as `source_letter.txt`. Do not normalize
   newlines, whitespace, punctuation, or spelling.
2. Segment every byte from zero through EOF into `comment` or `non_comment` rows.
   Headers, sign-offs, decision metadata, and other non-comment text remain visible.
3. Show the byte-complete segmentation to the user. The user confirms or corrects
   comment boundaries before the tracker is final.
4. Create one concern per confirmed comment segment in source order. A compound
   comment remains one concern with multiple `action_type` values. Separately
   numbered subcomments may be separate segments.
5. Copy `verbatim_text` from the exact source bytes. Compute all SHA-256 fields and
   byte ranges; do not ask a model to reproduce hashes from memory.
6. Classify `authority_status` only from explicit committee language or author
   confirmation. When neither exists, use `unclear` plus an unresolved basis.
7. Fill artifact, owner, dependency, and required-before fields only when the letter,
   author, or selected profile supplies them. Empty/unresolved is valid and preferred
   to inference.
8. Present the concern records to the user for confirmation. Working views may
   reorder the complete concern set but never replace source order.
9. Emit the placeholder-only response skeleton. It contains one concern marker,
   author-response placeholder, and evidence placeholder per concern.
10. Run the deterministic checker and report any failure without claiming partial
    completion.

## Bundle layout

Use `committee_correspondence/<source_sha256_first_12>/`:

```text
<12-hex>/
├── source_letter.txt
├── concern_tracker.json
└── response_skeleton.md
```

All tracker paths are bundle-relative. Never point the checker at arbitrary local
files through a tracker path. Do not use symlinks.

## Classification vocabulary

`authority_status` is one of:

- `explicitly_required` — the source explicitly requires the action;
- `conditional` — the source states an if/then or contingent requirement;
- `question` — the source asks for information without settling the answer;
- `suggestion` — the source explicitly presents an optional suggestion;
- `unclear` — none of the above is textually supported or the user has not confirmed.

`action_type[]` is multi-valued:

- `design`
- `explanation`
- `revise_artifact`
- `add_artifact`
- `administrative`
- `legal_or_policy_check`

Do not collapse a compound comment into a single label. Do not add a priority or
severity field. Source order is not priority.

## Optional authority-profile enrichment

No selected profile is a supported terminal input state:

```json
{
  "state": "not_selected",
  "selected_profile_ids": [],
  "artifact_resolution_state": "artifact_agnostic"
}
```

When a user later selects a #666 profile, profile-derived artifact names and
requirement ids carry explicit provenance. The profile cannot rewrite source text,
authority status, owner, deadline, dependency, or order. A failed lookup uses
`artifact_resolution_state=unresolved`; it does not silently fall back to another
jurisdiction.

## Response skeleton

The skeleton begins with exactly:

```markdown
Status: drafting aid — no concern is asserted resolved.
```

Each concern block uses:

```markdown
<!-- concern:CC-001 -->
### Concern CC-001

**Draft response:** [AUTHOR RESPONSE REQUIRED — drafting aid; do not claim resolved]

**Evidence:** [EVIDENCE OR ARTIFACT POINTER REQUIRED]
```

It ends with exactly:

```markdown
> **Human-subjects boundary:** This output does not authorize recruitment, consent, access to identifiable data, intervention, or data collection.
```

The skeleton is not a completed response and contains no claim that work occurred.
During later drafting, keep the original skeleton as the checked baseline; save a
drafted response as a separate artifact rather than overwriting its hash-bound
placeholder state.

## Handoff

After user confirmation and a passing checker result, hand off both
`concern_tracker.json` and `response_skeleton.md` to response drafting or
resubmission work. Downstream work joins on `concern_id` and preserves the source
locator. Evidence remains absent until the author supplies a real artifact pointer.

Run:

```bash
python scripts/check_committee_correspondence.py \
  committee_correspondence/<12-hex>/concern_tracker.json
```
