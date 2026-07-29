# P-5 — Expected change surface as a navigation hypothesis (SD-10)

**HELD OUT.** Never enters a measured run's context.

| Field | Value |
|-------|-------|
| Controlled factor | Where the fix landed and whether it satisfies the criterion |
| Held constant | Roadmap, decision letter, Round-1 findings, config cards, original manuscript |
| Arms | `arm-a` = fix at the expected surface; `arm-b` = equivalent fix elsewhere; `arm-c` = cosmetic edit AT the expected surface |
| Spec definition | §14 P-5 |

## Construct, and one honest caveat about the letter

The Phase-1 record for REV-001 should set `expected_change_surface` to **§4.2 Measurement** —
that is where the Round-1 finding points and where a reader would look first. It is a
navigation hypothesis, not a requirement (§3.2, SD-10).

The Response to Reviewers is **arm-supplied** here, and it truthfully describes each arm's
edit. It is therefore a *dependent* of the controlled factor, not a second independent
variable: a letter that pointed at §4.2 in the arm that edited Appendix C would be a lie and
would confound P-5 with P-2. Arm-c's letter is truthful too, and that is the point — "Section
4.2 has been substantially expanded" is a true statement about an edit that does not satisfy
the criterion.

## Expected per-item outcome

| Item | Priority | arm-a | arm-b | arm-c |
|------|----------|-------|-------|-------|
| REV-001 | `must_fix` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` | `NOT_ADDRESSED` |
| REV-002 | `must_fix` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` |
| REV-003 | `must_fix` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` | `FULLY_ADDRESSED` |

### REV-001 `evidence_anchor` location — the cell that carries P-5

| Arm | Expected anchor location | Note |
|-----|--------------------------|------|
| arm-a | revised §4.2 (the alpha / omega sentence) | at the expected surface |
| arm-b | revised **Appendix C** (the CFA fit indices) | **not** at the expected surface, and correct |
| arm-c | — (`NOT_ADDRESSED` carries an anchor showing what is there, or none) | — |

**a↔b is the SD-10 test.** The verdict cell must be `identical` (`FULLY_ADDRESSED` in both)
while the anchor cell must `differ`. A run that downgrades arm-b because the fix is not in
§4.2 has turned the navigation hypothesis into a location requirement — the exact reading
SD-10 forbids: "a fix elsewhere that satisfies `operationalization.fully_addressed` counts".

The criterion is explicitly disjunctive and explicitly about *this sample*: an
internal-consistency coefficient computed on this sample, **or** a measurement model with fit
indices estimated on this sample. Arm-a takes the first disjunct, arm-b the second. Both are
satisfied on the merits.

### Why arm-c is `NOT_ADDRESSED`

Arm-c's §4.2 grows from two sentences to nine. It adds the instrument's provenance, its four
content areas, the item count per area, the scoring range, the administration mode and
timing, the number of translations, and the direction of scoring. Every one of those is
descriptive. The only reliability figure it introduces is `alpha = .88` **from the original
validation** — that is the prior-study reliability the Round-1 finding already ruled out:
"Prior-study reliability is not evidence about this sample" (roadmap `description`), and "that
tells us the scale worked in someone else's sample" (Reviewer 2's finding).

So the expected surface was edited, substantially, in good faith, and the criterion is
untouched. §3.2's rationale for keeping `expected_change_surface` at all is exactly this:
"the surface exists so a cosmetic edit at the expected location cannot satisfy the item by
position alone."

`PARTIALLY_ADDRESSED` would be wrong here, and worth recording as a miss if it occurs: the
criterion's `partially_addressed` operationalization should be something like "a coefficient
computed on this sample is reported for a subscale only, or a measurement model is reported
without fit indices" — an incomplete step toward this-sample evidence. Arm-c takes no step
toward it; it elaborates around it.

## Expected decision

| Observable | arm-a | arm-b | arm-c |
|------------|-------|-------|-------|
| `decision_state` | `Accept` (B6) | `Accept` (B6) | `Major Revision` (B3) |
| `reject_recommended` | `false` | `false` | `false` |
| `revision` | 1 | 1 | 1 |

Arm-c: 1 of 3 P1 items unaddressed = 33% < 50%, so B2 does not fire and no
`reject_recommended` is set; B3 carries it.

## Adjustment records

None expected in any arm. Each arm's Phase 2A already reaches its final verdict from the
manuscripts alone; the letters add no verdict-moving evidence. In particular arm-b's Phase 2A
should locate Appendix C **without** the letter — the appendix is in the revised manuscript
and the patch adds it. A run that only finds Appendix C after reading the letter and books an
`author_pointer_located_evidence` adjustment has reached the right verdict by the wrong route.
**P-5 declares no adjustment cell**, so this is not a pair-metric miss and must not be scored as
one — inventing a cell here would put P-5's denominator at 8 against a pinned 7. Record it in the
run record under the secondary absolute-correctness metric, where an arm's full expected
observable set is what is compared.

## Pair structure

| Pair | Observable | Relation | Target | Expected |
|------|-----------|----------|--------|----------|
| **a↔b** | `final_verdict` | **identical** | REV-001 | `FULLY_ADDRESSED` both |
| **a↔b** | `evidence_anchor_location` | **differs** | REV-001 | §4.2 vs Appendix C |
| a↔b | `decision_state` | identical | — | `Accept` both |
| a↔c | `final_verdict` | differs | REV-001 | `FULLY_ADDRESSED` vs `NOT_ADDRESSED` |
| a↔c | `decision_state` | differs | — | `Accept` vs `Major Revision` |
| b↔c | `final_verdict` | differs | REV-001 | `FULLY_ADDRESSED` vs `NOT_ADDRESSED` |
| b↔c | `decision_state` | differs | — | `Accept` vs `Major Revision` |

a↔b is a same-verdict/different-anchor pair, which no other scenario in the set contains. It
is the reason P-5 has three arms rather than two: location-tolerance and
position-insufficiency are opposite errors, and a two-arm design can only catch one of them.

## Rule anchors

- SD-10 — `expected_change_surface` is a navigation hypothesis, not a mandatory location; equivalent fixes count
- §3.2 — `expected_change_surface` definition and the cosmetic-edit-at-the-surface rationale; `operationalization.fully_addressed` is a concrete evidence pattern
- §3.3 — `evidence_anchor` typed into the REVISED manuscript
- §3.4 — `author_pointer_located_evidence` basis (expected absent here)
- §6 Step 2 B2, B3, B6
