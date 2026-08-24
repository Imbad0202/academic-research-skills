# #684 expert-stage readiness check — 2026-08-24

**Evidence commit:** `5cc3e93a8b11d0bc2363bde0e18cff79559e9714`
**Verdict:** subject execution is complete and replay-valid; the measurement is
blocked only at the independent human-expert stage.

This check used a detached worktree at the evidence commit. It did not expose
or reconstruct the private arm map, create labels, contact an expert, or run a
model/API call.

## Replayed checks

- `run_review_criteria_constructive_value.py validate-assets`: PASS — 16
  locked assets, six items, and 24 planned calls.
- Focused runner/scorer/#684 integration suite: PASS — 59 tests.
- Retained execution inventory: 24 prompts, outputs, receipts, and event
  streams; no replacement call was made.
- Blinded expert packet: 24 outputs; arm identity, mechanism state, other
  experts, raw aggregate, and expected direction are withheld.

## Frozen bindings

| Artifact | SHA-256 |
|---|---|
| run plan | `a8691eea4c60931057a2e5deb035463b1aed82a444bfe47f185d78866b6d5c43` |
| execution manifest | `41e43e5847f682382af2569f35b76f764476120649de3b309cb9ce44a5a40779` |
| expert packet | `9f6c14026cb89d384c364663a1fa55b9960d374ce4a9edb687170f75b03e2e76` |

## Remaining authorized sequence

1. At least two independent human experts receive only the frozen packet and
   guide and return separate schema-valid label files.
2. A separate human adjudicator, still blind to arm, resolves only permitted
   disagreements and returns the closed adjudication file.
3. Run `validate-labels`, `finalize`, and `build-report` against those retained
   human artifacts.
4. Publish the resulting `heldout-measurement/1.1` row regardless of favorable,
   null, mixed, or adverse direction.

Until those people and artifacts exist, the correct state is
`status/blocked`; agent/model judgments cannot satisfy the human-expert
exception selected by the preregistered plan.
