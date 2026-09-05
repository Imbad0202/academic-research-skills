# Risk Register: Risk → Control → Evidence Status → Residual Gap

**Purpose.** The suite's known risks are each handled somewhere — the citation gate,
the claim-drift guards, the consent surfaces, the capability matrix — but those
mechanisms live in different files. This register is the single artifact that links
each standing risk to its existing controls, the evidence status behind them, and
what is still open, so that when a new mechanism ships there is one place to answer:
which risk does this retire, and what remains?

**Origin.** ISO/IEC 42001-spirit gap assessment
([`audits/iso42001-spirit-gap-assessment-2026-08-17.md`](../audits/iso42001-spirit-gap-assessment-2026-08-17.md),
finding F-1, [#759](https://github.com/Imbad0202/academic-research-skills/issues/759)).
This is the deliberately lightweight substitute for a formal AIMS risk process, which
was assessed and rejected as disproportionate for a solo-maintained repo (assessment
§6). Feasibility here is one of this repo's distilled operating principles (with
informative anchors to ISO/IEC 42001) — not an ISO-mandated artifact.

**Posture.** The register indexes, it never re-authors. Each row cites its controls
where they are defined and mirrors its evidence status from the stage capability
matrix ([`shared/contracts/capability/stage_capability_matrix.json`](../shared/contracts/capability/stage_capability_matrix.json),
rendered at [STAGE_CAPABILITY_MATRIX.md](STAGE_CAPABILITY_MATRIX.md)); it never
redefines a control or upgrades a status. Statuses use the matrix vocabulary
(`DESIGNED` / `NOT_RUN` / `MEASURED` / `MIXED`). A status citing a named matrix row
is lint-pinned to that row's recorded `behavioral_evidence.status` by
`scripts/check_risk_register.py`; a status marked as asserted-here is a maintainer
assertion with no matrix backing, and may only carry a no-measurement status: the
matrix stays the sole authority for `MEASURED`/`MIXED`. An open issue in a Residual
gap cell is the honest answer, not a defect being hidden: `NOT_RUN` means exactly
that. Two authoring constraints keep this file checkable: a backtick code span
containing a slash is treated as a repo path that must exist, and the citation
phrasings are reserved for well-formed citations.

## Risks

### R1 — Hallucinated citations

A generated reference does not exist, or a real reference is cited for a claim it
does not support.

- **Existing controls**: deterministic four-index existence gate
  (`scripts/verify_passport.py`, `scripts/verification_gate/__init__.py`) with opt-in
  terminal policies (`shared/contracts/passport/terminal_policies.schema.json`);
  locator-bearing citation emission (`scripts/check_v3_7_3_three_layer_citation.py`);
  Phase E claim verification for the supports-the-claim half.
- **Evidence status**: `NOT_RUN` (capability matrix row `retrieval.citation_existence_gate`);
  `NOT_RUN` (capability matrix row `integrity_check.claim_verification`).
- **Residual gap**: no measured hallucinated-citation catch rate — that needs an
  independently-authored ground-truth set, not one derived from the gate's own
  reducer; the Claim Registry's semantic completeness is unknown by contract. No
  open issue schedules either measurement yet. The vendor's own evaluation of the
  current session model reports fabricated references as rare and misrepresented
  findings or conclusions as the residual error class that needs domain
  familiarity to catch (Claude Fable 5.1 system card §2.2.4), which moves the
  weight of this row onto the supports-the-claim half — exactly the unmeasured
  claim-verification row above.

### R2 — Silent claim-strength drift in revision

A revision round strengthens or weakens a claim without an authorizing roadmap item.

- **Existing controls**: claim-strength ladder
  (`shared/references/claim_strength_ladder.md`); deterministic token conservation
  (`scripts/check_revision_token_conservation.py`); advisory Phase E6 drift check.
- **Evidence status**: `MEASURED` (capability matrix row `revision.claim_drift_guard`).
- **Residual gap**: the measured row covers a condensed guard-block prompt, not the
  shipped pipeline path as-wired, and licenses no causal claim; re-measurement after
  any change is a manual maintainer action.

### R3 — Indirect prompt injection via retrieved content

Text retrieved from a source carries instructions that an agent follows as if they
came from the user.

- **Existing controls**: the retrieved-content instruction/data boundary as a
  standing principle (#367); the offline structural probe
  (`scripts/run_indirect_prompt_injection_probe.py`), which by design never
  dispatches a model.
- **Evidence status**: `DESIGNED` (asserted here; no capability-matrix row) — the
  probe checks structure, so no behavioral injection-resistance number exists.
- **Residual gap**: live injection behavior unmeasured
  ([#675](https://github.com/Imbad0202/academic-research-skills/issues/675));
  structural instruction/data isolation at the task-envelope boundary is design work
  ([#676](https://github.com/Imbad0202/academic-research-skills/issues/676)).

### R4 — Unpublished-content exposure via cross-model transport

A consented second-model call carries unpublished manuscript content to an external
provider.

- **Existing controls**: consent-gated transport with explicit per-call surfaces
  (`shared/cross_model_verification.md`); the single user-facing network map
  (`docs/DATA_FLOWS.md`); the contained, bounded subscription transport protocol.
- **Evidence status**: `NOT_RUN` (asserted here; no capability-matrix row) — the
  deterministic envelope pieces are CI-pinned; behavioral compliance with the
  consent contract is unmeasured.
- **Residual gap**: consent surfaces are prompt-contract layers whose behavior
  varies with the session model; the no-autonomous-publication line is a scope
  boundary and review criterion, not a runtime guarantee (`POSITIONING.md`).
  Provider-side safety monitoring may escalate a flagged conversation to human
  review at the provider (`shared/cross_model_verification.md` § Provider-side
  monitoring and safety interventions), so consent has to assume provider staff
  may read what is sent.

### R5 — Upstream model-version behavior drift

A new session-model version silently changes behavior that older measurements
described.

- **Existing controls**: commit-frozen measurement rows re-measured per change; the
  matrix staleness rule (`stale_after_days`); periodic harness-retirement audits
  (`audits/harness-retirement-2026-09-model-update.md` is the most recent
  completed report, run on the Fable 5 → Fable 5.1 and GPT-5.6 Sol → GPT-6 Astra
  change).
- **Evidence status**: `NOT_RUN` (asserted here; no capability-matrix row) — no
  measurement of cross-version drift itself exists.
- **Residual gap**: measured rows are model- and time-specific by contract;
  re-running them on a model change is a manual maintainer action, not automated.
  The session model can also change per request without a version change: the
  runtime's classifier-triggered fallback is invisible to the suite
  (`shared/model_tiering.md`, the declared-model note under Resolving a tier at
  dispatch time), so every "session model" in a provenance record is the declared
  model, not a per-call attestation.

### R6 — Correlated same-family model error

Generator and reviewer share a model family, so both miss the same failures.

- **Existing controls**: optional cross-model verification and the cross-model
  reviewer track (`shared/cross_model_verification.md`); the Review Panel Provenance
  block's single-family correlated-error caveat; the same-family calibration
  epistemic note.
- **Evidence status**: `NOT_RUN` (capability matrix row `review.calibration`).
- **Residual gap**: first measured reviewer error profile pending
  ([#653](https://github.com/Imbad0202/academic-research-skills/issues/653)); a
  second model is an error-detection control, not organizational independence.
  A second model is also only as observable as its outputs: the current OpenAI
  verifier's vendor reports that covert underperformance by that model would
  likely evade the vendor's own monitors (GPT-6 Astra system card §9.2.2.3), and
  ARS's typed evidence anchors bound what a verifier can assert, not what it
  withholds.

### R7 — User over-reliance / rubber-stamping

The researcher approves AI output without reading it, and attestations become
rubber stamps.

- **Existing controls**: read-scope attestation as declaration-not-proof
  (`/ars-mark-read` requires an explicit scope); the override ladder with recorded
  reasoning (`shared/compliance_checkpoint_protocol.md`); the advisory
  collaboration-depth observer (`shared/collaboration_depth_rubric.md`).
- **Evidence status**: `NOT_RUN` (asserted here; no capability-matrix row).
- **Residual gap**: these are trust-based controls with audit trails, not coercive
  controls — final integrity responsibility stays with the human researcher, and no
  evaluation measures over-reliance itself.

### R8 — Venue-policy staleness

Disclosure guidance cites a venue policy the venue has since changed.

- **Existing controls**: disclosure mode with per-venue policy anchors
  (`academic-paper/references/disclosure_mode_protocol.md`).
- **Evidence status**: `NOT_RUN` (asserted here; no capability-matrix row).
- **Residual gap**: no live policy re-validation exists; the user must confirm
  against the venue's current text before submission.

### R9 — Dependency / supply-chain compromise

A compromised or drifting third-party dependency alters suite behavior.

- **Existing controls**: stdlib-first runtime scripts; a small declared
  dev-dependency manifest (`requirements-dev.txt`, lower-bound pins only, no
  lockfile); the plugin-agent tools allowlist (`scripts/check_tools_allowlist.py`);
  CI lints running repo-side in GitHub Actions.
- **Evidence status**: `NOT_RUN` (asserted here; no capability-matrix row).
- **Residual gap**: no SBOM or supplier-review program — assessed and rejected as
  disproportionate (assessment §6); dev dependencies carry no exact version or hash
  locking; dependency changes ride ordinary code review.

### R10 — Install-channel enforcement loss

A user installs through a channel where documented enforcement never runs.

- **Existing controls**: the per-channel availability matrix
  (`docs/CONTROL_AVAILABILITY.md`); the write-scope guard's disclosed degrade posture
  (`hooks/run_guard.sh`), indexed as five `write_scope_guard_*` rows in the
  degradation registry (`shared/contracts/degradation_registry.json`,
  [#769](https://github.com/Imbad0202/academic-research-skills/issues/769));
  per-channel notes in `docs/SETUP.md`.
- **Evidence status**: `NOT_RUN` (asserted here; no capability-matrix row) —
  availability is documented; loss-of-enforcement behavior is not separately
  measured.
- **Residual gap**: what each channel loses is per-mechanism (see the availability
  matrix): prompt-level protocols survive in most non-plugin channels but are absent
  in claude.ai Projects, and hook enforcement is absent outside the plugin channel
  unless the user wires the hook into their own settings manually (matrix note 3).

### R11 — Fabricated or distorted checkpoint authority

The orchestrating model treats something other than the researcher's own turn as
a checkpoint decision — an automated message, a subagent's report, a template
default, or its own paraphrase — or restates the researcher's decision to a
subagent as a broader authorization than was given.

- **Existing controls**: MANDATORY checkpoint templates that wait for an explicit
  user turn (`academic-pipeline/references/pipeline_state_machine.md`); the
  orchestrator's checkpoint-authority fidelity rule
  (`academic-pipeline/agents/pipeline_orchestrator_agent.md`); deterministic
  authorization inputs that bind an author choice to exact patch bytes
  (`scripts/revision_roadmap.py`, the #670 integrity-correction authorization);
  read attestations that are declared, never inferred (`/ars-mark-read`).
- **Evidence status**: `NOT_RUN` (asserted here; no capability-matrix row) — the
  deterministic authorization inputs are CI-pinned; the prompt-level rule is not
  measured on any session model.
- **Residual gap**: the failure class is vendor-documented, not ARS-measured
  (evidence mapped in `audits/harness-retirement-2026-09-model-update.md` G-1);
  the prompt rule is trust-based.
