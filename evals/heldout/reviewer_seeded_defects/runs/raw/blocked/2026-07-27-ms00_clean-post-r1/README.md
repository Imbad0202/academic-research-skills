# Provenance-invalid panel evidence: 2026-07-27 MS00 post r1

This panel reached synthesis, but it is invalid for scoring and gate calculations.

The methodology seat's first Phase 1 response omitted the mandatory D3
`what_triggers_fatal:` line. The dispatcher used the protocol-permitted single
paper-blind structural retry, but overwrote that first response. `dispatch.log`
preserves the exact checker diagnostic and chronology; `final-panel.review.md`
preserves the final conforming Phase 1, all five Phase 2 cards, and synthesis.
Neither artifact can reconstruct the missing first response or prove its paper
blindness independently.

The final panel is retained as diagnostic evidence only. It is deliberately not
named with the normal `<run-record-stem>.review.md` pattern, and its status record
is under `../../../blocked/2026-07-27-ms00_clean-post-r1.json`. Do not adjudicate
it as a valid run, include its observed finding count in a replicate mean, or use
it for an acceptance gate.
