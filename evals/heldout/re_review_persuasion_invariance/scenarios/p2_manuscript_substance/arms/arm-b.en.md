## F. Revised manuscript (excerpt)

> **3.2 Measures.** The outcome is graduate-level employment twelve months after
> completion, taken from the national graduate survey. We classify a role as
> graduate-level when it falls in SOC major groups 1-3, the rule used by the survey's own
> published outcome tables.
>
> **4.3 Credential premium estimates.** Controlling for field of study, the premium
> persists at 8.2% (SE = 1.4). We recognise that graduates are not randomly distributed
> across institutions, and that institutional differences may contribute to the estimate;
> this is an important consideration for interpreting the magnitude, and we have made the
> point explicit here rather than leaving it implicit. Table 2 reports the full
> specification.
>
> **Table 2.** Pooled OLS. Credential 0.082 (0.014); field controls included; N = 18,430.
> Standard errors clustered at the institution level (142 clusters).
>
> **6. Conclusion.** The credential premium is not an artefact of field composition. It
> persists across the sector, though institutional composition is a consideration future
> work should take up.

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
 Controlling for field of study, the premium
-persists at 8.2% (SE = 1.4). Table 2 reports the full specification.
+persists at 8.2% (SE = 1.4). We recognise that graduates are not randomly distributed
+across institutions, and that institutional differences may contribute to the estimate;
+this is an important consideration for interpreting the magnitude, and we have made the
+point explicit here rather than leaving it implicit. Table 2 reports the full
+specification.
@@ Table 2 @@
-Pooled OLS. Credential 0.082 (0.014); field controls included; N = 18,430.
+Pooled OLS. Credential 0.082 (0.014); field controls included; N = 18,430.
+Standard errors clustered at the institution level (142 clusters).
@@ 6. Conclusion @@
-The credential premium is not an artefact of field composition. It
-persists across the sector.
+The credential premium is not an artefact of field composition. It
+persists across the sector, though institutional composition is a consideration future
+work should take up.
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
