# panel-synthesis fixtures (#510)

`full-consistent/` — one canonical `reviewer_full` round (3 reviewers with two
mandatory warns each, 2 all-pass) whose consistent synthesis is
`fired_conditions: [F2]` + `editorial_decision=major_revision` under the
simple-majority quantifier (3-of-5). Consumed by the CLI integration tests in
`scripts/test_check_panel_synthesis.py`; all mutation cases are in-code
transforms of the same builder, not extra files.

Regenerate: the fixture-authoring snippet in
`docs/superpowers/plans/2026-07-15-510-panel-synthesis-checker.md` Task 5.
