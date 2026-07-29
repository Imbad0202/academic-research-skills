## F. Revised manuscript (excerpt)

> **Abstract.** … self-efficacy predicted end-of-year attainment (b = 0.31) …
>
> **4.2 Measurement.** Self-efficacy was measured with the 12-item Academic Self-Efficacy
> Scale (Lin & Ortega, 2021; DOI 10.5555/ases.2021.0043). Items are rated 1-5 and summed.
> Internal consistency in the present sample was high (Cronbach's alpha = .89; McDonald's
> omega = .90, n = 1,204).
>
> **4.3 Analytic strategy.** We estimate ordinary least squares models with school fixed
> effects. Missingness on the self-efficacy composite was 4.7%; we use multiple imputation
> by chained equations (20 imputations) under a missing-at-random assumption.
>
> **5. Results.** Self-efficacy predicts end-of-year attainment (b = 0.31, SE = 0.09,
> p = .001).

## G. Revision patch and apply report

**Patch (excerpt)**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ Abstract @@
-… self-efficacy was a moderate predictor of end-of-year attainment (d = 0.55) …
+… self-efficacy predicted end-of-year attainment (b = 0.31) …
@@ 4.2 Measurement @@
 Scale (Lin & Ortega, 2021; DOI 10.5555/ases.2021.0043). Items are rated 1-5 and summed.
+Internal consistency in the present sample was high (Cronbach's alpha = .89; McDonald's
+omega = .90, n = 1,204).
@@ 4.3 Analytic strategy @@
 We estimate ordinary least squares models with school fixed
 effects.
+Missingness on the self-efficacy composite was 4.7%; we use multiple imputation
+by chained equations (20 imputations) under a missing-at-random assumption.
```

**Apply report**

```json
{
  "report_format_version": "1.2",
  "base_draft_hash": "<<BASE_DRAFT_HASH>>",
  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
  "patch_digest": "<<PATCH_DIGEST>>",
  "hunks_applied": 3,
  "hunks_rejected": 0
}
```

## H. Response to Reviewers

**R1 (REV-001).** Section 4.2 now reports internal consistency computed on the present
sample: alpha = .89, omega = .90 (n = 1,204).

**R2 (REV-002).** Section 4.3 now names the procedure (multiple imputation by chained
equations, 20 imputations, MAR) and states the missingness proportion (4.7%).

**R3 (REV-003).** The abstract now reports b = 0.31, matching Section 5.
