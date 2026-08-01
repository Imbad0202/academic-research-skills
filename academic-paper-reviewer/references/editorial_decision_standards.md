# Editorial Decision Standards — Criteria for Editorial Decision Making

This document defines the explicit criteria for Accept / Minor Revision / Major Revision / Reject decisions, for use by `eic_agent` and `editorial_synthesizer_agent`.

---

## 0. Decision Authority by Mode

| Mode | Decision engine | Working scale | Output |
|------|-----------------|---------------|--------|
| `full` (sprint contract) | Mechanical synthesizer over reviewer contract v2; the matrix below never overrides it | `block/warn/pass` + `block_class` | Accept / Minor Revision / Major Revision / Reject |
| `methodology-focus` (sprint contract) | Same mechanical engine, scoped to methods + presentation; no venue-fit dimension | same | four-value enum |
| `full` / `methodology-focus` without a contract | Synthesis Protocol + the qualitative criteria and recommendation matrix in this file | reviewer recommendations | four-value enum |
| `re-review` | #576 three-gate contract: `re_review_mode_protocol.md` § Decision Derivation, recomputed by `scripts/check_re_review_synthesis.py` | item verdicts (FULLY/PARTIALLY/NOT_ADDRESSED/MADE_WORSE/CANNOT_VERIFY) | Accept / Minor Revision / Major Revision / user_review_required (Reject is not a Stage 3' decision) |
| `quick` | Journal-Fit Reviewer assessment only; advisory, not an editorial decision | — | signal |
| `guided` | Issue-list dialogue; no editorial decision letter | — | — |
| `calibration` | `quality_rubrics.md` 0–100 Decision Mapping, measurement-only | 0–100 | four-value labels against the gold set |

Under a sprint contract, the mechanical synthesizer governs. This file's recommendation matrix is the no-contract path and cannot soften, harden, or override a fired contract action. Numeric decision thresholds live only in `quality_rubrics.md` § Decision Mapping; this file uses qualitative criteria and reviewer-recommendation counts.

---

## 1. Decision Categories

### Decision Symmetry and Register Independence (#574 B1)

These principles govern every category below:

- **Symmetric evidence standards.** An Accept conclusion and a Reject conclusion carry the same evidence burden: Accept requires positive, anchored verification that each criterion is met, exactly as Reject requires anchored evidence that criteria failed. Neither direction gets a wider margin of caution.
- **Decisions follow criteria, not distributions.** Review rigor comes from the venue's actual criteria and article-type expectations (Reviewer Configuration Card), never from acceptance-rate base rates or an expected decision distribution. Base rates describe other papers, not this one; a review round that produces more rejections is not thereby a better round.
- **Register is independent of severity.** Tone rules (respectful, constructive) govern WORDING only. They never lower a finding's severity or soften a decision, and adversarial or rigor-signaling framing never raises a severity or hardens a decision.

### Accept

**Definition**: The paper can be published without further review.

**Criteria**:
- Every applicable core criterion is positively verified
- No unresolved decision-bearing weakness remains
- At least 3/4 reviewers recommend Accept or Minor Revision
- No unresolved major academic issues

**Conditions**:
- May include minor copyediting suggestions
- May require final formatting adjustments
- Does not need to be sent for review again

