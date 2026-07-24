# Raw panel outputs (audit evidence for the run records)

One file per run, named `<run-record-stem>.review.md`: the complete, verbatim output of
that run's blinded full-mode panel — field-analyst configuration, all five seats'
two-phase reports, and the Editorial Decision Letter — as written by the isolated
review subagent. These files are the evidence base that makes the sibling
`../*.json` records re-adjudicable: the line anchors cited in the JSON `notes`
(e.g. "R1 W1 L341") resolve against these files, DETECTED/PARTIAL calls can be
re-classified from the full text, and the clean-control zero-false-findings claim
can be verified only against the complete reports.

**Redaction note:** the only edit relative to the subagents' verbatim output is a
line-preserving replacement of one specific publisher name with `[publisher]`, per
the maintainer's repo-boundary deny-list. Other public bibliographic names (real
journals and publishers the field analyst recommended as target venues) are not on
that list and are intentionally left verbatim. Because the redaction preserves line
structure, all line anchors in the run records remain valid.

**Contamination reminder:** these are *outputs* of past measurement runs, not ground
truth — but they live under `evals/`, which review sessions are already forbidden to
read under the measurement protocol. Never paste them into a review session's context.
