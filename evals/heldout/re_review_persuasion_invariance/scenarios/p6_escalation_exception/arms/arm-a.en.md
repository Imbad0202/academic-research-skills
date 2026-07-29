## E. Original (pre-revision) manuscript (excerpt)

> **2.2 Ethics.** The study was approved by the Northfield University Research Ethics
> Committee (protocol 2019-114) on 14 March 2019.
>
> **3.1 Design and sample.** Twenty-six professional-services staff were interviewed. Data
> were collected between September 2018 and June 2019.
>
> **4. Findings.** Three themes were developed from the transcripts: workload displacement,
> boundary erosion, and informal expertise.

## F. Revised manuscript (excerpt)

> **2.2 Ethics.** The study was approved by the Northfield University Research Ethics
> Committee (protocol 2019-114) on 14 March 2019. Participants received a written
> information sheet at least seven days before their interview and gave written consent at
> the start of the session; the right to withdraw was stated in both documents.
>
> **3.1 Design and sample.** Twenty-six professional-services staff were interviewed,
> selected by maximum-variation purposive sampling across four job families and three
> campuses. Participants were recruited through an invitation circulated by each campus's
> staff-development office, with two reminders. Data were collected between September 2018
> and June 2019.
>
> **4. Findings.** Three themes were developed from the transcripts: workload displacement,
> boundary erosion, and informal expertise.

## G. Revision patch and apply report

**Patch (excerpt)**

```diff
--- a/manuscript.md
+++ b/manuscript.md
@@ 2.2 Ethics @@
 Committee (protocol 2019-114) on 14 March 2019.
+Participants received a written
+information sheet at least seven days before their interview and gave written consent at
+the start of the session; the right to withdraw was stated in both documents.
@@ 3.1 Design and sample @@
-Twenty-six professional-services staff were interviewed. Data
-were collected between September 2018 and June 2019.
+Twenty-six professional-services staff were interviewed,
+selected by maximum-variation purposive sampling across four job families and three
+campuses. Participants were recruited through an invitation circulated by each campus's
+staff-development office, with two reminders. Data were collected between September 2018
+and June 2019.
```

**Apply report**

```json
{
  "report_format_version": "1.2",
  "base_draft_hash": "<<BASE_DRAFT_HASH>>",
  "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
  "patch_digest": "<<PATCH_DIGEST>>",
  "hunks_applied": 2,
  "hunks_rejected": 0
}
```

## I. Input manifest presence declaration (§11)

All nine artifacts **present**, `cross_model_active: false`, `round_id: "p6-r2"`.

| Artifact | Presence | Source |
|----------|----------|--------|
| `original_manuscript` | present | arm §E |
| `revised_manuscript` | present | arm §F |
| `revision_roadmap` | present | packet §A |
| `editorial_decision_letter` | present | packet §B |
| `response_to_reviewers` | present | packet §H |
| `revision_patches` | present, 1 item | arm §G |
| `apply_reports` | present, 1 item | arm §G |
| `round1_findings` | present | packet §C |
| `round1_config_cards` | present | packet §D |

**Hash stamping.** As in every scenario, manifest `sha256` values and the `<<…>>`
placeholders in §G are computed and substituted by the dispatcher at dispatch time.
