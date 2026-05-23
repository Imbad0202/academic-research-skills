# Clinical Epistemic Status Example

This example shows how to detect silent epistemic upgrades in clinical and health research writing. It is a documentation example, not a schema decision for the final `epistemic_status` vocabulary.

Use this when a draft turns preliminary, observational, in-vitro, or hypothesis-level evidence into stronger clinical or causal language.

---

## Scenario

A draft contains the following sentence:

> GLP-1 receptor agonist use prevented cardiovascular hospitalization in patients with type 2 diabetes and should be prioritized in routine care.

The cited source is a retrospective electronic health record cohort study. The source text says:

> In this retrospective cohort, GLP-1 receptor agonist exposure was associated with a lower rate of cardiovascular hospitalization after adjustment for measured covariates. Residual confounding remains possible, and prospective trials are needed before practice recommendations can be made.

The citation may be real and correctly formatted, but the draft still overstates the source.

---

## Status Mapping

This example preserves both epistemic axes mentioned in issue #183:

| Axis | Conservative label | Why |
|---|---|---|
| Current 5-tier claim-confidence axis | `Preliminary` or `Supported` | The finding has empirical support, but it is observational and not necessarily replicated. |
| Proposed research-design axis | `observational_evidence` | The study design supports association language, not an intervention-level causal claim. |
| Disallowed upgrade | `causal_claim` / `validated_conclusion` | The source explicitly says residual confounding remains possible and trials are needed. |

Do not collapse these axes without a project-level vocabulary decision. For this example, the safety rule is simpler: the draft cannot use stronger language than the source supports.

---

## Silent Upgrade Audit

| Source signal | Draft language | Upgrade type | Safer rewrite |
|---|---|---|---|
| "retrospective cohort" | "prevented" | Observational to causal | "was associated with a lower rate of..." |
| "associated with" | "prevented" | Association to cause | "was associated with..." |
| "after adjustment for measured covariates" | omitted | Confounding hedge dropped | "after adjustment for measured covariates, with residual confounding possible..." |
| "prospective trials are needed" | "should be prioritized in routine care" | Evidence summary to clinical recommendation | "does not establish routine-care prioritization without prospective trial evidence..." |
| "patients with type 2 diabetes" | broad clinical population implied | Population scope widened | "in the studied type 2 diabetes cohort..." |

---

## Checklist

Before accepting a clinical claim, verify:

1. **Study design**: Does the source describe an RCT, cohort, case-control study, cross-sectional study, in-vitro study, animal model, qualitative study, or hypothesis paper?
2. **Verb strength**: Does the draft use verbs such as "causes", "prevents", "proves", "establishes", or "should be used" when the source only says "associated", "suggests", "may", or "needs validation"?
3. **Clinical action**: Does the draft move from evidence summary to diagnosis, treatment, triage, deployment, or routine-care recommendation?
4. **Population scope**: Does the draft generalize beyond the source population, setting, disease stage, or inclusion criteria?
5. **Protected hedges**: Are phrases such as "retrospective", "observational", "in this cohort", "preliminary", "may", "associated with", and "requires validation" preserved?
6. **Human review boundary**: If the claim affects clinical interpretation, does the draft frame the output as research synthesis rather than patient-specific advice?

---

## Example Verdict

```yaml
claim_under_review: "GLP-1 receptor agonist use prevented cardiovascular hospitalization and should be prioritized in routine care."
source_design: "retrospective cohort"
source_anchor: "associated with a lower rate... residual confounding remains possible... prospective trials are needed"
current_5_tier_status: "Preliminary or Supported"
design_stage_status: "observational_evidence"
silent_upgrade_detected: true
upgrade_kind:
  - "association_to_cause"
  - "observational_to_clinical_recommendation"
  - "hedge_drop"
required_rewrite: "GLP-1 receptor agonist exposure was associated with a lower rate of cardiovascular hospitalization in the studied retrospective cohort; residual confounding remains possible, and this finding does not by itself justify routine-care prioritization."
clinical_safety_note: "Research synthesis only. Not patient-specific diagnosis, treatment, triage, or clinical decision support."
```

---

## Mini Fixtures

These synthetic cases can guide future tests or examples without committing to the final schema:

| Case | Weak source status | Unsafe draft upgrade | Expected correction |
|---|---|---|---|
| Association to cause | Observational association | "X caused lower mortality" | "X was associated with lower mortality in the studied cohort" |
| In-vitro to clinical use | Bench-only mechanism | "X is ready for patient treatment" | "X showed an in-vitro mechanism that requires animal and clinical validation" |
| Hypothesis to conclusion | Discussion hypothesis | "The study demonstrates X" | "The authors hypothesize X; direct evidence was not tested" |

---

## Relation to Epistemic Status Work

This example is related to issue #183. It intentionally avoids choosing between the existing 5-tier claim-confidence vocabulary and the proposed research-design-stage vocabulary. Instead, it documents the clinical safety invariant that both vocabularies need to preserve: downstream writing must not silently upgrade a source's evidentiary status, conclusion strength, population scope, or clinical actionability.