**Typical scenarios**:
- Paper has undergone multiple revision rounds, all issues resolved
- First-pass acceptance when the paper genuinely meets every criterion — the decision follows the criteria, never a frequency expectation (#574 B1: no base-rate anchoring, qualitative or numeric)

---

### Minor Revision

**Definition**: The paper is fundamentally acceptable and can be published after limited modifications; typically does not need to be sent for review again after revision.

**Criteria**:
- The paper is fundamentally acceptable and remaining issues are limited
- No issue requires restructuring core arguments or methods
- At least 3/4 reviewers recommend Accept or Minor Revision
- Issues can be resolved within 2-4 weeks
- Modifications do not involve restructuring core arguments or methods

**Typical revision items**:
- Supplementing a small number of references
- Clarifying certain methodology description details
- Improving clarity of argumentation
- Correcting citation format
- Adding discussion of limitations
- Adjusting conclusion wording (avoiding overclaiming)

**Response requirements**:
- Authors must respond to reviewer comments item by item
- After revision, reviewed by the journal's handling editor (usually not sent for external review again)
- Revision deadline: 2-4 weeks

---

### Major Revision

**Definition**: The paper has potential but has significant issues, requiring substantial revision followed by re-review.

**Criteria**:
- One or more material weaknesses require substantial revision
- The weaknesses are repairable rather than fatal
- At least 2/4 reviewers recommend Major Revision or better
- Issues are serious but fixable (not fundamental design flaws)
- Revision requires 6-8 weeks of work

**Typical revision items**:
- Re-analyzing data (additional analysis or correcting errors)
- Substantially rewriting literature review (missing key references)
- Supplementing additional data collection
- Reorganizing paper structure
- Correcting significant methodological flaws
- Strengthening theoretical framework application
- Adding robustness checks

**Response requirements**:
- Authors must write a detailed point-by-point response letter
- After revision, sent for re-review (may go back to original reviewers or new reviewers)
- Revision deadline: 6-8 weeks
- Typically a maximum of 2 rounds of Major Revision allowed

---

### Reject

**Definition**: The paper is not suitable for publication in this journal, even with revision.

**Criteria (meeting any one may trigger Reject consideration)**:
- A core criterion has a fundamental unfixable failure
- The paper cannot become suitable for this venue through revision
- At least 3/4 reviewers recommend Reject
- Fundamental unfixable issues exist

**Reject subtypes**:

| Subtype | Description | Suggestion |
|---------|-------------|-----------|
| **Reject — Out of Scope** | Topic not within journal scope | Recommend more suitable journals |
| **Reject — Fundamental Flaw** | Fatal flaw in research design | Suggest redesigning the research |
| **Reject — Insufficient Contribution** | Lacks originality or incremental contribution | Suggest how to strengthen contribution |
| **Reject — Premature** | Paper not yet mature enough | Suggest specific improvement directions |
| **Reject — Resubmit Encouraged** | Has potential but needs fundamental restructuring | Provide detailed restructuring suggestions |

**Even with Reject, must**:
- Affirm genuine merits where they exist — do not manufacture praise to soften the decision (#574 A1/B1)
- Provide specific improvement suggestions
- Recommend more suitable journals (if it's a scope issue)
- Maintain professional, respectful tone

---

## 2. Decision Matrix

### Decision Matrix Based on Reviewer Recommendations

| Journal-Fit Reviewer | R1 | R2 | R3 | -> Recommended Decision |
|----------------------|----|----|-----|----------------------|
| Accept | Accept | Accept | Accept | **Accept** |
| Accept | Accept | Accept | Minor | **Accept** (with suggestions) |
| Accept | Accept | Minor | Minor | **Minor Revision** |
| Accept | Minor | Minor | Minor | **Minor Revision** |
| Minor | Minor | Minor | Minor | **Minor Revision** |
| Minor | Minor | Minor | Major | **Minor-to-Major** (depends on specific issues) |
| Minor | Minor | Major | Major | **Major Revision** |
| Minor | Major | Major | Major | **Major Revision** |
| Major | Major | Major | Major | **Major Revision** |
| Major | Major | Major | Reject | **Major Revision** (last chance) |
| Major | Major | Reject | Reject | **Reject** (resubmit encouraged) |
| Major | Reject | Reject | Reject | **Reject** |
| Reject | Reject | Reject | Reject | **Reject** |

### Special Situation Handling

**Split Decision (evenly divided)**:
- Example: Accept + Accept + Reject + Reject
- The Journal-Fit Reviewer (or synthesizer) needs to deeply analyze the cause of disagreement
- Resolve on the arbitration principles (evidence first, expertise first). A genuinely unresolvable split records the dissent and routes the author to respond to it — revision is the vehicle for that response, not a policy of rounding splits toward the stricter verdict (#574 B1)
- May consider inviting a fifth reviewer

**One Outlier (one unusual opinion)**:
- Example: Minor + Minor + Minor + Reject
- Carefully examine the Reject rationale
- If the rationale is valid and others missed it, escalate to Major Revision
- If the rationale is insufficient, maintain Minor Revision but mention the opinion in the Decision Letter

---

## 3. Decision Confidence Calibration

### Impact of Reviewer Confidence Score

| Confidence | Impact on Decision |
|-----------|-------------------|
| 5 (Very High) | This reviewer's opinion carries the highest weight |
| 4 (High) | Standard weight |
| 3 (Medium) | Standard weight, but reduced in case of disagreement |
| 2 (Low) | For reference only, not used as a decisive opinion |
| 1 (Very Low) | Ignore this reviewer's recommendation (but retain specific comments) |

### Cross-Dimension Decision Impact

Finding severity is transported from the reviewer cards (the Schema 6 enum, `shared/handoff_schemas.md` § Weakness Object) — this table assigns NO severities (#574 A3); it describes how dimension-score patterns bear on the DECISION only.

| Situation | Decision impact |
|-----------|-----------------|
| Methodology owner identifies a fatal design flaw | Even if other dimensions are excellent, Reject is available |
| Domain owner identifies a repairable major literature omission | Major Revision, require supplementation |
| Perspective owner identifies a cross-disciplinary relevance failure | Minor or Major Revision, based on its decision impact |
| Journal-Fit Reviewer identifies a writing-and-structure weakness | Does not by itself invalidate the academic core; require language or structural revision |

---

## 4. Revision Round Policy

### Standard Policy

| Round | Expectation | Handling |
|-------|-------------|---------|
| R1 (First revision) | Respond to all reviewer comments | Send for re-review or handling-editor review |
| R2 (Second revision) | Respond to residual issues | Usually the journal's handling editor makes the final decision |
| R3 (Third revision) | Very rare, usually only handling formatting | The journal's handling editor makes the final decision |

### Upgrade/Downgrade Rules

- Minor Revision with incomplete revisions -> May escalate to Major Revision
- Major Revision with excellent revisions -> May downgrade to Minor Revision or Accept
- Major Revision with insufficient revisions -> May Reject (infinite revision cycles are not encouraged)
- Beyond 2 rounds of Major Revision -> Strongly recommend Accept or Reject, no further extension

---

## 5. Professional Ethics of Editorial Review

### Reviewer Ethics

1. **Confidentiality**: The review process and paper content are confidential
2. **Conflict of interest**: Recuse if there is a collaborative or competitive relationship with the author
3. **Timeliness**: Complete the review within the committed timeframe
4. **Constructiveness**: Even when recommending Reject, provide constructive feedback
5. **Impartiality**: No bias based on author's gender, race, institution, or nationality
6. **No plagiarism**: Do not use unpublished ideas seen during review
7. **Appropriate language**: Avoid personal attacks, sarcasm, or demeaning language

### Editor Ethics

1. **Fair decision**: Based on academic quality, not influenced by external pressure
2. **Transparent process**: Decision letter must clearly explain the rationale
3. **Reasonable deadlines**: Give authors sufficient revision time
4. **Appeal channel**: Authors have the right to respond to or challenge review comments
5. **Consistent standards**: Papers of similar quality should receive similar decisions

### Ethical Considerations for Special Situations

| Situation | Ethical Handling |
|-----------|-----------------|
| Author is your student/colleague | Must recuse or disclose the relationship |
| Paper's viewpoint is opposite to yours | Evaluate argument quality, not correctness of position |
| Paper uses your theory but misunderstands it | May point it out but cannot require citation of your own work |
| Suspected data fabrication | Report to the real journal's Editor-in-Chief (EIC); the journal initiates its investigation procedure |
| Paper is similar to your ongoing research | Disclose potential conflict of interest |
