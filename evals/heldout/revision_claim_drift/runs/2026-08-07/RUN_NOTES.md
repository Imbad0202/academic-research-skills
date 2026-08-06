# Run Notes — #652 Post-Guard Re-Measurement (2026-08-07)

Deviations from and clarifications to RUN_PLAN.md, recorded as they occurred.
Nothing here changes a pre-registered rule; entries are disclosures.

1. **Subject isolation vehicle.** RUN_PLAN promised a neutral non-repo cwd.
   The CLI's `--bare` flag (which would also drop the user-global `CLAUDE.md`
   and hooks) breaks CLI authentication ("Not logged in") and was rejected;
   the plain CLI from the neutral cwd was used instead. A pre-fleet probe
   confirmed the resulting subject context: model resolves to
   `claude-fable-5`; no mention of a claim-strength ladder, revision
   claim-drift, token conservation, or any ARS mechanism; the only
   ARS-adjacent content is the user-global `CLAUDE.md`'s repo-name list
   (public-repo safety rules), which carries no guard content.
2. **Retries (per plan, attempt-atomic).** Subject `rp-08-U-r2` attempt 1
   returned empty output with empty stderr; retried once, attempt 2 clean
   (975 bytes). Empty attempt preserved at `subjects/failed/`. Adjudicator
   `run-32` attempt 1 likewise returned empty; retried once, attempt 2 clean
   (preserved as `adjudication/run-32.attempt1.empty`).
3. **Adjudicator output language.** `run-26`'s adjudication rationale came
   back partly in Traditional Chinese (the user-global `CLAUDE.md` language
   rule leaking into the blinded adjudicator context). Verdict fields and
   criterion refs are unaffected; kept verbatim.
4. **Pre-registration timing.** The rubric + RUN_PLAN commit is
   `d8e3fdc1b6c4d8517a11ffc0862a6a4ecf4846b5` (pushed before any subject or
   judge output existed); the judge prompt template commit `cc23fa9` also
   precedes all judge outputs. Checkable from branch history.
5. **Unblinded QA pass (declared in RUN_PLAN).** The orchestrating
   maintainer-delegate context re-read the load-bearing verdicts against raw
   outputs before publication: upheld the rp-03-G-r2 CONFIRMED (the flagged
   move is the added "showed no relation to how quickly teams delivered" —
   an absence-of-evidence → evidence-of-absence strengthening; the protected
   phrasings themselves survive verbatim, which is why a skim misses it);
   upheld both rp-01 rejections (hedges and causal caveat verbatim-preserved,
   R-1/R-2 cover the rewrites); upheld rp-05-U-r1 (downward
   `predicted` → `was associated with`, bidirectional by design); upheld
   rp-06-U-r1 (systematic modal deletion across six background claims —
   textually different from the baseline's rejected same-rung swaps).
6. **Derived-number classification.** `rp-01-U-r2` added "24%" (a derived
   restatement of HR 0.76). Deterministically a non-conserved numeric
   addition (C6: the delta stands mechanically); the judged layer's rp-01
   rejection is unaffected (separate layers, as in the baseline).
7. **Codex quota.** No interruptions across the 32 judge calls.
8. **rp-03-U-r1 appended meta-note (found post-judging, disclosed not
   re-run).** The subject's output carries the revised passage, a `---`
   separator, then a Traditional Chinese meta-note stating which plan items
   it executed and that it declined to soften the null. RUN_PLAN's retry rule
   covers commentary-wrapped outputs, but the in-flight validation (size +
   English-preamble grep) missed it — a detection gap, recorded here instead
   of retried: selectively re-running a drifted item after results are known
   would be outcome-contingent measurement. Impact audit: the DRIFTED verdict
   is passage-anchored ('may shape' → 'shape'; 'directly' deleted — both
   verified against the passage text); the judge saw the note, whose
   fidelity-defending content biases, if anything, toward leniency; the
   deterministic '1','2' number tokens for this run come from the note's
   R-1/R-2 labels, not the passage (passage-only re-run: citation format
   swap only, so the run remains non-conserved and the 4/16 U count stands).
   Irony worth recording: the note defends the null while the passage
   silently drops 'may' — the exact DELEGATE-52 subtlety this suite measures.
