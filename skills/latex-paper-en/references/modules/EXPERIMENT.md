# Module: Experiment Review

**Trigger**: experiment, evaluation, baseline, ablation, significance, efficiency comparison

**Purpose**: Review an existing experiment or evaluation section and emit reviewer-style findings without drafting a replacement paragraph.

## Commands

```bash
uv run python -B scripts/analyze_experiment.py main.tex --section experiments
uv run python -B scripts/analyze_experiment.py main.tex --section results
```

## Review Focus

- baseline/comparator specificity
- metric and numeric evidence
- overclaiming or promotional wording
- missing ablation evidence
- missing statistical significance or variance reporting
- missing efficiency comparison
- conclusions that go beyond the evidence shown

## Raw Script Output

```latex
% EXPERIMENT (Line 42) [Severity: Major] [Priority: P1]: Comparison claim names only generic baselines; cite or name the exact comparator.
% EXPERIMENT (Line 42) [Severity: Major] [Priority: P1]: Performance claim is not tied to a concrete metric or numeric result.
```

## Skill-Layer Response

- Keep the final response in LaTeX-friendly review comment style.
- Do not rewrite the experiment section unless the user explicitly asks for revised prose.
- Never invent baselines, metrics, significance claims, or efficiency numbers.

---

## Discussion & Results-Literature Integration (B3-B4)

### B3: Discussion Depth — Attribution Over Repetition

**Rule**: The Discussion section must go beyond restating numbers. It should explain *why* results occur using causal/attribution language. A discussion that merely echoes tables without interpretation is shallow.

**Detection heuristic** (script-automated):
- Scan all visible lines in the `discussion` section
- Count lines containing attribution markers: `because|due to|owing to|as a result of|attributed to|caused by|mechanism|explains|explanation|reason|hypothesis|interpret|stems from|arises from|driven by|suggests that|indicates that`
- If ratio < 15% of total visible lines (minimum 5 lines) → Major/P1

| Pattern | Verdict |
|---------|---------|
| "Model A achieves 95%. Model B achieves 90%." | Shallow repetition (flag) |
| "Model A outperforms Model B, likely due to its ability to capture long-range dependencies." | Attribution present (pass) |

### B4: Results-Literature Echo

**Rule**: The Discussion should reference prior work cited in Related Work to compare findings. Citation keys from Related Work should reappear in Discussion to show the authors have contextualized their results.

**Detection heuristic** (script-automated):
- Extract citation keys (`\cite{...}`) from `related` section range
- Extract citation keys from `discussion` section range
- If zero overlap → Major/P1

**Fix**: Add sentences like "Consistent with findings by Smith et al. \cite{smith2020}, our results confirm..." or "Unlike the approach of Jones \cite{jones2019}, our method demonstrates..."

---

## Conclusion Completeness Check (B5)

**Rule**: A complete Conclusion must contain three elements:
1. **Core findings summary** — explicit restatement of what was demonstrated
2. **Implications** — broader impact or practical significance
3. **Limitations / Future work** — acknowledged boundaries and next steps

**Detection heuristic** (script-automated):
- Scan `conclusion` section for three keyword categories:
  - Findings: `we have shown|we demonstrated|results show|this paper has presented|our experiments confirm|we proposed|findings indicate|key finding|main result`
  - Implications: `implication|suggests that.*practical|enables|opens|paves the way|facilitates|contributes to|advance|potential for|applicable to`
  - Limitations: `limitation|future work|future direction|remain|challenge|could be extended|further research|further investigation|not addressed|beyond the scope|caveat`
- Missing limitations → Major/P1
- Missing implications → Minor/P2
- Missing findings summary → Minor/P2
