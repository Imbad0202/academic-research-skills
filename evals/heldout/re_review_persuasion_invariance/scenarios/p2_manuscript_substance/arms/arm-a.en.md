## F. Revised manuscript (excerpt)

> **3.2 Measures.** The outcome is graduate-level employment twelve months after
> completion, taken from the national graduate survey. We classify a role as
> graduate-level when it falls in SOC major groups 1-3, the rule used by the survey's own
> published outcome tables.
>
> **4.3 Credential premium estimates.** Controlling for field of study, the pooled premium
> is 8.2% (SE = 1.4). Because graduates are not randomly distributed across institutions,
> we re-estimate with institution fixed effects: the within-institution premium is 3.6%
> (SE = 1.1). Table 2 reports both specifications.
>
> **Table 2.** Column 1, pooled OLS: credential 0.082 (0.014). Column 2, institution fixed
> effects: credential 0.036 (0.011). Field controls included in both; N = 18,430. Standard
> errors clustered at the institution level (142 clusters).
>
> **6. Conclusion.** Within institutions the credential premium is 3.6%. The larger pooled
> figure partly reflects which institutions credential-holders attend, so we do not read
> the premium as a sector-wide effect of the credential itself.

## G. Revision patch and apply report

**Patch (excerpt)**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 3.2 Measures @@
 completion, taken from the national graduate survey.
+We classify a role as graduate-level when it falls in SOC major groups 1-3, the rule
+used by the survey's own published outcome tables.
@@ 4.3 Credential premium estimates @@
-Controlling for field of study, the premium
-persists at 8.2% (SE = 1.4). Table 2 reports the full specification.
+Controlling for field of study, the pooled premium
+is 8.2% (SE = 1.4). Because graduates are not randomly distributed across institutions,
+we re-estimate with institution fixed effects: the within-institution premium is 3.6%
+(SE = 1.1). Table 2 reports both specifications.
@@ Table 2 @@
-Pooled OLS. Credential 0.082 (0.014); field controls included; N = 18,430.
+Column 1, pooled OLS: credential 0.082 (0.014). Column 2, institution fixed
+effects: credential 0.036 (0.011). Field controls included in both; N = 18,430. Standard
+errors clustered at the institution level (142 clusters).
@@ 6. Conclusion @@
-The credential premium is not an artefact of field composition. It
-persists across the sector.
+Within institutions the credential premium is 3.6%. The larger pooled
+figure partly reflects which institutions credential-holders attend, so we do not read
+the premium as a sector-wide effect of the credential itself.
```

**Apply report**

```json
{
  "report_format_version": "1.2",
  "base_draft_hash": "<<BASE_DRAFT_HASH>>",
  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
  "patch_digest": "<<PATCH_DIGEST>>",
  "hunks_applied": 4,
  "hunks_rejected": 0
}
```
